# Modo SMPlayer – F998

## 📌 Descripción general

El **Modo SMPlayer** del panel **F998** está orientado al control cómodo y preciso de la reproducción de vídeo mediante **SMPlayer** (y su backend **mpv**), utilizando controles físicos y comunicación serie.

Este modo reutiliza criterios ergonómicos y filosóficos del modo Kdenlive, pero adaptados a un entorno de **reproducción**, no de edición.

---

## 🎛️ Filosofía de funcionamiento

- El panel actúa como **control remoto avanzado** para SMPlayer
- No se utiliza HID
- Las acciones se envían como atajos de teclado o comandos IPC
- Los botones activos **siempre están encendidos o en parpadeo**
- El parpadeo indica estados alternativos (pausa, desarmado, error de foco)

---

## 🔁 Activación del modo

- El **Modo SMPlayer** está asociado al **botón 38**

Estados del botón 38:
- **Encendido fijo** → modo activo
- **Parpadeo** → modo seleccionado pero bloqueado (foco incorrecto)

Al entrar en el modo:
- Se apagan todos los LEDs
- Se encienden únicamente los controles operativos del modo

---

## 🔍 Control de foco

Antes de ejecutar cualquier acción:

- El script comprueba si **SMPlayer** tiene el foco
- Si no lo tiene:
  - No se envían órdenes
  - El botón 38 pasa a **parpadeo**
- Al recuperar el foco:
  - El botón 38 se enciende fijo
  - Se reanudan las acciones

Este mecanismo evita interferencias con otras aplicaciones.

---

## ⏱️ Delays

- **Delay humano en botones**: 300 ms
- **Delay en ruedas (`digPot`)**: activo en este modo

Esto permite un control preciso sin sobrepasar acciones.

---

## 🎚️ Controles asignados

### 🔄 Ruedas (digPot)

#### 🎞️ Rueda de navegación – `digPot(7)`

Se aprovechan los **atajos nativos de SMPlayer**:

| Valor digPot(7) | Acción enviada |
|---------------|---------------|
| 0 | PageDown |
| 1 | Flecha abajo |
| 2 | Flecha izquierda |
| 3 | (centro) – sin acción |
| 4 | Flecha derecha |
| 5 | Flecha arriba |
| 6 | PageUp |

Esta rueda permite:
- navegación por la línea de tiempo
- saltos rápidos y finos

---

#### 🔊 Volumen SMPlayer – `digPot(2)`

- Controla el **volumen interno de SMPlayer**
- Acciones enviadas:
  - `9` → subir volumen
  - `0` → bajar volumen
- El sentido está ajustado ergonómicamente

---

#### 🔊 Volumen del sistema – `digPot(1)`

- Control del volumen global del sistema
- Implementado mediante `amixer`

---

### 🎚️ Potenciómetros analógicos

- No utilizados en este modo

---

## ⌨️ Botones

### ▶️ Play / Pause

- **Botón 27**
- Acción: `Espacio`

Estados del LED:
- **Encendido fijo** → reproducción
- **Parpadeo** → pausa

---

### ⏪⏩ Avance / retroceso de frame

- **Botón 36** → frame anterior (`,`)
- **Botón 37** → frame siguiente (`.`)

---

### 📸 Captura de pantalla

- **Botón 26**
- Acción: tecla `S`

---

### 🎬 Saltos especiales (mpv IPC)

SMPlayer lanza `mpv` con soporte IPC:

```bash
--input-ipc-server=/tmp/mpvsocket
```

Se aprovecha este canal para acciones precisas:

- **Botón 16** → saltar al inicio del vídeo
- **Botón 17** → saltar a 1 minuto antes del final

Los comandos se envían mediante `socat`.

---

## 🎛️ Indicadores visuales

### 🔋 Barra de batería

- Indica:
  - Dirección de desplazamiento
  - Intensidad del salto
- Nunca se llena completamente la barra

---

### 🧱 Matriz 4×9

- No se utiliza para vúmetros
- Puede emplearse para alertas de estado o errores

---

## 🧠 Estado interno

El modo mantiene estado de:
- reproducción / pausa
- foco de ventana

Al entrar en el modo:
- Se inicializan LEDs
- Se limpian indicadores gráficos

---

## ✔️ Estado del modo

- Funcional
- Estable
- Adecuado para reproducción diaria

El **Modo SMPlayer** se considera **estable (v1)**.

---

## 🚀 Posibles mejoras futuras

- Control de velocidad de reproducción
- Subtítulos
- Selección de pistas de audio
- Feedback desde mpv

---

> **Nota**: Este modo convive con otros perfiles del panel F998 como Kdenlive o Macros y se selecciona desde el bucle principal de modos.

