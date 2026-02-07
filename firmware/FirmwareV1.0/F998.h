//
// Jordi Orts 2026
// CC 3.0 BY-NC-SA
//


void F998_setup();

// Rangos de los parametros
// v=0..3
// p=0..100
// c=0..8
// b=0..3
// n=0..40
// f=0..255
// a=1..9
// i=0..6
// j=0..9
// mask=0..15

// leer entradas
int tecla();                                // devuelve codigo letra pulsada (0 ninguna)
int pot(int a);                             // devuelve porcentaje potenciometro a
int digPot(int a);                          // devuelve valor potenciometro a discreto (0..6)
// vumetros
void vumetro(int v, int porcentaje);        // llena de izquierda a derecha el vumetro v según porcentaje
void vumetroR(int v, int porcentaje);       // llena de derecha a izquierda el vumetro v según porcentaje
void horizontalPos(int v, int c);           // enciende el led en la columna c del vumetro v
void verticalBar(int c, int porcentaje);    // llena la barra vertical de la columna c segun porcentaje
void restauraMatrix();                      // recupera el estado de la matriz de leds
void vumetroClear();                        // apaga todos los vumetros
void vumetroFull();                         // llena la matriz de leds
void zoom(int c);                           // Utiliza la matriz de leds para simbolizar un gradiente de zoom hasta la columna c
// bateria
void bateria(int porcentaje);               // llena de izquierda a derecha la barra de bateria segun porcentaje
void bateriaR(int porcentaje);              // llena de derecha a izquierda la barra de bateria segun porcentaje
void bateriaPos(int b, bool s);             // enciende/apaga el led b de la barra de bateria
void bateriaBlink(int b, bool s);           // marca/desmarca para blink el led b de la barra de bateria
void bateriaClear();                        // apaga la barra de bateria
// leds botones
void ledButton(int n, bool s);              // enciende/apaga el led del boton n
void ledBlink(int n, bool s);               // marca/desmarca para blink el led del boton n
void ledInvert(int n);                      // invierte el estad on/off del led del boton n
// macros
void animModo(uint8_t mask);                // ejecuta animacion segun mascara de vumetros mask
uint8_t mascaraModo(int f);                 // devuelve la mascara asociada a la animacion f
// bajo nivel
void ledAt(int i, int j, bool s);           // enciende/apaga el led segmento i grid j
void ledAtBlink(int i, int j, bool s);      // marca para blink el led segmento i grid j
void updateBlink();                         // invierte leds marcados
