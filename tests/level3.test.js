/* Tests del LEVEL 3 (traducción español -> inglés).
   Ejecutar:  node tests/level3.test.js
   Carga el código real de index.html (tests/load.js) y comprueba, para cada una de las
   preguntas type "translate": positivos (deben ACEPTARSE) y negativos (deben FALLAR). */
"use strict";
const { load } = require("./load.js");
const T = load();
const QS = T.MODULES.filter(m => m.level === 3).flatMap(m => m.questions);

/* ---------- datos por pregunta ----------
   full: la respuesta modelo SIN contracciones (de aquí salen las variantes contraídas)
   pos:  variantes añadidas que deben aceptarse
   neg:  respuestas incorrectas que deben fallar                                        */
const CASES = {
  ps_l3_0: { full: "I get up at seven every day.",
    pos: ["Every day I get up at seven.", "I get up at 7 every day", "I get up at 7 am every day", "I get up at 7:00 every day",
          "I get up at 7 a.m. every day", "I get up at seven o'clock every day", "I get up at seven oclock every day",
          "I get up at 7 o clock every day", "Each day I get up at seven", "I get up every day at seven", "I get up at seven daily",
          "Every day, I get up at seven!", "Every day,I get up at seven"],
    neg: ["day every seven at up get I", "I get at seven up every day", "I gets up at seven every day",
          "I am getting up at seven every day", "I getting up at seven every day", "I get up at seven", "I got up at seven every day",
          "I wake up at seven every day", "get", ""] },
  ps_l3_1: { full: "My mother does not work on Fridays.",
    pos: ["My mum doesn't work on Fridays.", "My mom doesn't work on Fridays", "My mother doesnt work on Fridays",
          "On Fridays, my mother doesn't work.", "My mummy does not work on Fridays"],
    neg: ["Fridays on work doesn't mother my", "My mother don't work on Fridays", "My mother doesn't works on Fridays",
          "My mother isn't working on Fridays", "My mother doesn't work on Friday", "My mother not works on Fridays",
          "My mother doesn't work in Fridays"] },
  ps_l3_2: { full: "Do you speak English at home?",
    pos: ["Do you speak English at your house?", "Do you speak English in your house?", "do you speak english at home"],
    neg: ["You speak English at home?", "Does you speak English at home?", "Are you speaking English at home?",
          "Do you speaks English at home?", "Do you speak English in home?", "Speak you English at home?"] },
  ps_l3_3: { full: "The train leaves at eight.",
    pos: ["The train leaves at 8.", "The train leaves at eight o'clock.", "The train leaves at 8:00", "The train leaves at 8 o'clock"],
    neg: ["The train leave at eight.", "The train is leaving at eight.", "The train leaves on eight.", "The train left at eight.",
          "Leaves the train at eight.", "The train departs at eight."] },
  ps_l3_4: { full: "We never arrive late for class.",
    pos: ["We never arrive late to class.", "We are never late for class.", "We're never late for class", "Were never late to class",
          "We never arrive late for our lessons.", "We never arrive late for the class"],
    neg: ["We arrive never late for class.", "We don't never arrive late for class.", "Never we arrive late for class.",
          "We never arrives late for class.", "We never are late for class.", "We never arrive late in class.",
          "We never arrived late for class."] },
  ps_l3_5: { full: "My sister studies medicine in Zaragoza.",
    pos: ["My sister studies Medicine in Zaragoza", "MY SISTER STUDIES MEDICINE IN ZARAGOZA"],
    neg: ["My sister studys medicine in Zaragoza.", "My sister study medicine in Zaragoza.", "My sister studies medicine on Zaragoza.",
          "Sister my studies medicine in Zaragoza.", "My sister is studies medicine in Zaragoza.", "My sister studied medicine in Zaragoza."] },

  pc_l3_0: { full: "I am doing my homework right now.",
    pos: ["I'm doing my homework right now.", "Right now I'm doing my homework.", "I am doing the homework right now.",
          "I'm doing my homework now.", "At the moment I am doing my homework.", "I am doing my homework at this moment"],
    neg: ["I do my homework right now.", "I am do my homework right now.", "I doing my homework right now.",
          "I is doing my homework right now.", "I am making my homework right now.", "I am doing right now my homework.",
          "I am doing my homework."] },
  pc_l3_1: { full: "Look! It is snowing.",
    pos: ["Look! It's snowing!", "It's snowing.", "Look, it is snowing", "look its snowing", "LOOK IT'S SNOWING"],
    neg: ["Look! Is snowing.", "Look! It snows.", "Look! It is snow.", "Look! It snowing.", "Look! Snowing it is.", "Look! It was snowing."] },
  pc_l3_2: { full: "My brother is not studying this afternoon.",
    pos: ["My brother isn't studying this afternoon.", "This afternoon my brother isn't studying.", "My brother isn't studying this evening",
          "My brother's not studying this afternoon.", "My brothers not studying this afternoon"],
    neg: ["My brother doesn't study this afternoon.", "My brother not studying this afternoon.", "My brother isn't study this afternoon.",
          "My brother aren't studying this afternoon.", "My brother isn't studying this tomorrow.", "My brother is studying this afternoon."] },
  pc_l3_3: { full: "What are you reading?",
    pos: ["What're you reading?", "Whatre you reading", "what are you reading"],
    neg: ["What do you read?", "What you are reading?", "What are you read?", "What is you reading?", "What were you reading?", "reading"] },
  pc_l3_4: { full: "This month we are living with my grandparents.",
    pos: ["We are living with my grandparents this month.", "We're living with my grandparents this month.",
          "This month, we're living with my grandparents.", "Were living with my grandparents this month",
          "We are living with my grandmother and grandfather this month."],
    neg: ["We live with my grandparents this month.", "We are live with my grandparents this month.", "We living with my grandparents this month.",
          "This month we are living my grandparents with.", "We are living with my grandparents.", "We are living at my grandparents this month."] },
  pc_l3_5: { full: "We are having dinner with Marta tomorrow.",
    pos: ["We're having dinner with Marta tomorrow.", "Tomorrow we are having dinner with Marta.", "We are having dinner tomorrow with Marta.",
          "We're going to have dinner with Marta tomorrow.", "We are going to have dinner with Marta tomorrow.",
          "We will have dinner with Marta tomorrow.", "We'll have dinner with Marta tomorrow.", "Well have dinner with Marta tomorrow",
          "We have dinner with Marta tomorrow.", "We are eating dinner with Marta tomorrow.", "We're having supper with Marta tomorrow.",
          "Tomorrow we're having dinner with Marta, it's already decided.", "We are having dinner with Marta tomorrow, it is settled.",
          "We're having dinner with Marta tomorrow; it's all arranged.", "We are having dinner with Marta tomorrow and it's already been decided.",
          "Tomorrow were having dinner with Marta, thats decided"],
    neg: ["We have dinner with Marta yesterday.", "We had dinner with Marta tomorrow.", "We are have dinner with Marta tomorrow.",
          "We having dinner with Marta tomorrow.", "We will having dinner with Marta tomorrow.", "We'll not have dinner with Marta tomorrow.",
          "We are having dinner Marta with tomorrow.", "We are having dinner with Marta."] },

  pp_l3_0: { full: "I have lost my mobile.",
    pos: ["I've lost my mobile.", "I have lost my phone.", "I've lost my mobile phone.", "Ive lost my cell phone", "I have lost the phone.",
          "I’ve lost my smartphone"],
    neg: ["I have lose my mobile.", "I have losed my mobile.", "I has lost my mobile.", "I am lost my mobile.", "I lost my mobile.",
          "Lost I have my mobile.", "I have lost."] },
  pp_l3_1: { full: "Have you ever been to London?",
    pos: ["Have you ever been in London?", "have you ever been to london"],
    neg: ["Did you ever be in London?", "Have you ever be to London?", "Have you ever went to London?", "Has you ever been to London?",
          "Have you ever been at London?", "You have ever been to London?", "Have you never been to London?"] },
  pp_l3_2: { full: "We have lived here for ten years.",
    pos: ["We've lived here for ten years.", "We have been living here for ten years.", "We've been living here for 10 years.",
          "We have been here for ten years.", "For ten years we have lived here.", "Weve lived here for 10 years"],
    neg: ["We live here for ten years.", "We have lived here since ten years.", "We have lived here ten years.",
          "We are living here for ten years.", "We have lived here during ten years.", "We has lived here for ten years.",
          "We have live here for ten years."] },
  pp_l3_3: { full: "My sister has not arrived yet.",
    pos: ["My sister hasn't arrived yet.", "My sister still hasn't arrived.", "My sister has still not arrived.",
          "My sister's not arrived yet.", "My sisters not arrived yet", "My sister hasnt arrived yet"],
    neg: ["My sister has not arrived already.", "My sister have not arrived yet.", "My sister didn't arrive yet.",
          "My sister has not arrive yet.", "My sister yet has not arrived.", "My sister is not arrived yet.", "My sister hasn't arrived."] },
  pp_l3_4: { full: "I have never eaten sushi.",
    pos: ["I've never eaten sushi.", "Ive never eaten sushi", "I have never eaten sushi before."],
    neg: ["I have never ate sushi.", "I have eaten never sushi.", "I have ever eaten sushi.", "I has never eaten sushi.",
          "I never eat sushi.", "I have never eat sushi.", "I never have eaten sushi."] },
  pp_l3_5: { full: "They have just left home.",
    pos: ["They've just left home.", "They have just left the house.", "They have just left their house.", "They've just gone out.",
          "They have just gone out of the house.", "Theyve just left home"],
    neg: ["They just have left home.", "They have left just home.", "They are just leaving home.", "They has just left home.",
          "They have just leave home.", "They have just leaved home.", "They have just gone out of home."] },

  ppc_l3_0: { full: "I have been studying for two hours.",
    pos: ["I've been studying for two hours.", "I have studied for two hours.", "I've been studying for 2 hours.", "For two hours I have been studying."],
    neg: ["I am studying for two hours.", "I have been studying since two hours.", "I have been study for two hours.",
          "I have studying for two hours.", "I studied for two hours.", "I have been studying two hours.", "I've been studying."] },
  ppc_l3_1: { full: "How long have you been waiting?",
    pos: ["How long have you been waiting for?", "how long have you been waiting"],
    neg: ["How long are you waiting?", "How long you have been waiting?", "How long have you been wait?", "How long has you been waiting?",
          "How long have you waited been?", "How long did you wait?"] },
  ppc_l3_2: { full: "It has been raining since Monday.",
    pos: ["It's been raining since Monday.", "It has rained since Monday.", "Since Monday it has been raining.", "Its been raining since monday"],
    neg: ["It is raining since Monday.", "It has been raining for Monday.", "It has been raining from Monday.", "It has been rain since Monday.",
          "Is raining since Monday.", "It have been raining since Monday.", "It has been raining since on Monday."] },
  ppc_l3_3: { full: "They have been working all day.",
    pos: ["They've been working all day.", "They have worked all day.", "They've been working all day long.", "They have been working the whole day.",
          "Theyve been working all day"],
    neg: ["They are working all day.", "They have been working every day.", "They has been working all day.", "They have been work all day.",
          "They worked all day.", "They have all day been working.", "They have been working."] },
  ppc_l3_4: { full: "My sister has been learning German for three years.",
    pos: ["My sister's been learning German for three years.", "My sister has learnt German for three years.",
          "My sister has learned German for three years.", "My sister has been learning German for 3 years.",
          "For three years my sister has been learning German.", "My sisters been learning german for 3 years"],
    neg: ["My sister is learning German for three years.", "My sister has been learning German since three years.",
          "My sister have been learning German for three years.", "My sister has been learn German for three years.",
          "My sister has learning German for three years.", "My sister has been learning German three years.",
          "My sister has been learning for three years German."] },
  ppc_l3_5: { full: "I have not been sleeping well lately.",
    pos: ["I haven't been sleeping well lately.", "I haven't slept well lately.", "I haven't been sleeping well recently.",
          "Lately I haven't been sleeping well.", "I've not been sleeping well lately.", "Ive not slept well lately"],
    neg: ["I haven't been sleeping good lately.", "I have not been sleep well lately.", "I don't have been sleeping well lately.",
          "I haven't been sleeping lately well.", "I am not sleeping well lately.", "I haven't been sleeping well.",
          "I hasn't been sleeping well lately."] },

  vs_l3_0: { full: "I usually have dinner at nine, but today I am having dinner earlier.",
    pos: ["I usually have dinner at nine, but today I'm having dinner earlier.", "I usually have dinner at nine, but today I am having it earlier.",
          "I usually have dinner at 9, but I'm having dinner earlier today.", "Usually I have supper at nine but today Im having supper earlier",
          "I normally eat dinner at nine, but today I'm eating earlier dinner".replace("earlier dinner", "dinner earlier"),
          "I usually have dinner at nine o'clock, but I am having dinner earlier."],
    neg: ["I usually am having dinner at nine, but today I have dinner earlier.", "I usually have dinner at nine, but today I have dinner earlier.",
          "I have usually dinner at nine, but today I am having dinner earlier.", "I usually has dinner at nine, but today I am having dinner earlier.",
          "I usually have dinner at nine, but today I am having dinner before.", "I usually have dinner at nine."] },
  vs_l3_1: { full: "I have known Ana since 2020.",
    pos: ["I've known Ana since 2020.", "I have known Ana since the year 2020.", "Since 2020 I have known Ana.",
          "I've known Ana since twenty twenty.", "Ive known Ana since two thousand and twenty", "I have known Ana since two thousand twenty"],
    neg: ["I know Ana since 2020.", "I have been knowing Ana since 2020.", "I am knowing Ana since 2020.", "I have known Ana for 2020.",
          "I have know Ana since 2020.", "I have known Ana since 2021.", "I knew Ana since 2020."] },
  vs_l3_2: { full: "What do you do at weekends?",
    pos: ["What do you do on weekends?", "What do you do at the weekend?", "What do you do on the weekend?", "At weekends, what do you do?"],
    neg: ["What are you doing at weekends?", "What do you at weekends?", "What does you do at weekends?", "What you do at weekends?",
          "What do you do in weekends?", "What do you make at weekends?"] },
  vs_l3_3: { full: "My brother is living in Dublin this year.",
    pos: ["My brother's living in Dublin this year.", "This year my brother is living in Dublin.", "My brothers living in Dublin this year"],
    neg: ["My brother lives in Dublin this year.", "My brother is live in Dublin this year.", "My brother are living in Dublin this year.",
          "My brother is living on Dublin this year.", "My brother living in Dublin this year.", "My brother is living in Dublin."] },
  vs_l3_4: { full: "I have not seen that series yet.",
    pos: ["I haven't seen that series yet.", "I haven't seen that show yet.", "I still haven't seen that series.", "I have still not seen that TV series.",
          "I havent seen that show yet"],
    neg: ["I have not saw that series yet.", "I did not see that series yet.", "I have not seen that series already.", "I have not seen yet that series.",
          "I has not seen that series yet.", "I haven't seen that serie yet.", "I haven't seen this series yet."] },
  vs_l3_5: { full: "Water boils at one hundred degrees.",
    pos: ["Water boils at 100 degrees.", "Water boils at a hundred degrees.", "Water boils at 100 degrees Celsius.", "Water boils at 100ºC.",
          "Water boils at 100 °C", "Water boils at one hundred degrees centigrade."],
    neg: ["Water is boiling at 100 degrees.", "Water boil at 100 degrees.", "The water boils at 100 degrees.", "Water boils in 100 degrees.",
          "Water boils at 10 degrees.", "Water boiled at 100 degrees."] },

  master_l3_0: { full: "My father works in an office.",
    pos: ["My dad works in an office.", "My father works at an office.", "My daddy works in an office"],
    neg: ["My father work in an office.", "My father is working in an office.", "My father works in a office.", "My father works on an office.",
          "My father works in office.", "Works my father in an office."] },
  master_l3_1: { full: "I have been waiting for you for half an hour.",
    pos: ["I've been waiting for you for half an hour.", "I've been waiting for you for thirty minutes.", "I have been waiting for you for 30 minutes.",
          "I've been waiting for you for half an hour now.", "I have been waiting half an hour for you.", "I've been waiting for half an hour.",
          "Ive been waiting for you for half an hour"],
    neg: ["I am waiting for you for half an hour.", "I have been waiting you for half an hour.", "I have been waiting for you since half an hour.",
          "I have been wait for you for half an hour.", "I wait for you for half an hour.", "I have been waiting for you half an hour.",
          "I have been waiting for you."] },
  master_l3_2: { full: "Have you ever ridden a horse?",
    pos: ["have you ever ridden a horse", "HAVE YOU EVER RIDDEN A HORSE?"],
    neg: ["Have you ever rode a horse?", "Have you ever ride a horse?", "Did you ever ride a horse?", "Has you ever ridden a horse?",
          "Have you ever ridden to horse?", "You have ever ridden a horse?"] },
  master_l3_3: { full: "They are eating in the kitchen.",
    pos: ["They're eating in the kitchen.", "They are having lunch in the kitchen.", "Theyre eating in the kitchen"],
    neg: ["They eat in the kitchen.", "They are eat in the kitchen.", "They is eating in the kitchen.", "They are eating on the kitchen.",
          "They eating in the kitchen.", "They are eating in kitchen the."] },
  master_l3_4: { full: "I do not understand this question.",
    pos: ["I don't understand this question.", "I dont understand this question", "i DON’T understand this question!"],
    neg: ["I am not understanding this question.", "I not understand this question.", "I does not understand this question.",
          "I don't understand that question.", "I do not understood this question.", "I doesn't understand this question."] },
  master_l3_5: { full: "I have already finished my homework.",
    pos: ["I've already finished my homework.", "I have already finished the homework.", "I have finished my homework already.",
          "Ive already finished my homework"],
    neg: ["I have finished already my homework.", "I already have finished my homework.", "I have already finish my homework.",
          "I am already finishing my homework.", "I already finished my homework.", "I has already finished my homework.",
          "I have yet finished my homework."] }
};

