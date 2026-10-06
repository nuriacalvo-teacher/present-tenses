// Extrae allClips() de video/index.html (con su propio LESSON) y lo imprime en JSON.
const fs = require("fs");
const h = fs.readFileSync(process.argv[2], "utf8");
const lesson = h.slice(h.indexOf("var LESSON = "), h.indexOf("\n};\n", h.indexOf("var LESSON = ")) + 3);
const grab = n => { const a = h.indexOf("function " + n + "("); let d = 0, i = h.indexOf("{", a);
  for (;; i++) { if (h[i] == "{") d++; if (h[i] == "}" && --d == 0) return h.slice(a, i + 1); } };
const src = lesson + "\nvar SCRIPT = LESSON.scenes, QUIZ = LESSON.quiz;\n" +
  ["turnsOf", "questionText", "feedbackText", "answerText", "allClips"].map(grab).join("\n") + "\nallClips();";
console.log(JSON.stringify(eval(src)));
