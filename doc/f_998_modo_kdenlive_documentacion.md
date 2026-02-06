# Modo Kdenlive – F998

## 📌 Descripción general

El **Modo Kdenlive** del panel F998 está diseñado para controlar de forma eficiente y ergonómica la edición de vídeo en **Kdenlive**, utilizando controles físicos (botones y potenciómetros) y comunicación serie.

Este modo **no utiliza HID**, sino que envía órdenes al sistema únicamente cuando la ventana de Kdenlive tiene el foco, evitando interferencias con otras aplicaciones.

---

## 🎛️ Filosofía de funcionamiento

- El panel actúa como **controlador especializado** para Kdenlive
- Las acciones solo se ejecutan cuando Kdenlive está en foco
- Los botones usados en el modo **siempre están encendidos o en parpadeo**, nunca apagados
- El parpadeo indica **estado alternativo** (pausa, desarmado, etc.)
- Existe un **delay humano** para evitar repeticiones accidentales

---

## 🔁 Activación del modo

- El modo Kdenlive está asociado al **botón 39**
- Estados del botón 39:
  - **Encendido fijo** → modo activo (ARM)
  - **Parpadeo** → modo desactivado (DISARM)

Cuando el modo está desactivado:
- El script **solo consulta el último botón pulsado**
- No se envían acciones a Kdenlive

---

## ⏱️ Delays

Para garantizar un uso cómodo:

- **Delay en botones**: 300 ms
- **Delay en rueda (digPot)**: configurable, aplicado a cada paso

Esto evita avances excesivos al pulsar o girar controles.

---

## 🎚️ Controles asignados

### 🔄 Ruedas (digPot)

#### 🎞️ Rueda de cursor – `digPot(7)`

- Valor centrado (`3`) → sin acción
- `< 3` → retroceder en el timeline (segundos)
- `> 3` → avanzar en el timeline (segundos)

Acción enviada:
- `Shift + Flecha izquierda / derecha`

El número de pasos depende de la distancia al centro, usando una tabla de aceleración configurable.

---

#### 🔍 Zoom del timeline – `digPot(6)`

- Valor centrado (`3`) → sin acción
- `< 3` → disminuir zoom
- `> 3` → aumentar zoom

Visualización:
- Se utiliza la matriz 4×9 mediante la función `zoom()`

---

#### 🔊 Volumen del sistema – `digPot(1)`

- Controla el **volumen global del sistema**, no el del clip
- Implementado mediante `amixer`
- Incrementos/decrementos proporcionales al desplazamiento

---

### 🎚️ Potenciómetros analógicos

#### 🔊 Volumen (fader)

- `pot(9)`
- Control continuo del volumen del sistema

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

- **Botón 36** → frame anterior (`Flecha izquierda`)
- **Botón 37** → frame siguiente (`Flecha derecha`)

---

### 🧩 Navegación de pistas

- **Botón 30** → pista inferior (`Flecha abajo`)
- **Botón 20** → pista superior (`Flecha arriba`)

---

### ✂️ Cortar clip

- **Botón 10**
- Acción: atajo de corte de Kdenlive

---

## 🎛️ Indicadores visuales

### 🔋 Barra de batería (dirección y velocidad)

- Se utiliza `bateria()` y `bateriaR()`
- Nunca se llena completamente la barra
- Indica:
  - Dirección del movimiento
  - Intensidad / velocidad

---

### 🧱 Matriz 4×9

- Visualiza el nivel de zoom
- Se limpia al cambiar de modo
- No se utiliza para vúmetros en este modo

---

## 🔍 Control de foco

Antes de enviar cualquier orden:

- El script comprueba si **Kdenlive tiene el foco**
- Si no lo tiene:
  - No se envían teclas
  - El botón 39 pasa a **parpadeo**
- Al recuperar el foco:
  - El botón 39 se enciende fijo
  - Se reanuda la ejecución normal

Este mecanismo evita interferencias durante la reproducción de vídeo.

---

## 🧠 Estado interno

- El modo mantiene estado de:
  - reproducción / pausa
  - armado / desarmado
- Al entrar en el modo:
  - Se inicializan LEDs
  - Se validan potenciómetros

---

## ✔️ Estado del modo

- Funcional
- Estable
- Usable en edición real
- Integrado en el bucle principal de modos

El **Modo Kdenlive** se considera **estable (v1)** y apto para uso diario.

---

## 🚀 Posibles mejoras futuras

- Control de herramientas específicas
- Jog/shuttle avanzado
- Edición multicámara
- Feedback desde Kdenlive

---

> **Nota**: Este modo forma parte del sistema multiperfil del panel F998 y convive con otros modos como Macros o SMPlayer.

