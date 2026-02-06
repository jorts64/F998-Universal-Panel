# F998 – Tabla resumen de comandos (v1.0)

Esta tabla es una **chuleta rápida** del protocolo serie del panel F998. Resume todos los comandos disponibles, sus parámetros y su función.

---

## 🔎 Lectura / Estado

| Comando | Parámetros | Respuesta | Descripción |
|--------|------------|-----------|-------------|
| `ID?` | — | `F998 v1.0` | Identificación del dispositivo |
| `GET` | — | `S P=… D=…` | Estado completo (potenciómetros y digPots) |
| `IN` | — | `K <n>` | Última tecla detectada (`0` = ninguna) |

---

## 🔘 LEDs de botones

| Comando | Parámetros | Descripción |
|--------|------------|-------------|
| `LB` | `n 0|1` | Enciende / apaga LED del botón `n` |
| `LBB` | `n 0|1` | Activa / desactiva blink del botón `n` |
| `LBI` | `n` | Invierte el estado base del LED del botón `n` |

Respuesta común: `OK`

---

## 📊 Matriz / Vúmetros

| Comando | Parámetros | Descripción |
|--------|------------|-------------|
| `VU` | `v p` | Vúmetro `v` (izquierda → derecha) |
| `VUR` | `v p` | Vúmetro `v` (derecha → izquierda) |
| `HP` | `v c` | Cursor horizontal en vúmetro `v` |
| `VB` | `c p` | Barra vertical en columna `c` (crece desde abajo) |
| `ZM` | `c` | Zoom triangular hasta columna `c` |
| `VC` | — | Limpia todos los vúmetros |
| `VF` | — | Llena todos los vúmetros |

---

## 🔋 Batería

| Comando | Parámetros | Descripción |
|--------|------------|-------------|
| `BAT` | `p` | Barra de batería (derecha → izquierda) |
| `BATR` | `p` | Barra de batería (izquierda → derecha) |
| `BATP` | `b 0|1` | Enciende / apaga LED de batería `b` |
| `BATB` | `b 0|1` | Blink LED de batería `b` |
| `BATC` | — | Apaga toda la barra de batería |

📌 `b = 1..4` (numeración humana, invertida internamente)

---

## 🔧 Bajo nivel (matriz)

| Comando | Parámetros | Descripción |
|--------|------------|-------------|
| `LAT` | `i j 0|1` | Enciende / apaga LED (grid `i`, segmento `j`) |
| `LAB` | `i j 0|1` | Activa / desactiva blink de LED |

---

## 🎬 Animaciones

| Comando | Parámetros | Descripción |
|--------|------------|-------------|
| `AN` | `mask` | Ejecuta animación sobre vúmetros seleccionados |

📌 `mask`: bits 0..3 → vúmetros 0..3

---

## ❌ Errores

| Respuesta | Significado |
|----------|-------------|
| `ERR 1` | Comando desconocido o argumentos inválidos |

---

## 🧠 Notas importantes

- Todos los comandos visuales responden `OK`
- Arduino no envía datos espontáneamente
- `IN` está pensado para polling rápido y frecuente
- `GET` es más pesado; usar con menor frecuencia
- El último comando recibido siempre prevalece
- El blink no modifica el estado base del LED

---

**F998 – Tabla de comandos v1.0**

