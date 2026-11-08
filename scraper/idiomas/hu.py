# Magyar (hu) · Magyarország · HUF. Tegeződés (mint a legtöbb modern magyar webshop/hangszerbolt).
# Számnév után egyes szám áll: "nouns", "guitars", "storesWord", "many", js "store"/"stores" mind egyes számúak
# ("1 234 gitár", "3 bolt"). A felső szintű "store"/"stores" csak a "desc"-ben szerepel ("{n} {stores}" → "5 boltban").
# Toldalékok: "{price}-tól", "{v}-ig", "{v}-tal" – a forintos ár mindig "Ft"-ra végződik, így "Ft-tól", "Ft-ig", "Ft-tal"
# helyes. Ha az árformátum valaha nem "Ft"-ra végződne, ezeket át kell nézni. A boltnevekhez (pl. Thomann) nem teszünk
# ragot (illeszkedés/névelő miatt), helyette "itt: {s}".

MONEY_NOTE = ("Ezres tagolás (nem törhető) szóközzel, fillér nélkül, a jel az összeg után: '129 900 Ft' "
              "(kód: f\"{round(v):,}\".replace(',', '\\u00a0') + '\\u00a0Ft').")

KINDS_LANG = {"electrica": "elektromos-gitarok", "acustica": "akusztikus-gitarok", "clasica": "klasszikus-gitarok",
              "pack": "gitarszettek", "bajo": "basszusgitarok", "ampli": "erositok", "pedal": "effektpedalok",
              "teclado": "billentyus-hangszerek", "micro": "mikrofonok", "estuche": "tokok-puhatokok", "varios": "kiegeszitok"}

PACK_LANG = ("Gitárszettek", "Szettek", "Keresés a szettek között: modell, márka, erősítővel…", "szett",
             {"Eléctrica": "Elektromos gitár", "Acústica": "Akusztikus gitár"})

