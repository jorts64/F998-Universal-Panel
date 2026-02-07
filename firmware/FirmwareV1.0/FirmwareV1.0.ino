//
// Jordi Orts 2026
// CC 3.0 BY-NC-SA
//

#include "F998.h"

#define SERIAL_BAUD 115200
#define CMD_BUF_LEN 64

char cmdBuf[CMD_BUF_LEN];
uint8_t cmdPos = 0;

void procesarSerial() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      cmdBuf[cmdPos] = '\0';
      ejecutarComando(cmdBuf);
      cmdPos = 0;
    }
    else if (cmdPos < CMD_BUF_LEN - 1) {
      cmdBuf[cmdPos++] = c;
    }
  }
}

int toInt(const char* s) {
  return atoi(s);
}

bool is01(const char* s) {
  return (s[0] == '0' || s[0] == '1') && s[1] == '\0';
}

void ejecutarComando(char* line) {
  char* argv[6];
  int argc = 0;

  char* tok = strtok(line, " ");
  while (tok && argc < 6) {
    argv[argc++] = tok;
    tok = strtok(NULL, " ");
  }

  if (argc == 0) return;

  // ---------------- IDENTIDAD ----------------
  if (!strcmp(argv[0], "ID?")) {
    Serial.println("F998 v1.0");
    return;
  }

  // ---------------- GET ----------------
  if (!strcmp(argv[0], "GET")) {
    Serial.print("S P=");
    for (int i = 1; i <= 9; i++) {
      Serial.print(pot(i));
      if (i < 9) Serial.print(",");
    }
    Serial.print(" D=");
    for (int i = 1; i <= 9; i++) {
      Serial.print(digPot(i));
      if (i < 9) Serial.print(",");
    }
    Serial.println();
    return;
  }
  // ---------------- IN ----------------
  if (!strcmp(argv[0], "IN")) {
    int k = tecla();
    Serial.print("K ");
    Serial.println(k);
    return;
  }

  // ---------------- LED BOTONES ----------------
  if (!strcmp(argv[0], "LB") && argc == 3 && is01(argv[2])) {
    ledButton(toInt(argv[1]), argv[2][0] == '1');
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "LBB") && argc == 3 && is01(argv[2])) {
    ledBlink(toInt(argv[1]), argv[2][0] == '1');
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "LBI") && argc == 2) {
    ledInvert(toInt(argv[1]));
    Serial.println("OK");
    return;
  }

  // ---------------- VÚMETROS / MATRIZ ----------------
  if (!strcmp(argv[0], "VU") && argc == 3) {
    vumetro(toInt(argv[1]), toInt(argv[2]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "VUR") && argc == 3) {
    vumetroR(toInt(argv[1]), toInt(argv[2]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "HP") && argc == 3) {
    horizontalPos(toInt(argv[1]), toInt(argv[2]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "VB") && argc == 3) {
    verticalBar(toInt(argv[1]), toInt(argv[2]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "ZM") && argc == 2) {
    zoom(toInt(argv[1]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "VC")) {
    vumetroClear();
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "VF")) {
    vumetroFull();
    Serial.println("OK");
    return;
  }

  // ---------------- BATERÍA ----------------
  if (!strcmp(argv[0], "BAT") && argc == 2) {
    bateria(toInt(argv[1]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "BATR") && argc == 2) {
    bateriaR(toInt(argv[1]));
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "BATP") && argc == 3 && is01(argv[2])) {
    bateriaPos(toInt(argv[1]), argv[2][0] == '1');
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "BATB") && argc == 3 && is01(argv[2])) {
    bateriaBlink(toInt(argv[1]), argv[2][0] == '1');
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "BATC")) {
    bateriaClear();
    Serial.println("OK");
    return;
  }

  // ---------------- ANIMACIÓN ----------------
  if (!strcmp(argv[0], "AN") && argc == 2) {
    animModo((uint8_t)toInt(argv[1]));
    Serial.println("OK");
    return;
  }

  // ---------------- BAJO NIVEL ----------------
  if (!strcmp(argv[0], "LAT") && argc == 4 && is01(argv[3])) {
    ledAt(toInt(argv[1]), toInt(argv[2]), argv[3][0] == '1');
    Serial.println("OK");
    return;
  }

  if (!strcmp(argv[0], "LAB") && argc == 4 && is01(argv[3])) {
    ledAtBlink(toInt(argv[1]), toInt(argv[2]), argv[3][0] == '1');
    Serial.println("OK");
    return;
  }

  // ---------------- ERROR ----------------
  Serial.println("ERR 1");   // comando desconocido o argumentos incorrectos
}


// ==================================================
// SETUP
// ==================================================

void setup() {
  F998_setup();
}

// ==================================================
// LOOP PRINCIPAL
// ==================================================

void loop() {
  procesarSerial();
  updateBlink();
}
