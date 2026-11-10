"""Botones de Amazon y eBay en las fichas (donde guitle cobra comisión): bien visibles, debajo de la tabla de tiendas.

  - Amazon: búsqueda del modelo con el código de afiliado del país (intl.SITES[...]["amazon"]; España: guitle-21).
  - eBay: búsqueda del modelo (aunque no haya el mismo anuncio, salen los parecidos) con el enlace de eBay Partner
    Network (campid de guitle) del eBay del país; los países sin eBay propio van al más cercano.
Códigos de cada eBay (mkrid): tabla oficial de eBay, developer.ebay.com/api-docs/buy/static/ref-epn-link.html.
"""
import html
from urllib.parse import quote_plus

CAMPID = "5339241544"  # eBay Partner Network (guitle), el mismo de scraper/ebay.py
EBAY_SITES = {  # dominio, mkrid
    "es": ("www.ebay.es", "1185-53479-19255-0"), "fr": ("www.ebay.fr", "709-53476-19255-0"),
    "it": ("www.ebay.it", "724-53478-19255-0"), "de": ("www.ebay.de", "707-53477-19255-0"),
    "at": ("www.ebay.at", "5221-53469-19255-0"), "ch": ("www.ebay.ch", "5222-53480-19255-0"),
    "nl": ("www.ebay.nl", "1346-53482-19255-0"), "be": ("www.benl.ebay.be", "1553-53471-19255-0"),
    "uk": ("www.ebay.co.uk", "710-53481-19255-0"), "ie": ("www.ebay.ie", "5282-53468-19255-0"),
    "pl": ("www.ebay.pl", "4908-226936-19255-0"), "us": ("www.ebay.com", "711-53200-19255-0"),
}
# Países de guitle sin eBay propio: el más cercano que envía allí
EBAY_FOR = {"pt": "es", "lu": "fr", "se": "de", "no": "de", "dk": "de", "fi": "de", "cz": "de", "sk": "de", "hu": "de",
            "ro": "de", "bg": "de", "gr": "de", "br": "us", "mx": "us", "ar": "us"}

TXT = {  # idioma (intl.SITES[...]["t"]) → (Amazon, eBay, nota)
    "es": ("Ver en Amazon", "Buscar en eBay", "Precio y envío en su web. Si compras desde aquí, guitle se lleva una pequeña comisión sin que te cueste más."),
    "pt": ("Ver na Amazon", "Procurar no eBay", "Preço e envio no site deles. Se comprar a partir daqui, o guitle recebe uma pequena comissão sem custo extra."),
    "br": ("Ver na Amazon", "Procurar no eBay", "Preço e frete no site deles. Se comprar por aqui, o guitle recebe uma pequena comissão sem custo extra."),
    "fr": ("Voir sur Amazon", "Chercher sur eBay", "Prix et livraison sur leur site. Si vous achetez depuis ici, guitle touche une petite commission sans surcoût."),
    "it": ("Vedi su Amazon", "Cerca su eBay", "Prezzo e spedizione sul loro sito. Se acquisti da qui, guitle riceve una piccola commissione senza costi in più."),
    "de": ("Bei Amazon ansehen", "Bei eBay suchen", "Preis und Versand auf deren Seite. Wenn du von hier kaufst, erhält guitle eine kleine Provision, ohne Mehrkosten."),
    "en": ("View on Amazon", "Search on eBay", "Price and delivery on their site. If you buy from here, guitle earns a small commission at no extra cost."),
    "nl": ("Bekijk op Amazon", "Zoek op eBay", "Prijs en verzending op hun site. Koop je via hier, dan krijgt guitle een kleine commissie zonder extra kosten."),
    "pl": ("Zobacz na Amazon", "Szukaj na eBay", "Cena i wysyłka na ich stronie. Kupując stąd, wspierasz guitle małą prowizją bez dodatkowych kosztów."),
    "sv": ("Se på Amazon", "Sök på eBay", "Pris och frakt på deras sida. Köper du härifrån får guitle en liten provision utan extra kostnad."),
    "nb": ("Se på Amazon", "Søk på eBay", "Pris og frakt på deres side. Kjøper du herfra, får guitle en liten provisjon uten ekstra kostnad."),
    "da": ("Se på Amazon", "Søg på eBay", "Pris og fragt på deres side. Køber du herfra, får guitle en lille provision uden ekstra omkostninger."),
    "cs": ("Zobrazit na Amazonu", "Hledat na eBay", "Cena a doprava na jejich webu. Pokud nakoupíte odsud, guitle získá malou provizi bez navýšení ceny."),
    "sk": ("Zobraziť na Amazone", "Hľadať na eBay", "Cena a doprava na ich webe. Ak nakúpite odtiaľto, guitle získa malú províziu bez navýšenia ceny."),
    "hu": ("Megnézem az Amazonon", "Keresés az eBay-en", "Ár és szállítás az ő oldalukon. Ha innen vásárolsz, a guitle kis jutalékot kap, neked nem kerül többe."),
    "ro": ("Vezi pe Amazon", "Caută pe eBay", "Prețul și livrarea pe site-ul lor. Dacă cumperi de aici, guitle primește un mic comision fără cost suplimentar."),
    "bg": ("Виж в Amazon", "Търси в eBay", "Цена и доставка на техния сайт. Ако купите оттук, guitle получава малка комисионна без допълнителни разходи."),
    "el": ("Δείτε στο Amazon", "Αναζήτηση στο eBay", "Τιμή και αποστολή στον ιστότοπό τους. Αν αγοράσετε από εδώ, το guitle παίρνει μια μικρή προμήθεια χωρίς επιπλέον κόστος."),
    "fi": ("Katso Amazonissa", "Hae eBaysta", "Hinta ja toimitus heidän sivullaan. Jos ostat täältä, guitle saa pienen palkkion ilman lisäkulua."),
}

