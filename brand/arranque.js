// Publicaciones de arranque de Instagram: presentación, carrusel "cómo funciona", story y portadas de destacadas.
// Uso: FONT=ruta/InterDisplay-ExtraBold.ttf FONT_TEXT=ruta/Inter-SemiBold.ttf node brand/arranque.js  (desde la raíz del repo)
// Las fotos salen de brand/.cache/ (alta resolución, ver generar.py) o, si no están, de img/p/.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const OUT = path.join(ROOT, "brand", "png", "arranque");
const BLUE = "#2a78d6", INK = "#0b0b0b", SURFACE = "#f4f4f2", MUTED = "#52514e";
const svg = name => fs.readFileSync(path.join(ROOT, "brand", name), "utf8");
const sized = (name, style) => svg(name).replace("<svg ", `<svg style="${style}" `);
const dataUri = file => "data:image/webp;base64," + fs.readFileSync(file).toString("base64");
const fontFace = (name, file) => file && fs.existsSync(file)
  ? `@font-face { font-family: "${name}"; src: url("data:font/ttf;base64,${fs.readFileSync(file).toString("base64")}"); }` : "";
const CSS = `${fontFace("InterDisplay", process.env.FONT)}${fontFace("InterText", process.env.FONT_TEXT)}
  * { margin: 0; box-sizing: border-box; } p { text-wrap: balance; } body { font-family: InterText, InterDisplay, system-ui, sans-serif; }
  .d { font-family: InterDisplay, system-ui, sans-serif; font-weight: 800; letter-spacing: -.03em; }`;

// Datos reales: tiendas con precio, guitarras con foto y la guitarra con más tiendas para el ejemplo.
const latest = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "latest.json"), "utf8"));
const isRef = id => latest.stores.find(s => s.id === id)?.reference;
const storeName = id => latest.stores.find(s => s.id === id)?.name || id;
const okItems = latest.items.filter(i => i.status === "ok" && i.price != null && !isRef(i.store));
const stores = [...new Set(okItems.map(i => storeName(i.store).replace(/ \(eBay\)$/, "")))].sort();
const guitars = latest.products.filter(p => p.category === "guitarra" && p.thumb).map(p => {
  const hi = path.join(ROOT, "brand", ".cache", p.thumb);
  const items = okItems.filter(i => i.sku === p.sku).sort((a, b) => a.price - b.price);
  return { ...p, items, img: dataUri(fs.existsSync(hi) ? hi : path.join(ROOT, "img", "p", p.thumb)) };
}).filter(p => p.items.length);
const pickNames = ["Player II Telecaster MN 3-Color", "Les Paul Standard 50s", "RG550", "Casino", "Player II Stratocaster MN Aquatone", "SG Standard"];
const showcase = pickNames.map(n => guitars.find(g => g.name.includes(n))).filter(Boolean);
const example = guitars.find(g => g.name.includes("Player II Stratocaster RW Polar"))
  || [...guitars].sort((a, b) => b.items.length - a.items.length)[0];
const eur = v => v.toLocaleString("es-ES", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €";
const day = new Date(example.items[0].price_date).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });

const guitarRow = (height, maxWidth) => showcase.map(g =>
  `<img src="${g.img}" style="height:${height}px;max-width:${maxWidth}px;object-fit:contain">`).join("");

// Iconos de trazo para las destacadas (24×24, estilo línea).
const ICONS = {
  chollos: `<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>`,
  "como-funciona": `<circle cx="12" cy="12" r="9.5"/><path d="M9.2 9.2a3 3 0 0 1 5.7 1c0 2-2.9 2.6-2.9 4.3"/><circle cx="12" cy="17.6" r=".9" fill="currentColor"/>`,
  tiendas: `<path d="M3.5 9 5 3.5h14L20.5 9"/><path d="M3.5 9h17v1.5a2.8 2.8 0 0 1-5.6 0 2.8 2.8 0 0 1-5.8 0 2.8 2.8 0 0 1-5.6 0z"/><path d="M5 13v7.5h14V13"/><path d="M10 20.5V16h4v4.5"/>`,
};
const icon = (name, size) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor"
  stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;

