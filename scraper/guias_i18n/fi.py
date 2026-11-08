"""Oppaat suomeksi (guitle.com/fi/guias/)."""
MORE, FAQ, GUIDES_WORD = "Näytä kaikki", "Usein kysytyt kysymykset", "Oppaat"
INDEX_TITLE = "Oppaat kitaran ostamiseen"
INDEX_DESC = "Oppaat sähkö-, klassisen tai akustisen kitaran, bassokitaran ja vahvistimen valintaan oikeilla malleilla ja tämän päivän hinnoilla."
COURSE_URL, COURSE_TITLE = "kurssi/", "Ilmainen kurssi: ensimmäinen kitarasi"
COURSE_DESC = "Viisi oppituntia alusta: asento, soinnut, rytmi, asteikot ja kaksi kappaletta, metronomin kanssa."

GUIDES = [
    {"slug": "ensimmainen-sahkokitara", "title": "Näin valitset ensimmäisen sähkökitarasi",
     "desc": "Millainen muoto, millaiset mikrofonit ja paljonko käyttää ensimmäiseen sähkökitaraan, sekä myydyimmät alle {p300} tämän päivän hinnoin.",
     "body": """<section class="hub-sec guia">
<h2>Millainen muoto</h2>
<ul>
<li><strong>Stratocaster-tyyppi (ST):</strong> monipuolisin ja mukavin, popiin, rockiin, bluesiin ja funkiin. Jos epäröit, aloita tästä.</li>
<li><strong>Telecaster-tyyppi (T):</strong> yksinkertaisempi, kirkas ja suora soundi, suosittu rockissa ja countryssa.</li>
<li><strong>Single cut (Les Paul -tyyppi):</strong> täyteläisempi soundi ja pidempi sustain, ihanteellinen rockiin ja bluesiin. Yleensä painavampi.</li>
<li><strong>Superstrat:</strong> ohut kaula ja tehokkaat mikrofonit, tehty hard rockiin ja metalliin.</li>
</ul>
<h2>Mikrofonit: single coil vai humbucker</h2>
<p><strong>Single coil -mikrofonit</strong> kuulostavat kirkkailta ja heleiltä; <strong>humbuckerit</strong> kuulostavat täyteläisemmiltä ja hurisevat vähemmän särön kanssa. <strong>HSS</strong>-kokoonpano yhdistää molemmat ja on aloittelijalle monipuolisin.</p>
<h2>Paljonko käyttää</h2>
<p>Hintaluokassa <strong>{p150}–{p300}</strong> löydät kitaroita, jotka kuulostavat hyviltä ja kestävät vuosia: muun muassa Yamaha Pacifica, Squier, Ibanez GIO, Epiphone tai Harley Benton. Sähkökitara tarvitsee <strong>vahvistimen</strong> (tai pienen kuulokevahvistimen); jos aloitat tyhjästä, paketti tulee yleensä halvemmaksi.</p>
<p>Saman mallin hinta voi vaihdella kaupasta toiseen yllättävän paljon. guitle vertaa hintaa joka päivä {shops} kaupassa ja tallentaa hintahistorian.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Sähkökitarat alle {p300}, joita useimmat kaupat myyvät (tämän päivän hinnat)")],
     "faqs": [("Millainen sähkökitara aloittelijalle?", "Stratocaster-tyyppinen HSS-mikrofoneilla, hintaan {p150}–{p300}: Yamaha Pacifica, Squier ja Ibanez GIO ovat suosittuja ensimmäisiä kitaroita."),
              ("Tarvitseeko sähkökitara vahvistimen?", "Kyllä: ilman vahvistinta sitä tuskin kuulee. Aluksi riittää pieni harjoitusvahvistin tai kuulokevahvistin."),
              ("Kannattaako aloittelijan kitarapaketti?", "Jos aloitat tyhjästä, kyllä: kitara, vahvistin ja tarvikkeet maksavat yhdessä vähemmän kuin erikseen.")]},
    {"slug": "klassinen-vai-akustinen-kitara", "title": "Klassinen vai akustinen kitara: kumpi valita",
     "desc": "Klassisen ja akustisen kitaran ero, kumpi valita aloittelijana, lasten koot ja mallit tämän päivän hinnoin.",
     "body": """<section class="hub-sec guia">
<h2>Kaikki on kielissä</h2>
<p><strong>Klassisessa</strong> kitarassa on <strong>nailonkielet</strong>: pehmeät sormille, lämmin soundi ja leveämpi kaula. <strong>Akustisessa</strong> (teräskielisessä) kitarassa on <strong>teräskielet</strong>: kirkkaampi ja voimakkaampi ääni, mutta alussa raskaampi sormille.</p>
<ul>
<li><strong>Klassinen:</strong> klassinen musiikki, flamenco, bossa nova sekä lapsille ja opettajan johdolla soittamiseen.</li>
<li><strong>Akustinen:</strong> pop, rock, folk ja laulun säestys.</li>
</ul>
<h2>Koot</h2>
<p>Klassisia kitaroita on koossa <strong>4/4</strong> aikuisille, <strong>3/4</strong> noin 8–11-vuotiaille lapsille ja <strong>1/2</strong> nuoremmille. <strong>Elektroakustisessa</strong> kitarassa on esivahvistin, joten sen voi kytkeä vahvistimeen.</p>
<h2>Paljonko käyttää</h2>
<p>Hyviä klassisia kitaroita saa noin <strong>{p100}–{p200}</strong> alkaen ja akustisia <strong>{p150}–{p300}</strong> alkaen. Täyspuukantiset kuulostavat paremmilta ja paranevat vuosien myötä. guitle vertaa hintaa joka päivä {shops} kaupassa.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klassiset kitarat alle {p200}, joita useimmat kaupat myyvät (tämän päivän hinnat)"),
               ("acustica", 300, 8, 3, True, "Akustiset kitarat alle {p300}, joita useimmat kaupat myyvät (tämän päivän hinnat)")],
     "faqs": [("Klassinen vai akustinen kitara aloittelijalle?", "Klassinen on mukavampi nailonkielten ansiosta; akustinen sopii paremmin, jos haluat soittaa poppia, rockia tai folkia."),
              ("Minkä kokoinen kitara lapselle?", "Suuntaa antavasti 1/2 noin 7–8-vuotiaaksi asti, 3/4 8–11-vuotiaille ja 4/4 12 vuodesta ylöspäin."),
              ("Voiko klassiseen kitaraan laittaa teräskielet?", "Ei: klassista kitaraa ei ole tehty sellaiselle kireydelle, ja kaula tai talla voi vaurioitua.")]},
    {"slug": "ensimmainen-bassokitara", "title": "Näin valitset ensimmäisen bassokitarasi",
     "desc": "4 vai 5 kieltä, Precision vai Jazz Bass ja paljonko käyttää ensimmäiseen bassoon, sekä myydyimmät alle {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 vai 5 kieltä</h2>
<p>Aloita <strong>nelikielisellä</strong> bassolla: se on standardi lähes kaikissa tyyleissä. <strong>Viisikielisessä</strong> on yksi ylimääräinen matala kieli, suosittu metallissa ja modernissa funkissa, mutta kaula on leveämpi.</p>
<ul>
<li><strong>Precision-tyyppi (P):</strong> pyöreä ja jämäkkä soundi, yksinkertainen ja toimiva.</li>
<li><strong>Jazz Bass -tyyppi (J):</strong> kaksi mikrofonia ja kapeampi kaula, terävämpi soundi.</li>
<li><strong>Short scale:</strong> lyhyempi mensuuri, mukavampi pienille käsille.</li>
</ul>
<p>Hintaluokassa <strong>{p200}–{p400}</strong> on erittäin hyviä aloitusbassoja. Basso tarvitsee bassovahvistimen: matalat taajuudet voivat rikkoa kitaravahvistimen.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Bassokitarat alle {p400}, joita useimmat kaupat myyvät (tämän päivän hinnat)")],
     "faqs": [("Millainen bassokitara aloittelijalle?", "Nelikielinen Precision-, Jazz Bass- tai PJ-basso hintaan {p200}–{p400}."),
              ("Voiko basson kytkeä kitaravahvistimeen?", "Mieluummin ei: matalat taajuudet voivat rikkoa kaiuttimen. Tarvitset bassovahvistimen.")]},
    {"slug": "ensimmainen-kitaravahvistin", "title": "Millainen kitaravahvistin aloittelijalle",
     "desc": "Montako wattia, mallintava vai putkivahvistin ja paljonko käyttää ensimmäiseen vahvistimeen, sekä myydyimmät alle {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Kotona tarvitset vähän</h2>
<p>Kotiharjoitteluun <strong>10–30 watin</strong> vahvistin riittää mainiosti; tärkeintä on, että se kuulostaa hyvältä pienellä äänenvoimakkuudella ja siinä on <strong>kuulokeliitäntä</strong>.</p>
<ul>
<li><strong>Mallintava (digitaalinen):</strong> jäljittelee monia vahvistimia ja siinä on sisäänrakennetut efektit: kätevin aloittelijalle (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Putkivahvistin:</strong> rockin ja bluesin klassinen soundi, kalliimpi ja tehty soittamaan kovaa.</li>
</ul>
<p>Hintaluokasta <strong>{p100}–{p300}</strong> löydät erittäin monipuolisia harjoitusvahvistimia.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Vahvistimet alle {p300}, joita useimmat kaupat myyvät (tämän päivän hinnat)")],
     "faqs": [("Millainen kitaravahvistin kotiin?", "10–30 watin vahvistin kuulokeliitännällä; digitaalinen mallintava vahvistin on kätevin aloittamiseen.")]},
    {"slug": "kitarapaketit", "title": "Kitarapaketit: milloin ne kannattavat",
     "desc": "Mitä kitarapaketti sisältää, milloin se tulee halvemmaksi kuin erikseen ostaminen, ja myydyimmät paketit tämän päivän hinnoin.",
     "body": """<section class="hub-sec guia">
<h2>Mitä paketissa on</h2>
<p>Sähkökitarapaketissa on yleensä <strong>kitara, pieni vahvistin, pussi, johto, hihna, plektroja ja viritin</strong>. Se <strong>kannattaa</strong>, jos aloitat tyhjästä; <strong>vähemmän</strong>, jos sinulla on jo vahvistin tai haluat tietyn kitaran. Katso ennen kaikkea kitaraa: se jää käyttöön.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Paketit alle {p400}, joita useimmat kaupat myyvät (tämän päivän hinnat)")],
     "faqs": [("Kannattaako kitarapaketti aloittelijalle?", "Kyllä, jos aloitat tyhjästä: se tulee halvemmaksi kuin kaiken ostaminen erikseen.")]},
]
