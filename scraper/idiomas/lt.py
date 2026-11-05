# Lietuvių (lt) — guitle.com texts. Country code in URLs: "lt" (the alertLegal link is rewritten by strings()).
# Polite "jūs" form: informal "tu" is unusual on Lithuanian shop and comparison sites.
# Plurals: Lithuanian has three forms after numbers (1 gitara, 2–9 gitaros, 10–20/…0 gitarų). Counted labels
# ("guitars", "storesWord", "nouns", "allWord", "many") use the genitive plural ("gitarų"), the usual choice for
# fixed labels next to large totals; it also fits "empty" ("… gitarų nerasta") and "meta" ("… iš {b} gitarų").
# js "store"/"stores" (shown next to small numbers, 1 vs 2+) use "parduotuvė"/"parduotuvės".
# "wait" only runs for n < 7, so "1 dieną" / "2–6 dienas" are exact.

# Anchor of the privacy section in LEGAL_LANG (add to intl._anchor: "lt": "privatumas").
PRIVACY_ANCHOR = "privatumas"

MONEY_NOTE = ("Lithuanian format: amount, no-break space, euro sign after it: 1299 € (four digits usually without a "
              "thousands separator; from five digits a space: 12 999 €), decimals with a comma: 1299,90 €. "
              "Percentages take a space: 15 %. intl.money() falls into the default branch (narrow no-break space as "
              "thousands separator), which is also acceptable; for exactly \"1299 €\" add a branch for lang 'lt' with "
              "no separator below 10 000.")

KINDS_LANG = {"electrica": "elektrines-gitaros", "acustica": "akustines-gitaros", "clasica": "klasikines-gitaros",
              "pack": "gitaru-rinkiniai", "bajo": "bosines-gitaros", "ampli": "stiprintuvai", "pedal": "efektu-pedalai",
              "teclado": "klavisiniai", "micro": "mikrofonai", "estuche": "deklai-krepsiai", "varios": "priedai"}

PACK_LANG = ("Gitarų rinkiniai", "Rinkiniai", "Ieškokite tarp rinkinių: modelis, gamintojas, su stiprintuvu…", "rinkinių",
             {"Eléctrica": "Elektrinė", "Acústica": "Akustinė"})