CSS = (".mkt{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 4px}"
       ".mkt a{flex:1 1 200px;display:flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:10px 16px;"
       "border-radius:12px;font-weight:700;font-size:1rem;text-decoration:none}"
       ".mkt .amz{background:#ff9900;color:#111}.mkt .amz:hover{background:#f08804}"
       ".mkt .eby{background:#fff;color:#0064d2;border:2px solid #0064d2}.mkt .eby:hover{background:#0064d2;color:#fff}"
       ".mkt-note{font-size:.8rem;color:var(--text-secondary,#666);margin:4px 0 0}")


def ebay_url(code, query):
    domain, mkrid = EBAY_SITES[EBAY_FOR.get(code, code)] if EBAY_FOR.get(code, code) in EBAY_SITES else EBAY_SITES["de"]
    return (f"https://{domain}/sch/i.html?_nkw={quote_plus(query)}&mkcid=1&mkrid={mkrid}&campid={CAMPID}"
            f"&customid=guitle-{code}&toolid=10001&mkevt=1")


ACTIVO = True  # visto bueno de Manuel a la vista previa (10/11/2026)


def buttons(code, lang, query, amazon_tpl):
    """HTML del bloque (con su <style>): Amazon si el país tiene código de afiliado, eBay siempre."""
    a, e, note = TXT.get(lang, TXT["en"])
    esc = lambda s: html.escape(s, quote=True)
    if not ACTIVO:
        return (f'<p class="muted small amazon"><a href="{esc(amazon_tpl.format(q=quote_plus(query)))}" target="_blank" '
                f'rel="sponsored noopener">{esc(a)}</a></p>' if amazon_tpl else "")
    links = []
    if amazon_tpl:
        links.append(f'<a class="amz" href="{esc(amazon_tpl.format(q=quote_plus(query)))}" target="_blank" rel="sponsored noopener">{esc(a)} →</a>')
    links.append(f'<a class="eby" href="{esc(ebay_url(code, query))}" target="_blank" rel="sponsored noopener">{esc(e)} →</a>')
    return f'<style>{CSS}</style><div class="mkt">{"".join(links)}</div><p class="mkt-note">{esc(note)}</p>'
