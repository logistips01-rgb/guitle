"""Ratgeber auf Deutsch (guitle.com/de/guias/, /at/, /ch/)."""
MORE, FAQ, GUIDES_WORD = "Alle ansehen", "Häufige Fragen", "Ratgeber"
INDEX_TITLE = "Ratgeber zum Gitarrenkauf"
INDEX_DESC = "Ratgeber zur Wahl von E-Gitarre, Konzert- oder Westerngitarre, Bass und Verstärker, mit echten Modellen und heutigen Preisen."
COURSE_URL, COURSE_TITLE = "kurs/", "Kostenloser Kurs: deine erste Gitarre"
COURSE_DESC = "Fünf Lektionen von null an: Haltung, Akkorde, Rhythmus, Tonleitern und zwei Songs, mit Metronom."

GUIDES = [
    {"slug": "erste-e-gitarre", "title": "So findest du deine erste E-Gitarre",
     "desc": "Welche Form, welche Tonabnehmer und wie viel Budget für deine erste E-Gitarre, mit den meistverkauften unter {p300} und ihrem heutigen Preis.",
     "body": """<section class="hub-sec guia">
<h2>Welche Form</h2>
<ul>
<li><strong>ST-Form (Stratocaster):</strong> die vielseitigste und bequemste, für Pop, Rock, Blues und Funk. Im Zweifel fang hier an.</li>
<li><strong>T-Form (Telecaster):</strong> schlichter, mit hellem, direktem Klang, beliebt in Rock und Country.</li>
<li><strong>Single Cut (Les-Paul-Form):</strong> fetter Klang mit viel Sustain, ideal für Rock und Blues. Meist schwerer.</li>
<li><strong>Superstrat:</strong> dünner Hals und kräftige Tonabnehmer, gebaut für Hard Rock und Metal.</li>
</ul>
<h2>Tonabnehmer: Single Coil oder Humbucker</h2>
<p><strong>Single Coils</strong> klingen klar und brillant; <strong>Humbucker</strong> klingen fetter und brummen bei Verzerrung weniger. Eine <strong>HSS</strong>-Bestückung vereint beides und ist für Einsteiger am vielseitigsten.</p>
<h2>Wie viel ausgeben</h2>
<p>Zwischen <strong>{p150} und {p300}</strong> gibt es Gitarren, die gut klingen und jahrelang halten: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone oder Harley Benton, unter anderen. Eine E-Gitarre braucht einen <strong>Verstärker</strong> (oder einen kleinen Kopfhörerverstärker); wer bei null anfängt, fährt mit einem Set oft günstiger.</p>
<p>Dasselbe Modell kann zwischen Shops um zig Euro schwanken. guitle vergleicht den Preis täglich in {shops} Shops und speichert den Preisverlauf.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "E-Gitarren unter {p300}, die die meisten Shops führen (heutige Preise)")],
     "faqs": [("Welche E-Gitarre sollte man als Anfänger kaufen?", "Eine Gitarre in ST-Form mit HSS-Tonabnehmern zwischen {p150} und {p300}: Yamaha Pacifica, Squier oder Ibanez GIO sind typische Einsteigermodelle."),
              ("Brauche ich einen Verstärker für die E-Gitarre?", "Ja: ohne Verstärker hört man sie kaum. Zum Anfangen reicht ein kleiner Übungsverstärker oder Kopfhörerverstärker."),
              ("Lohnt sich ein E-Gitarren-Set?", "Wenn du bei null anfängst, ja: Gitarre, Verstärker und Zubehör sind zusammen günstiger als einzeln.")]},
    {"slug": "konzert-oder-westerngitarre", "title": "Konzertgitarre oder Westerngitarre: welche wählen",
     "desc": "Unterschiede zwischen Konzert- und Westerngitarre, welche sich für den Einstieg eignet, Größen für Kinder und Modelle mit heutigen Preisen.",
     "body": """<section class="hub-sec guia">
<h2>Der Unterschied liegt in den Saiten</h2>
<p>Die <strong>Konzertgitarre</strong> hat <strong>Nylonsaiten</strong>: weich für die Finger, warmer Klang und breiterer Hals. Die <strong>Westerngitarre</strong> hat <strong>Stahlsaiten</strong>: brillanter und lauter, am Anfang aber härter für die Finger.</p>
<ul>
<li><strong>Konzertgitarre:</strong> Klassik, Flamenco, Bossa Nova sowie für Kinder und den Unterricht.</li>
<li><strong>Westerngitarre:</strong> Pop, Rock, Folk und Liedbegleitung.</li>
</ul>
<h2>Größen</h2>
<p>Konzertgitarren gibt es in <strong>4/4</strong> für Erwachsene, <strong>3/4</strong> für Kinder von etwa 8 bis 11 Jahren und <strong>1/2</strong> für Jüngere. Eine <strong>Elektroakustik</strong>-Gitarre hat einen Preamp zum Anschluss an einen Verstärker.</p>
<h2>Wie viel ausgeben</h2>
<p>Gute Konzertgitarren gibt es ab etwa <strong>{p100}–{p200}</strong>, Westerngitarren ab <strong>{p150}–{p300}</strong>. Mit massiver Decke klingen sie besser und reifen mit der Zeit. guitle vergleicht den Preis täglich in {shops} Shops.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Konzertgitarren unter {p200}, die die meisten Shops führen (heutige Preise)"),
               ("acustica", 300, 8, 3, True, "Westerngitarren unter {p300}, die die meisten Shops führen (heutige Preise)")],
     "faqs": [("Konzert- oder Westerngitarre für Anfänger?", "Die Konzertgitarre ist dank Nylonsaiten bequemer; die Westerngitarre passt besser, wenn du Pop, Rock oder Folk spielen willst."),
              ("Welche Gitarrengröße braucht ein Kind?", "Grob 1/2 bis 7-8 Jahre, 3/4 von 8 bis 11 und 4/4 ab 12 Jahren."),
              ("Kann man Stahlsaiten auf eine Konzertgitarre ziehen?", "Nein: Sie ist nicht für diese Spannung gebaut, Hals oder Steg können Schaden nehmen.")]},
    {"slug": "erster-e-bass", "title": "So findest du deinen ersten E-Bass",
     "desc": "4 oder 5 Saiten, Precision oder Jazz Bass und wie viel Budget für deinen ersten Bass, mit den meistverkauften unter {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 oder 5 Saiten</h2>
<p>Fang mit einem <strong>4-Saiter</strong> an: Er ist in fast allen Stilen Standard. Ein <strong>5-Saiter</strong> hat eine zusätzliche tiefe Saite, beliebt in Metal und modernem Funk, aber einen breiteren Hals.</p>
<ul>
<li><strong>Precision-Form (P):</strong> runder, druckvoller Klang, einfach und effektiv.</li>
<li><strong>Jazz-Bass-Form (J):</strong> zwei Tonabnehmer und schlankerer Hals, definierterer Klang.</li>
<li><strong>Short Scale:</strong> kürzere Mensur, bequemer für kleine Hände.</li>
</ul>
<p>Zwischen <strong>{p200} und {p400}</strong> gibt es sehr gute Einsteigerbässe. Ein Bass braucht einen Bassverstärker: Die tiefen Töne können einen Gitarrenverstärker beschädigen.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Bässe unter {p400}, die die meisten Shops führen (heutige Preise)")],
     "faqs": [("Welchen Bass sollte man als Anfänger kaufen?", "Einen 4-Saiter in Precision-, Jazz-Bass- oder PJ-Form zwischen {p200} und {p400}."),
              ("Kann man einen Bass an einen Gitarrenverstärker anschließen?", "Nicht empfehlenswert: Die tiefen Frequenzen können den Lautsprecher beschädigen. Du brauchst einen Bassverstärker.")]},
    {"slug": "erster-gitarrenverstaerker", "title": "Welcher Gitarrenverstärker für Einsteiger",
     "desc": "Wie viel Watt, Modeling oder Röhre und wie viel Budget für deinen ersten Verstärker, mit den meistverkauften unter {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Für zu Hause reicht wenig</h2>
<p>Zum Üben zu Hause reichen <strong>10 bis 30 Watt</strong> völlig; wichtig ist, dass er leise gut klingt und einen <strong>Kopfhörerausgang</strong> hat.</p>
<ul>
<li><strong>Modeling (digital):</strong> simuliert viele Verstärker und hat Effekte eingebaut: am praktischsten für den Einstieg (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Röhre:</strong> der klassische Rock- und Bluessound, teurer und zum lauten Spielen gedacht.</li>
</ul>
<p>Zwischen <strong>{p100} und {p300}</strong> gibt es sehr komplette Übungsverstärker.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Verstärker unter {p300}, die die meisten Shops führen (heutige Preise)")],
     "faqs": [("Welcher Gitarrenverstärker für zu Hause?", "Einer mit 10 bis 30 Watt und Kopfhörerausgang; ein digitaler Modeling-Verstärker ist für den Einstieg am praktischsten.")]},
    {"slug": "gitarren-sets", "title": "Gitarren-Sets: wann lohnen sie sich",
     "desc": "Was in einem Gitarren-Set steckt, wann es sich gegenüber dem Einzelkauf lohnt und die meistverkauften Sets mit heutigen Preisen.",
     "body": """<section class="hub-sec guia">
<h2>Was in einem Set steckt</h2>
<p>Ein E-Gitarren-Set enthält meist <strong>Gitarre, kleinen Verstärker, Tasche, Kabel, Gurt, Plektren und Stimmgerät</strong>. Es <strong>lohnt sich</strong>, wenn du bei null anfängst; <strong>weniger</strong>, wenn du schon einen Verstärker hast oder eine bestimmte Gitarre willst. Achte vor allem auf die Gitarre: Sie bleibt.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Sets unter {p400}, die die meisten Shops führen (heutige Preise)")],
     "faqs": [("Lohnt sich ein Gitarren-Set für Anfänger?", "Ja, wenn du bei null anfängst: Es ist günstiger als alles einzeln zu kaufen.")]},
]
