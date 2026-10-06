// Captura cada escena de video/index.html con todas sus animaciones encendidas,
// para revisar que nada se sale ni choca con el subtítulo.
//   node tools/comprobar/capturas.js CARPETA_DE_SALIDA   (desde la raiz)
const path = require("path");
let pw; try { pw = require("playwright"); } catch (e) { pw = require("/opt/node22/lib/node_modules/playwright"); }
(async () => {
  const out = process.argv[2] || ".";
  const b = await pw.chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
  const errs = []; p.on("pageerror", e => errs.push(String(e)));
  await p.goto("file://" + path.resolve("video/index.html")); await p.waitForTimeout(800);
  const n = await p.evaluate(() => document.querySelectorAll("section.scene").length);
  for (let i = 0; i < n; i++) {
    const choque = await p.evaluate(i => {
      document.querySelectorAll("section.scene").forEach((s, k) => s.hidden = k !== i);
      const s = document.querySelectorAll("section.scene")[i];
      s.querySelectorAll("[data-b]").forEach(e => e.classList.add("on"));
      const cap = document.querySelector(".caption").getBoundingClientRect(); let peor = 0;
      s.querySelectorAll(".ex, .note, .vs-c, .tl, .chips, .formula, .meaning, .opts, .recap, .practise").forEach(e => {
        const q = e.getBoundingClientRect(); if (q.height && q.right > cap.left && q.left < cap.right) peor = Math.max(peor, q.bottom - cap.top);
      });
      return Math.round(peor);
    }, i);
    await p.waitForTimeout(2500);
    await p.screenshot({ path: path.join(out, "escena" + i + ".png") });
    console.log("escena", i, choque > 0 ? "CHOCA con el subtítulo (" + choque + " px)" : "bien");
  }
  console.log("errores JS:", errs.length ? errs : "ninguno"); await b.close();
})();
