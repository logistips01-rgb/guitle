// Vídeo de presentación de guitle para TikTok (1080×1920, 30 fps): escenas en HTML/CSS animadas fotograma a
// fotograma con Playwright. Los fotogramas salen en <dir>/frames/ y ffmpeg los monta en el MP4 (sin audio).
// Uso: node marketing/presentacion-tiktok.js <dir con g0.webp…g7.webp> [--sin-subtitulos]   (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DIR = path.resolve(process.argv[2]);
const FPS = 30, T = 21;
const BLUE = "#2a78d6", INK = "#0b0b0b", YELLOW = "#ffd84d", GREEN = "#1f9d55", RED = "#d64545";
const b64 = f => fs.readFileSync(f).toString("base64");
const svg = (name, style) => fs.readFileSync(path.join(ROOT, "brand", name), "utf8").replace("<svg ", `<svg style="${style}" `);
const font = (w, f) => `@font-face{font-family:Inter;font-weight:${w};src:url(data:font/woff2;base64,${b64(path.join(ROOT, "fonts", f))})}`;
const g = i => `data:image/webp;base64,${b64(path.join(DIR, `g${i}.webp`))}`;

// Escenas [inicio, fin] en segundos; cada una entra y sale con un fundido corto.
const SCENES = [[0, 2.9], [2.9, 7.0], [7.0, 11.6], [11.6, 16.4], [16.4, T]];
const sceneKf = SCENES.map(([s, e], i) => {
  const pc = t => (Math.min(Math.max(t, 0), T) / T * 100).toFixed(3) + "%";
  const fin = i === 0 ? `0%{opacity:1}` : `0%,${pc(s)}{opacity:0}${pc(s + .2)}{opacity:1}`;
  const fout = i === SCENES.length - 1 ? `100%{opacity:1}` : `${pc(e - .15)}{opacity:1}${pc(e)},100%{opacity:0}`;
  return `@keyframes sc${i}{${fin}${fout}}`;
}).join("");
// Animación de un elemento: nombre, duración y segundo en que empieza.
const a = (name, at, dur = .5) => `animation:${name} ${dur}s cubic-bezier(.2,.9,.25,1.15) ${at}s both`;

const CSS = font(600, "inter-semibold.woff2") + font(800, "inter-extrabold.woff2") + sceneKf + `
*{margin:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;font-weight:600;
  background:radial-gradient(120% 80% at 50% 0%,#3b8ae6 0%,${BLUE} 55%,#1f63b8 100%);color:#fff}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;text-align:center;padding:200px 70px 0}
.d{font-weight:800;letter-spacing:-.04em;line-height:1}
.card{background:#fff;color:${INK};border-radius:44px;box-shadow:0 30px 80px rgba(0,0,0,.18)}
@keyframes up{from{opacity:0;transform:translateY(80px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes stamp{from{opacity:0;transform:scale(2.2) rotate(-14deg)}to{opacity:1;transform:rotate(-6deg)}}
@keyframes left{from{opacity:0;transform:translateX(-140px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(500px)}to{opacity:1;transform:none}}
@keyframes hl{from{background:#fff;color:${INK}}to{background:${GREEN};color:#fff}}
@keyframes hlr{from{background:#fff;color:${INK}}to{background:#fde8e8;color:${RED}}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}
@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-60px)}}
`;

const row = (store, price, i, at, cls = "") =>
  `<div style="display:flex;justify-content:space-between;align-items:center;padding:22px 30px;border-radius:22px;font-size:40px;${a("left", at, .45)}${cls}">
    <span>${store}</span><span class="d" style="font-size:44px;letter-spacing:-.02em">${price}</span></div>`;
