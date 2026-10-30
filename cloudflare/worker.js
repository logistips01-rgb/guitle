// guitle.com desde el bucket R2 "guitle" (lo llena .github/workflows/r2.yml). Mismas direcciones que GitHub Pages:
// "/" y "/fr/" sirven su index.html, "/fr" redirige a "/fr/", "/catalogo" sirve catalogo.html y www va a guitle.com.
// Las fotos de producto (img/p/, nombre = huella de la URL) no cambian nunca: caché larga. El resto, 10 minutos,
// como GitHub Pages, para que los precios nuevos se vean enseguida.

const TYPES = {
  html: "text/html; charset=utf-8", css: "text/css; charset=utf-8", js: "text/javascript; charset=utf-8",
  json: "application/json; charset=utf-8", xml: "application/xml; charset=utf-8", txt: "text/plain; charset=utf-8",
  svg: "image/svg+xml", webp: "image/webp", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif",
  ico: "image/x-icon", avif: "image/avif", woff2: "font/woff2", woff: "font/woff", webmanifest: "application/manifest+json",
};

const ext = key => (key.match(/\.([a-z0-9]+)$/i) || [])[1]?.toLowerCase();

export default {
  async fetch(req, env, ctx) {
    if (req.method !== "GET" && req.method !== "HEAD") return new Response("Method Not Allowed", { status: 405, headers: { allow: "GET, HEAD" } });
    const url = new URL(req.url);
    if (url.hostname.startsWith("www.")) {
      url.hostname = url.hostname.slice(4);
      return Response.redirect(url.toString(), 301);
    }

    const cache = caches.default;
    const hit = await cache.match(req);
    if (hit) return hit;

    let key;
    try { key = decodeURIComponent(url.pathname).replace(/^\/+/, ""); } catch { return notFound(); }
    if (key === "" || key.endsWith("/")) key += "index.html";

    let obj = await env.SITE.get(key, { onlyIf: req.headers });
    if (!obj && !ext(key)) {
      // "/catalogo" → catalogo.html; "/fr" → "/fr/".
      obj = await env.SITE.get(key + ".html", { onlyIf: req.headers });
      if (obj) key += ".html";
      else if (await env.SITE.head(key + "/index.html")) {
        url.pathname += "/";
        return Response.redirect(url.toString(), 301);
      }
    }
    if (!obj) return notFound();

    const headers = new Headers();
    obj.writeHttpMetadata(headers);
    headers.set("content-type", TYPES[ext(key)] || headers.get("content-type") || "application/octet-stream");
    headers.set("etag", obj.httpEtag);
    headers.set("cache-control", key.startsWith("img/p/") ? "public, max-age=2592000, immutable" : "public, max-age=600");
    headers.set("x-content-type-options", "nosniff");

    // onlyIf: si el navegador ya tiene esta versión, R2 devuelve el objeto sin cuerpo → 304.
    if (!("body" in obj)) return new Response(null, { status: 304, headers });
    const res = new Response(req.method === "HEAD" ? null : obj.body, { headers });
    if (req.method === "GET") ctx.waitUntil(cache.put(req, res.clone()));
    return res;
  },
};

function notFound() {
  return new Response('<!doctype html><meta charset="utf-8"><title>No encontrado · guitle</title>' +
    '<p style="font-family:system-ui;padding:40px">Esta página no existe. <a href="/">Volver a guitle</a></p>',
    { status: 404, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" } });
}
