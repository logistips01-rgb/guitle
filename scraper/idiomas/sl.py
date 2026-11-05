# Slovenščina (sl) · Slovenija · EUR. Bralca tikamo (kot večina glasbenih spletnih trgovin).
# Števniki: "nouns", "guitars", "storesWord", "many", "allWord" so v rodilniku množine („1.234 kitar”, „12 od 345 kitar”,
# „Ni kitar …”). "inN"/"desc" uporabljata mestnik množine („v 3 trgovinah”), pravilen za vsak n ≥ 3 (za 2 bi bilo „dveh”).
# js "stores" (kartica: „{n} trgovine”) je oblika za 3–4; za 2 bi bilo „trgovini”, za 5+ „trgovin”.
# js "wait": dvojina („2 dneva”) se ne da izraziti z day/days, zato vrstilni števnik „{n}. dan” brez {days}.
# Sidro razdelka o zasebnosti: "zasebnost".

MONEY_NOTE = ("Slovenian style: dot as thousands separator, comma for decimals, symbol after the amount with a "
              "non-breaking space: '1.299 €', '1.299,50 €'. intl.money() only uses the dot for lang 'de', 'it', 'es': "
              "add 'sl' (otherwise it would print '1 299 €').")

KINDS_LANG = {"electrica": "elektricne-kitare", "acustica": "akusticne-kitare", "clasica": "klasicne-kitare",
              "pack": "kitarski-kompleti", "bajo": "bas-kitare", "ampli": "ojacevalci", "pedal": "efektni-pedali",
              "teclado": "klaviature", "micro": "mikrofoni", "estuche": "kovcki-torbe", "varios": "dodatki"}

PACK_LANG = ("Kitarski kompleti", "Kompleti", "Išči med kompleti: model, znamka, z ojačevalcem …", "kompletov",
             {"Eléctrica": "Električna", "Acústica": "Akustična"})

