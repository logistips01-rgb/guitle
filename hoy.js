// "Chollos de hoy" (guitle.com/hoy/, /<país>/hoy/): las guitarras que se han publicado hoy en Instagram, en el mismo
// orden, para el enlace de la bio. Las guarda la sesión de redes en data/hoy/<país>.json:
// {"fecha": "AAAA-MM-DD", "pais": "es", "items": [{"slug","name","brand","price","store","kind","img","why"}]}
(() => {
  const root = document.getElementById("hoy");
  if (!root) return;
  const pais = root.dataset.pais, base = pais === "es" ? "" : "/" + pais;
  const t = JSON.parse(root.dataset.t || "{}");
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const DIRS = { record: "records", disque: "disques", disco: "dischi" };  // discos: su sección; guitarras: /g/
  const img = s => !s ? "" : /^https?:|^\//.test(s) ? s : "/img/p/" + s;
  const empty = () => { root.innerHTML = `<p class="hub-intro">${esc(t.empty)} <a class="navlink" href="${base}/">${esc(t.catalog)} →</a></p>`; };
  fetch(`/data/hoy/${pais}.json?d=${new Date().toISOString().slice(0, 13)}`)
    .then(r => r.ok ? r.json() : null)
    .then(d => {
      if (!d || !Array.isArray(d.items) || !d.items.length) return empty();
      const date = new Date(d.fecha + "T12:00:00").toLocaleDateString(document.documentElement.lang, { day: "numeric", month: "long" });
      root.innerHTML = `<p class="hub-intro">${esc(t.date.replace("{d}", date))}</p><div class="grid">` + d.items.map(p =>
        `<a class="tile" href="${base}/${DIRS[p.kind] || "g"}/${encodeURIComponent(p.slug)}.html"><div class="img">${p.img ? `<img loading="lazy" src="${esc(img(p.img))}" alt="">` : ""}</div>` +
        `<div class="body"><span class="brand">${esc(p.brand)}</span><span class="name">${esc(p.name)}</span>` +
        `<span class="price"><strong>${esc(p.price)}</strong></span>` +
        `<span class="foot"><span>${esc(p.store)}</span></span>${p.why ? `<span class="why" style="display:block;color:var(--text-secondary);font-size:.85rem;margin-top:6px">${esc(p.why)}</span>` : ""}</div></a>`
      ).join("") + "</div>";
    })
    .catch(empty);
})();
