# =================================================
# MODO KDENLIVE (extraído del script original)
# =================================================

import time
import subprocess
from pynput.keyboard import Controller, Key


# -------------------------------------------------
# CONSTANTES (copiadas del script original)
# -------------------------------------------------

BTN_KDENLIVE = 39

BTN_PLAY = 27
BTN_FRAME_LEFT = 36
BTN_FRAME_RIGHT = 37

BTN_CUT = 10
BTN_TRACK_UP = 20
BTN_TRACK_DOWN = 30

BTN_DELAY = 0.30
WHEEL_DELAY = 0.08
ZOOM_DELAY = 0.12
VOLUME_DELAY = 0.15

ACCEL_RUEDA = {1: 1, 2: 4, 3: 8}
VOLUME_STEP = 2  # %


# -------------------------------------------------
# VARIABLES GLOBALES (idénticas al original)
# -------------------------------------------------

kdenlive_en_pausa = False
last_button = 0
last_wheel = 0
last_zoom = 0
last_volume = 0
zoom_level = 4

kbd = Controller()


# -------------------------------------------------
# FUNCIONES
# -------------------------------------------------

def kdenlive_init(f):
    global kdenlive_en_pausa, zoom_level

    kdenlive_en_pausa = False
    zoom_level = 4

    f.ledButton(BTN_PLAY, True)
    f.zoom(zoom_level)


def kdenlive_loop(f, k, estado, kdenlive_en_foco):
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


def kdenlive_exit(f):
    f.bateriaClear()
