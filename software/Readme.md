# Script python

Se ha concebido de forma modular: si se quiere añadir (o reemplazar) u modo solo hay que definir su bloque, asignarle un boton y conectarlo al bucle pricipal.

Se han implementado 4 modos para que sirvan de ejemplo:
* Modo kdenlive
* Modo SMPlayer
* Modo Macros
* Modo preeditor

La API se encuentra en un archivo aparte y está totalmente documentada en la carpeta *docs*

## Modo preeditor

* *f998_worker.py* es el agente encargado de procesar el marcado generado por el modo preeditor. Se recomienda su ejecucuón en otro ordenador dedicado, dond residan los archivos orige de video.
* El modo preeditor puede acceder remotamente a esos archivos (Adaptar y ejecutar *videosRemotos.sh*), generar los jobs en formato JSON. 
* Esos jobs se copian en la carpeta de cola *jobs* del worker. Si el worker está en ejecución pero sin carga el procesado se iniciará inmediatamente. Si está ocupado ya los procesará cuando le llegue el turno en la cola
* El worker traduce automáticamente los caminos remotos a locales. Tal vez sea necesario adaptar el traductor a su layout concreto
* Si el worker detecta 2 jobs del tipo 2x03a 2x03b una vez procesados los concatena para generar el archivo 2x03.mp4
* Dentro del código del propio worker se puede modificar la resolución de salida de los vídeos geerados

[Documentación completa worker.py](../doc/f_998_worker_documentacion.md)
