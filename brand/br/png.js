// PNG de los logos por país (brand/<país>/*.svg). Uso: node brand/br/png.js [br|fr] (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const DIR = path.join(process.cwd(), "brand", process.argv[2] || "br");
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [file, width, transparent] of [["logo.svg", 2000, true], ["logo-blanco.svg", 2000, true], ["logo-negro.svg", 2000, true], ["instagram-perfil.svg", 1080, false]]) {
    const svg = fs.readFileSync(path.join(DIR, file), "utf8");
    const [, , vw, vh] = svg.match(/viewBox="([^"]+)"/)[1].split(" ").map(Number);
    const height = Math.round(width * vh / vw);
    await page.setViewportSize({ width, height });
    await page.setContent(`<style>*{margin:0}</style>${svg.replace(/<svg [^>]*?(width="\d+" height="\d+")?/, (m) => m.replace(/ width="\d+" height="\d+"/, "") + ` style="width:${width}px;height:${height}px;display:block"`)}`);
    await page.screenshot({ path: path.join(DIR, file.replace(".svg", ".png")), omitBackground: transparent });
  }
  await browser.close();
  console.log(`PNG en brand/${process.argv[2] || "br"}/`);
})();
