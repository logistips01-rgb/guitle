// Chollos (chollos.html y black-friday.html): data/deals-<categoría>.json de scraper/deals.py.
const eur = v => v == null ? "–" : v.toLocaleString("es-ES", { style: "currency", currency: "EUR", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const NOPHOTO = '<svg class="nophoto" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 3l-6.5 6.5"/><path d="M19.5 1.5l3 3-1.5 1.5-3-3z"/><path d="M14.5 9.5c-1.6-1.6-3.9-1.3-5 .2-1 .4-2.6.1-4 1.5-2.1 2.1-1.7 5.4.6 7.7s5.6 2.7 7.7.6c1.4-1.4 1.1-3 1.5-4 1.5-1.1 1.8-3.4.2-5z"/><circle cx="9.6" cy="14.4" r="1.4"/></svg>';
const KINDS = { electrica: "Eléctrica", acustica: "Acústica", clasica: "Clásica", teclado: "Teclado", pedal: "Pedal" };
const MIN_DAYS = 7;

async function load(path) {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(path);
  return r.json();
}

function tile(r, badge, extra = "") {
  return `<a class="tile" href="g/${esc(r.slug)}.html">
    <div class="badges">${badge}</div>
    <div class="img">${r.th ? `<img loading="lazy" src="img/p/${esc(r.th)}" alt="">` : NOPHOTO}</div>
    <div class="body"><span class="brand">${esc(r.brand || "")} <span class="kind">· ${KINDS[r.kind]}</span></span>
      <span class="name">${esc(r.name)}</span>${extra}
      <span class="price"><strong>${eur(r.price)}</strong></span>
      <span class="foot"><span>${esc(r.storeName)}</span><span class="stores-n">${r.stores} ${r.stores === 1 ? "tienda" : "tiendas"}</span></span>
    </div></a>`;
}

Promise.all(Object.keys(KINDS).map(k => load(`data/deals-${k}.json`).then(d => ({ k, d })).catch(() => null))).then(all => {
  all = all.filter(Boolean);
  const days = Math.max(0, ...all.map(x => x.d.history_days));
  const pick = key => all.flatMap(({ k, d }) => d[key].map(r => ({ ...r, kind: k, storeName: d.stores[r.store] || r.store,
    fakeStore: r.inflated ? d.stores[r.inflated.store] || r.inflated.store : "" })));
  const render = (id, list, badge, extra, emptyText) => {
    document.getElementById(id).innerHTML = list.length
      ? `<div class="grid">${list.map(r => tile(r, badge(r), extra ? extra(r) : "")).join("")}</div>`
      : `<div class="waiting">${emptyText}</div>`;
  };
  const nDays = n => `${n} ${n === 1 ? "día" : "días"}`;
  const wait = days < MIN_DAYS
    ? `Esta sección se activa con ${MIN_DAYS} días de histórico: llevamos ${nDays(days)}. Vuelve en unos días.`
    : "Hoy no hay ninguna. Las revisamos cada día.";
  render("records", pick("records").sort((a, b) => a.vs_avg - b.vs_avg),
         r => `<span class="badge low">Mínimo</span><span class="badge">${r.vs_avg.toFixed(0)} % vs media</span>`, null, wait);
  render("real_drops", pick("real_drops").sort((a, b) => a.vs_avg - b.vs_avg),
         r => `<span class="badge">${r.vs_avg.toFixed(0)} % vs media</span>`, null, wait);
  render("today", pick("today").sort((a, b) => a.vs_yesterday - b.vs_yesterday),
         r => `<span class="badge">−${eur(Math.abs(r.vs_yesterday))} hoy</span>`, null, "Hoy ninguna tienda ha rebajado sus guitarras. Lo revisamos cada día.");
  render("inflated", pick("inflated"), () => '<span class="badge bad">Inflado</span>',
         r => `<span class="fake">${esc(r.fakeStore)}: antes <b>${eur(r.inflated.before)}</b>, subió a <s>${eur(r.inflated.raised)}</s> y ahora "rebajada" a <b>${eur(r.inflated.now)}</b>.</span>`,
         days < 14 ? `Para detectarlos necesitamos unas semanas de histórico: llevamos ${nDays(days)}. Estará listo para el Black Friday.` : "Hoy no hemos detectado ninguno.");
  document.getElementById("status").textContent = `Precios revisados cada día · ${nDays(days)} de histórico.`;
});
