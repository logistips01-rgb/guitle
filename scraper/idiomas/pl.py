# Polski (pl) · Polska · PLN. Zwracamy się do czytelnika na "ty" (jak większość polskich sklepów muzycznych online).
# Liczebniki: "nouns", "guitars", "storesWord", "many" są w dopełniaczu l.mn. ("1 234 gitar", "12 z 345 gitar",
# "Brak gitar…"). js "store"/"stores" to mianownik (karta: "1 sklep" / "3 sklepy"; przy 5+ byłoby "sklepów").
# Najwyższego poziomu "store"/"stores" używa tylko "desc" ("w {n} {stores}"), więc są w miejscowniku (sklepie/sklepach).

MONEY_NOTE = ("Kwota z twardą spacją jako separatorem tysięcy i symbolem po kwocie: '1 299 zł' (z groszami: '1 299,50 zł'; "
              "w kodzie: f\"{whole:,}\".replace(',', '\\u202f' lub '\\u00a0') + ('' if not cents else f',{cents:02d}') + '\\u00a0zł').")

KINDS_LANG = {"electrica": "gitary-elektryczne", "acustica": "gitary-akustyczne", "clasica": "gitary-klasyczne",
              "pack": "zestawy-gitarowe", "bajo": "gitary-basowe", "ampli": "wzmacniacze", "pedal": "efekty-gitarowe",
              "teclado": "keyboardy", "micro": "mikrofony", "estuche": "futeraly-pokrowce", "varios": "akcesoria"}

PACK_LANG = ("Zestawy gitarowe", "Zestawy", "Szukaj w zestawach: model, marka, ze wzmacniaczem…", "zestawów",
             {"Eléctrica": "Gitara elektryczna", "Acústica": "Gitara akustyczna"})

