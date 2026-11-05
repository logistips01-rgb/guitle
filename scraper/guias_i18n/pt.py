"""Guias em português de Portugal (guitle.com/pt/guias/)."""
MORE, FAQ, GUIDES_WORD = "Ver todas", "Perguntas frequentes", "Guias"
INDEX_TITLE = "Guias para comprar guitarra"
INDEX_DESC = "Guias para escolher guitarra elétrica, clássica ou acústica, baixo e amplificador, com modelos e preços reais de hoje."
COURSE_URL, COURSE_TITLE = "curso/", "Curso grátis: a tua primeira guitarra"
COURSE_DESC = "Cinco lições desde zero: postura, acordes, ritmo, escalas e duas canções, com metrónomo."

GUIDES = [
    {"slug": "primeira-guitarra-eletrica", "title": "Como escolher a tua primeira guitarra elétrica",
     "desc": "Que forma, que captadores e quanto gastar na tua primeira guitarra elétrica, com as mais vendidas abaixo de {p300} e o preço de hoje em cada loja.",
     "body": """<section class="hub-sec guia">
<h2>Que forma escolher</h2>
<ul>
<li><strong>Tipo Stratocaster (ST):</strong> a mais versátil e confortável. Serve para pop, rock, blues e funk. Na dúvida, começa por aqui.</li>
<li><strong>Tipo Telecaster (T):</strong> mais simples, com um som brilhante e direto, muito usada no rock e no country.</li>
<li><strong>Single cut (tipo Les Paul):</strong> som mais encorpado e com mais sustain, ideal para rock e blues. Costuma pesar mais.</li>
<li><strong>Superstrat ou moderna:</strong> braço fino e captadores potentes, pensada para rock pesado e metal.</li>
</ul>
<h2>Captadores: simples ou duplos</h2>
<p>Os <strong>simples</strong> (single coil) soam claros e brilhantes; os <strong>duplos</strong> (humbucker) soam mais encorpados e com menos ruído com distorção. A configuração <strong>HSS</strong> junta os dois e é a mais versátil para quem ainda não sabe que estilo vai tocar.</p>
<h2>Quanto gastar</h2>
<p>Entre <strong>{p150} e {p300}</strong> há guitarras que soam bem e duram anos: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone ou Harley Benton, entre outras. Lembra-te de que uma elétrica precisa de <strong>amplificador</strong> (ou de um pequeno amplificador de auscultadores); se começas do zero, um pack costuma sair mais barato.</p>
<p>O mesmo modelo pode variar dezenas de euros entre lojas. No guitle comparamos o preço em {shops} lojas todos os dias e guardamos o histórico.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "As elétricas abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Que guitarra elétrica comprar para começar?", "Uma tipo Stratocaster com captadores HSS entre {p150} e {p300}: Yamaha Pacifica, Squier ou Ibanez GIO são modelos muito habituais para começar."),
              ("Preciso de amplificador para tocar guitarra elétrica?", "Sim: sem amplificador quase não se ouve. Para começar chega um pequeno amplificador de estudo ou um de auscultadores."),
              ("Vale a pena comprar um pack de guitarra elétrica?", "Se começas do zero, sim: guitarra, amplificador e acessórios saem mais baratos do que em separado.")]},
    {"slug": "guitarra-classica-ou-acustica", "title": "Guitarra clássica ou acústica: qual escolher",
     "desc": "Diferenças entre guitarra clássica e acústica, qual escolher para começar, tamanhos para crianças e modelos com o preço de hoje.",
     "body": """<section class="hub-sec guia">
<h2>A diferença está nas cordas</h2>
<p>A <strong>clássica</strong> leva cordas de <strong>nylon</strong>: são macias, não magoam os dedos e têm um som quente. A <strong>acústica</strong> leva cordas de <strong>aço</strong>: soa mais brilhante e potente, mas no início custa mais pressionar as cordas.</p>
<ul>
<li><strong>Clássica:</strong> música clássica, flamenco, bossa nova e, em geral, para crianças e para aprender com professor.</li>
<li><strong>Acústica:</strong> pop, rock, folk e acompanhar canções a cantar.</li>
</ul>
<h2>Tamanhos</h2>
<p>As clássicas têm tamanhos: <strong>4/4</strong> para adultos, <strong>3/4</strong> para crianças de cerca de 8 a 11 anos e <strong>1/2</strong> para as mais pequenas. Uma <strong>eletroacústica</strong> leva um pré-amplificador para ligar a um amplificador.</p>
<h2>Quanto gastar</h2>
<p>Há boas clássicas a partir de uns <strong>{p100}–{p200}</strong> e acústicas a partir de <strong>{p150}–{p300}</strong>. Com tampo maciço soam melhor e melhoram com os anos. No guitle comparamos o preço em {shops} lojas todos os dias.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Clássicas abaixo de {p200} que mais lojas vendem (preços de hoje)"),
               ("acustica", 300, 8, 3, True, "Acústicas abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("O que é melhor para começar, guitarra clássica ou acústica?", "A clássica é mais confortável para começar pelas cordas de nylon; a acústica é melhor se queres tocar pop, rock ou folk."),
              ("Que tamanho de guitarra precisa uma criança?", "Como orientação, 1/2 até aos 7-8 anos, 3/4 dos 8 aos 11 e 4/4 a partir dos 12."),
              ("Posso pôr cordas de aço numa guitarra clássica?", "Não: a clássica não foi feita para a tensão das cordas de aço e o braço ou a ponte podem estragar-se.")]},
    {"slug": "primeiro-baixo-eletrico", "title": "Como escolher o teu primeiro baixo elétrico",
     "desc": "4 ou 5 cordas, Precision ou Jazz Bass e quanto gastar no teu primeiro baixo, com os mais vendidos abaixo de {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 ou 5 cordas</h2>
<p>Para começar, um baixo de <strong>4 cordas</strong>: é o padrão em quase todos os estilos. O de <strong>5 cordas</strong> acrescenta uma corda grave, muito usada no metal ou no funk moderno, mas tem o braço mais largo.</p>
<ul>
<li><strong>Tipo Precision (P):</strong> som grosso e redondo, simples e muito agradecido.</li>
<li><strong>Tipo Jazz Bass (J):</strong> duas pastilhas e braço mais fino, com som mais definido.</li>
<li><strong>Escala curta:</strong> trastes mais juntos, mais confortável para mãos pequenas.</li>
</ul>
<p>Entre <strong>{p200} e {p400}</strong> há baixos muito bons para começar. O baixo precisa de um amplificador de baixo: um de guitarra pode estragar-se com os graves.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Baixos abaixo de {p400} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Que baixo comprar para começar?", "Um baixo de 4 cordas tipo Precision, Jazz Bass ou PJ entre {p200} e {p400}."),
              ("Posso ligar um baixo a um amplificador de guitarra?", "Não é recomendável: os graves podem danificar o altifalante. Precisas de um amplificador de baixo.")]},
    {"slug": "primeiro-amplificador-guitarra", "title": "Que amplificador de guitarra comprar para começar",
     "desc": "Quantos watts, modelador ou válvulas e quanto gastar no teu primeiro amplificador, com os mais vendidos abaixo de {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Para casa chega pouco</h2>
<p>Para estudar em casa, um amplificador de <strong>10 a 30 watts</strong> é mais do que suficiente; o importante é que soe bem a volume baixo e tenha <strong>saída de auscultadores</strong>.</p>
<ul>
<li><strong>Modelador (digital):</strong> imita muitos amplificadores e traz efeitos; para começar é o mais prático (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>A válvulas:</strong> o som clássico do rock e do blues, mais caro e pensado para tocar com volume.</li>
</ul>
<p>Entre <strong>{p100} e {p300}</strong> há amplificadores de estudo muito completos.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplificadores abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Que amplificador de guitarra comprar para casa?", "Um de 10 a 30 watts com saída de auscultadores; um modelador digital é o mais prático para começar."),
              ("Quantos watts precisa um amplificador de guitarra?", "Para casa, 10 a 30 watts. Para tocar com bateria, a partir de 30–50 watts.")]},
    {"slug": "packs-de-guitarra", "title": "Packs de guitarra: quando compensam",
     "desc": "O que traz um pack de guitarra, quando compensa face a comprar em separado e os packs mais vendidos com o preço de hoje.",
     "body": """<section class="hub-sec guia">
<h2>O que traz um pack</h2>
<p>Um pack de guitarra elétrica costuma trazer <strong>guitarra, amplificador pequeno, saco, cabo, correia, palhetas e afinador</strong>. <strong>Compensa</strong> se começas do zero; <strong>não compensa</strong> se já tens amplificador ou queres uma guitarra concreta. Repara sobretudo na guitarra: é o que mais dura.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Packs abaixo de {p400} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Vale a pena um pack de guitarra para começar?", "Sim, se começas do zero: sai mais barato do que comprar tudo em separado.")]},
]
