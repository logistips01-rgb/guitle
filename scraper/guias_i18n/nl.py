"""Gidsen in het Nederlands (guitle.com/nl/guias/, /be/)."""
MORE, FAQ, GUIDES_WORD = "Alles bekijken", "Veelgestelde vragen", "Gidsen"
INDEX_TITLE = "Gidsen voor het kopen van een gitaar"
INDEX_DESC = "Gidsen om een elektrische, klassieke of akoestische gitaar, basgitaar en versterker te kiezen, met echte modellen en prijzen van vandaag."
COURSE_URL, COURSE_TITLE = "cursus/", "Gratis cursus: je eerste gitaar"
COURSE_DESC = "Vijf lessen vanaf nul: houding, akkoorden, ritme, toonladders en twee liedjes, met metronoom."

GUIDES = [
    {"slug": "eerste-elektrische-gitaar", "title": "Zo kies je je eerste elektrische gitaar",
     "desc": "Welke vorm, welke elementen en hoeveel uitgeven aan je eerste elektrische gitaar, met de bestverkochte onder {p300} en hun prijs van vandaag.",
     "body": """<section class="hub-sec guia">
<h2>Welke vorm</h2>
<ul>
<li><strong>Stratocaster-model (ST):</strong> de veelzijdigste en meest comfortabele, voor pop, rock, blues en funk. Twijfel je, begin dan hier.</li>
<li><strong>Telecaster-model (T):</strong> eenvoudiger, met een heldere, directe klank, geliefd in rock en country.</li>
<li><strong>Single cut (Les Paul-model):</strong> vollere klank met meer sustain, ideaal voor rock en blues. Meestal zwaarder.</li>
<li><strong>Superstrat:</strong> dunne hals en krachtige elementen, gemaakt voor hardrock en metal.</li>
</ul>
<h2>Elementen: single coil of humbucker</h2>
<p><strong>Single coils</strong> klinken helder en sprankelend; <strong>humbuckers</strong> klinken voller en brommen minder met vervorming. Een <strong>HSS</strong>-configuratie combineert beide en is het veelzijdigst voor beginners.</p>
<h2>Hoeveel uitgeven</h2>
<p>Tussen <strong>{p150} en {p300}</strong> vind je gitaren die goed klinken en jaren meegaan: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone of Harley Benton, onder andere. Een elektrische gitaar heeft een <strong>versterker</strong> nodig (of een kleine koptelefoonversterker); begin je vanaf nul, dan is een set vaak goedkoper.</p>
<p>Hetzelfde model kan tientallen euro's verschillen tussen winkels. guitle vergelijkt de prijs elke dag in {shops} winkels en bewaart de prijsgeschiedenis.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Elektrische gitaren onder {p300} die de meeste winkels verkopen (prijzen van vandaag)")],
     "faqs": [("Welke elektrische gitaar koop je als beginner?", "Een Stratocaster-model met HSS-elementen tussen {p150} en {p300}: Yamaha Pacifica, Squier en Ibanez GIO zijn veelgekozen eerste gitaren."),
              ("Heb ik een versterker nodig voor een elektrische gitaar?", "Ja: zonder versterker hoor je hem nauwelijks. Om te beginnen volstaat een kleine oefenversterker of koptelefoonversterker."),
              ("Is een gitaarset voor beginners de moeite waard?", "Als je vanaf nul begint wel: gitaar, versterker en accessoires zijn samen goedkoper dan los.")]},
    {"slug": "klassieke-of-akoestische-gitaar", "title": "Klassieke of akoestische gitaar: welke kies je",
     "desc": "Het verschil tussen klassieke en akoestische gitaren, welke je kiest als beginner, maten voor kinderen en modellen met hun prijs van vandaag.",
     "body": """<section class="hub-sec guia">
<h2>Het zit in de snaren</h2>
<p>Een <strong>klassieke</strong> gitaar heeft <strong>nylon</strong> snaren: zacht voor de vingers, warm van klank, met een bredere hals. Een <strong>akoestische</strong> (western) gitaar heeft <strong>stalen</strong> snaren: helderder en luider, maar in het begin zwaarder voor de vingers.</p>
<ul>
<li><strong>Klassiek:</strong> klassieke muziek, flamenco, bossa nova, en voor kinderen of les bij een docent.</li>
<li><strong>Akoestisch:</strong> pop, rock, folk en zingen met begeleiding.</li>
</ul>
<h2>Maten</h2>
<p>Klassieke gitaren zijn er in <strong>4/4</strong> voor volwassenen, <strong>3/4</strong> voor kinderen van ongeveer 8 tot 11 jaar en <strong>1/2</strong> voor jongere kinderen. Een <strong>elektro-akoestische</strong> gitaar heeft een voorversterker om aan te sluiten op een versterker.</p>
<h2>Hoeveel uitgeven</h2>
<p>Goede klassieke gitaren vanaf zo'n <strong>{p100}–{p200}</strong>, akoestische vanaf <strong>{p150}–{p300}</strong>. Met een massief bovenblad klinken ze beter en worden ze met de jaren mooier. guitle vergelijkt de prijs elke dag in {shops} winkels.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Klassieke gitaren onder {p200} die de meeste winkels verkopen (prijzen van vandaag)"),
               ("acustica", 300, 8, 3, True, "Akoestische gitaren onder {p300} die de meeste winkels verkopen (prijzen van vandaag)")],
     "faqs": [("Klassieke of akoestische gitaar voor beginners?", "Klassiek is comfortabeler dankzij de nylon snaren; akoestisch is beter als je pop, rock of folk wilt spelen."),
              ("Welke gitaarmaat heeft een kind nodig?", "Grofweg 1/2 tot 7-8 jaar, 3/4 van 8 tot 11 jaar en 4/4 vanaf 12 jaar."),
              ("Kan ik stalen snaren op een klassieke gitaar zetten?", "Nee: een klassieke gitaar is niet gebouwd voor die spanning; hals of brug kunnen beschadigen.")]},
    {"slug": "eerste-basgitaar", "title": "Zo kies je je eerste basgitaar",
     "desc": "4 of 5 snaren, Precision of Jazz Bass en hoeveel uitgeven aan je eerste bas, met de bestverkochte onder {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 of 5 snaren</h2>
<p>Begin met een <strong>4-snarige</strong> bas: de standaard in bijna elke stijl. Een <strong>5-snarige</strong> heeft een extra lage snaar, populair in metal en moderne funk, maar een bredere hals.</p>
<ul>
<li><strong>Precision-model (P):</strong> ronde, stevige klank, eenvoudig en doeltreffend.</li>
<li><strong>Jazz Bass-model (J):</strong> twee elementen en een slankere hals, met een strakkere klank.</li>
<li><strong>Short scale:</strong> kortere mensuur, comfortabeler voor kleine handen.</li>
</ul>
<p>Tussen <strong>{p200} en {p400}</strong> zijn er heel goede basgitaren om mee te beginnen. Een bas heeft een basversterker nodig: de lage tonen kunnen een gitaarversterker beschadigen.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Basgitaren onder {p400} die de meeste winkels verkopen (prijzen van vandaag)")],
     "faqs": [("Welke basgitaar koop je als beginner?", "Een 4-snarige Precision-, Jazz Bass- of PJ-bas tussen {p200} en {p400}."),
              ("Kan ik een bas op een gitaarversterker aansluiten?", "Liever niet: de lage tonen kunnen de luidspreker beschadigen. Je hebt een basversterker nodig.")]},
    {"slug": "eerste-gitaarversterker", "title": "Welke gitaarversterker koop je als beginner",
     "desc": "Hoeveel watt, modeling of buizen en hoeveel uitgeven aan je eerste versterker, met de bestverkochte onder {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Thuis heb je weinig nodig</h2>
<p>Om thuis te oefenen is een versterker van <strong>10 tot 30 watt</strong> ruim voldoende; belangrijk is dat hij zacht goed klinkt en een <strong>koptelefoonuitgang</strong> heeft.</p>
<ul>
<li><strong>Modeling (digitaal):</strong> bootst veel versterkers na en heeft ingebouwde effecten: het handigst om mee te beginnen (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Buizen:</strong> de klassieke rock- en bluesklank, duurder en gemaakt om luid te spelen.</li>
</ul>
<p>Tussen <strong>{p100} en {p300}</strong> vind je heel complete oefenversterkers.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Versterkers onder {p300} die de meeste winkels verkopen (prijzen van vandaag)")],
     "faqs": [("Welke gitaarversterker voor thuis?", "Een van 10 tot 30 watt met koptelefoonuitgang; een digitale modelingversterker is het handigst om te beginnen.")]},
    {"slug": "gitaarsets", "title": "Gitaarsets: wanneer zijn ze de moeite waard",
     "desc": "Wat er in een gitaarset zit, wanneer die voordeliger is dan los kopen, en de bestverkochte sets met hun prijs van vandaag.",
     "body": """<section class="hub-sec guia">
<h2>Wat zit er in een set</h2>
<p>Een elektrische gitaarset bevat meestal een <strong>gitaar, kleine versterker, gigbag, kabel, riem, plectrums en stemapparaat</strong>. Hij is <strong>de moeite waard</strong> als je vanaf nul begint; <strong>minder</strong> als je al een versterker hebt of een bepaalde gitaar wilt. Let vooral op de gitaar: die blijft.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Sets onder {p400} die de meeste winkels verkopen (prijzen van vandaag)")],
     "faqs": [("Is een gitaarset de moeite waard voor beginners?", "Ja als je vanaf nul begint: het is goedkoper dan alles los kopen.")]},
]
