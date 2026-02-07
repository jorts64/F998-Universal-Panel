# =================================================
# LICENCIA CREATIVE COMMONS 3.0 BY-NC-SA
# Jordi Orts 2026
# =================================================

import serial
import time


class F998:
    # -------------------------------------------------
    # Inicialización / conexión
    # -------------------------------------------------
    def __init__(self, port, baud=115200, timeout=0.05):
        self.ser = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=timeout
        )
        time.sleep(0.2)  # permitir reset del Arduino
        self.flush()

    def close(self):
        self.ser.close()

    def flush(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    # -------------------------------------------------
    # Bajo nivel serie
    # -------------------------------------------------
    def _send(self, cmd):
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.ser.write(cmd.encode("ascii"))

    def _readline(self):
        return self.ser.readline().decode("ascii", errors="ignore").strip()

    def _command(self, cmd):
        self._send(cmd)
        return self._readline()

    # -------------------------------------------------
    # Identificación
    # -------------------------------------------------
    def identificacion(self):
        return self._command("ID?")

    # -------------------------------------------------
    # Lectura de entradas
    # -------------------------------------------------
    def tecla(self):
        """
        Polling rápido de teclado.
        Devuelve:
            int (0 = ninguna tecla)
        """
        self._send("IN")
        r = self._readline()
        if r.startswith("K "):
            try:
                return int(r[2:])
            except ValueError:
                return 0
        return 0

    def estado(self):
        """
        Devuelve un diccionario:
        {
            'P': [pot1..pot9],
            'D': [digPot1..digPot9]
        }
        """
        self._send("GET")
        r = self._readline()

        estado = {"P": [], "D": []}

        if not r.startswith("S"):
            return estado

        partes = r.split()
        for p in partes:
            if p.startswith("P="):
                estado["P"] = [int(x) for x in p[2:].split(",")]
            elif p.startswith("D="):
                estado["D"] = [int(x) for x in p[2:].split(",")]

        return estado

    # -------------------------------------------------
    # LEDs de botones
    # -------------------------------------------------
    def ledButton(self, n, estado=True):
        self._command(f"LB {n} {1 if estado else 0}")

    def ledBlink(self, n, estado=True):
        self._command(f"LBB {n} {1 if estado else 0}")

    def ledInvert(self, n):
        self._command(f"LBI {n}")

    # -------------------------------------------------
    # Matriz / Vúmetros
    # -------------------------------------------------
    def vumetro(self, v, porcentaje):
        self._command(f"VU {v} {porcentaje}")

    def vumetroR(self, v, porcentaje):
        self._command(f"VUR {v} {porcentaje}")

    def horizontalPos(self, v, c):
        self._command(f"HP {v} {c}")

    def verticalBar(self, c, porcentaje):
        self._command(f"VB {c} {porcentaje}")

    def zoom(self, c):
        self._command(f"ZM {c}")

    def vumetroClear(self):
        self._command("VC")

    def vumetroFull(self):
        self._command("VF")

    # -------------------------------------------------
    # Batería
    # -------------------------------------------------
    def bateria(self, porcentaje):
        self._command(f"BAT {porcentaje}")

    def bateriaR(self, porcentaje):
        self._command(f"BATR {porcentaje}")

    def bateriaPos(self, b, estado=True):
        self._command(f"BATP {b} {1 if estado else 0}")

    def bateriaBlink(self, b, estado=True):
        self._command(f"BATB {b} {1 if estado else 0}")

    def bateriaClear(self):
        self._command("BATC")

    # -------------------------------------------------
    # Bajo nivel (matriz)
    # -------------------------------------------------
    def ledAt(self, i, j, estado=True):
        self._command(f"LAT {i} {j} {1 if estado else 0}")

    def ledAtBlink(self, i, j, estado=True):
        self._command(f"LAB {i} {j} {1 if estado else 0}")

    # -------------------------------------------------
    # Animaciones
    # -------------------------------------------------
    def animModo(self, mask):
        self._command(f"AN {mask}")
