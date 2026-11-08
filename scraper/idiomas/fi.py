# Suomi (Suomi, EUR). Sivustokoodi oletettu: "fi" (alertLegal osoittaa /fi/legal.html; strings() kirjoittaa koodin joka tapauksessa uudelleen).
# Tietosuoja-ankkuri LEGALissa on "tietosuoja": lisää "fi": "tietosuoja" funktioon intl._anchor().
#
# HUOM. lukusanat: koodi tuottaa "{n} {sana}" (esim. "1 234 kitaraa", "{a}/{b} {many}", "{n} {stores}"), joten
# monikkosanat ovat yksikön partitiivissa (kitaraa, kauppaa, bassoa…) ja yksikkö nominatiivissa (kauppa).
# "wait": "... {n} {days} ajan" -> day/days ovat molemmat genetiivissä ("päivän"): "1 päivän ajan", "5 päivän ajan".

T_LANG = {
    "tagline": "kitarat parhaaseen hintaan", "homeLabel": "guitle, etusivu",
    "homeTitle": "guitle · kitaroiden hintavertailu",
    "homeDesc": "guitle vertailee sähkökitaroiden, akustisten ja klassisten kitaroiden hintoja Suomeen toimittavissa "
                "kaupoissa ja näyttää jokaisen mallin hintahistorian.",
    "h1": "Kitarasi <span>parhaaseen hintaan</span><small>Kitaroiden hintavertailu</small>",
    "searchPh": "Hae: strat, les paul, yamaha, ibanez…", "searchBtn": "Hae", "searchLabel": "Hae kitaraa",
    "guitars": "kitaraa", "storesWord": "kauppaa", "catalog": "Valikoima",
    "dealsH": "Suurimmat hintaerot kauppojen välillä", "dealsBadge": "−{p} % kalleimpaan verrattuna",
    "catsH": "Selaa tuoteryhmiä", "soon": "tulossa pian", "storesH": "Vertailemamme kaupat",
    "howH": "Näin se toimii",
    "steps": ["Tarkistamme joka päivä jokaisen kitaran hinnan, saatavuuden ja kuvan Suomeen toimittavissa kaupoissa.",
              "Tallennamme hintahistorian, jotta näet, onko hinta todella hyvä vai yleensä alempi.",
              "Halutessasi lähetämme sinulle sähköpostia, kun hinta laskee."],
    "affiliate": "Osa kauppoihin johtavista linkeistä on kumppanilinkkejä: jos ostat, guitle voi saada palkkion ilman lisäkustannuksia sinulle.",
    "legal": "Oikeudelliset tiedot", "privacy": "Tietosuoja", "cookies": "Evästeet", "otherCountries": "guitle muissa maissa:",
    "updated": "Tiedot päivitetty {d}", "home": "Etusivu",
    "kinds": {"electrica": ("Sähkökitarat", "Sähkökitarat", "Hae sähkökitaroista: malli, merkki, väri…"),
              "acustica": ("Akustiset kitarat", "Akustiset", "Hae akustisista kitaroista: malli, merkki, puulaji…"),
              "clasica": ("Klassiset kitarat", "Klassiset", "Hae klassisista kitaroista: malli, merkki, flamenco…"),
              "bajo": ("Sähkö- ja akustiset bassot", "Bassot", "Hae bassoista: malli, merkki, 5-kielinen…"),
              "ampli": ("Kitara- ja bassovahvistimet", "Vahvistimet", "Hae vahvistimista: malli, merkki, kombo, nuppi…"),
              "pedal": ("Efektipedaalit", "Efektit", "Hae efektipedaaleista: malli, merkki, efekti…"),
              "teclado": ("Koskettimet ja digitaalipianot", "Koskettimet", "Hae koskettimista: malli, merkki…"),
              "micro": ("Mikrofonit", "Mikrofonit", "Hae mikrofoneista: malli, merkki, tyyppi…"),
              "estuche": ("Laukut ja kotelot", "Laukut", "Hae laukuista ja koteloista: malli, merkki…"),
              "varios": ("Kitaratarvikkeet", "Tarvikkeet", "Hae tarvikkeista: kielet, plektrat, hihnat, johdot…")},
    "nouns": {"bajo": "bassoa", "ampli": "vahvistinta", "pedal": "pedaalia", "teclado": "kosketinsoitinta", "micro": "mikrofonia",
              "estuche": "laukkua", "varios": "tuotetta"},
    "allWord": "tuotetta",
    "anyPrice": "Kaikki hinnat", "upTo": "Enintään {v}", "over": "Yli {v}", "brandLabel": "Merkki", "priceLabel": "Hinta",
    "showLabel": "Näytä", "showAll": "Kaikki", "showMulti": "Useassa kaupassa", "showStock": "Varastossa",
    "showLow": "Alimmassa hinnassaan", "showLh": "Vain vasenkätiset", "loading": "Ladataan valikoimaa…", "sortLabel": "Järjestä",
    "sorts": ["Eniten kauppoja", "Halvin ensin", "Kallein ensin", "Suurin hintaero kauppojen välillä", "Nimi"],
    "moreBtn": "Näytä lisää", "sections": "Osastot", "searchAria": "Hae",
    "bestPrice": "paras hinta", "inStock": "varastossa", "noStock": "ei varastossa", "goLong": "Siirry kauppaan", "goShort": "Kauppaan",
    "store": "kauppa", "stores": "kauppaa", "lh": "vasenkätinen", "storesH3": "Kaupat", "historyH3": "Hintahistoria",
    "amazon": "", "titleFrom": "{name}: hinta alkaen {price} {where}", "inN": "{n} kaupassa", "inS": "kaupassa {s}",
    "whereMany": "kaupassa {s} · {n} kauppaa", "whereDiff": ", hintaero jopa {d}",
    "desc": "{name} alkaen {price} kaupassa {s}. Vertaa hintoja: {n} {stores} ({list}). Katso hintahistoriasta, onko nyt "
            "hyvä hetki ostaa.",
    "alertTitle": "Hintavahti", "alertWait": "Hetkinen…", "alertSaving": "Tallennamme vastaustasi.",
    "alertGo": "Siirry guitleen", "alertBad": ["Virheellinen linkki", "Kopioi koko linkki sähköpostista ja yritä uudelleen."],
    "alertDone": ["Hintavahti vahvistettu!", "Lähetämme sinulle sähköpostia heti, kun hinta laskee. Jokaisessa viestissä on linkki "
                                             "hintavahdin perumiseen."],
    "alertGone": ["Hintavahti poistettu", "Et saa enää sähköposteja tästä hintavahdista. Olemme poistaneet osoitteesi listaltamme."],
    "alertMissing": ["Hintavahtia ei löytynyt", "Se on ehkä jo vahvistettu tai poistettu, tai vahvistamatta on kulunut yli 7 päivää. "
                                                "Tarvitsetko apua? Lähetä viesti osoitteeseen hola@guitle.com."],
    "js": {"loadErr": "Valikoiman lataaminen epäonnistui.", "allBrands": "Kaikki merkit", "all": "Kaikki", "low": "Alin",
           "save": "Säästä {v}", "lh": "vasenkätinen", "store": "kauppa", "stores": "kauppaa",
           "empty": "Näillä suodattimilla ei löytynyt yhtään {many}.", "more": "Näytä lisää ({n} jäljellä)",
           "meta": "{a}/{b} {many} · {m} vertailtavissa useassa kaupassa · päivitetty {d}", "best": "paras hinta",
           "inStock": "varastossa", "noStock": "ei varastossa", "goLong": "Siirry kauppaan", "goShort": "Kauppaan", "close": "Sulje",
           "inAt": "kaupassa {s}", "saveMax": " · jopa {v} halvempi kuin kallein", "atLow": "Alimmassa seuratussa hinnassaan",
           "lowTag": "Alin seurattu: {v}", "storesH": "Kaupat", "evolH": "Hintahistoria",
           "histErr": "Hintahistorian lataaminen epäonnistui.", "histSoon": "Hintahistoria täydentyy tulevina päivinä.",
           "many": "kitaraa",
           "types": {"ST": "ST-mallit", "T": "T-mallit", "Semihueca": "Puoliakustiset", "Offset / Retro": "Offset / Retro",
                     "Moderna / Metal": "Moderni / Metal", "Otras": "Muut", "Auditorio / Concierto": "Auditorium / Concert",
                     "12 cuerdas": "12-kieliset", "Tamaño reducido": "Pienikokoiset", "Clásica": "Klassinen",
                     "Flamenca": "Flamenco", "Electroclásica": "Sähköistetty klassinen",
                     "4 cuerdas": "4-kieliset", "5 cuerdas": "5-kieliset", "6 cuerdas o más": "6 kieltä tai enemmän",
                     "Acústico": "Akustinen basso", "Fretless": "Nauhattomat", "Escala corta": "Lyhyt mensuuri", "Combo": "Kombot",
                     "Cabezal": "Nupit", "Pantalla": "Kaapit", "Para bajo": "Bassolle", "Para acústica": "Akustiselle kitaralle",
                     "De auriculares y portátil": "Kuuloke- ja minivahvistimet", "Para eléctrica": "Sähkökitaralle",
                     "Para clásica": "Klassiselle kitaralle", "Overdrive y distorsión": "Overdrive ja särö",
                     "Modulación": "Modulaatio", "Compresor": "Kompressori", "Wah y volumen": "Wah ja volyymi",
                     "Octavador y pitch": "Oktaavi ja pitch", "Ecualizador": "EQ", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Syntikat", "Afinador": "Viritin", "Multiefectos": "Multiefektit",
                     "Reverb": "Reverb", "Piano digital": "Digitaalipianot", "Teclado portátil": "Kannettavat koskettimet",
                     "Piano de escenario": "Stage-pianot", "Controlador MIDI": "MIDI-ohjaimet", "Piano acústico": "Akustiset pianot",
                     "Dinámico": "Dynaamiset", "Condensador": "Kondensaattori", "Inalámbrico": "Langattomat",
                     "Para instrumento": "Soitinmikrofonit", "De cinta": "Nauhamikrofonit", "Cuerdas": "Kielet",
                     "Púas": "Plektrat", "Correas": "Hihnat", "Cables": "Johdot", "Afinadores": "Virittimet",
                     "Cejillas": "Kapot", "Soportes": "Telineet", "Pastillas": "Kitaramikit", "Recambios": "Varaosat",
                     "Mantenimiento": "Huolto ja hoito"},
           "wait": "Olemme seuranneet tätä mallia {n} {days} ajan", "day": "päivän", "days": "päivän",
           "waitSub": "Arvio tarkentuu muutaman viikon hintahistorian jälkeen.",
           "min": "Alin seurattu hinta", "minSub": "Emme ole koskaan nähneet sitä halvemmalla.",
           "minBelow": " {p} % alle 30 päivän keskihinnan.",
           "good": "Hyvä hetki ostaa: {p} % alle keskihinnan", "goodSub": "30 päivän keskihinta: {avg}.",
           "bad": "Nyt {p} % tavallista kalliimpi",
           "badSub": "Jos sinulla ei ole kiire, odota: 30 päivän keskihinta on {avg} ja alin hinta {min}.",
           "normal": "Normaali hinta", "normalSub": "30 päivän keskihinnan tasolla ({avg}). Alin seurattu: {min}.",
           "today": "hinta tänään", "lowest": "alin ({d})", "highest": "korkein", "avg": "{n} päivän keskihinta",
           "since": "Seurattu {d} alkaen", "noHist": "Hintahistoriaa ei vielä ole.", "pvp": "Ohjehinta", "bestLine": "Paras hinta",
           "alertOpen": "Ilmoita, kun hinta laskee", "emailPh": "nimi@esimerkki.fi", "emailLabel": "Sähköpostiosoitteesi",
           "targetPh": "Enimmäishinta (valinnainen)", "targetLabel": "Tavoitehinta euroina", "alertBtn": "Ilmoita minulle",
           "alertLegal": "Maksuton, ei rekisteröitymistä. Napsauttamalla ”Ilmoita minulle” hyväksyt "
                         "<a href=\"/fi/legal.html#tietosuoja\">tietosuojaselosteemme</a>: käytämme sähköpostiosoitettasi vain "
                         "tähän hintavahtiin, ja voit perua sen yhdellä napsautuksella.",
           "alertOk": "<b>Valmista!</b> Saat muutaman minuutin kuluttua osoitteeseen {email} viestin, jolla vahvistat hintavahdin "
                      "(tarkista myös roskapostikansio).",
           "alertErr": "Hintavahdin tallentaminen epäonnistui. Tarkista sähköpostiosoite ja yritä uudelleen."},
    "mail": {"tagline": "kitarat parhaaseen hintaan",
             "footer": "guitle vertailee soitinkauppojen hintoja joka päivä. Saat tämän viestin, koska tilasit hintavahdin "
                       "guitle.com-sivustolla. Rekisterinpitäjä: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Tietosuoja", "confirmSubject": "Vahvista guitle-hintavahtisi",
             "confirmTitle": "Vahvista hintavahtisi", "asked": "Pyysit meitä ilmoittamaan, kun hinta laskee{target}:",
             "below": " alle <b>{v}</b>", "confirmAsk": "Vahvista, että haluat saada hintavahdin ilmoitukset tähän osoitteeseen:",
             "confirmBtn": "Vahvista hintavahti",
             "notYou": "Jos et tilannut tätä, älä tee mitään: vahvistamattomat hintavahdit poistetaan automaattisesti 7 päivän kuluttua.",
             "dropSubject": "Hinta laski: {name} nyt {price}", "dropTitle": "Hinta on laskenut!", "nowAt": "kaupassa {s} · aiemmin {v}",
             "seeAll": "Katso hinnat kaikissa kaupoissa",
             "check": "Hinnat muuttuvat päivittäin: tarkista hinta kaupasta ennen ostamista. Etkö ole enää kiinnostunut?",
             "stop": "Peru tämä hintavahti"},
}

