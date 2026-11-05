// Imágenes del disco de @guitle.uk a partir de <carpeta>/plan.json (scraper/discos_ig.py): post.jpg (4:5) y story.jpg (9:16).
// Uso: node brand/discos.js social/<fecha>/uk/discos   (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DIR = path.resolve(process.argv[2]);
const plan = JSON.parse(fs.readFileSync(path.join(DIR, "plan.json"), "utf8"));
const d = plan.disco;
const BLUE = "#2a78d6", INK = "#0b0b0b", SURFACE = "#f4f4f2", MUTED = "#52514e", GREEN = "#1f9d55", YELLOW = "#ffd84d";
const b64 = f => fs.readFileSync(f).toString("base64");
const svg = (name, style) => fs.readFileSync(path.join(ROOT, "brand", name), "utf8").replace("<svg ", `<svg style="${style}" `);
const font = (w, f) => `@font-face{font-family:Inter;font-weight:${w};src:url(data:font/woff2;base64,${b64(path.join(ROOT, "fonts", f))})}`;
const CSS = font(600, "inter-semibold.woff2") + font(800, "inter-extrabold.woff2") +
  `*{margin:0;box-sizing:border-box} p{text-wrap:balance} body{font-family:Inter,sans-serif;font-weight:600} .d{font-weight:800;letter-spacing:-.035em}`;
const esc = s => String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const gbp = v => "£" + v.toLocaleString("en-GB", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const mime = d.photo.endsWith(".png") ? "image/png" : "image/jpeg";
const cover = `data:${mime};base64,${b64(path.join(DIR, d.photo))}`;
const semana = plan.tipo === "semana";
const cab = semana ? "Vinyl deal of the week" : `Same record, ${gbp(d.ahorro)} cheaper`;
const size = (t, big) => (t.length > 60 ? big - 18 : t.length > 38 ? big - 10 : big);
const pill = (text, bg, fg, fs) => `<span class="d" style="background:${bg};color:${fg};font-size:${fs}px;padding:14px 30px;border-radius:999px;letter-spacing:-.01em;white-space:nowrap">${text}</span>`;

const post = `<div style="width:1080px;height:1350px;background:${SURFACE};padding:60px 70px;display:flex;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center">${svg("logo-sin-lema.svg", "height:80px;width:auto")}
    ${pill(semana ? "🏆 Deal of the week" : "💿 Record deal", semana ? YELLOW : BLUE, semana ? INK : "#fff", 32)}</div>
  <div style="flex:1"></div>
  <p class="d" style="font-size:${semana ? 84 : 80}px;line-height:1;color:${INK}">${esc(cab)}</p>
  <div style="display:flex;gap:44px;margin-top:40px;align-items:center">
    <img src="${cover}" style="width:560px;height:560px;object-fit:cover;border-radius:24px;box-shadow:0 24px 60px rgba(0,0,0,.18);flex:none">
    <div style="display:flex;flex-direction:column;gap:22px">
      <div style="background:#fff;border-radius:28px;padding:28px 30px"><p style="font-size:26px;color:${GREEN}">Cheapest today</p>
        <p class="d" style="font-size:${gbp(d.lo).length > 6 ? 80 : 96}px;line-height:1;color:${GREEN};margin-top:6px">${gbp(d.lo)}</p>
        <p style="font-size:30px;color:${INK};margin-top:8px">at ${esc(d.tienda)}</p></div>
      <div style="padding:0 30px"><p style="font-size:26px;color:${MUTED}">Other UK record shops</p>
        <p class="d" style="font-size:56px;line-height:1.1;color:${MUTED}">up to ${gbp(d.hi)}</p></div></div></div>
  <p style="font-size:30px;color:${MUTED};text-transform:uppercase;letter-spacing:.06em;margin-top:44px">${esc(d.artist)} · ${esc(plan.fmt)}</p>
  <p class="d" style="font-size:${size(d.title, 58)}px;line-height:1.06;color:${INK};margin-top:8px">${esc(d.title)}</p>
  <div style="flex:1"></div>
  <p style="font-size:26px;color:${MUTED}">We compare prices across UK record shops · guitle.com/uk/records</p></div>`;

const story = `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;padding:120px 80px 110px;display:flex;flex-direction:column;align-items:center;text-align:center">
  ${svg("logo-blanco-sin-lema.svg", "width:360px;height:auto;flex:none")}
  <div style="margin-top:44px">${pill(semana ? "🏆 Vinyl deal of the week" : "💿 Same record, cheaper", semana ? YELLOW : "#fff", semana ? INK : BLUE, 38)}</div>
  <img src="${cover}" style="width:780px;height:780px;object-fit:cover;border-radius:32px;margin-top:56px;box-shadow:0 30px 80px rgba(0,0,0,.25)">
  <p style="font-size:32px;text-transform:uppercase;letter-spacing:.06em;opacity:.85;margin-top:48px">${esc(d.artist)} · ${esc(plan.fmt)}</p>
  <p class="d" style="font-size:${size(d.title, 62)}px;line-height:1.06;margin-top:10px">${esc(d.title)}</p>
  <p class="d" style="font-size:140px;line-height:1;margin-top:34px">${gbp(d.lo)}</p>
  <p style="font-size:38px;margin-top:10px">at ${esc(d.tienda)}</p>
  <p style="font-size:34px;margin-top:26px;background:rgba(255,255,255,.16);padding:14px 30px;border-radius:20px">Up to ${gbp(d.hi)} elsewhere · save ${gbp(d.ahorro)}</p>
  <div style="flex:1"></div>
  <p style="font-size:30px;opacity:.9">Prices & stock: link in bio · guitle.com/uk/records</p></div>`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [out, w, h, html] of [["post.jpg", 1080, 1350, post], ["story.jpg", 1080, 1920, story]]) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<style>${CSS}</style>${html}`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(DIR, out), type: "jpeg", quality: 90 });
  }
  await browser.close();
  console.log(`post.jpg y story.jpg en ${path.relative(ROOT, DIR)}/`);
})();
