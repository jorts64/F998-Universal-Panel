# =================================================
# MODO MACROS (extraído completo del original)
# =================================================

import time
import yaml
import subprocess
import pyautogui


# =================================================
# CONSTANTES
# =================================================

BTN_MACROS = 29
MACROS_FILE = "macros.yaml"

MACRO_DELAY = 0.3
MACRO_STEP_DELAY = 0.1


# =================================================
# VARIABLES GLOBALES (idénticas al original)
# =================================================

macros = {}
last_macro_time = 0


# =================================================
# KEYMAP ES (copiado intacto)
# =================================================

KEYMAP_ES = {
    "<": "94",
    ">": "50+94",
    "º": "49",
    "ª": "49",
    "\\": "51",
    "|": "50+51",
    "!": "50+10",
    "¡": "21",
    "@": "50+11",
    "·": "49",
    "#": "50+12",
    "$": "50+13",
    "~": "50+49",
    "%": "50+14",
    "&": "50+16",
    "(": "50+18",
    ")": "50+19",
    "=": "21",
    "?": "50+61",
    "¿": "49",
    "'": "48",
    '"': "50+48",
    "[": "34",
    "]": "35",
    "+": "50+21",
    "*": "50+17",
    "{": "50+34",
    "}": "50+35",
    "ç": "49",
    "Ç": "49",
    ";": "47",
    ":": "50+47",
    ",": "59",
    ".": "60",
    "_": "50+20",
    "-": "20",
}


# =================================================
# FUNCIONES
# =================================================

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


# =================================================
# INIT / LOOP / EXIT
# =================================================

def macros_init(f):
    global macros

    macros = cargar_macros()

    for b in macros.keys():
        f.ledButton(b, True)


def macros_loop(f, k, estado):
    global last_macro_time

    now = time.time()

    if k in macros and now - last_macro_time > MACRO_DELAY:
        last_macro_time = now
        ejecutar_macro(macros[k])


def macros_exit(f):
    pass
