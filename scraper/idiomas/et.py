# Eesti (et) — guitle.com texts. Country code in URLs: "ee" (the alertLegal link is rewritten by strings()).
# Informal "sina" form, like the German "du".
# Plurals: after a number Estonian uses the partitive singular ("5 kitarri", "12 poodi"), which also fits
# "ühtegi {many}" in "empty", so the nouns below are in partitive singular.

# Anchor of the privacy section in LEGAL_LANG (add to intl._anchor: "et": "privaatsus").
PRIVACY_ANCHOR = "privaatsus"

MONEY_NOTE = ("Estonian format: amount, no-break space, euro sign after it: 1299 € (four digits usually without a "
              "thousands separator; from five digits a space: 12 999 €), decimals with a comma: 1299,90 €. "
              "intl.money() falls into the default branch (narrow no-break space as thousands separator), which is "
              "also acceptable; for exactly \"1299 €\" add a branch for lang 'et' with no separator below 10 000.")

KINDS_LANG = {"electrica": "elektrikitarrid", "acustica": "akustilised-kitarrid", "clasica": "klassikalised-kitarrid",
              "pack": "kitarrikomplektid", "bajo": "basskitarrid", "ampli": "voimendid", "pedal": "efektipedaalid",
              "teclado": "klahvpillid", "micro": "mikrofonid", "estuche": "kohvrid-kotid", "varios": "tarvikud"}

PACK_LANG = ("Kitarrikomplektid", "Komplektid", "Otsi komplektide hulgast: mudel, bränd, koos võimendiga…", "komplekti",
             {"Eléctrica": "Elektrikitarr", "Acústica": "Akustiline kitarr"})

