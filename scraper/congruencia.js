// Abre cada ficha elegida por scraper/congruencia.py en un navegador y mira si el precio de guitle sale en la página
// tal como la ve el cliente. Uso: node scraper/congruencia.js filas.json data/congruencia.json
// Los números de la página se leen en cualquier formato (1.299,00 / 1,299.00 / 1 299 zł / 8 290 Kč) y se comparan
// con el precio de guitle (tolerancia de 1 céntimo). 4 fichas a la vez, siempre de tiendas distintas.
const fs = require('fs');
const { chromium } = require('playwright');
const [, , input, output] = process.argv;
const rows = JSON.parse(fs.readFileSync(input, 'utf8'));

function numbers(text) {
  const out = [];
  const t = text.replace(/[   ]/g, ' ');
  for (const m of t.matchAll(/\d{1,3}(?:[ .,']\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?/g)) {
    let s = m[0].replace(/[ ']/g, '');
    const lastDot = s.lastIndexOf('.'), lastComma = s.lastIndexOf(',');
    const dec = Math.max(lastDot, lastComma);
    if (dec >= 0 && s.length - dec - 1 <= 2) {  // el último separador con 1-2 cifras detrás es el decimal
      s = s.slice(0, dec).replace(/[.,]/g, '') + '.' + s.slice(dec + 1);
    } else {
      s = s.replace(/[.,]/g, '');
    }
    const v = parseFloat(s);
    if (!isNaN(v)) out.push(v);
  }
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
  });
  const results = [];
  let next = 0;
  async function worker() {
    while (next < rows.length) {
      const r = rows[next++];
      const page = await ctx.newPage();
      const res = { ...r };
      try {
        const resp = await page.goto(r.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4000);
        res.http = resp ? resp.status() : 0;
        const text = await page.evaluate(() => document.body ? document.body.innerText : '');
        if (res.http >= 400 || text.length < 200) {
          res.estado = 'sin_comprobar';  // la tienda no deja ver la página a GitHub (403, captcha…)
        } else {
          const nums = numbers(text);
          // También con los céntimos aparte (434⁴⁶ € → 43446) y en cuotas de Brasil (10x de R$ 399,00 = 3.990)
          const cents = r.precio % 1 ? Math.round(r.precio * 100) : null;
          const cuotas = [...text.matchAll(/(\d{1,2})\s?x\s?(?:de\s)?R\$\s?([\d.]+,\d{2})/g)]
            .map(m => +m[1] * parseFloat(m[2].replace(/\./g, '').replace(',', '.')));
          res.estado = nums.some(v => Math.abs(v - r.precio) < 0.011 || (cents && v === cents))
            || cuotas.some(v => Math.abs(v - r.precio) < 0.11) ? 'ok' : 'distinto';
          if (res.estado === 'distinto') {
            const t = text.replace(/\s+/g, ' ');
            res.visibles = [...t.matchAll(/(?:€|£|\$|zł|Kč|kr|Ft|lei|лв|CHF|R\$)\s?[\d.,  ]{2,12}|[\d.,  ]{2,12}\s?(?:€|£|zł|Kč|kr|Ft|lei|лв|CHF)/g)]
              .slice(0, 6).map(m => m[0].trim());
          }
        }
      } catch (e) {
        res.estado = 'sin_comprobar';
        res.error = String(e.message || e).split('\n')[0].slice(0, 120);
      }
      results.push(res);
      await page.close();
    }
  }
  await Promise.all([worker(), worker(), worker(), worker()]);
  await browser.close();
  const count = s => results.filter(r => r.estado === s).length;
  const out = {
    actualizado: new Date().toISOString().slice(0, 16),
    total: results.length, ok: count('ok'), distinto: count('distinto'), sin_comprobar: count('sin_comprobar'),
    distintos: results.filter(r => r.estado === 'distinto'),
    sin_comprobar_tiendas: results.filter(r => r.estado === 'sin_comprobar').map(r => `${r.pais}·${r.tienda}`),
  };
  fs.writeFileSync(output, JSON.stringify(out, null, 1) + '\n');
  console.log(`congruencia: ${out.ok} ok, ${out.distinto} distintos, ${out.sin_comprobar} sin comprobar de ${out.total}`);
  for (const r of out.distintos) console.log(`::warning::${r.pais} ${r.tienda}: guitle ${r.precio} · página ${JSON.stringify(r.visibles)} · ${r.url}`);
})();
