// guitle.com: si la web española no responde (los cortes de LaLiga bloquean las IP de Cloudflare en España durante los
// partidos), este service worker abre la misma página en guitle.es, la copia de emergencia (GitHub Pages; ver
// .github/workflows/copia-es.yml). No guarda nada en caché: solo mira las navegaciones y, si fallan o no contestan en
// 12 s, redirige. Lo registra c.js en guitle.com. Las webs de los demás países no se tocan (no tienen copia).
const COUNTRY = /^\/(?:pt|fr|it|uk|de|br|ie|at|nl|be|ch|pl|se|no|dk|cz|sk|hu|ro|bg|gr|fi|lu|mx|ar)(?:\/|$)/;
const ESPEJO = "https://guitle.es";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", event => event.waitUntil(self.clients.claim()));

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.mode !== "navigate" || req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.hostname !== "guitle.com" || COUNTRY.test(url.pathname)) return;
  event.respondWith((async () => {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 12000);
    try {
      return await fetch(req, { signal: ctrl.signal });
    } catch (e) {
      // ?ref=corte: en las estadísticas, las visitas rescatadas de un corte ("r_promo-corte")
      const q = new URLSearchParams(url.search);
      if (!q.has("ref") && !q.has("utm_source")) q.set("ref", "corte");
      return Response.redirect(ESPEJO + url.pathname + "?" + q.toString(), 302);
    } finally {
      clearTimeout(timer);
    }
  })());
});