/* ---------- generadores de variantes ---------- */
const CONTRACT = [
  [/\bI am\b/i, "I'm"], [/\byou are\b/i, "you're"], [/\bwe are\b/i, "we're"], [/\bthey are\b/i, "they're"],
  [/\bit is\b/i, "it's"], [/\bit has\b/i, "it's"], [/\bI have\b/i, "I've"], [/\bwe have\b/i, "we've"], [/\bthey have\b/i, "they've"],
  [/\bis not\b/i, "isn't"], [/\bare not\b/i, "aren't"], [/\bhas not\b/i, "hasn't"], [/\bhave not\b/i, "haven't"],
  [/\bdo not\b/i, "don't"], [/\bdoes not\b/i, "doesn't"], [/\bwe will\b/i, "we'll"]
];
function contractAll(s) { let o = s; for (let k = 0; k < 3; k++) CONTRACT.forEach(([rx, to]) => { o = o.replace(rx, m => keepCase(m, to)); }); return o; }
function contractFirst(s) {
  let best = null;
  CONTRACT.forEach(([rx, to]) => { const m = rx.exec(s); if (m && (!best || m.index < best.i)) best = { i: m.index, len: m[0].length, to: keepCase(m[0], to) }; });
  return best ? s.slice(0, best.i) + best.to + s.slice(best.i + best.len) : s;
}
function keepCase(m, to) { return m[0] === m[0].toUpperCase() && m[0] !== m[0].toLowerCase() ? to[0].toUpperCase() + to.slice(1) : to; }
function contractLast(s) {
  let best = null;
  CONTRACT.forEach(([rx, to]) => {
    const g = new RegExp(rx.source, "gi"); let m;
    while ((m = g.exec(s))) if (!best || m.index > best.i) best = { i: m.index, len: m[0].length, to: keepCase(m[0], to) };
  });
  return best ? s.slice(0, best.i) + best.to + s.slice(best.i + best.len) : s;
}

