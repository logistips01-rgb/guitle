// Página de una guitarra: tiendas, veredicto ("¿es buen momento?") e histórico de precios.
// Junta el histórico del catálogo (cambios de precio por tienda) con el de seguimiento (data/history.json).
const CFG = document.body.dataset;
const eur = v => v == null ? "–" : v.toLocaleString("es-ES", { style: "currency", currency: "EUR", minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const fmtDay = d => d ? new Date(d + "T12:00:00").toLocaleDateString("es-ES", { day: "numeric", month: "short" }) : "";
const PALETTE = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6", "--s7", "--s8"];
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
    out.push([d, best]);
  }
  return { days: out.map(x => x[0]), best: out };
}

function verdict(current, best) {
  const n = best.length;
  if (n < 7) return { cls: "wait", text: `Llevamos ${n} ${n === 1 ? "día" : "días"} siguiendo esta guitarra`,
                      sub: "El veredicto será más fiable con unas semanas de histórico." };
  const last30 = best.slice(-30).map(x => x[1]).filter(v => v != null);
  const avg = last30.reduce((a, b) => a + b, 0) / last30.length;
  const min = Math.min(...best.map(x => x[1]).filter(v => v != null));
  const diff = (current - avg) / avg * 100;
  if (current <= min) return { cls: "good", text: "Precio mínimo registrado", sub: `Nunca la hemos visto más barata. ${diff < -0.5 ? `Un ${Math.abs(diff).toFixed(0)} % por debajo de su media de 30 días.` : ""}` };
  if (diff <= -5) return { cls: "good", text: `Buen momento: un ${Math.abs(diff).toFixed(0)} % por debajo de su precio medio`, sub: `Media de los últimos 30 días: ${eur(Math.round(avg))}.` };
  if (diff >= 5) return { cls: "bad", text: `Ahora está un ${diff.toFixed(0)} % más cara de lo habitual`, sub: `Si no tienes prisa, espera: su media de 30 días es ${eur(Math.round(avg))} y su mínimo, ${eur(min)}.` };
  return { cls: "neutral", text: "Precio normal", sub: `En la línea de su media de 30 días (${eur(Math.round(avg))}). Mínimo registrado: ${eur(min)}.` };
}

(async () => {
  let cat;
  try { cat = await load(CFG.src); } catch (e) { document.getElementById("price").textContent = "No se pudo cargar el precio."; return; }
  const p = cat.products.find(x => String(x.id) === CFG.id);
  if (!p) { document.getElementById("price").textContent = "Ya no la encontramos en ninguna tienda."; return; }
  const names = cat.stores;
  const color = Object.fromEntries(Object.keys(names).map((s, i) => [s, PALETTE[i % PALETTE.length]]));
  const best = p.items[0];
  document.getElementById("price").textContent = eur(best.p);
  const save = Math.max(...p.items.map(i => i.p)) - best.p;
  document.getElementById("where").textContent = `en ${names[best.s] || best.s}` +
    (p.items.length > 1 ? ` · ${p.items.length} tiendas${save >= 1 ? `, hasta ${eur(Math.round(save))} de diferencia` : ""}` : "");

  // Tiendas
  document.getElementById("stores").innerHTML = p.items.map((i, n) => {
    const go = i.u ? `href="${esc(i.u)}" target="_blank" rel="sponsored noopener"` : "";
    const store = esc(names[i.s] || i.s);
    return `<tr class="${n === 0 ? "best-row" : ""}">
      <td><span class="swatch" style="background:var(${color[i.s] || "--reference"})"></span>${i.u ? `<a class="store-link" ${go}>${store}</a>` : store}</td>
      <td class="num"><strong>${eur(i.p)}</strong></td>
      <td class="num muted col-diff">${n === 0 ? "mejor precio" : "+" + eur(Math.round((i.p - best.p) * 100) / 100)}</td>
      <td>${i.st === true ? '<span class="tag">en stock</span>' : i.st === false ? '<span class="tag warn">sin stock</span>' : ""}</td>
      <td class="muted col-date">${fmtDay(i.d)}</td>
      <td class="num">${i.u ? `<a class="go" ${go}><span class="go-long">Ir a la tienda</span><span class="go-short">Ir</span></a>` : ""}</td></tr>`;
  }).join("");

  // Histórico: catálogo (+ seguimiento si es una guitarra seguida)
  const series = {};
  try { Object.assign(series, (await load(CFG.history))[p.ean] || {}); } catch (e) {}
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
      [eur(best.p), "precio hoy"], [eur(minV), `mínimo histórico (${fmtDay(minDay)})`], [eur(maxV), "máximo histórico"],
      [eur(Math.round(avg)), `media ${Math.min(30, vals.length)} días`],
    ].map(([b, s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join("");
  }
  const note = document.getElementById("chart-note");
  note.textContent = days.length ? `Seguimos esta guitarra desde el ${fmtDay(days[0])}.` : "Aún no hay histórico de precios.";
  if (days.length < 2 || !window.Chart) { document.querySelector(".chart-box").classList.add("hidden"); return; }
  const datasets = Object.entries(series).map(([store, pts]) => ({
    label: names[store] || "PVP oficial", stepped: true, borderWidth: 1.5, pointRadius: 0,
    borderDash: pvp.includes(store) ? [6, 4] : [],
    borderColor: css(color[store] || "--reference"), backgroundColor: css(color[store] || "--reference"),
    data: [...pts.map(([d, y]) => ({ x: d, y })), { x: today, y: pts.at(-1)[1] }],
  }));
  datasets.unshift({ label: "Mejor precio", stepped: true, borderWidth: 3, pointRadius: 0, borderColor: css("--text-primary"),
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
