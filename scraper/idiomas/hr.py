# Hrvatski (hr) · Hrvatska · EUR. Čitatelju se obraćamo s „ti” (kao većina glazbenih web-trgovina).
# Brojevi: "nouns", "guitars", "storesWord", "many", "allWord" su u genitivu množine („1.234 gitara”, „12 od 345 gitara”,
# „Nema gitara…”). "inN"/"desc" koriste lokativ množine („u 3 trgovinama”), ispravan za svaki n ≥ 2.
# js "stores" (kartica: „{n} trgovine”) je oblik za 2–4, najčešći slučaj; za 5+ bilo bi „trgovina”.
# Sidro odjeljka o privatnosti: "privatnost".

MONEY_NOTE = ("Croatian style (euro since 2023): dot as thousands separator, comma for decimals, symbol after the amount "
              "with a non-breaking space: '1.299 €', '1.299,50 €'. intl.money() only uses the dot for lang 'de', 'it', "
              "'es': add 'hr' (otherwise it would print '1 299 €').")

KINDS_LANG = {"electrica": "elektricne-gitare", "acustica": "akusticne-gitare", "clasica": "klasicne-gitare",
              "pack": "gitarski-setovi", "bajo": "bas-gitare", "ampli": "pojacala", "pedal": "efekt-pedale",
              "teclado": "klavijature", "micro": "mikrofoni", "estuche": "koferi-torbe", "varios": "pribor"}

PACK_LANG = ("Gitarski setovi", "Setovi", "Pretraži setove: model, marka, s pojačalom…", "setova",
             {"Eléctrica": "Električna", "Acústica": "Akustična"})

