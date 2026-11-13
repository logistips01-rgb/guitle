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
// Moneda y textos del país (plan.cc y plan.t, de scraper/discos_ig.py); por defecto, Reino Unido en inglés
const gbp = plan.cc && plan.cc !== "uk"
  ? v => v.toLocaleString("es-ES", { useGrouping: "always", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €"
  : v => "£" + v.toLocaleString("en-GB", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const T = Object.assign({ cab_same: `Same record, ${gbp(d.ahorro)} cheaper`, cab_semana: "Vinyl deal of the week",
  pill_post: "💿 Record deal", pill_post_semana: "🏆 Deal of the week", pill_story: "💿 Same record, cheaper",
  pill_story_semana: "🏆 Vinyl deal of the week", cheapest: "Cheapest today", at: "at", others: "Other UK record shops",
  upto: "up to", footer: "We compare prices across UK record shops · guitle.com/uk/records",
  elsewhere: `Up to ${gbp(d.hi)} elsewhere · save ${gbp(d.ahorro)}`, save: `You save ${gbp(d.ahorro)}`,
  story_footer: "Prices & stock: link in bio · guitle.com/uk/records" }, plan.t || {});
const mime = d.photo.endsWith(".png") ? "image/png" : "image/jpeg";
const cover = `data:${mime};base64,${b64(path.join(DIR, d.photo))}`;
const semana = plan.tipo === "semana";
const cab = semana ? T.cab_semana : T.cab_same;
const size = (t, big) => (t.length > 60 ? big - 18 : t.length > 38 ? big - 10 : big);
const pill = (text, bg, fg, fs) => `<span class="d" style="background:${bg};color:${fg};font-size:${fs}px;padding:14px 30px;border-radius:999px;letter-spacing:-.01em;white-space:nowrap">${text}</span>`;

const post = `<div style="width:1080px;height:1350px;background:${SURFACE};padding:60px 70px;display:flex;flex-direction:column">
  <div style="display:flex;justify-content:space-between;align-items:center">${svg("logo-sin-lema.svg", "height:80px;width:auto")}
    ${pill(semana ? T.pill_post_semana : T.pill_post, semana ? YELLOW : BLUE, semana ? INK : "#fff", 32)}</div>
  <div style="flex:1"></div>
  <p class="d" style="font-size:${semana ? 84 : 80}px;line-height:1;color:${INK}">${esc(cab)}</p>
  <div style="display:flex;gap:44px;margin-top:40px;align-items:center">
    <img src="${cover}" style="width:560px;height:560px;object-fit:cover;border-radius:24px;box-shadow:0 24px 60px rgba(0,0,0,.18);flex:none">
    <div style="display:flex;flex-direction:column;gap:22px">
      <div style="background:#fff;border-radius:28px;padding:28px 30px"><p style="font-size:26px;color:${GREEN}">${T.cheapest}</p>
        <p class="d" style="font-size:${gbp(d.lo).length > 8 ? 64 : gbp(d.lo).length > 6 ? 76 : 96}px;line-height:1;color:${GREEN};margin-top:6px;white-space:nowrap">${gbp(d.lo)}</p>
        <p style="font-size:30px;color:${INK};margin-top:8px">${T.at} ${esc(d.tienda)}</p></div>
      <div style="padding:0 30px"><p style="font-size:26px;color:${MUTED}">${T.others}</p>
        <p class="d" style="font-size:56px;line-height:1.1;color:${INK}">${T.upto} <span style="text-decoration:line-through;text-decoration-color:#e03131;text-decoration-thickness:6px">${gbp(d.hi)}</span></p>
        <div style="margin-top:22px">${pill(T.save, YELLOW, INK, 34)}</div></div></div></div>
  <p style="font-size:30px;color:${MUTED};text-transform:uppercase;letter-spacing:.06em;margin-top:44px">${esc(d.artist)} · ${esc(plan.fmt)}</p>
  <p class="d" style="font-size:${size(d.title, 58)}px;line-height:1.06;color:${INK};margin-top:8px">${esc(d.title)}</p>
  <div style="flex:1"></div>
  <p style="font-size:26px;color:${MUTED}">${T.footer}</p></div>`;

const story = `<div style="width:1080px;height:1920px;background:${BLUE};color:#fff;padding:120px 80px 110px;display:flex;flex-direction:column;align-items:center;text-align:center">
  ${svg("logo-blanco-sin-lema.svg", "width:360px;height:auto;flex:none")}
  <div style="margin-top:44px">${pill(semana ? T.pill_story_semana : T.pill_story, semana ? YELLOW : "#fff", semana ? INK : BLUE, 38)}</div>
  <img src="${cover}" style="width:640px;height:640px;object-fit:cover;border-radius:32px;margin-top:44px;box-shadow:0 30px 80px rgba(0,0,0,.25)">
  <p style="font-size:30px;text-transform:uppercase;letter-spacing:.06em;opacity:.85;margin-top:36px">${esc(d.artist)} · ${esc(plan.fmt)}</p>
  <p class="d" style="font-size:${size(d.title, 56)}px;line-height:1.06;margin-top:8px">${esc(d.title)}</p>
  <!-- Comparación bien visible (Manuel, 13-11): el más barato frente al precio de las otras tiendas, tachado, y el ahorro -->
  <div style="display:flex;gap:24px;margin-top:36px;width:100%">
    <div style="flex:1.25;background:#fff;border-radius:28px;padding:26px 20px">
      <p style="font-size:30px;color:${GREEN}">${T.cheapest}</p>
      <p class="d" style="font-size:${gbp(d.lo).length > 8 ? 78 : 96}px;line-height:1;color:${GREEN};margin-top:8px;white-space:nowrap">${gbp(d.lo)}</p>
      <p style="font-size:32px;color:${INK};margin-top:8px">${T.at} ${esc(d.tienda)}</p></div>
    <div style="flex:1;background:rgba(0,0,0,.22);border-radius:28px;padding:26px 20px">
      <p style="font-size:30px">${T.others}</p>
      <p style="font-size:30px;margin-top:6px">${T.upto}</p>
      <p class="d" style="font-size:${gbp(d.hi).length > 8 ? 62 : 74}px;line-height:1;margin-top:6px;white-space:nowrap;text-decoration:line-through;text-decoration-color:#ff5a5a;text-decoration-thickness:7px">${gbp(d.hi)}</p></div>
  </div>
  <div style="margin-top:34px">${pill(T.save, YELLOW, INK, 62)}</div>
  <div style="flex:1"></div>
  <p style="font-size:30px;opacity:.9">${T.story_footer}</p></div>`;

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
