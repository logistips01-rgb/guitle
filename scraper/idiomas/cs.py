# Čeština (cs) · Česko · CZK. Vykání (běžné v českých e-shopech), "vy" s malým písmenem.
# Číslovky: "nouns", "guitars", "storesWord", "many" jsou v 2. pádě mn. č. ("1 234 kytar", "12 z 345 kytar",
# "Těmto filtrům odpovídá 0 kytar"). js "store"/"stores" = 1. pád ("1 obchod" / "3 obchody"; u 5+ by bylo "obchodů").
# "store"/"stores" na nejvyšší úrovni používá jen "desc" ("v {n} {stores}"), proto jsou v 6. pádě (obchodě/obchodech).
# Pozor: kód jazyka je "cs", ale adresář webu bude nejspíš "/cz/" (alertLegal se stejně přepisuje podle země).

MONEY_NOTE = ("Částka s mezerou (nezlomitelnou) jako oddělovačem tisíců a symbolem za částkou: '1 299 Kč' "
              "(haléře se v e-shopech prakticky neuvádějí; případně '1 299,50 Kč').")

KINDS_LANG = {"electrica": "elektricke-kytary", "acustica": "akusticke-kytary", "clasica": "klasicke-kytary",
              "pack": "kytarove-sety", "bajo": "baskytary", "ampli": "zesilovace", "pedal": "kytarove-efekty",
              "teclado": "klavesy", "micro": "mikrofony", "estuche": "pouzdra-obaly", "varios": "prislusenstvi"}

PACK_LANG = ("Kytarové sety", "Sety", "Hledat v setech: model, značka, se zesilovačem…", "setů",
             {"Eléctrica": "Elektrická kytara", "Acústica": "Akustická kytara"})

