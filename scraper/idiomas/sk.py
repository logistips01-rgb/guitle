# Slovenčina (sk) · Slovensko · EUR. Vykanie (bežné v slovenských e-shopoch), "vy" s malým písmenom.
# Číslovky: "nouns", "guitars", "storesWord", "many" sú v genitíve pl. ("1 234 gitár", "12 z 345 gitár",
# "Týmto filtrom zodpovedá 0 gitár"). js "store"/"stores" = nominatív ("1 obchod" / "3 obchody"; pri 5+ by bolo "obchodov").
# "store"/"stores" na najvyššej úrovni používa len "desc" ("v {n} {stores}"), preto sú v lokáli (obchode/obchodoch).

MONEY_NOTE = ("EUR, slovenský zápis: medzera (nezlomiteľná) ako oddeľovač tisícov, desatinná "
              "čiarka, symbol za sumou: '1 299 €', '1 299,50 €' (t. j. ako francúzsky/portugalský formát v money()).")

KINDS_LANG = {"electrica": "elektricke-gitary", "acustica": "akusticke-gitary", "clasica": "klasicke-gitary",
              "pack": "gitarove-sety", "bajo": "basgitary", "ampli": "zosilnovace", "pedal": "gitarove-efekty",
              "teclado": "klavesy", "micro": "mikrofony", "estuche": "puzdra-obaly", "varios": "prislusenstvo"}

PACK_LANG = ("Gitarové sety", "Sety", "Hľadať v setoch: model, značka, so zosilňovačom…", "setov",
             {"Eléctrica": "Elektrická gitara", "Acústica": "Akustická gitara"})

