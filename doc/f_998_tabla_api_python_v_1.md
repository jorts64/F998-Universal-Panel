# F998 – Tabla resumen API Python (v1.0 revisada)

> **Estado:** alineada 100 % con firmware y protocolo

---

## Conexión

| Método | Descripción |
|------|-------------|
| `F998(port, baud=115200)` | abre conexión |
| `close()` | cierra puerto |
| `identificacion()` | ID del dispositivo |

---

## Lectura de entradas

| Método | Devuelve |
|------|----------|
| `tecla()` | `int` (0 = ninguna) |
| `estado()` | `{ 'P': [1..9], 'D': [1..9] }` |

---

## LEDs botones

| Método | Acción |
|------|--------|
| `ledButton(n, s)` | LED botón |
| `ledBlink(n, s)` | blink botón |
| `ledInvert(n)` | invierte LED |

---

## Matriz / vúmetros

| Método | Acción |
|------|--------|
| `vumetro(v, p)` | vúmetro L→R |
| `vumetroR(v, p)` | vúmetro R→L |
| `verticalBar(c, p)` | barra vertical |
| `horizontalPos(v, c)` | punto horizontal |
| `zoom(c)` | zoom triangular |
| `vumetroClear()` | limpia matriz |
| `vumetroFull()` | llena matriz |

---

## Batería

| Método | Acción |
|------|--------|
| `bateria(p)` | barra batería |
| `bateriaR(p)` | barra invertida |
| `bateriaPos(b, s)` | LED batería |
| `bateriaBlink(b, s)` | blink batería |
| `bateriaClear()` | limpia batería |

---

## Bajo nivel

| Método | Acción |
|------|--------|
| `ledAt(i, j, s)` | LED directo |
| `ledAtBlink(i, j, s)` | blink directo |

---

## Animaciones

| Método | Acción |
|------|--------|
| `animModo(mask)` | animación |

---

## Notas

- No hay nombres en inglés
- Python **no cachea estado**
- Un comando → una acción

---

**F998 – Tabla API Python v1.0 revisada**

