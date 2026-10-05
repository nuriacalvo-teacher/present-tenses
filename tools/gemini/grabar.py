#!/usr/bin/env python3
"""Graba la narracion del video (video/index.html) con las voces de Gemini.

Profesora y alumno hablan en dialogo. Para caber en la cuota gratuita (10
peticiones al dia), cada capitulo se graba de una vez (una peticion por
capitulo y una para todo el quiz) y luego se corta en frases: el audio se
transcribe con Whisper, se alinea con el guion y se corta en la pausa entre
frase y frase. Asi tambien se comprueba que no falta ninguna frase.

    GEMINI_API_KEY=... python3 tools/gemini/grabar.py

Solo graba los capitulos que han cambiado o que faltan. Si un capitulo no se
puede cortar bien (no salen tantas pausas como frases), no se guarda nada de
el: se avisa y se repite en la siguiente ejecucion. Si se acaba la cuota del
dia, se para y guarda lo que ya tiene.

Deja los MP3 y el manifest.json en video/audio/, igual que build_video.py.
"""

import array
import base64
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from build_video import lesson_of, AUDIO_DIR       # noqa: E402

KEY = os.environ.get("GEMINI_API_KEY", "").strip()
API = "https://generativelanguage.googleapis.com/v1beta/interactions"
MODEL = "gemini-3.8-flash-tts"

# Voces britanicas (GET /v1beta/voices?language_code=en-GB): profesora de 54 anos
# y chico de 22, los dos con acento de Winchester (sur de Inglaterra).
VOZ_PROFESORA = "en-gb-tutor-6"
VOZ_ALUMNO = "en-gb-podcaster-4"
# Si el modelo no admite esas voces, se pasa a estas.
RESERVA = ("Kore", "Puck")

PROFESORA = ("Energetic, firm and enthusiastic English teacher with a natural British accent "
             "(Southern England). Lively, clear and engaging, never sleepy.")
ALUMNO = ("Enthusiastic British teenage student with a natural British accent "
          "(Southern England). Spontaneous and natural.")
ESPANOL = " Pronounce 'IES Goya, Zaragoza' the Spanish way."

# Que capitulos van juntos en una misma peticion ("quiz" = todo el quiz).
# Maximo 10 peticiones al dia: 9 grupos (intro + cap. 1, un grupo por capitulo,
# aviso del quiz + cierre, el quiz y las respuestas del alumno).
GRUPOS = [[0, 1], [2], [3], [4], [5], [6], [7, 8], ["quiz"], ["respuestas"]]

# Solo cambian lo que se ENVIA a la voz, nunca el texto del manifest.
SAY_AS = []

PAUSA_MIN = 0.12       # s: silencio mas corto que cuenta como pausa
TROZO_PAUSA = 0.35     # s: pausa por la que se trocea el audio para transcribirlo
MARGEN = 0.12          # s: silencio que se deja al principio y al final de cada clip


class SinCuota(Exception):
    pass


# ---------------------------------------------------------------------------
# guion -> clips
# ---------------------------------------------------------------------------
def turno(raw):
    """'S: [estilo] Texto' -> (quien, estilo, texto)."""
    who = "S" if re.match(r"^S:\s*", raw) else "T"
    rest = re.sub(r"^S:\s*", "", raw)
    m = re.match(r"^\[([^\]]*)\]\s*", rest)
    estilo = m.group(1) if m else ""
    return who, estilo, rest[m.end():] if m else rest


def respuesta(q, j):
    """La frase del quiz con la opcion j puesta: la dice el alumno al elegirla.
    Igual que answerText() en video/index.html."""
    t = re.sub(r"\s*\u2014\s*", " ", q["before"] + q["opts"][j] + q["after"])
    return re.sub(r"\s+", " ", t).strip()