// Cabecera común del carrusel: logo pequeño y número de diapositiva.
const slideHead = n => `<div style="display:flex;justify-content:space-between;align-items:center">
  ${sized("logo-sin-lema.svg", "height:80px;width:auto")}
  <span class="d" style="font-size:30px;color:${MUTED};letter-spacing:0">${n}/4</span></div>`;
const slide = (n, body) => `<div style="width:1080px;height:1350px;background:${SURFACE};padding:70px;display:flex;flex-direction:column">
  ${slideHead(n)}${body}</div>`;
const h1 = (text, size = 84, color = INK) => `<p class="d" style="font-size:${size}px;line-height:1.04;color:${color}">${text}</p>`;
const lead = (text, color = MUTED) => `<p style="font-size:38px;line-height:1.3;color:${color};margin-top:26px">${text}</p>`;

const pages = {
  "1-presentacion.png": [1080, 1350, `<div style="width:1080px;height:1350px;background:${BLUE};color:#fff;padding:90px 80px 80px;display:flex;flex-direction:column">
      <div style="width:440px">${sized("logo-blanco.svg", "width:440px;height:auto;display:block")}</div>
      <div style="margin-top:60px">${h1("Compara el precio de tu próxima guitarra.", 92, "#fff")}
        ${lead("Revisamos cada día las tiendas de Europa y te decimos dónde está más barata.", "rgba(255,255,255,.9)")}</div>
      <div style="flex:1;background:#fff;border-radius:44px;margin-top:50px;display:flex;justify-content:space-evenly;align-items:center;padding:0 24px;min-height:0">
        ${guitarRow(360, 140)}</div>
      <p class="d" style="font-size:44px;margin-top:44px;letter-spacing:-.01em">guitle.com</p></div>`],

  "2-carrusel-1.png": [1080, 1350, slide(1, `
      <div style="margin-top:90px">${h1("¿Cómo funciona guitle?", 104)}${lead("Encuentra la guitarra que buscas al mejor precio, sin abrir veinte pestañas.")}</div>
      <div style="flex:1;background:#fff;border-radius:40px;margin-top:60px;display:flex;justify-content:space-evenly;align-items:center;padding:0 20px">
        ${guitarRow(560, 145)}</div>
      <p class="d" style="font-size:38px;color:${BLUE};margin-top:40px;text-align:right;letter-spacing:-.01em">Desliza →</p>`)],

  "2-carrusel-2.png": [1080, 1350, slide(2, `
      <div style="margin-top:90px">${h1(`Revisamos ${stores.length} tiendas cada día`)}${lead("Precio, disponibilidad y descuentos de cada guitarra, actualizados a diario.")}</div>
      <div style="display:flex;flex-wrap:wrap;gap:20px;margin-top:70px">
        ${stores.map(s => `<span class="d" style="background:#fff;font-size:42px;padding:22px 34px;border-radius:999px;letter-spacing:-.01em">${s}</span>`).join("")}</div>
      <p style="font-size:30px;color:${MUTED};margin-top:auto">Y vamos sumando más.</p>`)],

  "2-carrusel-3.png": [1080, 1350, slide(3, `
      <div style="margin-top:70px">${h1("Te decimos dónde está más barata")}</div>
      <div style="flex:1;background:#fff;border-radius:40px;margin-top:50px;padding:44px;display:flex;gap:40px;align-items:center">
        <img src="${example.img}" style="height:680px;max-width:250px;object-fit:contain">
        <div style="flex:1">
          <p style="font-size:26px;color:${MUTED};text-transform:uppercase;letter-spacing:.06em">${example.brand}</p>
          <p class="d" style="font-size:40px;line-height:1.08;margin:6px 0 26px">${example.name.replace(example.brand + " ", "")}</p>
          ${example.items.slice(0, 6).map((i, k) => `<div style="display:flex;justify-content:space-between;align-items:center;padding:16px 22px;border-radius:18px;margin-top:8px;
              font-size:31px;${k ? `color:${INK}` : `background:${BLUE};color:#fff`}">
            <span>${storeName(i.store)}</span><span class="d" style="letter-spacing:-.01em">${eur(i.price)}</span></div>`).join("")}</div></div>
      <p style="font-size:26px;color:${MUTED};margin-top:24px">Precios reales del ${day}.</p>`)],

  "2-carrusel-4.png": [1080, 1350, slide(4, `
      <div style="margin-top:90px">${h1("Y aquí, los chollos del día", 104)}
        ${lead("Cada día publicamos las mejores bajadas de precio. Síguenos para no perderte ninguna.")}</div>
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:40px">
        <span style="color:${BLUE}">${icon("chollos", 230)}</span>
        <span class="d" style="background:${BLUE};color:#fff;font-size:56px;padding:30px 64px;border-radius:999px;letter-spacing:-.01em">Busca tu guitarra en guitle.com</span></div>`)],

  "3-story-ya-estamos-aqui.png": [1080, 1920, `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;padding:150px 80px;display:flex;flex-direction:column;align-items:center;text-align:center">
      ${sized("logo-blanco.svg", "width:640px;height:auto")}
      <div style="margin-top:90px">${h1("¡Ya estamos aquí!", 118, "#fff")}
        ${lead("Compara el precio de las guitarras en las tiendas de Europa, cada día.", "rgba(255,255,255,.9)")}</div>
      <div style="background:#fff;border-radius:48px;width:100%;height:560px;margin-top:70px;display:flex;justify-content:space-evenly;align-items:center;padding:0 24px">
        ${guitarRow(600, 135)}</div>
      <!-- Hueco para el sticker de enlace a guitle.com (se pone en la app) -->
      <p class="d" style="font-size:44px;margin-top:auto;letter-spacing:-.01em">guitle.com</p></div>`],

  // Primera story del destacado de chollos: explica qué hay dentro y que los precios son del día.
  "5-cartel-chollos.png": [1080, 1920, `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;padding:150px 80px;display:flex;flex-direction:column;align-items:center;text-align:center">
      ${sized("logo-blanco.svg", "width:520px;height:auto")}
      <div style="margin-top:150px">${icon("chollos", 300)}</div>
      <div style="margin-top:60px">${h1("Chollos", 170, "#fff")}
        ${lead("Las mejores bajadas de precio en guitarras, cada día.", "rgba(255,255,255,.92)")}</div>
      <div style="background:#fff;color:${INK};border-radius:40px;width:100%;margin-top:auto;padding:44px 50px;text-align:left">
        <p class="d" style="font-size:44px;line-height:1.1">Ojo: cada precio es del día de su story.</p>
        <p style="font-size:34px;line-height:1.3;color:${MUTED};margin-top:14px">Los precios cambian a diario. Consulta el precio actual en <b style="color:${BLUE}">guitle.com</b>.</p></div></div>`],
};
// Portadas de destacadas: se suben como story; Instagram muestra el círculo central.
for (const name of Object.keys(ICONS)) {
  pages[`4-destacada-${name}.png`] = [1080, 1920, `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;display:flex;align-items:center;justify-content:center">
      ${icon(name, 400)}</div>`];
}

(async () => {
  fs.mkdirSync(path.join(OUT, "jpg"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [out, [w, h, html]] of Object.entries(pages)) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<style>${CSS}</style>${html}`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, out) });
    // Instagram solo publica JPEG por la API
    await page.screenshot({ path: path.join(OUT, "jpg", out.replace(".png", ".jpg")), type: "jpeg", quality: 92 });
  }
  await browser.close();
  console.log(`${Object.keys(pages).length} imágenes generadas en brand/png/arranque/ (PNG) y jpg/`);
})();
