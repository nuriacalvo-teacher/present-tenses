# REVISAR · Variantes dudosas del Level 3 (Present Tenses)

Variantes que **no** he añadido en silencio porque no está claro que deban aceptarse. Algunas cambian el matiz, usan un verbo distinto al de la pista, solo valen en un registro o una variedad concreta, o esquivan el punto gramatical que se evalúa.
Para aceptar una, basta con añadirla al `pat` de su frase en `index.html` (y un caso positivo en `tests/level3.test.js`).

Leyenda de la propuesta: **Sí** = la aceptaría · **No** = la dejaría fallar · **Tú decides** = depende del criterio de clase.

## Variantes que NO se aceptan ahora

| qid | Frase española | Variante | Propuesta | Razonamiento |
|---|---|---|---|---|
| ps_l3_0 | Me levanto a las siete todos los días. | I wake up at seven every day | No | *wake up* es despertarse, no levantarse; la pista es *(get up)*. |
| ps_l3_0 | Me levanto a las siete todos los días. | I always get up at seven | Tú decides | *always* ≈ todos los días, pero no traduce la expresión y pierde la estructura "every day". |
| ps_l3_1 | Mi madre no trabaja los viernes. | My mother doesn't work Fridays | Tú decides | Natural en inglés americano (sin *on*), pero en clase se enseña *on Fridays*. |
| ps_l3_3 | El tren sale a las ocho. | The train departs at eight | Sí | Correcto y natural, pero el verbo no es el de la pista *(leave)*. |
| ps_l3_4 | Nunca llegamos tarde a clase. | We never get to class late | Sí | Correcto; verbo distinto de *(arrive)*. |
| ps_l3_4 | Nunca llegamos tarde a clase. | We never come late to class | No | Poco natural; lo normal es *arrive / be late*. |
| ps_l3_5 | Mi hermana estudia medicina en Zaragoza. | My sister is studying medicine in Zaragoza | Tú decides | Correcto (situación temporal: la carrera), pero el módulo evalúa el present simple (*studies*). |
| ps_l3_5 | Mi hermana estudia medicina en Zaragoza. | …at Zaragoza University / at the University of Zaragoza | Tú decides | Añade información que no está en el español. |
| pc_l3_4 | Este mes vivimos con mis abuelos. | We are staying with my grandparents this month | Sí | Muy natural para una situación temporal; verbo distinto de *(live)*. |
| pc_l3_4 | Este mes vivimos con mis abuelos. | We are living at my grandparents' (house) this month | Tú decides | Correcto, pero cambia la estructura (*with* → *at … house*). |
| pc_l3_4 | Este mes vivimos con mis abuelos. | …with my grandma and grandpa | Sí | Registro familiar; mismo significado. |
| pc_l3_5 | Mañana cenamos con Marta, ya está decidido. | We have dinner with Marta tomorrow · We will have dinner… · We're going to have… | **Aceptadas por indicación tuya** | Las pediste expresamente. Pedagógicamente, el módulo explica "plan cerrado → present continuous"; el present simple de futuro suena a horario y *will* a decisión espontánea. Si quieres ser más estricta, quítalas del `pat`. |
| pc_l3_5 | Mañana cenamos con Marta, ya está decidido. | We are eating dinner with Marta tomorrow (y *going to eat*, *will eat*) | **Aceptadas por indicación tuya** | Pediste aceptar *eat dinner* como sinónimo de *have dinner*; la pista es *(have)*. |
| pc_l3_5 | Mañana cenamos con Marta, ya está decidido. | We're gonna have dinner… | No | Registro informal (*gonna*). |
| pp_l3_0 | He perdido el móvil. | I lost my mobile / I lost my phone | Tú decides | Inglés americano: el past simple se usa para resultados recientes. El módulo evalúa el present perfect. |
| pp_l3_2 | Vivimos aquí desde hace diez años. | We've lived here ten years | No | Existe en inglés hablado, pero pediste que *for* no se ignore nunca. |
| pp_l3_3 | Mi hermana todavía no ha llegado. | My sister didn't arrive yet | No | Inglés americano coloquial; el módulo evalúa el present perfect con *yet*. |
| pp_l3_3 | Mi hermana todavía no ha llegado. | My sister hasn't got here yet / My sister isn't here yet | Tú decides | Correctas y naturales, pero sin el verbo *(arrive)*; la segunda ni siquiera usa present perfect. |
| pp_l3_4 | Nunca he comido sushi. | I have never had sushi / I have never tried sushi | Sí (*had*) · Tú decides (*tried*) | *have* = comer es muy natural; *try* = probar cambia un poco el matiz. |
| pp_l3_4 | Nunca he comido sushi. | I never have eaten sushi | No | Posición enfática del adverbio; en el nivel de la app se enseña *have never eaten*. |
| pp_l3_5 | Acaban de salir de casa. | They just left (home) | Tú decides | Inglés americano (past simple + *just*). Lo mencionaste como "(US)", pero el módulo evalúa *have just + participio*. |
| pp_l3_5 | Acaban de salir de casa. | They have just left | Tú decides | Correcto, pero no traduce "de casa". |
| ppc_l3_1 | ¿Cuánto tiempo llevas esperando? | How long have you waited? | No | Posible, pero mucho menos natural que el continuo para una espera que sigue en curso. |
| ppc_l3_1 | ¿Cuánto tiempo llevas esperando? | How much time have you been waiting? | No | Calco del español; no es la forma natural. |
| ppc_l3_4 | Mi hermana lleva tres años aprendiendo alemán. | My sister has been studying German for three years | Sí | Correcto; verbo distinto de *(learn)*. |
| ppc_l3_5 | No he estado durmiendo bien últimamente. | I'm not sleeping well lately | Tú decides | Muy frecuente en inglés hablado, pero el módulo evalúa el present perfect continuous. |
| ppc_l3_5 | No he estado durmiendo bien últimamente. | I haven't been sleeping very well lately | Sí | Añade *very*; mismo significado. |
| vs_l3_0 | Normalmente ceno a las nueve, pero hoy estoy cenando antes. | …but today I'm having an early dinner | Tú decides | Natural, pero cambia la estructura. |
| vs_l3_0 | Normalmente ceno a las nueve, pero hoy estoy cenando antes. | …but today I'm eating earlier | Tú decides | Natural; omite *dinner*. |
| vs_l3_0 | Normalmente ceno a las nueve, pero hoy estoy cenando antes. | …having dinner sooner | No (**antes se aceptaba**) | La versión anterior igualaba *sooner* con *earlier*; en esta frase *sooner* no es natural. |
| vs_l3_4 | Todavía no he visto esa serie. | I haven't watched that series yet | Sí | Muy natural (*watch* una serie); verbo distinto de *(see)*. |
| vs_l3_4 | Todavía no he visto esa serie. | I haven't seen that serie yet | No (**antes se aceptaba**) | *serie* no existe en inglés; la ortografía cuenta. |
| master_l3_1 | Llevo esperándote media hora. | …for a half hour | Sí | Inglés americano; mismo significado. |
| master_l3_1 | Llevo esperándote media hora. | I have been waiting half an hour for you | **Aceptada (ya se aceptaba antes)** | Sin *for* ante la duración, pero es natural y ya estaba entre las alternativas. Se mantiene para no empeorar la corrección actual. |
| master_l3_2 | ¿Alguna vez has montado a caballo? | Have you ever been horse riding? / …horseback riding? | Sí | Muy natural; usa *riding* en vez de *ridden*. |
| master_l3_2 | ¿Alguna vez has montado a caballo? | Did you ever ride a horse? | No | Inglés americano coloquial; el módulo evalúa el present perfect con *ever*. |
| master_l3_3 | Están comiendo en la cocina. | They are having dinner / a meal in the kitchen | Tú decides | "Comer" en España es *lunch*; *dinner* cambia el momento del día. |
| master_l3_4 | No entiendo esta pregunta. | I can't understand this question | Sí | Muy natural; añade *can*. |
| master_l3_5 | Ya he terminado los deberes. | I have already done my homework | Sí | Colocación muy natural (*do homework*); verbo distinto de *(finish)*. |
| master_l3_5 | Ya he terminado los deberes. | I already finished my homework | Tú decides | Inglés americano (past simple + *already*). |

## Decisiones del motor que conviene conocer

- **Ciertas palabras terminadas en -s se leen como si llevaran 's**: *my sisters book* = *my sister's book*; *my brothers living* = *my brother is living*. Es la tolerancia al "apóstrofo ausente" que pediste. No da por buena una frase incorrecta, porque la lectura resultante tiene que coincidir exactamente con una respuesta aceptada.
- **am/pm después de una hora se ignoran**: *7 pm* vale igual que *7 am*. En estas frases la hora no dice si es de mañana o de tarde. Si en otra app aparece "a las siete de la tarde", habrá que exigirlo en la plantilla.
- ***gotten* no se iguala a *got***, porque *I gotten* (incorrecto) acabaría valiendo igual que *I got*. Si hace falta en alguna frase, se añade en su `pat`.
- **Nunca se aceptan** *'ll not* (se exige *won't* / *will not*), *gonna / wanna / gotta* ni erratas (*studys*, *goed*, *serie*).
