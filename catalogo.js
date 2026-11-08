// Catálogo de guitarras: búsqueda, filtros y ficha con tiendas e histórico (catalogo.html, acusticas.html, clasicas.html).
// Solo miniaturas propias (img/p/): la web no carga nada de terceros. Sin miniatura todavía, sin foto.
// Otros países (guitle.com/pt/…): textos en window.GUITLE_T y el idioma en <html lang>; sin ellos, en español.
const T = Object.assign({
  loadErr: "No se pudo cargar el catálogo.", allBrands: "Todas las marcas", all: "Todas", low: "Mínimo", save: "Ahorra {v}",
  lh: "zurda", store: "tienda", stores: "tiendas", empty: "No hay {many} con esos filtros.", more: "Ver más ({n} restantes)",
  meta: "{a} de {b} {many} · {m} comparables en varias tiendas · actualizado {d}", best: "mejor precio", inStock: "en stock",
  noStock: "sin stock", goLong: "Ir a la tienda", goShort: "Ir", close: "Cerrar", inAt: "en {s}",
  saveMax: " · hasta {v} menos que en la más cara", atLow: "En su mínimo registrado", lowTag: "Mínimo registrado: {v}",
  storesH: "Tiendas", evolH: "Evolución del precio", histErr: "No se pudo cargar el histórico.",
  histSoon: "El histórico se irá completando con las próximas lecturas.", types: {},
}, window.GUITLE_T || {});
const tf = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const LOCALE = document.documentElement.lang === "es" ? "es-ES" : document.documentElement.lang;
const typeName = t => T.types[t] || t;
const pic = p => p.th ? (document.body.dataset.img || "img/p/") + p.th : null;
const eur = v => v == null ? "–" : v.toLocaleString(LOCALE, { style: "currency", currency: document.body.dataset.cur || "EUR", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const norm = s => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
const fmtDay = d => d ? new Date(d + "T12:00:00").toLocaleDateString(LOCALE, { day: "numeric", month: "short" }) : "";
// Sinónimos habituales en las búsquedas
const ALIASES = { tele: "telecaster", strat: "stratocaster", lp: "les paul", negra: "black", blanca: "white", roja: "red", azul: "blue" };
const PAGE = 48;
// Sin foto todavía (o solo un primer plano): silueta de guitarra en gris, para no romper la cuadrícula.
const NOPHOTO = '<svg class="nophoto" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3l-6.5 6.5"/><path d="M19.5 1.5l3 3-1.5 1.5-3-3z"/><path d="M14.5 9.5c-1.6-1.6-3.9-1.3-5 .2-1 .4-2.6.1-4 1.5-2.1 2.1-1.7 5.4.6 7.7s5.6 2.7 7.7.6c1.4-1.4 1.1-3 1.5-4 1.5-1.1 1.8-3.4.2-5z"/><circle cx="9.6" cy="14.4" r="1.4"/></svg>';
// Cada página dice qué catálogo carga: <body data-src="…json" data-history="…json" data-kind="electrica|acustica|clasica">
const CFG = document.body.dataset;
const TYPE_ORDERS = {
  electrica: ["ST", "T", "Single cut", "Double cut", "Semihueca", "Offset / Retro", "Moderna / Metal", "Otras"],
  acustica: ["Dreadnought", "Auditorio / Concierto", "Jumbo", "Parlor", "12 cuerdas", "Tamaño reducido", "Roundback", "Otras"],
  clasica: ["Clásica", "Flamenca", "Electroclásica", "Tamaño reducido", "Otras"],
  teclado: ["Piano digital", "Teclado portátil", "Piano de escenario", "Sintetizador", "Controlador MIDI", "Piano acústico", "Otras"],
  pedal: ["Overdrive y distorsión", "Delay", "Reverb", "Modulación", "Compresor", "Wah y volumen", "Octavador y pitch",
          "Ecualizador", "Puerta de ruido", "Sintetizador", "Looper", "Afinador", "Multiefectos", "Para bajo", "Otras"],
  bajo: ["4 cuerdas", "5 cuerdas", "6 cuerdas o más", "Escala corta", "Fretless", "Acústico", "Otras"],
  ampli: ["Combo", "Cabezal", "Pantalla", "Para bajo", "Para acústica", "De auriculares y portátil", "Otras"],
  estuche: ["Para eléctrica", "Para acústica", "Para clásica", "Para bajo", "Otras"],
  micro: ["Dinámico", "Condensador", "Inalámbrico", "Para instrumento", "USB", "De cinta", "Otras"],
  pack: ["Eléctrica", "Acústica", "Clásica", "Otras"],
  varios: ["Cuerdas", "Púas", "Correas", "Cables", "Afinadores", "Cejillas", "Soportes", "Pastillas", "Recambios", "Mantenimiento", "Otras"],
};
// Cómo se llama lo que hay en cada catálogo (recuento y mensajes).
const MANY = T.many || { pack: "packs", teclado: "teclados", pedal: "pedales", bajo: "bajos", ampli: "amplis", estuche: "fundas y estuches", micro: "micrófonos", varios: "accesorios" }[CFG.kind] || "guitarras";
const TYPE_ORDER = TYPE_ORDERS[CFG.kind] || TYPE_ORDERS.electrica;

async function load1(path) {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}
// Una lista puede venir de varios ficheros ("a.json,b.json": los packs de España): se juntan productos, tiendas e histórico.
async function load(paths) {
  const parts = await Promise.all(paths.split(",").map(p => load1(p).catch(e => null)));
  const ok = parts.filter(Boolean);
  if (!ok.length) throw new Error(`${paths}: sin datos`);
  if (ok.length === 1) return ok[0];
  if (ok[0].products) return { ...ok[0], stores: Object.assign({}, ...ok.map(d => d.stores)), products: ok.flatMap(d => d.products) };
  return Object.assign({}, ...ok);
}

const params = new URLSearchParams(location.search);
const state = { q: params.get("q") || "", type: params.get("type") || "", brand: params.get("brand") || "",
                range: params.get("range") || "", show: params.get("show") || "", sort: params.get("sort") || "stores", shown: PAGE };
let catalog, storeName, storeColor, priceHistory = null, chart = null;

load(CFG.src).then(data => {
  catalog = data;
  storeName = data.stores;
  const palette = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"];
  storeColor = Object.fromEntries(Object.keys(storeName).map((s, i) => [s, palette[i % palette.length]]));
  for (const p of data.products) {
    const prices = p.items.map(i => i.p);
    p.best = p.items[0];
    p.max = Math.max(...prices);
    p.save = p.max - p.best.p;
    p.nStores = new Set(p.items.map(i => i.s)).size;
    p.atLow = p.low != null && p.best.p <= p.low;
    p.text = norm([p.name, p.brand, p.type, p.ean].join(" "));
  }
  const brands = {};
  data.products.forEach(p => { if (p.brand) brands[p.brand] = (brands[p.brand] || 0) + 1; });
  document.getElementById("brand").innerHTML = `<option value="">${esc(T.allBrands)}</option>` +
    Object.entries(brands).sort((a, b) => b[1] - a[1]).map(([b, n]) => `<option value="${esc(b)}">${esc(b)} (${n})</option>`).join("");
  const types = TYPE_ORDER.filter(t => data.products.some(p => p.type === t));
  document.getElementById("types").innerHTML = ["", ...types].map(t =>
    `<button class="chip cat" data-type="${esc(t)}">${esc(t ? typeName(t) : T.all)}</button>`).join("");
  for (const id of ["q", "brand", "range", "show", "sort"]) document.getElementById(id).value = state[id];
  render();
  const open = params.get("p");
  // Enlaces antiguos (?p=EAN) → página propia de la guitarra.
  if (open) { const p = data.products.find(x => x.id === open); if (p) { if (p.slug) location.replace("g/" + p.slug + ".html"); else openSheet(p); } }
}).catch(() => { document.getElementById("meta").textContent = T.loadErr; });

function matches(p) {
  if (state.type && p.type !== state.type) return false;
  if (state.brand && p.brand !== state.brand) return false;
  if (state.range) {
    const [lo, hi] = state.range.split("-").map(v => v === "" ? null : +v);
    if ((lo != null && p.best.p < lo) || (hi != null && p.best.p > hi)) return false;
  }
  if (state.show === "multi" && p.nStores < 2) return false;
  if (state.show === "stock" && !p.items.some(i => i.st)) return false;
  if (state.show === "low" && !p.atLow) return false;
  if (state.show === "lh" && !p.lh) return false;
  const words = norm(state.q).split(" ").filter(Boolean).map(w => ALIASES[w] || w);
  return words.every(w => p.text.includes(w));
}

const SORTS = {
  stores: (a, b) => b.nStores - a.nStores || a.best.p - b.best.p,
  price: (a, b) => a.best.p - b.best.p,
  "price-desc": (a, b) => b.best.p - a.best.p,
  save: (a, b) => b.save - a.save,
  name: (a, b) => a.name.localeCompare(b.name, LOCALE),
};

function tile(p) {
  const badges = [p.atLow && p.nStores ? `<span class="badge low">${esc(T.low)}</span>` : "",
                  p.save >= 1 ? `<span class="badge">${esc(tf(T.save, { v: eur(Math.round(p.save)) }))}</span>` : ""].join("");
  // Cada guitarra enlaza a su página (g/…html): histórico completo y veredicto; sin página, la ficha emergente.
  return `<${p.slug ? "a" : "div"} class="tile" data-id="${esc(p.id)}"${p.slug ? ` href="g/${esc(p.slug)}.html"` : ""}>
    <div class="badges">${badges}</div>
    <div class="img">${pic(p) ? `<img loading="lazy" src="${esc(pic(p))}" alt="">` : NOPHOTO}</div>
    <div class="body"><span class="brand">${esc(p.brand || "")}${p.type && p.type !== "Otras" ? " · " + esc(typeName(p.type)) : ""}${p.lh ? " · " + esc(T.lh) : ""}</span>
      <span class="name">${esc(p.name.replace(new RegExp("^" + (p.brand || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + " ", "i"), ""))}</span>
      <span class="price"><strong>${eur(p.best.p)}</strong></span>
      <span class="foot"><span>${esc(storeName[p.best.s] || p.best.s)}</span><span class="stores-n">${p.nStores} ${p.nStores === 1 ? T.store : T.stores}</span></span>
    </div></${p.slug ? "a" : "div"}>`;
}

function render() {
  window.history.replaceState(null, "", (() => {
    const p = new URLSearchParams();
    for (const k of ["q", "type", "brand", "range", "show"]) if (state[k]) p.set(k, state[k]);
    if (state.sort !== "stores") p.set("sort", state.sort);
    return p.toString() ? "?" + p : location.pathname;
  })());
  document.querySelectorAll("#types .chip").forEach(c => c.classList.toggle("on", c.dataset.type === state.type));
  const list = catalog.products.filter(matches).sort(SORTS[state.sort] || SORTS.stores);
  const grid = document.getElementById("grid");
  grid.innerHTML = list.length ? list.slice(0, state.shown).map(tile).join("")
    : `<p class="empty">${esc(tf(T.empty, { many: MANY }))}</p>`;
  const more = document.getElementById("more");
  more.classList.toggle("hidden", list.length <= state.shown);
  more.textContent = tf(T.more, { n: list.length - state.shown });
  const multi = catalog.products.filter(p => p.nStores > 1).length;
  document.getElementById("meta").textContent = tf(T.meta, {
    a: list.length.toLocaleString(LOCALE), b: catalog.products.length.toLocaleString(LOCALE, { useGrouping: "always" }), many: MANY,
    m: multi.toLocaleString(LOCALE), d: new Date(catalog.updated).toLocaleDateString(LOCALE, { day: "numeric", month: "short" }) });
}

let typing;
let counting;
document.getElementById("q").addEventListener("input", e => {
  clearTimeout(typing); typing = setTimeout(() => { state.q = e.target.value; state.shown = PAGE; render(); }, 150);
  // Contador de búsquedas (c.js): la que queda escrita 2 s, no cada tecla.
  clearTimeout(counting); counting = setTimeout(() => window.guitleSearch && window.guitleSearch(e.target.value), 2000);
});
if (params.get("q")) setTimeout(() => window.guitleSearch && window.guitleSearch(params.get("q")), 500);
for (const id of ["brand", "range", "show", "sort"])
  document.getElementById(id).addEventListener("change", e => { state[id] = e.target.value; state.shown = PAGE; render(); });
document.getElementById("types").addEventListener("click", e => {
  const c = e.target.closest(".chip"); if (!c) return;
  state.type = c.dataset.type; state.shown = PAGE; render();
});
document.getElementById("more").addEventListener("click", () => { state.shown += PAGE; render(); });
document.getElementById("grid").addEventListener("click", e => {
  const t = e.target.closest(".tile"); if (!t || t.tagName === "A") return;
  openSheet(catalog.products.find(p => p.id === t.dataset.id));
});

// Ficha: tiendas y evolución del precio
function openSheet(p) {
  const s = document.getElementById("sheet");
  const rows = p.items.map((i, n) => {
    const store = esc(storeName[i.s] || i.s);
    const go = i.u ? `href="${esc(i.u)}" target="_blank" rel="sponsored noopener"` : "";
    return `<tr class="${n === 0 ? "best-row" : ""}">
      <td><span class="swatch" style="background:var(${storeColor[i.s] || "--reference"})"></span>${i.u ? `<a class="store-link" ${go}>${store}</a>` : store}</td>
      <td class="num"><strong>${eur(i.p)}</strong></td>
      <td class="num muted col-diff">${n === 0 ? esc(T.best) : "+" + eur(Math.round((i.p - p.best.p) * 100) / 100)}</td>
      <td class="col-stock">${i.st === true ? `<span class="tag">${esc(T.inStock)}</span>` : i.st === false ? `<span class="tag warn">${esc(T.noStock)}</span>` : ""}</td>
      <td class="muted col-date">${fmtDay(i.d)}</td>
      <td class="num">${i.u ? `<a class="go" ${go}><span class="go-long">${esc(T.goLong)}</span><span class="go-short">${esc(T.goShort)}</span></a>` : ""}</td></tr>`;
  }).join("");
  s.innerHTML = `<button class="close" aria-label="${esc(T.close)}">✕</button>
    <div class="hero">${pic(p) ? `<img src="${esc(pic(p))}" alt="">` : ""}
      <div><div class="muted">${esc(p.brand || "")}${p.type ? " · " + esc(typeName(p.type)) : ""}</div><h2>${esc(p.name)}</h2>
        <div class="big">${eur(p.best.p)}</div><div class="muted">${esc(tf(T.inAt, { s: storeName[p.best.s] || p.best.s }))}${p.save >= 1 ? esc(tf(T.saveMax, { v: eur(Math.round(p.save)) })) : ""}</div>
        <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap">${p.atLow ? `<span class="badge low">${esc(T.atLow)}</span>` : ""}
          ${p.low != null && !p.atLow ? `<span class="tag">${esc(tf(T.lowTag, { v: eur(p.low) }))}</span>` : ""}${p.ean ? `<span class="tag">EAN ${esc(p.ean)}</span>` : ""}</div>
        ${p.sku ? `<div style="margin-top:8px"><a class="shop" href="guitarras.html?q=${encodeURIComponent(p.name)}">Ver en seguimiento (con PVP, cupones y estuche)</a></div>` : ""}
      </div></div>
    <h3>${esc(T.storesH)}</h3><div class="table-wrap"><table>${rows}</table></div>
    <h3>${esc(T.evolH)}</h3><div class="chart-box"><canvas id="chart"></canvas></div>
    <p class="muted" id="chart-note" style="font-size:.85rem"></p>`;
  s.classList.add("open"); document.getElementById("bg").classList.add("open");
  s.querySelector(".close").onclick = closeSheet;
  drawChart(p);
}
function closeSheet() {
  document.getElementById("sheet").classList.remove("open"); document.getElementById("bg").classList.remove("open");
  if (chart) { chart.destroy(); chart = null; }
}
document.getElementById("bg").addEventListener("click", closeSheet);
document.addEventListener("keydown", e => { if (e.key === "Escape") closeSheet(); });

async function drawChart(p) {
  const note = document.getElementById("chart-note");
  try { priceHistory = priceHistory || await load(CFG.history); } catch (e) { note.textContent = T.histErr; return; }
  // Claves del histórico: el EAN y, para las tiendas sin EAN (Egitana, Thomann), la URL de su ficha.
  const series = {};
  for (const k of p.hk || (p.ean ? [p.ean] : [])) for (const [s, pts] of Object.entries(priceHistory[k] || {})) series[s] = series[s] || pts;
  const today = new Date().toISOString().slice(0, 10);
  const datasets = Object.entries(series).map(([store, pts]) => ({
    label: storeName[store] || store, borderWidth: 2, pointRadius: 2.5, borderColor: css(storeColor[store] || "--reference"),
    backgroundColor: css(storeColor[store] || "--reference"),
    data: [...pts.map(([d, v]) => ({ x: d, y: v })), { x: today, y: pts.at(-1)[1] }],
  }));
  const days = new Set(Object.values(series).flat().map(([d]) => d));
  if (days.size < 2) {
    note.textContent = T.histSoon;
    document.querySelector(".chart-box").classList.add("hidden");
    return;
  }
  if (!datasets.length || !window.Chart) return;
  if (chart) chart.destroy();
  const labels = [...new Set([...days, today])].sort();
  chart = new Chart(document.getElementById("chart"), {
    type: "line", data: { labels, datasets },
    options: { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      scales: { x: { grid: { color: css("--grid") }, ticks: { color: css("--text-muted"), maxTicksLimit: 6 } },
                y: { grid: { color: css("--grid") }, ticks: { color: css("--text-muted"), callback: v => eur(v) } } },
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10 } },
                 tooltip: { callbacks: { label: c => `${c.dataset.label}: ${eur(c.parsed.y)}` } } } },
  });
}