T_LANG = {
    "tagline": "kytary za nejlepší cenu", "homeLabel": "guitle, úvodní stránka",
    "homeTitle": "guitle · srovnávač cen kytar",
    "homeDesc": "guitle srovnává ceny kytar: elektrických, akustických i klasických v obchodech, které prodávají v Česku, "
                "s historií ceny každého modelu.",
    "h1": "Vaše kytara <span>za nejlepší cenu</span><small>Srovnávač cen kytar</small>",
    "searchPh": "Hledat: strat, les paul, yamaha, ibanez…", "searchBtn": "Hledat", "searchLabel": "Hledat kytaru",
    "guitars": "kytar", "storesWord": "obchodů", "catalog": "Katalog",
    "dealsH": "Největší cenové rozdíly mezi obchody", "dealsBadge": "−{p} % oproti nejdražšímu",
    "catsH": "Procházet podle kategorie", "soon": "již brzy", "storesH": "Obchody, které srovnáváme",
    "howH": "Jak to funguje",
    "steps": ["Každý den kontrolujeme cenu, dostupnost a fotku každé kytary v obchodech, které prodávají v Česku.",
              "Ukládáme historii cen, abyste viděli, jestli je cena opravdu dobrá, nebo bývá obvykle nižší.",
              "Pokud chcete, pošleme vám e-mail, jakmile cena klesne."],
    "affiliate": "Některé odkazy na obchody jsou affiliate odkazy: pokud nakoupíte, může guitle získat provizi – bez dalších nákladů pro vás.",
    "legal": "Právní informace", "privacy": "Ochrana soukromí", "cookies": "Cookies", "otherCountries": "guitle v dalších zemích:",
    "updated": "Data aktualizována {d}", "home": "Úvod",
    "kinds": {"electrica": ("Elektrické kytary", "Elektrické", "Hledat v elektrických kytarách: model, značka, barva…"),
              "acustica": ("Akustické kytary", "Akustické", "Hledat v akustických kytarách: model, značka, dřevo…"),
              "clasica": ("Klasické kytary", "Klasické", "Hledat v klasických kytarách: model, značka, flamenco…"),
              "bajo": ("Elektrické a akustické baskytary", "Baskytary", "Hledat v baskytarách: model, značka, pětistrunná…"),
              "ampli": ("Kytarové a baskytarové zesilovače", "Zesilovače", "Hledat v zesilovačích: model, značka, kombo, hlava…"),
              "pedal": ("Kytarové efekty", "Efekty", "Hledat v efektech: model, značka, typ efektu…"),
              "teclado": ("Klávesy a digitální piana", "Klávesy", "Hledat v klávesách: model, značka…"),
              "micro": ("Mikrofony", "Mikrofony", "Hledat v mikrofonech: model, značka, typ…"),
              "estuche": ("Pouzdra a obaly", "Pouzdra", "Hledat v pouzdrech a obalech: model, značka…"),
              "varios": ("Kytarové příslušenství", "Příslušenství", "Hledat v příslušenství: struny, trsátka, popruhy, kabely…")},
    # Co se počítá v každé kategorii (úvod a seznam) – 2. pád mn. č.
    "nouns": {"bajo": "baskytar", "ampli": "zesilovačů", "pedal": "efektů", "teclado": "kláves", "micro": "mikrofonů",
              "estuche": "pouzder", "varios": "položek"},
    "allWord": "produktů",
    "anyPrice": "Libovolná cena", "upTo": "Do {v}", "over": "Nad {v}", "brandLabel": "Značka", "priceLabel": "Cena",
    "showLabel": "Zobrazit", "showAll": "Vše", "showMulti": "Ve více obchodech", "showStock": "Skladem",
    "showLow": "Za nejnižší cenu", "showLh": "Jen pro leváky", "loading": "Načítáme katalog…", "sortLabel": "Řadit",
    "sorts": ["Nejvíc obchodů", "Nejnižší cena", "Nejvyšší cena", "Největší úspora mezi obchody", "Název"],
    "moreBtn": "Zobrazit další", "sections": "Sekce", "searchAria": "Hledat",
    "bestPrice": "nejlepší cena", "inStock": "skladem", "noStock": "není skladem", "goLong": "Do obchodu", "goShort": "Koupit",
    "store": "obchodě", "stores": "obchodech", "lh": "pro leváky", "storesH3": "Obchody", "historyH3": "Vývoj ceny",
    "amazon": "", "titleFrom": "{name}: cena od {price} {where}", "inN": "v {n} obchodech", "inS": "v obchodě {s}",
    "whereMany": "v obchodě {s} · v {n} obchodech", "whereDiff": ", rozdíl až {d}",
    "desc": "{name} od {price} v obchodě {s}. Porovnejte cenu v {n} {stores} ({list}) a podívejte se na vývoj ceny, ať víte, "
            "jestli je teď vhodná chvíle na nákup.",
    "alertTitle": "Hlídání ceny", "alertWait": "Okamžik…", "alertSaving": "Ukládáme vaši odpověď.",
    "alertGo": "Přejít na guitle", "alertBad": ["Neplatný odkaz", "Zkopírujte celý odkaz z e-mailu a zkuste to znovu."],
    "alertDone": ["Hlídání ceny potvrzeno!", "Napíšeme vám, jakmile cena klesne. Každý e-mail obsahuje odkaz pro odhlášení."],
    "alertGone": ["Hlídání ceny zrušeno", "K tomuto hlídání už vám nepřijdou žádné e-maily. Vaši adresu jsme vymazali z našeho seznamu."],
    "alertMissing": ["Hlídání ceny nenalezeno", "Možná už bylo potvrzeno nebo zrušeno, nebo uplynulo víc než 7 dní bez "
                                                 "potvrzení. Potřebujete pomoc? Napište nám na hola@guitle.com."],
    "js": {"loadErr": "Katalog se nepodařilo načíst.", "allBrands": "Všechny značky", "all": "Vše", "low": "Nejnižší",
           "save": "Ušetříte {v}", "lh": "pro leváky", "store": "obchod", "stores": "obchody",
           "empty": "Těmto filtrům odpovídá 0 {many}.", "more": "Zobrazit další (zbývá {n})",
           "meta": "{a} z {b} {many} · {m} k porovnání ve více obchodech · aktualizováno {d}", "best": "nejlepší cena",
           "inStock": "skladem", "noStock": "není skladem", "goLong": "Do obchodu", "goShort": "Koupit", "close": "Zavřít",
           "inAt": "v obchodě {s}", "saveMax": " · až o {v} levněji než v nejdražším", "atLow": "Za nejnižší zaznamenanou cenu",
           "lowTag": "Nejnižší cena: {v}", "storesH": "Obchody", "evolH": "Vývoj ceny",
           "histErr": "Historii cen se nepodařilo načíst.", "histSoon": "Historie cen se doplní během následujících dní.",
           "many": "kytar",
           "types": {"ST": "Typ ST", "T": "Typ T", "Semihueca": "Semiakustické", "Offset / Retro": "Offset / Retro", "Moderna / Metal": "Moderní / Metal",
                     "Otras": "Ostatní", "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12strunné",
                     "Tamaño reducido": "Zmenšené", "Clásica": "Klasické", "Flamenca": "Flamenco",
                     "Electroclásica": "Elektroklasické",
                     "4 cuerdas": "4strunné", "5 cuerdas": "5strunné", "6 cuerdas o más": "6strunné a více",
                     "Acústico": "Akustické baskytary", "Fretless": "Fretless", "Escala corta": "Krátká menzura", "Combo": "Komba",
                     "Cabezal": "Hlavy", "Pantalla": "Reproboxy", "Para bajo": "Pro baskytaru", "Para acústica": "Pro akustickou kytaru",
                     "De auriculares y portátil": "Sluchátkové a mini zesilovače", "Para eléctrica": "Pro elektrickou kytaru",
                     "Para clásica": "Pro klasickou kytaru", "Overdrive y distorsión": "Overdrive a distortion",
                     "Modulación": "Modulace", "Compresor": "Kompresor", "Wah y volumen": "Wah a volume",
                     "Octavador y pitch": "Oktávery a pitch", "Ecualizador": "Ekvalizér", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Syntezátory", "Afinador": "Ladička", "Multiefectos": "Multiefekty",
                     "Reverb": "Dozvuk", "Piano digital": "Digitální piana", "Teclado portátil": "Keyboardy",
                     "Piano de escenario": "Stage piana", "Controlador MIDI": "MIDI kontrolery", "Piano acústico": "Akustická piana",
                     "Dinámico": "Dynamické", "Condensador": "Kondenzátorové", "Inalámbrico": "Bezdrátové",
                     "Para instrumento": "Nástrojové", "De cinta": "Páskové", "Cuerdas": "Struny",
                     "Púas": "Trsátka", "Correas": "Popruhy", "Cables": "Kabely", "Afinadores": "Ladičky",
                     "Cejillas": "Kapodastry", "Soportes": "Stojany", "Pastillas": "Snímače", "Recambios": "Náhradní díly",
                     "Mantenimiento": "Údržba"},
           "wait": "Tento model sledujeme po dobu {n} {days}", "day": "dne", "days": "dní",
           "waitSub": "Hodnocení bude spolehlivější po několika týdnech historie.",
           "min": "Nejnižší zaznamenaná cena", "minSub": "Levněji jsme ho ještě neviděli.",
           "minBelow": " O {p} % pod průměrem za 30 dní.",
           "good": "Vhodná chvíle: o {p} % pod průměrnou cenou", "goodSub": "Průměr za posledních 30 dní: {avg}.",
           "bad": "Teď je o {p} % dražší než obvykle",
           "badSub": "Pokud nespěcháte, počkejte: průměr za 30 dní je {avg} a nejnižší cena {min}.",
           "normal": "Běžná cena", "normalSub": "Odpovídá průměru za 30 dní ({avg}). Nejnižší zaznamenaná: {min}.",
           "today": "cena dnes", "lowest": "nejnižší ({d})", "highest": "nejvyšší", "avg": "průměr za {n} dní",
           "since": "Sledujeme od {d}", "noHist": "Zatím bez historie cen.", "pvp": "Doporučená cena", "bestLine": "Nejlepší cena",
           "alertOpen": "Dejte mi vědět, až cena klesne", "emailPh": "jmeno@priklad.cz", "emailLabel": "Váš e-mail",
           "targetPh": "Max. cena (nepovinné)", "targetLabel": "Cílová cena v korunách", "alertBtn": "Hlídat cenu",
           "alertLegal": "Zdarma a bez registrace. Kliknutím na „Hlídat cenu“ souhlasíte se "
                         "<a href=\"/cz/legal.html#soukromi\">zásadami ochrany soukromí</a>: váš e-mail použijeme jen pro toto "
                         "hlídání a odhlásit se můžete jedním kliknutím.",
           "alertOk": "<b>Hotovo!</b> Za pár minut vám na {email} přijde e-mail pro potvrzení hlídání "
                      "(zkontrolujte i složku se spamem).",
           "alertErr": "Hlídání se nepodařilo uložit. Zkontrolujte e-mailovou adresu a zkuste to znovu."},
    "mail": {"tagline": "kytary za nejlepší cenu",
             "footer": "guitle každý den srovnává ceny hudebnin. Tento e-mail dostáváte, protože jste si na guitle.com "
                       "nastavili hlídání ceny. Správce údajů: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Ochrana soukromí", "confirmSubject": "Potvrďte hlídání ceny na guitle",
             "confirmTitle": "Potvrďte hlídání ceny", "asked": "Požádali jste nás o upozornění, až cena klesne{target}:",
             "below": " pod <b>{v}</b>", "confirmAsk": "Potvrďte prosím, že chcete upozornění dostávat na tuto adresu:",
             "confirmBtn": "Potvrdit hlídání",
             "notYou": "Pokud jste to nebyli vy, nic nedělejte: nepotvrzená hlídání se po 7 dnech automaticky smažou.",
             "dropSubject": "Cena klesla: {name} nyní za {price}", "dropTitle": "Cena klesla!", "nowAt": "v obchodě {s} · dříve {v}",
             "seeAll": "Zobrazit ceny ve všech obchodech",
             "check": "Ceny se mění každý den: před nákupem si je ověřte v obchodě. Už vás to nezajímá?",
             "stop": "Zrušit toto hlídání"},
}

