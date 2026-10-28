// Imágenes de Instagram del día a partir de social/<fecha>/plan.json (scraper/instagram.py):
// post-N.jpg (post de chollo o carrusel del top) y story-N.jpg (chollos). Fuente Inter de fonts/.
// Uso: node brand/social.js social/<fecha>   (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DIR = path.resolve(process.argv[2]);
const plan = JSON.parse(fs.readFileSync(path.join(DIR, "plan.json"), "utf8"));
const BLUE = "#2a78d6", INK = "#0b0b0b", SURFACE = "#f4f4f2", MUTED = "#52514e";
const svg = (name, style) => fs.readFileSync(path.join(ROOT, "brand", name), "utf8").replace("<svg ", `<svg style="${style}" `);
const b64 = file => fs.readFileSync(file).toString("base64");
const font = (w, file) => `@font-face { font-family: Inter; font-weight: ${w}; src: url("data:font/woff2;base64,${b64(path.join(ROOT, "fonts", file))}"); }`;
const CSS = font(600, "inter-semibold.woff2") + font(800, "inter-extrabold.woff2") + `
  * { margin: 0; box-sizing: border-box; } p { text-wrap: balance; }
  body { font-family: Inter, system-ui, sans-serif; font-weight: 600; }
  .d { font-weight: 800; letter-spacing: -.035em; }`;
