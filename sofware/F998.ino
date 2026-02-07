//
// Funciones hardware F998
// (c) Jordi Orts 2026
// CC BY-NC-SA
//

bool ledStat[40];

#include <TM1628.h>

// Pines (los tuyos)
TM1628 module(7, 9, 8);
const int L0 = 14;  // C1
const int L1 = 3;   // C2
const int L2 = 15;  // C4
const int L3 = 2;   // C5
const int PIN_TECLA_9 = 16;


const int L_PINS[4] = { L0, L1, L2, L3 };

// ---- Configuración ----
const int MAX_GRID = 16;     // TM1628 soporta hasta 16
const int MAX_SEG  = 16;     // usamos setSegments16()

// RAM local de LEDs (GRID × SEG)
uint16_t gridState[MAX_GRID];

const int SIG_PIN = A10;

const int S0_PIN = 18;
const int S1_PIN = 19;
const int S2_PIN = 20;
const int S3_PIN = 21;

// i = 1..9
// valor = S3 S2 S1 S0 (binario)
const uint8_t potChannel[10] = {
  0,    // índice 0 no usado
  13,   // 1
  15,   // 2
  11,   // 3
  14,   // 4
  10,   // 5
  7,    // 6
  6,    // 7
  9,    // 8
  8     // 9
};

const int potMax[10] = {
  0,    // índice 0 no usado
  683,
  684,
  684,
  684,
  684,
  684,
  684,
  684,
  684
};

const int MUX_S[4] = {S0_PIN, S1_PIN, S2_PIN, S3_PIN};
const int MUX_ADC  = SIG_PIN;   // pin analógico común del multiplexor

// ---------------- BLINK ----------------
bool ledBlinkStat[40];              // LEDs de botones
bool gridBlink[MAX_GRID][16];       // matriz (grid × seg)
bool blinkPhase = false;
unsigned long lastBlink = 0;
const unsigned long BLINK_MS = 350;



// --------------------------------------------------
void F998_setup() {
  pinMode(PIN_TECLA_9, INPUT_PULLUP);
  
  module.setupDisplay(true, 2);
  module.setAlphaNumeric(false);
  module.clearDisplay();
  
  // Inicializar RAM local
  for (int g = 0; g < MAX_GRID; g++) {
    gridState[g] = 0x0000;
    module.setSegments16(0x0000, g);
  }

  pinMode(S0_PIN, OUTPUT);
  pinMode(S1_PIN, OUTPUT);
  pinMode(S2_PIN, OUTPUT);
  pinMode(S3_PIN, OUTPUT);

  delay(100);
}

int teclaTM() {
  uint32_t k = module.getButtons();

  if (k == 0) return 0;

  if (k & 0x00000001) return 10;
  if (k & 0x00000002) return 11;
  if (k & 0x00000004) return 12;
  if (k & 0x00000008) return 13;
  if (k & 0x00000010) return 14;
  if (k & 0x00000020) return 15;
  if (k & 0x00000040) return 16;
  if (k & 0x00000080) return 17;

  if (k & 0x00000100) return 18;
  if (k & 0x00000200) return 19;

  if (k & 0x00010000) return 20;
  if (k & 0x00020000) return 21;
  if (k & 0x00040000) return 22;
  if (k & 0x00080000) return 23;
  if (k & 0x00100000) return 24;
  if (k & 0x00200000) return 25;
  if (k & 0x00400000) return 26;
  if (k & 0x00800000) return 27;

  if (k & 0x01000000) return 28;
  if (k & 0x02000000) return 29;

  return 0;   // por si acaso
}

int teclaExtra() {
  // ---------- ESTADO BASE ----------
  pinMode(L0, INPUT_PULLUP);
  pinMode(L1, INPUT_PULLUP);
  pinMode(L2, INPUT_PULLUP);
  pinMode(L3, INPUT_PULLUP);
  delayMicroseconds(5);

  if (digitalRead(L0) == LOW) return 36;
  if (digitalRead(L1) == LOW) return 37;
  if (digitalRead(L2) == LOW) return 38;
  if (digitalRead(L3) == LOW) return 39;

  // ---------- L1 = OUTPUT LOW ----------
  pinMode(L1, OUTPUT);
  digitalWrite(L1, LOW);
  delayMicroseconds(5);

  if (digitalRead(L0) == LOW) return 31;

  pinMode(L1, INPUT_PULLUP);

  // ---------- L2 = OUTPUT LOW ----------
  pinMode(L2, OUTPUT);
  digitalWrite(L2, LOW);
  delayMicroseconds(5);

  if (digitalRead(L0) == LOW) return 33;
  if (digitalRead(L1) == LOW) return 34;
  if (digitalRead(L3) == LOW) return 35;

  pinMode(L2, INPUT_PULLUP);

  // ---------- L3 = OUTPUT LOW ----------
  pinMode(L3, OUTPUT);
  digitalWrite(L3, LOW);
  delayMicroseconds(5);

  if (digitalRead(L0) == LOW) return 30;
  if (digitalRead(L1) == LOW) return 32;

  return 0;
}

