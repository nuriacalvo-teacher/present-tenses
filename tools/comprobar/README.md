# Comprobaciones del vídeo-lección

Se ejecutan desde la raíz del repositorio. No gastan cuota de Gemini.

| Script | Cuándo | Qué hace |
|---|---|---|
| `textos.py` | antes de grabar | Comprueba que la página y `grabar.py` generan los mismos textos para todos los clips, y lista las 3 respuestas de cada pregunta del quiz para comprobar que todas forman frase. |
| `capturas.js CARPETA` | antes de grabar | Hace una captura de cada escena con todas sus animaciones encendidas y avisa si algo choca con el subtítulo. |
| `revisar.py video/audio [clips…]` | después de grabar | Transcribe los clips con Whisper (small.en y medium.en para los dudosos) y los compara con el guion palabra por palabra. Avisa de las palabras de más. |
| `reproducir.js URL CARPETA` | después de grabar | Reproduce el vídeo entero en Chromium a x8 acertando y fallando preguntas. Da la nota, los clips que no han sonado y los errores de JavaScript. |
| `montaje.py CAP PREG salida.mp3` | al final | Monta en un MP3 un capítulo entero y una pregunta del quiz respondida mal. |

Diferencias de Whisper que no son fallos: "4" por "for", "e s Goya", "Kalvo", "sore" por "saw".

Necesitan `pip install faster-whisper`, `ffmpeg` y Playwright con Chromium.
En el contenedor de Claude, para edge-tts y para descargar Whisper, añade
`/root/.ccr/ca-bundle.crt` al fichero de certifi.