T_LANG = {
    "tagline": "kitare po najboljši ceni", "homeLabel": "guitle, domov",
    "homeTitle": "guitle · primerjava cen kitar",
    "homeDesc": "guitle primerja cene kitar: električne, akustične in klasične kitare v trgovinah, ki dostavljajo v "
                "Slovenijo, z zgodovino cen vsakega modela.",
    "h1": "Tvoja kitara, <span>po najboljši ceni</span><small>Primerjava cen kitar</small>",
    "searchPh": "Išči: strat, les paul, yamaha, ibanez …", "searchBtn": "Išči", "searchLabel": "Poišči kitaro",
    "guitars": "kitar", "storesWord": "trgovin", "catalog": "Katalog",
    "dealsH": "Največje razlike v cenah med trgovinami", "dealsBadge": "−{p} % glede na najdražjo",
    "catsH": "Brskaj po kategorijah", "soon": "kmalu", "storesH": "Trgovine, ki jih primerjamo",
    "howH": "Kako deluje",
    "steps": ["Vsak dan preverimo ceno, zalogo in fotografijo vsake kitare v trgovinah, ki dostavljajo v Slovenijo.",
              "Hranimo zgodovino cen, da vidiš, ali je cena res dobra ali je običajno nižja.",
              "Če želiš, ti pošljemo e-pošto, ko cena pade."],
    "affiliate": "Nekatere povezave do trgovin so partnerske: če kupiš, lahko guitle prejme provizijo, brez dodatnih stroškov zate.",
    "legal": "Pravno obvestilo", "privacy": "Zasebnost", "cookies": "Piškotki", "otherCountries": "guitle v drugih državah:",
    "updated": "Podatki posodobljeni {d}", "home": "Domov",
    "kinds": {"electrica": ("Električne kitare", "Električne", "Išči med električnimi kitarami: model, znamka, barva …"),
              "acustica": ("Akustične kitare", "Akustične", "Išči med akustičnimi kitarami: model, znamka, les …"),
              "clasica": ("Klasične kitare", "Klasične", "Išči med klasičnimi kitarami: model, znamka, flamenko …"),
              "bajo": ("Električne in akustične bas kitare", "Bas kitare", "Išči med bas kitarami: model, znamka, 5 strun …"),
              "ampli": ("Ojačevalci za kitaro in bas", "Ojačevalci", "Išči med ojačevalci: model, znamka, kombo, glava …"),
              "pedal": ("Efektni pedali", "Efekti", "Išči med efektnimi pedali: model, znamka, efekt …"),
              "teclado": ("Klaviature in digitalni klavirji", "Klaviature", "Išči med klaviaturami: model, znamka …"),
              "micro": ("Mikrofoni", "Mikrofoni", "Išči med mikrofoni: model, znamka, vrsta …"),
              "estuche": ("Kovčki in torbe", "Kovčki", "Išči med kovčki in torbami: model, znamka …"),
              "varios": ("Kitarska dodatna oprema", "Dodatki", "Išči med dodatki: strune, trzalice, pasovi, kabli …")},
    # Kaj štejemo v vsaki kategoriji (domača stran in seznam) in, če niso samo kitare, skupaj (rodilnik množine).
    "nouns": {"bajo": "bas kitar", "ampli": "ojačevalcev", "pedal": "pedalov", "teclado": "klaviatur", "micro": "mikrofonov",
              "estuche": "kovčkov in torb", "varios": "izdelkov"},
    "allWord": "izdelkov",
    "anyPrice": "Katera koli cena", "upTo": "Do {v}", "over": "Nad {v}", "brandLabel": "Znamka", "priceLabel": "Cena",
    "showLabel": "Prikaži", "showAll": "Vse", "showMulti": "V več trgovinah", "showStock": "Na zalogi",
    "showLow": "Po najnižji ceni", "showLh": "Samo za levičarje", "loading": "Nalaganje kataloga …", "sortLabel": "Razvrsti",
    "sorts": ["Največ trgovin", "Najnižja cena", "Najvišja cena", "Največji prihranek med trgovinami", "Ime"],
    "moreBtn": "Prikaži več", "sections": "Razdelki", "searchAria": "Išči",
    "bestPrice": "najboljša cena", "inStock": "na zalogi", "noStock": "ni na zalogi", "goLong": "V trgovino", "goShort": "Pojdi",
    "store": "trgovini", "stores": "trgovinah", "lh": "za levičarje", "storesH3": "Trgovine", "historyH3": "Zgodovina cen",
    "amazon": "", "titleFrom": "{name}: cena od {price} {where}", "inN": "v {n} trgovinah", "inS": "v trgovini {s}",
    "whereMany": "v trgovini {s} · trgovin: {n}", "whereDiff": ", razlika do {d}",
    "desc": "{name} od {price} v trgovini {s}. Primerjaj ceno v {n} {stores} ({list}) in si oglej zgodovino cen, da veš, ali je "
            "zdaj pravi trenutek za nakup.",
    "alertTitle": "Cenovno obvestilo", "alertWait": "Trenutek …", "alertSaving": "Shranjujemo tvoj odgovor.",
    "alertGo": "Na guitle", "alertBad": ["Neveljavna povezava", "Kopiraj celotno povezavo iz e-pošte in poskusi znova."],
    "alertDone": ["Obvestilo potrjeno!", "Pisali ti bomo takoj, ko cena pade. Vsako sporočilo vsebuje povezavo za odjavo."],
    "alertGone": ["Obvestilo izbrisano", "Za to obvestilo ne boš več prejemal sporočil. Tvoj naslov smo izbrisali s seznama."],
    "alertMissing": ["Obvestila ni mogoče najti", "Morda je bilo že potrjeno ali izbrisano ali pa je minilo več kot 7 dni brez "
                                                  "potrditve. Potrebuješ pomoč? Piši nam na hola@guitle.com."],
    "js": {"loadErr": "Kataloga ni bilo mogoče naložiti.", "allBrands": "Vse znamke", "all": "Vse", "low": "Najnižja",
           "save": "Prihrani {v}", "lh": "za levičarje", "store": "trgovina", "stores": "trgovine",
           "empty": "Ni {many} s temi filtri.", "more": "Prikaži več (še {n})",
           "meta": "{a} od {b} {many} · {m} primerljivih v več trgovinah · posodobljeno {d}", "best": "najboljša cena",
           "inStock": "na zalogi", "noStock": "ni na zalogi", "goLong": "V trgovino", "goShort": "Pojdi", "close": "Zapri",
           "inAt": "v trgovini {s}", "saveMax": " · do {v} ceneje kot v najdražji", "atLow": "Po najnižji zabeleženi ceni",
           "lowTag": "Najnižja: {v}", "storesH": "Trgovine", "evolH": "Gibanje cene",
           "histErr": "Zgodovine cen ni bilo mogoče naložiti.", "histSoon": "Zgodovina cen se bo dopolnjevala v prihodnjih dneh.",
           "many": "kitar",
           "types": {"ST": "Oblika ST", "T": "Oblika T", "Semihueca": "Polakustične", "Offset / Retro": "Offset / Retro",
                     "Moderna / Metal": "Moderne / Metal", "Otras": "Drugo", "Auditorio / Concierto": "Auditorium / Concert",
                     "12 cuerdas": "12 strun", "Tamaño reducido": "Manjše velikosti", "Clásica": "Klasične",
                     "Flamenca": "Flamenko", "Electroclásica": "Elektroklasične",
                     "4 cuerdas": "4 strune", "5 cuerdas": "5 strun", "6 cuerdas o más": "6 strun in več",
                     "Acústico": "Akustični bas", "Fretless": "Fretless", "Escala corta": "Kratka menzura", "Combo": "Kombo ojačevalci",
                     "Cabezal": "Glave", "Pantalla": "Zvočniške omarice", "Para bajo": "Za bas", "Para acústica": "Za akustično kitaro",
                     "De auriculares y portátil": "Mini in za slušalke", "Para eléctrica": "Za električno kitaro",
                     "Para clásica": "Za klasično kitaro", "Overdrive y distorsión": "Overdrive in distorzija",
                     "Modulación": "Modulacija", "Compresor": "Kompresorji", "Wah y volumen": "Wah in glasnost",
                     "Octavador y pitch": "Oktaver in pitch", "Ecualizador": "Izenačevalniki (EQ)", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintetizatorji", "Afinador": "Uglaševalci", "Multiefectos": "Multiefekti",
                     "Reverb": "Reverb", "Piano digital": "Digitalni klavirji", "Teclado portátil": "Prenosne klaviature",
                     "Piano de escenario": "Odrski klavirji", "Controlador MIDI": "MIDI krmilniki", "Piano acústico": "Akustični klavirji",
                     "Dinámico": "Dinamični", "Condensador": "Kondenzatorski", "Inalámbrico": "Brezžični",
                     "Para instrumento": "Za instrumente", "De cinta": "Trakasti", "Cuerdas": "Strune",
                     "Púas": "Trzalice", "Correas": "Pasovi", "Cables": "Kabli", "Afinadores": "Uglaševalci",
                     "Cejillas": "Kapodastri", "Soportes": "Stojala", "Pastillas": "Magneti", "Recambios": "Rezervni deli",
                     "Mantenimiento": "Vzdrževanje"},
           "wait": "Ta model spremljamo šele {n}. dan", "day": "dan", "days": "dni",
           "waitSub": "Ocena postane zanesljivejša po nekaj tednih zgodovine cen.",
           "min": "Najnižja zabeležena cena", "minSub": "Nižje cene še nismo videli.",
           "minBelow": " {p} % pod 30-dnevnim povprečjem.",
           "good": "Dober trenutek: {p} % pod povprečno ceno", "goodSub": "Povprečje zadnjih 30 dni: {avg}.",
           "bad": "Cena je trenutno {p} % višja kot običajno",
           "badSub": "Če se ti ne mudi, počakaj: 30-dnevno povprečje je {avg}, najnižja cena pa {min}.",
           "normal": "Običajna cena", "normalSub": "V skladu s 30-dnevnim povprečjem ({avg}). Najnižja zabeležena: {min}.",
           "today": "cena danes", "lowest": "najnižja ({d})", "highest": "najvišja", "avg": "povprečje {n} dni",
           "since": "Spremljamo od {d}", "noHist": "Zgodovine cen še ni.", "pvp": "Priporočena cena", "bestLine": "Najboljša cena",
           "alertOpen": "Obvesti me, ko cena pade", "emailPh": "ti@primer.si", "emailLabel": "Tvoj e-poštni naslov",
           "targetPh": "Najv. cena (neobvezno)", "targetLabel": "Želena cena v evrih", "alertBtn": "Obvesti me",
           "alertLegal": "Brezplačno in brez registracije. S klikom na »Obvesti me« sprejemaš "
                         "<a href=\"/si/legal.html#zasebnost\">pravilnik o zasebnosti</a>: tvoj e-poštni naslov uporabimo samo za to "
                         "obvestilo, odjaviš pa se z enim klikom.",
           "alertOk": "<b>Končano!</b> Čez nekaj minut boš na {email} prejel sporočilo za potrditev obvestila (preveri tudi mapo z neželeno pošto).",
           "alertErr": "Obvestila ni bilo mogoče shraniti. Preveri e-poštni naslov in poskusi znova."},
    "mail": {"tagline": "kitare po najboljši ceni",
             "footer": "guitle vsak dan primerja cene glasbenih trgovin. To sporočilo prejemaš, ker si na guitle.com zahteval "
                       "cenovno obvestilo. Upravljavec: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Zasebnost", "confirmSubject": "Potrdi svoje cenovno obvestilo guitle",
             "confirmTitle": "Potrdi cenovno obvestilo", "asked": "Želiš, da te obvestimo, ko cena pade{target}:",
             "below": " pod <b>{v}</b>", "confirmAsk": "Potrdi, da želiš prejemati obvestilo na ta naslov:",
             "confirmBtn": "Potrdi obvestilo",
             "notYou": "Če to nisi bil ti, ne naredi ničesar: nepotrjena obvestila se samodejno izbrišejo po 7 dneh.",
             "dropSubject": "Cena je padla: {name} zdaj {price}", "dropTitle": "Cena je padla!", "nowAt": "v trgovini {s} · prej {v}",
             "seeAll": "Oglej si cene v vseh trgovinah",
             "check": "Cene se spreminjajo vsak dan: pred nakupom jih preveri v trgovini. Te ne zanima več?",
             "stop": "Prekliči to obvestilo"},
}