T_LANG = {
    "tagline": "gitary za najlepšiu cenu", "homeLabel": "guitle, úvodná stránka",
    "homeTitle": "guitle · porovnávač cien gitár",
    "homeDesc": "guitle porovnáva ceny gitár: elektrických, akustických aj klasických v obchodoch, ktoré predávajú na Slovensku, "
                "s históriou ceny každého modelu.",
    "h1": "Vaša gitara <span>za najlepšiu cenu</span><small>Porovnávač cien gitár</small>",
    "searchPh": "Hľadať: strat, les paul, yamaha, ibanez…", "searchBtn": "Hľadať", "searchLabel": "Hľadať gitaru",
    "guitars": "gitár", "storesWord": "obchodov", "catalog": "Katalóg",
    "dealsH": "Najväčšie cenové rozdiely medzi obchodmi", "dealsBadge": "−{p} % oproti najdrahšiemu",
    "catsH": "Prehľadávať podľa kategórie", "soon": "už čoskoro", "storesH": "Obchody, ktoré porovnávame",
    "howH": "Ako to funguje",
    "steps": ["Každý deň kontrolujeme cenu, dostupnosť a fotku každej gitary v obchodoch, ktoré predávajú na Slovensku.",
              "Ukladáme históriu cien, aby ste videli, či je cena naozaj dobrá, alebo býva zvyčajne nižšia.",
              "Ak chcete, pošleme vám e-mail, keď cena klesne."],
    "affiliate": "Niektoré odkazy na obchody sú affiliate odkazy: ak nakúpite, guitle môže získať províziu – bez ďalších nákladov pre vás.",
    "legal": "Právne informácie", "privacy": "Ochrana súkromia", "cookies": "Cookies", "otherCountries": "guitle v ďalších krajinách:",
    "updated": "Údaje aktualizované {d}", "home": "Úvod",
    "kinds": {"electrica": ("Elektrické gitary", "Elektrické", "Hľadať v elektrických gitarách: model, značka, farba…"),
              "acustica": ("Akustické gitary", "Akustické", "Hľadať v akustických gitarách: model, značka, drevo…"),
              "clasica": ("Klasické gitary", "Klasické", "Hľadať v klasických gitarách: model, značka, flamenco…"),
              "bajo": ("Elektrické a akustické basgitary", "Basgitary", "Hľadať v basgitarách: model, značka, päťstrunová…"),
              "ampli": ("Gitarové a basové zosilňovače", "Zosilňovače", "Hľadať v zosilňovačoch: model, značka, kombo, hlava…"),
              "pedal": ("Gitarové efekty", "Efekty", "Hľadať v efektoch: model, značka, typ efektu…"),
              "teclado": ("Klávesy a digitálne piana", "Klávesy", "Hľadať v klávesoch: model, značka…"),
              "micro": ("Mikrofóny", "Mikrofóny", "Hľadať v mikrofónoch: model, značka, typ…"),
              "estuche": ("Puzdrá a obaly", "Puzdrá", "Hľadať v puzdrách a obaloch: model, značka…"),
              "varios": ("Gitarové príslušenstvo", "Príslušenstvo", "Hľadať v príslušenstve: struny, trsátka, popruhy, káble…")},
    # Čo sa počíta v každej kategórii (úvod a zoznam) – genitív pl.
    "nouns": {"bajo": "basgitár", "ampli": "zosilňovačov", "pedal": "efektov", "teclado": "klávesov", "micro": "mikrofónov",
              "estuche": "puzdier", "varios": "položiek"},
    "allWord": "produktov",
    "anyPrice": "Ľubovoľná cena", "upTo": "Do {v}", "over": "Nad {v}", "brandLabel": "Značka", "priceLabel": "Cena",
    "showLabel": "Zobraziť", "showAll": "Všetko", "showMulti": "Vo viacerých obchodoch", "showStock": "Na sklade",
    "showLow": "Za najnižšiu cenu", "showLh": "Len pre ľavákov", "loading": "Načítavame katalóg…", "sortLabel": "Zoradiť",
    "sorts": ["Najviac obchodov", "Najnižšia cena", "Najvyššia cena", "Najväčšia úspora medzi obchodmi", "Názov"],
    "moreBtn": "Zobraziť ďalšie", "sections": "Sekcie", "searchAria": "Hľadať",
    "bestPrice": "najlepšia cena", "inStock": "na sklade", "noStock": "nie je na sklade", "goLong": "Do obchodu", "goShort": "Kúpiť",
    "store": "obchode", "stores": "obchodoch", "lh": "pre ľavákov", "storesH3": "Obchody", "historyH3": "Vývoj ceny",
    "amazon": "", "titleFrom": "{name}: cena od {price} {where}", "inN": "v {n} obchodoch", "inS": "v obchode {s}",
    "whereMany": "v obchode {s} · v {n} obchodoch", "whereDiff": ", rozdiel až {d}",
    "desc": "{name} od {price} v obchode {s}. Porovnajte cenu v {n} {stores} ({list}) a pozrite si vývoj ceny, aby ste vedeli, "
            "či je teraz vhodná chvíľa na kúpu.",
    "alertTitle": "Stráženie ceny", "alertWait": "Moment…", "alertSaving": "Ukladáme vašu odpoveď.",
    "alertGo": "Prejsť na guitle", "alertBad": ["Neplatný odkaz", "Skopírujte celý odkaz z e-mailu a skúste to znova."],
    "alertDone": ["Stráženie ceny potvrdené!", "Napíšeme vám, hneď ako cena klesne. Každý e-mail obsahuje odkaz na odhlásenie."],
    "alertGone": ["Stráženie ceny zrušené", "K tomuto stráženiu vám už nebudú chodiť e-maily. Vašu adresu sme vymazali z nášho zoznamu."],
    "alertMissing": ["Stráženie ceny sa nenašlo", "Možno už bolo potvrdené alebo zrušené, alebo uplynulo viac ako 7 dní bez "
                                                   "potvrdenia. Potrebujete pomoc? Napíšte nám na hola@guitle.com."],
    "js": {"loadErr": "Katalóg sa nepodarilo načítať.", "allBrands": "Všetky značky", "all": "Všetko", "low": "Najnižšia",
           "save": "Ušetríte {v}", "lh": "pre ľavákov", "store": "obchod", "stores": "obchody",
           "empty": "Týmto filtrom zodpovedá 0 {many}.", "more": "Zobraziť ďalšie (zostáva {n})",
           "meta": "{a} z {b} {many} · {m} na porovnanie vo viacerých obchodoch · aktualizované {d}", "best": "najlepšia cena",
           "inStock": "na sklade", "noStock": "nie je na sklade", "goLong": "Do obchodu", "goShort": "Kúpiť", "close": "Zavrieť",
           "inAt": "v obchode {s}", "saveMax": " · až o {v} lacnejšie ako v najdrahšom", "atLow": "Za najnižšiu zaznamenanú cenu",
           "lowTag": "Najnižšia cena: {v}", "storesH": "Obchody", "evolH": "Vývoj ceny",
           "histErr": "Históriu cien sa nepodarilo načítať.", "histSoon": "História cien sa doplní počas nasledujúcich dní.",
           "many": "gitár",
           "types": {"ST": "Typ ST", "T": "Typ T", "Semihueca": "Semiakustické", "Offset / Retro": "Offset / Retro", "Moderna / Metal": "Moderné / Metal",
                     "Otras": "Ostatné", "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12-strunové",
                     "Tamaño reducido": "Zmenšené", "Clásica": "Klasické", "Flamenca": "Flamenco",
                     "Electroclásica": "Elektroklasické",
                     "4 cuerdas": "4-strunové", "5 cuerdas": "5-strunové", "6 cuerdas o más": "6-strunové a viac",
                     "Acústico": "Akustické basgitary", "Fretless": "Fretless", "Escala corta": "Krátka menzúra", "Combo": "Kombá",
                     "Cabezal": "Hlavy", "Pantalla": "Reproboxy", "Para bajo": "Pre basgitaru", "Para acústica": "Pre akustickú gitaru",
                     "De auriculares y portátil": "Slúchadlové a mini zosilňovače", "Para eléctrica": "Pre elektrickú gitaru",
                     "Para clásica": "Pre klasickú gitaru", "Overdrive y distorsión": "Overdrive a distortion",
                     "Modulación": "Modulácia", "Compresor": "Kompresor", "Wah y volumen": "Wah a volume",
                     "Octavador y pitch": "Oktávery a pitch", "Ecualizador": "Ekvalizér", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Syntetizátory", "Afinador": "Ladička", "Multiefectos": "Multiefekty",
                     "Reverb": "Dozvuk", "Piano digital": "Digitálne piana", "Teclado portátil": "Keyboardy",
                     "Piano de escenario": "Stage piana", "Controlador MIDI": "MIDI kontroléry", "Piano acústico": "Akustické piana",
                     "Dinámico": "Dynamické", "Condensador": "Kondenzátorové", "Inalámbrico": "Bezdrôtové",
                     "Para instrumento": "Nástrojové", "De cinta": "Páskové", "Cuerdas": "Struny",
                     "Púas": "Trsátka", "Correas": "Popruhy", "Cables": "Káble", "Afinadores": "Ladičky",
                     "Cejillas": "Kapodastre", "Soportes": "Stojany", "Pastillas": "Snímače", "Recambios": "Náhradné diely",
                     "Mantenimiento": "Údržba"},
           "wait": "Tento model sledujeme počas {n} {days}", "day": "dňa", "days": "dní",
           "waitSub": "Hodnotenie bude spoľahlivejšie po niekoľkých týždňoch histórie.",
           "min": "Najnižšia zaznamenaná cena", "minSub": "Lacnejšie sme ho ešte nevideli.",
           "minBelow": " O {p} % pod priemerom za 30 dní.",
           "good": "Vhodná chvíľa: o {p} % pod priemernou cenou", "goodSub": "Priemer za posledných 30 dní: {avg}.",
           "bad": "Teraz je o {p} % drahší ako zvyčajne",
           "badSub": "Ak sa vám neponáhľa, počkajte: priemer za 30 dní je {avg} a najnižšia cena {min}.",
           "normal": "Bežná cena", "normalSub": "Zodpovedá priemeru za 30 dní ({avg}). Najnižšia zaznamenaná: {min}.",
           "today": "cena dnes", "lowest": "najnižšia ({d})", "highest": "najvyššia", "avg": "priemer za {n} dní",
           "since": "Sledujeme od {d}", "noHist": "Zatiaľ bez histórie cien.", "pvp": "Odporúčaná cena", "bestLine": "Najlepšia cena",
           "alertOpen": "Dajte mi vedieť, keď cena klesne", "emailPh": "meno@priklad.sk", "emailLabel": "Váš e-mail",
           "targetPh": "Max. cena (nepovinné)", "targetLabel": "Cieľová cena v eurách", "alertBtn": "Strážiť cenu",
           "alertLegal": "Zadarmo a bez registrácie. Kliknutím na „Strážiť cenu“ súhlasíte so "
                         "<a href=\"/sk/legal.html#sukromie\">zásadami ochrany súkromia</a>: váš e-mail použijeme len na toto "
                         "stráženie a odhlásiť sa môžete jedným kliknutím.",
           "alertOk": "<b>Hotovo!</b> O pár minút vám na {email} príde e-mail na potvrdenie stráženia "
                      "(pozrite sa aj do priečinka so spamom).",
           "alertErr": "Stráženie sa nepodarilo uložiť. Skontrolujte e-mailovú adresu a skúste to znova."},
    "mail": {"tagline": "gitary za najlepšiu cenu",
             "footer": "guitle každý deň porovnáva ceny hudobnín. Tento e-mail dostávate, pretože ste si na guitle.com "
                       "nastavili stráženie ceny. Prevádzkovateľ údajov: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Ochrana súkromia", "confirmSubject": "Potvrďte stráženie ceny na guitle",
             "confirmTitle": "Potvrďte stráženie ceny", "asked": "Požiadali ste nás o upozornenie, keď cena klesne{target}:",
             "below": " pod <b>{v}</b>", "confirmAsk": "Potvrďte, prosím, že chcete upozornenia dostávať na túto adresu:",
             "confirmBtn": "Potvrdiť stráženie",
             "notYou": "Ak ste to neboli vy, nerobte nič: nepotvrdené stráženia sa po 7 dňoch automaticky vymažú.",
             "dropSubject": "Cena klesla: {name} teraz za {price}", "dropTitle": "Cena klesla!", "nowAt": "v obchode {s} · predtým {v}",
             "seeAll": "Zobraziť ceny vo všetkých obchodoch",
             "check": "Ceny sa menia každý deň: pred kúpou si ich overte v obchode. Už vás to nezaujíma?",
             "stop": "Zrušiť toto stráženie"},
}

