// PNG del kit de marca a partir de los SVG de brand/ y de los datos reales (data/latest.json, img/p/).
// Uso: FONT=ruta/InterDisplay-ExtraBold.ttf FONT_TEXT=ruta/Inter-SemiBold.ttf node brand/png.js  (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const OUT = path.join(ROOT, "brand", "png");
const BLUE = "#2a78d6", INK = "#0b0b0b", SURFACE = "#f4f4f2";
const svg = name => fs.readFileSync(path.join(ROOT, "brand", name), "utf8");
const dataUri = file => "data:image/webp;base64," + fs.readFileSync(file).toString("base64");
const fontFace = (name, file) => file && fs.existsSync(file)
  ? `@font-face { font-family: "${name}"; src: url("data:font/ttf;base64,${fs.readFileSync(file).toString("base64")}"); }` : "";
const CSS = `${fontFace("InterDisplay", process.env.FONT)}${fontFace("InterText", process.env.FONT_TEXT)}
  * { margin: 0; box-sizing: border-box; } body { font-family: InterText, InterDisplay, system-ui, sans-serif; }
  .d { font-family: InterDisplay, system-ui, sans-serif; font-weight: 800; letter-spacing: -.03em; }`;

// Guitarras de ejemplo: productos seguidos con miniatura, una por forma y con el mejor precio.
const latest = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "latest.json"), "utf8"));
const guitars = latest.products.filter(p => p.category === "guitarra" && p.thumb).map(p => {
  const items = latest.items.filter(i => i.sku === p.sku && i.status === "ok" && i.price != null
    && !latest.stores.find(s => s.id === i.store)?.reference).sort((a, b) => a.price - b.price);
  const hi = path.join(ROOT, "brand", ".cache", p.thumb);  // alta resolución (generar.py)
  return { ...p, best: items[0], img: dataUri(fs.existsSync(hi) ? hi : path.join(ROOT, "img", "p", p.thumb)) };
}).filter(p => p.best);
const pickNames = ["Player II Telecaster MN 3-Color", "Les Paul Standard 50s", "RG550", "Casino", "Player II Stratocaster MN Aquatone", "SG Standard", "Standard Telecaster MN BPG"];
const showcase = pickNames.map(n => guitars.find(g => g.name.includes(n))).filter(Boolean);
const deal = guitars.find(g => g.name.includes("Player II Stratocaster RW Polar")) || guitars[0];
const storeName = id => latest.stores.find(s => s.id === id)?.name || id;
const eur = v => v.toLocaleString("es-ES", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €";

const pages = {
  "instagram-perfil.png": [1080, 1080, `<div style="width:1080px;height:1080px">${svg("icono-cuadrado.svg").replace("<svg ", '<svg style="width:1080px;height:1080px" ')}</div>`],
  "portada-redes.png": [1500, 500, `<div style="width:1500px;height:500px;background:${SURFACE};display:flex;align-items:center;padding:0 80px;gap:40px">
      <div style="flex:none;width:560px">${svg("logo.svg").replace("<svg ", '<svg style="width:520px;height:auto;display:block" ')}
        <p style="margin-top:26px;font-size:26px;color:#52514e;line-height:1.35">Compara los precios de las guitarras en las tiendas de Europa, cada día.</p>
        <p class="d" style="margin-top:14px;font-size:28px;color:${BLUE}">guitle.com</p></div>
      <div style="flex:1;background:#fff;border-radius:36px;display:flex;justify-content:space-evenly;align-items:center;height:420px;padding:0 20px">
        ${showcase.slice(0, 6).map(g => `<img src="${g.img}" style="height:370px;max-width:120px;object-fit:contain">`).join("")}</div></div>`],
  "post-plantilla.png": [1080, 1350, `<div style="width:1080px;height:1350px;background:${SURFACE};padding:70px;display:flex;flex-direction:column">
      <div style="display:flex;justify-content:space-between;align-items:center">${svg("logo-sin-lema.svg").replace("<svg ", '<svg style="height:96px;width:auto" ')}
        <span class="d" style="background:${BLUE};color:#fff;font-size:34px;padding:14px 30px;border-radius:999px">Chollo de hoy</span></div>
      <div style="flex:1;background:#fff;border-radius:40px;margin:50px 0 40px;display:flex;align-items:center;justify-content:center">
        <img src="${deal.img}" style="height:640px"></div>
      <p style="font-size:34px;color:#52514e;text-transform:uppercase;letter-spacing:.06em">${deal.brand}</p>
      <p class="d" style="font-size:58px;line-height:1.08;color:${INK};margin-top:8px">${deal.name.replace(deal.brand + " ", "")}</p>
      <div style="display:flex;align-items:baseline;gap:24px;margin-top:22px">
        <span class="d" style="font-size:96px;color:${INK}">${eur(deal.best.price)}</span>
        <span style="font-size:34px;color:#52514e">en ${storeName(deal.best.store)}</span></div></div>`],
  "story-plantilla.png": [1080, 1920, `<div style="width:1080px;height:1920px;background:${BLUE};padding:130px 80px;display:flex;flex-direction:column;align-items:center;text-align:center;color:#fff">
      ${svg("logo-blanco.svg").replace("<svg ", '<svg style="width:640px;height:auto" ')}
      <div style="background:#fff;border-radius:48px;width:100%;flex:1;margin:70px 0 50px;display:flex;align-items:center;justify-content:center">
        <img src="${deal.img}" style="height:880px"></div>
      <p class="d" style="font-size:60px;line-height:1.1">${deal.name}</p>
      <p class="d" style="font-size:120px;margin-top:20px">${eur(deal.best.price)}</p>
      <p style="font-size:38px;margin-top:10px;opacity:.9">en ${storeName(deal.best.store)} · compáralo en guitle.com</p></div>`],
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  // Logos e iconos sueltos (fondo transparente)
  const logos = { "logo.png": ["logo.svg", 2000], "logo-blanco.png": ["logo-blanco.svg", 2000], "logo-negro.png": ["logo-negro.svg", 2000],
                  "logo-sin-lema.png": ["logo-sin-lema.svg", 2000], "icono.png": ["icono.svg", 1024], "icono-blanco.png": ["icono-blanco.svg", 1024] };
  for (const [out, [file, width]] of Object.entries(logos)) {
    const s = svg(file);
    const [, , vw, vh] = s.match(/viewBox="([^"]+)"/)[1].split(" ").map(Number);
    const height = Math.round(width * vh / vw);
    await page.setViewportSize({ width, height });
    await page.setContent(`<style>*{margin:0}</style>${s.replace("<svg ", `<svg style="width:${width}px;height:${height}px;display:block" `)}`);
    await page.screenshot({ path: path.join(OUT, out), omitBackground: true });
  }
  for (const [out, [w, h, html]] of Object.entries(pages)) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<style>${CSS}</style>${html}`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, out) });
  }
  // Iconos de la web (PWA)
  for (const [out, size] of [["icons/icon-192.png", 192], ["icons/icon-512.png", 512], ["icons/apple-touch-icon.png", 180]]) {
    await page.setViewportSize({ width: size, height: size });
    const s = out.includes("apple") ? svg("icono-cuadrado.svg") : svg("icono.svg");
    await page.setContent(`<style>*{margin:0}</style>${s.replace("<svg ", `<svg style="width:${size}px;height:${size}px;display:block" `)}`);
    await page.screenshot({ path: path.join(ROOT, out), omitBackground: !out.includes("apple") });
  }
  await browser.close();
  console.log("PNG generados en brand/png/ e icons/");
})();