T_LANG = {
    "tagline": "gitárok a legjobb áron", "homeLabel": "guitle, főoldal",
    "homeTitle": "guitle · gitár-árösszehasonlító",
    "homeDesc": "A guitle gitárárakat hasonlít össze: elektromos, akusztikus és klasszikus gitárok a Magyarországon értékesítő "
                "boltokban, minden modell ártörténetével.",
    "h1": "A gitárod <span>a legjobb áron</span><small>Gitár-árösszehasonlító</small>",
    "searchPh": "Keresés: strat, les paul, yamaha, ibanez…", "searchBtn": "Keresés", "searchLabel": "Gitár keresése",
    "guitars": "gitár", "storesWord": "bolt", "catalog": "Katalógus",
    "dealsH": "A legnagyobb árkülönbségek a boltok között", "dealsBadge": "−{p}% a legdrágábbhoz képest",
    "catsH": "Böngéssz kategóriák szerint", "soon": "hamarosan", "storesH": "Az összehasonlított boltok",
    "howH": "Hogyan működik?",
    "steps": ["Minden nap ellenőrizzük minden gitár árát, készletét és fotóját a Magyarországon értékesítő boltokban.",
              "Elmentjük az ártörténetet, hogy lásd, tényleg jó-e egy ár, vagy általában alacsonyabb szokott lenni.",
              "Ha szeretnéd, e-mailt küldünk, amikor csökken az ár."],
    "affiliate": "A boltokra mutató linkek egy része partnerlink (affiliate): ha vásárolsz, a guitle jutalékot kaphat – neked ez semmibe sem kerül.",
    "legal": "Impresszum", "privacy": "Adatvédelem", "cookies": "Sütik", "otherCountries": "A guitle más országokban:",
    "updated": "Adatok frissítve: {d}", "home": "Főoldal",
    "kinds": {"electrica": ("Elektromos gitárok", "Elektromos", "Keresés az elektromos gitárok között: modell, márka, szín…"),
              "acustica": ("Akusztikus gitárok", "Akusztikus", "Keresés az akusztikus gitárok között: modell, márka, faanyag…"),
              "clasica": ("Klasszikus gitárok", "Klasszikus", "Keresés a klasszikus gitárok között: modell, márka, flamenco…"),
              "bajo": ("Elektromos és akusztikus basszusgitárok", "Basszusgitárok", "Keresés a basszusgitárok között: modell, márka, 5 húros…"),
              "ampli": ("Gitár- és basszuserősítők", "Erősítők", "Keresés az erősítők között: modell, márka, kombó, fej…"),
              "pedal": ("Effektpedálok", "Effektek", "Keresés az effektek között: modell, márka, effekt típusa…"),
              "teclado": ("Billentyűs hangszerek és digitális zongorák", "Billentyűsök", "Keresés a billentyűsök között: modell, márka…"),
              "micro": ("Mikrofonok", "Mikrofonok", "Keresés a mikrofonok között: modell, márka, típus…"),
              "estuche": ("Tokok és puhatokok", "Tokok", "Keresés a tokok és puhatokok között: modell, márka…"),
              "varios": ("Gitárkiegészítők", "Kiegészítők", "Keresés a kiegészítők között: húrok, pengetők, gitárszíjak, kábelek…")},
    # Mit számolunk az egyes kategóriákban (főoldal és lista) – számnév után egyes szám.
    "nouns": {"bajo": "basszusgitár", "ampli": "erősítő", "pedal": "effekt", "teclado": "billentyűs hangszer", "micro": "mikrofon",
              "estuche": "tok", "varios": "termék"},
    "allWord": "termék",
    "anyPrice": "Bármilyen ár", "upTo": "{v}-ig", "over": "{v} felett", "brandLabel": "Márka", "priceLabel": "Ár",
    "showLabel": "Mutasd", "showAll": "Mind", "showMulti": "Több boltban", "showStock": "Raktáron",
    "showLow": "Legalacsonyabb áron", "showLh": "Csak balkezes", "loading": "Katalógus betöltése…", "sortLabel": "Rendezés",
    "sorts": ["Legtöbb bolt", "Legalacsonyabb ár", "Legmagasabb ár", "Legnagyobb megtakarítás a boltok között", "Név"],
    "moreBtn": "Továbbiak", "sections": "Kategóriák", "searchAria": "Keresés",
    "bestPrice": "legjobb ár", "inStock": "raktáron", "noStock": "nincs raktáron", "goLong": "Tovább a bolthoz", "goShort": "Bolt",
    "store": "boltban", "stores": "boltban", "lh": "balkezes", "storesH3": "Boltok", "historyH3": "Ártörténet",
    "amazon": "", "titleFrom": "{name}: {price}-tól, {where}", "inN": "{n} boltban", "inS": "itt: {s}",
    "whereMany": "itt: {s} · {n} bolt", "whereDiff": ", akár {d} különbség",
    "desc": "{name} már {price}-tól, itt: {s}. Hasonlítsd össze az árát {n} {stores} ({list}), és nézd meg az ártörténetet, "
            "hogy lásd, most érdemes-e megvenni.",
    "alertTitle": "Árfigyelő", "alertWait": "Egy pillanat…", "alertSaving": "Mentjük a válaszodat.",
    "alertGo": "Tovább a guitle-re", "alertBad": ["Érvénytelen link", "Másold ki a teljes linket az e-mailből, és próbáld újra."],
    "alertDone": ["Árfigyelő megerősítve!", "Írunk, amint csökken az ár. Minden e-mailben találsz leiratkozó linket."],
    "alertGone": ["Árfigyelő törölve", "Erről az árfigyelőről nem kapsz több e-mailt. A címedet töröltük a listánkról."],
    "alertMissing": ["Az árfigyelő nem található", "Lehet, hogy már meg volt erősítve vagy törölve lett, vagy több mint 7 nap telt el "
                                                   "megerősítés nélkül. Segítség kell? Írj nekünk: hola@guitle.com."],
    "js": {"loadErr": "Nem sikerült betölteni a katalógust.", "allBrands": "Minden márka", "all": "Mind", "low": "Legalacsonyabb",
           "save": "{v} megtakarítás", "lh": "balkezes", "store": "bolt", "stores": "bolt",
           "empty": "Nincs a szűrőknek megfelelő {many}.", "more": "Továbbiak (még {n})",
           "meta": "{a} / {b} {many} · {m} több boltban is összevethető · frissítve: {d}", "best": "legjobb ár",
           "inStock": "raktáron", "noStock": "nincs raktáron", "goLong": "Tovább a bolthoz", "goShort": "Bolt", "close": "Bezárás",
           "inAt": "itt: {s}", "saveMax": " · akár {v}-tal olcsóbb, mint a legdrágább", "atLow": "A valaha mért legalacsonyabb áron",
           "lowTag": "Legalacsonyabb ár: {v}", "storesH": "Boltok", "evolH": "Az ár alakulása",
           "histErr": "Nem sikerült betölteni az ártörténetet.", "histSoon": "Az ártörténet a következő napokban töltődik fel.",
           "many": "gitár",
           "types": {"ST": "ST típus", "T": "T típus", "Semihueca": "Félakusztikus", "Offset / Retro": "Offset / Retro", "Moderna / Metal": "Modern / Metal",
                     "Otras": "Egyéb", "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12 húros",
                     "Tamaño reducido": "Kisebb méretű", "Clásica": "Klasszikus", "Flamenca": "Flamenco",
                     "Electroclásica": "Elektroklasszikus",
                     "4 cuerdas": "4 húros", "5 cuerdas": "5 húros", "6 cuerdas o más": "6 vagy több húros",
                     "Acústico": "Akusztikus basszusgitárok", "Fretless": "Fretless", "Escala corta": "Rövid menzúra", "Combo": "Kombók",
                     "Cabezal": "Erősítőfejek", "Pantalla": "Hangládák", "Para bajo": "Basszusgitárhoz", "Para acústica": "Akusztikus gitárhoz",
                     "De auriculares y portátil": "Fejhallgató- és mini erősítők", "Para eléctrica": "Elektromos gitárhoz",
                     "Para clásica": "Klasszikus gitárhoz", "Overdrive y distorsión": "Overdrive és torzító",
                     "Modulación": "Moduláció", "Compresor": "Kompresszor", "Wah y volumen": "Wah és volume",
                     "Octavador y pitch": "Oktáver és pitch", "Ecualizador": "Equalizer", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Szintetizátorok", "Afinador": "Hangoló", "Multiefectos": "Multieffektek",
                     "Reverb": "Zengető", "Piano digital": "Digitális zongorák", "Teclado portátil": "Hordozható billentyűsök",
                     "Piano de escenario": "Színpadi zongorák", "Controlador MIDI": "MIDI-vezérlők", "Piano acústico": "Akusztikus zongorák",
                     "Dinámico": "Dinamikus", "Condensador": "Kondenzátor", "Inalámbrico": "Vezeték nélküli",
                     "Para instrumento": "Hangszermikrofonok", "De cinta": "Szalagmikrofonok", "Cuerdas": "Húrok",
                     "Púas": "Pengetők", "Correas": "Gitárszíjak", "Cables": "Kábelek", "Afinadores": "Hangolók",
                     "Cejillas": "Kapodaszterek", "Soportes": "Állványok", "Pastillas": "Hangszedők", "Recambios": "Alkatrészek",
                     "Mantenimiento": "Ápolás"},
           "wait": "{n} {days} követjük ezt a modellt", "day": "napja", "days": "napja",
           "waitSub": "Az értékelés néhány hét ártörténet után lesz megbízhatóbb.",
           "min": "A valaha mért legalacsonyabb ár", "minSub": "Ennél olcsóbban még sosem láttuk.",
           "minBelow": " {p}%-kal a 30 napos átlag alatt.",
           "good": "Jó alkalom: {p}%-kal az átlagár alatt", "goodSub": "Az elmúlt 30 nap átlaga: {avg}.",
           "bad": "Most {p}%-kal drágább a szokásosnál",
           "badSub": "Ha nem sürgős, várj: a 30 napos átlag {avg}, a legalacsonyabb ár {min}.",
           "normal": "Szokásos ár", "normalSub": "Megfelel a 30 napos átlagnak ({avg}). Legalacsonyabb mért ár: {min}.",
           "today": "mai ár", "lowest": "legalacsonyabb ({d})", "highest": "legmagasabb", "avg": "{n} napos átlag",
           "since": "Követés kezdete: {d}", "noHist": "Még nincs ártörténet.", "pvp": "Listaár", "bestLine": "Legjobb ár",
           "alertOpen": "Szólj, ha csökken az ár", "emailPh": "te@pelda.hu", "emailLabel": "E-mail-címed",
           "targetPh": "Max. ár (nem kötelező)", "targetLabel": "Célár forintban", "alertBtn": "Értesíts",
           "alertLegal": "Ingyenes, regisztráció nélkül. Az „Értesíts” gombra kattintva elfogadod az "
                         "<a href=\"/hu/legal.html#adatvedelem\">adatvédelmi tájékoztatót</a>: az e-mail-címedet csak erre az "
                         "árfigyelőre használjuk, és egy kattintással leiratkozhatsz.",
           "alertOk": "<b>Kész!</b> Pár percen belül kapsz egy e-mailt erre a címre: {email}, amellyel megerősítheted az árfigyelőt "
                      "(nézd meg a spam mappát is).",
           "alertErr": "Nem sikerült menteni az árfigyelőt. Ellenőrizd az e-mail-címet, és próbáld újra."},
    "mail": {"tagline": "gitárok a legjobb áron",
             "footer": "A guitle naponta összehasonlítja a hangszerboltok árait. Azért kapod ezt az e-mailt, mert árfigyelőt kértél "
                       "a guitle.com oldalon. Adatkezelő: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Adatvédelem", "confirmSubject": "Erősítsd meg a guitle-árfigyelődet",
             "confirmTitle": "Erősítsd meg az árfigyelőt", "asked": "Azt kérted, hogy szóljunk, ha az ár{target} csökken:",
             "below": " <b>{v}</b> alá", "confirmAsk": "Kérjük, erősítsd meg, hogy erre a címre szeretnéd kapni az értesítést:",
             "confirmBtn": "Árfigyelő megerősítése",
             "notYou": "Ha nem te voltál, ne tegyél semmit: a meg nem erősített árfigyelőket 7 nap után automatikusan töröljük.",
             "dropSubject": "Csökkent az ár: {name} most {price}", "dropTitle": "Csökkent az ár!", "nowAt": "itt: {s} · korábban {v}",
             "seeAll": "Árak megtekintése minden boltban",
             "check": "Az árak naponta változnak: vásárlás előtt ellenőrizd a bolt oldalán. Már nem érdekel?",
             "stop": "Árfigyelő leállítása"},
}

