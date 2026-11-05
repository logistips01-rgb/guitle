# Română (ro) · România · RON. Ne adresăm cititorului cu „tu” (ca majoritatea magazinelor muzicale online).
# Numerale: în română, de la 20 în sus se intercalează „de” („1.234 de chitare”). Pe pagina principală numărul și
# cuvântul sunt afișate separat (statistică), deci forma simplă e acceptabilă; în js "meta" am pus {many} la început
# ca să evităm „{b} chitare” cu b ≥ 20.
# Ancora secțiunii de confidențialitate: "confidentialitate".

MONEY_NOTE = ("Romanian lei after the amount, dot as thousands separator, comma for decimals, non-breaking space before "
              "'lei': '1.299 lei', '1.299,50 lei'. intl.CUR_AFTER['RON'] = ('.', 'lei') already gives this.")

KINDS_LANG = {"electrica": "chitare-electrice", "acustica": "chitare-acustice", "clasica": "chitare-clasice",
              "pack": "pachete-chitara", "bajo": "chitare-bas", "ampli": "amplificatoare", "pedal": "pedale-efecte",
              "teclado": "claviaturi", "micro": "microfoane", "estuche": "huse-cutii", "varios": "accesorii"}

PACK_LANG = ("Pachete de chitară", "Pachete", "Caută în pachete: model, marcă, cu amplificator…", "pachete",
             {"Eléctrica": "Chitară electrică", "Acústica": "Chitară acustică"})