T_LANG = {
    "tagline": "gitary w najlepszej cenie", "homeLabel": "guitle, strona główna",
    "homeTitle": "guitle · porównywarka cen gitar",
    "homeDesc": "guitle porównuje ceny gitar: elektrycznych, akustycznych i klasycznych w sklepach, które sprzedają w Polsce, "
                "z historią cen każdego modelu.",
    "h1": "Twoja gitara <span>w najlepszej cenie</span><small>Porównywarka cen gitar</small>",
    "searchPh": "Szukaj: strat, les paul, yamaha, ibanez…", "searchBtn": "Szukaj", "searchLabel": "Szukaj gitary",
    "guitars": "gitar", "storesWord": "sklepów", "catalog": "Katalog",
    "dealsH": "Największe różnice cen między sklepami", "dealsBadge": "−{p}% względem najdroższego",
    "catsH": "Przeglądaj według kategorii", "soon": "wkrótce", "storesH": "Porównywane sklepy",
    "howH": "Jak to działa",
    "steps": ["Codziennie sprawdzamy cenę, dostępność i zdjęcie każdej gitary w sklepach, które sprzedają w Polsce.",
              "Zapisujemy historię cen – dzięki temu widzisz, czy cena jest naprawdę dobra, czy zwykle bywa niższa.",
              "Jeśli chcesz, wyślemy ci e-mail, gdy cena spadnie."],
    "affiliate": "Niektóre linki do sklepów to linki afiliacyjne: jeśli coś kupisz, guitle może otrzymać prowizję – bez dodatkowych kosztów dla ciebie.",
    "legal": "Nota prawna", "privacy": "Prywatność", "cookies": "Cookies", "otherCountries": "guitle w innych krajach:",
    "updated": "Dane zaktualizowane {d}", "home": "Strona główna",
    "kinds": {"electrica": ("Gitary elektryczne", "Elektryczne", "Szukaj wśród gitar elektrycznych: model, marka, kolor…"),
              "acustica": ("Gitary akustyczne", "Akustyczne", "Szukaj wśród gitar akustycznych: model, marka, drewno…"),
              "clasica": ("Gitary klasyczne", "Klasyczne", "Szukaj wśród gitar klasycznych: model, marka, flamenco…"),
              "bajo": ("Gitary basowe elektryczne i akustyczne", "Basy", "Szukaj wśród basów: model, marka, 5-strunowy…"),
              "ampli": ("Wzmacniacze gitarowe i basowe", "Wzmacniacze", "Szukaj wśród wzmacniaczy: model, marka, combo, głowa…"),
              "pedal": ("Efekty gitarowe", "Efekty", "Szukaj wśród efektów: model, marka, rodzaj efektu…"),
              "teclado": ("Keyboardy i pianina cyfrowe", "Keyboardy", "Szukaj wśród keyboardów: model, marka…"),
              "micro": ("Mikrofony", "Mikrofony", "Szukaj wśród mikrofonów: model, marka, typ…"),
              "estuche": ("Futerały i pokrowce", "Futerały", "Szukaj wśród futerałów i pokrowców: model, marka…"),
              "varios": ("Akcesoria gitarowe", "Akcesoria", "Szukaj w akcesoriach: struny, kostki, paski, kable…")},
    # Co liczymy w każdej kategorii (strona główna i lista) – dopełniacz l.mn.
    "nouns": {"bajo": "basów", "ampli": "wzmacniaczy", "pedal": "efektów", "teclado": "keyboardów", "micro": "mikrofonów",
              "estuche": "futerałów", "varios": "artykułów"},
    "allWord": "produktów",
    "anyPrice": "Dowolna cena", "upTo": "Do {v}", "over": "Powyżej {v}", "brandLabel": "Marka", "priceLabel": "Cena",
    "showLabel": "Pokaż", "showAll": "Wszystkie", "showMulti": "W kilku sklepach", "showStock": "Dostępne",
    "showLow": "W najniższej cenie", "showLh": "Tylko leworęczne", "loading": "Ładowanie katalogu…", "sortLabel": "Sortuj",
    "sorts": ["Najwięcej sklepów", "Najniższa cena", "Najwyższa cena", "Największa różnica między sklepami", "Nazwa"],
    "moreBtn": "Pokaż więcej", "sections": "Działy", "searchAria": "Szukaj",
    "bestPrice": "najlepsza cena", "inStock": "dostępny", "noStock": "niedostępny", "goLong": "Przejdź do sklepu", "goShort": "Sklep",
    "store": "sklepie", "stores": "sklepach", "lh": "dla leworęcznych", "storesH3": "Sklepy", "historyH3": "Historia cen",
    "amazon": "", "titleFrom": "{name}: cena od {price} {where}", "inN": "w {n} sklepach", "inS": "w sklepie {s}",
    "whereMany": "w sklepie {s} · w {n} sklepach", "whereDiff": ", różnica do {d}",
    "desc": "{name} od {price} w sklepie {s}. Porównaj cenę w {n} {stores} ({list}) i sprawdź historię cen, żeby wiedzieć, "
            "czy to dobry moment na zakup.",
    "alertTitle": "Alert cenowy", "alertWait": "Chwileczkę…", "alertSaving": "Zapisujemy twoją odpowiedź.",
    "alertGo": "Przejdź do guitle", "alertBad": ["Nieprawidłowy link", "Skopiuj cały link z e-maila i spróbuj ponownie."],
    "alertDone": ["Alert potwierdzony!", "Napiszemy do ciebie, gdy tylko cena spadnie. W każdym e-mailu znajdziesz link do wypisania się."],
    "alertGone": ["Alert usunięty", "Nie dostaniesz już e-maili z tym alertem. Usunęliśmy twój adres z naszej listy."],
    "alertMissing": ["Nie znaleziono alertu", "Możliwe, że był już potwierdzony lub usunięty albo minęło ponad 7 dni bez "
                                               "potwierdzenia. Potrzebujesz pomocy? Napisz do nas: hola@guitle.com."],
    "js": {"loadErr": "Nie udało się załadować katalogu.", "allBrands": "Wszystkie marki", "all": "Wszystkie", "low": "Najniższa",
           "save": "Oszczędzasz {v}", "lh": "dla leworęcznych", "store": "sklep", "stores": "sklepy",
           "empty": "Brak {many} spełniających te kryteria.", "more": "Pokaż więcej (jeszcze {n})",
           "meta": "{a} z {b} {many} · {m} do porównania w kilku sklepach · aktualizacja {d}", "best": "najlepsza cena",
           "inStock": "dostępny", "noStock": "niedostępny", "goLong": "Przejdź do sklepu", "goShort": "Sklep", "close": "Zamknij",
           "inAt": "w sklepie {s}", "saveMax": " · do {v} taniej niż w najdroższym", "atLow": "W najniższej odnotowanej cenie",
           "lowTag": "Najniższa cena: {v}", "storesH": "Sklepy", "evolH": "Historia cen",
           "histErr": "Nie udało się załadować historii cen.", "histSoon": "Historia cen uzupełni się w najbliższych dniach.",
           "many": "gitar",
           "types": {"ST": "Typ ST", "T": "Typ T", "Semihueca": "Półpudła", "Offset / Retro": "Offset / Retro", "Moderna / Metal": "Nowoczesne / Metal",
                     "Otras": "Inne", "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12-strunowe",
                     "Tamaño reducido": "Mniejszy rozmiar", "Clásica": "Klasyczne", "Flamenca": "Flamenco",
                     "Electroclásica": "Elektroklasyczne",
                     "4 cuerdas": "4-strunowe", "5 cuerdas": "5-strunowe", "6 cuerdas o más": "6-strunowe i więcej",
                     "Acústico": "Basy akustyczne", "Fretless": "Fretless", "Escala corta": "Krótka menzura", "Combo": "Combo",
                     "Cabezal": "Głowy", "Pantalla": "Kolumny", "Para bajo": "Do basu", "Para acústica": "Do gitary akustycznej",
                     "De auriculares y portátil": "Słuchawkowe i mini", "Para eléctrica": "Do gitary elektrycznej",
                     "Para clásica": "Do gitary klasycznej", "Overdrive y distorsión": "Overdrive i distortion",
                     "Modulación": "Modulacja", "Compresor": "Kompresor", "Wah y volumen": "Wah i volume",
                     "Octavador y pitch": "Oktawer i pitch", "Ecualizador": "Korektor (EQ)", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Syntezatory", "Afinador": "Tuner", "Multiefectos": "Multiefekty",
                     "Reverb": "Pogłos", "Piano digital": "Pianina cyfrowe", "Teclado portátil": "Keyboardy",
                     "Piano de escenario": "Pianina estradowe", "Controlador MIDI": "Kontrolery MIDI", "Piano acústico": "Pianina akustyczne",
                     "Dinámico": "Dynamiczne", "Condensador": "Pojemnościowe", "Inalámbrico": "Bezprzewodowe",
                     "Para instrumento": "Instrumentalne", "De cinta": "Wstęgowe", "Cuerdas": "Struny",
                     "Púas": "Kostki", "Correas": "Paski", "Cables": "Kable", "Afinadores": "Tunery",
                     "Cejillas": "Kapodastry", "Soportes": "Statywy", "Pastillas": "Przetworniki", "Recambios": "Części zamienne",
                     "Mantenimiento": "Pielęgnacja"},
           "wait": "Śledzimy ten model od {n} {days}", "day": "dnia", "days": "dni",
           "waitSub": "Ocena będzie pewniejsza po kilku tygodniach historii cen.",
           "min": "Najniższa odnotowana cena", "minSub": "Nigdy nie widzieliśmy jej taniej.",
           "minBelow": " {p}% poniżej średniej z 30 dni.",
           "good": "Dobry moment: {p}% poniżej średniej ceny", "goodSub": "Średnia z ostatnich 30 dni: {avg}.",
           "bad": "Teraz jest o {p}% drożej niż zwykle",
           "badSub": "Jeśli ci się nie spieszy, poczekaj: średnia z 30 dni to {avg}, a najniższa cena – {min}.",
           "normal": "Normalna cena", "normalSub": "Zgodna ze średnią z 30 dni ({avg}). Najniższa odnotowana: {min}.",
           "today": "cena dziś", "lowest": "najniższa ({d})", "highest": "najwyższa", "avg": "średnia z {n} dni",
           "since": "Śledzimy od {d}", "noHist": "Brak jeszcze historii cen.", "pvp": "Cena katalogowa", "bestLine": "Najlepsza cena",
           "alertOpen": "Daj mi znać, gdy cena spadnie", "emailPh": "ty@przyklad.pl", "emailLabel": "Twój e-mail",
           "targetPh": "Maks. cena (opcjonalnie)", "targetLabel": "Docelowa cena w złotych", "alertBtn": "Powiadom mnie",
           "alertLegal": "Za darmo i bez rejestracji. Klikając „Powiadom mnie”, akceptujesz "
                         "<a href=\"/pl/legal.html#prywatnosc\">politykę prywatności</a>: twój e-mail wykorzystamy tylko do tego "
                         "alertu, a wypiszesz się jednym kliknięciem.",
           "alertOk": "<b>Gotowe!</b> Za kilka minut dostaniesz e-mail na adres {email}, żeby potwierdzić alert "
                      "(zajrzyj też do folderu spam).",
           "alertErr": "Nie udało się zapisać alertu. Sprawdź adres e-mail i spróbuj ponownie."},
    "mail": {"tagline": "gitary w najlepszej cenie",
             "footer": "guitle codziennie porównuje ceny sklepów muzycznych. Dostajesz tę wiadomość, bo na guitle.com ustawiono "
                       "alert cenowy dla tego adresu. Administrator danych: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Prywatność", "confirmSubject": "Potwierdź swój alert cenowy w guitle",
             "confirmTitle": "Potwierdź alert cenowy", "asked": "Chcesz dostać powiadomienie, gdy cena spadnie{target}:",
             "below": " poniżej <b>{v}</b>", "confirmAsk": "Potwierdź, że chcesz otrzymywać alert na ten adres:",
             "confirmBtn": "Potwierdź alert",
             "notYou": "Jeśli to nie ty, nic nie rób: niepotwierdzone alerty są automatycznie usuwane po 7 dniach.",
             "dropSubject": "Cena spadła: {name} teraz {price}", "dropTitle": "Cena spadła!", "nowAt": "w sklepie {s} · wcześniej {v}",
             "seeAll": "Zobacz ceny we wszystkich sklepach",
             "check": "Ceny zmieniają się codziennie: przed zakupem sprawdź cenę w sklepie. Już cię nie interesuje?",
             "stop": "Wyłącz ten alert"},
}

