print("Jordi Orts 2026 CC 3.0 BY-NC-SA")

# =================================================
# LICENCIA CREATIVE COMMONS 3.0 BY-NC-SA
# Jordi Orts 2026
# =================================================


import time
import subprocess
from pynput.keyboard import Controller, Key
import yaml
import pyautogui
import json
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog
import socket
import threading
from f998 import F998


# =================================================
# CONFIGURACIÓN GENERAL
# =================================================

MODOS = [18, 19, 28, 29, 38, 39]
DELAY_POLL = 0.05

BTN_DELAY = 0.30
WHEEL_DELAY = 0.08
ZOOM_DELAY = 0.12
VOLUME_DELAY = 0.15

BTN_KDENLIVE = 39
BTN_SMPLAYER = 38
BTN_MACROS = 29
BTN_PREEDITOR = 28
MACROS_FILE = "macros.yaml"

ACCEL_RUEDA = {1: 1, 2: 4, 3: 8}
VOLUME_STEP = 2  # %

# Comunes

BTN_PLAY = 27
BTN_FRAME_LEFT = 36
BTN_FRAME_RIGHT = 37

# Kdenlive

BTN_CUT = 10
BTN_TRACK_UP = 20
BTN_TRACK_DOWN = 30

# SMPlayer

BTN_SCREENSHOT = 26
BTN_GOTO_START = 34
BTN_GOTO_END = 35
# SMPlayer – Marcadores
BTN_MARK_ADD  = 15   # Ctrl + A
BTN_MARK_PREV = 24   # Ctrl + B
BTN_MARK_NEXT = 25   # Ctrl + N

MPV_SOCKET = "/tmp/mpvsocket"

# Editor SMPlayer

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
# INICIALIZACIÓN
# =================================================

kbd = Controller()
f = F998("/dev/ttyACM0")
print(f.identificacion())

# =================================================
# UTILIDADES LED / MATRIZ
# =================================================

def apagar_todos_los_leds():
    for b in range(1, 40):
        f.ledBlink(b, False)
        f.ledButton(b, False)

def encender_leds_modo():
    for b in MODOS:
        f.ledBlink(b, False)
        f.ledButton(b, True)

def limpiar_matriz():
    f.vumetroClear()
    f.bateriaClear()

def limpiar_blink_matriz():
    for c in range(0, 9):
        for i in range(0, 4):
            f.ledAtBlink(i, c, False)

# =================================================
# CONTROL DE FOCO
# =================================================


def proceso_en_foco(nombre_proceso):
    """
    Devuelve True si el proceso indicado tiene el foco.
    La detección se realiza mediante PID de la ventana activa.
    Compatible con Ubuntu y Debian.
    """
    try:
        pid = subprocess.check_output(
            ["xdotool", "getactivewindow", "getwindowpid"],
            text=True
        ).strip()

        proc = subprocess.check_output(
            ["ps", "-p", pid, "-o", "comm="],
            text=True
        ).strip().lower()

        return nombre_proceso.lower() in proc

    except Exception:
        return False

def smplayer_en_foco():
    return proceso_en_foco("smplayer")


def kdenlive_en_foco():
    return proceso_en_foco("kdenlive")

# =================================================
# COMPROBACIÓN PREVIA
# =================================================

def comprobar_condiciones_entrada(boton):
    f.ledBlink(boton, True)
    f.ledButton(boton, True)

    venimos_de_error = False

    while True:
        estado = f.estado()
        error = False

        if not venimos_de_error:
            limpiar_matriz()
            limpiar_blink_matriz()

        # digPot 1..7 centrados
        for a in range(1, 8):
            if estado["D"][a - 1] != 3:
                error = True
                c = a - 1
                for i in range(0, 4):
                    f.ledAtBlink(i, c, True)

        # pot 8..9 a 0
        for a in range(8, 10):
            if estado["P"][a - 1] != 0:
                error = True
                c = a - 1
                for i in range(0, 4):
                    f.ledAtBlink(i, c, True)

        if error:
            venimos_de_error = True
            time.sleep(0.1)
            continue

        break

    f.ledBlink(boton, False)
    f.ledButton(boton, True)
    limpiar_matriz()
    limpiar_blink_matriz()

# =================================================
# PLANTILLA DE MODO
# =================================================

