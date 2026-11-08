"""Poradniki po polsku (guitle.com/pl/guias/)."""
MORE, FAQ, GUIDES_WORD = "Zobacz wszystkie", "Najczęstsze pytania", "Poradniki"
INDEX_TITLE = "Poradniki: jak kupić gitarę"
INDEX_DESC = "Poradniki, jak wybrać gitarę elektryczną, klasyczną lub akustyczną, gitarę basową i wzmacniacz, z prawdziwymi modelami i dzisiejszymi cenami."
COURSE_URL, COURSE_TITLE = "kurs/", "Darmowy kurs: twoja pierwsza gitara"
COURSE_DESC = "Pięć lekcji od zera: postawa, akordy, rytm, skale i dwie piosenki, z metronomem."

GUIDES = [
    {"slug": "pierwsza-gitara-elektryczna", "title": "Jak wybrać pierwszą gitarę elektryczną",
     "desc": "Jaki kształt, jakie przetworniki i ile wydać na pierwszą gitarę elektryczną, z najpopularniejszymi modelami do {p300} i ich dzisiejszymi cenami.",
     "body": """<section class="hub-sec guia">
<h2>Jaki kształt</h2>
<ul>
<li><strong>Typ Stratocaster (ST):</strong> najbardziej uniwersalna i wygodna, do popu, rocka, bluesa i funku. Jeśli masz wątpliwości, zacznij od niej.</li>
<li><strong>Typ Telecaster (T):</strong> prostsza, o jasnym i bezpośrednim brzmieniu, lubiana w rocku i country.</li>
<li><strong>Single cut (typ Les Paul):</strong> pełniejsze brzmienie i dłuższy sustain, idealna do rocka i bluesa. Zwykle cięższa.</li>
<li><strong>Superstrat:</strong> cienki gryf i mocne przetworniki, stworzona do hard rocka i metalu.</li>
</ul>
<h2>Przetworniki: single coil czy humbucker</h2>
<p><strong>Single coile</strong> brzmią jasno i perliście; <strong>humbuckery</strong> brzmią pełniej i mniej buczą na przesterze. Układ <strong>HSS</strong> łączy oba i jest najbardziej uniwersalny dla początkujących.</p>
<h2>Ile wydać</h2>
<p>W przedziale <strong>{p150}–{p300}</strong> znajdziesz gitary, które dobrze brzmią i posłużą latami: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone czy Harley Benton, między innymi. Gitara elektryczna potrzebuje <strong>wzmacniacza</strong> (albo małego wzmacniacza słuchawkowego); jeśli zaczynasz od zera, zestaw często wychodzi taniej.</p>
<p>Ten sam model może kosztować w różnych sklepach zauważalnie inaczej. guitle codziennie porównuje ceny w {shops} sklepach i zapisuje historię cen.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Gitary elektryczne do {p300}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)")],
     "faqs": [("Jaką gitarę elektryczną kupić na początek?", "Typ Stratocaster z przetwornikami HSS w przedziale {p150}–{p300}: Yamaha Pacifica, Squier i Ibanez GIO to częsty wybór na pierwszą gitarę."),
              ("Czy do gitary elektrycznej potrzebny jest wzmacniacz?", "Tak: bez wzmacniacza prawie jej nie słychać. Na początek wystarczy mały wzmacniacz do ćwiczeń albo wzmacniacz słuchawkowy."),
              ("Czy warto kupić zestaw gitarowy dla początkujących?", "Jeśli zaczynasz od zera, tak: gitara, wzmacniacz i akcesoria w zestawie kosztują mniej niż kupowane osobno.")]},
    {"slug": "gitara-klasyczna-czy-akustyczna", "title": "Gitara klasyczna czy akustyczna: którą wybrać",
     "desc": "Czym różni się gitara klasyczna od akustycznej, którą wybrać na początek, rozmiary dla dzieci i modele z dzisiejszymi cenami.",
     "body": """<section class="hub-sec guia">
<h2>Wszystko zależy od strun</h2>
<p>Gitara <strong>klasyczna</strong> ma struny <strong>nylonowe</strong>: miękkie dla palców, o ciepłym brzmieniu, z szerszym gryfem. Gitara <strong>akustyczna</strong> (westernowa) ma struny <strong>stalowe</strong>: brzmi jaśniej i głośniej, ale na początku bardziej daje się palcom we znaki.</p>
<ul>
<li><strong>Klasyczna:</strong> muzyka klasyczna, flamenco, bossa nova, a także dla dzieci i do nauki z nauczycielem.</li>
<li><strong>Akustyczna:</strong> pop, rock, folk i akompaniament do śpiewu.</li>
</ul>
<h2>Rozmiary</h2>
<p>Gitary klasyczne występują w rozmiarze <strong>4/4</strong> dla dorosłych, <strong>3/4</strong> dla dzieci w wieku mniej więcej 8–11 lat i <strong>1/2</strong> dla młodszych. Gitara <strong>elektroakustyczna</strong> ma wbudowany przedwzmacniacz, więc można ją podłączyć do wzmacniacza.</p>
<h2>Ile wydać</h2>
<p>Dobre gitary klasyczne kosztują od około <strong>{p100}–{p200}</strong>, akustyczne od <strong>{p150}–{p300}</strong>. Z litą płytą wierzchnią brzmią lepiej i z czasem jeszcze zyskują. guitle codziennie porównuje ceny w {shops} sklepach.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Gitary klasyczne do {p200}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)"),
               ("acustica", 300, 8, 3, True, "Gitary akustyczne do {p300}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)")],
     "faqs": [("Gitara klasyczna czy akustyczna na początek?", "Klasyczna jest wygodniejsza dzięki nylonowym strunom; akustyczna jest lepsza, jeśli chcesz grać pop, rock lub folk."),
              ("Jaki rozmiar gitary potrzebuje dziecko?", "W przybliżeniu 1/2 do 7–8 lat, 3/4 od 8 do 11 lat i 4/4 od 12 lat."),
              ("Czy na gitarę klasyczną można założyć struny stalowe?", "Nie: gitara klasyczna nie jest zbudowana na takie naciągi; może ucierpieć gryf albo mostek.")]},
    {"slug": "pierwsza-gitara-basowa", "title": "Jak wybrać pierwszą gitarę basową",
     "desc": "4 czy 5 strun, Precision czy Jazz Bass i ile wydać na pierwszy bas, z najpopularniejszymi modelami do {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 czy 5 strun</h2>
<p>Zacznij od basu <strong>4-strunowego</strong>: to standard niemal w każdym gatunku. <strong>5-strunowy</strong> ma dodatkową niską strunę, popularną w metalu i nowoczesnym funku, ale też szerszy gryf.</p>
<ul>
<li><strong>Typ Precision (P):</strong> okrągłe, mocne brzmienie, prosty i skuteczny.</li>
<li><strong>Typ Jazz Bass (J):</strong> dwa przetworniki i smuklejszy gryf, z bardziej zwartym brzmieniem.</li>
<li><strong>Short scale:</strong> krótsza menzura, wygodniejsza dla małych dłoni.</li>
</ul>
<p>W przedziale <strong>{p200}–{p400}</strong> są bardzo dobre basy na początek. Bas potrzebuje wzmacniacza basowego: niskie częstotliwości mogą uszkodzić wzmacniacz gitarowy.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Gitary basowe do {p400}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)")],
     "faqs": [("Jaką gitarę basową kupić na początek?", "4-strunowy bas typu Precision, Jazz Bass lub PJ w przedziale {p200}–{p400}."),
              ("Czy można podłączyć bas do wzmacniacza gitarowego?", "Lepiej nie: niskie częstotliwości mogą uszkodzić głośnik. Potrzebny jest wzmacniacz basowy.")]},
    {"slug": "pierwszy-wzmacniacz-gitarowy", "title": "Jaki wzmacniacz gitarowy kupić na początek",
     "desc": "Ile watów, modeling czy lampy i ile wydać na pierwszy wzmacniacz, z najpopularniejszymi modelami do {p300}.",
     "body": """<section class="hub-sec guia">
<h2>W domu wystarczy niewiele</h2>
<p>Do ćwiczeń w domu wzmacniacz o mocy <strong>10–30 watów</strong> w zupełności wystarczy; ważne, żeby dobrze brzmiał po cichu i miał <strong>wyjście słuchawkowe</strong>.</p>
<ul>
<li><strong>Modeling (cyfrowy):</strong> naśladuje wiele wzmacniaczy i ma wbudowane efekty: najwygodniejszy na początek (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Lampowy:</strong> klasyczne brzmienie rocka i bluesa, droższy i stworzony do głośnego grania.</li>
</ul>
<p>W przedziale <strong>{p100}–{p300}</strong> znajdziesz bardzo kompletne wzmacniacze do ćwiczeń.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Wzmacniacze do {p300}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)")],
     "faqs": [("Jaki wzmacniacz gitarowy do domu?", "Taki o mocy 10–30 watów z wyjściem słuchawkowym; cyfrowy wzmacniacz typu modeling jest najwygodniejszy na początek.")]},
    {"slug": "zestawy-gitarowe", "title": "Zestawy gitarowe: kiedy się opłacają",
     "desc": "Co zawiera zestaw gitarowy, kiedy wychodzi taniej niż zakup osobno i najpopularniejsze zestawy z dzisiejszymi cenami.",
     "body": """<section class="hub-sec guia">
<h2>Co jest w zestawie</h2>
<p>Zestaw z gitarą elektryczną zwykle zawiera <strong>gitarę, mały wzmacniacz, pokrowiec, kabel, pasek, kostki i tuner</strong>. <strong>Opłaca się</strong>, jeśli zaczynasz od zera; <strong>mniej</strong>, jeśli masz już wzmacniacz albo chcesz konkretną gitarę. Patrz przede wszystkim na gitarę: to ona zostanie z tobą na dłużej.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Zestawy do {p400}, które sprzedaje najwięcej sklepów (dzisiejsze ceny)")],
     "faqs": [("Czy zestaw gitarowy opłaca się początkującym?", "Tak, jeśli zaczynasz od zera: wychodzi taniej niż kupowanie wszystkiego osobno.")]},
]
