"""Guides en français (guitle.com/fr/guides…, /lu/)."""
MORE, FAQ, GUIDES_WORD = "Tout voir", "Questions fréquentes", "Guides"
INDEX_TITLE = "Guides pour acheter une guitare"
INDEX_DESC = "Guides pour choisir une guitare électrique, classique ou folk, une basse et un ampli, avec des modèles et les prix réels du jour."
COURSE_URL, COURSE_TITLE = "cours/", "Cours gratuit : ta première guitare"
COURSE_DESC = "Cinq leçons depuis zéro : posture, accords, rythme, gammes et deux morceaux, avec métronome."

GUIDES = [
    {"slug": "premiere-guitare-electrique", "title": "Comment choisir sa première guitare électrique",
     "desc": "Quelle forme, quels micros et quel budget pour ta première guitare électrique, avec les plus vendues à moins de {p300} et leur prix du jour.",
     "body": """<section class="hub-sec guia">
<h2>Quelle forme choisir</h2>
<ul>
<li><strong>Type Stratocaster (ST) :</strong> la plus polyvalente et confortable, pour la pop, le rock, le blues et le funk. Dans le doute, commence par là.</li>
<li><strong>Type Telecaster (T) :</strong> plus simple, au son brillant et direct, très utilisée en rock et en country.</li>
<li><strong>Single cut (type Les Paul) :</strong> son plus épais avec plus de sustain, idéale pour le rock et le blues. Souvent plus lourde.</li>
<li><strong>Superstrat :</strong> manche fin et micros puissants, pensée pour le hard rock et le metal.</li>
</ul>
<h2>Micros : simples ou doubles</h2>
<p>Les <strong>simples bobinages</strong> sonnent clair et brillant ; les <strong>humbuckers</strong> sonnent plus gras et soufflent moins en saturation. La configuration <strong>HSS</strong> réunit les deux : la plus polyvalente pour débuter.</p>
<h2>Quel budget</h2>
<p>Entre <strong>{p150} et {p300}</strong>, on trouve des guitares qui sonnent bien et durent des années : Yamaha Pacifica, Squier, Ibanez GIO, Epiphone ou Harley Benton, entre autres. Une électrique a besoin d'un <strong>ampli</strong> (ou d'un petit ampli casque) ; pour débuter de zéro, un pack revient souvent moins cher.</p>
<p>Le même modèle peut varier de plusieurs dizaines d'euros d'un magasin à l'autre. Sur guitle, nous comparons le prix dans {shops} magasins chaque jour et gardons l'historique.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Les électriques à moins de {p300} vendues par le plus de magasins (prix du jour)")],
     "faqs": [("Quelle guitare électrique acheter pour débuter ?", "Une type Stratocaster avec des micros HSS entre {p150} et {p300} : Yamaha Pacifica, Squier ou Ibanez GIO sont des modèles très courants pour débuter."),
              ("Faut-il un ampli pour jouer de la guitare électrique ?", "Oui : sans ampli, on l'entend à peine. Pour débuter, un petit ampli de travail ou un ampli casque suffit."),
              ("Un pack guitare électrique, est-ce une bonne idée ?", "Si tu pars de zéro, oui : guitare, ampli et accessoires reviennent moins cher qu'achetés séparément.")]},
    {"slug": "guitare-classique-ou-folk", "title": "Guitare classique ou folk : laquelle choisir",
     "desc": "Différences entre guitare classique et folk, laquelle choisir pour débuter, tailles pour enfants et modèles avec leur prix du jour.",
     "body": """<section class="hub-sec guia">
<h2>Tout est dans les cordes</h2>
<p>La <strong>classique</strong> a des cordes en <strong>nylon</strong> : douces pour les doigts, au son chaud, avec un manche large. La <strong>folk</strong> a des cordes en <strong>acier</strong> : plus brillante et puissante, mais plus dure pour les doigts au début.</p>
<ul>
<li><strong>Classique :</strong> musique classique, flamenco, bossa nova, et pour les enfants ou un apprentissage avec professeur.</li>
<li><strong>Folk :</strong> pop, rock, folk et accompagnement au chant.</li>
</ul>
<h2>Tailles</h2>
<p>Les classiques existent en <strong>4/4</strong> pour les adultes, <strong>3/4</strong> pour les enfants d'environ 8 à 11 ans et <strong>1/2</strong> pour les plus petits. Une <strong>électro-acoustique</strong> a un préampli pour se brancher sur un ampli.</p>
<h2>Quel budget</h2>
<p>Bonnes classiques dès <strong>{p100}–{p200}</strong>, folks dès <strong>{p150}–{p300}</strong>. Avec une table massive, elles sonnent mieux et se bonifient avec le temps. Sur guitle, nous comparons le prix dans {shops} magasins chaque jour.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Classiques à moins de {p200} vendues par le plus de magasins (prix du jour)"),
               ("acustica", 300, 8, 3, True, "Folks à moins de {p300} vendues par le plus de magasins (prix du jour)")],
     "faqs": [("Pour débuter, guitare classique ou folk ?", "La classique est plus confortable grâce au nylon ; la folk est meilleure si tu veux jouer pop, rock ou folk."),
              ("Quelle taille de guitare pour un enfant ?", "En gros, 1/2 jusqu'à 7-8 ans, 3/4 de 8 à 11 ans et 4/4 à partir de 12 ans."),
              ("Peut-on mettre des cordes acier sur une classique ?", "Non : la classique n'est pas conçue pour cette tension, le manche ou le chevalet peuvent s'abîmer.")]},
    {"slug": "premiere-basse-electrique", "title": "Comment choisir sa première basse électrique",
     "desc": "4 ou 5 cordes, Precision ou Jazz Bass et quel budget pour ta première basse, avec les plus vendues à moins de {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 ou 5 cordes</h2>
<p>Pour débuter, une basse <strong>4 cordes</strong> : c'est la norme dans presque tous les styles. La <strong>5 cordes</strong> ajoute une corde grave, prisée en metal ou en funk moderne, mais son manche est plus large.</p>
<ul>
<li><strong>Type Precision (P) :</strong> son rond et puissant, simple et efficace.</li>
<li><strong>Type Jazz Bass (J) :</strong> deux micros et manche plus fin, son plus défini.</li>
<li><strong>Diapason court :</strong> frettes plus rapprochées, plus confortable pour les petites mains.</li>
</ul>
<p>Entre <strong>{p200} et {p400}</strong>, il y a de très bonnes basses pour débuter. Une basse a besoin d'un ampli basse : les graves peuvent abîmer un ampli guitare.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Basses à moins de {p400} vendues par le plus de magasins (prix du jour)")],
     "faqs": [("Quelle basse acheter pour débuter ?", "Une 4 cordes type Precision, Jazz Bass ou PJ entre {p200} et {p400}."),
              ("Peut-on brancher une basse sur un ampli guitare ?", "Ce n'est pas conseillé : les graves peuvent endommager le haut-parleur. Il faut un ampli basse.")]},
    {"slug": "premier-ampli-guitare", "title": "Quel ampli guitare acheter pour débuter",
     "desc": "Combien de watts, modélisation ou lampes et quel budget pour ton premier ampli, avec les plus vendus à moins de {p300}.",
     "body": """<section class="hub-sec guia">
<h2>À la maison, peu suffit</h2>
<p>Pour travailler chez soi, un ampli de <strong>10 à 30 watts</strong> suffit largement ; l'important est qu'il sonne bien à faible volume et ait une <strong>sortie casque</strong>.</p>
<ul>
<li><strong>À modélisation :</strong> imite de nombreux amplis et intègre des effets : le plus pratique pour débuter (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>À lampes :</strong> le son classique du rock et du blues, plus cher et fait pour jouer fort.</li>
</ul>
<p>Entre <strong>{p100} et {p300}</strong>, on trouve des amplis de travail très complets.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplis à moins de {p300} vendus par le plus de magasins (prix du jour)")],
     "faqs": [("Quel ampli guitare pour la maison ?", "Un ampli de 10 à 30 watts avec sortie casque ; un ampli à modélisation est le plus pratique pour débuter.")]},
    {"slug": "packs-guitare", "title": "Packs guitare : quand sont-ils intéressants",
     "desc": "Ce que contient un pack guitare, quand il vaut mieux qu'un achat séparé, et les packs les plus vendus avec leur prix du jour.",
     "body": """<section class="hub-sec guia">
<h2>Ce que contient un pack</h2>
<p>Un pack guitare électrique contient en général <strong>guitare, petit ampli, housse, câble, sangle, médiators et accordeur</strong>. Il est <strong>intéressant</strong> si tu pars de zéro ; <strong>moins</strong> si tu as déjà un ampli ou vises une guitare précise. Regarde surtout la guitare : c'est elle qui dure.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Packs à moins de {p400} vendus par le plus de magasins (prix du jour)")],
     "faqs": [("Un pack guitare pour débuter, ça vaut le coup ?", "Oui si tu pars de zéro : c'est moins cher que d'acheter chaque élément séparément.")]},
]