def modo_base(boton_modo, botones, on_init, on_loop, on_exit):
    apagar_todos_los_leds()
    limpiar_matriz()
    limpiar_blink_matriz()

    f.ledBlink(boton_modo, True)
    f.ledButton(boton_modo, True)

    for b in botones:
        f.ledButton(b, True)

    on_init()

    while True:
        k = f.tecla()
        estado = f.estado()

        if k in MODOS and k != boton_modo:
            on_exit()
            return k

        on_loop(k, estado)
        time.sleep(DELAY_POLL)

# =================================================
# KDENLIVE v2 (COMPLETO)
# =================================================

kdenlive_en_pausa = False
last_button = last_wheel = last_zoom = last_volume = 0
zoom_level = 4

def kdenlive_init():
    global kdenlive_en_pausa, zoom_level
    kdenlive_en_pausa = False
    zoom_level = 4
    f.ledButton(BTN_PLAY, True)
    f.zoom(zoom_level)

def kdenlive_loop(k, estado):
    global kdenlive_en_pausa
    global last_button, last_wheel, last_zoom, last_volume, zoom_level

    foco = kdenlive_en_foco()

    f.ledBlink(BTN_KDENLIVE, not foco)
    if foco:
        f.ledButton(BTN_KDENLIVE, True)
    else:
        return

    now = time.time()

    # ---------- BOTONES ----------
    if k and now - last_button > BTN_DELAY:
        last_button = now

        if k == BTN_PLAY:
            kbd.tap(Key.space)
            kdenlive_en_pausa = not kdenlive_en_pausa
            f.ledBlink(BTN_PLAY, kdenlive_en_pausa)
            if not kdenlive_en_pausa:
                f.ledButton(BTN_PLAY, True)

        elif k == BTN_FRAME_LEFT:
            kbd.tap(Key.left)

        elif k == BTN_FRAME_RIGHT:
            kbd.tap(Key.right)

        elif k == BTN_TRACK_UP:
            kbd.tap(Key.up)

        elif k == BTN_TRACK_DOWN:
            kbd.tap(Key.down)

        elif k == BTN_CUT:
            kbd.tap('x')

    # ---------- ZOOM (digPot 6) ----------
    dz = estado["D"][5] - 3
    if dz != 0 and now - last_zoom > ZOOM_DELAY:
        last_zoom = now
        if dz > 0:
            kbd.press(Key.ctrl); kbd.tap('+'); kbd.release(Key.ctrl)
            zoom_level = min(8, zoom_level + 1)
        else:
            kbd.press(Key.ctrl); kbd.tap('-'); kbd.release(Key.ctrl)
            zoom_level = max(0, zoom_level - 1)
        f.zoom(zoom_level)

    # ---------- RUEDA SEGUNDOS (digPot 7) ----------
    dc = estado["D"][6] - 3
    if dc != 0 and now - last_wheel > WHEEL_DELAY:
        last_wheel = now
        pasos = ACCEL_RUEDA.get(abs(dc), 1)
        for _ in range(pasos):
            kbd.press(Key.shift)
            kbd.tap(Key.right if dc > 0 else Key.left)
            kbd.release(Key.shift)
        vel = min(75, pasos * 10)
        f.bateria(vel) if dc > 0 else f.bateriaR(vel)
    else:
        f.bateriaClear()

    # ---------- VOLUMEN SISTEMA (digPot 1) ----------
    dv = estado["D"][0] - 3
    if dv != 0 and now - last_volume > VOLUME_DELAY:
        last_volume = now
        pasos = abs(dv)
        if dv > 0:
            subprocess.call(
                ["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%+"]
            )
        else:
            subprocess.call(
                ["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%-"]
            )

def kdenlive_exit():
    f.bateriaClear()

def modo_kdenlive():
    return modo_base(
        BTN_KDENLIVE,
        [
            BTN_PLAY,
            BTN_FRAME_LEFT,
            BTN_FRAME_RIGHT,
            BTN_TRACK_UP,
            BTN_TRACK_DOWN,
            BTN_CUT,
        ],
        kdenlive_init,
        kdenlive_loop,
        kdenlive_exit
    )

# =================================================
# MODO SMPlayer
# =================================================
smplayer_en_pausa = False
last_button_sm = 0
last_wheel_sm = 0
last_volume_smplayer = 0 
last_volume_system = 0 
last_pause_check = 0
cached_pause_state = None