T_LANG = {
    "tagline": "chitare la cel mai bun preț", "homeLabel": "guitle, pagina principală",
    "homeTitle": "guitle · comparator de prețuri pentru chitare",
    "homeDesc": "guitle compară prețurile chitarelor: electrice, acustice și clasice, în magazinele care livrează în "
                "România, cu istoricul de preț al fiecărui model.",
    "h1": "Chitara ta, <span>la cel mai bun preț</span><small>Comparator de prețuri pentru chitare</small>",
    "searchPh": "Caută: strat, les paul, yamaha, ibanez…", "searchBtn": "Caută", "searchLabel": "Caută o chitară",
    "guitars": "chitare", "storesWord": "magazine", "catalog": "Catalog",
    "dealsH": "Cele mai mari diferențe de preț între magazine", "dealsBadge": "−{p}% față de cel mai scump",
    "catsH": "Caută pe categorii", "soon": "în curând", "storesH": "Magazine comparate",
    "howH": "Cum funcționează",
    "steps": ["Zilnic verificăm prețul, stocul și fotografia fiecărei chitare din magazinele care livrează în România.",
              "Păstrăm istoricul prețurilor, ca să vezi dacă un preț e cu adevărat bun sau de obicei e mai mic.",
              "Dacă vrei, îți trimitem un e-mail când scade prețul."],
    "affiliate": "Unele linkuri către magazine sunt linkuri de afiliere: dacă cumperi, guitle poate primi un comision, fără niciun cost suplimentar pentru tine.",
    "legal": "Informații legale", "privacy": "Confidențialitate", "cookies": "Cookie-uri", "otherCountries": "guitle în alte țări:",
    "updated": "Date actualizate la {d}", "home": "Pagina principală",
    "kinds": {"electrica": ("Chitare electrice", "Electrice", "Caută în chitarele electrice: model, marcă, culoare…"),
              "acustica": ("Chitare acustice", "Acustice", "Caută în chitarele acustice: model, marcă, lemn…"),
              "clasica": ("Chitare clasice", "Clasice", "Caută în chitarele clasice: model, marcă, flamenco…"),
              "bajo": ("Chitare bas electrice și acustice", "Bas", "Caută în chitarele bas: model, marcă, 5 corzi…"),
              "ampli": ("Amplificatoare de chitară și bas", "Amplificatoare", "Caută în amplificatoare: model, marcă, combo, head…"),
              "pedal": ("Pedale de efecte", "Efecte", "Caută în pedalele de efecte: model, marcă, efect…"),
              "teclado": ("Claviaturi și piane digitale", "Claviaturi", "Caută în claviaturi: model, marcă…"),
              "micro": ("Microfoane", "Microfoane", "Caută în microfoane: model, marcă, tip…"),
              "estuche": ("Huse și cutii", "Huse", "Caută în huse și cutii: model, marcă…"),
              "varios": ("Accesorii pentru chitară", "Accesorii", "Caută în accesorii: corzi, pene, curele, cabluri…")},
    # Ce se numără în fiecare categorie (pagina principală și listă) și, dacă nu sunt doar chitare, totalul.
    "nouns": {"bajo": "chitare bas", "ampli": "amplificatoare", "pedal": "pedale", "teclado": "claviaturi", "micro": "microfoane",
              "estuche": "huse", "varios": "articole"},
    "allWord": "produse",
    "anyPrice": "Orice preț", "upTo": "Până la {v}", "over": "Peste {v}", "brandLabel": "Marcă", "priceLabel": "Preț",
    "showLabel": "Afișează", "showAll": "Toate", "showMulti": "În mai multe magazine", "showStock": "În stoc",
    "showLow": "La prețul minim", "showLh": "Doar pentru stângaci", "loading": "Se încarcă catalogul…", "sortLabel": "Sortează",
    "sorts": ["Cele mai multe magazine", "Preț crescător", "Preț descrescător", "Cea mai mare economie între magazine", "Nume"],
    "moreBtn": "Vezi mai multe", "sections": "Secțiuni", "searchAria": "Caută",
    "bestPrice": "cel mai bun preț", "inStock": "în stoc", "noStock": "stoc epuizat", "goLong": "Mergi la magazin", "goShort": "Vezi",
    "store": "magazin", "stores": "magazine", "lh": "pentru stângaci", "storesH3": "Magazine", "historyH3": "Istoric preț",
    "amazon": "", "titleFrom": "{name}: preț de la {price} {where}", "inN": "în {n} magazine", "inS": "la {s}",
    "whereMany": "la {s} · {n} magazine", "whereDiff": ", până la {d} diferență",
    "desc": "{name} de la {price} la {s}. Compară prețul în {n} {stores} ({list}) și vezi istoricul de preț ca să știi dacă "
            "e un moment bun să cumperi.",
    "alertTitle": "Alertă de preț", "alertWait": "Un moment…", "alertSaving": "Îți salvăm răspunsul.",
    "alertGo": "Mergi la guitle", "alertBad": ["Link invalid", "Copiază linkul complet din e-mail și încearcă din nou."],
    "alertDone": ["Alertă confirmată!", "Îți scriem imediat ce scade prețul. Fiecare e-mail conține un link de dezabonare."],
    "alertGone": ["Alertă ștearsă", "Nu vei mai primi e-mailuri pentru această alertă. Ți-am șters adresa din lista noastră."],
    "alertMissing": ["Alerta nu a fost găsită", "Poate a fost deja confirmată sau ștearsă ori au trecut mai mult de 7 zile fără "
                                                "confirmare. Ai nevoie de ajutor? Scrie-ne la hola@guitle.com."],
    "js": {"loadErr": "Catalogul nu a putut fi încărcat.", "allBrands": "Toate mărcile", "all": "Toate", "low": "Preț minim",
           "save": "Economisești {v}", "lh": "pentru stângaci", "store": "magazin", "stores": "magazine",
           "empty": "Nu există {many} cu aceste filtre.", "more": "Vezi mai multe (încă {n})",
           "meta": "{many}: {a} din {b} · {m} comparabile în mai multe magazine · actualizat la {d}", "best": "cel mai bun preț",
           "inStock": "în stoc", "noStock": "stoc epuizat", "goLong": "Mergi la magazin", "goShort": "Vezi", "close": "Închide",
           "inAt": "la {s}", "saveMax": " · cu până la {v} mai ieftin decât cel mai scump", "atLow": "La cel mai mic preț înregistrat",
           "lowTag": "Preț minim: {v}", "storesH": "Magazine", "evolH": "Evoluția prețului",
           "histErr": "Istoricul prețurilor nu a putut fi încărcat.", "histSoon": "Istoricul prețurilor se completează în zilele următoare.",
           "many": "chitare",
           "types": {"ST": "Tip ST", "T": "Tip T", "Semihueca": "Semi-hollow", "Offset / Retro": "Offset / Retro",
                     "Moderna / Metal": "Modernă / Metal", "Otras": "Altele", "Auditorio / Concierto": "Auditorium / Concert",
                     "12 cuerdas": "12 corzi", "Tamaño reducido": "Dimensiuni reduse", "Clásica": "Clasică",
                     "Flamenca": "Flamenco", "Electroclásica": "Electro-clasică",
                     "4 cuerdas": "4 corzi", "5 cuerdas": "5 corzi", "6 cuerdas o más": "6 corzi sau mai multe",
                     "Acústico": "Bas acustic", "Fretless": "Fretless", "Escala corta": "Scală scurtă", "Combo": "Combo-uri",
                     "Cabezal": "Head-uri", "Pantalla": "Cabinete", "Para bajo": "Pentru bas", "Para acústica": "Pentru chitară acustică",
                     "De auriculares y portátil": "Mini și pentru căști", "Para eléctrica": "Pentru chitară electrică",
                     "Para clásica": "Pentru chitară clasică", "Overdrive y distorsión": "Overdrive și distorsiune",
                     "Modulación": "Modulație", "Compresor": "Compresor", "Wah y volumen": "Wah și volum",
                     "Octavador y pitch": "Octaver și pitch", "Ecualizador": "Egalizator", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Sintetizatoare", "Afinador": "Acordor", "Multiefectos": "Multiefecte",
                     "Reverb": "Reverb", "Piano digital": "Piane digitale", "Teclado portátil": "Orgi portabile",
                     "Piano de escenario": "Stage piane", "Controlador MIDI": "Controlere MIDI", "Piano acústico": "Piane acustice",
                     "Dinámico": "Dinamice", "Condensador": "Cu condensator", "Inalámbrico": "Wireless",
                     "Para instrumento": "Pentru instrumente", "De cinta": "Cu panglică", "Cuerdas": "Corzi",
                     "Púas": "Pene", "Correas": "Curele", "Cables": "Cabluri", "Afinadores": "Acordoare",
                     "Cejillas": "Capodastre", "Soportes": "Stative", "Pastillas": "Doze", "Recambios": "Piese de schimb",
                     "Mantenimiento": "Întreținere"},
           "wait": "Urmărim acest model de {n} {days}", "day": "zi", "days": "zile",
           "waitSub": "Verdictul devine mai sigur după câteva săptămâni de istoric.",
           "min": "Cel mai mic preț înregistrat", "minSub": "Nu l-am văzut niciodată mai ieftin.",
           "minBelow": " Cu {p}% sub media pe 30 de zile.",
           "good": "Moment bun: cu {p}% sub prețul mediu", "goodSub": "Media ultimelor 30 de zile: {avg}.",
           "bad": "Acum e cu {p}% mai scump decât de obicei",
           "badSub": "Dacă nu te grăbești, așteaptă: media pe 30 de zile este {avg}, iar minimul, {min}.",
           "normal": "Preț normal", "normalSub": "În linie cu media pe 30 de zile ({avg}). Minim înregistrat: {min}.",
           "today": "prețul de azi", "lowest": "minim ({d})", "highest": "maxim", "avg": "media pe {n} zile",
           "since": "Urmărit din {d}", "noHist": "Încă nu există istoric de preț.", "pvp": "Preț recomandat", "bestLine": "Cel mai bun preț",
           "alertOpen": "Anunță-mă dacă scade prețul", "emailPh": "tu@exemplu.ro", "emailLabel": "E-mailul tău",
           "targetPh": "Preț max. (opțional)", "targetLabel": "Prețul dorit în lei", "alertBtn": "Anunță-mă",
           "alertLegal": "Gratuit, fără cont. Apăsând „Anunță-mă” accepți "
                         "<a href=\"/ro/legal.html#confidentialitate\">politica de confidențialitate</a>: folosim e-mailul tău doar "
                         "pentru această alertă și te poți dezabona cu un clic.",
           "alertOk": "<b>Gata!</b> În câteva minute vei primi un e-mail la {email} ca să confirmi alerta (verifică și folderul Spam).",
           "alertErr": "Nu am putut salva alerta. Verifică adresa de e-mail și încearcă din nou."},
    "mail": {"tagline": "chitare la cel mai bun preț",
             "footer": "guitle compară zilnic prețurile magazinelor de instrumente muzicale. Primești acest e-mail pentru că ai cerut "
                       "o alertă pe guitle.com. Operator de date: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Confidențialitate", "confirmSubject": "Confirmă alerta de preț guitle",
             "confirmTitle": "Confirmă alerta de preț", "asked": "Ai cerut să fii anunțat când scade prețul{target}:",
             "below": " sub <b>{v}</b>", "confirmAsk": "Confirmă că vrei să primești alerta la această adresă:",
             "confirmBtn": "Confirmă alerta",
             "notYou": "Dacă nu ai fost tu, nu face nimic: alertele neconfirmate se șterg automat după 7 zile.",
             "dropSubject": "Preț redus: {name} acum {price}", "dropTitle": "Prețul a scăzut!", "nowAt": "la {s} · înainte {v}",
             "seeAll": "Vezi prețurile din toate magazinele",
             "check": "Prețurile se schimbă zilnic: verifică-le pe site-ul magazinului înainte de a cumpăra. Nu te mai interesează?",
             "stop": "Oprește această alertă"},
}

