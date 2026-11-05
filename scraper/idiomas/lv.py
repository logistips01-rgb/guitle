# Latviešu (lv) — guitle.com texts. Country code in URLs: "lv" (the alertLegal link is rewritten by strings()).
# Informal "tu" form, like the German "du" (the common style of Latvian comparison sites, cf. "salīdzini").
# Plurals: counts use the nominative plural ("12 ģitāras", "5 veikali"), correct for every number not ending in 1
# (or ending in 11). "wait" only runs for n < 7, so "1 dienu" / "2–6 dienas" are exact.

# Anchor of the privacy section in LEGAL_LANG (add to intl._anchor: "lv": "privatums").
PRIVACY_ANCHOR = "privatums"

MONEY_NOTE = ("Latvian format: amount, no-break space, euro sign after it: 1299 € (four digits usually without a "
              "thousands separator; from five digits a space: 12 999 €), decimals with a comma: 1299,90 €. "
              "intl.money() falls into the default branch (narrow no-break space as thousands separator), which is "
              "also acceptable; for exactly \"1299 €\" add a branch for lang 'lv' with no separator below 10 000.")

KINDS_LANG = {"electrica": "elektriskas-gitaras", "acustica": "akustiskas-gitaras", "clasica": "klasiskas-gitaras",
              "pack": "gitaru-komplekti", "bajo": "basgitaras", "ampli": "pastiprinataji", "pedal": "efektu-pedali",
              "teclado": "taustininstrumenti", "micro": "mikrofoni", "estuche": "futrali-somas", "varios": "piederumi"}

PACK_LANG = ("Ģitāru komplekti", "Komplekti", "Meklē komplektos: modelis, zīmols, ar pastiprinātāju…", "komplekti",
             {"Eléctrica": "Elektriskā", "Acústica": "Akustiskā"})

