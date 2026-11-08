"""Průvodce v češtině (guitle.com/cz/guias/)."""
MORE, FAQ, GUIDES_WORD = "Zobrazit vše", "Časté otázky", "Průvodce"
INDEX_TITLE = "Průvodce nákupem kytary"
INDEX_DESC = "Průvodce výběrem elektrické, klasické nebo akustické kytary, baskytary a komba, se skutečnými modely a dnešními cenami."
COURSE_URL, COURSE_TITLE = "kurz/", "Kurz zdarma: tvoje první kytara"
COURSE_DESC = "Pět lekcí od nuly: držení, akordy, rytmus, stupnice a dvě písničky, s metronomem."

GUIDES = [
    {"slug": "prvni-elektricka-kytara", "title": "Jak vybrat první elektrickou kytaru",
     "desc": "Jaký tvar, jaké snímače a kolik utratit za první elektrickou kytaru, s nejprodávanějšími modely do {p300} a jejich dnešní cenou.",
     "body": """<section class="hub-sec guia">
<h2>Jaký tvar</h2>
<ul>
<li><strong>Typ Stratocaster (ST):</strong> nejuniverzálnější a nejpohodlnější, na pop, rock, blues i funk. Pokud váháš, začni tady.</li>
<li><strong>Typ Telecaster (T):</strong> jednodušší, s jasným a přímým zvukem, oblíbená v rocku a country.</li>
<li><strong>Single cut (typ Les Paul):</strong> plnější zvuk a delší sustain, ideální na rock a blues. Obvykle je těžší.</li>
<li><strong>Superstrat:</strong> tenký krk a silné snímače, stavěná na hard rock a metal.</li>
</ul>
<h2>Snímače: single coil, nebo humbucker</h2>
<p><strong>Single coily</strong> znějí jasně a třpytivě; <strong>humbuckery</strong> znějí plněji a se zkreslením méně brumí. Zapojení <strong>HSS</strong> kombinuje obojí a pro začátečníky je nejuniverzálnější.</p>
<h2>Kolik utratit</h2>
<p>V rozmezí <strong>{p150}–{p300}</strong> najdeš kytary, které dobře znějí a vydrží roky: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone nebo Harley Benton, mimo jiné. Elektrická kytara potřebuje <strong>kombo</strong> (nebo malý sluchátkový zesilovač); pokud začínáš od nuly, set často vyjde levněji.</p>
<p>Stejný model se může mezi obchody citelně lišit v ceně. guitle každý den porovnává ceny v {shops} obchodech a ukládá historii cen.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elektrické kytary do {p300}, které prodává nejvíc obchodů (dnešní ceny)")],
     "faqs": [("Jakou elektrickou kytaru koupit jako začátečník?", "Typ Stratocaster se snímači HSS v rozmezí {p150}–{p300}: Yamaha Pacifica, Squier a Ibanez GIO patří k nejčastěji voleným prvním kytarám."),
              ("Potřebuju k elektrické kytaře kombo?", "Ano: bez zesilovače ji skoro neuslyšíš. Na začátek stačí malé cvičné kombo nebo sluchátkový zesilovač."),
              ("Vyplatí se kytarový set pro začátečníky?", "Pokud začínáš od nuly, ano: kytara, kombo a příslušenství vyjdou v setu levněji než zvlášť.")]},
    {"slug": "klasicka-nebo-akusticka-kytara", "title": "Klasická, nebo akustická kytara: kterou vybrat",
     "desc": "Rozdíl mezi klasickou a akustickou kytarou, kterou zvolit jako začátečník, velikosti pro děti a modely s dnešní cenou.",
     "body": """<section class="hub-sec guia">
<h2>Jde hlavně o struny</h2>
<p><strong>Klasická</strong> kytara má <strong>nylonové</strong> struny: jsou měkké na prsty, znějí teple a krk je širší. <strong>Akustická</strong> (westernová) kytara má <strong>ocelové</strong> struny: zní jasněji a hlasitěji, ale ze začátku víc bolí prsty.</p>
<ul>
<li><strong>Klasická:</strong> klasická hudba, flamenco, bossa nova, a také pro děti nebo výuku s učitelem.</li>
<li><strong>Akustická:</strong> pop, rock, folk a doprovod ke zpěvu.</li>
</ul>
<h2>Velikosti</h2>
<p>Klasické kytary se vyrábějí ve velikosti <strong>4/4</strong> pro dospělé, <strong>3/4</strong> pro děti zhruba od 8 do 11 let a <strong>1/2</strong> pro mladší děti. <strong>Elektroakustická</strong> kytara má předzesilovač, takže ji zapojíš do zesilovače.</p>
<h2>Kolik utratit</h2>
<p>Dobré klasické kytary seženeš zhruba od <strong>{p100}–{p200}</strong>, akustické od <strong>{p150}–{p300}</strong>. S masivní deskou znějí lépe a časem se ještě rozehrají. guitle každý den porovnává ceny v {shops} obchodech.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klasické kytary do {p200}, které prodává nejvíc obchodů (dnešní ceny)"),
               ("acustica", 300, 8, 3, True, "Akustické kytary do {p300}, které prodává nejvíc obchodů (dnešní ceny)")],
     "faqs": [("Klasická, nebo akustická kytara pro začátečníky?", "Klasická je díky nylonovým strunám pohodlnější; akustická je lepší, pokud chceš hrát pop, rock nebo folk."),
              ("Jakou velikost kytary potřebuje dítě?", "Zhruba 1/2 do 7–8 let, 3/4 od 8 do 11 let a 4/4 od 12 let."),
              ("Můžu dát na klasickou kytaru ocelové struny?", "Ne: klasická kytara není stavěná na takový tah; může se poškodit krk nebo kobylka.")]},
    {"slug": "prvni-baskytara", "title": "Jak vybrat první baskytaru",
     "desc": "4, nebo 5 strun, Precision, nebo Jazz Bass a kolik utratit za první baskytaru, s nejprodávanějšími modely do {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4, nebo 5 strun</h2>
<p>Začni se <strong>čtyřstrunnou</strong> baskytarou: je to standard téměř v každém žánru. <strong>Pětistrunná</strong> má navíc hlubokou strunu, oblíbenou v metalu a moderním funku, ale i širší krk.</p>
<ul>
<li><strong>Typ Precision (P):</strong> kulatý, pevný zvuk, jednoduchá a účinná.</li>
<li><strong>Typ Jazz Bass (J):</strong> dva snímače a štíhlejší krk, se sevřenějším zvukem.</li>
<li><strong>Short scale:</strong> kratší menzura, pohodlnější pro menší ruce.</li>
</ul>
<p>V rozmezí <strong>{p200}–{p400}</strong> jsou velmi dobré baskytary na začátek. Baskytara potřebuje baskytarové kombo: hluboké tóny můžou kytarové kombo poškodit.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Baskytary do {p400}, které prodává nejvíc obchodů (dnešní ceny)")],
     "faqs": [("Jakou baskytaru koupit jako začátečník?", "Čtyřstrunnou baskytaru typu Precision, Jazz Bass nebo PJ v rozmezí {p200}–{p400}."),
              ("Můžu zapojit baskytaru do kytarového komba?", "Raději ne: hluboké tóny můžou poškodit reproduktor. Potřebuješ baskytarové kombo.")]},
    {"slug": "prvni-kytarovy-zesilovac", "title": "Jaký kytarový zesilovač koupit jako začátečník",
     "desc": "Kolik wattů, modeling, nebo lampy a kolik utratit za první kombo, s nejprodávanějšími modely do {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Doma ti stačí málo</h2>
<p>Na cvičení doma bohatě stačí kombo s výkonem <strong>10 až 30 wattů</strong>; důležité je, aby dobře znělo potichu a mělo <strong>výstup na sluchátka</strong>.</p>
<ul>
<li><strong>Modeling (digitální):</strong> napodobuje spoustu zesilovačů a má vestavěné efekty: na začátek nejpraktičtější (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Lampové:</strong> klasický rockový a bluesový zvuk, dražší a stavěné na hlasité hraní.</li>
</ul>
<p>V rozmezí <strong>{p100}–{p300}</strong> najdeš velmi dobře vybavená cvičná komba.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Komba do {p300}, která prodává nejvíc obchodů (dnešní ceny)")],
     "faqs": [("Jaké kytarové kombo na doma?", "S výkonem 10 až 30 wattů a výstupem na sluchátka; digitální modelingové kombo je na začátek nejpraktičtější.")]},
    {"slug": "kytarove-sety", "title": "Kytarové sety: kdy se vyplatí",
     "desc": "Co obsahuje kytarový set, kdy vyjde levněji než nákup zvlášť a nejprodávanější sety s dnešní cenou.",
     "body": """<section class="hub-sec guia">
<h2>Co je v setu</h2>
<p>Set s elektrickou kytarou obvykle obsahuje <strong>kytaru, malé kombo, obal, kabel, popruh, trsátka a ladičku</strong>. <strong>Vyplatí se</strong>, pokud začínáš od nuly; <strong>méně</strong>, pokud už zesilovač máš nebo chceš konkrétní kytaru. Hlavně se dívej na kytaru: ta ti zůstane.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Sety do {p400}, které prodává nejvíc obchodů (dnešní ceny)")],
     "faqs": [("Vyplatí se kytarový set pro začátečníky?", "Ano, pokud začínáš od nuly: vyjde levněji než kupovat všechno zvlášť.")]},
]
