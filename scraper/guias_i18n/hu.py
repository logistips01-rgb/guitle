"""Útmutatók magyarul (guitle.com/hu/guias/)."""
MORE, FAQ, GUIDES_WORD = "Összes megtekintése", "Gyakori kérdések", "Útmutatók"
INDEX_TITLE = "Útmutatók gitárvásárláshoz"
INDEX_DESC = "Útmutatók elektromos, klasszikus vagy akusztikus gitár, basszusgitár és erősítő választásához, valódi modellekkel és mai árakkal."
COURSE_URL, COURSE_TITLE = "tanfolyam/", "Ingyenes tanfolyam: az első gitárod"
COURSE_DESC = "Öt lecke a nulláról: tartás, akkordok, ritmus, skálák és két dal, metronómmal."

GUIDES = [
    {"slug": "elso-elektromos-gitar", "title": "Hogyan válaszd ki az első elektromos gitárodat",
     "desc": "Milyen forma, milyen hangszedők és mennyit költs az első elektromos gitárodra, a legkeresettebb {p300} alatti modellekkel és mai áraikkal.",
     "body": """<section class="hub-sec guia">
<h2>Milyen forma</h2>
<ul>
<li><strong>Stratocaster típus (ST):</strong> a legsokoldalúbb és legkényelmesebb, pophoz, rockhoz, blueshoz és funkhoz. Ha bizonytalan vagy, ezzel kezdj.</li>
<li><strong>Telecaster típus (T):</strong> egyszerűbb, tiszta, közvetlen hanggal, a rock és a country kedvence.</li>
<li><strong>Single cut (Les Paul típus):</strong> teltebb hang és hosszabb kitartás, ideális rockhoz és blueshoz. Általában nehezebb.</li>
<li><strong>Superstrat:</strong> vékony nyak és erős hangszedők, hard rockhoz és metalhoz készült.</li>
</ul>
<h2>Hangszedők: single coil vagy humbucker</h2>
<p>A <strong>single coil</strong> hangszedők fényesen, csillogóan szólnak; a <strong>humbuckerek</strong> teltebben, és torzítással kevésbé zúgnak. A <strong>HSS</strong> kiosztás mindkettőt ötvözi, és kezdőknek ez a legsokoldalúbb.</p>
<h2>Mennyit költs</h2>
<p><strong>{p150} és {p300}</strong> között olyan gitárokat találsz, amelyek jól szólnak és évekig kitartanak: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone vagy Harley Benton, többek között. Az elektromos gitárhoz <strong>erősítő</strong> kell (vagy egy kis fejhallgató-erősítő); ha a nulláról indulsz, egy szett gyakran olcsóbb.</p>
<p>Ugyanannak a modellnek az ára boltonként érezhetően eltérhet. A guitle minden nap összehasonlítja az árakat {shops} boltban, és elmenti az ártörténetet.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "{p300} alatti elektromos gitárok, amelyeket a legtöbb bolt árul (mai árak)")],
     "faqs": [("Milyen elektromos gitárt vegyen egy kezdő?", "Egy HSS hangszedős Stratocaster típusút {p150} és {p300} között: a Yamaha Pacifica, a Squier és az Ibanez GIO gyakori első gitárok."),
              ("Kell erősítő az elektromos gitárhoz?", "Igen: erősítő nélkül alig hallani. Kezdésnek elég egy kis gyakorlóerősítő vagy fejhallgató-erősítő."),
              ("Megéri kezdőként gitárszettet venni?", "Ha a nulláról kezded, igen: a gitár, az erősítő és a kiegészítők szettben olcsóbbak, mint külön.")]},
    {"slug": "klasszikus-vagy-akusztikus-gitar", "title": "Klasszikus vagy akusztikus gitár: melyiket válaszd",
     "desc": "A klasszikus és az akusztikus gitár közti különbség, melyiket válaszd kezdőként, gyerekméretek és modellek mai áron.",
     "body": """<section class="hub-sec guia">
<h2>A húrokon múlik</h2>
<p>A <strong>klasszikus</strong> gitáron <strong>nejlon</strong> húrok vannak: kíméletesek az ujjakhoz, meleg a hangjuk, és szélesebb a nyak. Az <strong>akusztikus</strong> (western) gitáron <strong>acél</strong> húrok vannak: fényesebben és hangosabban szól, de eleinte jobban megviseli az ujjakat.</p>
<ul>
<li><strong>Klasszikus:</strong> klasszikus zene, flamenco, bossa nova, valamint gyerekeknek és tanári órákhoz.</li>
<li><strong>Akusztikus:</strong> pop, rock, folk és énekkíséret.</li>
</ul>
<h2>Méretek</h2>
<p>A klasszikus gitárok <strong>4/4</strong>-es méretben készülnek felnőtteknek, <strong>3/4</strong>-esben nagyjából 8–11 éves gyerekeknek és <strong>1/2</strong>-esben a kisebbeknek. Az <strong>elektroakusztikus</strong> gitárban előerősítő van, így erősítőre köthető.</p>
<h2>Mennyit költs</h2>
<p>Jó klasszikus gitárok nagyjából <strong>{p100}–{p200}</strong> körül kezdődnek, akusztikusak <strong>{p150}–{p300}</strong> körül. Tömör fedlappal jobban szólnak, és az évek során még szebb lesz a hangjuk. A guitle minden nap összehasonlítja az árakat {shops} boltban.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "{p200} alatti klasszikus gitárok, amelyeket a legtöbb bolt árul (mai árak)"),
               ("acustica", 300, 8, 3, True, "{p300} alatti akusztikus gitárok, amelyeket a legtöbb bolt árul (mai árak)")],
     "faqs": [("Klasszikus vagy akusztikus gitár kezdőknek?", "A klasszikus a nejlonhúrok miatt kényelmesebb; az akusztikus jobb, ha popot, rockot vagy folkot szeretnél játszani."),
              ("Mekkora gitár kell egy gyereknek?", "Nagyjából 1/2-es 7–8 éves korig, 3/4-es 8 és 11 év között, 4/4-es 12 éves kortól."),
              ("Tehetek acélhúrt klasszikus gitárra?", "Nem: a klasszikus gitár nem erre a húrfeszességre készült; a nyak vagy a húrláb megsérülhet.")]},
    {"slug": "elso-basszusgitar", "title": "Hogyan válaszd ki az első basszusgitárodat",
     "desc": "4 vagy 5 húr, Precision vagy Jazz Bass, és mennyit költs az első basszusgitárodra, a legkeresettebb {p400} alatti modellekkel.",
     "body": """<section class="hub-sec guia">
<h2>4 vagy 5 húr</h2>
<p>Kezdj <strong>négyhúros</strong> basszusgitárral: szinte minden stílusban ez az alap. Az <strong>öthúros</strong> egy plusz mély húrt kap, ami a metalban és a modern funkban népszerű, de szélesebb a nyaka.</p>
<ul>
<li><strong>Precision típus (P):</strong> kerek, testes hang, egyszerű és hatékony.</li>
<li><strong>Jazz Bass típus (J):</strong> két hangszedő és karcsúbb nyak, feszesebb hanggal.</li>
<li><strong>Short scale:</strong> rövidebb menzúra, kényelmesebb kisebb kézhez.</li>
</ul>
<p><strong>{p200} és {p400}</strong> között nagyon jó kezdő basszusgitárokat találsz. A basszusgitárhoz basszuserősítő kell: a mély hangok tönkretehetik a gitárerősítőt.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "{p400} alatti basszusgitárok, amelyeket a legtöbb bolt árul (mai árak)")],
     "faqs": [("Milyen basszusgitárt vegyen egy kezdő?", "Négyhúros Precision, Jazz Bass vagy PJ típusút {p200} és {p400} között."),
              ("Bedughatom a basszusgitárt gitárerősítőbe?", "Inkább ne: a mély hangok tönkretehetik a hangszórót. Basszuserősítő kell hozzá.")]},
    {"slug": "elso-gitarerosito", "title": "Milyen gitárerősítőt vegyen egy kezdő",
     "desc": "Hány watt, modellező vagy csöves, és mennyit költs az első erősítődre, a legkeresettebb {p300} alatti modellekkel.",
     "body": """<section class="hub-sec guia">
<h2>Otthonra kevés is elég</h2>
<p>Otthoni gyakorláshoz bőven elég egy <strong>10–30 wattos</strong> erősítő; az a fontos, hogy halkan is jól szóljon, és legyen <strong>fejhallgató-kimenete</strong>.</p>
<ul>
<li><strong>Modellező (digitális):</strong> sokféle erősítőt utánoz, és beépített effektjei vannak: kezdéshez ez a legpraktikusabb (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Csöves:</strong> a klasszikus rock- és blueshangzás, drágább, és hangos játékra készült.</li>
</ul>
<p><strong>{p100} és {p300}</strong> között nagyon jól felszerelt gyakorlóerősítőket találsz.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "{p300} alatti erősítők, amelyeket a legtöbb bolt árul (mai árak)")],
     "faqs": [("Milyen gitárerősítő kell otthonra?", "Egy 10–30 wattos, fejhallgató-kimenettel; kezdéshez a digitális modellező erősítő a legpraktikusabb.")]},
    {"slug": "gitarszettek", "title": "Gitárszettek: mikor érik meg",
     "desc": "Mi van egy gitárszettben, mikor olcsóbb, mint külön megvenni mindent, és a legkeresettebb szettek mai áron.",
     "body": """<section class="hub-sec guia">
<h2>Mi van egy szettben</h2>
<p>Egy elektromosgitár-szettben általában van <strong>gitár, kis erősítő, puhatok, kábel, heveder, pengetők és hangoló</strong>. <strong>Megéri</strong>, ha a nulláról indulsz; <strong>kevésbé</strong>, ha már van erősítőd, vagy egy konkrét gitárt szeretnél. Leginkább a gitárt nézd meg: az marad veled.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "{p400} alatti szettek, amelyeket a legtöbb bolt árul (mai árak)")],
     "faqs": [("Megéri kezdőként gitárszettet venni?", "Igen, ha a nulláról kezded: olcsóbb, mint mindent külön megvenni.")]},
]
