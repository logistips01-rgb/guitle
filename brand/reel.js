// Reel del día (1080×1920, 30 fps, sin voz) a partir de social/<fecha>/plan.json: el chollo o el top 5 animados.
// Escenas en HTML/CSS que se capturan fotograma a fotograma con Playwright; ffmpeg las monta en reel.mp4.
// Sirve para Instagram Reels y para subirlo a TikTok. Uso: node brand/reel.js social/<fecha>   (desde la raíz del repo)
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = process.cwd();
const DIR = path.resolve(process.argv[2]);
const plan = JSON.parse(fs.readFileSync(path.join(DIR, "plan.json"), "utf8"));
const FPS = 30;
const BLUE = "#2a78d6", INK = "#0b0b0b", MUTED = "#52514e", YELLOW = "#ffd84d", GREEN = "#1f9d55", RED = "#d64545";
const b64 = f => fs.readFileSync(f).toString("base64");
const svg = (name, style) => fs.readFileSync(path.join(ROOT, "brand", name), "utf8").replace("<svg ", `<svg style="${style}" `);
const font = (w, f) => `@font-face{font-family:Inter;font-weight:${w};src:url(data:font/woff2;base64,${b64(path.join(ROOT, "fonts", f))})}`;
const img = p => `data:image/webp;base64,${b64(path.join(DIR, p.photo))}`;
const eur = v => v.toLocaleString("es-ES", { useGrouping: "always", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €";
const esc = s => String(s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const model = p => esc(p.brand && p.name.startsWith(p.brand + " ") ? p.name.slice(p.brand.length + 1) : p.name);
const a = (name, at, dur = .5) => `animation:${name} ${dur}s cubic-bezier(.2,.9,.25,1.15) ${at}s both`;

// Escenas: [duración, (inicio) => html]. Cada una entra y sale con un fundido corto.
const scenes = [];
const hook = (t0, label) => `<div class="d" style="background:${YELLOW};color:${INK};font-size:64px;padding:18px 44px;border-radius:999px;${a("pop", t0 + .05, .4)}">${label}</div>`;
const photoCard = (p, t0, h) => `<div class="card" style="width:100%;height:${h}px;margin-top:50px;display:flex;align-items:center;justify-content:center;padding:40px;${a("rise", t0 + .1, .7)}">
  <img src="${img(p)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>`;
const nameBlock = (p, t0) => `<p style="font-size:38px;text-transform:uppercase;letter-spacing:.06em;margin-top:44px;opacity:.85;${a("up", t0)}">${esc(p.brand)}</p>
  <p class="d" style="font-size:${model(p).length > 34 ? 70 : 84}px;margin-top:10px;text-wrap:balance;${a("up", t0 + .1)}">${model(p)}</p>`;
const cta = t0 => `<div style="${a("pop", t0 + .1, .5)}">${svg("logo-blanco.svg", "width:700px;height:auto")}</div>
  <p class="d" style="font-size:84px;margin-top:90px;text-wrap:balance;${a("up", t0 + .5)}">Compara antes de comprar</p>
  <div class="d" style="margin-top:60px;background:#fff;color:${BLUE};font-size:76px;padding:26px 66px;border-radius:999px;animation:pop .45s ease ${t0 + 1}s both,pulse 1s ease-in-out ${t0 + 1.5}s 2">guitle.com</div>
  <p style="font-size:44px;margin-top:50px;${a("up", t0 + 1.2)}">Síguenos para más chollos</p>`;

const post = plan.post;
if (post.type === "chollo") {
  const p = post.deal;
  scenes.push([2.8, t => `${hook(t, "Chollo del día")}${photoCard(p, t, 900)}${nameBlock(p, t + .5)}`]);
  // Precio en otras tiendas frente al mejor
  const bar = (label, v, w, color, at, strong) => `<div style="${a("left", at, .5)}">
    <div style="display:flex;justify-content:space-between;font-size:42px;margin-bottom:12px"><span>${label}</span><span class="d" style="font-size:52px;letter-spacing:-.02em">${eur(v)}</span></div>
    <div style="height:56px;border-radius:16px;background:rgba(255,255,255,.18)"><div style="height:100%;width:${w}%;border-radius:16px;background:${color};${strong ? "box-shadow:0 0 0 6px rgba(255,255,255,.35)" : ""}"></div></div></div>`;
  const max = Math.max(p.max, p.median, p.price);
  scenes.push([4.2, t => `<p class="d" style="font-size:110px;${a("up", t + .05)}">¿Dónde está<br>más barata?</p>
    <div style="width:100%;display:flex;flex-direction:column;gap:56px;margin-top:110px;text-align:left">
      ${bar("La más cara", p.max, p.max / max * 100, RED, t + .5)}
      ${bar("Precio habitual", p.median, p.median / max * 100, "rgba(255,255,255,.75)", t + 1.0)}
      ${bar(`En ${esc(p.store)}`, p.price, p.price / max * 100, GREEN, t + 1.6, true)}</div>
    <p style="font-size:38px;margin-top:80px;opacity:.9;${a("up", t + 2.2)}">Comparada en ${p.stores} tiendas · ${plan.fecha}</p>`]);
  scenes.push([3.4, t => `<div class="card" style="width:640px;height:820px;display:flex;align-items:center;justify-content:center;padding:40px;${a("pop", t + .05, .5)}">
      <img src="${img(p)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>
    <p class="d" style="font-size:190px;margin-top:70px;${a("pop", t + .35, .45)}">${eur(p.price)}</p>
    <p style="font-size:50px;margin-top:20px;${a("up", t + .6)}">en ${esc(p.store)}</p>
    <div class="d" style="margin-top:50px;background:${YELLOW};color:${INK};font-size:46px;padding:20px 36px;border-radius:24px;text-wrap:balance;letter-spacing:-.02em;${a("pop", t + 1.0, .4)}">${esc(p.why)}</div>`]);
} else if (post.type === "bf") {
  // Cuenta atrás para el Black Friday: el precio de hoy de una guitarra popular, para comprobar luego si la rebaja es real
  const p = post.deal;
  scenes.push([2.6, t => `${hook(t, "Black Friday")}
    <p class="d" style="font-size:170px;margin-top:330px;${a("up", t + .2)}">Faltan</p>
    <p class="d" style="font-size:420px;color:${YELLOW};margin-top:10px;${a("pop", t + .45, .5)}">${post.days}</p>
    <p class="d" style="font-size:150px;margin-top:10px;${a("up", t + .7)}">${post.days === 1 ? "día" : "días"}</p>`]);
  scenes.push([2.8, t => `<p class="d" style="font-size:96px;text-wrap:balance;${a("up", t + .05)}">Apunta este precio</p>
    ${photoCard(p, t + .2, 840)}${nameBlock(p, t + .6)}`]);
  scenes.push([3.4, t => `<p style="font-size:50px;opacity:.85;margin-top:300px;${a("up", t + .05)}">Hoy, ${plan.fecha}</p>
    <p class="d" style="font-size:200px;margin-top:30px;${a("pop", t + .25, .45)}">${eur(p.price)}</p>
    <p style="font-size:50px;margin-top:20px;${a("up", t + .5)}">en ${esc(p.store)}</p>
    <div class="card" style="margin-top:90px;padding:40px 50px;font-size:46px;text-wrap:balance;${a("up", t + .9)}">En las otras ${p.stores - 1} tiendas: <b class="d" style="letter-spacing:-.02em">de ${eur(p.next)} a ${eur(p.max)}</b></div>`]);
  scenes.push([3.0, t => `<p class="d" style="font-size:124px;margin-top:400px;text-wrap:balance;${a("up", t + .05)}">¿Bajará de verdad en Black Friday?</p>
    <p style="font-size:54px;margin-top:70px;text-wrap:balance;${a("up", t + .5)}">El 27 de noviembre te lo decimos, con su histórico de precios.</p>
    <div class="d" style="margin-top:80px;background:${YELLOW};color:${INK};font-size:58px;padding:22px 44px;border-radius:999px;${a("pop", t + 1.0, .4)}">Guárdalo 📌</div>`]);
} else if (post.type === "guitle") {
  // Sobre guitle: diapositivas de texto con un elemento visual (fila de guitarras, precios, gráfica…)
  const visual = (v, t) => {
    if (!v) return "";
    if (v.type === "guitars") return `<div class="card" style="width:100%;height:640px;margin-top:80px;display:flex;justify-content:space-evenly;align-items:center;padding:30px 20px;${a("rise", t + .4, .7)}">
      ${v.photos.map(f => `<img src="data:image/webp;base64,${b64(path.join(DIR, f))}" style="height:100%;max-width:${Math.floor(900 / v.photos.length)}px;object-fit:contain">`).join("")}</div>`;
    if (v.type === "prices") return `<div class="card" style="width:100%;margin-top:70px;padding:30px 40px;text-align:left;${a("up", t + .4)}">
      ${v.rows.map((r, i) => `<div style="display:flex;justify-content:space-between;padding:18px 24px;border-radius:18px;font-size:42px;
        ${i === 0 ? `background:${GREEN};color:#fff` : i === v.rows.length - 1 ? `background:#fde8e8;color:${RED}` : ""}"><span>${esc(r[0])}</span><b class="d" style="letter-spacing:-.02em">${eur(r[1])}</b></div>`).join("")}</div>`;
    if (v.type === "chart") {
      const pts = v.points, max = Math.max(...pts), min = Math.min(...pts), X = i => 40 + i * 820 / (pts.length - 1), Y = q => 380 - (q - min) / (max - min || 1) * 300;
      return `<div class="card" style="width:100%;margin-top:70px;padding:30px;${a("up", t + .4)}"><svg viewBox="0 0 900 440" width="100%">
        <polyline fill="none" stroke="${BLUE}" stroke-width="10" stroke-linejoin="round" points="${pts.map((q, i) => `${X(i)},${Y(q)}`).join(" ")}"/>
        ${v.marks.map(([i, txt, color]) => `<circle cx="${X(i)}" cy="${Y(pts[i])}" r="16" fill="${color}"/><text x="${Math.min(X(i), 760)}" y="${Y(pts[i]) - 30}" font-size="38" font-weight="800" fill="${color}" text-anchor="middle">${txt}</text>`).join("")}
      </svg></div>`;
    }
    if (v.type === "chips") return `<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:18px;margin-top:70px;${a("up", t + .4)}">
      ${v.items.map(x => `<span class="d" style="background:#fff;color:${INK};font-size:42px;padding:18px 30px;border-radius:999px;letter-spacing:-.02em">${esc(x)}</span>`).join("")}</div>`;
    return "";
  };
  post.slides.forEach(sl => scenes.push([sl.dur || 3.2, t => `${sl.hook ? hook(t, esc(sl.hook)) : ""}
    <p class="d" style="font-size:${sl.size || 112}px;margin-top:${sl.visual ? (sl.hook ? 70 : 120) : 420}px;text-wrap:balance;${a("up", t + .1)}">${esc(sl.title)}</p>
    ${sl.sub ? `<p style="font-size:50px;margin-top:44px;text-wrap:balance;opacity:.92;${a("up", t + .3)}">${esc(sl.sub)}</p>` : ""}
    ${visual(sl.visual, t)}`]));
} else {
  const n = post.picks.length;
  scenes.push([2.8, t => `${hook(t, post.hook || "Top " + n)}
    <p class="d" style="font-size:128px;margin-top:60px;text-wrap:balance;${a("up", t + .2)}">${esc(post.title[0].toUpperCase() + post.title.slice(1))}</p>
    <div class="card" style="width:100%;height:760px;margin-top:70px;display:flex;justify-content:space-evenly;align-items:center;padding:30px 20px;${a("rise", t + .4, .7)}">
      ${post.picks.map(p => `<img src="${img(p)}" style="height:100%;max-width:${Math.floor(900 / n)}px;object-fit:contain">`).join("")}</div>`]);
  post.picks.forEach((p, i) => scenes.push([p.why ? 2.8 : 2.3, t => `<div style="display:flex;width:100%;justify-content:space-between;align-items:center">
      <span class="d" style="font-size:${p.label ? 96 : 150}px;color:${YELLOW};${a("pop", t + .05, .4)}">${p.label ? esc(p.label) : "#" + (i + 1)}</span>
      <span style="font-size:36px;opacity:.85">${i + 1} / ${n}</span></div>
    ${photoCard(p, t, 820)}${nameBlock(p, t + .3)}
    <p class="d" style="font-size:120px;margin-top:26px;${a("pop", t + .55, .4)}">${eur(p.price)}</p>
    <p style="font-size:42px;margin-top:10px;${a("up", t + .7)}">en ${esc(p.store)} · ${p.stores} tiendas</p>
    ${p.why ? `<div class="d" style="margin-top:30px;background:${YELLOW};color:${INK};font-size:40px;padding:16px 30px;border-radius:20px;letter-spacing:-.02em;${a("pop", t + .9, .4)}">${esc(p.why)}</div>` : ""}`]));
}
scenes.push([3.0, t => cta(t)]);

let t = 0;
const timed = scenes.map(([d, html]) => { const s = t; t += d; return [s, t, html(s)]; });
const T = t;
const pc = x => (Math.min(Math.max(x, 0), T) / T * 100).toFixed(3) + "%";
const kf = timed.map(([s, e], i) => `@keyframes sc${i}{${i ? `0%,${pc(s)}{opacity:0}${pc(s + .2)}{opacity:1}` : "0%{opacity:1}"}` +
  `${i === timed.length - 1 ? "100%{opacity:1}" : `${pc(e - .15)}{opacity:1}${pc(e)},100%{opacity:0}`}}`).join("");
const HTML = `<style>${font(600, "inter-semibold.woff2")}${font(800, "inter-extrabold.woff2")}${kf}
*{margin:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;font-family:Inter,sans-serif;font-weight:600;
  background:${post.type === "bf" ? "radial-gradient(120% 80% at 50% 0%,#2a2a2a 0%,#0b0b0b 70%)" : `radial-gradient(120% 80% at 50% 0%,#3b8ae6 0%,${BLUE} 55%,#1f63b8 100%)`};color:#fff}
.sc{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;text-align:center;padding:170px 70px 0}
.d{font-weight:800;letter-spacing:-.04em;line-height:1}
.card{background:#fff;color:${INK};border-radius:44px;box-shadow:0 30px 80px rgba(0,0,0,.18)}
@keyframes up{from{opacity:0;transform:translateY(70px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}
@keyframes left{from{opacity:0;transform:translateX(-140px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(400px)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}
</style>${timed.map(([, , html], i) => `<div class="sc" style="animation:sc${i} ${T}s linear both${i === timed.length - 1 ? ";justify-content:center;padding:0 70px 300px" : ""}">${html}</div>`).join("")}`;

(async () => {
  const frames = fs.mkdtempSync(path.join(os.tmpdir(), "reel-"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.setContent(HTML);
  await page.evaluate(() => document.fonts.ready);
  const total = Math.round(T * FPS);
  for (let f = 0; f < total; f++) {
    await page.evaluate(ms => { for (const an of document.getAnimations()) { an.pause(); an.currentTime = ms; } }, f / FPS * 1000);
    await page.screenshot({ path: path.join(frames, `f${String(f).padStart(4, "0")}.jpg`), type: "jpeg", quality: 90 });
  }
  await browser.close();
  // Pista de audio muda: Instagram la exige en los Reels.
  execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(frames, "f%04d.jpg"),
    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-c:v", "libx264", "-preset", "slow", "-crf", "24",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "64k", "-shortest", path.join(DIR, "reel.mp4")]);
  fs.rmSync(frames, { recursive: true, force: true });
  console.log(`reel.mp4 (${T.toFixed(1)} s) en ${path.relative(ROOT, DIR)}/`);
})();
