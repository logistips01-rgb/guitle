// Página de una guitarra: veredicto ("¿es buen momento?") e histórico de precios.
// Junta el histórico del catálogo (cambios de precio por tienda) con el de seguimiento (data/history.json).
const CFG = document.body.dataset;
// Otros países (guitle.com/pt/…): textos en window.GUITLE_T y el idioma en <html lang>; sin ellos, en español.
const T = Object.assign({
  wait: "Llevamos {n} {days} siguiendo este modelo", day: "día", days: "días",
  waitSub: "El veredicto será más fiable con unas semanas de histórico.",
  min: "Precio mínimo registrado", minSub: "Nunca la hemos visto más barata.", minBelow: " Un {p} % por debajo de su media de 30 días.",
  good: "Buen momento: un {p} % por debajo de su precio medio", goodSub: "Media de los últimos 30 días: {avg}.",
  bad: "Ahora está un {p} % más cara de lo habitual", badSub: "Si no tienes prisa, espera: su media de 30 días es {avg} y su mínimo, {min}.",
  normal: "Precio normal", normalSub: "En la línea de su media de 30 días ({avg}). Mínimo registrado: {min}.",
  today: "precio hoy", lowest: "mínimo histórico ({d})", highest: "máximo histórico", avg: "media {n} días",
  since: "Seguimos este modelo desde el {d}.", noHist: "Aún no hay histórico de precios.", pvp: "PVP oficial", bestLine: "Mejor precio",
  alertOpen: "Avísame si baja de precio", emailPh: "tu@correo.com", emailLabel: "Tu correo", targetPh: "Precio máx. (opcional)",
  targetLabel: "Precio objetivo en euros", alertBtn: "Avisarme",
  alertLegal: "Gratis y sin registro. Al pulsar «Avisarme» aceptas la <a href=\"/legal.html#privacidad\">política\n        de privacidad</a>: usaremos tu correo solo para este aviso y te das de baja con un clic.",
  alertOk: "<b>¡Hecho!</b> En unos minutos te llegará un correo a {email} para confirmar el aviso\n        (mira también en correo no deseado).",
  alertErr: "No se ha podido guardar el aviso. Revisa el correo e inténtalo de nuevo.",
}, window.GUITLE_T || {});
const tf = (s, o) => s.replace(/\{(\w+)\}/g, (_, k) => o[k]);
const LOCALE = document.documentElement.lang === "es" ? "es-ES" : document.documentElement.lang;
const eur = v => v == null ? "–" : v.toLocaleString(LOCALE, { style: "currency", currency: document.body.dataset.cur || "EUR", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const fmtDay = d => d ? new Date(d + "T12:00:00").toLocaleDateString(LOCALE, { day: "numeric", month: "short" }) : "";
const today = new Date().toISOString().slice(0, 10);

async function load(path) {
  const r = await fetch(path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}

const addDays = (day, n) => new Date(Date.parse(day + "T12:00:00Z") + n * 864e5).toISOString().slice(0, 10);

// {tienda: [[día, precio], ...]} (solo cambios) → precio de cada tienda cada día, y el mejor de cada día.
function daily(series) {
  const days = Object.values(series).flat().map(([d]) => d).sort();
  if (!days.length) return { days: [], best: [] };
  const out = [], perStore = {};
  for (let d = days[0]; d <= today; d = addDays(d, 1)) {
    let best = null;
    for (const [store, pts] of Object.entries(series)) {
      for (const [pd, price] of pts) if (pd <= d) perStore[store] = price;
      if (perStore[store] != null && (best == null || perStore[store] < best)) best = perStore[store];
    }
    out.push([d, best, Object.keys(perStore).length]);
  }
  // Los primeros días se iban sumando tiendas: con una sola, su precio parecía el "mejor" y luego una "bajada" que
  // era solo una tienda nueva. El mejor precio empieza el primer día con al menos la mitad de las tiendas.
  const most = Math.max(...out.map(x => x[2])), from = out.findIndex(x => x[2] * 2 >= most);
  return { days: out.map(x => x[0]), best: out.slice(from).map(([d, b]) => [d, b]) };
}

function verdict(current, best) {
  const n = best.length;
  if (n < 7) return { cls: "wait", text: tf(T.wait, { n, days: n === 1 ? T.day : T.days }), sub: T.waitSub };
  const last30 = best.slice(-30).map(x => x[1]).filter(v => v != null);
  const avg = last30.reduce((a, b) => a + b, 0) / last30.length;
  const min = Math.min(...best.map(x => x[1]).filter(v => v != null));
  const diff = (current - avg) / avg * 100;
  const o = { p: Math.abs(diff).toFixed(0), avg: eur(Math.round(avg)), min: eur(min) };
  if (current <= min) return { cls: "good", text: T.min, sub: T.minSub + (diff < -0.5 ? tf(T.minBelow, o) : "") };
  if (diff <= -5) return { cls: "good", text: tf(T.good, o), sub: tf(T.goodSub, o) };
  if (diff >= 5) return { cls: "bad", text: tf(T.bad, o), sub: tf(T.badSub, o) };
  return { cls: "neutral", text: T.normal, sub: tf(T.normalSub, o) };
}

(async () => {
  // Precio, tiendas y oferta van ya en el HTML (scraper/pages.py); aquí solo el veredicto y el histórico.
  const { names, colors: color, hk } = JSON.parse(document.getElementById("stores-data").textContent);
  const best = { p: Number(CFG.best) };
  const p = { ean: CFG.ean };

  // Histórico: catálogo (+ seguimiento si es una guitarra seguida)
  const series = {};
  // Claves del histórico: el EAN y, para las tiendas sin EAN (Egitana, Thomann), la URL de su ficha.
  try {
    const h = await load(CFG.history);
    for (const k of hk || [p.ean]) for (const [s, pts] of Object.entries(h[k] || {})) series[s] = series[s] || pts;
  } catch (e) {}
  if (CFG.sku) {
    try {
      const recs = (await load("/data/history.json")).filter(r => r.sku === CFG.sku && r.status === "ok" && r.price != null);
      for (const r of recs) {
        const pts = (series[r.store] = (series[r.store] || []).filter(([d]) => d !== r.date.slice(0, 10)));
        pts.push([r.date.slice(0, 10), r.price]);
      }
      for (const s in series) series[s].sort((a, b) => a[0] < b[0] ? -1 : 1);
    } catch (e) {}
  }
  // Las series de tiendas que no venden la guitarra en el catálogo son la web de la marca: el PVP oficial,
  // que se dibuja como referencia pero no cuenta para el mejor precio.
  const pvp = Object.keys(series).filter(s => !names[s]);
  const shops = Object.fromEntries(Object.entries(series).filter(([s]) => names[s]));
  const { days, best: bestDaily } = daily(shops);
  const v = verdict(best.p, bestDaily);
  const box = document.getElementById("verdict");
  box.className = "verdict " + v.cls;
  box.innerHTML = `${esc(v.text)}<small>${esc(v.sub)}</small>`;

  const vals = bestDaily.map(x => x[1]).filter(x => x != null);
  if (vals.length) {
    const minV = Math.min(...vals), maxV = Math.max(...vals);
    const minDay = bestDaily.find(x => x[1] === minV)[0];
    const last30 = vals.slice(-30), avg = last30.reduce((a, b) => a + b, 0) / last30.length;
    document.getElementById("stats").innerHTML = [
      [eur(best.p), T.today], [eur(minV), tf(T.lowest, { d: fmtDay(minDay) })], [eur(maxV), T.highest],
      [eur(Math.round(avg)), tf(T.avg, { n: Math.min(30, vals.length) })],
    ].map(([b, s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join("");
  }
  const note = document.getElementById("chart-note");
  note.textContent = days.length ? tf(T.since, { d: fmtDay(days[0]) }) : T.noHist;
  if (days.length < 2 || !window.Chart) { document.querySelector(".chart-box").classList.add("hidden"); return; }
  const datasets = Object.entries(series).map(([store, pts]) => ({
    label: names[store] || T.pvp, borderWidth: 1.5, pointRadius: 2.5,
    borderDash: pvp.includes(store) ? [6, 4] : [],
    borderColor: css(color[store] || "--reference"), backgroundColor: css(color[store] || "--reference"),
    data: [...pts.map(([d, y]) => ({ x: d, y })), { x: today, y: pts.at(-1)[1] }],
  }));
  datasets.unshift({ label: T.bestLine, borderWidth: 3, pointRadius: 3.5, borderColor: css("--text-primary"),
                     backgroundColor: css("--text-primary"), data: bestDaily.map(([x, y]) => ({ x, y })) });
  new Chart(document.getElementById("chart"), {
    type: "line", data: { labels: days, datasets },
    options: { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      scales: { x: { grid: { color: css("--grid") }, ticks: { color: css("--text-muted"), maxTicksLimit: 6, callback: function (v) { return fmtDay(this.getLabelForValue(v)); } } },
                y: { grid: { color: css("--grid") }, ticks: { color: css("--text-muted"), callback: v => eur(v) } } },
      plugins: { legend: { labels: { color: css("--text-secondary"), boxWidth: 10 } },
                 tooltip: { callbacks: { title: c => fmtDay(c[0].label), label: c => `${c.dataset.label}: ${eur(c.parsed.y)}` } } } },
  });
})();

// Aviso por correo cuando baja el precio: se guarda en Firestore (colección "alertas") con un código aleatorio como
// id, que solo conoce quien se apunta (confirmar y darse de baja en alerta.html). La tarea scraper/alerts.py envía
// el correo de confirmación y los avisos. Las reglas de Firestore no dejan leer la colección desde la web.
(() => {
  const ALERTS = "https://firestore.googleapis.com/v1/projects/guitle-d48d8/databases/(default)/documents/alertas";
  // Un botón discreto junto al precio; el formulario se abre al pulsarlo.
  const after = document.getElementById("verdict");
  if (!after) return;
  // En otros países el aviso lleva delante su código ("pt/<slug>"): scraper/alerts.py busca en ese catálogo.
  const slug = (CFG.site ? CFG.site + "/" : "") + location.pathname.split("/").pop().replace(/\.html$/, "");
  const name = document.querySelector(".pname")?.textContent.trim() || slug;
  const price = +CFG.best;
  const box = document.createElement("div");
  box.className = "alert-box";
  box.innerHTML = `<button type="button" class="alert-open" aria-expanded="false">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
      ${esc(T.alertOpen)}</button>
    <form id="alert-form" hidden>
      <input type="email" id="alert-email" required placeholder="${esc(T.emailPh)}" autocomplete="email" aria-label="${esc(T.emailLabel)}">
      <input type="number" id="alert-target" min="1" step="1" placeholder="${esc(T.targetPh)}" aria-label="${esc(T.targetLabel)}">
      <button type="submit">${esc(T.alertBtn)}</button>
      <p class="small muted">${T.alertLegal}</p>
    </form>
    <p class="small" id="alert-msg" role="status"></p>`;
  after.after(box);
  const open = box.querySelector(".alert-open"), form = box.querySelector("form");
  open.addEventListener("click", () => {
    form.hidden = !form.hidden;
    open.setAttribute("aria-expanded", String(!form.hidden));
    if (!form.hidden) box.querySelector("#alert-email").focus();
  });
  const msg = box.querySelector("#alert-msg");
  box.querySelector("#alert-form").addEventListener("submit", async e => {
    e.preventDefault();
    const email = box.querySelector("#alert-email").value.trim();
    const target = parseFloat(box.querySelector("#alert-target").value);
    const id = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(24))))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
    const fields = { email: { stringValue: email }, slug: { stringValue: slug }, name: { stringValue: name.slice(0, 190) },
                     price: { doubleValue: price }, ok: { booleanValue: false } };
    if (target > 0) fields.target = { doubleValue: target };
    const button = box.querySelector("button");
    button.disabled = true;
    try {
      const r = await fetch(`${ALERTS}?documentId=${id}`, { method: "POST", headers: { "Content-Type": "application/json" },
                                                          body: JSON.stringify({ fields }) });
      if (!r.ok) throw new Error(r.status);
      form.hidden = true; open.hidden = true;
      msg.innerHTML = tf(T.alertOk, { email: esc(email) });
    } catch (err) {
      button.disabled = false;
      msg.textContent = T.alertErr;
    }
  });
})();