# Dozorový úřad v Česku: Úřad pro ochranu osobních údajů (ÚOOÚ), uoou.gov.cz.
# Fráze pro případný legal_replace: "nebo u Úřadu pro ochranu osobních údajů (ÚOOÚ)".
LEGAL_LANG = ("Právní informace a ochrana soukromí", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Právní informace a ochrana soukromí</h1>
<p class="muted">Stav k 28. říjnu 2026. Toto je překlad; v případě pochybností platí <a href="/legal.html">španělské znění</a>.</p>

<h2 id="aviso">Právní informace</h2>
<p>Provozovatelem tohoto webu je <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Španělsko
(španělské daňové identifikační číslo NIF 17747339X), kontakt
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, web guitle.com. Činnost: srovnávání cen hudebních nástrojů a affiliate reklama.
Hosting: GitHub Pages (GitHub, Inc.).</p>

<h2 id="podminky">Podmínky užívání</h2>
<p>guitle je srovnávač cen a sám nic neprodává. Zobrazujeme ceny, které obchody zveřejňují na svých webech, a odkazujeme na ně, abyste
nakoupili přímo v obchodě. Za nákup, doručení, záruku a vrácení zboží odpovídá příslušný obchod.</p>
<ul>
<li><b>Ceny jsou orientační.</b> Ceny pravidelně kontrolujeme, mohou se ale kdykoli změnit. Platná je vždy cena, kterou obchod zobrazí při objednávce.</li>
<li><b>Bez záruky správnosti.</b> Dbáme na správnost produktů, cen a dostupnosti, chyby se ale stát mohou. Pokud nějakou najdete, napište nám.</li>
<li><b>Ochranné známky a obrázky.</b> Ochranné známky, názvy produktů a obrázky patří jejich vlastníkům a slouží jen k označení produktů.</li>
<li><b>Obsah guitle.</b> Design, logo, texty a soubory dat guitle patří provozovateli. Hromadné kopírování nebo komerční využití bez svolení není dovoleno.</li>
</ul>

<h2 id="affiliate">Affiliate odkazy</h2>
<p>Některé odkazy na obchody jsou affiliate odkazy: pokud po kliknutí nakoupíte, může obchod guitle vyplatit malou provizi. Vy zaplatíte stejnou
cenu. Provize neovlivňují pořadí: obchody jsou vždy seřazeny podle ceny, od nejlevnějšího.</p>

<h2 id="soukromi">Zásady ochrany soukromí</h2>
<p>guitle k používání webu nepožaduje žádné osobní údaje: žádná registrace, žádný newsletter, žádné analytické ani reklamní nástroje, které by vás
sledovaly. Návštěvy počítáme jen anonymně, a pokud si nastavíte hlídání ceny, uložíme pro ně vaši e-mailovou adresu.</p>
<ul>
<li><b>Hlídání ceny.</b> Pokud chcete dostat upozornění, až cena produktu klesne, uložíme vaši e-mailovou adresu, produkt, jeho cenu v daný den
a případně vaši cílovou cenu. Použijeme je jen k odeslání potvrzovacího e-mailu a upozornění k tomuto produktu, nikdy k marketingu,
a nikomu je nepředáváme. Právní základ: váš souhlas (čl. 6 odst. 1 písm. a) GDPR), který udělíte vytvořením hlídání a potvrzením e-mailu.
Údaje ukládáme v Google Cloud Firestore (Google Ireland Ltd., server v Madridu) a e-maily posíláme z naší schránky hola@guitle.com
(DonDominio, Španělsko). Nepotvrzená hlídání mažeme po 7 dnech; potvrzená uchováváme, dokud se neodhlásíte odkazem v kterémkoli e-mailu
(hlídání se okamžitě smaže), nebo dokud nás nepožádáte o výmaz.</li>
<li><b>Nastavení ve vašem prohlížeči.</b> Filtry a zvolené zobrazení se ukládají do místního úložiště vašeho prohlížeče (localStorage) a neodesílají se na žádný server.</li>
<li><b>Hosting.</b> Web běží na GitHub Pages (GitHub, Inc.). Jako každý webový server může GitHub z technických a bezpečnostních důvodů
zaznamenávat IP adresu každé návštěvy. GitHub je zapojen do rámce EU-US Data Privacy Framework.</li>
<li><b>Počítadlo návštěv.</b> Každá stránka zvýší anonymní počítadlo o 1: den, zobrazená stránka, web, ze kterého přicházíte (např. google.com),
co zadáte do vyhledávání v katalogu, a pokud přejdete do obchodu, jeho název. Žádné cookies, žádná IP adresa, nic, co by vás identifikovalo.
Počítadla jsou uložena v Google Cloud Firestore (Google Ireland Ltd.) na serveru v Evropské unii (Madrid).</li>
<li><b>Žádné další požadavky na třetí strany.</b> Písma, grafy i fotografie produktů se načítají z guitle.com.</li>
<li><b>Přechod do obchodu.</b> Kliknutím na odkaz do obchodu opouštíte guitle a platí zásady ochrany soukromí daného obchodu.</li>
</ul>
<p><b>Vaše práva.</b> Svá práva na přístup, opravu, výmaz, vznesení námitky, omezení zpracování a přenositelnost údajů můžete uplatnit e-mailem na
<a href="mailto:hola@guitle.com">hola@guitle.com</a>. Můžete také podat stížnost u dozorového úřadu pro ochranu osobních údajů, například u
Agencia Española de Protección de Datos nebo u Úřadu pro ochranu osobních údajů (ÚOOÚ). Správce údajů: provozovatel uvedený v právních informacích.</p>

<h2 id="cookies">Cookies</h2>
<p>guitle nepoužívá cookies, vlastní ani třetích stran – proto nevidíte žádnou cookie lištu. K zapamatování vašeho nastavení používáme jen
místní úložiště prohlížeče. Obchody, na které odkazujeme, mohou na svých webech používat vlastní cookies.</p>
""")
