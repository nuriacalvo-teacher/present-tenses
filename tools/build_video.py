#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_video.py · graba la narracion del video-leccion (video/index.html).

Por que existe
--------------
El video se narraba con la voz del propio navegador, y esa voz no es la misma
en cada aparato: en Safari y en iPhone suena metalica, y en Linux (Vitalinux)
muchas veces no hay ninguna instalada. Este script graba cada frase una sola
vez, con voces neuronales, y a partir de ahi el video suena igual en
cualquier sitio donde se proyecte.

Que graba
---------
Saca los textos del propio video/index.html (el bloque `var LESSON = {...}`):
  - cada frase de cada capitulo       -> s<capitulo>_<frase>.mp3
  - cada pregunta del quiz            -> q<n>.mp3
  - el "Correct!" y el "Not quite"    -> q<n>_ok.mp3 y q<n>_no.mp3
Narra la voz `voz_narradora` y el quiz la voz `voz_quiz` (tools/voces.txt).
"IES Goya, Zaragoza" lo dice la voz `voz_es`, con pronunciacion espanola.

Uso
---
    pip install edge-tts
    python3 tools/build_video.py

Deja los ficheros en video/audio/ junto con video/audio/manifest.json. La
pagina detecta ese manifest sola: si esta, usa las grabaciones; si no, sigue
usando la voz del navegador.

El manifest guarda el texto de cada clip. Si cambias el guion y no vuelves a
grabar, ese clip se da cuenta de que la grabacion ya no corresponde y pasa
solo a la voz del navegador, en vez de decir algo que ya no toca. Al volver a
grabar, solo se rehacen los clips que han cambiado.

Opciones utiles
---------------
    --force              regraba aunque ya exista
    --only s1_2 q0       graba solo esos clips
    --demo               una muestra corta, para oir las voces
    --audition           comparativa con todas las voces britanicas
    --list-voices        lista las voces disponibles
