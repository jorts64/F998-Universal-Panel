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

from modes.kdenlive import *
from modes.smplayer import *
from modes.preeditor import *
from modes.macros import *

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
    Versión robusta basada en PID real de la ventana activa.
    """

    try:
        # Obtener ventana activa
        wid = subprocess.check_output(
            ["xdotool", "getactivewindow"],
            text=True
        ).strip()

        if not wid:
            return False

        # Obtener PID real de esa ventana
        pid = subprocess.check_output(
            ["xdotool", "getwindowpid", wid],
            text=True
        ).strip()

        if not pid:
            return False

        # Obtener nombre real del proceso
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
# MODO kdenlive
# =================================================

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
        lambda: kdenlive_init(f),
        lambda k, estado: kdenlive_loop(f, k, estado, kdenlive_en_foco),
        lambda: kdenlive_exit(f),
    )

# =================================================
# MODO SMPlayer
# =================================================

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
        lambda: smplayer_init(f),
        lambda k, estado: smplayer_loop(f, k, estado, smplayer_en_foco),
        lambda: smplayer_exit(f),
    )


# =================================================
# MODO MACROS
# =================================================

def modo_macros():
    return modo_base(
        BTN_MACROS,
        botones=[],
        on_init=lambda: macros_init(f),
        on_loop=lambda k, estado: macros_loop(f, k, estado),
        on_exit=lambda: macros_exit(f),
    )

# =================================================
# MODO Editor SMPlayer
# =================================================

def modo_preeditor():
    return modo_base(
        BTN_PREEDITOR,
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
            BTN_EDIT_JSON,
            BTN_MARK_END,
        ],
        lambda: preeditor_init(f),
        lambda k, estado: preeditor_loop(f, k, estado, smplayer_en_foco),
        lambda: preeditor_exit(f),
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