T_LANG = {
    "tagline": "gitaros už geriausią kainą", "homeLabel": "guitle, pradžia",
    "homeTitle": "guitle · gitarų kainų palyginimas",
    "homeDesc": "guitle lygina gitarų kainas: elektrinės, akustinės ir klasikinės gitaros parduotuvėse, pristatančiose "
                "į Lietuvą, su kiekvieno modelio kainų istorija.",
    "h1": "Jūsų gitara <span>už geriausią kainą</span><small>Gitarų kainų palyginimas</small>",
    "searchPh": "Ieškokite: Strat, Les Paul, Yamaha, Ibanez…", "searchBtn": "Ieškoti", "searchLabel": "Ieškoti gitaros",
    "guitars": "gitarų", "storesWord": "parduotuvių", "catalog": "Katalogas",
    "dealsH": "Didžiausi kainų skirtumai tarp parduotuvių", "dealsBadge": "−{p} %, palyginti su brangiausia",
    "catsH": "Naršykite pagal kategoriją", "soon": "netrukus", "storesH": "Lyginamos parduotuvės",
    "howH": "Kaip tai veikia",
    "steps": ["Kasdien tikriname kiekvienos gitaros kainą, likutį ir nuotrauką parduotuvėse, pristatančiose į Lietuvą.",
              "Saugome kainų istoriją, kad matytumėte, ar kaina tikrai gera, ar paprastai būna mažesnė.",
              "Jei norite, atsiųsime jums el. laišką, kai kaina sumažės."],
    "affiliate": "Kai kurios nuorodos į parduotuves yra partnerių nuorodos: jei pirksite, guitle gali gauti komisinį atlygį – "
                 "jums tai nieko papildomai nekainuoja.",
    "legal": "Teisinė informacija", "privacy": "Privatumas", "cookies": "Slapukai", "otherCountries": "guitle kitose šalyse:",
    "updated": "Duomenys atnaujinti {d}", "home": "Pradžia",
    "kinds": {"electrica": ("Elektrinės gitaros", "Elektrinės", "Ieškokite tarp elektrinių gitarų: modelis, gamintojas, spalva…"),
              "acustica": ("Akustinės gitaros", "Akustinės", "Ieškokite tarp akustinių gitarų: modelis, gamintojas, mediena…"),
              "clasica": ("Klasikinės gitaros", "Klasikinės", "Ieškokite tarp klasikinių gitarų: modelis, gamintojas, flamenkas…"),
              "bajo": ("Elektrinės ir akustinės bosinės gitaros", "Bosinės", "Ieškokite tarp bosinių gitarų: modelis, gamintojas, 5 stygų…"),
              "ampli": ("Gitarų ir bosinių gitarų stiprintuvai", "Stiprintuvai", "Ieškokite tarp stiprintuvų: modelis, gamintojas, kombo, galva…"),
              "pedal": ("Efektų pedalai", "Efektai", "Ieškokite tarp efektų pedalų: modelis, gamintojas, efektas…"),
              "teclado": ("Klavišiniai ir skaitmeniniai pianinai", "Klavišiniai", "Ieškokite tarp klavišinių: modelis, gamintojas…"),
              "micro": ("Mikrofonai", "Mikrofonai", "Ieškokite tarp mikrofonų: modelis, gamintojas, tipas…"),
              "estuche": ("Dėklai ir krepšiai", "Dėklai", "Ieškokite tarp dėklų ir krepšių: modelis, gamintojas…"),
              "varios": ("Gitarų priedai", "Priedai", "Ieškokite tarp priedų: stygos, mediatoriai, diržai, laidai…")},
    # Lo que se cuenta en cada categoría de equipo (portada y lista) y, si no son solo guitarras, el total.
    "nouns": {"bajo": "bosinių gitarų", "ampli": "stiprintuvų", "pedal": "pedalų", "teclado": "klavišinių",
              "micro": "mikrofonų", "estuche": "dėklų", "varios": "priedų"},
    "allWord": "prekių",
    "anyPrice": "Bet kokia kaina", "upTo": "Iki {v}", "over": "Virš {v}", "brandLabel": "Gamintojas", "priceLabel": "Kaina",
    "showLabel": "Rodyti", "showAll": "Viską", "showMulti": "Keliose parduotuvėse", "showStock": "Yra sandėlyje",
    "showLow": "Už mažiausią kainą", "showLh": "Tik kairiarankiams", "loading": "Įkeliamas katalogas…", "sortLabel": "Rikiuoti",
    "sorts": ["Daugiausia parduotuvių", "Mažiausia kaina", "Didžiausia kaina", "Didžiausias sutaupymas tarp parduotuvių",
              "Pavadinimas"],
    "moreBtn": "Rodyti daugiau", "sections": "Skyriai", "searchAria": "Ieškoti",
    "bestPrice": "geriausia kaina", "inStock": "yra sandėlyje", "noStock": "nėra sandėlyje", "goLong": "Į parduotuvę",
    "goShort": "Eiti",
    "store": "parduotuvėje", "stores": "parduotuvėse", "lh": "kairiarankiams", "storesH3": "Parduotuvės",
    "historyH3": "Kainų istorija",
    "amazon": "", "titleFrom": "{name}: kaina nuo {price} {where}", "inN": "{n} parduotuvėse", "inS": "parduotuvėje {s}",
    "whereMany": "parduotuvėje {s} · palyginta {n} parduotuvėse", "whereDiff": ", skirtumas iki {d}",
    "desc": "{name} nuo {price} parduotuvėje {s}. Palyginkite kainą {n} {stores} ({list}) ir peržiūrėkite kainų istoriją, "
            "kad žinotumėte, ar dabar tinkamas metas pirkti.",
    "alertTitle": "Pranešimas apie kainą", "alertWait": "Akimirką…", "alertSaving": "Išsaugome jūsų atsakymą.",
    "alertGo": "Į guitle", "alertBad": ["Netinkama nuoroda", "Nukopijuokite visą nuorodą iš el. laiško ir bandykite dar kartą."],
    "alertDone": ["Pranešimas patvirtintas!", "Parašysime jums, kai tik kaina sumažės. Kiekviename laiške yra nuoroda "
                                              "pranešimo atsisakyti."],
    "alertGone": ["Pranešimas ištrintas", "Apie šį pranešimą laiškų daugiau negausite. Jūsų adresą ištrynėme iš savo sąrašo."],
    "alertMissing": ["Pranešimas nerastas", "Galbūt jis jau patvirtintas ar ištrintas arba praėjo daugiau nei 7 dienos be "
                                            "patvirtinimo. Reikia pagalbos? Rašykite mums hola@guitle.com."],
    "js": {"loadErr": "Nepavyko įkelti katalogo.", "allBrands": "Visi gamintojai", "all": "Visi", "low": "Mažiausia",
           "save": "Sutaupykite {v}", "lh": "kairiarankiams", "store": "parduotuvė", "stores": "parduotuvės",
           "empty": "Pagal šiuos filtrus {many} nerasta.", "more": "Rodyti daugiau (liko {n})",
           "meta": "{a} iš {b} {many} · {m} galima palyginti keliose parduotuvėse · atnaujinta {d}", "best": "geriausia kaina",
           "inStock": "yra sandėlyje", "noStock": "nėra sandėlyje", "goLong": "Į parduotuvę", "goShort": "Eiti", "close": "Uždaryti",
           "inAt": "parduotuvėje {s}", "saveMax": " · iki {v} pigiau nei brangiausioje", "atLow": "Už mažiausią užfiksuotą kainą",
           "lowTag": "Mažiausia užfiksuota: {v}", "storesH": "Parduotuvės", "evolH": "Kainų istorija",
           "histErr": "Nepavyko įkelti kainų istorijos.", "histSoon": "Kainų istorija pasipildys per artimiausias dienas.",
           "many": "gitarų",
           "types": {"ST": "ST tipo", "T": "T tipo", "Semihueca": "Pusiau akustinės", "Offset / Retro": "Offset / retro",
                     "Moderna / Metal": "Modernios / metalas", "Otras": "Kitos", "Auditorio / Concierto": "Auditorium / koncertinės",
                     "12 cuerdas": "12 stygų", "Tamaño reducido": "Mažesnio dydžio", "Clásica": "Klasikinės",
                     "Flamenca": "Flamenko", "Electroclásica": "Elektroklasikinės",
                     "4 cuerdas": "4 stygų", "5 cuerdas": "5 stygų", "6 cuerdas o más": "6 ir daugiau stygų",
                     "Acústico": "Akustinės bosinės", "Fretless": "Fretless", "Escala corta": "Trumpos menzūros",
                     "Combo": "Kombo", "Cabezal": "Stiprintuvų galvos", "Pantalla": "Kabinetai",
                     "Para bajo": "Bosinėms gitaroms", "Para acústica": "Akustinėms gitaroms",
                     "De auriculares y portátil": "Ausinių ir mini stiprintuvai", "Para eléctrica": "Elektrinėms gitaroms",
                     "Para clásica": "Klasikinėms gitaroms", "Overdrive y distorsión": "Overdrive ir distortion",
                     "Modulación": "Moduliacija", "Compresor": "Kompresoriai", "Wah y volumen": "Wah ir garsumas",
                     "Octavador y pitch": "Oktaveriai ir pitch", "Ecualizador": "Ekvalaizeriai", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintezatoriai", "Afinador": "Derintuvai", "Multiefectos": "Multiefektai",
                     "Reverb": "Reverb", "Piano digital": "Skaitmeniniai pianinai", "Teclado portátil": "Nešiojami klavišiniai",
                     "Piano de escenario": "Sceniniai pianinai", "Controlador MIDI": "MIDI valdikliai",
                     "Piano acústico": "Akustiniai pianinai",
                     "Dinámico": "Dinaminiai", "Condensador": "Kondensatoriniai", "Inalámbrico": "Belaidžiai",
                     "Para instrumento": "Instrumentiniai", "De cinta": "Juostiniai", "Cuerdas": "Stygos",
                     "Púas": "Mediatoriai", "Correas": "Diržai", "Cables": "Laidai", "Afinadores": "Derintuvai",
                     "Cejillas": "Kapodastrai", "Soportes": "Stovai", "Pastillas": "Garso nuėmėjai",
                     "Recambios": "Atsarginės dalys", "Mantenimiento": "Priežiūra"},
           "wait": "Šį modelį stebime jau {n} {days}", "day": "dieną", "days": "dienas",
           "waitSub": "Įvertinimas tampa patikimesnis, kai sukaupiama kelių savaičių kainų istorija.",
           "min": "Mažiausia užfiksuota kaina", "minSub": "Pigiau jo dar nesame matę.",
           "minBelow": " {p} % mažiau nei 30 dienų vidurkis.",
           "good": "Tinkamas metas pirkti: {p} % mažiau nei vidutinė kaina", "goodSub": "30 dienų vidurkis: {avg}.",
           "bad": "Šiuo metu {p} % brangiau nei įprastai",
           "badSub": "Jei neskubate, palaukite: 30 dienų vidurkis yra {avg}, o mažiausia kaina – {min}.",
           "normal": "Įprasta kaina", "normalSub": "Atitinka 30 dienų vidurkį ({avg}). Mažiausia užfiksuota: {min}.",
           "today": "kaina šiandien", "lowest": "mažiausia ({d})", "highest": "didžiausia", "avg": "{n} d. vidurkis",
           "since": "Stebima nuo {d}", "noHist": "Kainų istorijos dar nėra.", "pvp": "Rekomenduojama kaina",
           "bestLine": "Geriausia kaina",
           "alertOpen": "Praneškite, kai kaina sumažės", "emailPh": "vardas@pavyzdys.lt", "emailLabel": "Jūsų el. paštas",
           "targetPh": "Didž. kaina (neprivaloma)", "targetLabel": "Norima kaina eurais", "alertBtn": "Pranešti man",
           "alertLegal": "Nemokamai ir be registracijos. Spustelėdami „Pranešti man“ sutinkate su mūsų "
                         "<a href=\"/lt/legal.html#privatumas\">privatumo politika</a>: jūsų el. paštą naudosime tik šiam "
                         "pranešimui, o atsisakyti galėsite vienu paspaudimu.",
           "alertOk": "<b>Atlikta!</b> Po kelių minučių adresu {email} gausite laišką pranešimui patvirtinti "
                      "(patikrinkite ir šlamšto aplanką).",
           "alertErr": "Nepavyko išsaugoti pranešimo. Patikrinkite el. pašto adresą ir bandykite dar kartą."},
    "mail": {"tagline": "gitaros už geriausią kainą",
             "footer": "guitle kasdien lygina muzikos parduotuvių kainas. Šį laišką gavote, nes svetainėje guitle.com užsisakėte "
                       "pranešimą apie kainą. Duomenų valdytojas: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Privatumas", "confirmSubject": "Patvirtinkite guitle pranešimą apie kainą",
             "confirmTitle": "Patvirtinkite pranešimą apie kainą", "asked": "Paprašėte pranešti, kai kaina sumažės{target}:",
             "below": " žemiau <b>{v}</b>", "confirmAsk": "Patvirtinkite, kad norite gauti pranešimą šiuo adresu:",
             "confirmBtn": "Patvirtinti pranešimą",
             "notYou": "Jei tai buvote ne jūs, nieko nedarykite: nepatvirtinti pranešimai automatiškai ištrinami po 7 dienų.",
             "dropSubject": "Kaina sumažėjo: {name} dabar {price}", "dropTitle": "Kaina sumažėjo!",
             "nowAt": "parduotuvėje {s} · anksčiau {v}",
             "seeAll": "Žiūrėti kainas visose parduotuvėse",
             "check": "Kainos keičiasi kasdien: prieš pirkdami patikrinkite jas parduotuvės svetainėje. Nebedomina?",
             "stop": "Atsisakyti šio pranešimo"},
}