def clips_del_grupo(lesson, grupo):
    out = []
    for g in grupo:
        if g == "respuestas":
            for i, q in enumerate(lesson["quiz"]):
                for j in range(len(q["opts"])):
                    t = respuesta(q, j)
                    estilo = "answering a quiz question out loud, saying the whole sentence with confidence"
                    if j != q["a"]:
                        estilo += ("; this sentence contains a deliberate grammar mistake for a language quiz: "
                                   "say it EXACTLY as written, word for word, keeping the mistake, never correct it")
                    out.append(("q%d_a%d" % (i, j), t, "S", estilo, t))
            continue
        if g == "quiz":
            for i, q in enumerate(lesson["quiz"]):
                buena = q["opts"][q["a"]]
                out.append(("q%d" % i, "Question %d. %s" % (i + 1, q["spoken"]), "T",
                            "clear and inviting, reading a quiz question; 'blank' marks the gap",
                            "Question %d. %s" % (i + 1, q["spoken"])))
                out.append(("q%d_ok" % i, "Correct! " + q["why"], "T",
                            "delighted, energetic praise, then a clear explanation",
                            "Correct! " + q["why"]))
                out.append(("q%d_no" % i, "Not quite. The right answer is: %s. %s" % (buena, q["why"]), "T",
                            "kind and encouraging, then a clear explanation",
                            "Not quite. The right answer is: %s. %s" % (buena, q["why"])))
            continue
        for j, beat in enumerate(lesson["scenes"][g]):
            for k, raw in enumerate([beat] if isinstance(beat, str) else beat):
                who, estilo, texto = turno(raw)
                out.append(("s%d_%d_%d" % (g, j, k), raw, who, estilo, texto))
    return out          # (clave, texto del manifest, quien, estilo, texto hablado)


def hablado(texto):
    for a, b in SAY_AS:
        texto = texto.replace(a, b)
    return texto


def firma(who):
    return "gemini:%s:%s" % (MODEL, VOZ_ALUMNO if who == "S" else VOZ_PROFESORA)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
def pedir(clips):
    global VOZ_PROFESORA, VOZ_ALUMNO
    for n in range(2):
        try:
            return pedir_con_voces(clips)
        except VozNoValida as e:
            if (VOZ_PROFESORA, VOZ_ALUMNO) == RESERVA or n:
                raise RuntimeError(str(e))
            print("    El modelo no admite %s / %s (%s). Se usan %s / %s."
                  % (VOZ_PROFESORA, VOZ_ALUMNO, str(e)[:200], RESERVA[0], RESERVA[1]))
            VOZ_PROFESORA, VOZ_ALUMNO = RESERVA


class VozNoValida(Exception):
    pass


