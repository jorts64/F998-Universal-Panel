# F998 -- Worker de Exportación

Documentación de Configuración y Uso

------------------------------------------------------------------------

## 1. Descripción General

El **Worker F998** es un sistema autónomo de procesamiento de
exportaciones de vídeo basado en archivos JSON.

Funciona como una cola de trabajos independiente del editor y del panel
físico.\
Se ejecuta en el mismo equipo donde están almacenados los vídeos reales.

El worker:

-   Traduce rutas automáticamente
-   Reencodea siempre (H.264)
-   Fuerza 30 fps constantes (CFR)
-   Soporta segmentos múltiples
-   Soporta token `END`
-   Gestiona capítulos multipart (`a`, `b`, `c`...)
-   No sobrescribe archivos finales
-   Funciona como sistema de cola continuo

------------------------------------------------------------------------

## 2. Requisitos

### Software

-   Python 3.8+
-   ffmpeg instalado y accesible desde PATH

Comprobación:

``` bash
ffmpeg -version
python3 --version
```

------------------------------------------------------------------------

## 3. Estructura de Carpetas

Directorio base:

    /srv/nas/VideoEncoder/

Estructura requerida:

    VideoEncoder/
    │
    ├── jobs/
    │   ├── done/
    │   └── error/
    │
    ├── temp/
    │
    └── output/

------------------------------------------------------------------------

## 4. Configuración del Worker

En el script principal:

``` python
EXPORT_PROFILE = "720p"   # 1080p | 720p | 576p
CRF_VALUE = 21
```

### Perfiles disponibles

``` python
PROFILES = {
    "1080p": {"scale": "1920:-2"},
    "720p":  {"scale": "1280:-2"},
    "576p":  {"scale": "1024:-2"}
}
```

------------------------------------------------------------------------

## 5. Formato del JSON

Ejemplo:

``` json
{
  "project_name": "TNG T1",
  "jobs": [
    {
      "output": "1x01",
      "source": "/home/jordi/VideosRemotos/TNG HDMI/V_20251227_005936.mp4",
      "segments": [
        {
          "in": 0.0,
          "out": 5400.76
        }
      ]
    }
  ],
  "created_at": "2026-02-14T19:03:52"
}
```

------------------------------------------------------------------------

## 6. Token END

Permite cortar hasta el final del archivo:

``` json
{
  "in": 21599.85,
  "out": "END"
}
```

------------------------------------------------------------------------

## 7. Capítulos Multipart

Ejemplo:

``` json
{ "output": "1x08a", ... }
{ "output": "1x08b", ... }
```

El worker:

1.  Procesa cada parte
2.  Valida secuencia
3.  Concatena
4.  Genera `1x08.mp4`

------------------------------------------------------------------------

## 8. Flujo de Uso

1.  Copiar JSON a:

```{=html}
<!-- -->
```
    /srv/nas/VideoEncoder/jobs/

2.  Ejecutar:

``` bash
./f998_worker.py
```

3.  Resultados en:

```{=html}
<!-- -->
```
    /srv/nas/VideoEncoder/output/

------------------------------------------------------------------------

## 9. Parámetros Técnicos

-   libx264
-   Audio AAC 160k
-   GOP 60
-   30 fps constantes
-   MP4 compatible SmartTV

Filtro clave:

    -vf "scale=XXXX:-2,fps=30"

------------------------------------------------------------------------

## 10. Manejo de Errores

El JSON se mueve a `/jobs/error/` si:

-   Falta archivo origen
-   ffmpeg falla
-   Multipart incompleto
-   Ya existe archivo final

------------------------------------------------------------------------

## 11. Resumen

✔ Sistema autónomo\
✔ Cola de trabajos\
✔ Soporte END\
✔ Soporte multipart\
✔ Reencode obligatorio\
✔ 30 fps constantes\
✔ Resolución configurable

------------------------------------------------------------------------

**Documento generado automáticamente el 2026-02-17 09:23:45**
