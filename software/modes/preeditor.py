# =================================================
# MODO PREEDITOR (extraído completo del original)
# =================================================

import json
from datetime import datetime

# Importamos todo el ecosistema SMPlayer
from modes.smplayer import (
    mpv_set_pause,
    mpv_get_time,
    mpv_get_path,
    update_play_led,
    smplayer_core,
    BTN_PLAY,
    BTN_FRAME_LEFT,
    BTN_FRAME_RIGHT,
    BTN_SCREENSHOT,
    BTN_GOTO_START,
    BTN_GOTO_END,
    BTN_MARK_ADD,
    BTN_MARK_PREV,
    BTN_MARK_NEXT,
)


# =================================================
# CONSTANTES
# =================================================

BTN_PREEDITOR = 28

BTN_NEW_PROJECT     = 12
BTN_CLOSE_PROJECT   = 22
BTN_EXPORT_PROJECT  = 32

BTN_NEW_CHAPTER     = 10
BTN_SAVE_CHAPTER    = 11

BTN_MARK_IN         = 20
BTN_MARK_OUT        = 30
BTN_ADD_SEGMENT     = 21
BTN_DELETE_LAST     = 31


# =================================================
# VARIABLES GLOBALES (idénticas al original)
# =================================================

proyecto = None

current_chapter_name = None
current_source_file = None

current_segments = []
current_in = None
current_out = None


# =================================================
# FUNCIONES VISUALES
# =================================================

def update_project_leds(f):

    if proyecto is not None:
        f.ledButton(BTN_NEW_PROJECT, False)
        f.ledButton(BTN_CLOSE_PROJECT, True)
    else:
        f.ledButton(BTN_NEW_PROJECT, True)
        f.ledButton(BTN_CLOSE_PROJECT, False)


def update_segment_matrix(f):

    for col in range(8):
        for row in range(4):
            f.ledAt(row, col, False)

    for idx, seg in enumerate(current_segments):
        if idx < 8:
            f.ledAt(2, idx, True)

    if current_in is not None and len(current_segments) < 8:
        f.ledAt(0, len(current_segments), True)

    if current_out is not None and len(current_segments) < 8:
        f.ledAt(1, len(current_segments), True)

    if proyecto and proyecto.get("jobs"):
        last_job = proyecto["jobs"][-1]

        for idx, seg in enumerate(last_job.get("segments", [])):
            if idx < 8:
                f.ledAt(3, idx, True)


def update_editor_buttons(f):

    if proyecto is None:
        f.ledButton(BTN_NEW_PROJECT, True)
        f.ledButton(BTN_CLOSE_PROJECT, False)
        f.ledButton(BTN_EXPORT_PROJECT, False)
    else:
        f.ledButton(BTN_NEW_PROJECT, False)
        f.ledButton(BTN_CLOSE_PROJECT, True)
        f.ledButton(BTN_EXPORT_PROJECT, True)

    if proyecto is None:
        f.ledButton(BTN_NEW_CHAPTER, False)
        f.ledButton(BTN_SAVE_CHAPTER, False)
    else:
        f.ledButton(BTN_NEW_CHAPTER, True)
        f.ledButton(BTN_SAVE_CHAPTER, bool(current_segments))

    if proyecto is None or current_chapter_name is None:
        f.ledButton(BTN_MARK_IN, False)
        f.ledButton(BTN_MARK_OUT, False)
        f.ledButton(BTN_ADD_SEGMENT, False)
        f.ledButton(BTN_DELETE_LAST, False)
        return

    f.ledButton(BTN_MARK_IN, True)
    f.ledButton(BTN_MARK_OUT, True)

    can_add = (
        current_in is not None
        and current_out is not None
        and current_out > current_in
    )

    f.ledButton(BTN_ADD_SEGMENT, can_add)
    f.ledButton(BTN_DELETE_LAST, bool(current_segments))


# =================================================
# EXPORT
# =================================================

def export_project_json():

    if not proyecto:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"f998_project_{timestamp}.json"

    data = proyecto.copy()
    data["created_at"] = datetime.now().isoformat()

    with open(filename, "w", encoding="utf-8") as fjson:
        json.dump(data, fjson, indent=2, ensure_ascii=False)


# =================================================
# LÓGICA PRINCIPAL
# =================================================

def preeditor_segment_logic(f, k):

    global proyecto
    global current_chapter_name, current_source_file
    global current_segments, current_in, current_out

    if not k:
        return

    if not proyecto and k not in (BTN_NEW_PROJECT,):
        return

    # ---------- PROYECTO ----------

    if k == BTN_NEW_PROJECT and proyecto is None:

        mpv_set_pause(True)

        from modes.smplayer import tk_prompt
        nombre = tk_prompt("Nuevo Proyecto", "Nombre del proyecto:")

        if nombre:
            proyecto = {
                "project_name": nombre,
                "jobs": []
            }

    elif k == BTN_CLOSE_PROJECT and proyecto is not None:

        from modes.smplayer import tk_prompt
        confirm = tk_prompt("Cerrar Proyecto", "Escribe 'SI' para confirmar:")

        if confirm == "SI":

            proyecto = None
            current_segments.clear()
            current_in = None
            current_out = None

    elif k == BTN_EXPORT_PROJECT:
        export_project_json()

    # ---------- CAPITULO ----------

    elif k == BTN_NEW_CHAPTER:

        if not proyecto:
            return

        mpv_set_pause(True)

        from modes.smplayer import tk_prompt
        nombre = tk_prompt("Nuevo Capítulo", "Nombre del capítulo:")

        if nombre:
            current_chapter_name = nombre
            current_source_file = mpv_get_path()

            current_segments.clear()
            current_in = None
            current_out = None

    elif k == BTN_SAVE_CHAPTER:
        if (
            proyecto
            and current_chapter_name
            and current_source_file
            and current_segments
        ):
            proyecto["jobs"].append({
                "output": current_chapter_name,
                "source": current_source_file,
                "segments": current_segments.copy()
            })

            current_segments.clear()
            current_in = None
            current_out = None

    # ---------- SEGMENTACION ----------

    elif k == BTN_MARK_IN:
        t = mpv_get_time()
        if t is not None:
            current_in = t

    elif k == BTN_MARK_OUT:
        t = mpv_get_time()
        if t is not None:
            current_out = t

    elif k == BTN_ADD_SEGMENT:
        if (
            current_in is not None
            and current_out is not None
            and current_out > current_in
            and len(current_segments) < 8
        ):
            current_segments.append({
                "in": current_in,
                "out": current_out
            })
            current_in = None
            current_out = None

    elif k == BTN_DELETE_LAST:
        if current_segments:
            current_segments.pop()

    update_editor_buttons(f)
    update_segment_matrix(f)


# =================================================
# INIT / LOOP / EXIT
# =================================================

def preeditor_init(f):

    update_project_leds(f)
    update_segment_matrix(f)
    f.ledButton(BTN_PREEDITOR, True)
    update_editor_buttons(f)


def preeditor_loop(f, k, estado, smplayer_en_foco):

    foco = smplayer_en_foco()

    f.ledBlink(BTN_PREEDITOR, not foco)

    if not foco:
        return

    f.ledButton(BTN_PREEDITOR, True)

    update_play_led(f)

    smplayer_core(f, k, estado)

    preeditor_segment_logic(f, k)


def preeditor_exit(f):
    pass