void restaurarLineas() {
  for (int i = 0; i < 4; i++) {
    pinMode(L_PINS[i], INPUT);
  }
}

int tecla() {
  int t;

  // 1) Teclado TM1628
  t = teclaTM();
  if (t != 0) return t;

  // 2) Tecla directa (9)
  if (digitalRead(PIN_TECLA_9) == LOW) return 9;

  // 3) Teclas extra
  t = teclaExtra();
  restaurarLineas();
  return t;
}


int pot(int i) {
  if (i < 1 || i > 9) return 0;

  uint8_t ch = potChannel[i];
  for (int b = 0; b < 4; b++) {
    digitalWrite(MUX_S[b], (ch >> b) & 0x01);
  }

  delayMicroseconds(5);

  int raw = analogRead(MUX_ADC);
  int maxv = potMax[i];

  if (raw < 0) raw = 0;
  if (raw > maxv) raw = maxv;

  // 🔴 CLAVE: usar long
  long percent = (long)raw * 100L / maxv;

  return (int)percent;
}

int digPot(int i) {
  int p = pot(i);   // 0..100

  if (p < 12)  return 0;
  if (p < 24)  return 1;
  if (p < 36)  return 2;
  if (p < 64)  return 3;
  if (p < 76)  return 4;
  if (p < 88)  return 5;
  return 6;
}

void vumetro(int i, int porcentaje) {
  // Validaciones
  if (i < 0 || i > 3) return;
  if (porcentaje < 0) porcentaje = 0;
  if (porcentaje > 100) porcentaje = 100;

  // Número de LEDs a encender (0..9)
  int leds = (porcentaje * 9 + 50) / 100;

  uint16_t mask = (leds == 0) ? 0 : ((1 << leds) - 1);

  gridState[i] = mask;
  module.setSegments16(gridState[i], i);
}


void bateria(int porcentaje) {
  int leds = 0;

  if (porcentaje < 25)
    leds = 1;
  else if (porcentaje <= 50)
    leds = 2;
  else if (porcentaje <= 90)
    leds = 3;
  else
    leds = 4;

  // Apagar los 4 LEDs primero
  for (int g = 0; g < 4; g++) {
    gridState[g] &= ~(1 << 9);   // limpiar SEG 9
    module.setSegments16(gridState[g], g);
  }

  // Encender desde la derecha hacia la izquierda
  for (int i = 0; i < leds; i++) {
    int grid = i;               // 0,1,2,3
    gridState[grid] |= (1 << 9);
    module.setSegments16(gridState[grid], grid);
  }
}

void ledAt(int i, int j, bool estado) {
  // Validaciones
  if (i < 0 || i > 6) return;
  if (j < 0 || j > 9) return;

  int grid = i; 

  if (estado == HIGH)
    gridState[grid] |= (1 << j);
  else
    gridState[grid] &= ~(1 << j);

  module.setSegments16(gridState[grid], grid);
}


void ledTeclaAt(int i, int j, bool estado) {
  // Validaciones
  if (i < 0 || i > 2) return;
  if (j < 0 || j > 9) return;

  int grid = 4 + i;   // filas de botones empiezan en GRID 4

  if (estado == HIGH)
    gridState[grid] |= (1 << j);
  else
    gridState[grid] &= ~(1 << j);

  module.setSegments16(gridState[grid], grid);
}

void ledButton(int i, bool estado) {
  int columna = i % 10;
  int fila = ( i / 10 ) -1; 
  ledTeclaAt( fila, columna, estado);
  ledStat[i] = estado;  
}

void ledInvert(int i) {
  bool nuevo = !ledStat[i];
  ledButton(i, nuevo);
  ledStat[i] = nuevo;  
}

void animModo(uint8_t mask) {
  const int step = 20;     // velocidad (más bajo = más suave)
  const int delayMs = 15;

  // Subida
  for (int v = 0; v <= 100; v += step) {
    for (int i = 0; i < 4; i++) {
      if (mask & (1 << i)) {
        vumetro(i, v);
      }
    }
    delay(delayMs);
  }

  delay(200);

  // Bajada
  for (int v = 100; v >= 0; v -= step) {
    for (int i = 0; i < 4; i++) {
      if (mask & (1 << i)) {
        vumetro(i, v);
      }
    }
    delay(delayMs);
  }
}

uint8_t mascaraModo(int sel) {
  switch (sel) {
    case -3: return 0b0001; // CPU
    case -2: return 0b0010; // TEMP
    case -1: return 0b0100; // RAM
    case  0: return 0b1000; // GPU
    case  1: return 0b0011; // Orange Pi
    case  2: return 0b0110; // Aireamos
    case  3: return 0b1100; // vúmetros 2 + 3 (inferiores
    default: return 0;
  }
}

