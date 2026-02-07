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
BTN_GOTO_START = 16
BTN_GOTO_END = 17

MPV_SOCKET = "/tmp/mpvsocket"


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

def kdenlive_en_foco():
    try:
        nombre = subprocess.check_output(
            ["xdotool", "getactivewindow", "getwindowname"],
            stderr=subprocess.DEVNULL
        ).decode(errors="ignore").lower()
        return "kdenlive" in nombre
    except Exception:
        return False

def smplayer_en_foco():
    try:
        nombre = subprocess.check_output(
            ["xdotool", "getactivewindow", "getwindowname"],
            stderr=subprocess.DEVNULL
        ).decode(errors="ignore").lower()
        return "smplayer" in nombre
    except Exception:
        return False

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

def mpv_cmd(cmd):
    try:
        subprocess.call(
            f'echo \'{cmd}\' | socat - "{MPV_SOCKET}"',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def smplayer_init():
    global smplayer_en_pausa
    smplayer_en_pausa = False

    # Play activo por defecto
    f.ledButton(BTN_PLAY, True)

def smplayer_loop(k, estado):
    global smplayer_en_pausa
    global last_button_sm, last_wheel_sm, last_volume_sm
    global last_volume_smplayer, last_volume_system

    foco = smplayer_en_foco()

    # LED del modo: encendido si foco, blink si no
    f.ledBlink(BTN_SMPLAYER, not foco)
    if foco:
        f.ledButton(BTN_SMPLAYER, True)
    else:
        return

    now = time.time()

    # ---------- BOTONES ----------
    if k and now - last_button_sm > BTN_DELAY:
        last_button_sm = now

        if k == BTN_PLAY:
            kbd.tap(Key.space)
            smplayer_en_pausa = not smplayer_en_pausa
            f.ledBlink(BTN_PLAY, smplayer_en_pausa)
            if not smplayer_en_pausa:
                f.ledButton(BTN_PLAY, True)

        elif k == BTN_FRAME_LEFT:
            kbd.tap(',')

        elif k == BTN_FRAME_RIGHT:
            kbd.tap('.')

        elif k == BTN_SCREENSHOT:
            kbd.tap('s')

        elif k == BTN_GOTO_START:
            mpv_cmd('{ "command": ["seek", 0, "absolute"] }')

        elif k == BTN_GOTO_END:
            mpv_cmd('{ "command": ["seek", -60, "absolute"] }')

    # ---------- RUEDA (digPot 7) ----------
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


    # ---------- VOLUMEN SISTEMA (digPot 1) ----------
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


    # ---------- VOLUMEN SMPLAYER (digPot 2) ----------
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

        elif k in MODOS:
            comprobar_condiciones_entrada(k)
            modo_dummy(k)

        else:
            time.sleep(DELAY_POLL)

# =================================================
# MAIN
# =================================================

bucle_principal()
