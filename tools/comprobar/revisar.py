#!/usr/bin/env python3
"""Transcribe todos los clips de video/audio y los compara con su texto.
Los dudosos y los de error deliberado se repiten con Whisper medium.en.
Avisa tambien de palabras de mas al principio o al final.
    python3 -I tools/comprobar/revisar.py video/audio   (desde la raiz)"""
import json, os, sys, subprocess, array
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gemini"))
import grabar
D = sys.argv[1]
man = json.load(open(os.path.join(D, "manifest.json")))["clips"]
lesson = grabar.lesson_of(); est = {}
for g in grabar.GRUPOS:
    for c in grabar.clips_del_grupo(lesson, g): est[c[0]] = c
malos = 0
solo = set(sys.argv[2:])          # opcional: solo estos clips
for k in sorted(man):
    if solo and k not in solo:
        continue
    c = est[k]; s = array.array("h")
    s.frombytes(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(D, man[k]["f"]), "-f", "s16le", "-ar", "24000", "-ac", "1", "pipe:1"], stdout=subprocess.PIPE).stdout)
    want = grabar.palabras(grabar.hablado(c[4]))
    got = [w[0] for w in grabar.transcribir_trozo(s)]
    fino = grabar.exacto(k, c[3])
    if got != want or fino:
        got2 = [w[0] for w in grabar.transcribir_trozo(s, nombre="medium.en")]
        if got2 == want: got = got2
    if got != want or grabar.sobra_en_bordes(got, want):
        malos += 1
        print("%-10s %s\n           oido: %s" % (k, " ".join(want), " ".join(got)))
    elif fino:
        print("%-10s OK exacto: %s" % (k, " ".join(got)))
print("clips con diferencias: %d de %d" % (malos, len(solo) or len(man)))
