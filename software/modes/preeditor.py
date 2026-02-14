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

BTN_EDIT_JSON = 13

BTN_MARK_END = 33


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

    # -----------------------------------------
    # Capítulos cerrados (fila 3)
    # -----------------------------------------
    if proyecto and proyecto.get("jobs"):
        num_jobs = len(proyecto["jobs"])

        for idx in range(min(num_jobs, 8)):
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
        and (
            current_out == "END"
            or current_out > current_in
        )
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
# EDITOR JSON
# =================================================

def editar_json_proyecto():

    global proyecto

    if not proyecto:
        return

    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Editar JSON Proyecto")

    # ---- COLORES OSCUROS ----
    bg_color = "#1e1e1e"
    fg_color = "#e0e0e0"
    insert_color = "#ffffff"
    select_bg = "#44475a"

    root.configure(bg=bg_color)

    text = tk.Text(
        root,
        bg=bg_color,
        fg=fg_color,
        insertbackground=insert_color,
        selectbackground=select_bg,
        width=100,
        height=35,
        undo=True
    )
    text.pack(padx=10, pady=10, fill="both", expand=True)

    # Insertar JSON formateado
    contenido = json.dumps(proyecto, indent=2, ensure_ascii=False)
    text.insert("1.0", contenido)

    def guardar():
        global proyecto
        nuevo_texto = text.get("1.0", tk.END)

        try:
            nuevo_json = json.loads(nuevo_texto)

            # Validación mínima estructural
            if not isinstance(nuevo_json, dict):
                raise ValueError("El JSON debe ser un objeto raíz.")

            if "project_name" not in nuevo_json:
                raise ValueError("Falta 'project_name'.")

            if "jobs" not in nuevo_json:
                raise ValueError("Falta 'jobs'.")

            for job in nuevo_json["jobs"]:
                if "segments" not in job:
                    raise ValueError("Cada job debe tener 'segments'.")

                for seg in job["segments"]:
                    if "in" not in seg or "out" not in seg:
                        raise ValueError("Cada segmento debe tener 'in' y 'out'.")

                    if not (
                        isinstance(seg["out"], (int, float))
                        or seg["out"] == "END"
                    ):
                        raise ValueError("'out' debe ser número o 'END'.")

            if not isinstance(nuevo_json["jobs"], list):
                raise ValueError("'jobs' debe ser una lista.")

            proyecto = nuevo_json
            root.destroy()

        except Exception as e:
            messagebox.showerror("Error JSON", f"JSON inválido:\n{e}")

    btn_frame = tk.Frame(root, bg=bg_color)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Guardar", command=guardar).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancelar", command=root.destroy).pack(side="left", padx=10)

    root.mainloop()

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

    elif k == BTN_EDIT_JSON:
        editar_json_proyecto()

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

    elif k == BTN_MARK_END:
        current_out = "END"

    elif k == BTN_ADD_SEGMENT:
        if (
            current_in is not None
            and current_out is not None
            and (
                current_out == "END"
                or current_out > current_in
            )
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