T_LANG = {
    "tagline": "kitarrid parima hinnaga", "homeLabel": "guitle, avaleht",
    "homeTitle": "guitle · kitarride hinnavõrdlus",
    "homeDesc": "guitle võrdleb kitarrihindu: elektrikitarrid, akustilised ja klassikalised kitarrid Eestisse tarnivates "
                "poodides koos iga mudeli hinnaajalooga.",
    "h1": "Sinu kitarr <span>parima hinnaga</span><small>Kitarride hinnavõrdlus</small>",
    "searchPh": "Otsi: Strat, Les Paul, Yamaha, Ibanez…", "searchBtn": "Otsi", "searchLabel": "Otsi kitarri",
    "guitars": "kitarri", "storesWord": "poodi", "catalog": "Kataloog",
    "dealsH": "Suurimad hinnavahed poodide vahel", "dealsBadge": "−{p}% kalleimast",
    "catsH": "Sirvi kategooriate kaupa", "soon": "varsti", "storesH": "Võrreldavad poed",
    "howH": "Kuidas see töötab",
    "steps": ["Iga päev kontrollime iga kitarri hinda, saadavust ja fotot poodides, mis tarnivad Eestisse.",
              "Salvestame hinnaajaloo, et näeksid, kas hind on tõesti hea või on see tavaliselt madalam.",
              "Soovi korral saadame sulle e-kirja, kui hind langeb."],
    "affiliate": "Mõned poelingid on partnerlingid: kui ostad, võib guitle saada vahendustasu – sinu jaoks ilma lisakuluta.",
    "legal": "Õiguslik teave", "privacy": "Privaatsus", "cookies": "Küpsised", "otherCountries": "guitle teistes riikides:",
    "updated": "Andmed uuendatud {d}", "home": "Avaleht",
    "kinds": {"electrica": ("Elektrikitarrid", "Elektrikitarrid", "Otsi elektrikitarride hulgast: mudel, bränd, värv…"),
              "acustica": ("Akustilised kitarrid", "Akustilised", "Otsi akustiliste kitarride hulgast: mudel, bränd, puit…"),
              "clasica": ("Klassikalised kitarrid", "Klassikalised", "Otsi klassikaliste kitarride hulgast: mudel, bränd, flamenko…"),
              "bajo": ("Elektri- ja akustilised basskitarrid", "Bassid", "Otsi basside hulgast: mudel, bränd, 5-keelne…"),
              "ampli": ("Kitarri- ja bassivõimendid", "Võimendid", "Otsi võimendite hulgast: mudel, bränd, kombo, võimendipea…"),
              "pedal": ("Efektipedaalid", "Efektid", "Otsi efektipedaalide hulgast: mudel, bränd, efekt…"),
              "teclado": ("Klahvpillid ja digiklaverid", "Klahvpillid", "Otsi klahvpillide hulgast: mudel, bränd…"),
              "micro": ("Mikrofonid", "Mikrofonid", "Otsi mikrofonide hulgast: mudel, bränd, tüüp…"),
              "estuche": ("Kohvrid ja kotid", "Kohvrid", "Otsi kohvrite ja kottide hulgast: mudel, bränd…"),
              "varios": ("Kitarritarvikud", "Tarvikud", "Otsi tarvikute hulgast: keeled, mediaatorid, rihmad, kaablid…")},
    # Lo que se cuenta en cada categoría de equipo (portada y lista) y, si no son solo guitarras, el total.
    "nouns": {"bajo": "bassi", "ampli": "võimendit", "pedal": "pedaali", "teclado": "klahvpilli", "micro": "mikrofoni",
              "estuche": "kohvrit", "varios": "tarvikut"},
    "allWord": "toodet",
    "anyPrice": "Kõik hinnad", "upTo": "Kuni {v}", "over": "Üle {v}", "brandLabel": "Bränd", "priceLabel": "Hind",
    "showLabel": "Näita", "showAll": "Kõik", "showMulti": "Mitmes poes", "showStock": "Laos",
    "showLow": "Madalaima hinnaga", "showLh": "Ainult vasakukäelised", "loading": "Kataloogi laaditakse…", "sortLabel": "Järjesta",
    "sorts": ["Kõige rohkem poode", "Madalaim hind", "Kõrgeim hind", "Suurim hinnavahe poodide vahel", "Nimi"],
    "moreBtn": "Näita rohkem", "sections": "Jaotised", "searchAria": "Otsi",
    "bestPrice": "parim hind", "inStock": "laos", "noStock": "pole laos", "goLong": "Mine poodi", "goShort": "Poodi",
    "store": "poes", "stores": "poes", "lh": "vasakukäeline", "storesH3": "Poed", "historyH3": "Hinnaajalugu",
    "amazon": "", "titleFrom": "{name}: hind alates {price} {where}", "inN": "{n} poes", "inS": "poes {s}",
    "whereMany": "poes {s} · võrreldud {n} poes", "whereDiff": ", hinnavahe kuni {d}",
    "desc": "{name} alates {price} poes {s}. Võrdle selle hinda {n} {stores} ({list}) ja vaata hinnaajalugu, et teada, "
            "kas praegu on hea aeg osta.",
    "alertTitle": "Hinnateavitus", "alertWait": "Hetk…", "alertSaving": "Salvestame sinu vastust.",
    "alertGo": "Ava guitle", "alertBad": ["Vigane link", "Kopeeri e-kirjast terve link ja proovi uuesti."],
    "alertDone": ["Teavitus kinnitatud!", "Saadame sulle e-kirja kohe, kui hind langeb. Igas e-kirjas on link teavitusest loobumiseks."],
    "alertGone": ["Teavitus kustutatud", "Selle teavituse kohta sa enam e-kirju ei saa. Kustutasime sinu aadressi oma nimekirjast."],
    "alertMissing": ["Teavitust ei leitud", "Võib-olla on see juba kinnitatud või kustutatud või möödus kinnitamata rohkem kui "
                                            "7 päeva. Vajad abi? Kirjuta meile hola@guitle.com."],
    "js": {"loadErr": "Kataloogi ei õnnestunud laadida.", "allBrands": "Kõik brändid", "all": "Kõik", "low": "Madalaim",
           "save": "Säästa {v}", "lh": "vasakukäeline", "store": "pood", "stores": "poodi",
           "empty": "Nende filtritega ei leitud ühtegi {many}.", "more": "Näita rohkem (veel {n})",
           "meta": "{a}/{b} {many} · {m} mitme poe hinnaga · uuendatud {d}", "best": "parim hind",
           "inStock": "laos", "noStock": "pole laos", "goLong": "Mine poodi", "goShort": "Poodi", "close": "Sulge",
           "inAt": "poes {s}", "saveMax": " · kuni {v} odavam kui kalleimas poes", "atLow": "Madalaima registreeritud hinnaga",
           "lowTag": "Madalaim registreeritud: {v}", "storesH": "Poed", "evolH": "Hinnaajalugu",
           "histErr": "Hinnaajalugu ei õnnestunud laadida.", "histSoon": "Hinnaajalugu täitub järgmiste päevade jooksul.",
           "many": "kitarri",
           "types": {"ST": "ST-tüüpi", "T": "T-tüüpi", "Semihueca": "Poolakustilised", "Offset / Retro": "Offset / retro",
                     "Moderna / Metal": "Moodsad / metal", "Otras": "Muud", "Auditorio / Concierto": "Auditorium / kontsert",
                     "12 cuerdas": "12-keelsed", "Tamaño reducido": "Väiksema korpusega", "Clásica": "Klassikalised",
                     "Flamenca": "Flamenko", "Electroclásica": "Elektroklassikalised",
                     "4 cuerdas": "4-keelsed", "5 cuerdas": "5-keelsed", "6 cuerdas o más": "6 ja enama keelega",
                     "Acústico": "Akustilised bassid", "Fretless": "Fretless", "Escala corta": "Lühikese mensuuriga",
                     "Combo": "Kombod", "Cabezal": "Võimendipead", "Pantalla": "Kõlarikapid", "Para bajo": "Bassile",
                     "Para acústica": "Akustilisele kitarrile",
                     "De auriculares y portátil": "Kõrvaklapi- ja minivõimendid", "Para eléctrica": "Elektrikitarrile",
                     "Para clásica": "Klassikalisele kitarrile", "Overdrive y distorsión": "Overdrive ja distortion",
                     "Modulación": "Modulatsioon", "Compresor": "Kompressor", "Wah y volumen": "Wah ja helitugevus",
                     "Octavador y pitch": "Oktaaver ja pitch", "Ecualizador": "Ekvalaiser", "Puerta de ruido": "Noise gate",
                     "Sintetizador": "Süntesaatorid", "Afinador": "Häälestaja", "Multiefectos": "Multiefektid",
                     "Reverb": "Reverb", "Piano digital": "Digiklaverid", "Teclado portátil": "Kaasaskantavad klahvpillid",
                     "Piano de escenario": "Lavaklaverid", "Controlador MIDI": "MIDI-kontrollerid",
                     "Piano acústico": "Akustilised klaverid",
                     "Dinámico": "Dünaamilised", "Condensador": "Kondensaatormikrofonid", "Inalámbrico": "Juhtmevabad",
                     "Para instrumento": "Pillimikrofonid", "De cinta": "Lintmikrofonid", "Cuerdas": "Keeled",
                     "Púas": "Mediaatorid", "Correas": "Rihmad", "Cables": "Kaablid", "Afinadores": "Häälestajad",
                     "Cejillas": "Kapod", "Soportes": "Pillialused", "Pastillas": "Helipead", "Recambios": "Varuosad",
                     "Mantenimiento": "Hooldus"},
           # Only shown while n < 7: "1 päev", "2–6 päeva".
           "wait": "Jälgime seda mudelit juba {n} {days}", "day": "päev", "days": "päeva",
           "waitSub": "Hinnang muutub usaldusväärsemaks, kui hinnaajalugu on kogunenud paar nädalat.",
           "min": "Madalaim registreeritud hind", "minSub": "Nii odavalt pole me seda veel näinud.",
           "minBelow": " {p}% alla 30 päeva keskmise.",
           "good": "Hea aeg osta: {p}% alla keskmise hinna", "goodSub": "30 päeva keskmine: {avg}.",
           "bad": "Praegu {p}% kallim kui tavaliselt",
           "badSub": "Kui sul pole kiiret, oota: 30 päeva keskmine on {avg} ja madalaim {min}.",
           "normal": "Tavaline hind", "normalSub": "30 päeva keskmise piires ({avg}). Madalaim registreeritud: {min}.",
           "today": "hind täna", "lowest": "madalaim ({d})", "highest": "kõrgeim", "avg": "{n} päeva keskmine",
           "since": "Jälgitud alates {d}", "noHist": "Hinnaajalugu veel pole.", "pvp": "Soovituslik hind", "bestLine": "Parim hind",
           "alertOpen": "Anna teada, kui hind langeb", "emailPh": "nimi@domeen.ee", "emailLabel": "Sinu e-post",
           "targetPh": "Max hind (valikuline)", "targetLabel": "Sihthind eurodes", "alertBtn": "Teavita mind",
           "alertLegal": "Tasuta ja ilma registreerimiseta. Klõpsates „Teavita mind“ nõustud meie "
                         "<a href=\"/ee/legal.html#privaatsus\">privaatsuspoliitikaga</a>: kasutame sinu e-posti ainult selle "
                         "teavituse jaoks ja sellest saab loobuda ühe klõpsuga.",
           "alertOk": "<b>Valmis!</b> Mõne minuti pärast saad aadressile {email} e-kirja teavituse kinnitamiseks "
                      "(vaata ka rämpsposti kausta).",
           "alertErr": "Teavitust ei õnnestunud salvestada. Kontrolli e-posti aadressi ja proovi uuesti."},
    "mail": {"tagline": "kitarrid parima hinnaga",
             "footer": "guitle võrdleb iga päev muusikapoodide hindu. Said selle e-kirja, sest tellisid guitle.com-is "
                       "hinnateavituse. Vastutav töötleja: Manuel Lorente Gálvez, hola@guitle.com.",
             "privacy": "Privaatsus", "confirmSubject": "Kinnita oma guitle'i hinnateavitus",
             "confirmTitle": "Kinnita oma hinnateavitus", "asked": "Palusid meil teada anda, kui hind langeb{target}:",
             "below": " alla <b>{v}</b>", "confirmAsk": "Palun kinnita, et soovid saada teavitust sellele aadressile:",
             "confirmBtn": "Kinnita teavitus",
             "notYou": "Kui see polnud sina, ära tee midagi: kinnitamata teavitused kustutatakse 7 päeva pärast automaatselt.",
             "dropSubject": "Hind langes: {name} nüüd {price}", "dropTitle": "Hind on langenud!", "nowAt": "poes {s} · varem {v}",
             "seeAll": "Vaata hindu kõigis poodides",
             "check": "Hinnad muutuvad iga päev: kontrolli enne ostu hinda poe lehel. Pole enam huvitatud?",
             "stop": "Loobu sellest teavitusest"},
}