def pedir_con_voces(clips):
    quienes = {c[2] for c in clips}
    dialogo = len(quienes) > 1
    content = []
    for n, (_, _, who, estilo, texto) in enumerate(clips):
        texto = hablado(texto)
        if n < len(clips) - 1:
            texto += " <long pause>"
        base = ALUMNO if who == "S" else PROFESORA
        if "IES Goya" in texto:
            base += ESPANOL
        meta = {"type": "speech_metadata", "style": base + (" Now: " + estilo + "." if estilo else "")}
        if dialogo:
            meta["speaker"] = "Student" if who == "S" else "Teacher"
        content.append({"type": "text", "text": texto, "annotations": [meta]})
    if dialogo:
        cfg = {"mode": "conversational", "speakers": [
            {"speaker": "Teacher", "voice": VOZ_PROFESORA},
            {"speaker": "Student", "voice": VOZ_ALUMNO}]}
    else:
        cfg = [{"voice": VOZ_ALUMNO if quienes == {"S"} else VOZ_PROFESORA}]
    body = json.dumps({"model": MODEL,
                       "input": [{"type": "user_input", "content": content}],
                       "response_format": {"type": "audio"},
                       "generation_config": {"speech_config": cfg}}).encode()
    for n in range(4):
        req = urllib.request.Request(API, data=body, method="POST", headers={
            "x-goog-api-key": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return audio_de(json.loads(r.read().decode()))
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:600]
            if e.code == 429 and "per day" in msg:
                raise SinCuota(msg)
            if e.code in (400, 404) and "voice" in msg.lower():
                raise VozNoValida(msg)
            if e.code in (429, 500, 503) and n < 3:
                print("    (%d, espero 65 s) %s" % (e.code, msg[:160]))
                time.sleep(65)
                continue
            raise RuntimeError("HTTP %d: %s" % (e.code, msg))


def audio_de(resp):
    found = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "audio" and isinstance(o.get("data"), str):
                found.append(o["data"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(resp)
    if not found:
        raise RuntimeError("la respuesta no trae audio: %s" % json.dumps(resp)[:400])
    return base64.b64decode(found[-1])


# ---------------------------------------------------------------------------
# audio
# ---------------------------------------------------------------------------
def a_pcm(audio):
    """Cualquier audio -> muestras PCM 16 bit, 24 kHz, mono."""
    conocido = audio[:4] == b"RIFF" or audio[:3] == b"ID3" or (audio[0] == 0xFF and audio[1] & 0xE0 == 0xE0)
    fmt = [] if conocido else ["-f", "s16le", "-ar", "24000", "-ac", "1"]
    p = subprocess.run(["ffmpeg", "-loglevel", "error"] + fmt + ["-i", "pipe:0",
                        "-f", "s16le", "-ar", "24000", "-ac", "1", "pipe:1"],
                       input=audio, stdout=subprocess.PIPE, check=True)
    s = array.array("h")
    s.frombytes(p.stdout)
    return s


def silencios(s, rate=24000, ventana=0.01):
    """Tramos de silencio [(inicio, fin)] en segundos."""
    n = int(rate * ventana)
    niveles = []
    for i in range(0, len(s) - n, n):
        trozo = s[i:i + n]
        niveles.append(max(abs(min(trozo)), abs(max(trozo))))
    if not niveles:
        return []
    ordenados = sorted(niveles)
    voz = ordenados[int(len(ordenados) * 0.9)] or 1
    umbral = max(voz * 0.04, 120)
    out, ini = [], None
    for k, v in enumerate(niveles + [umbral + 1]):
        if v < umbral and ini is None:
            ini = k
        elif v >= umbral and ini is not None:
            if (k - ini) * ventana >= PAUSA_MIN:
                out.append((ini * ventana, k * ventana))
            ini = None
    return out


NUMEROS = {w: str(n) for n, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
DECENAS = {w: 10 * n for n, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if n > 1}


# Whisper escribe en ortografia americana.
BRITANICO = {"kalvo": "calvo","neighbours": "neighbors", "neighbour": "neighbor", "colour": "color", "colours": "colors",
             "favourite": "favorite", "programme": "program", "practise": "practice", "centre": "center",
             "theatre": "theater", "travelling": "traveling", "realise": "realize"}


def palabras(texto):
    """Palabras normalizadas para comparar el guion con lo que oye Whisper,
    que escribe los numeros en cifras ('seven forty-five' -> 7 45)."""
    ws = re.findall(r"[a-z0-9]+", texto.lower().replace("'", "").replace("o'clock", "oclock"))
    out = []
    for w in ws:
        w = BRITANICO.get(w, w)
        if w == "oclock":
            out += ["o", "clock"]
        elif w in DECENAS:
            out.append(str(DECENAS[w]))
        elif w in NUMEROS and out and out[-1].isdigit() and int(out[-1]) % 10 == 0 and int(out[-1]) >= 20 \
                and int(NUMEROS[w]) < 10:
            out[-1] = str(int(out[-1]) + int(NUMEROS[w]))     # forty five -> 45
        else:
            out.append(NUMEROS.get(w, w))
    return out


def exacto(clave, estilo=""):
    """Las respuestas del quiz y las frases del alumno con un error a proposito
    tienen que sonar palabra por palabra, sin que la voz las corrija."""
    return re.match(r"^q\d+_a\d+$", clave) is not None or "mistake" in estilo.lower()


MODELO_ASR = {}


def modelo(nombre):
    from faster_whisper import WhisperModel
    if nombre not in MODELO_ASR:
        MODELO_ASR[nombre] = WhisperModel(nombre, device="cpu", compute_type="int8")
    return MODELO_ASR[nombre]


def transcribir_trozo(s, rate=24000, nombre="small.en", desde=0.0):
    tmp = os.path.join(HERE, "_tmp%d.wav" % os.getpid())
    guardar_wav(s, tmp, rate)
    segs, _ = modelo(nombre).transcribe(tmp, language="en", word_timestamps=True, vad_filter=False,
                                        beam_size=5, condition_on_previous_text=False)
    out = []
    for seg in segs:
        if re.sub(r"[^a-z ]", "", seg.text.lower()).strip() in INVENTADAS:
            continue
        for w in seg.words or []:
            for p in palabras(w.word):
                out.append((p, desde + w.start, desde + w.end))
    os.remove(tmp)
    return out


# Frases que Whisper se inventa en los silencios.
INVENTADAS = {"thanks for watching", "thank you for watching", "thank you so much for watching"}


def transcribir(s, rate=24000):
    """Palabras reconocidas con su tiempo: [(palabra, inicio, fin)].
    Se transcribe trozo a trozo, cortando en las pausas largas: de una sola
    vez, Whisper se salta frases parecidas y 'corrige' los errores a
    proposito con el contexto de las frases anteriores."""
    total = len(s) / float(rate)
    cortes = [(a + b) / 2.0 for a, b in silencios(s, rate) if b - a >= TROZO_PAUSA and a > 0.05 and b < total - 0.05]
    out, a = [], 0.0
    for x in cortes + [total]:
        if x - a >= 0.3:
            out += transcribir_trozo(s[int(a * rate):int(x * rate)], rate, desde=a)
        a = x
    return out


def oir_exacto(s, a, b, texto, rate=24000):
    """Segunda opinion para una frase que tiene que sonar tal cual: se
    transcribe sola con un modelo mas grande."""
    oido = [w[0] for w in transcribir_trozo(s[int(a * rate):int(b * rate)], rate, "medium.en")]
    return oido == palabras(hablado(texto)), " ".join(oido)


def cortar(s, clips, rate=24000):
    """Corta el audio del grupo en un trozo por clip. Transcribe el audio,
    lo alinea con el guion y corta en la pausa mas larga entre la ultima
    palabra de una frase y la primera de la siguiente.

    Devuelve (tramos, buenos): buenos[n] es False si la frase n no se ha
    dicho tal cual (le faltan palabras, le sobran o, en las que llevan errores
    a proposito, la voz los ha corregido); esas no se guardan. Si la voz se
    ha saltado una frase, esa sale como no buena y las demas se cortan igual.
    Lanza ValueError si no se encuentra ninguna o no se puede cortar."""
    import difflib
    total = len(s) / float(rate)
    oido = transcribir(s, rate)
    guion, de_quien = [], []
    for n, c in enumerate(clips):
        ws = palabras(hablado(c[4]))
        guion += ws
        de_quien += [n] * len(ws)
    sm = difflib.SequenceMatcher(None, guion, [w[0] for w in oido], autojunk=False)
    t_ini, t_fin, aciertos, pos = {}, {}, [0] * len(clips), {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            n = de_quien[blk.a + k]
            w = oido[blk.b + k]
            aciertos[n] += 1
            t_ini.setdefault(n, w[1])
            t_fin[n] = w[2]
            pos.setdefault(n, [blk.b + k, blk.b + k])[1] = blk.b + k
    buenos, hay = [], []
    for n, c in enumerate(clips):
        tot = max(1, sum(1 for q in de_quien if q == n))
        if aciertos[n] < max(1, 0.5 * tot):
            print("    %s no se oye en el audio (%d de %d palabras): se repetira" % (c[0], aciertos[n], tot))
            buenos.append(False)
            continue
        hay.append(n)
        sobran = pos[n][1] - pos[n][0] + 1 - aciertos[n]
        if exacto(c[0], c[3]):
            ok = aciertos[n] == tot and sobran == 0
        else:
            ok = aciertos[n] >= 0.8 * tot and sobran <= max(2, int(0.12 * tot))
        if not ok and not exacto(c[0], c[3]):
            print("    %s no se ha dicho tal cual: %s" % (c[0], " ".join(w[0] for w in oido[pos[n][0]:pos[n][1] + 1])))
        buenos.append(ok)
    if not hay:
        raise ValueError("no se reconoce ninguna frase")
    sil = silencios(s, rate)
    cortes = []
    for n, m in zip(hay, hay[1:]):
        a, b = t_fin[n], t_ini[m]
        if b < a:
            raise ValueError("las frases %s y %s se solapan" % (clips[n][0], clips[m][0]))
        hueco = [x for x in sil if x[1] > a - 0.05 and x[0] < b + 0.05]
        if hueco:
            x = max(hueco, key=lambda x: x[1] - x[0])
            cortes.append((max(x[0], a), min(x[1], b) if b > a else x[1]))
        else:
            # frases pegadas: se corta en el momento de menos volumen
            x = punto_mas_bajo(s, a - 0.1, b + 0.1, rate)
            cortes.append((x, x))
    ini0 = max(0.0, t_ini[hay[0]] - 0.3)
    fin0 = min(total, t_fin[hay[-1]] + 0.5)
    trozos, a = [], ini0
    for x in cortes:
        trozos.append((a, x[0]))
        a = x[1]
    trozos.append((a, fin0))
    tramos = [(0.0, 0.0)] * len(clips)
    for n, (a, b) in zip(hay, trozos):
        tramos[n] = (max(0.0, a - MARGEN), min(total, b + MARGEN))
    # Cada trozo se transcribe solo: la voz puede meter palabras que no estan
    # en el guion justo antes o despues de una frase ("Okay, fantastic...").
    # Las frases exactas tienen que coincidir palabra por palabra (con una
    # segunda opinion de medium.en); a las demas no les puede sobrar casi nada.
    for n in hay:
        c = clips[n]
        trozo = s[int(tramos[n][0] * rate):int(tramos[n][1] * rate)]
        esperado = palabras(hablado(c[4]))
        oido_n = [w[0] for w in transcribir_trozo(trozo, rate)]
        if exacto(c[0], c[3]):
            ok = oido_n == esperado
            if not ok:
                ok, texto = oir_exacto(s, tramos[n][0], tramos[n][1], c[4], rate)
                print("    %s %s: %s" % (c[0], "bien (medium.en)" if ok else "no se ha dicho tal cual", texto))
            buenos[n] = ok
        elif buenos[n] and len(oido_n) > len(esperado) + max(2, int(0.12 * len(esperado))):
            buenos[n] = False
            print("    %s lleva algo de mas: %s" % (c[0], " ".join(oido_n)))
    return tramos, buenos


def punto_mas_bajo(s, a, b, rate=24000, ventana=0.01):
    n = int(rate * ventana)
    mejor, t = None, (a + b) / 2.0
    for i in range(max(0, int(a * rate)), min(len(s) - n, int(b * rate)), n):
        trozo = s[i:i + n]
        nivel = max(abs(min(trozo)), abs(max(trozo)))
        if mejor is None or nivel < mejor:
            mejor, t = nivel, (i + n / 2.0) / rate
    return t


def guardar_mp3(s, a, b, destino, rate=24000):
    trozo = s[int(a * rate):int(b * rate)]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1",
                    "-i", "pipe:0", "-af", "afade=t=in:d=0.01,areverse,afade=t=in:d=0.03,areverse",
                    "-ar", "24000", "-ac", "1", "-b:a", "48k", destino],
                   input=trozo.tobytes(), check=True)
    return round(len(trozo) / float(rate), 2)


def guardar_wav(s, destino, rate=24000):
    with wave.open(destino, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(s.tobytes())


# ---------------------------------------------------------------------------
def main():
    if not KEY:
        sys.exit("Falta la clave GEMINI_API_KEY.")
    lesson = lesson_of()
    man_path = os.path.join(AUDIO_DIR, "manifest.json")
    try:
        previo = json.load(io.open(man_path, encoding="utf-8"))
    except (IOError, ValueError):
        previo = {}
    viejos = previo.get("clips", {})
    clips_out = {}
    fallos = os.path.join(HERE, "salida")
    hechos, mal, pendientes = [], [], []
    sin_cuota = False

    for grupo in GRUPOS:
        nombre = "+".join(str(g) if g in ("quiz", "respuestas") else "cap%s" % g for g in grupo)
        clips = []
        for c in clips_del_grupo(lesson, grupo):
            v = viejos.get(c[0], {})
            if (v.get("t") == c[1] and v.get("v") == firma(c[2])
                    and os.path.exists(os.path.join(AUDIO_DIR, c[0] + ".mp3"))):
                clips_out[c[0]] = v                          # ya grabado y al dia
            else:
                clips.append(c)
        if not clips:
            print("  %-12s ya estaba grabado" % nombre)
            continue
        if sin_cuota:
            pendientes.append(nombre)
            continue
        print("  %-12s grabando %d frases..." % (nombre, len(clips)), flush=True)
        try:
            audio = pedir(clips)
        except SinCuota:
            print("  Se ha acabado la cuota de hoy. Lo que falta se graba otro dia.")
            sin_cuota = True
            pendientes.append(nombre)
            continue
        except Exception as e:                               # noqa: BLE001
            print("  ERROR en %s: %s" % (nombre, str(e)[:500]))
            mal.append(nombre)
            continue
        s = a_pcm(audio)
        try:
            tramos, buenos = cortar(s, clips)
        except ValueError as e:
            print("  %s no se ha podido cortar bien (%s). Se repetira." % (nombre, e))
            os.makedirs(fallos, exist_ok=True)
            guardar_wav(s, os.path.join(fallos, nombre + ".wav"))
            mal.append(nombre)
            time.sleep(21)
            continue
        for c, (a, b), ok in zip(clips, tramos, buenos):
            if ok:
                d = guardar_mp3(s, a, b, os.path.join(AUDIO_DIR, c[0] + ".mp3"))
                clips_out[c[0]] = {"f": c[0] + ".mp3", "d": d, "t": c[1], "v": firma(c[2])}
        repetir = [c[0] for c, ok in zip(clips, buenos) if not ok]
        print("               -> %.0f s de audio%s" % (len(s) / 24000.0,
              "; se repetiran: " + ", ".join(repetir) if repetir else ""))
        if repetir:
            mal.append("%s (%s)" % (nombre, ", ".join(repetir)))
        if len(repetir) < len(clips):
            hechos.append(nombre)
        time.sleep(21)                                       # maximo 3 peticiones por minuto

    if not hechos:
        print("\nNo se ha grabado nada nuevo: no se toca video/audio.")
        print("Fallidos: %s · pendientes: %s" % (", ".join(mal) or "ninguno", ", ".join(pendientes) or "ninguno"))
        return
    # los clips de capitulos que no se han podido grabar: se conservan los
    # antiguos solo si siguen correspondiendo al guion (si no, voz del navegador)
    for k, v in viejos.items():
        if k not in clips_out and os.path.exists(os.path.join(AUDIO_DIR, v.get("f", ""))):
            clips_out[k] = v
    vivos = {v["f"] for v in clips_out.values()}
    claves = set()
    for grupo in GRUPOS:
        claves.update(c[0] for c in clips_del_grupo(lesson, grupo))
    for k in list(clips_out):
        if k not in claves:
            del clips_out[k]
            vivos.discard(k + ".mp3")
    for f in os.listdir(AUDIO_DIR):
        if re.match(r"^(s\d+_\d+(_\d+)?|q\d+(_ok|_no|_a\d+)?)\.mp3$", f) and f not in vivos:
            os.remove(os.path.join(AUDIO_DIR, f))

    data = {"version": 2,
            "voices": {"profesora": VOZ_PROFESORA, "alumno": VOZ_ALUMNO, "modelo": MODEL},
            "clips": {k: clips_out[k] for k in sorted(clips_out)}}
    with io.open(man_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    resumen = ["## Narracion con Gemini", "",
               "- grabados hoy: %s" % (", ".join(hechos) or "ninguno"),
               "- no se han podido cortar o han fallado: %s" % (", ".join(mal) or "ninguno"),
               "- pendientes por la cuota: %s" % (", ".join(pendientes) or "ninguno"),
               "- clips listos: %d de %d" % (sum(1 for k in claves if k in clips_out
                                                and clips_out[k]["v"].startswith("gemini")), len(claves))]
    print("\n" + "\n".join(resumen))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write("\n".join(resumen) + "\n")


if __name__ == "__main__":
    main()