# --------------------------------------------------
# ENVÍO SIMPLE (sin esperar respuesta)
# --------------------------------------------------

def mpv_send(cmd_dict):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(MPV_SOCKET)

        sock.sendall((json.dumps(cmd_dict) + "\n").encode())
        sock.close()

    except Exception:
        return None


# --------------------------------------------------
# CONSULTA (lectura segura por línea)
# --------------------------------------------------

def mpv_query(cmd_dict):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(MPV_SOCKET)

        sock.sendall((json.dumps(cmd_dict) + "\n").encode())

        # Lectura robusta hasta salto de línea
        file = sock.makefile()
        line = file.readline()

        sock.close()

        if line:
            return json.loads(line)

    except Exception:
        return None


# --------------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------------

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


def update_play_led():

    global last_pause_check
    global cached_pause_state

    now = time.time()

    # Consultar cada 300 ms
    if now - last_pause_check < 0.3:
        return

    last_pause_check = now

    p = mpv_get_pause()
    if p is None:
        return

    # Solo actuar si cambia el estado
    if p != cached_pause_state:

        cached_pause_state = p

        # Siempre encendido en modo activo
        f.ledButton(BTN_PLAY, True)

        # Parpadea si está en pausa
        f.ledBlink(BTN_PLAY, p)


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
    hilo.join()   # <- espera pero loop principal no está bloqueado

    return resultado["valor"]


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

def smplayer_init():
    global smplayer_en_pausa
    smplayer_en_pausa = False

    # Play activo por defecto
    f.ledButton(BTN_PLAY, True)

def smplayer_core(k, estado):

    global last_button_sm
    global last_wheel_sm
    global last_volume_smplayer
    global last_volume_system

    now = time.time()

    # --------------------------------------------------
    # SINCRONIZACIÓN LED PLAY
    # --------------------------------------------------
    update_play_led()

    # --------------------------------------------------
    # BOTONES
    # --------------------------------------------------
    if k and now - last_button_sm > BTN_DELAY:

        last_button_sm = now

        if k == BTN_PLAY:

            p = mpv_get_pause()
            if p is not None:
                mpv_set_pause(not p)

        elif k == BTN_FRAME_LEFT:
            kbd.tap(',')

        elif k == BTN_FRAME_RIGHT:
            kbd.tap('.')

        elif k == BTN_SCREENSHOT:
            kbd.tap('s')

        elif k == BTN_GOTO_START:
            mpv_send({"command": ["seek", 0, "absolute"]})

        elif k == BTN_GOTO_END:
            mpv_send({"command": ["seek", -60, "absolute"]})

        elif k == BTN_MARK_ADD:
            kbd.press(Key.ctrl)
            kbd.tap('a')
            kbd.release(Key.ctrl)

        elif k == BTN_MARK_PREV:
            kbd.press(Key.ctrl)
            kbd.tap('b')
            kbd.release(Key.ctrl)

        elif k == BTN_MARK_NEXT:
            kbd.press(Key.ctrl)
            kbd.tap('n')
            kbd.release(Key.ctrl)

    # --------------------------------------------------
    # RUEDA (digPot 7)
    # --------------------------------------------------
    if now - last_wheel_sm > WHEEL_DELAY:

        last_wheel_sm = now
        v = estado["D"][6]

        if v == 0:
            kbd.tap(Key.page_down)
        elif v == 1:
            kbd.tap(Key.down)
        elif v == 2:
            kbd.tap(Key.left)
        elif v == 4:
            kbd.tap(Key.right)
        elif v == 5:
            kbd.tap(Key.up)
        elif v == 6:
            kbd.tap(Key.page_up)

    # --------------------------------------------------
    # VOLUMEN SISTEMA (digPot 1)
    # --------------------------------------------------
    dv = estado["D"][0] - 3
    if dv != 0 and now - last_volume_system > VOLUME_DELAY:

        last_volume_system = now
        pasos = abs(dv)

        if dv > 0:
            subprocess.call(
                ["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%+"]
            )
        else:
            subprocess.call(
                ["amixer", "-q", "set", "Master", f"{pasos * VOLUME_STEP}%-"]
            )

    # --------------------------------------------------
    # VOLUMEN SMPLAYER (digPot 2)
    # --------------------------------------------------
    dv = estado["D"][1] - 3
    if dv != 0 and now - last_volume_smplayer > VOLUME_DELAY:

        last_volume_smplayer = now

        for _ in range(abs(dv)):
            kbd.tap('9' if dv < 0 else '0')


