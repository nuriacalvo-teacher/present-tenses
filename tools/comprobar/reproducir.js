// Reproduce el vídeo entero en Chromium a velocidad x8 y responde el quiz:
// acierta las preguntas pares y falla las impares. Al final dice la nota,
// los clips que han sonado, si se ha usado la voz del navegador y los
// errores de JavaScript.
//   (cd video/.. && npx http-server -p 8766 -s . &)   sirve la raiz del repositorio
//   NO_PROXY=localhost node tools/comprobar/reproducir.js http://localhost:8766/video/index.html CARPETA
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
const fs = require("fs"), path = require("path");
(async () => {
  const url = process.argv[2], out = process.argv[3] || ".";
  const b = await pw.chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required"] });
  const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = [];
  p.on("pageerror", e => errs.push(String(e)));
  p.on("console", m => { if (m.type() === "error" && !/fonts|ERR_CERT/.test(m.text())) errs.push(m.text()); });
  await p.addInitScript(() => {
    window.__played = []; window.__tts = [];
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { this.playbackRate = 8; window.__played.push(this.src.split("/").pop()); return play.call(this); };
    if (window.speechSynthesis) window.speechSynthesis.speak = u => { if (u.text.trim()) window.__tts.push(u.text); setTimeout(() => u.onend && u.onend(), 50); };
  });
  await p.goto(url); await p.waitForTimeout(1000);
  // la última frase del cierre marca el final
  const fin = await p.evaluate(() => { const L = LESSON.scenes[LESSON.scenes.length - 1]; let t = L[L.length - 1]; t = typeof t === "string" ? t : t[t.length - 1];
    return t.replace(/^S:\s*/, "").replace(/^\[[^\]]*\]\s*/, ""); });
  await p.click("#startBtn");
  const t0 = Date.now(); let done = false;
  while (Date.now() - t0 < 900000) {
    const s = await p.evaluate(() => ({ quiz: !document.querySelector("section.quiz").hidden,
      qi: +document.getElementById("qNum").textContent - 1,
      opts: document.querySelectorAll("#opts .opt:not(.correct):not(.wrong):not(.dim)").length,
      fb: !document.getElementById("fb").hidden, cap: document.getElementById("caption").textContent }));
    if (s.quiz && s.opts && !s.fb && /^Question/.test(s.cap)) {
      const a = await p.evaluate(qi => LESSON.quiz[qi].a, s.qi);
      await p.waitForTimeout(400);
      await p.locator("#opts .opt").nth(s.qi % 2 === 0 ? a : (a + 1) % 3).click();
    } else if (s.quiz && s.fb) {
      await p.waitForTimeout(1500);
      if (await p.locator("#nextQ").isVisible()) await p.click("#nextQ");
    } else if (s.cap === fin) { await p.waitForTimeout(2500); done = true; break; }
    await p.waitForTimeout(250);
  }
  const r = await p.evaluate(() => ({ played: window.__played, tts: window.__tts, score: document.getElementById("score").textContent }));
  await p.screenshot({ path: path.join(out, "final.png") });
  const man = JSON.parse(fs.readFileSync(path.resolve("video/audio/manifest.json"))).clips;
  const sonados = new Set(r.played.map(f => f.replace(/\.mp3$/, "")));
  const faltan = Object.keys(man).filter(k => !sonados.has(k) && !/^q\d+_(a\d+|ok|no)$/.test(k));
  console.log("terminado:", done, "· segundos:", Math.round((Date.now() - t0) / 1000), "· nota:", r.score + "/" + await p.evaluate(() => LESSON.quiz.length));
  console.log("clips sonados:", sonados.size, "· sin sonar (sin contar opciones no elegidas):", faltan.length ? faltan : "ninguno");
  console.log("frases con voz del navegador:", r.tts.length ? r.tts : "ninguna");
  console.log("errores JS:", errs.length ? errs : "ninguno");
  await b.close();
})();
