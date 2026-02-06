# Modo Macros – F998

## 📌 Descripción general

El **Modo Macros** permite asociar acciones configurables a los botones del panel F998 mediante un archivo de configuración externo (`macros.yaml`).

Las acciones **no están codificadas en el programa**, sino descritas en YAML, lo que permite modificar el comportamiento del panel sin tocar el código Python.

Este modo está pensado para:
- Lanzar aplicaciones
- Enviar combinaciones de teclas
- Insertar texto o snippets
- Ejecutar secuencias complejas de acciones

---

## 📁 Archivo de configuración: `macros.yaml`

### Estructura general

```yaml
<BOTON>:
  type: <tipo>
  value: <valor>
```

- `<BOTON>`: código lógico del botón F998 (por ejemplo `10`–`37`)
- `type`: tipo de acción
- `value`: contenido asociado a la acción

Ejemplo simple:

```yaml
10:
  type: command
  value: "firefox"
```

---

## 🎛️ Tipos de macros soportados

### 1️⃣ `command`

Ejecuta un comando del sistema operativo.

```yaml
type: command
value: "gnome-terminal"
```

Implementación:
- `subprocess.Popen(..., shell=True)`

Uso típico:
- Lanzar aplicaciones
- Ejecutar scripts

---

### 2️⃣ `keys`

Simula una combinación de teclas.

```yaml
type: keys
value: ["ctrl", "c"]
```

Implementación:
- Envío de pulsaciones mediante `pynput` o `xdotool key`

Uso típico:
- Atajos de teclado
- Navegación

---

### 3️⃣ `text`

Inserta texto utilizando **inyección por keycodes** adaptada al teclado español (ES).

```yaml
type: text
value: "Hola mundo"
```

Características:
- Soporta `\n` (Enter) y `\t` (Tab)
- Utiliza un mapa explícito de keycodes (`KEYMAP_ES`)
- Los caracteres **no reproducibles** del teclado español se traducen a una *dead quote* (`'`)

Ejemplo avanzado:

```yaml
value: "<html>\n<body>\n</body>\n</html>"
```

---

### ⚠️ Limitaciones conocidas del tipo `text`

Algunos caracteres específicos del teclado español **no pueden reproducirse de forma determinista** mediante inyección de teclado:

- `º`
- `ª`
- `·`
- `¿`
- `ç`, `Ç`

Estos caracteres se sustituyen intencionadamente por una **dead quote (`'`)** como marcador visual.

Este comportamiento es:
- Intencionado
- Determinista
- Documentado

---

### 4️⃣ `sequence`

Permite definir **macros compuestas** por varias acciones encadenadas.

```yaml
type: sequence
value:
  - {type: keys, value: ["ctrl", "c"]}
  - {type: text, value: "pegado"}
```

Características:
- Las acciones se ejecutan en orden
- Se aplica un pequeño retardo entre pasos (`MACRO_STEP_DELAY`)
- Cada paso reutiliza el mismo motor de macros

Tipos permitidos dentro de una secuencia:
- `command`
- `keys`
- `text`
- `sequence` (no recursivo, por ahora)

---

## ⏱️ Delays y control de repetición

Para evitar ejecuciones accidentales:

- Existe un retardo mínimo entre macros (`MACRO_DELAY`)
- Las secuencias aplican además un retardo entre pasos (`MACRO_STEP_DELAY`)

Estos valores son configurables en el script Python.

---

## 🎹 Numeración de botones

- Los botones se identifican por su **código lógico F998**
- Normalmente se usan los valores `10–37`
- Los botones de modo (`18, 19, 28, 29, 38, 39`) **no deberían** usarse para macros

Ejemplo válido:

```yaml
27:
  type: text
  value: "Hola desde el boton 27"
```

---

## 🧠 Filosofía de diseño

- El archivo YAML describe el *qué*
- El código Python implementa el *cómo*
- No hay lógica específica por botón en el programa
- El sistema es extensible sin romper compatibilidad

---

## 🚀 Posibles extensiones futuras

El diseño actual permite añadir fácilmente:

- `delay:` por paso en secuencias
- `repeat:` para bucles
- `condition:` (foco de ventana, modo activo)
- Varios archivos de macros por perfil

---

## ✔️ Estado del modo

- Funcional
- Estable
- Documentado
- Apto para uso diario

El **Modo Macros** se considera **cerrado en versión v1.1**.