# Dozorný orgán na Slovensku: Úrad na ochranu osobných údajov Slovenskej republiky, dataprotection.gov.sk.
# Fráza pre prípadný legal_replace: "alebo na Úrade na ochranu osobných údajov Slovenskej republiky".
LEGAL_LANG = ("Právne informácie a ochrana súkromia", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Právne informácie a ochrana súkromia</h1>
<p class="muted">Stav k 28. októbru 2026. Toto je preklad; v prípade pochybností platí <a href="/legal.html">španielske znenie</a>.</p>

<h2 id="aviso">Právne informácie</h2>
<p>Prevádzkovateľom tejto webovej stránky je <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Španielsko
(španielske daňové identifikačné číslo NIF 17747339X), kontakt
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, web guitle.com. Činnosť: porovnávanie cien hudobných nástrojov a affiliate reklama.
Hosting: GitHub Pages (GitHub, Inc.).</p>

<h2 id="podmienky">Podmienky používania</h2>
<p>guitle je porovnávač cien a sám nič nepredáva. Zobrazujeme ceny, ktoré obchody zverejňujú na svojich weboch, a odkazujeme na ne, aby ste
nakúpili priamo v obchode. Za nákup, doručenie, záruku a vrátenie tovaru zodpovedá príslušný obchod.</p>
<ul>
<li><b>Ceny sú orientačné.</b> Ceny pravidelne kontrolujeme, môžu sa však kedykoľvek zmeniť. Platí vždy cena, ktorú obchod zobrazí pri objednávke.</li>
<li><b>Bez záruky správnosti.</b> Dbáme na správnosť produktov, cien a dostupnosti, chyby sa však môžu stať. Ak nejakú nájdete, napíšte nám.</li>
<li><b>Ochranné známky a obrázky.</b> Ochranné známky, názvy produktov a obrázky patria ich vlastníkom a slúžia len na označenie produktov.</li>
<li><b>Obsah guitle.</b> Dizajn, logo, texty a súbory údajov guitle patria prevádzkovateľovi. Hromadné kopírovanie alebo komerčné využitie bez povolenia nie je dovolené.</li>
</ul>

<h2 id="affiliate">Affiliate odkazy</h2>
<p>Niektoré odkazy na obchody sú affiliate odkazy: ak po kliknutí nakúpite, obchod môže guitle vyplatiť malú províziu. Vy zaplatíte rovnakú
cenu. Provízie neovplyvňujú poradie: obchody sú vždy zoradené podľa ceny, od najlacnejšieho.</p>

<h2 id="sukromie">Zásady ochrany súkromia</h2>
<p>guitle na používanie webu nepožaduje žiadne osobné údaje: žiadna registrácia, žiadny newsletter, žiadne analytické ani reklamné nástroje, ktoré by vás
sledovali. Návštevy počítame len anonymne, a ak si nastavíte stráženie ceny, uložíme na ten účel vašu e-mailovú adresu.</p>
<ul>
<li><b>Stráženie ceny.</b> Ak chcete dostať upozornenie, keď cena produktu klesne, uložíme vašu e-mailovú adresu, produkt, jeho cenu v daný deň
a prípadne vašu cieľovú cenu. Použijeme ich len na odoslanie potvrdzovacieho e-mailu a upozornení k tomuto produktu, nikdy na marketing,
a nikomu ich neposkytujeme. Právny základ: váš súhlas (čl. 6 ods. 1 písm. a) GDPR), ktorý udelíte vytvorením stráženia a potvrdením e-mailu.
Údaje ukladáme v Google Cloud Firestore (Google Ireland Ltd., server v Madride) a e-maily posielame z našej schránky hola@guitle.com
(DonDominio, Španielsko). Nepotvrdené stráženia mažeme po 7 dňoch; potvrdené uchovávame, kým sa neodhlásite odkazom v ktoromkoľvek e-maile
(stráženie sa okamžite vymaže), alebo kým nás nepožiadate o vymazanie.</li>
<li><b>Nastavenia vo vašom prehliadači.</b> Filtre a zvolené zobrazenie sa ukladajú do lokálneho úložiska vášho prehliadača (localStorage) a neodosielajú sa na žiadny server.</li>
<li><b>Hosting.</b> Web beží na GitHub Pages (GitHub, Inc.). Ako každý webový server môže GitHub z technických a bezpečnostných dôvodov
zaznamenávať IP adresu každej návštevy. GitHub je zapojený do rámca EU-US Data Privacy Framework.</li>
<li><b>Počítadlo návštev.</b> Každá stránka zvýši anonymné počítadlo o 1: deň, zobrazená stránka, web, z ktorého prichádzate (napr. google.com),
čo zadáte do vyhľadávania v katalógu, a ak prejdete do obchodu, jeho názov. Žiadne cookies, žiadna IP adresa, nič, čo by vás identifikovalo.
Počítadlá sú uložené v Google Cloud Firestore (Google Ireland Ltd.) na serveri v Európskej únii (Madrid).</li>
<li><b>Žiadne ďalšie požiadavky na tretie strany.</b> Písma, grafy aj fotografie produktov sa načítavajú z guitle.com.</li>
<li><b>Prechod do obchodu.</b> Kliknutím na odkaz do obchodu opúšťate guitle a platia zásady ochrany súkromia daného obchodu.</li>
</ul>
<p><b>Vaše práva.</b> Svoje práva na prístup, opravu, vymazanie, namietanie, obmedzenie spracúvania a prenosnosť údajov môžete uplatniť e-mailom na
<a href="mailto:hola@guitle.com">hola@guitle.com</a>. Môžete tiež podať sťažnosť dozornému orgánu pre ochranu osobných údajov, napríklad na
Agencia Española de Protección de Datos alebo na Úrade na ochranu osobných údajov Slovenskej republiky. Prevádzkovateľ: osoba uvedená v právnych informáciách.</p>

<h2 id="cookies">Cookies</h2>
<p>guitle nepoužíva cookies, vlastné ani tretích strán – preto nevidíte žiadnu cookie lištu. Na zapamätanie vašich nastavení používame len
lokálne úložisko prehliadača. Obchody, na ktoré odkazujeme, môžu na svojich weboch používať vlastné cookies.</p>
""")