const icon = (paths, color) => `<svg viewBox="0 0 24 24" width="96" height="96" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
const item = (ic, title, sub, at) => `<div class="card" style="display:flex;align-items:center;gap:34px;padding:38px 46px;width:100%;text-align:left;${a("left", at, .5)}">
  ${ic}<div><p class="d" style="font-size:64px;letter-spacing:-.03em">${title}</p><p style="font-size:32px;color:#52514e;margin-top:8px">${sub}</p></div></div>`;

// Subtítulos (sin voz): franja fija por encima de la zona que tapan los textos y botones de TikTok.
const SUBS = process.argv[3] !== "--sin-subtitulos";
const SUBTITLES = [
  [.3, 2.85, "¿Vas a comprarte una guitarra? ¡Espera!"],
  [3.1, 6.9, "La misma guitarra puede costar casi 100 € más según la tienda"],
  [7.2, 11.5, "Somos guitle: comparamos cada día 11.000 guitarras en 14 tiendas"],
  [11.8, 16.3, "Chollos de verdad, tops por precio y los descuentos falsos que debes evitar"],
  [16.6, T, "Síguenos y no vuelvas a pagar de más"],
];
let subCss = "";
const subKf = (s, e) => {
  const name = "sub" + Math.round(s * 10), pc = t => (Math.min(t, T) / T * 100).toFixed(3) + "%";
  subCss += `@keyframes ${name}{0%,${pc(s)}{opacity:0;transform:translateY(20px)}${pc(s + .2)}{opacity:1;transform:none}` +
    (e >= T ? `100%{opacity:1}}` : `${pc(e - .15)}{opacity:1}${pc(e)},100%{opacity:0}}`);
  return name;
};
SUBTITLES.forEach(([s, e]) => subKf(s, e));
const HTML = `<style>${CSS}${subCss}
.sub{position:absolute;left:90px;right:90px;top:1330px;text-align:center}
.sub span{display:inline-block;background:rgba(0,0,0,.62);color:#fff;font-weight:800;font-size:50px;line-height:1.25;padding:18px 30px;border-radius:22px;letter-spacing:-.01em;text-wrap:balance}</style>
<!-- 1. Gancho -->
<div class="sc" style="animation:sc0 ${T}s linear both">
  <p class="d" style="font-size:140px;margin-top:0;${a("up", .1, .55)}">¿Vas a<br>comprarte una guitarra?</p>
  <div class="card" style="width:100%;height:560px;margin-top:70px;display:flex;justify-content:space-evenly;align-items:center;padding:0 20px;${a("rise", .35, .8)}">
    ${[1, 2, 0, 3, 4].map(i => `<img src="${g(i)}" style="height:500px;width:180px;object-fit:contain">`).join("")}</div>
  <div class="d" style="position:absolute;top:760px;background:${YELLOW};color:${INK};font-size:130px;padding:26px 64px;border-radius:30px;${a("stamp", 1.75, .35)}">¡Espera!</div>
</div>
<!-- 2. Misma guitarra, distinto precio (tiendas anónimas) -->
<div class="sc" style="animation:sc1 ${T}s linear both">
  <p class="d" style="font-size:104px;${a("up", 3.0)}">La misma guitarra,<br><span style="color:${YELLOW}">distinto precio</span></p>
  <div class="card" style="width:100%;margin-top:50px;padding:36px 40px 70px;display:flex;gap:30px;align-items:center;${a("up", 3.2)}">
    <img src="${g(0)}" style="height:600px;width:220px;object-fit:contain">
    <div style="flex:1;display:flex;flex-direction:column;gap:6px">
      ${row("Tienda A", "721 €", 0, 3.6, `;animation:left .45s ease 3.6s both,hl .3s ease 5.3s forwards`)}
      ${row("Tienda B", "758 €", 1, 3.8)}${row("Tienda C", "769 €", 2, 4.0)}${row("Tienda D", "777 €", 3, 4.2)}
      ${row("Tienda E", "799 €", 4, 4.4)}
      ${row("Tienda F", "811 €", 5, 4.6, `;animation:left .45s ease 4.6s both,hlr .3s ease 5.3s forwards`)}</div></div>
  <div class="d" style="margin-top:-46px;background:${YELLOW};color:${INK};font-size:84px;padding:24px 50px;border-radius:28px;${a("pop", 5.5, .4)}">90 € de diferencia</div>
</div>
<!-- 3. Somos guitle -->
<div class="sc" style="animation:sc2 ${T}s linear both;justify-content:center;padding:0 70px 620px">
  <div style="${a("pop", 7.15, .6)}">${svg("logo-blanco.svg", "width:820px;height:auto")}</div>
  <div style="display:flex;gap:26px;margin-top:110px;width:100%">
    <div class="card" style="flex:1.4;padding:44px 20px;${a("up", 8.6)}"><p class="d" id="count" style="font-size:100px;color:${BLUE}">0</p><p style="font-size:36px;margin-top:10px">guitarras</p></div>
    <div class="card" style="flex:1;padding:44px 20px;${a("up", 9.4)}"><p class="d" style="font-size:100px;color:${BLUE}">14</p><p style="font-size:36px;margin-top:10px">tiendas</p></div></div>
  <p class="d" style="font-size:80px;margin-top:60px;${a("up", 10.2)}">cada día</p>
</div>
<!-- 4. Qué vas a ver aquí -->
<div class="sc" style="animation:sc3 ${T}s linear both;justify-content:center;padding:0 70px 620px">
  <p class="d" style="font-size:118px;${a("up", 11.7)}">Aquí vas a ver</p>
  <div style="display:flex;flex-direction:column;gap:34px;margin-top:60px;width:100%">
    ${item(icon(`<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5" fill="${BLUE}"/>`, BLUE), "Chollos de verdad", "Rebajas comprobadas con el histórico", 12.3)}
    ${item(icon(`<path d="M6 20V10M12 20V4M18 20v-7"/>`, BLUE), "Tops por precio", "Las mejores por menos de 300, 700, 1.200 €…", 13.4)}
    ${item(icon(`<path d="M12 3 2 20h20z"/><path d="M12 10v4"/><circle cx="12" cy="17" r=".8" fill="${RED}"/>`, RED), "Descuentos falsos", "Los que suben el precio para «rebajarlo»", 14.4)}</div>
</div>
<!-- 5. Síguenos -->
<div class="sc" style="animation:sc4 ${T}s linear both;justify-content:center;padding:0 70px 620px">
  <div style="${a("pop", 16.5, .5)}">${svg("icono-blanco.svg", "width:300px;height:300px")}</div>
  <p class="d" style="font-size:150px;margin-top:60px;${a("up", 16.8)}">Síguenos</p>
  <p style="font-size:52px;margin-top:26px;${a("up", 17.2)}">y no vuelvas a pagar de más</p>
  <div class="d" style="margin-top:70px;background:#fff;color:${BLUE};font-size:80px;padding:28px 70px;border-radius:999px;${a("pop", 18.6, .45)};animation:pop .45s ease 18.6s both,pulse 1s ease-in-out 19.2s 2">guitle.com</div>
</div>
${SUBS ? SUBTITLES.map(([s, e, t]) => `<div class="sub" style="animation:${subKf(s, e)} ${T}s linear both"><span>${t}</span></div>`).join("") : ""}`;

(async () => {
  const out = path.join(DIR, "frames");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.setContent(HTML);
  await page.evaluate(() => document.fonts.ready);
  for (let f = 0; f < T * FPS; f++) {
    const t = f / FPS;
    await page.evaluate(t => {
      for (const an of document.getAnimations()) { an.pause(); an.currentTime = t * 1000; }
      // Contador de guitarras: de 0 a 11.000 entre 8,7 s y 10,0 s
      const k = Math.min(1, Math.max(0, (t - 8.7) / 1.3)), e = 1 - Math.pow(1 - k, 3);
      document.getElementById("count").textContent = (Math.round(e * 11000 / 10) * 10).toLocaleString("es-ES", { useGrouping: "always" });
    }, t);
    await page.screenshot({ path: path.join(out, `f${String(f).padStart(4, "0")}.jpg`), type: "jpeg", quality: 92 });
  }
  await browser.close();
  console.log(`${T * FPS} fotogramas en ${out}`);
})();