# Supervisory authority: the text says "your country's data protection supervisory authority";
# in Lithuania that is the Valstybinė duomenų apsaugos inspekcija (VDAI) — usable via SITES["lt"]["legal_replace"]:
# ("savo šalies duomenų apsaugos priežiūros institucijai", "Valstybinei duomenų apsaugos inspekcijai").
LEGAL_LANG = ("Teisinė informacija ir privatumas", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Teisinė informacija ir privatumas</h1>
<p class="muted">Atnaujinta 2026 m. spalio 28 d. Tai vertimas; kilus abejonių, viršenybę turi <a href="/legal.html">ispaniška versija</a>.</p>

<h2 id="aviso">Teisinė informacija</h2>
<p>Šią svetainę valdo <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Ispanija
(Ispanijos mokesčių mokėtojo kodas NIF 17747339X), kontaktai
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, svetainė guitle.com. Veikla: muzikos instrumentų kainų palyginimas ir partnerių reklama.
Prieglobos paslaugos: GitHub Pages (GitHub, Inc.).</p>

<h2 id="salygos">Naudojimo sąlygos</h2>
<p>guitle yra kainų palyginimo svetainė ir pati nieko neparduoda. Rodome kainas, kurias parduotuvės skelbia savo svetainėse, ir pateikiame
nuorodas į jas, kad pirktumėte tiesiogiai parduotuvėje. Už pirkimą, pristatymą, garantiją ir grąžinimą atsako kiekviena parduotuvė.</p>
<ul>
<li><b>Kainos yra orientacinės.</b> Kainas tikriname reguliariai, tačiau jos gali bet kada pasikeisti. Galioja visada ta kaina, kurią parduotuvė rodo užsakymo metu.</li>
<li><b>Tikslumas negarantuojamas.</b> Stengiamės, kad prekės, kainos ir likučiai būtų teisingi, tačiau klaidų gali pasitaikyti. Pastebėję klaidą, praneškite mums.</li>
<li><b>Prekių ženklai ir nuotraukos.</b> Prekių ženklai, prekių pavadinimai ir nuotraukos priklauso jų savininkams ir naudojami tik prekėms identifikuoti.</li>
<li><b>guitle turinys.</b> guitle dizainas, logotipas, tekstai ir duomenų rinkiniai priklauso svetainės valdytojui. Masinis kopijavimas ar komercinis naudojimas be leidimo draudžiamas.</li>
</ul>

<h2 id="affiliate">Partnerių nuorodos</h2>
<p>Kai kurios nuorodos į parduotuves yra partnerių nuorodos: jei perėję nuoroda ką nors nusipirksite, parduotuvė gali sumokėti guitle nedidelį
komisinį atlygį. Jums kaina nesikeičia. Komisiniai neturi įtakos rezultatų tvarkai: parduotuvės visada rikiuojamos pagal kainą, pigiausia pirmiausia.</p>

<h2 id="privatumas">Privatumo politika</h2>
<p>Norint naudotis svetaine, guitle neprašo jokių asmens duomenų: jokios registracijos, naujienlaiškių, analitikos ar reklamos įrankių,
kurie jus sektų. Apsilankymus skaičiuojame tik anonimiškai, o jei užsisakote pranešimą apie kainą, šiam pranešimui išsaugome jūsų el. pašto adresą.</p>
<ul>
<li><b>Pranešimai apie kainą.</b> Jei norite sužinoti, kada prekės kaina sumažės, išsaugome jūsų el. pašto adresą, prekę,
jos tos dienos kainą ir, jei ją nurodėte, jūsų norimą kainą. Juos naudojame tik patvirtinimo laiškui ir šios prekės pranešimams siųsti,
niekada reklamai, ir niekam jų neperduodame. Teisinis pagrindas: jūsų sutikimas (Bendrojo duomenų apsaugos reglamento 6 straipsnio 1 dalies a punktas),
kurį duodate užsakydami pranešimą ir patvirtindami savo el. paštą. Duomenys saugomi Google Cloud Firestore (Google Ireland Ltd., serveris Madride); laiškus
siunčiame iš mūsų pašto dėžutės hola@guitle.com (DonDominio, Ispanija). Nepatvirtinti pranešimai ištrinami po 7 dienų; patvirtinti saugomi, kol jų atsisakysite
paspaudę nuorodą bet kuriame laiške (pranešimas iš karto ištrinamas) arba paprašysite mūsų juos ištrinti.</li>
<li><b>Nustatymai jūsų naršyklėje.</b> Filtrai ir pasirinktas vaizdas išsaugomi jūsų naršyklės vietinėje saugykloje (localStorage) ir į jokį serverį nesiunčiami.</li>
<li><b>Priegloba.</b> Svetainė talpinama GitHub Pages (GitHub, Inc.). Kaip ir bet kuris žiniatinklio serveris, GitHub dėl techninių ir saugumo priežasčių
gali registruoti kiekvieno lankytojo IP adresą. GitHub dalyvauja ES ir JAV duomenų privatumo sistemoje (EU-US Data Privacy Framework).</li>
<li><b>Apsilankymų skaitiklis.</b> Kiekvienas puslapis padidina anoniminį skaitiklį vienetu: diena, peržiūrėtas puslapis, svetainė, iš kurios atėjote (pvz., google.com),
ką įvedate katalogo paieškoje ir, jei pereinate į parduotuvę, jos pavadinimas. Jokių slapukų, IP adreso ar ko nors, kas jus identifikuotų. Skaitikliai saugomi
Google Cloud Firestore (Google Ireland Ltd.) Europos Sąjungoje esančiame serveryje (Madride).</li>
<li><b>Jokių kitų užklausų trečiosioms šalims.</b> Šriftai, grafikai ir prekių nuotraukos įkeliami iš guitle.com.</li>
<li><b>Perėjus į parduotuvę.</b> Perėję į parduotuvę, paliekate guitle, ir tuomet taikoma tos parduotuvės privatumo politika.</li>
</ul>
<p><b>Jūsų teisės.</b> Savo teises susipažinti su duomenimis, juos ištaisyti, ištrinti, nesutikti su tvarkymu, apriboti jį ir perkelti duomenis galite
įgyvendinti parašę adresu <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Taip pat galite pateikti skundą duomenų apsaugos priežiūros
institucijai, pavyzdžiui, Ispanijos Agencia Española de Protección de Datos arba savo šalies duomenų apsaugos priežiūros institucijai.
Duomenų valdytojas: teisinėje informacijoje nurodytas svetainės valdytojas.</p>

<h2 id="cookies">Slapukai</h2>
<p>guitle nenaudoja slapukų – nei savų, nei trečiųjų šalių, todėl nematote slapukų juostos. Naudojame tik naršyklės vietinę saugyklą,
kad įsimintume jūsų nustatymus. Parduotuvės, į kurias pateikiame nuorodas, savo svetainėse gali naudoti savus slapukus.</p>
""")