def smplayer_exit():
    pass

def modo_smplayer():
    return modo_base(
        BTN_SMPLAYER,
        [
            BTN_PLAY,
            BTN_FRAME_LEFT,
            BTN_FRAME_RIGHT,
            BTN_SCREENSHOT,
            BTN_GOTO_START,
            BTN_GOTO_END,
            BTN_MARK_ADD,
            BTN_MARK_PREV,
            BTN_MARK_NEXT,
        ],
        smplayer_init,
        smplayer_loop,
        smplayer_exit
    )


# =================================================
# MODO MACROS
# =================================================
macros = {}
last_macro_time = 0
MACRO_DELAY = 0.3   # evitar dobles disparos
MACRO_STEP_DELAY = 0.1   # 100 ms entre acciones


KEYMAP_ES = {
    # < >
    "<": "94",      #OK
    ">": "50+94",   #OK

    # º ª
    "º": "49",      #NO
    "ª": "49",     #NO

    # Barra inversa y vertical
    "\\": "51",     #OK
    "|": "50+51",   #OK

    # Exclamaciones
    "!": "50+10",   #OK
    "¡": "21",

    # Arroba y centro
    "@": "50+11",   #OK
    "·": "49",      #NO

    # Almohadilla / dólar
    "#": "50+12",   #OK
    "$": "50+13",   #OK

    # Tilde y porcentaje
    "~": "50+49",   #OK
    "%": "50+14",   #OK

    # Ampersand
    "&": "50+16",   #OK

    # Paréntesis
    "(": "50+18",   #OK
    ")": "50+19",   #OK

    # Igual / interrogación
    "=": "21",      #OK
    "?": "50+61",   #OK
    "¿": "49",      #NO

    # Comillas
    "'": "48",      #OK
    '"': "50+48",   #OK

    # Corchetes
    "[": "34",      #OK
    "]": "35",      #OK

    # Más / asterisco
    "+": "50+21",   #OK
    "*": "50+17",   #OK

    # Llaves
    "{": "50+34",   #OK
    "}": "50+35",   #OK

    # c cedilla
    "ç": "49",      #NO
    "Ç": "49",      #NO
    
    # Punto y coma / coma / dos puntos
    ";": "47",      #OK
    ":": "50+47",   #OK
    ",": "59",      #OK
    ".": "60",      #OK

    # Guiones
    "_": "50+20",   #OK
    "-": "20",      #OK
}

def escribir_texto_es(texto):
    for c in texto:
        if c == "\n":
            subprocess.run(["xdotool", "key", "Return"], check=False)

        elif c == "\t":
            subprocess.run(["xdotool", "key", "Tab"], check=False)

        elif c in KEYMAP_ES:
            subprocess.run(
                ["xdotool", "key", KEYMAP_ES[c]],
                check=False
            )

        else:
            subprocess.run(
                ["xdotool", "type", "--delay", "0", c],
                check=False
            )