PACK_LANG = ("Kitarapaketit", "Paketit", "Hae kitarapaketeista: malli, merkki, vahvistimella…", "pakettia",
             {"Eléctrica": "Sähkökitara", "Acústica": "Akustinen kitara"})

KINDS_LANG = {"electrica": "sahkokitarat", "acustica": "akustiset-kitarat", "clasica": "klassiset-kitarat", "bajo": "bassot",
              "ampli": "vahvistimet", "pedal": "efektipedaalit", "teclado": "koskettimet", "micro": "mikrofonit",
              "estuche": "laukut-kotelot", "varios": "tarvikkeet", "pack": "kitarapaketit"}

PRIVACY_ANCHOR = "tietosuoja"

MONEY_NOTE = ("Suomi (fi-FI, EUR): välilyönti (sitova, \\u00a0 tai \\u202f) tuhaterottimena, desimaalipilkku, '€' perässä "
              "välilyönnin kanssa: '1 299 €', '1 299,50 €'. money() tuottaa tämän jo nykyisellä oletushaaralla "
              "(lang 'fi' -> erotin \\u202f), kuten ranskalle/portugalille. JS toLocaleString('fi-FI', currency 'EUR') antaa '1 299 €'.")

# Valvontaviranomainen: Tietosuojavaltuutetun toimisto. Ehdotus SITES["fi"]["legal_replace"]:
#   [("tai oman maasi valvontaviranomaiselle", "tai Tietosuojavaltuutetun toimistolle")]
LEGAL_LANG = ("Oikeudelliset tiedot ja tietosuoja", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Oikeudelliset tiedot ja tietosuoja</h1>
<p class="muted">Päivitetty: 28. lokakuuta 2026. Tämä on käännös; epäselvissä tapauksissa sovelletaan <a href="/legal.html">espanjankielistä versiota</a>.</p>

<h2 id="aviso">Oikeudelliset tiedot</h2>
<p>Tätä sivustoa ylläpitää <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Espanja
(espanjalainen verotunniste NIF 17747339X), yhteystiedot <a href="mailto:hola@guitle.com">hola@guitle.com</a>, sivusto guitle.com.
Toiminta: soittimien hintavertailu ja kumppanimarkkinointi. Palvelin: GitHub Pages (GitHub, Inc.).</p>

<h2 id="kayttoehdot">Käyttöehdot</h2>
<p>guitle on hintavertailupalvelu eikä myy itse mitään. Näytämme hinnat, jotka kaupat julkaisevat verkkosivuillaan, ja linkitämme niihin, jotta
ostat suoraan kaupasta. Ostoksesta, toimituksesta, takuusta ja palautuksista vastaa kukin kauppa.</p>
<ul>
<li><b>Hinnat ovat suuntaa antavia.</b> Tarkistamme hinnat säännöllisesti, mutta ne voivat muuttua milloin tahansa. Voimassa on aina se hinta, jonka kauppa näyttää tilatessasi.</li>
<li><b>Ei takuuta tietojen oikeellisuudesta.</b> Pyrimme siihen, että tuotteet, hinnat ja saatavuus ovat oikein, mutta virheitä voi esiintyä. Jos huomaat virheen, kerro meille.</li>
<li><b>Tavaramerkit ja kuvat.</b> Tavaramerkit, tuotenimet ja kuvat kuuluvat omistajilleen, ja niitä käytetään vain tuotteiden tunnistamiseen.</li>
<li><b>guitlen sisältö.</b> guitlen ulkoasu, logo, tekstit ja tietokokoelmat kuuluvat sivuston ylläpitäjälle. Laajamittainen kopiointi tai kaupallinen käyttö ilman lupaa on kielletty.</li>
</ul>

<h2 id="affiliate">Kumppanilinkit</h2>
<p>Osa kauppoihin johtavista linkeistä on kumppanilinkkejä: jos ostat jotain linkin kautta, kauppa voi maksaa guitlelle pienen palkkion. Hinta on
sinulle sama. Palkkiot eivät vaikuta järjestykseen: kaupat järjestetään aina hinnan mukaan halvimmasta alkaen.</p>

<h2 id="tietosuoja">Tietosuojaseloste</h2>
<p>guitle ei pyydä henkilötietoja sivuston käyttämiseen: ei rekisteröitymistä, ei uutiskirjeitä eikä sinua seuraavia analytiikka- tai
mainostyökaluja. Laskemme käynnit vain anonyymisti, ja jos tilaat hintavahdin, tallennamme sähköpostiosoitteesi sitä varten.</p>
<ul>
<li><b>Hintavahdit.</b> Jos haluat tiedon, kun tuotteen hinta laskee, tallennamme sähköpostiosoitteesi, tuotteen, sen kyseisen päivän hinnan ja
tavoitehintasi, jos annat sellaisen. Käytämme tietoja vain vahvistusviestin ja kyseisen tuotteen hintailmoitusten lähettämiseen, emme koskaan
markkinointiin, emmekä luovuta niitä kenellekään. Käsittelyperuste: suostumuksesi (EU:n yleisen tietosuoja-asetuksen 6 artiklan 1 kohdan a alakohta),
jonka annat tilaamalla hintavahdin ja vahvistamalla sähköpostiosoitteesi. Tiedot tallennetaan Google Cloud Firestoreen (Google Ireland Ltd.,
palvelin Madridissa), ja viestit lähetetään postilaatikostamme hola@guitle.com (DonDominio, Espanja). Vahvistamattomat hintavahdit poistetaan
7 päivän kuluttua; vahvistetut säilytetään, kunnes perut ne jokaisessa viestissä olevalla linkillä (hintavahti poistetaan heti) tai pyydät
meitä poistamaan ne.</li>
<li><b>Asetukset selaimessasi.</b> Valitsemasi suodattimet tai näkymä tallennetaan selaimesi paikalliseen tallennustilaan (localStorage), eikä niitä lähetetä millekään palvelimelle.</li>
<li><b>Palvelin.</b> Sivusto toimii GitHub Pagesissa (GitHub, Inc.). Kuten mikä tahansa verkkopalvelin, GitHub voi kirjata kunkin kävijän
IP-osoitteen teknisistä ja tietoturvasyistä. GitHub on sertifioitu EU:n ja Yhdysvaltojen välisen tietosuojakehyksen (EU-US Data Privacy Framework) mukaisesti.</li>
<li><b>Kävijälaskuri.</b> Jokainen sivu kasvattaa anonyymia laskuria yhdellä: päivä, katsottu sivu, sivusto, jolta tulit (esimerkiksi google.com),
valikoiman hakukenttään kirjoittamasi teksti ja, jos siirryt kauppaan, kaupan nimi. Ei evästeitä, ei IP-osoitetta, ei mitään, mikä tunnistaisi
sinut. Laskurit tallennetaan Google Cloud Firestoreen (Google Ireland Ltd.) EU:ssa sijaitsevalle palvelimelle (Madrid).</li>
<li><b>Ei muita kolmansien osapuolten pyyntöjä.</b> Fontit, kaaviot ja tuotekuvat ladataan guitle.com-sivustolta.</li>
<li><b>Siirtyminen kauppaan.</b> Kun siirryt kauppaan, poistut guitlesta, ja silloin sovelletaan kaupan tietosuojaselostetta.</li>
</ul>
<p><b>Oikeutesi.</b> Voit käyttää oikeuttasi tarkastaa tietosi, oikaista ja poistaa ne, vastustaa ja rajoittaa niiden käsittelyä sekä siirtää ne
järjestelmästä toiseen lähettämällä sähköpostia osoitteeseen <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Voit myös tehdä valituksen
tietosuojavalvontaviranomaiselle, esimerkiksi Espanjan Agencia Española de Protección de Datos -viranomaiselle
tai oman maasi valvontaviranomaiselle. Rekisterinpitäjä: oikeudellisissa tiedoissa mainittu ylläpitäjä.</p>

<h2 id="cookies">Evästeet</h2>
<p>guitle ei käytä evästeitä, ei omia eikä kolmansien osapuolten – siksi et näe evästeilmoitusta. Käytämme vain selaimen paikallista
tallennustilaa asetustesi muistamiseen. Kaupat, joihin linkitämme, voivat käyttää omia evästeitään sivustoillaan.</p>
""")
