"""Guide in italiano (guitle.com/it/guias/)."""
MORE, FAQ, GUIDES_WORD = "Vedi tutte", "Domande frequenti", "Guide"
INDEX_TITLE = "Guide per comprare una chitarra"
INDEX_DESC = "Guide per scegliere chitarra elettrica, classica o acustica, basso e amplificatore, con modelli e prezzi reali di oggi."
COURSE_URL, COURSE_TITLE = "corso/", "Corso gratuito: la tua prima chitarra"
COURSE_DESC = "Cinque lezioni da zero: postura, accordi, ritmo, scale e due canzoni, con metronomo."

GUIDES = [
    {"slug": "prima-chitarra-elettrica", "title": "Come scegliere la prima chitarra elettrica",
     "desc": "Che forma, che pickup e quanto spendere per la tua prima chitarra elettrica, con le più vendute sotto i {p300} e il prezzo di oggi in ogni negozio.",
     "body": """<section class="hub-sec guia">
<h2>Che forma scegliere</h2>
<ul>
<li><strong>Tipo Stratocaster (ST):</strong> la più versatile e comoda, per pop, rock, blues e funk. Nel dubbio, parti da qui.</li>
<li><strong>Tipo Telecaster (T):</strong> più semplice, con un suono brillante e diretto, molto usata nel rock e nel country.</li>
<li><strong>Single cut (tipo Les Paul):</strong> suono più corposo e più sustain, ideale per rock e blues. Di solito pesa di più.</li>
<li><strong>Superstrat:</strong> manico sottile e pickup potenti, pensata per hard rock e metal.</li>
</ul>
<h2>Pickup: single coil o humbucker</h2>
<p>I <strong>single coil</strong> suonano chiari e brillanti; gli <strong>humbucker</strong> più corposi e con meno ronzio in distorsione. La configurazione <strong>HSS</strong> unisce entrambi: la più versatile per iniziare.</p>
<h2>Quanto spendere</h2>
<p>Tra <strong>{p150} e {p300}</strong> ci sono chitarre che suonano bene e durano anni: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone o Harley Benton, tra le altre. Un'elettrica ha bisogno di un <strong>amplificatore</strong> (o di un piccolo ampli per cuffie); se parti da zero, un kit di solito costa meno.</p>
<p>Lo stesso modello può variare di decine di euro tra un negozio e l'altro. Su guitle confrontiamo il prezzo in {shops} negozi ogni giorno e ne conserviamo lo storico.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Le elettriche sotto i {p300} vendute da più negozi (prezzi di oggi)")],
     "faqs": [("Quale chitarra elettrica comprare per iniziare?", "Una tipo Stratocaster con pickup HSS tra {p150} e {p300}: Yamaha Pacifica, Squier o Ibanez GIO sono modelli molto comuni per iniziare."),
              ("Serve un amplificatore per suonare la chitarra elettrica?", "Sì: senza ampli quasi non si sente. Per iniziare basta un piccolo ampli da studio o un ampli per cuffie."),
              ("Conviene un kit chitarra elettrica?", "Se parti da zero sì: chitarra, ampli e accessori costano meno che comprati separatamente.")]},
    {"slug": "chitarra-classica-o-acustica", "title": "Chitarra classica o acustica: quale scegliere",
     "desc": "Differenze tra chitarra classica e acustica, quale scegliere per iniziare, misure per bambini e modelli con il prezzo di oggi.",
     "body": """<section class="hub-sec guia">
<h2>La differenza sta nelle corde</h2>
<p>La <strong>classica</strong> ha corde in <strong>nylon</strong>: morbide per le dita, dal suono caldo e con il manico largo. L'<strong>acustica</strong> ha corde in <strong>acciaio</strong>: più brillante e potente, ma all'inizio più dura per le dita.</p>
<ul>
<li><strong>Classica:</strong> musica classica, flamenco, bossa nova, e per bambini o per studiare con un insegnante.</li>
<li><strong>Acustica:</strong> pop, rock, folk e accompagnare il canto.</li>
</ul>
<h2>Misure</h2>
<p>Le classiche esistono in <strong>4/4</strong> per adulti, <strong>3/4</strong> per bambini di circa 8-11 anni e <strong>1/2</strong> per i più piccoli. Un'<strong>elettroacustica</strong> ha un preamplificatore per collegarla a un ampli.</p>
<h2>Quanto spendere</h2>
<p>Buone classiche da <strong>{p100}–{p200}</strong>, acustiche da <strong>{p150}–{p300}</strong>. Con tavola massello suonano meglio e migliorano col tempo. Su guitle confrontiamo il prezzo in {shops} negozi ogni giorno.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Classiche sotto i {p200} vendute da più negozi (prezzi di oggi)"),
               ("acustica", 300, 8, 3, True, "Acustiche sotto i {p300} vendute da più negozi (prezzi di oggi)")],
     "faqs": [("Per iniziare meglio chitarra classica o acustica?", "La classica è più comoda grazie al nylon; l'acustica è meglio se vuoi suonare pop, rock o folk."),
              ("Che misura di chitarra serve a un bambino?", "Indicativamente 1/2 fino a 7-8 anni, 3/4 dagli 8 agli 11 e 4/4 dai 12 anni."),
              ("Si possono montare corde in acciaio su una classica?", "No: la classica non è fatta per quella tensione, il manico o il ponte possono rovinarsi.")]},
    {"slug": "primo-basso-elettrico", "title": "Come scegliere il primo basso elettrico",
     "desc": "4 o 5 corde, Precision o Jazz Bass e quanto spendere per il tuo primo basso, con i più venduti sotto i {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 o 5 corde</h2>
<p>Per iniziare, un basso a <strong>4 corde</strong>: è lo standard in quasi tutti i generi. Il <strong>5 corde</strong> aggiunge una corda grave, usata nel metal o nel funk moderno, ma ha il manico più largo.</p>
<ul>
<li><strong>Tipo Precision (P):</strong> suono rotondo e pieno, semplice ed efficace.</li>
<li><strong>Tipo Jazz Bass (J):</strong> due pickup e manico più sottile, suono più definito.</li>
<li><strong>Scala corta:</strong> tasti più vicini, più comodo per mani piccole.</li>
</ul>
<p>Tra <strong>{p200} e {p400}</strong> ci sono bassi ottimi per iniziare. Il basso ha bisogno di un ampli per basso: i bassi possono danneggiare un ampli per chitarra.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Bassi sotto i {p400} venduti da più negozi (prezzi di oggi)")],
     "faqs": [("Quale basso comprare per iniziare?", "Un 4 corde tipo Precision, Jazz Bass o PJ tra {p200} e {p400}."),
              ("Posso collegare un basso a un ampli per chitarra?", "Non è consigliato: le frequenze basse possono danneggiare l'altoparlante. Serve un ampli per basso.")]},
    {"slug": "primo-amplificatore-chitarra", "title": "Quale amplificatore per chitarra comprare per iniziare",
     "desc": "Quanti watt, modeling o valvolare e quanto spendere per il tuo primo ampli, con i più venduti sotto i {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Per casa basta poco</h2>
<p>Per studiare a casa, un ampli da <strong>10 a 30 watt</strong> è più che sufficiente; conta che suoni bene a volume basso e abbia l'<strong>uscita cuffie</strong>.</p>
<ul>
<li><strong>Modeling (digitale):</strong> imita molti amplificatori e ha effetti integrati: il più pratico per iniziare (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Valvolare:</strong> il suono classico del rock e del blues, più caro e pensato per suonare forte.</li>
</ul>
<p>Tra <strong>{p100} e {p300}</strong> ci sono ampli da studio molto completi.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplificatori sotto i {p300} venduti da più negozi (prezzi di oggi)")],
     "faqs": [("Quale amplificatore per chitarra per casa?", "Uno da 10 a 30 watt con uscita cuffie; un modeling digitale è il più pratico per iniziare.")]},
    {"slug": "kit-chitarra", "title": "Kit chitarra: quando conviene",
     "desc": "Cosa contiene un kit chitarra, quando conviene rispetto all'acquisto separato e i kit più venduti con il prezzo di oggi.",
     "body": """<section class="hub-sec guia">
<h2>Cosa contiene un kit</h2>
<p>Un kit chitarra elettrica di solito contiene <strong>chitarra, piccolo ampli, borsa, cavo, tracolla, plettri e accordatore</strong>. <strong>Conviene</strong> se parti da zero; <strong>meno</strong> se hai già un ampli o cerchi una chitarra precisa. Guarda soprattutto la chitarra: è ciò che dura.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Kit sotto i {p400} venduti da più negozi (prezzi di oggi)")],
     "faqs": [("Conviene un kit chitarra per iniziare?", "Sì se parti da zero: costa meno che comprare ogni pezzo separatamente.")]},
]
