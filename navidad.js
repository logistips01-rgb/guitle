// Regalos de Navidad: "Nuestra selección en Amazon", elegida a mano en data/navidad/<país>.json:
// [{"nombre": "...", "enlace": "https://amzn.to/... o https://www.amazon.es/dp/...?tag=guitle-21", "precio": "29,99 €",
//   "foto": "https://... (opcional)", "nota": "por qué es buen regalo (opcional)"}]
(() => {
  const box = document.getElementById("amzsel");
  if (!box) return;
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const ok = u => /^https:\/\/(www\.)?(amazon\.(es|fr|it|co\.uk|de|com)|amzn\.(to|eu))\//.test(u || "");
  fetch(`/data/navidad/${box.dataset.pais}.json?d=${new Date().toISOString().slice(0, 13)}`)
    .then(r => r.ok ? r.json() : [])
    .then(list => {
      list = (Array.isArray(list) ? list : []).filter(p => p && p.nombre && ok(p.enlace));
      if (!list.length) return;
      box.innerHTML = `<h2>${esc(box.dataset.h)}</h2><div class="grid">` + list.map(p =>
        `<a class="tile" href="${esc(p.enlace)}" target="_blank" rel="sponsored noopener"><div class="img">${p.foto ? `<img loading="lazy" src="${esc(p.foto)}" alt="">` : ""}</div>` +
        `<div class="body"><span class="name">${esc(p.nombre)}</span>${p.precio ? `<span class="price"><strong>${esc(p.precio)}</strong></span>` : ""}` +
        `${p.nota ? `<span class="foot"><span>${esc(p.nota)}</span></span>` : ""}<span class="amz" style="margin-top:8px">${esc(box.dataset.b)} →</span></div></a>`
      ).join("") + "</div>";
      box.hidden = false;
    })
    .catch(() => {});
})();