T_LANG = {
    "tagline": "gitare po najboljoj cijeni", "homeLabel": "guitle, početna",
    "homeTitle": "guitle · usporedba cijena gitara",
    "homeDesc": "guitle uspoređuje cijene gitara: električne, akustične i klasične gitare u trgovinama koje dostavljaju u "
                "Hrvatsku, uz povijest cijena svakog modela.",
    "h1": "Tvoja gitara, <span>po najboljoj cijeni</span><small>Usporedba cijena gitara</small>",
    "searchPh": "Traži: strat, les paul, yamaha, ibanez…", "searchBtn": "Traži", "searchLabel": "Traži gitaru",
    "guitars": "gitara", "storesWord": "trgovina", "catalog": "Katalog",
    "dealsH": "Najveće razlike u cijeni među trgovinama", "dealsBadge": "−{p} % u odnosu na najskuplju",
    "catsH": "Pregledaj po kategorijama", "soon": "uskoro", "storesH": "Trgovine koje uspoređujemo",
    "howH": "Kako funkcionira",
    "steps": ["Svaki dan provjeravamo cijenu, dostupnost i fotografiju svake gitare u trgovinama koje dostavljaju u Hrvatsku.",
              "Čuvamo povijest cijena kako bi vidio je li cijena zaista dobra ili je obično niža.",
              "Ako želiš, javit ćemo ti e-poštom kad cijena padne."],
    "affiliate": "Neke poveznice na trgovine su partnerske: ako kupiš, guitle može dobiti proviziju, bez dodatnog troška za tebe.",
    "legal": "Pravne informacije", "privacy": "Privatnost", "cookies": "Kolačići", "otherCountries": "guitle u drugim zemljama:",
    "updated": "Podaci ažurirani {d}", "home": "Početna",
    "kinds": {"electrica": ("Električne gitare", "Električne", "Pretraži električne gitare: model, marka, boja…"),
              "acustica": ("Akustične gitare", "Akustične", "Pretraži akustične gitare: model, marka, drvo…"),
              "clasica": ("Klasične gitare", "Klasične", "Pretraži klasične gitare: model, marka, flamenco…"),
              "bajo": ("Električne i akustične bas-gitare", "Bas-gitare", "Pretraži bas-gitare: model, marka, 5 žica…"),
              "ampli": ("Pojačala za gitaru i bas", "Pojačala", "Pretraži pojačala: model, marka, combo, glava…"),
              "pedal": ("Efekt pedale", "Efekti", "Pretraži efekt pedale: model, marka, efekt…"),
              "teclado": ("Klavijature i digitalni pianini", "Klavijature", "Pretraži klavijature: model, marka…"),
              "micro": ("Mikrofoni", "Mikrofoni", "Pretraži mikrofone: model, marka, vrsta…"),
              "estuche": ("Koferi i torbe", "Koferi", "Pretraži kofere i torbe: model, marka…"),
              "varios": ("Gitarski pribor", "Pribor", "Pretraži pribor: žice, trzalice, remeni, kabeli…")},
    # Što se broji u svakoj kategoriji (početna i popis) i, ako nisu samo gitare, ukupno (genitiv množine).
    "nouns": {"bajo": "bas-gitara", "ampli": "pojačala", "pedal": "pedala", "teclado": "klavijatura", "micro": "mikrofona",
              "estuche": "kofera i torbi", "varios": "artikala"},
    "allWord": "proizvoda",
    "anyPrice": "Bilo koja cijena", "upTo": "Do {v}", "over": "Više od {v}", "brandLabel": "Marka", "priceLabel": "Cijena",
    "showLabel": "Prikaži", "showAll": "Sve", "showMulti": "U više trgovina", "showStock": "Na zalihi",
    "showLow": "Po najnižoj cijeni", "showLh": "Samo za ljevake", "loading": "Učitavanje kataloga…", "sortLabel": "Poredaj",
    "sorts": ["Najviše trgovina", "Najniža cijena", "Najviša cijena", "Najveća ušteda među trgovinama", "Naziv"],
    "moreBtn": "Prikaži više", "sections": "Odjeljci", "searchAria": "Traži",
    "bestPrice": "najbolja cijena", "inStock": "na zalihi", "noStock": "nije na zalihi", "goLong": "Idi u trgovinu", "goShort": "Idi",
    "store": "trgovini", "stores": "trgovinama", "lh": "za ljevake", "storesH3": "Trgovine", "historyH3": "Povijest cijena",
    "amazon": "", "titleFrom": "{name}: cijena od {price} {where}", "inN": "u {n} trgovinama", "inS": "u trgovini {s}",
    "whereMany": "u trgovini {s} · trgovina: {n}", "whereDiff": ", razlika do {d}",
    "desc": "{name} od {price} u trgovini {s}. Usporedi cijenu u {n} {stores} ({list}) i pogledaj povijest cijena da vidiš je li "
            "sada dobar trenutak za kupnju.",
    "alertTitle": "Obavijest o cijeni", "alertWait": "Trenutak…", "alertSaving": "Spremamo tvoj odgovor.",
    "alertGo": "Idi na guitle", "alertBad": ["Neispravna poveznica", "Kopiraj cijelu poveznicu iz e-pošte i pokušaj ponovno."],
    "alertDone": ["Obavijest potvrđena!", "Javit ćemo ti čim cijena padne. Svaka poruka sadrži poveznicu za odjavu."],
    "alertGone": ["Obavijest izbrisana", "Više nećeš primati poruke za ovu obavijest. Tvoju smo adresu izbrisali s popisa."],
    "alertMissing": ["Obavijest nije pronađena", "Možda je već potvrđena ili izbrisana ili je prošlo više od 7 dana bez "
                                                 "potvrde. Trebaš pomoć? Piši nam na hola@guitle.com."],
    "js": {"loadErr": "Katalog se nije mogao učitati.", "allBrands": "Sve marke", "all": "Sve", "low": "Najniža",
           "save": "Uštedi {v}", "lh": "za ljevake", "store": "trgovina", "stores": "trgovine",
           "empty": "Nema {many} s ovim filtrima.", "more": "Prikaži više (još {n})",
           "meta": "{a} od {b} {many} · {m} usporedivih u više trgovina · ažurirano {d}", "best": "najbolja cijena",
           "inStock": "na zalihi", "noStock": "nije na zalihi", "goLong": "Idi u trgovinu", "goShort": "Idi", "close": "Zatvori",
           "inAt": "u trgovini {s}", "saveMax": " · do {v} jeftinije nego u najskupljoj", "atLow": "Po najnižoj zabilježenoj cijeni",
           "lowTag": "Najniža: {v}", "storesH": "Trgovine", "evolH": "Kretanje cijene",
           "histErr": "Povijest cijena nije se mogla učitati.", "histSoon": "Povijest cijena popunjavat će se idućih dana.",
           "many": "gitara",
           "types": {"ST": "ST oblik", "T": "T oblik", "Semihueca": "Poluakustične", "Offset / Retro": "Offset / Retro",
                     "Moderna / Metal": "Moderne / Metal", "Otras": "Ostalo", "Auditorio / Concierto": "Auditorium / Concert",
                     "12 cuerdas": "12 žica", "Tamaño reducido": "Manje veličine", "Clásica": "Klasične",
                     "Flamenca": "Flamenco", "Electroclásica": "Elektroklasične",
                     "4 cuerdas": "4 žice", "5 cuerdas": "5 žica", "6 cuerdas o más": "6 i više žica",
                     "Acústico": "Akustični bas", "Fretless": "Fretless", "Escala corta": "Kratka menzura", "Combo": "Combo pojačala",
                     "Cabezal": "Glave", "Pantalla": "Kabineti", "Para bajo": "Za bas", "Para acústica": "Za akustičnu gitaru",
                     "De auriculares y portátil": "Mini i za slušalice", "Para eléctrica": "Za električnu gitaru",
                     "Para clásica": "Za klasičnu gitaru", "Overdrive y distorsión": "Overdrive i distorzija",
                     "Modulación": "Modulacija", "Compresor": "Kompresori", "Wah y volumen": "Wah i volumen",
                     "Octavador y pitch": "Oktaver i pitch", "Ecualizador": "Ekvilajzeri", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintisajzeri", "Afinador": "Štimeri", "Multiefectos": "Multiefekti",
                     "Reverb": "Reverb", "Piano digital": "Digitalni pianini", "Teclado portátil": "Prijenosne klavijature",
                     "Piano de escenario": "Stage pianini", "Controlador MIDI": "MIDI kontroleri", "Piano acústico": "Akustični klaviri",
                     "Dinámico": "Dinamički", "Condensador": "Kondenzatorski", "Inalámbrico": "Bežični",
                     "Para instrumento": "Za instrumente", "De cinta": "Vrpčani", "Cuerdas": "Žice",
                     "Púas": "Trzalice", "Correas": "Remeni", "Cables": "Kabeli", "Afinadores": "Štimeri",
                     "Cejillas": "Kapodasteri", "Soportes": "Stalci", "Pastillas": "Magneti", "Recambios": "Rezervni dijelovi",
                     "Mantenimiento": "Održavanje"},
           "wait": "Ovaj model pratimo tek {n} {days}", "day": "dan", "days": "dana",
           "waitSub": "Procjena postaje pouzdanija nakon nekoliko tjedana povijesti cijena.",
           "min": "Najniža zabilježena cijena", "minSub": "Nikad nismo vidjeli nižu cijenu.",
           "minBelow": " {p} % ispod 30-dnevnog prosjeka.",
           "good": "Dobar trenutak: {p} % ispod prosječne cijene", "goodSub": "Prosjek zadnjih 30 dana: {avg}.",
           "bad": "Cijena je trenutačno {p} % viša nego obično",
           "badSub": "Ako ti se ne žuri, pričekaj: 30-dnevni prosjek je {avg}, a najniža cijena {min}.",
           "normal": "Uobičajena cijena", "normalSub": "U skladu s 30-dnevnim prosjekom ({avg}). Najniža zabilježena: {min}.",
           "today": "cijena danas", "lowest": "najniža ({d})", "highest": "najviša", "avg": "prosjek {n} dana",
           "since": "Pratimo od {d}", "noHist": "Još nema povijesti cijena.", "pvp": "Preporučena cijena", "bestLine": "Najbolja cijena",
           "alertOpen": "Javi mi ako cijena padne", "emailPh": "ti@primjer.hr", "emailLabel": "Tvoja e-pošta",
           "targetPh": "Maks. cijena (neobavezno)", "targetLabel": "Željena cijena u eurima", "alertBtn": "Javi mi",
           "alertLegal": "Besplatno i bez registracije. Klikom na „Javi mi” prihvaćaš "
                         "<a href=\"/hr/legal.html#privatnost\">pravila privatnosti</a>: tvoju e-poštu koristimo samo za ovu "
                         "obavijest, a odjaviti se možeš jednim klikom.",
           "alertOk": "<b>Gotovo!</b> Za nekoliko minuta stići će ti poruka na {email} za potvrdu obavijesti (provjeri i mapu neželjene pošte).",
           "alertErr": "Obavijest nije spremljena. Provjeri adresu e-pošte i pokušaj ponovno."},
    "mail": {"tagline": "gitare po najboljoj cijeni",
             "footer": "guitle svaki dan uspoređuje cijene glazbenih trgovina. Ovu poruku primaš jer si zatražio obavijest "
                       "na guitle.com. Voditelj obrade: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Privatnost", "confirmSubject": "Potvrdi svoju guitle obavijest o cijeni",
             "confirmTitle": "Potvrdi obavijest o cijeni", "asked": "Zatražio si da ti javimo kad cijena padne{target}:",
             "below": " ispod <b>{v}</b>", "confirmAsk": "Potvrdi da želiš primati obavijest na ovu adresu:",
             "confirmBtn": "Potvrdi obavijest",
             "notYou": "Ako to nisi bio ti, ne poduzimaj ništa: nepotvrđene obavijesti automatski se brišu nakon 7 dana.",
             "dropSubject": "Cijena je pala: {name} sada {price}", "dropTitle": "Cijena je pala!", "nowAt": "u trgovini {s} · prije {v}",
             "seeAll": "Pogledaj cijene u svim trgovinama",
             "check": "Cijene se mijenjaju svaki dan: provjeri ih u trgovini prije kupnje. Više te ne zanima?",
             "stop": "Otkaži ovu obavijest"},
}

