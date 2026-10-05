# Narración del vídeo-lección

El vídeo-lección está en `video/index.html` y se abre en
**https://nuriacalvo-teacher.github.io/present-tenses/video/**.

## El problema

Si el vídeo se narra con la voz del propio navegador, suena distinto en cada
aparato:

| Dispositivo | Qué voz sale de fábrica | Cómo suena |
|---|---|---|
| Mac con Chrome o Edge | voces de Google / Microsoft | bien |
| Mac con Safari | voz **compacta** de Apple | metálica |
| iPhone / iPad | voz **compacta** de Apple | metálica |
| Android | Google TTS | bien |
| Windows | voces de Microsoft | de correcto a muy bien |
| Linux / Vitalinux | normalmente **ninguna** | no narra |

Con la narración **grabada** suena igual en todas partes. La voz del navegador
queda solo como respaldo.

## Qué hay grabado

`video/audio/` tiene un MP3 por frase y `manifest.json`:

- `s0_0_0.mp3` …: cada frase de cada capítulo (capítulo_paso_frase).
- `q0.mp3` …: las preguntas del quiz; `q0_ok.mp3`, `q0_no.mp3`: acierto / fallo.
- `q0_a0.mp3` …: el alumno diciendo la frase con la opción elegida.
- `manifest.json`: fichero, duración y **el texto** de cada clip, y las voces.

## Si cambias el guion

Las frases están en `video/index.html`, en el bloque `var LESSON = { … }`
(cerca del final). `scenes` son los capítulos, frase a frase; `quiz` son las
preguntas.

El índice guarda **el texto de cada clip**. Si cambias una frase y no vuelves
a grabar, esa frase nota que su grabación ya no corresponde y se dice con la
voz del navegador, en vez de decir algo que ya no toca. Las demás siguen con
su grabación.

Para ponerla al día, vuelve a grabar (ver abajo): **solo se rehacen los clips
que han cambiado**.

## Qué hace la página con la voz del navegador (respaldo)

Solo se usa si no hay grabación, o para una frase cuyo texto ha cambiado. Con
las mismas reglas que BRIT, `battles` y `ad`:

- Las voces se identifican por **voiceURI**, nunca por el nombre (en iOS la
  compacta y la mejorada se llaman las dos "Daniel").
- Las voces "de broma" de Apple se filtran también por voiceURI, porque en un
  Mac en español cambian de nombre ("Jester" → "Bufón").
- En Apple, velocidad **1.0** y el tono **sin tocar**.
- El truco de pause()+resume() cada 9 s es **solo** para Chrome de escritorio.
- Hay un selector de voz en la portada, que **desaparece** cuando hay
  grabación.
- Si no hay grabación ni ninguna voz instalada (Vitalinux), avisa y el vídeo
  sigue con los subtítulos. Con grabación, en Vitalinux suena normal.
- Sin `manifest.json`, todo funciona con la voz del navegador.

## Narración con Gemini: profesora + alumno

El guion de `video/index.html` es ahora un diálogo. Cada paso de un capítulo
puede tener varias frases seguidas:

```
"Texto"            lo dice la profesora (voz Kore)
"S: Texto"         lo dice el alumno (voz Puck)
"[alegre] Texto"   lo de los corchetes es CÓMO decirlo: no se lee ni sale en pantalla
```

En pantalla, el subtítulo indica quién habla: **TEACHER** o **STUDENT**.

Se graba con `tools/gemini/grabar.py`, desde la pestaña **Actions** →
*Grabar la narración con Gemini*. Necesita el secreto `GEMINI_API_KEY`.

- El plan gratuito de Gemini permite **10 peticiones al día** (y 3 por
  minuto). Se hacen 9: la intro con el capítulo 1, un capítulo por petición,
  el aviso del quiz con el cierre, las preguntas del quiz y las respuestas
  del alumno (`GRUPOS` en `grabar.py`).
- Las frases con un error a propósito (las del alumno con "mistake" en el
  estilo y las respuestas incorrectas del quiz) tienen que sonar palabra por
  palabra. Si Whisper *small* no las oye exactas, se vuelven a comprobar
  solas con Whisper *medium.en*.
- Después, el programa transcribe el audio con Whisper, lo compara con el
  guion y lo corta en frases. Si falta alguna frase o no cuadra, ese capítulo
  no se guarda y se repite en la siguiente ejecución.
- Solo se graba lo que ha cambiado o falta. Si se acaba la cuota, se guarda
  lo hecho y el resto se graba otro día.
- Las voces y el carácter de cada personaje están al principio de
  `tools/gemini/grabar.py` (`VOZ_PROFESORA`, `VOZ_ALUMNO`, `PROFESORA`, `ALUMNO`).
