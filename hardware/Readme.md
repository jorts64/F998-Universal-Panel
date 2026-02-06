# Modificación del hardware

Primero debemos abrir la caja. Me fue muy útil un [vídeo en YouTube](https://www.youtube.com/watch?v=PxLtwtSuTzQ) . Importante: la mayoría de tornillos se hallan debajo de las patas adhesivas.

Una vez abierta la caja veremos dos placas unidas por una manguera flexible: la PCB atornillada a la tapa con los leds, botones y potenciómetros (la que queremos reutilzar en nuestro panel); y la PCB atornillada a la parte inferior, estrecha con un DSP y los conectores de audio, conectada a una bateria, que vamos a rremplazar por nuestro Arduino Pro Micro.

* Quitamos los 2 tornillos que fijan la PCB del DSP a la base
* Desconectamos la manguera por el extremo de la PCB del DSP a cuyo oonector podemos acceder ahora
* Sacamos placa del DSP y la bateria. No las usaremos

En la caja pondremos en su lugar:
* Arduino Pro Micro USB-C
* Módulo CD74HC4067
* Adaptador FPC-30p
* Regulador LDO 3V3

Yo los fijé a la caja con cinta adhesiva doble cara de vinilo: me va genial.

El Arduino Pro Micro aprovecha la abertura serigrafiada *OTG/PC Live* para su conector USB-C. Hará falta limar un poco el divisor plástico interior para que encaje perfectamente.

El Adaptador FPC-30p ha de ir alineado con la manguera de la tapa. Recomiendo fijarlo al final, cuando se haya hecho todo el cableado y probado el sistena.

Yo utilicé una *placa de prototipos D1 mini* para el LDO y los dos diodos 1N4007

![](Placa prototipos D1 mini.png](F998-ArduinoProMicro.png)
