# F998 – Nuevo modo: **Modo Macros**

## 📌 Objetivo

Añadir al proyecto **F998** un nuevo modo de funcionamiento llamado **Modo Macros**, que permita asociar acciones configurables a los botones de un panel físico (30 botones) conectado al ordenador mediante comunicación serie.

El comportamiento de cada botón **no estará codificado en el programa**, sino definido en un **archivo de configuración externo**, editable por el usuario.

---

## 🧱 Arquitectura general

```
[ Panel F998 (30 botones) ]
           ↓ (UART / USB-Serial)
[ Módulo Python F998 ]
           ↓
[ Archivo de configuración ]
           ↓
[ Ejecutores de acciones ]
           ↓
[ Sistema operativo / Teclado virtual ]
```

---

## 🔌 Entrada: panel de botones

- El panel envía por el puerto serie el identificador del botón pulsado.
- Formatos posibles:
  - Enteros: `1..30`
  - Cadenas: `"B12\n"` o similares

El módulo Python del F998 interpreta este valor y lo traduce a un identificador de botón interno.

---

## 📁 Configuración del modo macros

### Formato recomendado

**YAML**, por su legibilidad y facilidad de ampliación.  
(JSON también sería viable si el proyecto lo requiere).

### Ejemplo de archivo `macros.yaml`

```yaml
1:
  type: command
  value: "gnome-terminal"

2:
  type: text
  value: "Hola mundo"

3:
  type: keys
  value: ["ctrl", "right"]

4:
  type: command
  value: "firefox https://www.debian.org"
```

Cada clave representa el **número de botón**.

---

## 🎛️ Tipos de acciones soportadas

### 1️⃣ `command`
Ejecuta un comando del sistema operativo.

```yaml
type: command
value: "gnome-terminal"
```

Implementación:
- `subprocess.Popen(..., shell=True)`

---

### 2️⃣ `text`
Escribe texto como si se introdujera por teclado.

```yaml
type: text
value: "Hola mundo"
```

Implementación:
- `pyautogui.write()`

---

### 3️⃣ `keys`
Simula una combinación de teclas.

```yaml
type: keys
value: ["ctrl", "right"]
```

Implementación:
- `pyautogui.hotkey()`

---

## 🧩 Dispatcher de acciones (lógica central)

```python
def ejecutar_macro(boton_id):
    macro = config.get(boton_id)
    if not macro:
        return

    if macro["type"] == "command":
        subprocess.Popen(macro["value"], shell=True)

    elif macro["type"] == "text":
        pyautogui.write(macro["value"])

    elif macro["type"] == "keys":
        pyautogui.hotkey(*macro["value"])
```

---

## 🔁 Integración con el sistema F998

El **Modo Macros** se añade como un modo adicional del sistema F998:

```python
if modo_actual == "macros":
    ejecutar_macro(boton_id)
```

Características:
- El archivo de macros se carga al entrar en el modo
- Puede recargarse sin reiniciar el sistema
- Botones no definidos → no ejecutan ninguna acción

---

## 🚀 Extensiones previstas (opcional)

### 🔹 Secuencias de acciones

```yaml
5:
  type: sequence
  value:
    - {type: keys, value: ["ctrl", "c"]}
    - {type: text, value: "pegado"}
```

---

### 🔹 Delays

```yaml
- {type: delay, value: 0.5}
```

---

### 🔹 Perfiles de macros

```yaml
profiles:
  default:
    1: {type: command, value: "gnome-terminal"}
  edicion:
    1: {type: keys, value: ["ctrl", "s"]}
```

---

## ⚠️ Consideraciones del sistema

- En entornos **Wayland**, la inyección de teclado puede estar limitada.
- Recomendaciones:
  - Ejecutar bajo **X11**
  - O integrar herramientas como **AutoKey** si es necesario

---

## ✅ Beneficios para F998

- Separación total entre hardware y comportamiento
- Configuración editable sin modificar código
- Escalable a más botones o acciones
- Reutilizable para futuros modos del sistema

---

## 📎 Resumen

El **Modo Macros del F998** convierte el panel físico en un dispositivo de automatización configurable, capaz de ejecutar comandos, escribir texto o simular pulsaciones de teclas, todo definido mediante archivos externos y gestionado desde Python.