"""

import argparse
import asyncio
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, "video", "index.html")
AUDIO_DIR = os.path.join(ROOT, "video", "audio")
VOICES_FILE = os.path.join(HERE, "voces.txt")

VOICES = {
    "narradora": "en-GB-SoniaNeural",
    "quiz": "en-GB-RyanNeural",
    "es": "es-ES-ElviraNeural",
}
LOCALES = ["en-GB", "en-IE"]
RATE = "-4%"

# Trozos que se dicen con la voz espanola, y como se le escriben para que los
# pronuncie bien ("ies" se lee como una palabra: EE-ES).
SPANISH_BITS = [("IES Goya, Zaragoza", "ies Goya, Zaragoza.")]

# Ayudas de pronunciacion: solo cambian lo que se ENVIA a la voz, nunca el
# texto guardado en el manifest (que tiene que ser igual que el de la pagina).
SAY_AS = [
    ("8:15", "eight fifteen"),
    ("7:45", "seven forty-five"),
    ("blank,", "blank ...,"),
]


def load_voice_config():
    """Lee tools/voces.txt para cambiar las voces sin tocar el codigo."""
    if not os.path.exists(VOICES_FILE):
        return
    for line in io.open(VOICES_FILE, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip().lower()
        if key.startswith("voz_") and val.strip() and key[4:] in VOICES:
            VOICES[key[4:]] = val.strip()


# ---------------------------------------------------------------------------
# 1 · leer el guion de la pagina
# ---------------------------------------------------------------------------
class JsLiteral(object):
    """Lector minimo de literales JavaScript: objetos con clave sin comillas,
    cadenas, numeros, true/false/null, comentarios y comas sobrantes."""

    def __init__(self, text):
        self.s = text
        self.i = 0

    def error(self, msg):
        line = self.s.count("\n", 0, self.i) + 1
        raise ValueError("%s (linea %d)" % (msg, line))

    def skip(self):
        while self.i < len(self.s):
            c = self.s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif self.s.startswith("/*", self.i):
                end = self.s.find("*/", self.i + 2)
                self.i = len(self.s) if end < 0 else end + 2
            elif self.s.startswith("//", self.i):
                end = self.s.find("\n", self.i)
                self.i = len(self.s) if end < 0 else end + 1
            else:
                return

    def value(self):
        self.skip()
        if self.i >= len(self.s):
            self.error("fin de fichero inesperado")
        c = self.s[self.i]
        if c == "{":
            return self.obj()
        if c == "[":
            return self.arr()
        if c in "\"'":
            return self.string()
        if self.s.startswith("true", self.i):
            self.i += 4
            return True
        if self.s.startswith("false", self.i):
            self.i += 5
            return False
        if self.s.startswith("null", self.i):
            self.i += 4
            return None
        m = re.match(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", self.s[self.i:])
        if not m:
            self.error("valor no reconocido: %r" % self.s[self.i:self.i + 20])
        self.i += m.end()
        txt = m.group(0)
        return float(txt) if ("." in txt or "e" in txt or "E" in txt) else int(txt)

    def string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= len(self.s):
                self.error("cadena sin cerrar")
            c = self.s[self.i]
            if c == "\\":
                nxt = self.s[self.i + 1]
                self.i += 2
                if nxt == "u":
                    out.append(chr(int(self.s[self.i:self.i + 4], 16)))
                    self.i += 4
                else:
                    out.append({"n": "\n", "t": "\t", "r": "\r", "b": "\b",
                                "f": "\f", "0": "\0"}.get(nxt, nxt))
            elif c == quote:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def arr(self):
        self.i += 1                      # [
        out = []
        while True:
            self.skip()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1
            elif self.s[self.i] != "]":
                self.error("se esperaba , o ]")

    def obj(self):
        self.i += 1                      # {
        out = {}
        while True:
            self.skip()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            if self.s[self.i] in "\"'":
                key = self.string()
            else:
                m = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", self.s[self.i:])
                if not m:
                    self.error("clave no reconocida")
                key = m.group(0)
                self.i += m.end()
            self.skip()
            if self.s[self.i] != ":":
                self.error("se esperaba : tras la clave %r" % key)
            self.i += 1
            out[key] = self.value()
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1
            elif self.s[self.i] != "}":
                self.error("se esperaba , o }")





# ---------------------------------------------------------------------------
# 2 · MP3 sin dependencias externas: duracion y silencio
# ---------------------------------------------------------------------------
BITRATES_V1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
BITRATES_V2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mp3_frames(data):
    """Recorre las tramas MPEG Layer III. Devuelve (offset, tamano, muestras,
    frecuencia). Se salta ID3 y cualquier basura entre tramas."""
    i = 0
    if data[:3] == b"ID3":
        size = 0
        for b in data[6:10]:
            size = (size << 7) | (b & 0x7F)
        i = 10 + size
    n = len(data)
    while i + 4 <= n:
        if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        version = (data[i + 1] >> 3) & 0x03      # 3=MPEG1 2=MPEG2 0=MPEG2.5
        layer = (data[i + 1] >> 1) & 0x03        # 1 = Layer III
        if version == 1 or layer != 1:
            i += 1
            continue
        br_index = (data[i + 2] >> 4) & 0x0F
        sr_index = (data[i + 2] >> 2) & 0x03
        padding = (data[i + 2] >> 1) & 0x01
        if br_index in (0, 15) or sr_index == 3:
            i += 1
            continue
        rate = RATES[version][sr_index]
        bitrate = (BITRATES_V1 if version == 3 else BITRATES_V2)[br_index] * 1000
        samples = 1152 if version == 3 else 576
        size = (samples // 8) * bitrate // rate + padding
        if size < 4 or i + size > n:
            break
        yield i, size, samples, rate
        i += size


def mp3_info(data):
    """(duracion en segundos, frecuencia de muestreo)."""
    total, rate = 0, 24000
    for _, _, samples, sr in mp3_frames(data):
        total += samples
        rate = sr
    return (total / float(rate) if rate else 0.0), rate


def silence_mp3(seconds, rate=24000):
    """Tramas MPEG-2 Layer III mono vacias: se decodifican como silencio y se
    pueden pegar delante o detras de cualquier MP3 de la misma frecuencia."""
    sr_index = {22050: 0, 24000: 1, 16000: 2}.get(rate)
    if sr_index is None:                          # frecuencia rara: sin silencio
        return b""
    bitrate = 32000
    frame_len = (576 // 8) * bitrate // rate      # 96 bytes a 24 kHz
    header = bytes([
        0xFF,
        0b11110011,                               # MPEG2 · Layer III · sin CRC
        (4 << 4) | (sr_index << 2),               # 32 kbps · frecuencia · sin padding
        0b11000000,                               # mono
    ])
    frame = header + b"\x00" * (frame_len - 4)
    count = int(round(seconds / (576.0 / rate)))
    return frame * max(0, count)





def lesson_of():
    src = io.open(PAGE, encoding="utf-8").read()
    marca = "var LESSON = "
    start = src.find(marca)
    if start < 0:
        raise SystemExit("No encuentro 'var LESSON = ' en video/index.html")
    reader = JsLiteral(src)
    reader.i = start + len(marca)
    return reader.value()


def clips_of(lesson):
    """Lista de (clave, texto, voz) en el mismo orden y con el mismo texto que
    usa la pagina. Si cambias como la pagina compone una frase, cambialo aqui
    tambien."""
    out = []
    for i, pasos in enumerate(lesson["scenes"]):
        for j, paso in enumerate(pasos):
            for k, t in enumerate([paso] if isinstance(paso, str) else paso):
                # "S: ..." lo dice el alumno (aqui, la voz del quiz)
                out.append(("s%d_%d_%d" % (i, j, k), t, "quiz" if t.startswith("S:") else "narradora"))
    for i, q in enumerate(lesson["quiz"]):
        out.append(("q%d" % i, "Question %d. %s" % (i + 1, q["spoken"]), "quiz"))
        out.append(("q%d_ok" % i, "Correct! " + q["why"], "quiz"))
        out.append(("q%d_no" % i, "Not quite. The right answer is: %s. %s" % (q["opts"][q["a"]], q["why"]), "quiz"))
        for j, opt in enumerate(q["opts"]):
            # la frase con la opcion elegida: la dice el alumno (answerText() en la pagina)
            t = re.sub(r"\s+", " ", re.sub(r"\s*\u2014\s*", " ", q["before"] + opt + q["after"])).strip()
            out.append(("q%d_a%d" % (i, j), t, "quiz"))
    return out


def spoken_text(raw):
    """Quita del guion lo que no se lee: el "S:" del alumno y los [corchetes]."""
    return re.sub(r"^\[[^\]]*\]\s*", "", re.sub(r"^S:\s*", "", raw))


def say_as(text):
    for a, b in SAY_AS:
        text = text.replace(a, b)
    return re.sub(r"-ing\b", " I.N.G.", text)


def pieces_of(text, role):
    """Parte una frase en trozos (texto, voz): lo espanol con la voz espanola."""
    voice = VOICES[role]
    out, rest = [], text
    while True:
        cut = None
        for bit, spoken in SPANISH_BITS:
            k = rest.find(bit)
            if k >= 0 and (cut is None or k < cut[0]):
                cut = (k, bit, spoken)
        if cut is None:
            break
        k, bit, spoken = cut
        before = rest[:k].strip()
        if before:
            out.append((say_as(before), voice))
        out.append((spoken, VOICES["es"]))
        rest = rest[k + len(bit):].lstrip(" .,")
    if rest.strip():
        out.append((say_as(rest.strip()), voice))
    return out


# ---------------------------------------------------------------------------
# 3 · sintesis
# ---------------------------------------------------------------------------
async def synth(text, voice):
    import edge_tts
    chunks = []
    communicate = edge_tts.Communicate(text, voice, rate=RATE)
    async for item in communicate.stream():
        if item["type"] == "audio":
            chunks.append(item["data"])
    if not chunks:
        raise RuntimeError("edge-tts no devolvio audio para la voz %s" % voice)
    return b"".join(chunks)


async def synth_clip(text, role):
    """Graba un clip. Si lleva un trozo en espanol, graba cada trozo con su voz
    y los pega con una pausa corta (todos son MP3 de 24 kHz mono)."""
    partes = pieces_of(text, role)
    audio = b""
    for n, (t, v) in enumerate(partes):
        trozo = await synth(t, v)
        if audio:
            audio += silence_mp3(0.15, mp3_info(trozo)[1])
        audio += trozo
    return audio


async def build_all(force, only, existing):
    lesson = lesson_of()
    clips = clips_of(lesson)
    if only:
        faltan = [k for k in only if k not in {c[0] for c in clips}]
        if faltan:
            raise SystemExit("Estos clips no existen: %s" % ", ".join(faltan))
    previas = (existing or {}).get("clips", {})
    voces = dict(VOICES)
    out, total = {}, len(clips)
    for n, (key, text, role) in enumerate(clips):
        nombre = key + ".mp3"
        destino = os.path.join(AUDIO_DIR, nombre)
        antigua = previas.get(key)
        firma = "%s|%s" % (VOICES[role], VOICES["es"])
        if only and key not in only:
            if antigua:
                out[key] = antigua
            continue
        if (not force and antigua and antigua.get("t") == text and antigua.get("v") == firma
                and antigua.get("f") == nombre and os.path.exists(destino)):
            print("  [%2d/%2d] %-7s (ya estaba)  %.1f s" % (n + 1, total, key, antigua["d"]))
            out[key] = antigua
            continue
        print("  [%2d/%2d] %-7s %-52s" % (n + 1, total, key, text[:52]), end="", flush=True)
        audio = await synth_clip(spoken_text(text), role)
        with open(destino, "wb") as fh:
            fh.write(audio)
        dur = round(mp3_info(audio)[0], 2)
        print("  ->  %.1f s" % dur)
        out[key] = {"f": nombre, "d": dur, "t": text, "v": firma}
    return {"version": 1, "voices": voces, "clips": out}


async def build_demo():
    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    clips = clips_of(lesson_of())
    elegidos = [c for c in clips if c[0] in ("s0_0_0", "s0_0_1", "s0_1_0", "s1_1_1", "q0", "q0_ok")]
    piezas, rate = [], 24000
    print("\nMuestra · narradora %s · quiz %s · castellano %s" % (VOICES["narradora"], VOICES["quiz"], VOICES["es"]))
    for key, text, role in elegidos:
        print("  %-6s %s" % (key, text[:66]))
        audio = await synth_clip(spoken_text(text), role)
        rate = mp3_info(audio)[1]
        if piezas:
            piezas.append(silence_mp3(0.8, rate))
        piezas.append(audio)
    out = os.path.join(AUDIO_DIR, "muestra-voces.mp3")
    with open(out, "wb") as fh:
        fh.write(b"".join(piezas))
    print("\nMuestra lista: %s  (%d segundos)" % (out, round(mp3_info(b"".join(piezas))[0])))
    print("Escuchala. Si te convencen, graba el video entero; si no, cambia")
    print("las voces en tools/voces.txt. Este fichero no afecta a la pagina.")
    return 0


async def build_audition():
    import edge_tts
    voices = [v for v in await edge_tts.list_voices()
              if any(v["Locale"].startswith(loc) for loc in LOCALES)]
    voices.sort(key=lambda v: (v["Locale"], v["Gender"], v["ShortName"]))
    if not voices:
        print("No he encontrado voces para: %s" % ", ".join(LOCALES), file=sys.stderr)
        return 1
    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    frase = "Welcome to Future Lab. This time tomorrow, I'll be lying on the beach."
    print("Grabando una comparativa con %d voces...\n" % len(voices))
    piezas, elapsed, rate = [], 0.0, 24000
    for v in voices:
        short = v["ShortName"]
        label = short.split("-")[-1].replace("Neural", "")
        print("  %d:%02d  %-32s %s" % (elapsed // 60, elapsed % 60, short, v["Gender"]))
        try:
            audio = await synth("%s. %s" % (label, frase), short)
        except Exception as exc:                        # noqa: BLE001
            print("        (fallo: %s)" % exc)
            continue
        seconds, rate = mp3_info(audio)
        if piezas:
            gap = silence_mp3(0.9, rate)
            piezas.append(gap)
            elapsed += mp3_info(gap)[0]
        piezas.append(audio)
        elapsed += seconds
    out = os.path.join(AUDIO_DIR, "comparativa-voces.mp3")
    with open(out, "wb") as fh:
        fh.write(b"".join(piezas))
    print("\nComparativa lista: %s  (%d min %02d s)" % (out, elapsed // 60, elapsed % 60))
    print("\nApunta las que mas te gusten y escribelas en tools/voces.txt.")
    return 0


async def check_voices(names):
    import edge_tts
    try:
        catalog = {v["ShortName"] for v in await edge_tts.list_voices()}
    except Exception:                                   # noqa: BLE001
        return True
    mal = sorted(n for n in names if n not in catalog)
    if not mal:
        return True
    print("\nEstas voces de tools/voces.txt no existen:\n", file=sys.stderr)
    for n in mal:
        print("    %s" % n, file=sys.stderr)
    print("\nDisponibles para ingles britanico y castellano de Espana:\n", file=sys.stderr)
    for n in sorted(v for v in catalog if v.startswith(("en-GB", "en-IE", "es-ES"))):
        print("    %s" % n, file=sys.stderr)
    return False


async def main_async(args):
    load_voice_config()

    if args.list_voices:
        import edge_tts
        for v in await edge_tts.list_voices():
            if v["Locale"].startswith(tuple(LOCALES + ["es-ES"])):
                print("%-32s %-8s %s" % (v["ShortName"], v["Gender"], v["Locale"]))
        return 0

    if args.audition:
        return await build_audition()
    if not await check_voices(sorted(set(VOICES.values()))):
        return 1
    if args.demo:
        return await build_demo()

    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    manifest_path = os.path.join(AUDIO_DIR, "manifest.json")
    data = None
    if os.path.exists(manifest_path):
        try:
            data = json.load(io.open(manifest_path, encoding="utf-8"))
        except ValueError:
            data = None

    print("\nGrabando el video · narradora %s · quiz %s · castellano %s\n"
          % (VOICES["narradora"], VOICES["quiz"], VOICES["es"]))
    data = await build_all(args.force, args.only, data)

    # se borran los MP3 de clips que ya no existen en el guion
    vivos = {c["f"] for c in data["clips"].values()}
    for nombre in os.listdir(AUDIO_DIR):
        if (re.match(r"^(s\d+_\d+(_\d+)?|q\d+(_ok|_no|_a\d+)?)\.mp3$", nombre) and nombre not in vivos):
            os.remove(os.path.join(AUDIO_DIR, nombre))
            print("  (borrado %s: ya no esta en el guion)" % nombre)

    with io.open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    tot = sum(c["d"] for c in data["clips"].values())
    print("\n%d clips · %d min %02d s de audio" % (len(data["clips"]), tot // 60, tot % 60))
    print("Manifest: %s" % manifest_path)
    return 0


def main():
    ap = argparse.ArgumentParser(description="Graba la narracion del video con edge-tts.")
    ap.add_argument("--force", action="store_true", help="regraba aunque ya exista")
    ap.add_argument("--only", nargs="+", metavar="CLIP", help="graba solo estos clips (p. ej. s1_2 q0)")
    ap.add_argument("--demo", action="store_true", help="graba solo una muestra corta")
    ap.add_argument("--audition", action="store_true", help="comparativa con todas las voces")
    ap.add_argument("--list-voices", action="store_true", help="lista las voces disponibles")
    args = ap.parse_args()
    try:
        import edge_tts                                # noqa: F401
    except ImportError:
        print("Falta edge-tts. Instalalo con:  pip install edge-tts", file=sys.stderr)
        return 1
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
