"""Sprievodcovia po slovensky (guitle.com/sk/guias/)."""
MORE, FAQ, GUIDES_WORD = "Zobraziť všetko", "Časté otázky", "Sprievodcovia"
INDEX_TITLE = "Sprievodcovia nákupom gitary"
INDEX_DESC = "Sprievodcovia výberom elektrickej, klasickej alebo akustickej gitary, basgitary a komba, so skutočnými modelmi a dnešnými cenami."
COURSE_URL, COURSE_TITLE = "kurz/", "Kurz zadarmo: tvoja prvá gitara"
COURSE_DESC = "Päť lekcií od nuly: držanie, akordy, rytmus, stupnice a dve pesničky, s metronómom."

GUIDES = [
    {"slug": "prva-elektricka-gitara", "title": "Ako vybrať prvú elektrickú gitaru",
     "desc": "Aký tvar, aké snímače a koľko minúť na prvú elektrickú gitaru, s najpredávanejšími modelmi do {p300} a ich dnešnou cenou.",
     "body": """<section class="hub-sec guia">
<h2>Aký tvar</h2>
<ul>
<li><strong>Typ Stratocaster (ST):</strong> najuniverzálnejšia a najpohodlnejšia, na pop, rock, blues aj funk. Ak váhaš, začni tu.</li>
<li><strong>Typ Telecaster (T):</strong> jednoduchšia, s jasným a priamym zvukom, obľúbená v rocku a country.</li>
<li><strong>Single cut (typ Les Paul):</strong> plnší zvuk a dlhší sustain, ideálna na rock a blues. Zvyčajne je ťažšia.</li>
<li><strong>Superstrat:</strong> tenký krk a silné snímače, stavaná na hard rock a metal.</li>
</ul>
<h2>Snímače: single coil, alebo humbucker</h2>
<p><strong>Single coily</strong> znejú jasne a iskrivo; <strong>humbuckery</strong> znejú plnšie a so skreslením menej brumia. Zapojenie <strong>HSS</strong> kombinuje oboje a pre začiatočníkov je najuniverzálnejšie.</p>
<h2>Koľko minúť</h2>
<p>V rozpätí <strong>{p150}–{p300}</strong> nájdeš gitary, ktoré dobre znejú a vydržia roky: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone či Harley Benton, okrem iných. Elektrická gitara potrebuje <strong>kombo</strong> (alebo malý slúchadlový zosilňovač); ak začínaš od nuly, set často vyjde lacnejšie.</p>
<p>Rovnaký model sa môže medzi obchodmi citeľne líšiť v cene. guitle každý deň porovnáva ceny v {shops} obchodoch a ukladá históriu cien.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elektrické gitary do {p300}, ktoré predáva najviac obchodov (dnešné ceny)")],
     "faqs": [("Akú elektrickú gitaru kúpiť ako začiatočník?", "Typ Stratocaster so snímačmi HSS v rozpätí {p150}–{p300}: Yamaha Pacifica, Squier a Ibanez GIO patria medzi najčastejšie volené prvé gitary."),
              ("Potrebujem k elektrickej gitare kombo?", "Áno: bez zosilňovača ju takmer nepočuť. Na začiatok stačí malé cvičné kombo alebo slúchadlový zosilňovač."),
              ("Oplatí sa gitarový set pre začiatočníkov?", "Ak začínaš od nuly, áno: gitara, kombo a príslušenstvo vyjdú v sete lacnejšie ako zvlášť.")]},
    {"slug": "klasicka-alebo-akusticka-gitara", "title": "Klasická, alebo akustická gitara: ktorú vybrať",
     "desc": "Rozdiel medzi klasickou a akustickou gitarou, ktorú zvoliť ako začiatočník, veľkosti pre deti a modely s dnešnou cenou.",
     "body": """<section class="hub-sec guia">
<h2>Ide najmä o struny</h2>
<p><strong>Klasická</strong> gitara má <strong>nylonové</strong> struny: sú mäkké na prsty, znejú teplo a krk je širší. <strong>Akustická</strong> (westernová) gitara má <strong>oceľové</strong> struny: znie jasnejšie a hlasnejšie, ale na začiatku viac bolia prsty.</p>
<ul>
<li><strong>Klasická:</strong> klasická hudba, flamenco, bossa nova, a tiež pre deti alebo výučbu s učiteľom.</li>
<li><strong>Akustická:</strong> pop, rock, folk a sprievod k spevu.</li>
</ul>
<h2>Veľkosti</h2>
<p>Klasické gitary sa vyrábajú vo veľkosti <strong>4/4</strong> pre dospelých, <strong>3/4</strong> pre deti približne od 8 do 11 rokov a <strong>1/2</strong> pre mladšie deti. <strong>Elektroakustická</strong> gitara má predzosilňovač, takže ju zapojíš do zosilňovača.</p>
<h2>Koľko minúť</h2>
<p>Dobré klasické gitary zoženieš zhruba od <strong>{p100}–{p200}</strong>, akustické od <strong>{p150}–{p300}</strong>. S masívnou doskou znejú lepšie a časom sa ešte rozohrajú. guitle každý deň porovnáva ceny v {shops} obchodoch.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klasické gitary do {p200}, ktoré predáva najviac obchodov (dnešné ceny)"),
               ("acustica", 300, 8, 3, True, "Akustické gitary do {p300}, ktoré predáva najviac obchodov (dnešné ceny)")],
     "faqs": [("Klasická, alebo akustická gitara pre začiatočníkov?", "Klasická je vďaka nylonovým strunám pohodlnejšia; akustická je lepšia, ak chceš hrať pop, rock alebo folk."),
              ("Akú veľkosť gitary potrebuje dieťa?", "Zhruba 1/2 do 7–8 rokov, 3/4 od 8 do 11 rokov a 4/4 od 12 rokov."),
              ("Môžem dať na klasickú gitaru oceľové struny?", "Nie: klasická gitara nie je stavaná na taký ťah; môže sa poškodiť krk alebo kobylka.")]},
    {"slug": "prva-basgitara", "title": "Ako vybrať prvú basgitaru",
     "desc": "4, alebo 5 strún, Precision, alebo Jazz Bass a koľko minúť na prvú basgitaru, s najpredávanejšími modelmi do {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4, alebo 5 strún</h2>
<p>Začni so <strong>štvorstrunovou</strong> basgitarou: je to štandard takmer v každom žánri. <strong>Päťstrunová</strong> má navyše hlbokú strunu, obľúbenú v metale a modernom funku, ale aj širší krk.</p>
<ul>
<li><strong>Typ Precision (P):</strong> okrúhly, pevný zvuk, jednoduchá a účinná.</li>
<li><strong>Typ Jazz Bass (J):</strong> dva snímače a štíhlejší krk, so zovretejším zvukom.</li>
<li><strong>Short scale:</strong> kratšia menzúra, pohodlnejšia pre menšie ruky.</li>
</ul>
<p>V rozpätí <strong>{p200}–{p400}</strong> sú veľmi dobré basgitary na začiatok. Basgitara potrebuje basové kombo: hlboké tóny môžu gitarové kombo poškodiť.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Basgitary do {p400}, ktoré predáva najviac obchodov (dnešné ceny)")],
     "faqs": [("Akú basgitaru kúpiť ako začiatočník?", "Štvorstrunovú basgitaru typu Precision, Jazz Bass alebo PJ v rozpätí {p200}–{p400}."),
              ("Môžem zapojiť basgitaru do gitarového komba?", "Radšej nie: hlboké tóny môžu poškodiť reproduktor. Potrebuješ basové kombo.")]},
    {"slug": "prvy-gitarovy-zosilnovac", "title": "Aký gitarový zosilňovač kúpiť ako začiatočník",
     "desc": "Koľko wattov, modeling, alebo elektrónky a koľko minúť na prvé kombo, s najpredávanejšími modelmi do {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Doma ti stačí málo</h2>
<p>Na cvičenie doma bohato stačí kombo s výkonom <strong>10 až 30 wattov</strong>; dôležité je, aby dobre znelo potichu a malo <strong>výstup na slúchadlá</strong>.</p>
<ul>
<li><strong>Modeling (digitálne):</strong> napodobňuje množstvo zosilňovačov a má zabudované efekty: na začiatok najpraktickejšie (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Elektrónkové:</strong> klasický rockový a bluesový zvuk, drahšie a stavané na hlasné hranie.</li>
</ul>
<p>V rozpätí <strong>{p100}–{p300}</strong> nájdeš veľmi dobre vybavené cvičné kombá.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Kombá do {p300}, ktoré predáva najviac obchodov (dnešné ceny)")],
     "faqs": [("Aké gitarové kombo na doma?", "S výkonom 10 až 30 wattov a výstupom na slúchadlá; digitálne modelingové kombo je na začiatok najpraktickejšie.")]},
    {"slug": "gitarove-sety", "title": "Gitarové sety: kedy sa oplatia",
     "desc": "Čo obsahuje gitarový set, kedy vyjde lacnejšie ako nákup zvlášť a najpredávanejšie sety s dnešnou cenou.",
     "body": """<section class="hub-sec guia">
<h2>Čo je v sete</h2>
<p>Set s elektrickou gitarou zvyčajne obsahuje <strong>gitaru, malé kombo, obal, kábel, popruh, trsátka a ladičku</strong>. <strong>Oplatí sa</strong>, ak začínaš od nuly; <strong>menej</strong>, ak už zosilňovač máš alebo chceš konkrétnu gitaru. Pozeraj hlavne na gitaru: tá ti zostane.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Sety do {p400}, ktoré predáva najviac obchodov (dnešné ceny)")],
     "faqs": [("Oplatí sa gitarový set pre začiatočníkov?", "Áno, ak začínaš od nuly: vyjde lacnejšie ako kupovať všetko zvlášť.")]},
]