# Organ nadzorczy w Polsce: Prezes Urzędu Ochrony Danych Osobowych (UODO), uodo.gov.pl.
# Fraza do ewentualnego legal_replace: "lub do Prezesa Urzędu Ochrony Danych Osobowych (UODO)".
LEGAL_LANG = ("Nota prawna i prywatność", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Nota prawna i prywatność</h1>
<p class="muted">Stan na: 28 października 2026 r. To jest tłumaczenie; w razie wątpliwości rozstrzyga <a href="/legal.html">wersja hiszpańska</a>.</p>

<h2 id="aviso">Nota prawna</h2>
<p>Operatorem tej strony jest <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Hiszpania
(hiszpański numer podatkowy NIF 17747339X), kontakt
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, strona guitle.com. Działalność: porównywanie cen instrumentów muzycznych i reklama afiliacyjna.
Hosting: GitHub Pages (GitHub, Inc.).</p>

<h2 id="warunki">Warunki korzystania</h2>
<p>guitle to porównywarka cen i sama niczego nie sprzedaje. Pokazujemy ceny, które sklepy publikują na swoich stronach, i kierujemy do nich –
kupujesz bezpośrednio w sklepie. Za zakup, wysyłkę, gwarancję i zwroty odpowiada dany sklep.</p>
<ul>
<li><b>Ceny orientacyjne.</b> Regularnie sprawdzamy ceny, ale mogą się one zmienić w każdej chwili. Wiążąca jest zawsze cena, którą sklep pokazuje przy składaniu zamówienia.</li>
<li><b>Brak gwarancji poprawności.</b> Dbamy o to, by produkty, ceny i dostępność były poprawne, ale błędy mogą się zdarzyć. Jeśli jakiś zauważysz, napisz do nas.</li>
<li><b>Znaki towarowe i zdjęcia.</b> Znaki towarowe, nazwy produktów i zdjęcia należą do ich właścicieli i służą wyłącznie do oznaczenia produktów.</li>
<li><b>Treści guitle.</b> Projekt, logo, teksty i zestawienia danych guitle należą do operatora. Masowe kopiowanie lub wykorzystanie komercyjne bez zgody jest zabronione.</li>
</ul>

<h2 id="afiliacja">Linki afiliacyjne</h2>
<p>Niektóre linki do sklepów to linki afiliacyjne: jeśli kupisz coś po kliknięciu, sklep może zapłacić guitle niewielką prowizję. Dla ciebie cena się
nie zmienia. Prowizje nie wpływają na kolejność: sklepy są zawsze sortowane według ceny, od najtańszego.</p>

<h2 id="prywatnosc">Polityka prywatności</h2>
<p>guitle nie wymaga podawania danych osobowych, by korzystać ze strony: bez rejestracji, bez newslettera, bez narzędzi analitycznych czy reklamowych,
które cię śledzą. Wizyty liczymy wyłącznie anonimowo, a jeśli ustawisz alert cenowy, przechowujemy twój adres e-mail na potrzeby tego alertu.</p>
<ul>
<li><b>Alerty cenowe.</b> Jeśli chcesz dostać powiadomienie, gdy cena produktu spadnie, zapisujemy twój adres e-mail, produkt, jego cenę z tego dnia
oraz – jeśli ją podasz – twoją cenę docelową. Wykorzystujemy je wyłącznie do wysłania e-maila z potwierdzeniem i alertów dotyczących tego produktu,
nigdy do celów marketingowych, i nikomu ich nie przekazujemy. Podstawa prawna: twoja zgoda (art. 6 ust. 1 lit. a RODO), wyrażona przy ustawieniu
alertu i potwierdzeniu adresu e-mail. Dane są przechowywane w Google Cloud Firestore (Google Ireland Ltd., serwer w Madrycie), a e-maile wysyłamy
z naszej skrzynki hola@guitle.com (DonDominio, Hiszpania). Niepotwierdzone alerty usuwamy po 7 dniach; potwierdzone przechowujemy do czasu, aż
wypiszesz się za pomocą linku w każdym e-mailu (alert zostaje wtedy od razu usunięty) albo poprosisz nas o usunięcie.</li>
<li><b>Ustawienia w twojej przeglądarce.</b> Filtry i wybrany widok są zapisywane w pamięci lokalnej twojej przeglądarki (localStorage) i nie są przesyłane na żaden serwer.</li>
<li><b>Hosting.</b> Strona jest udostępniana przez GitHub Pages (GitHub, Inc.). Jak każdy serwer WWW, GitHub może rejestrować adres IP każdej wizyty
ze względów technicznych i bezpieczeństwa. GitHub uczestniczy w programie EU-US Data Privacy Framework.</li>
<li><b>Licznik odwiedzin.</b> Każda strona zwiększa anonimowy licznik o 1: dzień, odwiedzona strona, witryna, z której przychodzisz (np. google.com),
to, co wpisujesz w wyszukiwarkę katalogu, oraz – jeśli przejdziesz do sklepu – jego nazwa. Bez cookies, bez adresu IP, bez niczego, co by cię
identyfikowało. Liczniki są przechowywane w Google Cloud Firestore (Google Ireland Ltd.) na serwerze w Unii Europejskiej (Madryt).</li>
<li><b>Brak innych zapytań do podmiotów trzecich.</b> Czcionki, wykresy i zdjęcia produktów są serwowane z guitle.com.</li>
<li><b>Przejście do sklepu.</b> Gdy klikniesz link do sklepu, opuszczasz guitle i obowiązuje polityka prywatności tego sklepu.</li>
</ul>
<p><b>Twoje prawa.</b> Możesz skorzystać z prawa dostępu do danych, ich sprostowania, usunięcia, sprzeciwu, ograniczenia przetwarzania i przenoszenia,
pisząc na adres <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Możesz też złożyć skargę do organu nadzorczego ds. ochrony danych, np. do
Agencia Española de Protección de Datos lub do Prezesa Urzędu Ochrony Danych Osobowych (UODO). Administrator danych: operator wskazany w nocie prawnej.</p>

<h2 id="cookies">Cookies</h2>
<p>guitle nie używa plików cookie – ani własnych, ani podmiotów trzecich – dlatego nie widzisz banera cookies. Korzystamy tylko z pamięci lokalnej
przeglądarki, żeby zapamiętać twoje ustawienia. Sklepy, do których prowadzą linki, mogą używać własnych plików cookie na swoich stronach.</p>
""")
