#!/usr/bin/env python3
"""Montaje corto para escuchar: un capitulo entero y una pregunta del quiz
respondida mal (pregunta, respuesta incorrecta del alumno y correccion).
    python3 tools/comprobar/montaje.py CAPITULO PREGUNTA SALIDA.mp3   (desde la raiz)
    ej.: python3 tools/comprobar/montaje.py 1 1 muestra.mp3"""
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gemini"))
import grabar
cap, qi, salida = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
l = grabar.lesson_of()
partes = []
for j, beat in enumerate(l["scenes"][cap]):
    for k in range(len([beat] if isinstance(beat, str) else beat)):
        partes += [("f", "video/audio/s%d_%d_%d.mp3" % (cap, j, k)), ("s", 0.35)]
    partes.append(("s", 0.5))
partes.append(("s", 1.0))
mala = (l["quiz"][qi]["a"] + 1) % len(l["quiz"][qi]["opts"])
for f in ("q%d" % qi, "q%d_a%d" % (qi, mala), "q%d_no" % qi):
    partes += [("f", "video/audio/%s.mp3" % f), ("s", 0.6)]
ins = []
for t, v in partes:
    ins += ["-i", v] if t == "f" else ["-f", "lavfi", "-t", str(v), "-i", "anullsrc=r=24000:cl=mono"]
flt = "".join("[%d:a]" % i for i in range(len(partes))) + "concat=n=%d:v=0:a=1[o]" % len(partes)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-filter_complex", flt, "-map", "[o]",
                "-ar", "24000", "-ac", "1", "-b:a", "64k", salida], check=True)
print("montaje:", salida)
