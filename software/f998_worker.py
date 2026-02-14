#!/usr/bin/env python3

import os
import re
import json
import time
import shutil
import subprocess
from pathlib import Path
from collections import defaultdict

# =========================
# CONFIG
# =========================

FROM_PREFIX = "/home/jordi/VideosRemotos/"
TO_PREFIX   = "/srv/nas/VideoEncoder/"

BASE_DIR = Path("/srv/nas/VideoEncoder")
JOBS_DIR = BASE_DIR / "jobs"
DONE_DIR = JOBS_DIR / "done"
ERROR_DIR = JOBS_DIR / "error"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

EXPORT_PROFILE = "720p"   # 1080p | 720p | 576p
CRF_VALUE = 21

PROFILES = {
    "1080p": {"scale": "1920:-2"},
    "720p":  {"scale": "1280:-2"},
    "576p":  {"scale": "1024:-2"}
}

SLEEP_SECONDS = 5


# =========================
# UTILIDADES
# =========================

def log(msg):
    print(f"[WORKER] {msg}")


def translate_path(path):
    if path.startswith(FROM_PREFIX):
        return path.replace(FROM_PREFIX, TO_PREFIX, 1)
    return path


def split_output_name(name):
    match = re.match(r"(.+?)([a-z])$", name)
    if match:
        return match.group(1), match.group(2)
    return name, None


def validate_sequence(parts):
    expected = [chr(ord('a') + i) for i in range(len(parts))]
    actual = [suffix for suffix, _ in parts]
    if actual != expected:
        raise ValueError("Multipart episode has missing letters")


def run_ffmpeg(cmd, log_file):
    with open(log_file, "a") as lf:
        subprocess.run(cmd, stdout=lf, stderr=lf, check=True)


# =========================
# PROCESAMIENTO
# =========================

def build_segment_command(source, start, end, output_path):
    profile = PROFILES[EXPORT_PROFILE]
    scale = profile["scale"]

    cmd = [
        "ffmpeg",
        "-y",
        "-i", source,
        "-ss", str(start)
    ]

    if not (isinstance(end, str) and end.upper() == "END"):
        cmd += ["-to", str(end)]

    cmd += [
        "-vf", f"scale={scale},fps=30",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", str(CRF_VALUE),
        "-profile:v", "high",
        "-level", "4.1",
        "-pix_fmt", "yuv420p",
        "-g", "60",
        "-keyint_min", "60",
        "-sc_threshold", "0",
        "-c:a", "aac",
        "-b:a", "160k",
        "-movflags", "+faststart",
        str(output_path)
    ]

    return cmd


def concat_files(file_list, final_output, log_file):
    list_file = TEMP_DIR / "concat_list.txt"

    with open(list_file, "w", encoding="utf-8") as f:
        for file in file_list:
            f.write(f"file '{file}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", str(CRF_VALUE),
        "-c:a", "aac",
        "-b:a", "160k",
        str(final_output)
    ]

    run_ffmpeg(cmd, log_file)
    list_file.unlink()


def process_job_group(base_name, parts, json_name):
    log_file = OUTPUT_DIR / f"{base_name}.log"

    final_output = OUTPUT_DIR / f"{base_name}.mp4"

    if final_output.exists():
        raise FileExistsError(f"{final_output} already exists")

    if len(parts) == 1 and parts[0][0] is None:
        # single job normal
        _, job = parts[0]
        process_single_job(job, final_output, log_file)
        return

    # multipart
    parts.sort(key=lambda x: x[0])
    validate_sequence(parts)

    temp_outputs = []

    for suffix, job in parts:
        temp_file = TEMP_DIR / f"{base_name}_{suffix}.mp4"
        process_single_job(job, temp_file, log_file)
        temp_outputs.append(temp_file)

    concat_files(temp_outputs, final_output, log_file)

    for f in temp_outputs:
        f.unlink()


def process_single_job(job, final_path, log_file):
    source = translate_path(job["source"])

    if not Path(source).exists():
        raise FileNotFoundError(f"Source not found: {source}")

    segment_outputs = []

    for idx, seg in enumerate(job["segments"]):
        start = seg["in"]
        end = seg["out"]

        if not isinstance(start, (int, float)):
            raise ValueError("Segment 'in' must be numeric")

        if not (isinstance(end, (int, float)) or
                (isinstance(end, str) and end.upper() == "END")):
            raise ValueError("Segment 'out' invalid")

        temp_segment = TEMP_DIR / f"{final_path.stem}_seg{idx}.mp4"

        cmd = build_segment_command(source, start, end, temp_segment)
        run_ffmpeg(cmd, log_file)

        segment_outputs.append(temp_segment)

    if len(segment_outputs) == 1:
        shutil.move(segment_outputs[0], final_path)
    else:
        concat_files(segment_outputs, final_path, log_file)
        for f in segment_outputs:
            f.unlink()


# =========================
# WORKER LOOP
# =========================

def process_json(json_file):
    log(f"Processing {json_file.name}")

    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        jobs = data["jobs"]

        grouped = defaultdict(list)

        for job in jobs:
            base, suffix = split_output_name(job["output"])
            grouped[base].append((suffix, job))

        for base in grouped:
            process_job_group(base, grouped[base], json_file.name)

        shutil.move(json_file, DONE_DIR / json_file.name)
        log(f"{json_file.name} DONE")

    except Exception as e:
        log(f"ERROR in {json_file.name}: {e}")
        shutil.move(json_file, ERROR_DIR / json_file.name)


def worker_loop():
    log("Worker started")

    while True:
        json_files = list(JOBS_DIR.glob("*.json"))

        for file in json_files:
            process_json(file)

        time.sleep(SLEEP_SECONDS)


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    for d in [DONE_DIR, ERROR_DIR, TEMP_DIR, OUTPUT_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    worker_loop()
