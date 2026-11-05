"""Guider på norsk bokmål (guitle.com/no/guias/)."""
MORE, FAQ, GUIDES_WORD = "Se alle", "Ofte stilte spørsmål", "Guider"
INDEX_TITLE = "Guider for å kjøpe gitar"
INDEX_DESC = "Guider for å velge elgitar, klassisk eller akustisk gitar, bassgitar og forsterker, med ekte modeller og dagens priser."
COURSE_URL, COURSE_TITLE = "kurs/", "Gratis kurs: din første gitar"
COURSE_DESC = "Fem leksjoner fra null: holdning, akkorder, rytme, skalaer og to låter, med metronom."

GUIDES = [
    {"slug": "forste-elgitar", "title": "Slik velger du din første elgitar",
     "desc": "Hvilken kroppsform, hvilke pickuper og hvor mye du bør bruke på din første elgitar, med de mest solgte under {p300} og dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Hvilken kroppsform</h2>
<ul>
<li><strong>Stratocaster-typen (ST):</strong> den mest allsidige og komfortable, for pop, rock, blues og funk. Er du i tvil, start her.</li>
<li><strong>Telecaster-typen (T):</strong> enklere, med en klar og direkte lyd, elsket i rock og country.</li>
<li><strong>Single cut (Les Paul-typen):</strong> fyldigere lyd med mer sustain, ideell for rock og blues. Som regel tyngre.</li>
<li><strong>Superstrat:</strong> tynn hals og kraftige pickuper, laget for hardrock og metal.</li>
</ul>
<h2>Pickuper: single coil eller humbucker</h2>
<p><strong>Single coils</strong> låter klart og glitrende; <strong>humbuckere</strong> låter fetere og brummer mindre med vreng. En <strong>HSS</strong>-konfigurasjon kombinerer begge og er den mest allsidige for nybegynnere.</p>
<h2>Hvor mye bør du bruke</h2>
<p>Mellom <strong>{p150} og {p300}</strong> finner du gitarer som låter bra og varer i mange år: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone eller Harley Benton, blant andre. En elgitar trenger en <strong>forsterker</strong> (eller en liten hodetelefonforsterker); starter du fra null, er en pakke ofte billigere.</p>
<p>Den samme modellen kan koste merkbart forskjellig fra butikk til butikk. guitle sammenligner prisen hver dag i {shops} butikker og lagrer prishistorikken.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elgitarer under {p300} som flest butikker selger (dagens priser)")],
     "faqs": [("Hvilken elgitar bør en nybegynner kjøpe?", "En Stratocaster-type med HSS-pickuper mellom {p150} og {p300}: Yamaha Pacifica, Squier og Ibanez GIO er populære førstegitarer."),
              ("Trenger jeg forsterker til en elgitar?", "Ja: uten forsterker hører du den knapt. For å begynne holder det med en liten øvingsforsterker eller en hodetelefonforsterker."),
              ("Lønner det seg med en gitarpakke for nybegynnere?", "Hvis du starter fra null, ja: gitar, forsterker og tilbehør blir billigere samlet enn hver for seg.")]},
    {"slug": "klassisk-eller-akustisk-gitar", "title": "Klassisk eller akustisk gitar: hvilken skal du velge",
     "desc": "Forskjellen mellom klassisk og akustisk gitar, hvilken du bør velge som nybegynner, størrelser for barn og modeller med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Det handler om strengene</h2>
<p>En <strong>klassisk</strong> gitar har <strong>nylonstrenger</strong>: snille mot fingrene, varm klang og bredere hals. En <strong>akustisk</strong> gitar (westerngitar) har <strong>stålstrenger</strong>: klarere og kraftigere, men tøffere for fingrene i starten.</p>
<ul>
<li><strong>Klassisk:</strong> klassisk musikk, flamenco, bossa nova, og for barn eller timer med lærer.</li>
<li><strong>Akustisk:</strong> pop, rock, folk og akkompagnement til sang.</li>
</ul>
<h2>Størrelser</h2>
<p>Klassiske gitarer finnes i <strong>4/4</strong> for voksne, <strong>3/4</strong> for barn fra omtrent 8 til 11 år og <strong>1/2</strong> for yngre barn. En <strong>elektroakustisk</strong> gitar har en innebygd forforsterker, så du kan koble den til en forsterker.</p>
<h2>Hvor mye bør du bruke</h2>
<p>Gode klassiske gitarer fra omtrent <strong>{p100}–{p200}</strong>, akustiske fra <strong>{p150}–{p300}</strong>. Med massivt lokk låter de bedre og blir finere med årene. guitle sammenligner prisen hver dag i {shops} butikker.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klassiske gitarer under {p200} som flest butikker selger (dagens priser)"),
               ("acustica", 300, 8, 3, True, "Akustiske gitarer under {p300} som flest butikker selger (dagens priser)")],
     "faqs": [("Klassisk eller akustisk gitar for nybegynnere?", "Klassisk er mer komfortabel takket være nylonstrengene; akustisk er bedre hvis du vil spille pop, rock eller folk."),
              ("Hvilken gitarstørrelse trenger et barn?", "Omtrent 1/2 opp til 7–8 år, 3/4 fra 8 til 11 år og 4/4 fra 12 år."),
              ("Kan jeg sette stålstrenger på en klassisk gitar?", "Nei: en klassisk gitar er ikke bygget for den strengspenningen; halsen eller stolen kan bli skadet.")]},
    {"slug": "forste-bassgitar", "title": "Slik velger du din første bassgitar",
     "desc": "4 eller 5 strenger, Precision eller Jazz Bass og hvor mye du bør bruke på din første bass, med de mest solgte under {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 eller 5 strenger</h2>
<p>Begynn med en <strong>4-strengs</strong> bass: standarden i nesten alle stilarter. En <strong>5-strengs</strong> har en ekstra dyp streng, populær i metal og moderne funk, men halsen er bredere.</p>
<ul>
<li><strong>Precision-typen (P):</strong> rund og kraftig lyd, enkel og effektiv.</li>
<li><strong>Jazz Bass-typen (J):</strong> to pickuper og slankere hals, med en mer definert lyd.</li>
<li><strong>Short scale:</strong> kortere mensur, mer komfortabel for små hender.</li>
</ul>
<p>Mellom <strong>{p200} og {p400}</strong> finnes det veldig gode basser å begynne med. En bass trenger en bassforsterker: de dype tonene kan skade en gitarforsterker.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Bassgitarer under {p400} som flest butikker selger (dagens priser)")],
     "faqs": [("Hvilken bassgitar bør en nybegynner kjøpe?", "En 4-strengs Precision-, Jazz Bass- eller PJ-bass mellom {p200} og {p400}."),
              ("Kan jeg koble en bass til en gitarforsterker?", "Helst ikke: de dype tonene kan skade høyttaleren. Du trenger en bassforsterker.")]},
    {"slug": "forste-gitarforsterker", "title": "Hvilken gitarforsterker bør en nybegynner kjøpe",
     "desc": "Hvor mange watt, modellering eller rør og hvor mye du bør bruke på din første forsterker, med de mest solgte under {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Hjemme trenger du ikke mye</h2>
<p>For å øve hjemme holder det i massevis med en forsterker på <strong>10 til 30 watt</strong>; det viktige er at den låter bra på lavt volum og har <strong>hodetelefonutgang</strong>.</p>
<ul>
<li><strong>Modellering (digital):</strong> etterligner mange forsterkere og har innebygde effekter: det mest praktiske å begynne med (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Rør:</strong> den klassiske rock- og bluesklangen, dyrere og laget for å spilles høyt.</li>
</ul>
<p>Mellom <strong>{p100} og {p300}</strong> finner du svært komplette øvingsforsterkere.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Forsterkere under {p300} som flest butikker selger (dagens priser)")],
     "faqs": [("Hvilken gitarforsterker passer hjemme?", "En på 10 til 30 watt med hodetelefonutgang; en digital modelleringsforsterker er det mest praktiske å begynne med.")]},
    {"slug": "gitarpakker", "title": "Gitarpakker: når lønner de seg",
     "desc": "Hva som følger med i en gitarpakke, når den er billigere enn å kjøpe alt hver for seg, og de mest solgte pakkene med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Hva følger med i en pakke</h2>
<p>En elgitarpakke inneholder som regel <strong>gitar, liten forsterker, gigbag, kabel, gitarreim, plekter og stemmeapparat</strong>. Den <strong>lønner seg</strong> hvis du starter fra null; <strong>mindre</strong> hvis du allerede har en forsterker eller vil ha en bestemt gitar. Se først og fremst på gitaren: det er den du beholder.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Pakker under {p400} som flest butikker selger (dagens priser)")],
     "faqs": [("Lønner det seg med en gitarpakke for nybegynnere?", "Ja, hvis du starter fra null: det er billigere enn å kjøpe alt hver for seg.")]},
]
