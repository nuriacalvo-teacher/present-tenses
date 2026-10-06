# Carpeta de audio del vídeo

La narración grabada de `video/index.html` (MP3 24 kHz, mono) y
`manifest.json`, que guarda el fichero, la duración y **el texto** de cada clip.

La página busca `manifest.json` al arrancar. **Si esta carpeta está vacía no
pasa nada**: se usa la voz del navegador.

Se graba con Gemini desde la pestaña **Actions** → *Grabar la narracion con
Gemini* → **Run workflow**. Ver `tools/README.md`.