void updateBlink() {
  unsigned long now = millis();
  if (now - lastBlink < BLINK_MS) return;

  lastBlink = now;
  blinkPhase = !blinkPhase;

  // --- LEDs botones ---
  for (int i = 0; i < 40; i++) {
    if (ledBlinkStat[i]) {
      int col = i % 10;
      int row = (i / 10) - 1;
      ledTeclaAt(row, col, blinkPhase ? ledStat[i] : !ledStat[i]);
    }
  }

  // --- Matriz ---
  for (int g = 0; g < MAX_GRID; g++) {
    uint16_t out = gridState[g];
    for (int s = 0; s < 16; s++) {
      if (gridBlink[g][s]) {
        if (blinkPhase)
          out ^= (1 << s);
      }
    }
    module.setSegments16(out, g);
  }
}

void ledBlink(int n, bool s) {
  if (n < 0 || n > 39) return;
  ledBlinkStat[n] = s;
}

void ledAtBlink(int i, int j, bool s) {
  if (i < 0 || i >= MAX_GRID) return;
  if (j < 0 || j > 15) return;
  gridBlink[i][j] = s;
}

void vumetroR(int v, int porcentaje) {
  if (v < 0 || v > 3) return;
  porcentaje = constrain(porcentaje, 0, 100);

  int leds = (porcentaje * 9 + 50) / 100;
  uint16_t mask = 0;

  for (int i = 0; i < leds; i++)
    mask |= (1 << (8 - i));

  gridState[v] = mask;
  module.setSegments16(mask, v);
}

void horizontalPos(int v, int c) {
  if (v < 0 || v > 3) return;
  if (c < 0 || c > 8) return;

  gridState[v] = (1 << c);
  module.setSegments16(gridState[v], v);
}

void verticalBar(int c, int porcentaje) {
  if (c < 0 || c > 8) return;
  porcentaje = constrain(porcentaje, 0, 100);

  int leds = (porcentaje * 4 + 50) / 100;   // 0..4

  for (int g = 0; g < 4; g++) {
    int grid = 3 - g;   // ⬅️ invertir: empezar desde abajo

    if (g < leds)
      gridState[grid] |= (1 << c);
    else
      gridState[grid] &= ~(1 << c);

    module.setSegments16(gridState[grid], grid);
  }
}

void restauraMatrix() {
  for (int g = 0; g < MAX_GRID; g++)
    module.setSegments16(gridState[g], g);
}

void vumetroClear() {
  for (int i = 0; i < 4; i++) {
    gridState[i] = 0;
    module.setSegments16(0, i);
  }
}

void vumetroFull() {
  for (int i = 0; i < 4; i++) {
    gridState[i] = 0x01FF; // 9 LEDs
    module.setSegments16(gridState[i], i);
  }
}

void zoom(int c) {
  if (c < 0) c = 0;
  if (c > 8) c = 8;

  // Reescribir completamente la matriz de vúmetros (grid 0..3)
  for (int g = 0; g < 4; g++) {
    gridState[g] = 0;   // 🔴 limpiar TODO
  }

  // Construir columnas 0..c
  for (int col = 0; col <= c; col++) {

    int niveles = (col / 2) + 1;   // 1,1,2,2,3,3,4,4,5
    if (niveles > 4) niveles = 4;

    // Encender desde abajo
    for (int n = 0; n < niveles; n++) {
      int grid = 3 - n;            // abajo → arriba
      gridState[grid] |= (1 << col);
    }
  }

  // Volcar a hardware
  for (int g = 0; g < 4; g++) {
    module.setSegments16(gridState[g], g);
  }
}

void bateriaR(int porcentaje) {
  int leds = 0;

  if (porcentaje < 25)
    leds = 0;
  else if (porcentaje < 50)
    leds = 1;
  else if (porcentaje < 75)
    leds = 2;
  else if (porcentaje < 100)
    leds = 3;
  else
    leds = 4;

  // Apagar los 4 LEDs primero
  for (int g = 0; g < 4; g++) {
    gridState[g] &= ~(1 << 9);
  }

  // Encender desde la IZQUIERDA (grid 3 → 0 visualmente)
  for (int i = 0; i < leds; i++) {
    int grid = 3 - i;          // ⬅️ sentido inverso a bateria()
    gridState[grid] |= (1 << 9);
  }

  // Volcar a hardware
  for (int g = 0; g < 4; g++) {
    module.setSegments16(gridState[g], g);
  }
}

void bateriaPos(int b, bool s) {
  if (b < 1 || b > 4) return;

  int grid = 4 - b;   // ⬅️ invertir numeración

  if (s)
    gridState[grid] |= (1 << 9);
  else
    gridState[grid] &= ~(1 << 9);

  module.setSegments16(gridState[grid], grid);
}

void bateriaBlink(int b, bool s) {
  if (b < 1 || b > 4) return;

  int grid = 4 - b;   // ⬅️ mismo mapeo
  gridBlink[grid][9] = s;
}

void bateriaClear() {
  for (int i = 0; i < 4; i++) {
    gridState[i] &= ~(1 << 9);
    module.setSegments16(gridState[i], i);
  }
}