# Nadzorni organ v Sloveniji: Informacijski pooblaščenec (IP), ip-rs.si.
# Izraz za morebitni legal_replace: "ali pri Informacijskem pooblaščencu (IP)".
LEGAL_LANG = ("Pravno obvestilo in zasebnost", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Pravno obvestilo in zasebnost</h1>
<p class="muted">Zadnja posodobitev: 28. oktobra 2026. To je prevod; v primeru dvoma velja <a href="/legal.html">španska različica</a>.</p>

<h2 id="aviso">Pravno obvestilo</h2>
<p>To spletno mesto upravlja <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Španija
(španska davčna številka NIF 17747339X), kontakt <a href="mailto:hola@guitle.com">hola@guitle.com</a>, spletno mesto guitle.com.
Dejavnost: primerjava cen glasbil in partnersko oglaševanje. Gostovanje: GitHub Pages (GitHub, Inc.).</p>

<h2 id="pogoji">Pogoji uporabe</h2>
<p>guitle je primerjalnik cen in ničesar ne prodaja. Prikazujemo cene, ki jih trgovine objavljajo na svojih spletnih mestih, in te usmerimo tja,
da kupiš neposredno v trgovini. Za nakup, dostavo, garancijo in vračila je odgovorna posamezna trgovina.</p>
<ul>
<li><b>Cene so informativne.</b> Cene redno preverjamo, vendar se lahko kadar koli spremenijo. Vedno velja cena, ki jo trgovina prikaže ob naročilu.</li>
<li><b>Brez jamstva za točnost.</b> Trudimo se, da so izdelki, cene in zaloge pravilni, vendar so napake mogoče. Če jo opaziš, nam piši.</li>
<li><b>Blagovne znamke in slike.</b> Blagovne znamke, imena izdelkov in slike pripadajo njihovim lastnikom in se uporabljajo samo za prepoznavanje izdelkov.</li>
<li><b>Vsebina guitle.</b> Oblikovanje, logotip, besedila in zbirke podatkov guitle so last njegovega lastnika. Množično kopiranje ali komercialna uporaba brez dovoljenja nista dovoljena.</li>
</ul>

<h2 id="affiliate">Partnerske povezave</h2>
<p>Nekatere povezave do trgovin so partnerske: če po kliku kupiš, lahko trgovina guitlu plača majhno provizijo. Zate se cena ne spremeni.
Provizije ne vplivajo na vrstni red: trgovine so vedno razvrščene po ceni, od najcenejše naprej.</p>

<h2 id="zasebnost">Pravilnik o zasebnosti</h2>
<p>guitle za uporabo spletnega mesta ne zahteva osebnih podatkov: brez registracije, brez e-novic, brez orodij za analitiko ali oglaševanje,
ki bi te sledila. Obiske štejemo samo anonimno, in če zahtevaš cenovno obvestilo, za to obvestilo hranimo tvoj e-poštni naslov.</p>
<ul>
<li><b>Cenovna obvestila.</b> Če želiš, da te obvestimo, ko cena izdelka pade, shranimo tvoj e-poštni naslov, izdelek, njegovo ceno na ta dan in,
če jo navedeš, želeno ceno. Uporabimo jih samo za potrditveno sporočilo in obvestila o tem izdelku, nikoli za trženje, in jih ne posredujemo
nikomur. Pravna podlaga: tvoja privolitev (točka (a) prvega odstavka 6. člena Splošne uredbe o varstvu podatkov, GDPR), ki jo daš, ko zahtevaš
obvestilo in potrdiš e-poštni naslov. Shranjeni so v Google Cloud Firestore (Google Ireland Ltd., strežnik v Madridu), sporočila pa pošiljamo iz
našega predala hola@guitle.com (DonDominio, Španija). Nepotrjena obvestila izbrišemo po 7 dneh; potrjena hranimo, dokler se ne odjaviš prek
povezave v vsakem sporočilu (obvestilo se takoj izbriše) ali dokler nas ne prosiš za izbris.</li>
<li><b>Nastavitve v tvojem brskalniku.</b> Filtri ali izbrani pogled se shranijo v lokalni shrambi tvojega brskalnika (localStorage) in se nikoli ne pošljejo na noben strežnik.</li>
<li><b>Gostovanje.</b> Spletno mesto gostuje na GitHub Pages (GitHub, Inc.). Kot vsak spletni strežnik lahko GitHub iz tehničnih in varnostnih
razlogov beleži naslov IP vsakega obiska. GitHub je certificiran v okviru EU-US Data Privacy Framework.</li>
<li><b>Števec obiskov.</b> Vsaka stran anonimnemu števcu prišteje 1: dan, ogledano stran, spletno mesto, s katerega prihajaš (na primer google.com),
kar vpišeš v iskalnik kataloga, in, če klikneš do trgovine, njeno ime. Brez piškotkov, brez naslova IP, brez česar koli, kar bi te identificiralo.
Števci so shranjeni v Google Cloud Firestore (Google Ireland Ltd.) na strežniku v Evropski uniji (Madrid).</li>
<li><b>Brez drugih zahtev do tretjih oseb.</b> Pisave, grafi in fotografije izdelkov se nalagajo z guitle.com.</li>
<li><b>Ko greš v trgovino.</b> Ko klikneš do trgovine, zapustiš guitle in velja pravilnik o zasebnosti te trgovine.</li>
</ul>
<p><b>Tvoje pravice.</b> Pravice do dostopa, popravka, izbrisa, ugovora, omejitve obdelave in prenosljivosti lahko uveljavljaš s sporočilom na
<a href="mailto:hola@guitle.com">hola@guitle.com</a>. Pritožbo lahko vložiš tudi pri nadzornem organu za varstvo podatkov, na primer pri
Agencia Española de Protección de Datos ali pri nacionalnem nadzornem organu za varstvo osebnih podatkov. Upravljavec: lastnik, naveden v pravnem obvestilu.</p>

<h2 id="cookies">Piškotki</h2>
<p>guitle ne uporablja piškotkov, ne lastnih ne piškotkov tretjih oseb, zato ne vidiš pasice o piškotkih. Uporabljamo samo lokalno shrambo brskalnika,
da si zapomnimo tvoje nastavitve. Trgovine, do katerih vodijo povezave, lahko na svojih spletnih mestih uporabljajo lastne piškotke.</p>
""")
