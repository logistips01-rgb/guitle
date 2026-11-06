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

// Fichas en cajas (scraper/cajas.py): las fichas de estos países salen de <país>/_g/<caja>.json.gz en vez de un
// fichero por ficha. Se activa un país cuando se ha comprobado que sus fichas salen idénticas (?caja=1 lo prueba sin
// activarlo). Si la caja no está o no tiene la ficha, se sirve el fichero de siempre.
const CAJAS = 2048;
const CON_CAJAS = new Set(["lu", "fi", "pt", "fr", "it", "de", "pl", "se", "no", "dk", "uk", "br", "ie", "at", "nl", "be", "ch", "cz", "sk", "ro", "bg", "hu", "gr", "mx", "ar"]);

function fnv(text) {
  let h = 0x811c9dc5;
  for (const b of new TextEncoder().encode(text)) h = Math.imul(h ^ b, 0x01000193) >>> 0;
  return h >>> 0;
}

// Cajas ya abiertas, en memoria (unas pocas decenas, 10 minutos): la siguiente ficha de la misma caja no vuelve a
// leer R2 ni a descomprimir. Y la caja comprimida, en la caché de Cloudflare, para el resto de servidores de la zona.
const BOXES = new Map();
const BOX_TTL = 600e3, BOX_MAX = 64;

async function openBox(env, box) {
  const hit = BOXES.get(box);
  if (hit && Date.now() - hit.t < BOX_TTL) return hit;
  const ckey = new Request(`https://cajas.guitle.com/${box}`);
  let res = await caches.default.match(ckey), etag;
  if (res) etag = res.headers.get("x-etag");
  else {
    const obj = await env.SITE.get(box);
    if (!obj) return null;
    etag = obj.etag.replace(/"/g, "");
    const raw = await obj.arrayBuffer();
    res = new Response(raw, { headers: { "cache-control": "public, max-age=600", "x-etag": etag } });
    await caches.default.put(ckey, res.clone());
  }
  const pages = JSON.parse(await new Response(res.body.pipeThrough(new DecompressionStream("gzip"))).text());
  const entry = { pages, etag, t: Date.now() };
  if (BOXES.size >= BOX_MAX) BOXES.delete(BOXES.keys().next().value);
  BOXES.set(box, entry);
  return entry;
}

async function fromBox(env, code, slug) {
  const box = await openBox(env, `${code}/_g/${(fnv(slug) % CAJAS).toString(16).padStart(4, "0")}.json.gz`);
  if (!box || typeof box.pages[slug] !== "string") return null;
  return { html: box.pages[slug], etag: `"${box.etag}-${fnv(slug).toString(16)}"` };
}

// Secciones enteras en cajas (scraper/cajas.py empaquetar_carpeta): la sección de discos de estos países. La clave es la
// ruta dentro del país ("records/x.html", "records/artist/y.html", "records/index.html").
const CAJAS_R = 512;
const SECCIONES = { records: new Set(["uk"]) };

async function fromSectionBox(env, code, rel) {
  const box = await openBox(env, `${code}/_r/${(fnv(rel) % CAJAS_R).toString(16).padStart(4, "0")}.json.gz`);
  if (!box || typeof box.pages[rel] !== "string") return null;
  return { html: box.pages[rel], etag: `"${box.etag}-${fnv(rel).toString(16)}"` };
}

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

    const sec = key.match(/^([a-z]{2})\/((records)\/.+\.html)$/);
    if (sec && (SECCIONES[sec[3]]?.has(sec[1]) || url.searchParams.get("caja") === "1")) {
      let box = null;
      try { box = await fromSectionBox(env, sec[1], sec[2]); } catch { box = null; }
      if (box) {
        const headers = new Headers({ "content-type": TYPES.html, etag: box.etag, "cache-control": "public, max-age=600",
          "x-content-type-options": "nosniff", "x-guitle-caja": "1" });
        if (req.headers.get("if-none-match") === box.etag) return new Response(null, { status: 304, headers });
        const res = new Response(req.method === "HEAD" ? null : box.html, { headers });
        if (req.method === "GET" && url.searchParams.get("caja") !== "1") ctx.waitUntil(cache.put(req, res.clone()));
        return res;
      }
    }
    const ficha = key.match(/^([a-z]{2})\/g\/([^/]+)\.html$/);
    const probar = url.searchParams.get("caja") === "1";
    if (ficha && (CON_CAJAS.has(ficha[1]) || probar)) {
      let box = null;
      try { box = await fromBox(env, ficha[1], ficha[2]); } catch { box = null; }
      if (box) {
        const headers = new Headers({ "content-type": TYPES.html, etag: box.etag, "cache-control": "public, max-age=600",
          "x-content-type-options": "nosniff", "x-guitle-caja": "1" });
        if (req.headers.get("if-none-match") === box.etag) return new Response(null, { status: 304, headers });
        const res = new Response(req.method === "HEAD" ? null : box.html, { headers });
        if (req.method === "GET" && !probar) ctx.waitUntil(cache.put(req, res.clone()));
        return res;
      }
      if (probar) return new Response("sin caja", { status: 404, headers: { "x-guitle-caja": "0" } });
    }

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
    // Los datos (precios, chollos de portada) caducan al minuto: un arreglo se ve enseguida en todas partes.
    headers.set("cache-control", key.startsWith("img/p/") ? "public, max-age=2592000, immutable"
      : key.startsWith("data/") ? "public, max-age=60" : "public, max-age=600");
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