T_LANG = {
    "tagline": "ģitāras par labāko cenu", "homeLabel": "guitle, sākumlapa",
    "homeTitle": "guitle · ģitāru cenu salīdzināšana",
    "homeDesc": "guitle salīdzina ģitāru cenas: elektriskās, akustiskās un klasiskās ģitāras veikalos, kas piegādā uz "
                "Latviju, ar katra modeļa cenu vēsturi.",
    "h1": "Tava ģitāra <span>par labāko cenu</span><small>Ģitāru cenu salīdzināšana</small>",
    "searchPh": "Meklē: Strat, Les Paul, Yamaha, Ibanez…", "searchBtn": "Meklēt", "searchLabel": "Meklēt ģitāru",
    "guitars": "ģitāras", "storesWord": "veikali", "catalog": "Katalogs",
    "dealsH": "Lielākās cenu atšķirības starp veikaliem", "dealsBadge": "−{p}% pret dārgāko",
    "catsH": "Pārlūko pēc kategorijas", "soon": "drīzumā", "storesH": "Salīdzinātie veikali",
    "howH": "Kā tas darbojas",
    "steps": ["Katru dienu pārbaudām katras ģitāras cenu, pieejamību un foto veikalos, kas piegādā uz Latviju.",
              "Saglabājam cenu vēsturi, lai tu redzētu, vai cena tiešām ir laba vai parasti mēdz būt zemāka.",
              "Ja vēlies, nosūtīsim tev e-pastu, kad cena kritīsies."],
    "affiliate": "Dažas saites uz veikaliem ir partneru saites: ja tu iepērcies, guitle var saņemt komisiju – tev tas neko papildus nemaksā.",
    "legal": "Juridiskā informācija", "privacy": "Privātums", "cookies": "Sīkdatnes", "otherCountries": "guitle citās valstīs:",
    "updated": "Dati atjaunināti {d}", "home": "Sākums",
    "kinds": {"electrica": ("Elektriskās ģitāras", "Elektriskās", "Meklē elektriskajās ģitārās: modelis, zīmols, krāsa…"),
              "acustica": ("Akustiskās ģitāras", "Akustiskās", "Meklē akustiskajās ģitārās: modelis, zīmols, koks…"),
              "clasica": ("Klasiskās ģitāras", "Klasiskās", "Meklē klasiskajās ģitārās: modelis, zīmols, flamenko…"),
              "bajo": ("Elektriskās un akustiskās basģitāras", "Basģitāras", "Meklē basģitārās: modelis, zīmols, 5 stīgu…"),
              "ampli": ("Ģitāru un basģitāru pastiprinātāji", "Pastiprinātāji", "Meklē pastiprinātājos: modelis, zīmols, kombo, galva…"),
              "pedal": ("Efektu pedāļi", "Efekti", "Meklē efektu pedāļos: modelis, zīmols, efekts…"),
              "teclado": ("Taustiņinstrumenti un digitālās klavieres", "Taustiņinstrumenti", "Meklē taustiņinstrumentos: modelis, zīmols…"),
              "micro": ("Mikrofoni", "Mikrofoni", "Meklē mikrofonos: modelis, zīmols, tips…"),
              "estuche": ("Futrāļi un somas", "Futrāļi", "Meklē futrāļos un somās: modelis, zīmols…"),
              "varios": ("Ģitāru piederumi", "Piederumi", "Meklē piederumos: stīgas, mediatori, siksnas, kabeļi…")},
    # Lo que se cuenta en cada categoría de equipo (portada y lista) y, si no son solo guitarras, el total.
    "nouns": {"bajo": "basģitāras", "ampli": "pastiprinātāji", "pedal": "pedāļi", "teclado": "taustiņinstrumenti",
              "micro": "mikrofoni", "estuche": "futrāļi", "varios": "piederumi"},
    "allWord": "preces",
    "anyPrice": "Jebkura cena", "upTo": "Līdz {v}", "over": "Virs {v}", "brandLabel": "Zīmols", "priceLabel": "Cena",
    "showLabel": "Rādīt", "showAll": "Visu", "showMulti": "Vairākos veikalos", "showStock": "Ir noliktavā",
    "showLow": "Par zemāko cenu", "showLh": "Tikai kreiļiem", "loading": "Ielādē katalogu…", "sortLabel": "Kārtot",
    "sorts": ["Visvairāk veikalu", "Zemākā cena", "Augstākā cena", "Lielākais ietaupījums starp veikaliem", "Nosaukums"],
    "moreBtn": "Rādīt vairāk", "sections": "Sadaļas", "searchAria": "Meklēt",
    "bestPrice": "labākā cena", "inStock": "ir noliktavā", "noStock": "nav noliktavā", "goLong": "Uz veikalu", "goShort": "Veikals",
    "store": "veikalā", "stores": "veikalos", "lh": "kreiļiem", "storesH3": "Veikali", "historyH3": "Cenu vēsture",
    "amazon": "", "titleFrom": "{name}: cena no {price} {where}", "inN": "{n} veikalos", "inS": "veikalā {s}",
    "whereMany": "veikalā {s} · salīdzināta {n} veikalos", "whereDiff": ", starpība līdz {d}",
    "desc": "{name} no {price} veikalā {s}. Salīdzini cenu {n} {stores} ({list}) un apskati cenu vēsturi, lai zinātu, "
            "vai tagad ir īstais brīdis pirkt.",
    "alertTitle": "Cenas paziņojums", "alertWait": "Mirkli…", "alertSaving": "Saglabājam tavu atbildi.",
    "alertGo": "Uz guitle", "alertBad": ["Nederīga saite", "Nokopē pilnu saiti no e-pasta un mēģini vēlreiz."],
    "alertDone": ["Paziņojums apstiprināts!", "Nosūtīsim tev e-pastu, tiklīdz cena kritīsies. Katrā e-pastā ir saite, "
                                              "lai atteiktos no paziņojuma."],
    "alertGone": ["Paziņojums dzēsts", "Par šo paziņojumu tu vairs nesaņemsi e-pastus. Tava adrese ir dzēsta no mūsu saraksta."],
    "alertMissing": ["Paziņojums nav atrasts", "Iespējams, tas jau ir apstiprināts vai dzēsts, vai arī pagājušas vairāk nekā "
                                               "7 dienas bez apstiprinājuma. Vajag palīdzību? Raksti mums uz hola@guitle.com."],
    "js": {"loadErr": "Neizdevās ielādēt katalogu.", "allBrands": "Visi zīmoli", "all": "Visi", "low": "Zemākā",
           "save": "Ietaupi {v}", "lh": "kreiļiem", "store": "veikals", "stores": "veikali",
           # {many} left out: Latvian would need the genitive ("neviena ģitāra / neviens pastiprinātājs").
           "empty": "Ar šiem filtriem nekas netika atrasts.", "more": "Rādīt vairāk (vēl {n})",
           "meta": "{a} no {b} ({many}) · {m} ar cenām vairākos veikalos · atjaunināts {d}", "best": "labākā cena",
           "inStock": "ir noliktavā", "noStock": "nav noliktavā", "goLong": "Uz veikalu", "goShort": "Veikals", "close": "Aizvērt",
           "inAt": "veikalā {s}", "saveMax": " · līdz {v} lētāk nekā dārgākajā", "atLow": "Par zemāko reģistrēto cenu",
           "lowTag": "Zemākā reģistrētā: {v}", "storesH": "Veikali", "evolH": "Cenu vēsture",
           "histErr": "Neizdevās ielādēt cenu vēsturi.", "histSoon": "Cenu vēsture papildināsies nākamajās dienās.",
           "many": "ģitāras",
           "types": {"ST": "ST tipa", "T": "T tipa", "Semihueca": "Pusakustiskās", "Offset / Retro": "Offset / retro",
                     "Moderna / Metal": "Modernās / metāls", "Otras": "Citas", "Auditorio / Concierto": "Auditorium / koncerta",
                     "12 cuerdas": "12 stīgu", "Tamaño reducido": "Mazāka izmēra", "Clásica": "Klasiskās",
                     "Flamenca": "Flamenko", "Electroclásica": "Elektroklasiskās",
                     "4 cuerdas": "4 stīgu", "5 cuerdas": "5 stīgu", "6 cuerdas o más": "6 un vairāk stīgu",
                     "Acústico": "Akustiskās basģitāras", "Fretless": "Fretless", "Escala corta": "Īsā mensūra",
                     "Combo": "Kombo", "Cabezal": "Pastiprinātāju galvas", "Pantalla": "Skaļruņu kabineti",
                     "Para bajo": "Basģitārai", "Para acústica": "Akustiskajai ģitārai",
                     "De auriculares y portátil": "Austiņu un mini pastiprinātāji", "Para eléctrica": "Elektriskajai ģitārai",
                     "Para clásica": "Klasiskajai ģitārai", "Overdrive y distorsión": "Overdrive un distortion",
                     "Modulación": "Modulācija", "Compresor": "Kompresori", "Wah y volumen": "Wah un skaļums",
                     "Octavador y pitch": "Oktāveri un pitch", "Ecualizador": "Ekvalaizeri", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintezatori", "Afinador": "Skaņotāji", "Multiefectos": "Multiefekti",
                     "Reverb": "Reverb", "Piano digital": "Digitālās klavieres",
                     "Teclado portátil": "Portatīvie taustiņinstrumenti",
                     "Piano de escenario": "Skatuves klavieres", "Controlador MIDI": "MIDI kontrolleri",
                     "Piano acústico": "Akustiskās klavieres",
                     "Dinámico": "Dinamiskie", "Condensador": "Kondensatora", "Inalámbrico": "Bezvadu",
                     "Para instrumento": "Instrumentu mikrofoni", "De cinta": "Lentes mikrofoni", "Cuerdas": "Stīgas",
                     "Púas": "Mediatori", "Correas": "Siksnas", "Cables": "Kabeļi", "Afinadores": "Skaņotāji",
                     "Cejillas": "Kapo", "Soportes": "Statīvi", "Pastillas": "Skaņas noņēmēji", "Recambios": "Rezerves daļas",
                     "Mantenimiento": "Kopšana"},
           "wait": "Šim modelim sekojam jau {n} {days}", "day": "dienu", "days": "dienas",
           "waitSub": "Vērtējums kļūst uzticamāks, kad uzkrājas dažu nedēļu cenu vēsture.",
           "min": "Zemākā reģistrētā cena", "minSub": "Tik lētu mēs to vēl neesam redzējuši.",
           "minBelow": " {p}% zem 30 dienu vidējās cenas.",
           "good": "Labs brīdis pirkt: {p}% zem vidējās cenas", "goodSub": "30 dienu vidējā cena: {avg}.",
           "bad": "Pašlaik par {p}% dārgāk nekā parasti",
           "badSub": "Ja nesteidzies, pagaidi: 30 dienu vidējā cena ir {avg}, zemākā – {min}.",
           "normal": "Parasta cena", "normalSub": "Atbilst 30 dienu vidējai cenai ({avg}). Zemākā reģistrētā: {min}.",
           "today": "cena šodien", "lowest": "zemākā ({d})", "highest": "augstākā", "avg": "{n} dienu vidējā",
           "since": "Sekojam kopš {d}", "noHist": "Cenu vēstures vēl nav.", "pvp": "Ieteicamā cena", "bestLine": "Labākā cena",
           "alertOpen": "Paziņo man, ja cena kritīsies", "emailPh": "tu@piemers.lv", "emailLabel": "Tavs e-pasts",
           "targetPh": "Maks. cena (nav obligāti)", "targetLabel": "Vēlamā cena eiro", "alertBtn": "Paziņot man",
           "alertLegal": "Bez maksas un bez reģistrācijas. Noklikšķinot uz „Paziņot man”, tu piekrīti mūsu "
                         "<a href=\"/lv/legal.html#privatums\">privātuma politikai</a>: tavu e-pastu izmantosim tikai šim "
                         "paziņojumam, un atteikties var ar vienu klikšķi.",
           "alertOk": "<b>Gatavs!</b> Pēc dažām minūtēm uz {email} saņemsi e-pastu, lai apstiprinātu paziņojumu "
                      "(pārbaudi arī mēstuļu mapi).",
           "alertErr": "Neizdevās saglabāt paziņojumu. Pārbaudi e-pasta adresi un mēģini vēlreiz."},
    "mail": {"tagline": "ģitāras par labāko cenu",
             "footer": "guitle katru dienu salīdzina mūzikas veikalu cenas. Tu saņem šo e-pastu, jo vietnē guitle.com pieteici "
                       "cenas paziņojumu. Pārzinis: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Privātums", "confirmSubject": "Apstiprini savu guitle cenas paziņojumu",
             "confirmTitle": "Apstiprini savu cenas paziņojumu", "asked": "Tu lūdzi mums paziņot, kad cena kritīsies{target}:",
             "below": " zem <b>{v}</b>", "confirmAsk": "Lūdzu, apstiprini, ka vēlies saņemt paziņojumu uz šo adresi:",
             "confirmBtn": "Apstiprināt paziņojumu",
             "notYou": "Ja tas nebiji tu, neko nedari: neapstiprinātie paziņojumi pēc 7 dienām tiek dzēsti automātiski.",
             "dropSubject": "Cena kritusies: {name} tagad {price}", "dropTitle": "Cena ir kritusies!", "nowAt": "veikalā {s} · iepriekš {v}",
             "seeAll": "Skatīt cenas visos veikalos",
             "check": "Cenas mainās katru dienu: pirms pirkuma pārbaudi tās veikala vietnē. Vairs neinteresē?",
             "stop": "Atteikties no šī paziņojuma"},
}

