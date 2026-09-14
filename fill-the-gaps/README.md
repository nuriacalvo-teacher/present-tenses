# Present Tenses · Fill in the Gaps

Aplicación web (un solo fichero `index.html`) para practicar los **cuatro tiempos del presente** en inglés con **ejercicios de rellenar huecos**: el alumnado escribe la forma verbal, no elige entre opciones.

## Qué incluye

- **6 bloques**, cada uno con **teoría** + **10 ejercicios de huecos**:
  1. Present Simple
  2. Present Continuous
  3. Present Perfect
  4. Present Perfect Continuous
  5. Simple vs Continuous
  6. Master Test (todos los tiempos mezclados)
- En cada bloque, los 10 ejercicios están repartidos entre los tres tipos de oración:
  **4 afirmativas · 3 negativas · 3 interrogativas** (marcadas con una etiqueta de color).
- El verbo aparece **en infinitivo entre paréntesis**: `(go)`, `(not / like)`, `(you / study)`.
- Corrección automática con **explicación gramatical** en cada ejercicio y **repaso final** ejercicio a ejercicio (respuesta del alumno vs. solución), imprimible.
- **Informe Final de Evaluación** al completar los 6 bloques (imprimible / PDF).
- **Panel del profesorado** (botón ⚙️ Profe) con una fila por alumno, nota por bloque, media y nivel.

## Cómo se corrigen los huecos

- No distingue mayúsculas ni espacios sobrantes, y admite el punto final.
- Acepta **contracción y forma completa**: `don't` = `do not`, `hasn't` = `has not`, `haven't been` = `have not been`.
- Acepta grafía británica y americana donde procede (`practising` / `practicing`).
- Si la única diferencia es el apóstrofo (`dont`), avisa con una pista en lugar de dejarlo sin explicación.
- Donde hay dos tiempos correctos (p. ej. `has lived` / `has been living` con *since*), se admiten ambos.

## Datos

Los resultados se guardan en Firebase Realtime Database, en el nodo **`results_fill`**, independiente del test de opción múltiple (`results`), para que las notas de los dos ejercicios no se mezclen.

## Uso

Abrir `index.html` en el navegador o publicarlo con GitHub Pages. No necesita instalación ni servidor.
