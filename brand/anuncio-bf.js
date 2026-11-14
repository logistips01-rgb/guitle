// Anuncio de pago de Black Friday (Meta, España): «¿Ese descuento de Black Friday es de verdad?» con 3 ejemplos reales
// (mínimo histórico, bajada real y descuento inflado) de guitle.com/black-friday.html. Sin nombres ni logos de tiendas.
// Lee <carpeta>/anuncio.json y deja feed.jpg (1080×1350), story.jpg y escena-*.jpg (1080×1920) para el vídeo.
// Uso: node brand/anuncio-bf.js <carpeta>   (desde la raíz del repo)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = process.cwd();
const DIR = path.resolve(process.argv[2]);
const A = JSON.parse(fs.readFileSync(path.join(DIR, "anuncio.json"), "utf8"));
const BLUE = "#2a78d6", INK = "#0b0b0b", MUTED = "#52514e", GREEN = "#1f9d55", RED = "#e03131", YELLOW = "#ffd84d";
const b64 = f => fs.readFileSync(f).toString("base64");
const svg = (name, style) => fs.readFileSync(path.join(ROOT, "brand", name), "utf8").replace("<svg ", `<svg style="${style}" `);
const font = (w, f) => `@font-face{font-family:Inter;font-weight:${w};src:url(data:font/woff2;base64,${b64(path.join(ROOT, "fonts", f))})}`;
const CSS = font(600, "inter-semibold.woff2") + font(800, "inter-extrabold.woff2") +
  `*{margin:0;box-sizing:border-box} p{text-wrap:balance} body{font-family:Inter,sans-serif;font-weight:600;color:#fff}
   .d{font-weight:800;letter-spacing:-.035em} s{text-decoration-color:${RED};text-decoration-thickness:5px}`;
const eur = v => v.toLocaleString("es-ES", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 }) + " €";
const foto = g => `data:image/webp;base64,${b64(path.join(DIR, g.foto))}`;
const pill = (t, bg, fg, fs) => `<span class="d" style="background:${bg};color:${fg};font-size:${fs}px;padding:12px 28px;border-radius:999px;letter-spacing:-.01em;white-space:nowrap">${t}</span>`;
const TIPOS = {
  minimo: { label: "✅ Mínimo histórico", bg: GREEN, fg: "#fff" },
  bajada: { label: "📉 Bajada real", bg: "#fff", fg: BLUE },
  inflado: { label: "⚠️ Descuento inflado", bg: RED, fg: "#fff" },
};
// Texto de cada ejemplo con sus cifras reales
const linea = g => g.tipo === "inflado"
  ? `Una tienda la subió de ${eur(g.antes)} a <s>${eur(g.subida)}</s> y ahora la «rebaja» a ${eur(g.ahora)}`
  : g.tipo === "minimo" ? `Su precio más bajo desde que la seguimos (media: ${eur(g.media)})`
  : `${Math.round(-g.vs_media)} % por debajo de su precio medio (${eur(g.media)})`;
const precio = g => g.tipo === "inflado" ? eur(g.ahora) : eur(g.precio);

// Tamaños: «feed» (3 en fila en 1080×1350), «story» (3 en fila en 1080×1920) y «big» (una sola, escenas del vídeo)
const Z = { feed: { pad: "22px 16px", pill: 23, img: 360, nom: 25, pre: 52, txt: 20, gap: 14 },
            story: { pad: "28px 16px", pill: 24, img: 540, nom: 30, pre: 64, txt: 23, gap: 18 },
            big: { pad: "34px 30px", pill: 40, img: 760, nom: 46, pre: 110, txt: 36, gap: 24 } };