# Supervisory authority: the text says "your country's data protection supervisory authority";
# in Latvia that is the Datu valsts inspekcija (DVI) — usable via SITES["lv"]["legal_replace"] if wanted:
# ("savas valsts datu aizsardzības uzraudzības iestādē", "Datu valsts inspekcijā").
LEGAL_LANG = ("Juridiskā informācija un privātums", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Juridiskā informācija un privātums</h1>
<p class="muted">Pēdējās izmaiņas: 2026. gada 28. oktobris. Šis ir tulkojums; šaubu gadījumā noteicošā ir <a href="/legal.html">spāņu valodas versija</a>.</p>

<h2 id="aviso">Juridiskā informācija</h2>
<p>Šīs vietnes uzturētājs ir <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Spānija
(Spānijas nodokļu maksātāja numurs NIF 17747339X), kontakti
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, vietne guitle.com. Darbība: mūzikas instrumentu cenu salīdzināšana un partneru reklāma.
Mitināšana: GitHub Pages (GitHub, Inc.).</p>

<h2 id="noteikumi">Lietošanas noteikumi</h2>
<p>guitle ir cenu salīdzināšanas vietne un pati neko nepārdod. Mēs rādām cenas, ko veikali publicē savās vietnēs, un sniedzam saites uz tiem,
lai tu varētu iepirkties tieši veikalā. Par pirkumu, piegādi, garantiju un atgriešanu atbild attiecīgais veikals.</p>
<ul>
<li><b>Cenas ir orientējošas.</b> Mēs regulāri pārbaudām cenas, taču tās var mainīties jebkurā brīdī. Spēkā vienmēr ir cena, ko veikals rāda pasūtījuma brīdī.</li>
<li><b>Precizitāte netiek garantēta.</b> Mēs cenšamies, lai produkti, cenas un pieejamība būtu pareizi, taču kļūdas ir iespējamas. Ja pamani kādu, dod mums ziņu.</li>
<li><b>Preču zīmes un attēli.</b> Preču zīmes, produktu nosaukumi un attēli pieder to īpašniekiem un tiek izmantoti tikai produktu identificēšanai.</li>
<li><b>guitle saturs.</b> guitle dizains, logotips, teksti un datu apkopojumi pieder vietnes uzturētājam. Masveida kopēšana vai komerciāla izmantošana bez atļaujas nav atļauta.</li>
</ul>

<h2 id="affiliate">Partneru saites</h2>
<p>Dažas saites uz veikaliem ir partneru saites: ja tu iepērcies pēc saites atvēršanas, veikals var samaksāt guitle nelielu komisiju. Tev cena
nemainās. Komisijas neietekmē rezultātu secību: veikali vienmēr ir sakārtoti pēc cenas, sākot ar lētāko.</p>

<h2 id="privatums">Privātuma politika</h2>
<p>Lai lietotu vietni, guitle neprasa nekādus personas datus: nav reģistrācijas, jaunumu vēstuļu, analītikas vai reklāmas rīku,
kas tev sekotu. Mēs tikai anonīmi skaitām apmeklējumus un, ja piesakies cenas paziņojumam, saglabājam tā vajadzībām tavu e-pasta adresi.</p>
<ul>
<li><b>Cenu paziņojumi.</b> Ja vēlies uzzināt, kad produkta cena kritīsies, mēs saglabājam tavu e-pasta adresi, produktu,
tā cenu attiecīgajā dienā un tavu vēlamo cenu, ja to norādi. Mēs tos izmantojam tikai apstiprinājuma e-pasta un šī produkta paziņojumu nosūtīšanai,
nekad reklāmai, un nevienam tos nenododam. Juridiskais pamats: tava piekrišana (Vispārīgās datu aizsardzības regulas 6. panta 1. punkta a) apakšpunkts), ko tu
sniedz, piesakot paziņojumu un apstiprinot savu e-pastu. Dati tiek glabāti Google Cloud Firestore (Google Ireland Ltd., serveris Madridē); e-pastus sūtām
no mūsu pastkastes hola@guitle.com (DonDominio, Spānija). Neapstiprinātie paziņojumi tiek dzēsti pēc 7 dienām; apstiprinātie tiek glabāti, līdz tu atsakies,
izmantojot saiti katrā e-pastā (paziņojums tiek dzēsts uzreiz), vai lūdz mums tos dzēst.</li>
<li><b>Iestatījumi tavā pārlūkā.</b> Filtri un izvēlētais skats tiek saglabāti tava pārlūka lokālajā krātuvē (localStorage) un netiek sūtīti uz nevienu serveri.</li>
<li><b>Mitināšana.</b> Vietne tiek mitināta GitHub Pages (GitHub, Inc.). Kā jebkurš tīmekļa serveris, GitHub tehnisku un drošības apsvērumu dēļ
var reģistrēt katra apmeklētāja IP adresi. GitHub piedalās ES–ASV Datu privātuma regulējumā (EU-US Data Privacy Framework).</li>
<li><b>Apmeklējumu skaitītājs.</b> Katra lapa palielina anonīmu skaitītāju par 1: diena, skatītā lapa, vietne, no kuras atnāci (piemēram, google.com), ko
ieraksti kataloga meklētājā un, ja pārej uz veikalu, veikala nosaukums. Nekādu sīkdatņu, IP adreses vai kā cita, kas tevi identificētu. Skaitītāji tiek
glabāti Google Cloud Firestore (Google Ireland Ltd.) serverī Eiropas Savienībā (Madridē).</li>
<li><b>Citu pieprasījumu trešajām personām nav.</b> Fonti, grafiki un produktu foto tiek ielādēti no guitle.com.</li>
<li><b>Pārejot uz veikalu.</b> Kad pāriec uz veikalu, tu atstāj guitle, un tad ir spēkā šī veikala privātuma politika.</li>
</ul>
<p><b>Tavas tiesības.</b> Tu vari izmantot savas tiesības piekļūt datiem, labot tos, dzēst, iebilst pret apstrādi, ierobežot to un pārnest datus,
rakstot uz <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Tu vari arī iesniegt sūdzību datu aizsardzības uzraudzības iestādē,
piemēram, Spānijas Agencia Española de Protección de Datos vai savas valsts datu aizsardzības uzraudzības iestādē.
Pārzinis: juridiskajā informācijā minētais vietnes uzturētājs.</p>

<h2 id="cookies">Sīkdatnes</h2>
<p>guitle neizmanto sīkdatnes – ne savas, ne trešo personu –, tāpēc tu neredzi sīkdatņu paziņojumu. Mēs izmantojam tikai pārlūka lokālo
krātuvi, lai atcerētos tavus iestatījumus. Veikali, uz kuriem sniedzam saites, savās vietnēs var izmantot savas sīkdatnes.</p>
""")