# Autoritatea de supraveghere din România: Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter
# Personal (ANSPDCP), dataprotection.ro.
# Frază pentru un eventual legal_replace: "sau la Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter Personal (ANSPDCP)".
LEGAL_LANG = ("Informații legale și confidențialitate", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Informații legale și confidențialitate</h1>
<p class="muted">Ultima actualizare: 28 octombrie 2026. Aceasta este o traducere; în caz de îndoială, prevalează <a href="/legal.html">versiunea în spaniolă</a>.</p>

<h2 id="aviso">Informații legale</h2>
<p>Acest site este administrat de <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Spania
(cod fiscal spaniol NIF 17747339X), contact <a href="mailto:hola@guitle.com">hola@guitle.com</a>, site guitle.com.
Activitate: comparare de prețuri pentru instrumente muzicale și publicitate prin afiliere. Găzduire: GitHub Pages (GitHub, Inc.).</p>

<h2 id="termeni">Condiții de utilizare</h2>
<p>guitle este un comparator de prețuri și nu vinde nimic. Afișăm prețurile pe care magazinele le publică pe site-urile lor și te trimitem
acolo, ca să cumperi direct de la ele. Achiziția, livrarea, garanția și returul sunt responsabilitatea fiecărui magazin.</p>
<ul>
<li><b>Prețurile sunt orientative.</b> Verificăm prețurile periodic, dar se pot schimba oricând. Prețul valabil este întotdeauna cel afișat de magazin la plasarea comenzii.</li>
<li><b>Fără garanția exactității.</b> Avem grijă ca produsele, prețurile și stocurile să fie corecte, dar pot apărea erori. Dacă găsești una, scrie-ne.</li>
<li><b>Mărci și imagini.</b> Mărcile, denumirile produselor și imaginile aparțin proprietarilor lor și sunt folosite doar pentru identificarea produselor.</li>
<li><b>Conținutul guitle.</b> Designul, logo-ul, textele și colecțiile de date guitle aparțin proprietarului său. Copierea în masă sau utilizarea comercială fără permisiune nu sunt permise.</li>
</ul>

<h2 id="affiliate">Linkuri de afiliere</h2>
<p>Unele linkuri către magazine sunt linkuri de afiliere: dacă cumperi după un clic, magazinul poate plăti guitle un mic comision. Pentru tine prețul
rămâne același. Comisioanele nu influențează ordinea rezultatelor: magazinele sunt sortate întotdeauna după preț, de la cel mai mic.</p>

<h2 id="confidentialitate">Politica de confidențialitate</h2>
<p>guitle nu îți cere date personale pentru a folosi site-ul: fără cont, fără newslettere, fără instrumente de analiză sau publicitate
care să te urmărească. Numărăm vizitele doar anonim și, dacă ceri o alertă de preț, păstrăm adresa ta de e-mail pentru acea alertă.</p>
<ul>
<li><b>Alerte de preț.</b> Dacă ne ceri să te anunțăm când scade prețul unui produs, stocăm adresa ta de e-mail, produsul, prețul lui din ziua respectivă
și, dacă îl indici, prețul dorit. Le folosim doar pentru e-mailul de confirmare și pentru alertele legate de acel produs, niciodată pentru marketing,
și nu le transmitem nimănui. Temei juridic: consimțământul tău (art. 6 alin. (1) lit. (a) din GDPR), pe care îl dai când ceri alerta și îți confirmi
e-mailul. Sunt stocate în Google Cloud Firestore (Google Ireland Ltd., server în Madrid), iar e-mailurile sunt trimise din căsuța noastră
hola@guitle.com (DonDominio, Spania). Alertele neconfirmate se șterg după 7 zile; cele confirmate se păstrează până te dezabonezi prin linkul din
fiecare e-mail (alerta se șterge imediat) sau până ne ceri să o ștergem.</li>
<li><b>Preferințe în browserul tău.</b> Filtrele sau modul de afișare ales se salvează în spațiul de stocare local al browserului tău (localStorage) și nu sunt trimise niciodată către vreun server.</li>
<li><b>Găzduire.</b> Site-ul este găzduit pe GitHub Pages (GitHub, Inc.). Ca orice server web, GitHub poate înregistra adresa IP a fiecărei vizite din
motive tehnice și de securitate. GitHub este certificat în cadrul EU-US Data Privacy Framework.</li>
<li><b>Contor de vizite.</b> Fiecare pagină adaugă 1 la un contor anonim: ziua, pagina vizitată, site-ul de pe care vii (de exemplu google.com), ce scrii
în căutarea din catalog și, dacă dai clic spre un magazin, numele acestuia. Fără cookie-uri, fără adresă IP, nimic care să te identifice. Contoarele sunt
stocate în Google Cloud Firestore (Google Ireland Ltd.), pe un server din Uniunea Europeană (Madrid).</li>
<li><b>Nicio altă solicitare către terți.</b> Fonturile, graficele și fotografiile produselor sunt servite de pe guitle.com.</li>
<li><b>Când mergi la un magazin.</b> Când dai clic spre un magazin, părăsești guitle și se aplică politica de confidențialitate a acelui magazin.</li>
</ul>
<p><b>Drepturile tale.</b> Îți poți exercita drepturile de acces, rectificare, ștergere, opoziție, restricționare și portabilitate scriindu-ne la
<a href="mailto:hola@guitle.com">hola@guitle.com</a>. Poți depune și o plângere la o autoritate de supraveghere a protecției datelor, de exemplu la
Agencia Española de Protección de Datos sau la autoritatea națională de supraveghere a protecției datelor. Operator de date: proprietarul menționat în informațiile legale.</p>

<h2 id="cookies">Cookie-uri</h2>
<p>guitle nu folosește cookie-uri, nici proprii, nici ale terților, de aceea nu vezi niciun banner de cookie-uri. Folosim doar spațiul de stocare local
al browserului pentru a-ți reține preferințele. Magazinele către care trimitem pot folosi propriile cookie-uri pe site-urile lor.</p>
""")
