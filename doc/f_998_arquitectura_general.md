# Arquitectura General del Sistema F998

## 📌 Visión global

El sistema **F998** es una arquitectura híbrida **hardware + software** diseñada para ofrecer un control físico avanzado sobre aplicaciones de escritorio mediante **comunicación serie**, sin utilizar HID.

El objetivo principal es separar claramente:

- **Hardware**: lectura fiable de entradas y control visual de salidas
- **Firmware**: abstracción del panel y protocolo estable
- **Software PC (Python)**: lógica de aplicación, modos y automatización

Esta separación permite que el panel sea **universal, extensible y reutilizable**.

---

## 🧱 Capas del sistema

La arquitectura se divide en **tres capas principales**:

```
┌──────────────────────────────┐
│        Aplicaciones PC       │
│  (Kdenlive, SMPlayer, etc.)  │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│     Software F998 (Python)   │
│  - bucle principal de modos  │
│  - lógica de cada modo       │
│  - macros y automatización  │
└──────────────▲───────────────┘
               │  Serie
┌──────────────┴───────────────┐
│     Firmware F998 (Arduino)  │
│  - lectura de entradas       │
│  - control de LEDs           │
│  - protocolo serie           │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│        Hardware F998         │
│  - botones                  │
│  - potenciómetros            │
│  - matriz de LEDs            │
└──────────────────────────────┘
```

---

## 🔌 Hardware F998

### Componentes principales

- Microcontrolador: **Arduino Pro Micro (ATmega32U4)**
- Driver de LEDs y teclas: **TM1628**
- Multiplexor analógico: **CD74HC4067**
- Matriz de LEDs: **4×9**
- Barra de batería: **4 LEDs**
- Botones iluminados: **30**

### Características clave

- Lectura estable y sin falsos positivos
- Numeración lógica única para botones y LEDs
- Hardware independiente del modo de uso

---

## 🧠 Firmware F998 (Arduino)

### Responsabilidades

- Inicialización del hardware
- Lectura de:
  - botones (TM1628 + matriz externa)
  - potenciómetros
- Control de:
  - LEDs de botones
  - matriz 4×9
  - barra de batería
- Ejecución de animaciones simples (blink, zoom, etc.)

### API expuesta

El firmware expone una API estable que incluye funciones como:

- `tecla()`
- `pot(i)` / `digPot(i)`
- `ledButton()` / `ledBlink()`
- `zoom()` / `bateria()`

El firmware **no conoce el significado funcional** de las acciones.

---

## 🔄 Protocolo de comunicación serie

### Principios

- Basado en texto
- Comandos simples y legibles
- Sin dependencias de HID
- Polling frecuente desde el PC

### Tipos de comandos

- Lectura de entradas (`IN`)
- Control de LEDs
- Control de matriz
- Animaciones

El protocolo está diseñado para ser:
- fácil de depurar
- extensible
- estable a largo plazo

---

## 🖥️ Software F998 (Python)

### Rol principal

El software en Python es el **cerebro del sistema**.

Se encarga de:

- Gestionar el bucle principal
- Seleccionar el modo activo
- Implementar la lógica de cada modo
- Traducir eventos físicos en acciones del sistema
- Gestionar foco de ventanas
- Ejecutar macros definidas por el usuario

---

## 🔁 Bucle principal de modos

El sistema funciona siempre en un **único modo activo**.

Flujo general:

1. Inicialización
2. Encendido de botones de modo
3. Espera de selección de modo
4. Validación de potenciómetros
5. Entrada en bucle del modo
6. Retorno al bucle principal al cambiar de modo

Este diseño evita interferencias entre modos.

---

## 🧩 Modos del sistema

### Modos implementados

- **Modo Kdenlive**: edición de vídeo
- **Modo SMPlayer**: reproducción multimedia
- **Modo Macros**: automatización configurable

Cada modo:

- define sus controles activos
- gestiona su estado interno
- controla LEDs y visualización
- puede bloquearse por foco o error

---

## 🧠 Gestión de estado

El sistema mantiene estados como:

- modo activo
- foco de ventana
- estados play/pause
- delays de entrada

Los estados están aislados por modo.

---

## 🎛️ Feedback visual

El panel proporciona feedback continuo mediante:

- LEDs de botones
- parpadeo (blink)
- matriz 4×9
- barra de batería

El usuario puede operar el panel **sin mirar la pantalla**.

---

## 📐 Principios de diseño

- Separación clara de responsabilidades
- No usar HID
- Control explícito del estado
- Feedback visual constante
- Robustez frente a errores
- Extensibilidad por diseño

---

## 🚀 Evolución futura

La arquitectura permite añadir:

- nuevos modos
- perfiles por aplicación
- feedback bidireccional
- comunicación con APIs externas

Sin necesidad de rediseñar el sistema base.

---

## ✔️ Estado de la arquitectura

- Coherente
- Probada en uso real
- Documentada
- Lista para evolución

El sistema F998 cuenta con una **arquitectura sólida y sostenible**.