const card = (g, size) => {
  const t = TIPOS[g.tipo], z = Z[size];
  return `<div style="background:rgba(255,255,255,.12);border-radius:30px;padding:${z.pad};display:flex;flex-direction:column;align-items:center;text-align:center;${size === "big" ? "" : "flex:1"}">
    ${pill(t.label, t.bg, t.fg, z.pill)}
    <div style="background:#fff;border-radius:24px;width:100%;height:${z.img}px;margin-top:${z.gap}px;display:flex;align-items:center;justify-content:center;padding:18px">
      <img src="${foto(g)}" style="max-height:100%;max-width:100%;object-fit:contain"></div>
    <p class="d" style="font-size:${z.nom}px;line-height:1.08;margin-top:${z.gap}px">${g.nombre}</p>
    <p class="d" style="font-size:${z.pre}px;line-height:1;margin-top:${z.gap / 2}px;color:${g.tipo === "inflado" ? "#ffb3b3" : YELLOW}">${precio(g)}</p>
    <p style="font-size:${z.txt}px;line-height:1.25;margin-top:${z.gap / 2}px;opacity:.95">${linea(g)}</p></div>`;
};
const head = (fs, mt) => `<p class="d" style="font-size:${fs}px;line-height:1.02;margin-top:${mt}px;text-align:center">¿Ese descuento de<br>Black Friday es de verdad?</p>`;
const pie = fs => `<p style="font-size:${fs}px;line-height:1.3;text-align:center;opacity:.95">${A.cifra}.<br><b class="d">Compara antes de comprar · guitle.com/black-friday</b></p>`;
const marco = (w, h, inner, pad = "70px 56px 64px") => `<div style="width:${w}px;height:${h}px;background:${BLUE};padding:${pad};display:flex;flex-direction:column;align-items:center">${inner}</div>`;

const feed = marco(1080, 1350, `${svg("logo-blanco-sin-lema.svg", "width:250px;height:auto;flex:none")}
  <div style="margin-top:26px">${pill("🖤 Black Friday", YELLOW, INK, 30)}</div>
  ${head(66, 24)}
  <div style="display:flex;gap:18px;width:100%;margin-top:34px">${A.guitarras.map(g => card(g, "feed")).join("")}</div>
  <div style="flex:1"></div>${pie(27)}`, "56px 50px 50px");
const story = marco(1080, 1920, `${svg("logo-blanco-sin-lema.svg", "width:320px;height:auto;flex:none")}
  <div style="margin-top:34px">${pill("🖤 Black Friday", YELLOW, INK, 38)}</div>
  ${head(84, 34)}
  <div style="display:flex;gap:18px;width:100%;margin-top:60px">${A.guitarras.map(g => card(g, "story")).join("")}</div>
  <div style="flex:1"></div>${pie(36)}`, "130px 56px 150px");
// Escenas del vídeo (1080×1920): portada con las 3 guitarras, una por ejemplo y el cierre
const escenas = [story,
  ...A.guitarras.map((g, i) => marco(1080, 1920, `${svg("logo-blanco-sin-lema.svg", "width:260px;height:auto;flex:none")}
    <p class="d" style="font-size:44px;margin-top:40px;opacity:.9">${i + 1} / ${A.guitarras.length}</p>
    <div style="flex:1"></div><div style="width:100%">${card(g, "big")}</div><div style="flex:1"></div>`, "130px 70px 150px")),
  marco(1080, 1920, `${svg("logo-blanco-sin-lema.svg", "width:420px;height:auto;flex:none")}
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:40px">
      <p class="d" style="font-size:92px;line-height:1.04">Que no te la cuelen<br>este Black Friday</p>
      <p style="font-size:44px;line-height:1.3">El histórico de precios de cada guitarra:<br>mínimos, bajadas reales y descuentos inflados.</p>
      ${pill(A.cifra_corta, YELLOW, INK, 40)}</div>
    <p class="d" style="font-size:54px">guitle.com/black-friday</p>`, "160px 70px 170px")];

(async () => {
  const browser = await chromium.launch();
  const shots = [["feed.jpg", 1080, 1350, feed], ...escenas.map((h, i) => [i ? `escena-${i}.jpg` : "story.jpg", 1080, 1920, h])];
  for (const [out, w, h, html] of shots) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>${html}</body></html>`);
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.join(DIR, out), type: "jpeg", quality: 92 });
    await page.close();
  }
  await browser.close();
  console.log(`feed.jpg, story.jpg y ${escenas.length - 1} escenas en ${path.relative(ROOT, DIR)}/`);
})();
