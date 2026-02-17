# =================================================
# MODO SMPLAYER (bloque completo original)
# =================================================

import time
import subprocess
import socket
import json
import tkinter as tk
import threading
from pynput.keyboard import Controller, Key


# =================================================
# CONSTANTES
# =================================================

BTN_SMPLAYER = 38

BTN_PLAY = 27
BTN_FRAME_LEFT = 36
BTN_FRAME_RIGHT = 37

BTN_SCREENSHOT = 26
BTN_GOTO_START = 34
BTN_GOTO_END = 35

BTN_MARK_ADD  = 15
BTN_MARK_PREV = 24
BTN_MARK_NEXT = 25

BTN_SKIP_40 = 17
BTN_SEEK_ABS = 16


MPV_SOCKET = "/tmp/mpvsocket"

BTN_DELAY = 0.30
WHEEL_DELAY = 0.08
VOLUME_DELAY = 0.15
VOLUME_STEP = 2  # %


# =================================================
# VARIABLES GLOBALES (idénticas al original)
# =================================================

smplayer_en_pausa = False
last_button_sm = 0
last_wheel_sm = 0
last_volume_smplayer = 0 
last_volume_system = 0 
last_pause_check = 0
cached_pause_state = None
last_frame_time = 0
last_speed_pos = None

kbd = Controller()


# =================================================
# MPV IPC
# =================================================

def mpv_send(cmd_dict):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(MPV_SOCKET)
        sock.sendall((json.dumps(cmd_dict) + "\n").encode())
        sock.close()
    except Exception:
        return None


def mpv_query(cmd_dict):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(MPV_SOCKET)
        sock.sendall((json.dumps(cmd_dict) + "\n").encode())

        file = sock.makefile()
        line = file.readline()
        sock.close()

        if line:
            return json.loads(line)

    except Exception:
        return None


def mpv_get_pause():
    r = mpv_query({"command": ["get_property", "pause"]})
    if r and "data" in r:
        return bool(r["data"])
    return None


def mpv_set_pause(state: bool):
    mpv_send({"command": ["set_property", "pause", state]})


def mpv_get_time():
    r = mpv_query({"command": ["get_property", "time-pos"]})
    if r and "data" in r and r["data"] is not None:
        return float(r["data"])
    return None


def mpv_get_path():
    r = mpv_query({"command": ["get_property", "path"]})
    if r and "data" in r:
        return r["data"]
    return None


def mpv_get_pid():
    r = mpv_query({"command": ["get_property", "pid"]})
    if r and "data" in r:
        return int(r["data"])
    return None


def mpv_seek_absolute(seconds):
    mpv_send({"command": ["seek", seconds, "absolute"]})


def mpv_seek_relative(seconds):
    mpv_send({"command": ["seek", seconds, "relative"]})


def mpv_set_speed(value):
    mpv_send({"command": ["set_property", "speed", value]})


def pedir_seek_absoluto():

    from modes.smplayer import tk_prompt

    valor = tk_prompt("Seek absoluto", "Introduce segundos:")

    if valor is None:
        return

    try:
        segundos = float(valor)

        if segundos < 0:
            return

        mpv_seek_absolute(segundos)

    except Exception:
        pass


# =================================================
# TK PROMPT
# =================================================

def tk_prompt(titulo, mensaje):

    resultado = {"valor": None}

    def dialogo():

        root = tk.Tk()
        root.title(titulo)

        tk.Label(root, text=mensaje).pack(padx=20, pady=10)

        entry = tk.Entry(root)
        entry.pack(padx=20, pady=10)
        entry.focus()

        def aceptar():
            resultado["valor"] = entry.get()
            root.destroy()

        entry.bind("<Return>", lambda e: aceptar())
        tk.Button(root, text="Aceptar", command=aceptar).pack(pady=10)

        root.mainloop()

    hilo = threading.Thread(target=dialogo)
    hilo.start()
    hilo.join()

    return resultado["valor"]


# =================================================
# FOCO SMPLAYER
# =================================================

