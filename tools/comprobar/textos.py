#!/usr/bin/env python3
"""Comprueba que la pagina (allClips() de video/index.html) y grabar.py
(clips_del_grupo) generan los mismos textos para todos los clips.
    python3 tools/comprobar/textos.py        (desde la raiz del repositorio)"""
import json, os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "gemini")); sys.path.insert(0, os.path.join(AQUI, ".."))
import grabar
pag = dict(json.loads(subprocess.check_output(["node", os.path.join(AQUI, "clips_pagina.js"), "video/index.html"])))
lesson = grabar.lesson_of()
py = {}
for g in grabar.GRUPOS:
    for c in grabar.clips_del_grupo(lesson, g):
        assert c[0] not in py, "clip repetido en GRUPOS: " + c[0]
        py[c[0]] = c[1]
mal = sorted(k for k in set(pag) | set(py) if pag.get(k) != py.get(k))
print("clips pagina %d, grabar.py %d, distintos %d, peticiones %d" % (len(pag), len(py), len(mal), len(grabar.GRUPOS)))
for k in mal:
    print(" ", k, repr(pag.get(k)), "|", repr(py.get(k)))
print("\nRespuestas del quiz (las tres opciones deben formar frase):")
for k in sorted(pag):
    if "_a" in k:
        print(" ", k, pag[k])
sys.exit(1 if mal else 0)
