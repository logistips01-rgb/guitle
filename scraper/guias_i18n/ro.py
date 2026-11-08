"""Ghiduri în română (guitle.com/ro/guias/)."""
MORE, FAQ, GUIDES_WORD = "Vezi tot", "Întrebări frecvente", "Ghiduri"
INDEX_TITLE = "Ghiduri pentru cumpărarea unei chitare"
INDEX_DESC = "Ghiduri pentru a alege o chitară electrică, clasică sau acustică, o chitară bas și un amplificator, cu modele reale și prețurile de azi."
COURSE_URL, COURSE_TITLE = "curs/", "Curs gratuit: prima ta chitară"
COURSE_DESC = "Cinci lecții de la zero: poziție, acorduri, ritm, game și două cântece, cu metronom."

GUIDES = [
    {"slug": "prima-chitara-electrica", "title": "Cum să-ți alegi prima chitară electrică",
     "desc": "Ce formă, ce doze și cât să cheltui pe prima chitară electrică, cu cele mai vândute sub {p300} și prețul lor de azi.",
     "body": """<section class="hub-sec guia">
<h2>Ce formă</h2>
<ul>
<li><strong>Tip Stratocaster (ST):</strong> cea mai versatilă și mai comodă, pentru pop, rock, blues și funk. Dacă ai dubii, începe cu ea.</li>
<li><strong>Tip Telecaster (T):</strong> mai simplă, cu un sunet clar și direct, foarte iubită în rock și country.</li>
<li><strong>Single cut (tip Les Paul):</strong> sunet mai gros și cu mai mult sustain, ideală pentru rock și blues. De obicei e mai grea.</li>
<li><strong>Superstrat:</strong> gât subțire și doze puternice, făcută pentru hard rock și metal.</li>
</ul>
<h2>Doze: single coil sau humbucker</h2>
<p><strong>Dozele single coil</strong> sună clar și strălucitor; <strong>humbuckerele</strong> sună mai plin și bâzâie mai puțin cu distorsiune. O configurație <strong>HSS</strong> le combină pe amândouă și e cea mai versatilă pentru începători.</p>
<h2>Cât să cheltui</h2>
<p>Între <strong>{p150} și {p300}</strong> găsești chitare care sună bine și țin ani de zile: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone sau Harley Benton, printre altele. O chitară electrică are nevoie de un <strong>amplificator</strong> (sau de un mic amplificator de căști); dacă pornești de la zero, un pachet iese de obicei mai ieftin.</p>
<p>Același model poate avea diferențe de preț serioase de la un magazin la altul. guitle compară zilnic prețul în {shops} magazine și păstrează istoricul prețurilor.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Chitare electrice sub {p300} vândute de cele mai multe magazine (prețurile de azi)")],
     "faqs": [("Ce chitară electrică să cumpăr ca începător?", "Una tip Stratocaster cu doze HSS, între {p150} și {p300}: Yamaha Pacifica, Squier și Ibanez GIO sunt alegeri foarte populare pentru prima chitară."),
              ("Am nevoie de amplificator pentru o chitară electrică?", "Da: fără amplificator abia se aude. Pentru început ajunge un mic amplificator de studiu sau unul de căști."),
              ("Merită un pachet de chitară pentru începători?", "Dacă pornești de la zero, da: chitara, amplificatorul și accesoriile costă mai puțin împreună decât separat.")]},
    {"slug": "chitara-clasica-sau-acustica", "title": "Chitară clasică sau acustică: pe care s-o alegi",
     "desc": "Diferența dintre chitara clasică și cea acustică, pe care s-o alegi ca începător, mărimile pentru copii și modele cu prețul lor de azi.",
     "body": """<section class="hub-sec guia">
<h2>Totul ține de corzi</h2>
<p>O chitară <strong>clasică</strong> are corzi de <strong>nailon</strong>: blânde cu degetele, cu un sunet cald și un gât mai lat. O chitară <strong>acustică</strong> (folk) are corzi de <strong>oțel</strong>: sună mai strălucitor și mai tare, dar la început e mai dură pentru degete.</p>
<ul>
<li><strong>Clasică:</strong> muzică clasică, flamenco, bossa nova, și pentru copii sau lecții cu profesor.</li>
<li><strong>Acustică:</strong> pop, rock, folk și acompaniament pentru voce.</li>
</ul>
<h2>Mărimi</h2>
<p>Chitarele clasice există în mărimea <strong>4/4</strong> pentru adulți, <strong>3/4</strong> pentru copiii de aproximativ 8–11 ani și <strong>1/2</strong> pentru cei mai mici. O chitară <strong>electro-acustică</strong> are preamplificator, ca s-o poți conecta la un amplificator.</p>
<h2>Cât să cheltui</h2>
<p>Chitare clasice bune găsești de la aproximativ <strong>{p100}–{p200}</strong>, iar acustice de la <strong>{p150}–{p300}</strong>. Cele cu față din lemn masiv sună mai bine și se îmbunătățesc cu anii. guitle compară zilnic prețul în {shops} magazine.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Chitare clasice sub {p200} vândute de cele mai multe magazine (prețurile de azi)"),
               ("acustica", 300, 8, 3, True, "Chitare acustice sub {p300} vândute de cele mai multe magazine (prețurile de azi)")],
     "faqs": [("Chitară clasică sau acustică pentru începători?", "Cea clasică e mai comodă datorită corzilor de nailon; cea acustică e mai potrivită dacă vrei să cânți pop, rock sau folk."),
              ("Ce mărime de chitară îi trebuie unui copil?", "Orientativ, 1/2 până la 7–8 ani, 3/4 între 8 și 11 ani și 4/4 de la 12 ani în sus."),
              ("Pot pune corzi de oțel pe o chitară clasică?", "Nu: chitara clasică nu e construită pentru acea tensiune și se pot deteriora gâtul sau călușul.")]},
    {"slug": "prima-chitara-bas", "title": "Cum să-ți alegi prima chitară bas",
     "desc": "4 sau 5 corzi, Precision sau Jazz Bass și cât să cheltui pe primul bas, cu cele mai vândute sub {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 sau 5 corzi</h2>
<p>Începe cu un bas cu <strong>4 corzi</strong>: standardul în aproape orice stil. Unul cu <strong>5 corzi</strong> are o coardă gravă în plus, populară în metal și funk modern, dar gâtul e mai lat.</p>
<ul>
<li><strong>Tip Precision (P):</strong> sunet rotund și consistent, simplu și eficient.</li>
<li><strong>Tip Jazz Bass (J):</strong> două doze și un gât mai subțire, cu un sunet mai definit.</li>
<li><strong>Short scale:</strong> menzură mai scurtă, mai comodă pentru mâini mici.</li>
</ul>
<p>Între <strong>{p200} și {p400}</strong> există basuri foarte bune pentru început. Un bas are nevoie de un amplificator de bas: frecvențele joase pot strica un amplificator de chitară.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Chitare bas sub {p400} vândute de cele mai multe magazine (prețurile de azi)")],
     "faqs": [("Ce chitară bas să cumpăr ca începător?", "Un bas cu 4 corzi tip Precision, Jazz Bass sau PJ, între {p200} și {p400}."),
              ("Pot conecta un bas la un amplificator de chitară?", "Mai bine nu: frecvențele joase pot strica difuzorul. Ai nevoie de un amplificator de bas.")]},
    {"slug": "primul-amplificator-de-chitara", "title": "Ce amplificator de chitară să cumperi ca începător",
     "desc": "Câți wați, modeling sau lămpi și cât să cheltui pe primul amplificator, cu cele mai vândute sub {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Acasă îți trebuie puțin</h2>
<p>Pentru studiu acasă, un amplificator de <strong>10–30 de wați</strong> e mai mult decât suficient; important e să sune bine la volum mic și să aibă <strong>ieșire de căști</strong>.</p>
<ul>
<li><strong>Modeling (digital):</strong> imită multe amplificatoare și are efecte incluse: cel mai practic pentru început (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Pe lămpi:</strong> sunetul clasic de rock și blues, mai scump și făcut pentru volum mare.</li>
</ul>
<p>Între <strong>{p100} și {p300}</strong> găsești amplificatoare de studiu foarte complete.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplificatoare sub {p300} vândute de cele mai multe magazine (prețurile de azi)")],
     "faqs": [("Ce amplificator de chitară pentru acasă?", "Unul de 10–30 de wați cu ieșire de căști; un amplificator digital cu modeling e cel mai practic pentru început.")]},
    {"slug": "pachete-de-chitara", "title": "Pachete de chitară: când merită",
     "desc": "Ce conține un pachet de chitară, când iese mai ieftin decât să cumperi separat și cele mai vândute pachete cu prețul lor de azi.",
     "body": """<section class="hub-sec guia">
<h2>Ce conține un pachet</h2>
<p>Un pachet de chitară electrică include de obicei <strong>chitara, un amplificator mic, husă, cablu, curea, pene și acordor</strong>. <strong>Merită</strong> dacă pornești de la zero; <strong>mai puțin</strong> dacă ai deja amplificator sau vrei o anumită chitară. Uită-te mai ales la chitară: ea e cea care rămâne.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Pachete sub {p400} vândute de cele mai multe magazine (prețurile de azi)")],
     "faqs": [("Merită un pachet de chitară pentru începători?", "Da, dacă pornești de la zero: iese mai ieftin decât să cumperi totul separat.")]},
]
