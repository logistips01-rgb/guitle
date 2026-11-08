"""Guider på svenska (guitle.com/se/guias/)."""
MORE, FAQ, GUIDES_WORD = "Visa alla", "Vanliga frågor", "Guider"
INDEX_TITLE = "Guider för att köpa gitarr"
INDEX_DESC = "Guider för att välja elgitarr, klassisk eller akustisk gitarr, elbas och förstärkare, med riktiga modeller och dagens priser."
COURSE_URL, COURSE_TITLE = "kurs/", "Gratis kurs: din första gitarr"
COURSE_DESC = "Fem lektioner från noll: hållning, ackord, rytm, skalor och två låtar, med metronom."

GUIDES = [
    {"slug": "forsta-elgitarren", "title": "Så väljer du din första elgitarr",
     "desc": "Vilken kroppsform, vilka mikrofoner och hur mycket du ska lägga på din första elgitarr, med de mest sålda under {p300} och deras pris i dag.",
     "body": """<section class="hub-sec guia">
<h2>Vilken kroppsform</h2>
<ul>
<li><strong>Stratocaster-typ (ST):</strong> den mest mångsidiga och bekväma, för pop, rock, blues och funk. Är du osäker, börja här.</li>
<li><strong>Telecaster-typ (T):</strong> enklare, med en klar och direkt ton, älskad inom rock och country.</li>
<li><strong>Single cut (Les Paul-typ):</strong> fylligare ton med mer sustain, perfekt för rock och blues. Oftast tyngre.</li>
<li><strong>Superstrat:</strong> tunn hals och kraftfulla mikrofoner, byggd för hårdrock och metal.</li>
</ul>
<h2>Mikrofoner: single coil eller humbucker</h2>
<p><strong>Single coils</strong> låter klart och glittrigt; <strong>humbuckers</strong> låter fetare och brummar mindre med distorsion. En <strong>HSS</strong>-konfiguration kombinerar båda och är den mest mångsidiga för nybörjare.</p>
<h2>Hur mycket ska du lägga</h2>
<p>Mellan <strong>{p150} och {p300}</strong> hittar du gitarrer som låter bra och håller i många år: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone eller Harley Benton, bland andra. En elgitarr behöver en <strong>förstärkare</strong> (eller en liten hörlursförstärkare); börjar du från noll är ett paket ofta billigare.</p>
<p>Samma modell kan kosta märkbart olika mycket i olika butiker. guitle jämför priset varje dag i {shops} butiker och sparar prishistoriken.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elgitarrer under {p300} som flest butiker säljer (dagens priser)")],
     "faqs": [("Vilken elgitarr ska man köpa som nybörjare?", "En Stratocaster-typ med HSS-mikrofoner mellan {p150} och {p300}: Yamaha Pacifica, Squier och Ibanez GIO är populära förstagitarrer."),
              ("Behöver jag en förstärkare till en elgitarr?", "Ja: utan förstärkare hörs den knappt. För att börja räcker en liten övningsförstärkare eller hörlursförstärkare."),
              ("Är ett gitarrpaket för nybörjare värt det?", "Om du börjar från noll, ja: gitarr, förstärkare och tillbehör blir billigare tillsammans än var för sig.")]},
    {"slug": "klassisk-eller-akustisk-gitarr", "title": "Klassisk eller akustisk gitarr: vilken ska du välja",
     "desc": "Skillnaden mellan klassisk och akustisk gitarr, vilken du ska välja som nybörjare, storlekar för barn och modeller med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Det handlar om strängarna</h2>
<p>En <strong>klassisk</strong> gitarr har <strong>nylonsträngar</strong>: snälla mot fingrarna, varm ton och en bredare hals. En <strong>akustisk</strong> gitarr (stålsträngad, westerngitarr) har <strong>stålsträngar</strong>: klarare och starkare, men i början tuffare för fingrarna.</p>
<ul>
<li><strong>Klassisk:</strong> klassisk musik, flamenco, bossa nova, och för barn eller lektioner med lärare.</li>
<li><strong>Akustisk:</strong> pop, rock, folk och att ackompanjera sång.</li>
</ul>
<h2>Storlekar</h2>
<p>Klassiska gitarrer finns i <strong>4/4</strong> för vuxna, <strong>3/4</strong> för barn från ungefär 8 till 11 år och <strong>1/2</strong> för yngre barn. En <strong>elakustisk</strong> gitarr har en inbyggd förförstärkare så att du kan koppla in den i en förstärkare.</p>
<h2>Hur mycket ska du lägga</h2>
<p>Bra klassiska gitarrer från ungefär <strong>{p100}–{p200}</strong>, akustiska från <strong>{p150}–{p300}</strong>. Med massivt lock låter de bättre och blir finare med åren. guitle jämför priset varje dag i {shops} butiker.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klassiska gitarrer under {p200} som flest butiker säljer (dagens priser)"),
               ("acustica", 300, 8, 3, True, "Akustiska gitarrer under {p300} som flest butiker säljer (dagens priser)")],
     "faqs": [("Klassisk eller akustisk gitarr för nybörjare?", "Klassisk är bekvämare tack vare nylonsträngarna; akustisk är bättre om du vill spela pop, rock eller folk."),
              ("Vilken gitarrstorlek behöver ett barn?", "Ungefär 1/2 upp till 7–8 år, 3/4 från 8 till 11 år och 4/4 från 12 år."),
              ("Kan jag sätta stålsträngar på en klassisk gitarr?", "Nej: en klassisk gitarr är inte byggd för den spänningen; halsen eller stallet kan skadas.")]},
    {"slug": "forsta-elbasen", "title": "Så väljer du din första elbas",
     "desc": "4 eller 5 strängar, Precision eller Jazz Bass och hur mycket du ska lägga på din första bas, med de mest sålda under {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 eller 5 strängar</h2>
<p>Börja med en <strong>4-strängad</strong> bas: standarden i nästan alla stilar. En <strong>5-strängad</strong> har en extra djup sträng, populär inom metal och modern funk, men halsen är bredare.</p>
<ul>
<li><strong>Precision-typ (P):</strong> rund och kraftfull ton, enkel och effektiv.</li>
<li><strong>Jazz Bass-typ (J):</strong> två mikrofoner och smalare hals, med en mer distinkt ton.</li>
<li><strong>Short scale:</strong> kortare skala, bekvämare för små händer.</li>
</ul>
<p>Mellan <strong>{p200} och {p400}</strong> finns det riktigt bra basar att börja med. En bas behöver en basförstärkare: de djupa tonerna kan skada en gitarrförstärkare.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Elbasar under {p400} som flest butiker säljer (dagens priser)")],
     "faqs": [("Vilken elbas ska man köpa som nybörjare?", "En 4-strängad Precision-, Jazz Bass- eller PJ-bas mellan {p200} och {p400}."),
              ("Kan jag koppla en bas till en gitarrförstärkare?", "Helst inte: de djupa tonerna kan skada högtalaren. Du behöver en basförstärkare.")]},
    {"slug": "forsta-gitarrforstarkaren", "title": "Vilken gitarrförstärkare ska man köpa som nybörjare",
     "desc": "Hur många watt, modellering eller rör och hur mycket du ska lägga på din första förstärkare, med de mest sålda under {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Hemma behöver du inte mycket</h2>
<p>För att öva hemma räcker en förstärkare på <strong>10 till 30 watt</strong> gott och väl; det viktiga är att den låter bra på låg volym och har ett <strong>hörlursuttag</strong>.</p>
<ul>
<li><strong>Modellering (digital):</strong> efterliknar många förstärkare och har inbyggda effekter: det smidigaste att börja med (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Rör:</strong> det klassiska rock- och blussoundet, dyrare och byggda för att spelas högt.</li>
</ul>
<p>Mellan <strong>{p100} och {p300}</strong> hittar du mycket kompletta övningsförstärkare.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Förstärkare under {p300} som flest butiker säljer (dagens priser)")],
     "faqs": [("Vilken gitarrförstärkare passar hemma?", "En på 10 till 30 watt med hörlursuttag; en digital modelleringsförstärkare är det smidigaste att börja med.")]},
    {"slug": "gitarrpaket", "title": "Gitarrpaket: när är de värda det",
     "desc": "Vad som ingår i ett gitarrpaket, när det är billigare än att köpa allt separat, och de mest sålda paketen med dagens pris.",
     "body": """<section class="hub-sec guia">
<h2>Vad ingår i ett paket</h2>
<p>Ett elgitarrpaket innehåller oftast <strong>gitarr, liten förstärkare, gigbag, kabel, axelband, plektrum och stämapparat</strong>. Det är <strong>värt det</strong> om du börjar från noll; <strong>mindre</strong> om du redan har en förstärkare eller vill ha en viss gitarr. Titta framför allt på gitarren: det är den du behåller.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Paket under {p400} som flest butiker säljer (dagens priser)")],
     "faqs": [("Är ett gitarrpaket värt det för nybörjare?", "Ja, om du börjar från noll: det är billigare än att köpa allt separat.")]},
]