# Nadzorno tijelo u Hrvatskoj: Agencija za zaštitu osobnih podataka (AZOP), azop.hr.
# Izraz za eventualni legal_replace: "ili Agenciji za zaštitu osobnih podataka (AZOP)".
LEGAL_LANG = ("Pravne informacije i privatnost", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Pravne informacije i privatnost</h1>
<p class="muted">Zadnje ažuriranje: 28. listopada 2026. Ovo je prijevod; u slučaju dvojbe mjerodavna je <a href="/legal.html">španjolska verzija</a>.</p>

<h2 id="aviso">Pravne informacije</h2>
<p>Ovu web-stranicu vodi <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Španjolska
(španjolski porezni broj NIF 17747339X), kontakt <a href="mailto:hola@guitle.com">hola@guitle.com</a>, web-stranica guitle.com.
Djelatnost: usporedba cijena glazbenih instrumenata i partnersko oglašavanje. Hosting: GitHub Pages (GitHub, Inc.).</p>

<h2 id="uvjeti">Uvjeti korištenja</h2>
<p>guitle je usporednik cijena i ništa ne prodaje. Prikazujemo cijene koje trgovine objavljuju na svojim stranicama i upućujemo te na njih
kako bi kupio izravno u trgovini. Za kupnju, dostavu, jamstvo i povrat odgovorna je svaka trgovina.</p>
<ul>
<li><b>Cijene su informativne.</b> Cijene redovito provjeravamo, ali se mogu promijeniti u bilo kojem trenutku. Vrijedi uvijek cijena koju trgovina prikazuje pri narudžbi.</li>
<li><b>Bez jamstva točnosti.</b> Trudimo se da proizvodi, cijene i dostupnost budu točni, ali moguće su pogreške. Ako uočiš neku, javi nam.</li>
<li><b>Žigovi i slike.</b> Žigovi, nazivi proizvoda i slike pripadaju njihovim vlasnicima i koriste se samo za prepoznavanje proizvoda.</li>
<li><b>Sadržaj guitlea.</b> Dizajn, logotip, tekstovi i zbirke podataka guitlea pripadaju njegovu vlasniku. Masovno kopiranje ili komercijalna upotreba bez dopuštenja nisu dopušteni.</li>
</ul>

<h2 id="affiliate">Partnerske poveznice</h2>
<p>Neke poveznice na trgovine su partnerske: ako kupiš nakon klika, trgovina guitleu može platiti malu proviziju. Za tebe se cijena ne mijenja.
Provizije ne utječu na redoslijed: trgovine su uvijek poredane po cijeni, od najjeftinije.</p>

<h2 id="privatnost">Pravila privatnosti</h2>
<p>guitle ne traži osobne podatke za korištenje stranice: bez registracije, bez newslettera, bez alata za analitiku ili oglašavanje
koji te prate. Posjete brojimo samo anonimno i, ako zatražiš obavijest o cijeni, čuvamo tvoju adresu e-pošte za tu obavijest.</p>
<ul>
<li><b>Obavijesti o cijeni.</b> Ako zatražiš da ti javimo kad cijena nekog proizvoda padne, spremamo tvoju adresu e-pošte, proizvod, njegovu cijenu
toga dana i, ako je navedeš, željenu cijenu. Koristimo ih samo za poruku potvrde i obavijesti o tom proizvodu, nikad za marketing, i ni s kim ih
ne dijelimo. Pravna osnova: tvoja privola (čl. 6. st. 1. točka (a) Opće uredbe o zaštiti podataka, GDPR), koju daješ kad zatražiš obavijest i potvrdiš
e-poštu. Podaci se pohranjuju u Google Cloud Firestore (Google Ireland Ltd., poslužitelj u Madridu), a poruke šaljemo s našeg sandučića
hola@guitle.com (DonDominio, Španjolska). Nepotvrđene obavijesti brišu se nakon 7 dana; potvrđene se čuvaju dok se ne odjaviš putem poveznice u
svakoj poruci (obavijest se odmah briše) ili dok nas ne zamoliš da je izbrišemo.</li>
<li><b>Postavke u tvom pregledniku.</b> Filtri ili odabrani prikaz spremaju se u lokalnu pohranu tvog preglednika (localStorage) i nikad se ne šalju ni na jedan poslužitelj.</li>
<li><b>Hosting.</b> Stranica je smještena na GitHub Pages (GitHub, Inc.). Kao i svaki web-poslužitelj, GitHub može bilježiti IP adresu svakog posjeta
iz tehničkih i sigurnosnih razloga. GitHub je certificiran u okviru EU-US Data Privacy Framework.</li>
<li><b>Brojač posjeta.</b> Svaka stranica dodaje 1 anonimnom brojaču: dan, pregledanu stranicu, stranicu s koje dolaziš (npr. google.com), ono što
upisuješ u tražilicu kataloga i, ako klikneš prema trgovini, njezin naziv. Bez kolačića, bez IP adrese, bez ičega što bi te identificiralo. Brojači se
pohranjuju u Google Cloud Firestore (Google Ireland Ltd.), na poslužitelju u Europskoj uniji (Madrid).</li>
<li><b>Nema drugih zahtjeva prema trećim stranama.</b> Fontovi, grafikoni i fotografije proizvoda učitavaju se s guitle.com.</li>
<li><b>Kad odeš u trgovinu.</b> Kad klikneš prema trgovini, napuštaš guitle i primjenjuju se pravila privatnosti te trgovine.</li>
</ul>
<p><b>Tvoja prava.</b> Prava na pristup, ispravak, brisanje, prigovor, ograničenje obrade i prenosivost možeš ostvariti slanjem poruke na
<a href="mailto:hola@guitle.com">hola@guitle.com</a>. Možeš podnijeti i pritužbu nadzornom tijelu za zaštitu podataka, primjerice
Agencia Española de Protección de Datos ili nacionalnom nadzornom tijelu za zaštitu osobnih podataka. Voditelj obrade: vlasnik naveden u pravnim informacijama.</p>

<h2 id="cookies">Kolačići</h2>
<p>guitle ne koristi kolačiće, ni vlastite ni kolačiće trećih strana, pa zato ne vidiš obavijest o kolačićima. Koristimo samo lokalnu pohranu preglednika
kako bismo zapamtili tvoje postavke. Trgovine na koje upućujemo mogu na svojim stranicama koristiti vlastite kolačiće.</p>
""")