# Supervisory authority: the text says "your country's data protection authority";
# in Estonia that is the Andmekaitse Inspektsioon (AKI) — usable via SITES["ee"]["legal_replace"] if wanted:
# ("oma riigi andmekaitse järelevalveasutusele", "Andmekaitse Inspektsioonile").
LEGAL_LANG = ("Õiguslik teave ja privaatsus", """
<h1 style="font-size:1.8rem;margin:24px 0 6px">Õiguslik teave ja privaatsus</h1>
<p class="muted">Viimati uuendatud: 28. oktoober 2026. See on tõlge; kahtluse korral kehtib <a href="/legal.html">hispaaniakeelne versioon</a>.</p>

<h2 id="aviso">Õiguslik teave</h2>
<p>Selle veebisaidi haldaja on <b>Manuel Lorente Gálvez</b>, Calle Allue Salvador 22, 50830 Villanueva de Gállego (Zaragoza), Hispaania
(Hispaania maksukohustuslase number NIF 17747339X), kontakt
<a href="mailto:hola@guitle.com">hola@guitle.com</a>, veebisait guitle.com. Tegevus: muusikainstrumentide hinnavõrdlus ja partnerreklaam.
Majutus: GitHub Pages (GitHub, Inc.).</p>

<h2 id="kasutustingimused">Kasutustingimused</h2>
<p>guitle on hinnavõrdlusportaal ega müü ise midagi. Näitame hindu, mida poed oma veebisaitidel avaldavad, ja lingime nendele,
et saaksid osta otse poest. Ostu, tarne, garantii ja tagastuse eest vastutab iga pood ise.</p>
<ul>
<li><b>Hinnad on soovituslikud.</b> Kontrollime hindu regulaarselt, kuid need võivad igal ajal muutuda. Kehtib alati hind, mida pood tellimuse esitamisel näitab.</li>
<li><b>Õigsust ei garanteerita.</b> Püüame, et tooted, hinnad ja laoseis oleksid õiged, kuid vead on võimalikud. Kui märkad mõnda, anna meile teada.</li>
<li><b>Kaubamärgid ja pildid.</b> Kaubamärgid, tootenimed ja pildid kuuluvad nende omanikele ning neid kasutatakse ainult toodete tuvastamiseks.</li>
<li><b>guitle'i sisu.</b> guitle'i kujundus, logo, tekstid ja andmekogumid kuuluvad haldajale. Massiline kopeerimine või ärilistel eesmärkidel kasutamine ilma loata ei ole lubatud.</li>
</ul>

<h2 id="affiliate">Partnerlingid</h2>
<p>Mõned poelingid on partnerlingid: kui ostad pärast lingil klõpsamist, võib pood maksta guitle'ile väikest vahendustasu. Sinu jaoks hind
ei muutu. Vahendustasud ei mõjuta tulemuste järjekorda: poed on alati sorteeritud hinna järgi, odavaim esimesena.</p>

<h2 id="privaatsus">Privaatsuspoliitika</h2>
<p>guitle ei küsi saidi kasutamiseks isikuandmeid: pole registreerimist, uudiskirju ega analüüsi- või reklaamitööriistu,
mis sind jälgiksid. Loendame külastusi ainult anonüümselt ja kui tellid hinnateavituse, salvestame selle jaoks sinu e-posti aadressi.</p>
<ul>
<li><b>Hinnateavitused.</b> Kui soovid teada saada, millal toote hind langeb, salvestame sinu e-posti aadressi, toote,
selle tolle päeva hinna ja sinu sihthinna, kui selle sisestad. Kasutame neid ainult kinnituskirja ja selle toote teavituste saatmiseks,
mitte kunagi reklaamiks, ega jaga neid kellegagi. Õiguslik alus: sinu nõusolek (isikuandmete kaitse üldmääruse artikli 6 lõike 1 punkt a), mille annad
teavitust tellides ja oma e-posti kinnitades. Andmeid hoitakse Google Cloud Firestore'is (Google Ireland Ltd., server Madridis); e-kirjad saadame
postkastist hola@guitle.com (DonDominio, Hispaania). Kinnitamata teavitused kustutatakse 7 päeva pärast; kinnitatud teavitusi hoitakse, kuni loobud
igas e-kirjas oleva lingi kaudu (teavitus kustutatakse kohe) või palud meil need kustutada.</li>
<li><b>Seaded sinu brauseris.</b> Filtrid ja valitud vaade salvestatakse sinu brauseri kohalikku mällu (localStorage) ega saadeta ühtegi serverisse.</li>
<li><b>Majutus.</b> Sait on majutatud GitHub Pagesis (GitHub, Inc.). Nagu iga veebiserver, võib GitHub tehnilistel ja turvalisuse põhjustel
logida iga külastaja IP-aadressi. GitHub osaleb ELi-USA andmekaitseraamistikus (EU-US Data Privacy Framework).</li>
<li><b>Külastuste loendur.</b> Iga leht suurendab anonüümset loendurit 1 võrra: päev, vaadatud leht, sait, kust tulid (nt google.com), mida
kataloogi otsingusse kirjutad ja, kui klõpsad poodi, poe nimi. Ei mingeid küpsiseid, IP-aadressi ega midagi, mis sind tuvastaks. Loendureid hoitakse
Google Cloud Firestore'is (Google Ireland Ltd.) Euroopa Liidus asuvas serveris (Madrid).</li>
<li><b>Muid päringuid kolmandatele osapooltele ei tehta.</b> Fondid, graafikud ja tootefotod laaditakse saidilt guitle.com.</li>
<li><b>Poodi minnes.</b> Kui klõpsad poodi, lahkud guitle'ist ja kehtib selle poe privaatsuspoliitika.</li>
</ul>
<p><b>Sinu õigused.</b> Saad kasutada oma õigust andmetega tutvuda, neid parandada, kustutada, esitada vastuväiteid, piirata töötlemist ja
andmeid üle kanda, kirjutades aadressile <a href="mailto:hola@guitle.com">hola@guitle.com</a>. Samuti võid esitada kaebuse andmekaitse
järelevalveasutusele, näiteks Hispaania Agencia Española de Protección de Datos'ile või oma riigi andmekaitse järelevalveasutusele.
Vastutav töötleja: õiguslikus teabes nimetatud haldaja.</p>

<h2 id="cookies">Küpsised</h2>
<p>guitle ei kasuta küpsiseid, ei omi ega kolmandate osapoolte omi – seepärast sa küpsiste bännerit ei näe. Kasutame ainult brauseri kohalikku
mälu, et sinu seadeid meeles pidada. Poed, millele lingime, võivad oma saitidel kasutada oma küpsiseid.</p>
""")
