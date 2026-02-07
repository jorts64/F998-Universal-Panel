El F998 se vende en AliExpress  como "Live Sound Card Audio Mixer With Interface DJ Mixer Effects Voice Changer Bluetooth-compatible Mixer For Live Streaming Singing" a un precio muy asequible, del orden de 15€.

Este proyecto lo convirte en un panel universal para PC con
* 31 botones
* 7 potenciometros
* 2 faders
* 71 leds

Hemos reemplazado el DSP que lleva por un Arduino Pro Micro, crado un firmware en Arduino IDE, un protocolo de comunicaciones y un script Python para aprovechar el hardware del F998.

El diseño es totalmente flexible. Se puede utilizar tal cual con un ordenador con Linux, ampliar o modificar los modos definidos en el script Python o incluso usar solo el firmware arduino y reemplazar la parte del PC por cualquier otra aplicacion en cualquier sistema operativo.

![](F998working.jpg)

# Guía de Usuario Final – Panel F998

## 📌 Introducción

El **panel F998** es un controlador físico programable diseñado para interactuar con aplicaciones de escritorio mediante comunicación serie. Está pensado para ofrecer **control rápido, ergonómico y visualmente claro** en tareas de edición, reproducción multimedia y automatización mediante macros.

Esta guía está dirigida al **usuario final**, no al desarrollador, y explica cómo usar el panel en el día a día.

---

## 🧭 Conceptos básicos

### 🔘 Botones

- Cada botón tiene un **LED asociado**
- Un botón puede estar:
  - **Apagado** → no pertenece al modo actual
  - **Encendido fijo** → acción activa
  - **Parpadeando** → estado alternativo (pausa, bloqueo, error, modo inactivo)

### 🎚️ Ruedas y potenciómetros

- Las **ruedas (digPot)** tienen una posición central
- Cuando están centradas:
  - no generan acciones
- Al desplazarlas:
  - la velocidad o intensidad depende de cuánto se alejan del centro

---

## 🔁 Modos del panel

El panel funciona siempre en **un único modo activo**.

Los modos se seleccionan mediante botones dedicados:

| Botón | Modo |
|------|------|
| 39 | Kdenlive |
| 38 | SMPlayer |
| 18, 19, 28, 29 | Modos reservados |

Al cambiar de modo:
- se apagan todos los LEDs
- se activan únicamente los controles del nuevo modo

---

## ▶️ Modo Kdenlive

Diseñado para **edición de vídeo**.

Funciones principales:
- Play / pausa
- Avance y retroceso de frames
- Zoom del timeline
- Movimiento rápido por la línea de tiempo
- Cambio de pista
- Corte de clips

Indicadores visuales:
- La matriz 4×9 muestra el nivel de zoom
- La barra de batería indica dirección y velocidad de desplazamiento

Notas importantes:
- Las acciones solo se envían cuando Kdenlive tiene el foco
- Si pierde el foco, el botón de modo parpadea

---

## ▶️ Modo SMPlayer

Diseñado para **reproducción de vídeo**.

Funciones principales:
- Play / pausa
- Avance y retroceso de frames
- Navegación por el vídeo con la rueda
- Control de volumen del reproductor
- Control de volumen del sistema
- Captura de pantalla

Notas importantes:
- Las acciones solo se envían cuando SMPlayer tiene el foco
- El panel se comporta como un control remoto avanzado

---

## ▶️ Modo Macros

Permite asignar **acciones personalizadas** a los botones mediante un archivo de configuración.

Tipos de acciones:
- Ejecutar comandos
- Enviar combinaciones de teclas
- Escribir texto o snippets
- Ejecutar secuencias de acciones

El usuario puede modificar el archivo `macros.yaml` para cambiar el comportamiento sin tocar el código.

Notas importantes:
- Algunos caracteres especiales del teclado español no pueden reproducirse y se sustituyen por un marcador visual
- Las macros se ejecutan con un pequeño retardo para evitar repeticiones accidentales

---

## 🔍 Indicadores y alertas

### ⚠️ Potenciómetros desajustados

Al cambiar de modo, el panel puede requerir que:
- las ruedas estén centradas
- ciertos potenciómetros estén a cero

Si no es así:
- la matriz 4×9 muestra la columna correspondiente parpadeando
- el modo no se activa hasta corregir la posición

---

## 🛠️ Buenas prácticas de uso

- Esperar un instante tras pulsar un botón (delay humano)
- No forzar ruedas fuera de su zona útil
- Comprobar siempre el LED del modo activo
- Usar el panel con la aplicación correcta en foco

---

## ✔️ Estado del sistema

El panel F998 es:
- estable
- robusto
- extensible

Está pensado para evolucionar con nuevos modos y funcionalidades.

---

## 📄 Documentación relacionada

- Modo Kdenlive – Documentación técnica
- Modo SMPlayer – Documentación técnica
- Modo Macros – Documentación técnica

---

> **Nota final**: El panel F998 está diseñado para ser intuitivo. Si los LEDs indican el estado correcto, el panel está listo para usarse.