def smplayer_focus():

    pid = mpv_get_pid()
    if not pid:
        return

    try:
        win_ids = subprocess.check_output(
            ["xdotool", "search", "--onlyvisible", "--pid", str(pid)],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip().split("\n")

        for wid in win_ids:
            if wid.strip():
                subprocess.call(
                    ["xdotool", "windowactivate", "--sync", wid],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                break

    except Exception:
        pass


# =================================================
# LED PLAY SYNC
# =================================================

def update_play_led(f):

    global last_pause_check
    global cached_pause_state

    now = time.time()

    if now - last_pause_check < 0.3:
        return

    last_pause_check = now

    p = mpv_get_pause()
    if p is None:
        return

    if p != cached_pause_state:

        cached_pause_state = p

        f.ledButton(BTN_PLAY, True)
        f.ledBlink(BTN_PLAY, p)


# =================================================
# CORE SMPLAYER (separado como en original)
# =================================================

def smplayer_core(f, k, estado):

    global last_button_sm
    global last_wheel_sm
    global last_volume_smplayer
    global last_volume_system

    now = time.time()

    update_play_led(f)

    # BOTONES
    if k and now - last_button_sm > BTN_DELAY:
        last_button_sm = now

        if k == BTN_PLAY:
            p = mpv_get_pause()
            if p is not None:
                mpv_set_pause(not p)

        elif k == BTN_FRAME_LEFT:
            mpv_seek_relative(-1)

        elif k == BTN_FRAME_RIGHT:
            mpv_seek_relative(1)

        elif k == BTN_SKIP_40:
            mpv_seek_relative(40 * 60)  # 2400 segundos

        elif k == BTN_SCREENSHOT:
            kbd.tap('s')

        elif k == BTN_GOTO_START:
            mpv_seek_absolute(0)

        elif k == BTN_GOTO_END:
            mpv_seek_absolute(-60)

        elif k == BTN_SEEK_ABS:
            pedir_seek_absoluto()

        elif k == BTN_MARK_ADD:
            kbd.press(Key.ctrl); kbd.tap('a'); kbd.release(Key.ctrl)

        elif k == BTN_MARK_PREV:
            kbd.press(Key.ctrl); kbd.tap('b'); kbd.release(Key.ctrl)

        elif k == BTN_MARK_NEXT:
            kbd.press(Key.ctrl); kbd.tap('n'); kbd.release(Key.ctrl)

    # RUEDA
    if now - last_wheel_sm > WHEEL_DELAY:
        last_wheel_sm = now

        v = estado["D"][6]

        if v == 0: kbd.tap(Key.page_down)
        elif v == 1: kbd.tap(Key.down)
        elif v == 2: kbd.tap(Key.left)
        elif v == 4: kbd.tap(Key.right)
        elif v == 5: kbd.tap(Key.up)
        elif v == 6: kbd.tap(Key.page_up)

    # --------------------------------------------------
    # FRAME STEP con digPot(5) con delay variable
    # --------------------------------------------------

    global last_frame_time

    dz = estado["D"][4] - 3  # digPot(5)
    now_frame = time.time()

    if dz != 0:

        # Determinar si necesita delay
        use_delay = abs(dz) == 1

        if not use_delay or (now_frame - last_frame_time > BTN_DELAY):

            last_frame_time = now_frame

            if dz < 0:
                kbd.tap(',')

            elif dz > 0:
                kbd.tap('.')

    # --------------------------------------------------
    # CONTROL VELOCIDAD con digPot(4) vía IPC
    # --------------------------------------------------

    global last_speed_pos

    speed_pos = estado["D"][3]  # digPot(4)

    if speed_pos != last_speed_pos:

        last_speed_pos = speed_pos

        delta = speed_pos - 3

        speed_map = {
            -3: 1/8,
            -2: 1/4,
            -1: 1/2,
             0: 1,
             1: 2,
             2: 4,
             3: 8,
        }

        if delta in speed_map:
            mpv_set_speed(speed_map[delta])


    # VOLUMEN SISTEMA
    dv = estado["D"][0] - 3
    if dv != 0 and now - last_volume_system > VOLUME_DELAY:
        last_volume_system = now
        pasos = abs(dv)

        if dv > 0:
            subprocess.call(["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%+"])
        else:
            subprocess.call(["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%-"])

    # VOLUMEN SMPLAYER
    dv = estado["D"][1] - 3
    if dv != 0 and now - last_volume_smplayer > VOLUME_DELAY:
        last_volume_smplayer = now

        for _ in range(abs(dv)):
            kbd.tap('9' if dv < 0 else '0')


# =================================================
# INIT / LOOP / EXIT
# =================================================

def smplayer_init(f):
    f.ledButton(BTN_PLAY, True)


def smplayer_loop(f, k, estado, smplayer_en_foco):

    foco = smplayer_en_foco()

    f.ledBlink(BTN_SMPLAYER, not foco)
    if foco:
        f.ledButton(BTN_SMPLAYER, True)
    else:
        return

    smplayer_core(f, k, estado)


def smplayer_exit(f):
    pass