function autoPositives(q, c) {
  const model = q.answers[0];
  const out = [
    ["modelo", model],
    ["sin punto final", model.replace(/[.!?]+$/, "")],
    ["sin ningún signo", model.replace(/[.,;:!?¿¡"]/g, "")],
    ["MAYÚSCULAS", model.toUpperCase()],
    ["minúsculas", model.toLowerCase()],
    ["espacios de más", "   " + model.replace(/ /g, "  ") + "   "],
    ["coma sin espacio", model.indexOf(", ") >= 0 ? model.replace(", ", ",") : model.replace(" ", ",")],
    ["signos pegados", model.replace(/ /g, " ").replace(/\.$/, "...!!")],
    ["forma completa", c.full]
  ];
  const cAll = contractAll(c.full);
  if (cAll !== c.full) {
    out.push(["contraído (')", cAll]);
    out.push(["contraído (’)", cAll.replace(/'/g, "’")]);
    out.push(["contraído sin apóstrofo", cAll.replace(/'/g, "")]);
    const mix1 = contractFirst(c.full), mix2 = contractLast(cAll.replace(/'/g, "")) ;
    out.push(["mezcla completo/contraído", mix1]);
    if (contractAll(c.full.replace(/\b(is|are|has|have|do|does) not\b/i, "$1 not")) !== c.full) {
      // mezcla: la primera contraída sin apóstrofo, el resto completo
      out.push(["mezcla sin apóstrofo", mix1.replace(/'/g, "")]);
    }
  }
  q.answers.forEach((a, k) => out.push(["mostrada " + k, a]));
  (q.alts || []).forEach((a, k) => out.push(["alt " + k, a]));
  return out;
}

/* ---------- tests del motor (independientes de las frases) ---------- */
let fails = 0;
const log = [];
function check(name, cond, extra) { if (!cond) { fails++; log.push("  ✗ " + name + (extra ? "  → " + extra : "")); } }

const E = T.L3;
check("signo -> espacio", E.prep("Every day,I get up.Now") === "every day i get up now", E.prep("Every day,I get up.Now"));
check("guiones -> espacio", E.prep("well-known – yes—no") === "well known yes no", E.prep("well-known – yes—no"));
check("apóstrofos tipográficos", E.prep("I’m Iʼm I`m I´m") === "i'm i'm i'm i'm", E.prep("I’m Iʼm I`m I´m"));
check("¿¡«»()[]/…", E.prep("¿Qué? ¡Sí! «a» (b) [c] d/e f…") === "qué sí a b c d e f", E.prep("¿Qué? ¡Sí! «a» (b) [c] d/e f…"));
check("números 7=seven", E.baseTokens("seven").join() === "7");
check("números 100", ["one hundred", "a hundred", "100"].every(s => E.baseTokens(s).join() === "100"));
check("años", ["2020", "twenty twenty", "two thousand and twenty", "two thousand twenty"].every(s => E.baseTokens(s).join() === "2020"));
check("veintiuno", E.baseTokens("twenty-one").join() === "21");
check("7:30 = seven thirty", E.baseTokens("7:30").join(" ") === E.baseTokens("seven thirty").join(" "));
check("o'clock opcional", ["at 7", "at seven o'clock", "at 7 oclock", "at 7 o clock", "at 7:00", "at 7 am", "at 7am", "at 7 a.m."]
  .every(s => E.baseTokens(s).join(" ") === "at 7"), ["at 7 a.m.", "at 7am"].map(s => E.baseTokens(s).join(" ")).join(" / "));
check("ordinales", E.baseTokens("21st").join() === E.baseTokens("twenty-first").join());
check("GB/US", E.baseTokens("travelling colour mom learned").join(" ") === "travelling colour mum learnt");
check("cannot", E.baseTokens("cannot").join(" ") === "can not");
const rd = (t, n) => E.studentReadings(t, n).map(x => x.join(" "));
[["don't", "do not"], ["dont", "do not"], ["doesnt", "does not"], ["isnt", "is not"], ["arent", "are not"], ["wasnt", "was not"],
 ["havent", "have not"], ["hasnt", "has not"], ["hadnt", "had not"], ["won't", "will not"], ["wont", "will not"], ["can't", "can not"],
 ["cant", "can not"], ["im", "i am"], ["i'm", "i am"], ["ive", "i have"], ["youre", "you are"], ["theyre", "they are"], ["we're", "we are"],
 ["were", "we are"], ["were", "were"], ["ill", "i will"], ["ill", "ill"], ["well", "we will"], ["its", "it is"], ["its", "its"],
 ["hes", "he has"], ["shes", "she is"], ["it's", "it has"], ["that's", "that is"], ["what's", "what is"], ["there's", "there is"],
 ["i'd", "i would"], ["i'd", "i had"], ["let's", "let us"], ["couldn't", "could not"], ["mustn't", "must not"], ["shouldnt", "should not"],
 ["sister's", "sister has"], ["sister's", "sister's"], ["sisters", "sister's"], ["they'll", "they will"], ["id", "id"], ["id", "i had"]]
  .forEach(([t, want]) => check("contracción " + t + " -> " + want, rd(t).indexOf(want) >= 0, rd(t).join(" | ")));
check("'ll not no vale", rd("i'll", "not").indexOf("i will") < 0);
check("'s modelo: it's been -> has", E.modelReadings("It's been raining").indexOf("it has been raining") >= 0);
check("'s modelo: it's snowing -> is", E.modelReadings("It's snowing")[0] === "it is snowing");
check("'d modelo: I'd gone -> had", E.modelReadings("I'd gone")[0] === "i had gone");
check("'d modelo: I'd go -> would", E.modelReadings("I'd go")[0] === "i would go");
const ex = [...new Set(E.expandPattern("(I|We) [usually] (get up|wake up) at (seven|7) [o'clock] {T:every day}").map(s => s.toLowerCase()))];
// 2 sujetos × 2 (usually) × 2 verbos × 2 (seven/7) × 2 (o'clock) × 2 (every/each day) × 2 posiciones (principio/final)
check("plantilla: nº de variantes", ex.length === 128, ex.length);
check("plantilla: hueco al principio", ex.indexOf("every day we usually wake up at 7") >= 0);
check("plantilla: anidada y opcional con alternativas", E.expandPattern("a (b (c|d)|e) [f|g]").length === 9);
check("plantilla: ; separa oraciones", E.expandPattern("x y {T:today} ; z w").indexOf("today x y z w") >= 0 &&
  E.expandPattern("x y {T:today} ; z w").indexOf("x y z w today") < 0);
{
  const big = { qid: "tope", type: "translate", answers: ["a"], pat: ["(a|b|c|d|e|f|g|h|i|j) (a|b|c|d|e|f|g|h|i|j) (a|b|c|d|e|f|g|h|i|j) (a|b|c|d|e|f|g|h|i|j)"] };
  const before = T.warnings.length;
  E.prepare(big);
  check("tope de 5000 variantes + aviso", big.accepted.size <= E.MAX_VARIANTS && T.warnings.length > before, big.accepted.size);
}

/* ---------- rendimiento: expandir TODO el nivel 3 ---------- */
const t0 = Number(process.hrtime.bigint()) / 1e6;
QS.forEach(q => E.prepare(q));
const ms = Number(process.hrtime.bigint()) / 1e6 - t0;
check("expansión de todo el nivel 3 < 200 ms", ms < 200, ms.toFixed(1) + " ms");

/* ---------- no se guarda ni se envía la lista de aceptadas ---------- */
QS.forEach(q => {
  const j = JSON.stringify(q);
  check(q.qid + ": accepted no serializable", j.indexOf("accepted") < 0 && j.indexOf("_l3trie") < 0);
  check(q.qid + ": modelAnswer ≤ 3 respuestas", T.modelAnswer(q).split("|").length <= 3, T.modelAnswer(q));
  check(q.qid + ": answers mostradas ≤ 3", q.answers.length <= 3);
});
{
  T.saveResultLocally({ moduleId: "ps_l3", score: 5, answers: QS.slice(0, 2) });
  const saved = Object.values(T.store).join(" ");
  check("saveResultLocally no guarda accepted", saved.indexOf("accepted") < 0 && saved.indexOf("get up at 7") < 0);
}

/* ---------- por pregunta ---------- */
const rows = [];
QS.forEach(q => {
  const c = CASES[q.qid];
  if (!c) { fails++; log.push("  ✗ " + q.qid + ": sin casos de test"); return; }
  const pos = autoPositives(q, c).concat(c.pos.map((p, k) => ["extra " + k, p]));
  const neg = c.neg.concat(["", "   ", ".", q.answers[0].split(" ")[0],
    q.answers[0].replace(/[.!?]$/, "").split(" ").reverse().join(" ")]);
  let pOk = 0, nOk = 0;
  pos.forEach(([name, s]) => {
    if (T.gradeTranslation(s, q)) pOk++;
    else { fails++; log.push("  ✗ " + q.qid + " POSITIVO rechazado (" + name + "): " + JSON.stringify(s)); }
  });
  neg.forEach(s => {
    if (!T.gradeTranslation(s, q)) nOk++;
    else { fails++; log.push("  ✗ " + q.qid + " NEGATIVO aceptado: " + JSON.stringify(s)); }
  });
  rows.push([q.qid, q.accepted.size, pOk + "/" + pos.length, nOk + "/" + neg.length]);
});

const pad = (s, n) => String(s).padEnd(n);
console.log("\n" + pad("qid", 14) + "| " + pad("variantes", 10) + "| " + pad("positivos OK", 13) + "| negativos OK");
console.log("-".repeat(56));
rows.forEach(r => console.log(pad(r[0], 14) + "| " + pad(r[1], 10) + "| " + pad(r[2], 13) + "| " + r[3]));
const tot = (i) => rows.reduce((a, r) => { const [x, y] = r[i].split("/").map(Number); return [a[0] + x, a[1] + y]; }, [0, 0]).join("/");
console.log("-".repeat(56));
console.log(pad("TOTAL " + rows.length, 14) + "| " + pad(rows.reduce((a, r) => a + r[1], 0), 10) + "| " + pad(tot(2), 13) + "| " + tot(3));
console.log("Expansión de todo el nivel 3: " + ms.toFixed(1) + " ms");
if (fails) { console.log("\n" + fails + " FALLOS:\n" + log.join("\n")); process.exit(1); }
console.log("\nTODO OK ✔");