const img = p => `data:image/webp;base64,${b64(path.join(DIR, p.photo))}`;
const eur = v => v.toLocaleString("es-ES", { useGrouping: "always", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €";
const esc = s => String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const model = p => esc(p.brand && p.name.startsWith(p.brand + " ") ? p.name.slice(p.brand.length + 1) : p.name);
const nameSize = (p, big) => { const n = model(p).length; return n > 46 ? big - 16 : n > 32 ? big - 8 : big; };
const pill = (text, bg, fg, size = 34) => `<span class="d" style="background:${bg};color:${fg};font-size:${size}px;padding:14px 30px;border-radius:999px;letter-spacing:-.01em;white-space:nowrap">${text}</span>`;
const KIND = { electrica: "Eléctrica", acustica: "Acústica", clasica: "Clásica" };

// Post 4:5 de un chollo
const dealPost = p => `<div style="width:1080px;height:1350px;background:${SURFACE};padding:64px 70px;display:flex;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center">${svg("logo-sin-lema.svg", "height:88px;width:auto")}
    ${pill("Chollo de hoy", BLUE, "#fff")}</div>
  <div style="flex:1;min-height:0;background:#fff;border-radius:40px;margin:44px 0 36px;display:flex;align-items:center;justify-content:center;padding:36px">
    <img src="${img(p)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>
  <p style="font-size:30px;color:${MUTED};text-transform:uppercase;letter-spacing:.06em">${esc(p.brand)} · ${KIND[p.kind]}</p>
  <p class="d" style="font-size:${nameSize(p, 56)}px;line-height:1.06;color:${INK};margin-top:8px">${model(p)}</p>
  <div style="display:flex;align-items:baseline;gap:22px;margin-top:18px">
    <span class="d" style="font-size:100px;line-height:1;color:${INK}">${eur(p.price)}</span>
    <span style="font-size:34px;color:${MUTED}">en ${esc(p.store)}</span></div>
  <p style="font-size:30px;color:${BLUE};margin-top:16px">${esc(p.why)}</p>
  <p style="font-size:24px;color:${MUTED};margin-top:18px">Precio del ${plan.fecha}, comparado en ${p.stores} tiendas · guitle.com</p></div>`;

// Story 9:16 de un chollo
const dealStory = p => `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;padding:120px 80px 110px;display:flex;flex-direction:column;align-items:center;text-align:center">
  ${svg("logo-blanco.svg", "width:420px;height:auto;flex:none")}
  <div style="margin-top:46px">${pill("Chollo del día", "#fff", BLUE, 40)}</div>
  <div style="flex:1;min-height:0;width:100%;background:#fff;border-radius:48px;margin:46px 0 44px;display:flex;align-items:center;justify-content:center;padding:44px">
    <img src="${img(p)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>
  <p style="font-size:32px;text-transform:uppercase;letter-spacing:.06em;opacity:.85">${esc(p.brand)}</p>
  <p class="d" style="font-size:${nameSize(p, 60)}px;line-height:1.06;margin-top:8px">${model(p)}</p>
  <p class="d" style="font-size:132px;line-height:1;margin-top:24px">${eur(p.price)}</p>
  <p style="font-size:38px;margin-top:12px">en ${esc(p.store)}</p>
  <p style="font-size:30px;margin-top:22px;background:rgba(255,255,255,.16);padding:14px 26px;border-radius:20px">${esc(p.why)}</p>
  <p style="font-size:26px;margin-top:34px;opacity:.85">Precio del ${plan.fecha} · Enlace en la bio · guitle.com</p></div>`;

// Carrusel del top: portada, una diapositiva por guitarra y cierre
const topCover = t => `<div style="width:1080px;height:1350px;background:${BLUE};color:#fff;padding:80px 70px 64px;display:flex;flex-direction:column">
  ${svg("logo-blanco.svg", "width:380px;height:auto;flex:none")}
  <p class="d" style="font-size:112px;line-height:1;margin-top:64px">${esc(t.title[0].toUpperCase() + t.title.slice(1))}</p>
  <p style="font-size:36px;margin-top:24px;opacity:.92">Las más vendidas en las tiendas, con su mejor precio de hoy.</p>
  <div style="flex:1;min-height:0;background:#fff;border-radius:44px;margin-top:50px;display:flex;justify-content:space-evenly;align-items:center;padding:30px 20px">
    ${t.picks.map(p => `<img src="${img(p)}" style="height:100%;max-width:${Math.floor(880 / t.picks.length)}px;object-fit:contain">`).join("")}</div>
  <p class="d" style="font-size:38px;margin-top:34px;text-align:right;letter-spacing:-.01em">Desliza →</p></div>`;
const topSlide = (t, p, i) => `<div style="width:1080px;height:1350px;background:${SURFACE};padding:64px 70px;display:flex;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center">${svg("logo-sin-lema.svg", "height:80px;width:auto")}
    ${pill(`${i} / ${t.picks.length}`, BLUE, "#fff", 34)}</div>
  <div style="flex:1;min-height:0;background:#fff;border-radius:40px;margin:44px 0 36px;display:flex;align-items:center;justify-content:center;padding:36px">
    <img src="${img(p)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>
  <p style="font-size:30px;color:${MUTED};text-transform:uppercase;letter-spacing:.06em">${esc(p.brand)}</p>
  <p class="d" style="font-size:${nameSize(p, 58)}px;line-height:1.06;color:${INK};margin-top:8px">${model(p)}</p>
  <div style="display:flex;align-items:baseline;gap:22px;margin-top:18px">
    <span class="d" style="font-size:96px;line-height:1;color:${INK}">${eur(p.price)}</span>
    <span style="font-size:34px;color:${MUTED}">en ${esc(p.store)}</span></div>
  <p style="font-size:26px;color:${MUTED};margin-top:20px">La venden ${p.stores} tiendas · precio del ${plan.fecha}</p></div>`;
const topEnd = () => `<div style="width:1080px;height:1350px;background:${BLUE};color:#fff;padding:80px 70px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center">
  <p class="d" style="font-size:120px;line-height:1">¿Con cuál te quedas?</p>
  <p style="font-size:40px;margin-top:36px;opacity:.92">Cuéntanoslo en comentarios y guarda este post para cuando vayas a comprar.</p>
  <div style="margin-top:70px">${pill("Compara precios en guitle.com", "#fff", BLUE, 50)}</div></div>`;

const pages = [];
const post = plan.post;
if (post.type === "chollo") pages.push(["post-1.jpg", 1080, 1350, dealPost(post.deal)]);
else pages.push(["post-1.jpg", 1080, 1350, topCover(post)],
  ...post.picks.map((p, i) => [`post-${i + 2}.jpg`, 1080, 1350, topSlide(post, p, i + 1)]),
  [`post-${post.picks.length + 2}.jpg`, 1080, 1350, topEnd()]);
plan.stories.forEach((p, i) => pages.push([`story-${i + 1}.jpg`, 1080, 1920, dealStory(p)]));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [out, w, h, html] of pages) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<style>${CSS}</style>${html}`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(DIR, out), type: "jpeg", quality: 90 });
  }
  await browser.close();
  console.log(`${pages.length} imágenes en ${path.relative(ROOT, DIR)}/`);
})();
