"""Guias em português do Brasil (guitle.com/br/guias/): no Brasil, "guitarra" é a elétrica e "violão" a acústica/clássica."""
MORE, FAQ, GUIDES_WORD = "Ver todos", "Perguntas frequentes", "Guias"
INDEX_TITLE = "Guias para comprar guitarra e violão"
INDEX_DESC = "Guias para escolher guitarra, violão, baixo e amplificador, com modelos e preços reais de hoje nas lojas do Brasil."
COURSE_URL, COURSE_TITLE = "curso/", "Curso grátis: seu primeiro violão ou guitarra"
COURSE_DESC = "Cinco aulas do zero: postura, acordes, ritmo, escalas e duas músicas, com metrônomo."

GUIDES = [
    {"slug": "primeira-guitarra", "title": "Como escolher sua primeira guitarra",
     "desc": "Formato, captadores e quanto gastar na sua primeira guitarra elétrica, com as mais vendidas abaixo de {p300} e o preço de hoje em cada loja.",
     "body": """<section class="hub-sec guia">
<h2>Qual formato escolher</h2>
<ul>
<li><strong>Tipo Stratocaster (ST):</strong> a mais versátil e confortável. Serve para pop, rock, blues e funk. Na dúvida, comece por ela.</li>
<li><strong>Tipo Telecaster (T):</strong> mais simples, com som brilhante e direto, muito usada no rock e no country.</li>
<li><strong>Tipo Les Paul:</strong> som mais encorpado e com mais sustain, ideal para rock e blues.</li>
<li><strong>Superstrat:</strong> braço fino e captadores fortes, pensada para rock pesado e metal.</li>
</ul>
<h2>Captadores: single ou humbucker</h2>
<p>Os <strong>single coil</strong> soam claros e brilhantes; os <strong>humbuckers</strong> soam mais encorpados e com menos ruído na distorção. A configuração <strong>HSS</strong> junta os dois e é a mais versátil para quem está começando.</p>
<h2>Quanto gastar</h2>
<p>Entre <strong>{p150} e {p300}</strong> há guitarras boas e duráveis: Tagima, Strinberg, Squier, Yamaha Pacifica ou Michael, entre outras. Toda guitarra precisa de <strong>amplificador</strong>; se você está começando do zero, um kit costuma sair mais em conta.</p>
<p>O mesmo modelo pode variar bastante de preço entre lojas. No guitle comparamos o preço em {shops} lojas todos os dias e guardamos o histórico.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "As guitarras abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Qual guitarra comprar para começar?", "Uma tipo Stratocaster com captadores HSS entre {p150} e {p300}: Tagima, Strinberg, Squier e Yamaha Pacifica são modelos muito comuns para iniciantes."),
              ("Preciso de amplificador para tocar guitarra?", "Sim: sem amplificador a guitarra quase não soa. Para começar, um cubo pequeno de estudo já basta."),
              ("Vale a pena comprar um kit de guitarra?", "Se você está começando do zero, sim: guitarra, cubo e acessórios saem mais baratos do que separados.")]},
    {"slug": "violao-nylon-ou-aco", "title": "Violão de nylon ou de aço: qual escolher",
     "desc": "Diferenças entre violão de nylon e de aço, qual escolher para começar, tamanhos para crianças e modelos com o preço de hoje.",
     "body": """<section class="hub-sec guia">
<h2>A diferença está nas cordas</h2>
<p>O <strong>violão de nylon</strong> tem cordas macias, que não machucam os dedos, e um som quente: é o da MPB, da bossa nova e do clássico. O <strong>violão de aço</strong> soa mais brilhante e forte, ótimo para pop, rock, sertanejo e folk, mas no começo exige mais dos dedos.</p>
<p>Para crianças ou para quem nunca tocou, o nylon é o mais confortável. Se você quer tocar sertanejo, pop ou rock, pode começar direto no aço.</p>
<h2>Tamanhos e elétrico</h2>
<p>Há violões menores (3/4 e 1/2) para crianças. O <strong>violão elétrico</strong> (eletroacústico) tem captação para ligar no amplificador ou na caixa de som.</p>
<h2>Quanto gastar</h2>
<p>Há bons violões a partir de uns <strong>{p100}–{p200}</strong> (Giannini, Michael, Tagima, Yamaha…). No guitle comparamos o preço em {shops} lojas todos os dias.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Violões de nylon abaixo de {p200} que mais lojas vendem (preços de hoje)"),
               ("acustica", 300, 8, 3, True, "Violões de aço abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Violão de nylon ou de aço: qual é melhor para começar?", "O de nylon é mais confortável para começar; o de aço é melhor se você quer tocar sertanejo, pop ou rock."),
              ("Posso colocar cordas de aço em um violão de nylon?", "Não: o violão de nylon não aguenta a tensão das cordas de aço e pode empenar o braço ou soltar o cavalete.")]},
    {"slug": "primeiro-contrabaixo", "title": "Como escolher seu primeiro contrabaixo",
     "desc": "4 ou 5 cordas, Precision ou Jazz Bass e quanto gastar no seu primeiro baixo, com os mais vendidos abaixo de {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 ou 5 cordas</h2>
<p>Para começar, um baixo de <strong>4 cordas</strong>: é o padrão em quase todos os estilos. O de <strong>5 cordas</strong> acrescenta uma corda grave, muito usada no gospel, no metal e no funk, mas tem o braço mais largo.</p>
<ul>
<li><strong>Tipo Precision (P):</strong> som grave e redondo, simples e versátil.</li>
<li><strong>Tipo Jazz Bass (J):</strong> dois captadores e braço mais fino, com som mais definido.</li>
</ul>
<p>Entre <strong>{p200} e {p400}</strong> há baixos muito bons para começar. O baixo precisa de um cubo de baixo: o de guitarra pode estragar com os graves.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Baixos abaixo de {p400} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Qual baixo comprar para começar?", "Um baixo de 4 cordas tipo Precision ou Jazz Bass entre {p200} e {p400}."),
              ("Posso ligar o baixo no cubo de guitarra?", "Não é recomendado: os graves podem danificar o alto-falante. Use um cubo de baixo.")]},
    {"slug": "primeiro-cubo-guitarra", "title": "Qual cubo de guitarra comprar para começar",
     "desc": "Quantos watts, digital ou valvulado e quanto gastar no seu primeiro amplificador, com os mais vendidos abaixo de {p300}.",
     "body": """<section class="hub-sec guia">
<h2>Para casa, pouco basta</h2>
<p>Para estudar em casa, um cubo de <strong>10 a 30 watts</strong> é suficiente; o importante é soar bem em volume baixo e ter <strong>saída de fone</strong>.</p>
<ul>
<li><strong>Digital (modelador):</strong> imita vários amplificadores e já vem com efeitos: o mais prático para começar.</li>
<li><strong>Valvulado:</strong> o som clássico do rock e do blues, mais caro e pensado para tocar alto.</li>
</ul>
<p>Entre <strong>{p100} e {p300}</strong> há cubos de estudo muito completos.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amplificadores abaixo de {p300} que mais lojas vendem (preços de hoje)")],
     "faqs": [("Qual cubo de guitarra comprar para casa?", "Um de 10 a 30 watts com saída de fone; um digital é o mais prático para começar.")]},
]