def cargar_macros():
    try:
        with open(MACROS_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            # normalizar claves a int
            return {int(k): v for k, v in data.items()}
    except Exception as e:
        print("Error cargando macros:", e)
        return {}

def ejecutar_macro(macro):
    tipo = macro.get("type")
    valor = macro.get("value")

    if tipo == "command":
        subprocess.Popen(valor, shell=True)

    elif tipo == "text":
        escribir_texto_es(str(valor))

    elif tipo == "keys":
        if isinstance(valor, list):
            pyautogui.hotkey(*valor)
    elif tipo == "sequence":
        for paso in valor:
            ejecutar_macro(paso)
            time.sleep(MACRO_STEP_DELAY)



def macros_init():
    global macros
    macros = cargar_macros()

    # Encender botones con macro definida
    for b in macros.keys():
        f.ledButton(b, True)

def macros_loop(k, estado):
    global last_macro_time

    now = time.time()

    if k in macros and now - last_macro_time > MACRO_DELAY:
        last_macro_time = now
        ejecutar_macro(macros[k])

def macros_exit():
    pass

def modo_macros():
    return modo_base(
        BTN_MACROS,
        botones=[],   # los enciende macros_init()
        on_init=macros_init,
        on_loop=macros_loop,
        on_exit=macros_exit
    )


# =================================================
# MODO Editor SMPlayer
# =================================================

# ----- PREEDITOR STATE -----

proyecto = None

current_chapter_name = None
current_source_file = None

current_segments = []
current_in = None
current_out = None


def update_project_leds():

    if proyecto is not None:
        f.ledButton(BTN_NEW_PROJECT, False)
        f.ledButton(BTN_CLOSE_PROJECT, True)
    else:
        f.ledButton(BTN_NEW_PROJECT, True)
        f.ledButton(BTN_CLOSE_PROJECT, False)

def update_segment_matrix():

    # Limpiar matriz completa columnas 0–7
    for col in range(8):
        for row in range(4):
            f.ledAt(row, col, False)

    # -----------------------------------------
    # Segmentos actuales (fila 2)
    # -----------------------------------------
    for idx, seg in enumerate(current_segments):
        if idx < 8:
            f.ledAt(2, idx, True)

    # -----------------------------------------
    # IN provisional (fila 0)
    # -----------------------------------------
    if current_in is not None and len(current_segments) < 8:
        f.ledAt(0, len(current_segments), True)

    # -----------------------------------------
    # OUT provisional (fila 1)
    # -----------------------------------------
    if current_out is not None and len(current_segments) < 8:
        f.ledAt(1, len(current_segments), True)

    # -----------------------------------------
    # Capítulos guardados (fila 3)
    # -----------------------------------------
    if proyecto and proyecto.get("jobs"):
        last_job = proyecto["jobs"][-1]

        for idx, seg in enumerate(last_job.get("segments", [])):
            if idx < 8:
                f.ledAt(3, idx, True)


def update_editor_buttons():

    # --------------------------------------------------
    # PROYECTO
    # --------------------------------------------------

    if proyecto is None:
        f.ledButton(BTN_NEW_PROJECT, True)
        f.ledButton(BTN_CLOSE_PROJECT, False)
        f.ledButton(BTN_EXPORT_PROJECT, False)
    else:
        f.ledButton(BTN_NEW_PROJECT, False)
        f.ledButton(BTN_CLOSE_PROJECT, True)
        f.ledButton(BTN_EXPORT_PROJECT, True)

    # --------------------------------------------------
    # CAPÍTULO
    # --------------------------------------------------

    if proyecto is None:
        f.ledButton(BTN_NEW_CHAPTER, False)
        f.ledButton(BTN_SAVE_CHAPTER, False)
    else:
        f.ledButton(BTN_NEW_CHAPTER, True)

        if current_segments:
            f.ledButton(BTN_SAVE_CHAPTER, True)
        else:
            f.ledButton(BTN_SAVE_CHAPTER, False)

    # --------------------------------------------------
    # SEGMENTACIÓN
    # --------------------------------------------------

    if proyecto is None or current_chapter_name is None:
        f.ledButton(BTN_MARK_IN, False)
        f.ledButton(BTN_MARK_OUT, False)
        f.ledButton(BTN_ADD_SEGMENT, False)
        f.ledButton(BTN_DELETE_LAST, False)
        return

    # IN / OUT siempre activos si hay capítulo
    f.ledButton(BTN_MARK_IN, True)
    f.ledButton(BTN_MARK_OUT, True)

    # ADD solo si IN y OUT válidos
    if (
        current_in is not None
        and current_out is not None
        and current_out > current_in
    ):
        f.ledButton(BTN_ADD_SEGMENT, True)
    else:
        f.ledButton(BTN_ADD_SEGMENT, False)

    # DELETE solo si hay segmentos
    if current_segments:
        f.ledButton(BTN_DELETE_LAST, True)
    else:
        f.ledButton(BTN_DELETE_LAST, False)



def export_project_json():
    if not proyecto:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"f998_project_{timestamp}.json"

    data = proyecto.copy()
    data["created_at"] = datetime.now().isoformat()

    with open(filename, "w", encoding="utf-8") as fjson:
        json.dump(data, fjson, indent=2, ensure_ascii=False)


def preeditor_segment_logic(k, estado):
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

        nombre = tk_prompt("Nuevo Proyecto", "Nombre del proyecto:")

        if nombre:
            proyecto = {
                "project_name": nombre,
                "jobs": []
            }

            update_editor_buttons()

    elif k == BTN_CLOSE_PROJECT and proyecto is not None:

        confirm = tk_prompt("Cerrar Proyecto", "Escribe 'SI' para confirmar:")

        if confirm == "SI":

            proyecto = None
            current_segments.clear()
            current_in = None
            current_out = None

            update_segment_matrix()
            update_editor_buttons()

    elif k == BTN_EXPORT_PROJECT:
        export_project_json()

    # ---------- CAPITULO ----------

    elif k == BTN_NEW_CHAPTER:

        if not proyecto:
            return

        # Pausar reproducción
        mpv_set_pause(True)

        nombre = tk_prompt("Nuevo Capítulo", "Nombre del capítulo (ej 1x03):")

        if nombre:
            current_chapter_name = nombre
            current_source_file = mpv_get_path()

            current_segments.clear()
            current_in = None
            current_out = None

            update_editor_buttons()
            update_segment_matrix()


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
            update_editor_buttons()
            update_segment_matrix()

    # ---------- SEGMENTACION ----------

    elif k == BTN_MARK_IN:
        t = mpv_get_time()
        if t is not None:
            current_in = t
            update_segment_matrix()

    elif k == BTN_MARK_OUT:
        t = mpv_get_time()
        if t is not None:
            current_out = t
            update_editor_buttons()
            update_segment_matrix()

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
            update_editor_buttons()
            update_segment_matrix()

    elif k == BTN_DELETE_LAST:
        if current_segments:
            current_segments.pop()
            update_editor_buttons()
            update_segment_matrix()

def preeditor_init():

    # Estado visual proyecto
    update_project_leds()

    # Estado visual segmentos
    update_segment_matrix()

    # LED modo siempre activo al entrar
    f.ledButton(BTN_PREEDITOR, True)

    update_editor_buttons()

def preeditor_loop(k, estado):
    global cached_pause_state

    foco = smplayer_en_foco()

    # LED modo PreEditor
    f.ledBlink(BTN_PREEDITOR, not foco)

    if not foco:
        return

    cached_pause_state = None
    update_play_led()

    f.ledButton(BTN_PREEDITOR, True)

    # Reutilizamos toda la lógica SMPlayer
    smplayer_core(k, estado)

    # Añadimos capa de segmentación
    preeditor_segment_logic(k, estado)


def modo_preeditor():

    update_project_leds()
    update_segment_matrix()

    return modo_base(
        BTN_PREEDITOR,   # 28
        [
            BTN_PLAY,
            BTN_FRAME_LEFT,
            BTN_FRAME_RIGHT,
            BTN_SCREENSHOT,
            BTN_GOTO_START,
            BTN_GOTO_END,
            BTN_MARK_ADD,
            BTN_MARK_PREV,
            BTN_MARK_NEXT,

            BTN_NEW_PROJECT,
            BTN_CLOSE_PROJECT,
            BTN_EXPORT_PROJECT,
            BTN_NEW_CHAPTER,
            BTN_SAVE_CHAPTER,
            BTN_MARK_IN,
            BTN_MARK_OUT,
            BTN_ADD_SEGMENT,
            BTN_DELETE_LAST,
        ],
        preeditor_init,
        preeditor_loop,
        lambda: None
    )


# =================================================
# MODO DUMMY
# =================================================

def modo_dummy(b):
    return modo_base(b, [], lambda: None, lambda k, e: None, lambda: None)

# =================================================
# BUCLE PRINCIPAL
# =================================================

def bucle_principal():
    apagar_todos_los_leds()
    limpiar_matriz()
    limpiar_blink_matriz()
    encender_leds_modo()

    while True:
        k = f.tecla()

        if k == BTN_KDENLIVE:
            comprobar_condiciones_entrada(k)
            modo_kdenlive()

        elif k == BTN_SMPLAYER:
            comprobar_condiciones_entrada(k)
            modo_smplayer()

        elif k == BTN_MACROS:
            comprobar_condiciones_entrada(k)
            modo_macros()

        elif k == BTN_PREEDITOR:
            comprobar_condiciones_entrada(k)
            modo_preeditor()

        elif k in MODOS:
            comprobar_condiciones_entrada(k)
            modo_dummy(k)

        else:
            time.sleep(DELAY_POLL)

# =================================================
# MAIN
# =================================================

bucle_principal()