# Felügyeleti hatóság Magyarországon: Nemzeti Adatvédelmi és Információszabadság Hatóság (NAIH), naih.hu.
# Kifejezés esetleges legal_replace-hez: "vagy a Nemzeti Adatvédelmi és Információszabadság Hatóságnál (NAIH)".
LEGAL_LANG = ("Impresszum és adatvédelem", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Impresszum és adatvédelem</h1>
<p class="muted">Hatályos: 2026. október 28. Ez fordítás; kétség esetén a <a href="/legal.html">spanyol változat</a> az irányadó.</p>

<h2 id="aviso">Impresszum</h2>
<p>A weboldal üzemeltetője: <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Spanyolország
(spanyol adóazonosító szám, NIF: 17747339X), kapcsolat:
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, weboldal: guitle.com. Tevékenység: hangszerek árának összehasonlítása és partnerprogramos (affiliate) hirdetés.
Tárhely: GitHub Pages (GitHub, Inc.).</p>

<h2 id="feltetelek">Felhasználási feltételek</h2>
<p>A guitle árösszehasonlító oldal, maga nem értékesít semmit. Megmutatjuk a boltok által a saját weboldalukon közzétett árakat, és
hozzájuk irányítunk, így közvetlenül a boltban vásárolsz. A vásárlásért, a szállításért, a jótállásért és a visszaküldésért az adott bolt felel.</p>
<ul>
<li><b>Az árak tájékoztató jellegűek.</b> Rendszeresen ellenőrizzük az árakat, de ezek bármikor változhatnak. Mindig az az ár érvényes, amelyet a bolt a rendeléskor mutat.</li>
<li><b>A pontosságért nem vállalunk garanciát.</b> Igyekszünk, hogy a termékek, árak és készletadatok pontosak legyenek, de előfordulhat hiba. Ha ilyet találsz, írj nekünk.</li>
<li><b>Védjegyek és képek.</b> A védjegyek, terméknevek és képek a jogosultjaik tulajdonát képezik, és csak a termékek azonosítására szolgálnak.</li>
<li><b>A guitle tartalmai.</b> A guitle dizájnja, logója, szövegei és adatgyűjteményei az üzemeltető tulajdonában vannak. Tömeges másolásuk vagy engedély nélküli kereskedelmi felhasználásuk nem megengedett.</li>
</ul>

<h2 id="affiliate">Partnerlinkek</h2>
<p>A boltokra mutató linkek egy része partnerlink (affiliate): ha a kattintás után vásárolsz, a bolt kis jutalékot fizethet a guitle-nek. Számodra
az ár ugyanaz marad. A jutalékok nem befolyásolják a sorrendet: a boltokat mindig ár szerint rendezzük, a legolcsóbbal kezdve.</p>

<h2 id="adatvedelem">Adatvédelmi tájékoztató</h2>
<p>A guitle használatához nem kérünk személyes adatot: nincs regisztráció, nincs hírlevél, nincsenek követő elemző- vagy hirdetési eszközök.
A látogatásokat csak névtelenül számoljuk, és ha árfigyelőt kérsz, az e-mail-címedet ehhez az árfigyelőhöz tároljuk.</p>
<ul>
<li><b>Árfigyelők.</b> Ha értesítést kérsz arról, hogy egy termék ára csökken, tároljuk az e-mail-címedet, a terméket, annak aznapi árát,
valamint – ha megadod – a célárat. Ezeket kizárólag a megerősítő e-mail és az adott termékre vonatkozó értesítések küldésére használjuk,
soha nem marketingcélra, és senkinek nem adjuk át. Jogalap: a hozzájárulásod (GDPR 6. cikk (1) bekezdés a) pont), amelyet az árfigyelő
kérésével és az e-mail-cím megerősítésével adsz meg. Az adatokat a Google Cloud Firestore-ban tároljuk (Google Ireland Ltd., madridi szerver),
az e-maileket pedig a hola@guitle.com postafiókunkból küldjük (DonDominio, Spanyolország). A meg nem erősített árfigyelőket 7 nap után töröljük;
a megerősítetteket addig őrizzük, amíg le nem iratkozol a minden e-mailben található linkkel (ekkor az árfigyelő azonnal törlődik), vagy amíg
nem kéred a törlését.</li>
<li><b>Beállítások a böngésződben.</b> A szűrőket és a választott nézetet a böngésződ helyi tárhelye (localStorage) őrzi, és semmilyen szerverre nem kerülnek.</li>
<li><b>Tárhely.</b> A weboldalt a GitHub Pages (GitHub, Inc.) szolgáltatja. Mint minden webszerver, a GitHub is naplózhatja a látogatók IP-címét
technikai és biztonsági okokból. A GitHub részt vesz az EU–USA adatvédelmi keretrendszerben (EU-US Data Privacy Framework).</li>
<li><b>Látogatásszámláló.</b> Minden oldal 1-gyel növel egy névtelen számlálót: a nap, a megnézett oldal, a weboldal, ahonnan érkeztél (például google.com),
amit a katalógus keresőjébe beírsz, és ha továbbkattintasz egy boltba, annak neve. Nincs süti, nincs IP-cím, semmi, ami azonosítana. A számlálókat
a Google Cloud Firestore-ban tároljuk (Google Ireland Ltd.), az Európai Unióban található szerveren (Madrid).</li>
<li><b>Nincs más harmadik félhez intézett kérés.</b> A betűtípusokat, a grafikonokat és a termékfotókat a guitle.com szolgálja ki.</li>
<li><b>Átlépés egy boltba.</b> Ha egy boltra kattintasz, elhagyod a guitle-t, és onnantól a bolt adatvédelmi tájékoztatója érvényes.</li>
</ul>
<p><b>A jogaid.</b> A hozzáféréshez, helyesbítéshez, törléshez, tiltakozáshoz, az adatkezelés korlátozásához és az adathordozhatósághoz való jogodat a
<a href="mailto:hola@guitle.com">hola@guitle.com</a> címre írt e-mailben gyakorolhatod. Panaszt tehetsz egy adatvédelmi felügyeleti hatóságnál is,
például a spanyol Agencia Española de Protección de Datosnál vagy a Nemzeti Adatvédelmi és Információszabadság Hatóságnál (NAIH). Adatkezelő: az impresszumban megnevezett üzemeltető.</p>

<h2 id="cookies">Sütik</h2>
<p>A guitle nem használ sütiket (cookie-kat), sem sajátot, sem harmadik félét – ezért nem látsz sütibannert. Csak a böngésző helyi tárhelyét
használjuk a beállításaid megjegyzésére. A belinkelt boltok a saját oldalukon használhatnak saját sütiket.</p>
""")
