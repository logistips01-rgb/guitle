"""Guider på dansk (guitle.com/dk/guias/)."""
MORE, FAQ, GUIDES_WORD = "Se alle", "Ofte stillede spørgsmål", "Guider"
INDEX_TITLE = "Guider til køb af guitar"
INDEX_DESC = "Guider til at vælge elguitar, klassisk eller akustisk guitar, elbas og forstærker, med rigtige modeller og dagens priser."
COURSE_URL, COURSE_TITLE = "kursus/", "Gratis kursus: din første guitar"
COURSE_DESC = "Fem lektioner fra bunden: holdning, akkorder, rytme, skalaer og to sange, med metronom."

GUIDES = [
    {"slug": "forste-elguitar", "title": "Sådan vælger du din første elguitar",
     "desc": "Hvilken kropsform, hvilke pickupper og hvor meget du skal bruge på din første elguitar, med de mest solgte under {p300} og deres pris i dag.",
     "body": """<section class="hub-sec guia">
<h2>Hvilken kropsform</h2>
<ul>
<li><strong>Stratocaster-typen (ST):</strong> den mest alsidige og behagelige, til pop, rock, blues og funk. Er du i tvivl, så start her.</li>
<li><strong>Telecaster-typen (T):</strong> enklere, med en klar og direkte lyd, elsket i rock og country.</li>
<li><strong>Single cut (Les Paul-typen):</strong> fyldigere lyd med mere sustain, ideel til rock og blues. Som regel tungere.</li>
<li><strong>Superstrat:</strong> tynd hals og kraftige pickupper, bygget til hardrock og metal.</li>
</ul>
<h2>Pickupper: single coil eller humbucker</h2>
<p><strong>Single coils</strong> lyder klart og funklende; <strong>humbuckere</strong> lyder federe og brummer mindre med forvrængning. En <strong>HSS</strong>-konfiguration kombinerer begge og er den mest alsidige til begyndere.</p>
<h2>Hvor meget skal du bruge</h2>
<p>Mellem <strong>{p150} og {p300}</strong> finder du guitarer, der lyder godt og holder i mange år: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone eller Harley Benton, blandt andre. En elguitar skal bruge en <strong>forstærker</strong> (eller en lille hovedtelefonforstærker); starter du fra bunden, er en pakke ofte billigere.</p>
<p>Den samme model kan koste mærkbart forskelligt fra butik til butik. guitle sammenligner prisen hver dag i {shops} butikker og gemmer prishistorikken.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elguitarer under {p300}, som flest butikker sælger (dagens priser)")],
     "faqs": [("Hvilken elguitar skal man købe som begynder?", "En Stratocaster-type med HSS-pickupper mellem {p150} og {p300}: Yamaha Pacifica, Squier og Ibanez GIO er populære første guitarer."),
              ("Skal jeg have en forstærker til en elguitar?", "Ja: uden forstærker kan du næsten ikke høre den. Til at starte med er en lille øveforstærker eller en hovedtelefonforstærker nok."),
              ("Kan det betale sig med en guitarpakke til begyndere?", "Hvis du starter fra bunden, ja: guitar, forstærker og tilbehør er billigere samlet end hver for sig.")]},
    {"slug": "klassisk-eller-akustisk-guitar", "title": "Klassisk eller akustisk guitar: hvilken skal du vælge",
     "desc": "Forskellen på klassisk og akustisk guitar, hvilken du skal vælge som begynder, størrelser til børn og modeller med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Det handler om strengene</h2>
<p>En <strong>klassisk</strong> guitar har <strong>nylonstrenge</strong>: blide mod fingrene, varm klang og en bredere hals. En <strong>akustisk</strong> guitar (westernguitar) har <strong>stålstrenge</strong>: klarere og kraftigere, men hårdere for fingrene i starten.</p>
<ul>
<li><strong>Klassisk:</strong> klassisk musik, flamenco, bossa nova, og til børn eller undervisning hos en lærer.</li>
<li><strong>Akustisk:</strong> pop, rock, folk og akkompagnement til sang.</li>
</ul>
<h2>Størrelser</h2>
<p>Klassiske guitarer findes i <strong>4/4</strong> til voksne, <strong>3/4</strong> til børn fra cirka 8 til 11 år og <strong>1/2</strong> til yngre børn. En <strong>elektroakustisk</strong> guitar har en indbygget forforstærker, så du kan slutte den til en forstærker.</p>
<h2>Hvor meget skal du bruge</h2>
<p>Gode klassiske guitarer fra cirka <strong>{p100}–{p200}</strong>, akustiske fra <strong>{p150}–{p300}</strong>. Med massivt dæk lyder de bedre og bliver smukkere med årene. guitle sammenligner prisen hver dag i {shops} butikker.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klassiske guitarer under {p200}, som flest butikker sælger (dagens priser)"),
               ("acustica", 300, 8, 3, True, "Akustiske guitarer under {p300}, som flest butikker sælger (dagens priser)")],
     "faqs": [("Klassisk eller akustisk guitar til begyndere?", "Klassisk er mere behagelig takket være nylonstrengene; akustisk er bedre, hvis du vil spille pop, rock eller folk."),
              ("Hvilken guitarstørrelse skal et barn have?", "Groft sagt 1/2 op til 7–8 år, 3/4 fra 8 til 11 år og 4/4 fra 12 år."),
              ("Kan jeg sætte stålstrenge på en klassisk guitar?", "Nej: en klassisk guitar er ikke bygget til den strengspænding; halsen eller stolen kan tage skade.")]},
    {"slug": "forste-elbas", "title": "Sådan vælger du din første elbas",
     "desc": "4 eller 5 strenge, Precision eller Jazz Bass og hvor meget du skal bruge på din første bas, med de mest solgte under {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 eller 5 strenge</h2>
<p>Start med en <strong>4-strenget</strong> bas: standarden i næsten alle genrer. En <strong>5-strenget</strong> har en ekstra dyb streng, populær i metal og moderne funk, men halsen er bredere.</p>
<ul>
<li><strong>Precision-typen (P):</strong> rund og kraftig lyd, enkel og effektiv.</li>
<li><strong>Jazz Bass-typen (J):</strong> to pickupper og en slankere hals, med en mere defineret lyd.</li>
<li><strong>Short scale:</strong> kortere mensur, mere behagelig til små hænder.</li>
</ul>
<p>Mellem <strong>{p200} og {p400}</strong> findes der rigtig gode basser at starte på. En bas skal bruge en basforstærker: de dybe toner kan skade en guitarforstærker.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Elbasser under {p400}, som flest butikker sælger (dagens priser)")],
     "faqs": [("Hvilken elbas skal man købe som begynder?", "En 4-strenget Precision-, Jazz Bass- eller PJ-bas mellem {p200} og {p400}."),
              ("Kan jeg slutte en bas til en guitarforstærker?", "Helst ikke: de dybe toner kan skade højttaleren. Du skal bruge en basforstærker.")]},
    {"slug": "forste-guitarforstaerker", "title": "Hvilken guitarforstærker skal man købe som begynder",
     "desc": "Hvor mange watt, modellering eller rør og hvor meget du skal bruge på din første forstærker, med de mest solgte under {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Derhjemme skal du ikke bruge meget</h2>
<p>Til at øve derhjemme er en forstærker på <strong>10 til 30 watt</strong> rigeligt; det vigtige er, at den lyder godt ved lav lydstyrke og har <strong>hovedtelefonudgang</strong>.</p>
<ul>
<li><strong>Modellering (digital):</strong> efterligner mange forstærkere og har indbyggede effekter: det mest praktiske at starte med (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Rør:</strong> den klassiske rock- og blueslyd, dyrere og bygget til at spille højt.</li>
</ul>
<p>Mellem <strong>{p100} og {p300}</strong> finder du meget komplette øveforstærkere.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Forstærkere under {p300}, som flest butikker sælger (dagens priser)")],
     "faqs": [("Hvilken guitarforstærker er god derhjemme?", "En på 10 til 30 watt med hovedtelefonudgang; en digital modelleringsforstærker er det mest praktiske at starte med.")]},
    {"slug": "guitarpakker", "title": "Guitarpakker: hvornår kan de betale sig",
     "desc": "Hvad en guitarpakke indeholder, hvornår den er billigere end at købe alt hver for sig, og de mest solgte pakker med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Hvad er der i en pakke</h2>
<p>En elguitarpakke indeholder som regel <strong>guitar, lille forstærker, gigbag, kabel, guitarrem, plektre og stemmeapparat</strong>. Den <strong>kan betale sig</strong>, hvis du starter fra bunden; <strong>mindre</strong>, hvis du allerede har en forstærker eller vil have en bestemt guitar. Kig især på guitaren: det er den, du beholder.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Pakker under {p400}, som flest butikker sælger (dagens priser)")],
     "faqs": [("Kan det betale sig med en guitarpakke til begyndere?", "Ja, hvis du starter fra bunden: det er billigere end at købe alt hver for sig.")]},
]
