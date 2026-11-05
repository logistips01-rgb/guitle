"""Guides in English (guitle.com/uk/guias/, /ie/)."""
MORE, FAQ, GUIDES_WORD = "See all", "Frequently asked questions", "Guides"
INDEX_TITLE = "Guitar buying guides"
INDEX_DESC = "Guides to choosing an electric, classical or acoustic guitar, a bass and an amp, with real models and today's prices."
COURSE_URL, COURSE_TITLE = "course/", "Free course: your first guitar"
COURSE_DESC = "Five lessons from scratch: posture, chords, rhythm, scales and two songs, with a metronome."

GUIDES = [
    {"slug": "first-electric-guitar", "title": "How to choose your first electric guitar",
     "desc": "Which shape, which pickups and how much to spend on your first electric guitar, with the best sellers under {p300} and today's price in every shop.",
     "body": """<section class="hub-sec guia">
<h2>Which shape</h2>
<ul>
<li><strong>Stratocaster style (ST):</strong> the most versatile and comfortable, for pop, rock, blues and funk. If in doubt, start here.</li>
<li><strong>Telecaster style (T):</strong> simpler, with a bright, direct sound, a favourite in rock and country.</li>
<li><strong>Single cut (Les Paul style):</strong> a thicker sound with more sustain, great for rock and blues. Usually heavier.</li>
<li><strong>Superstrat:</strong> thin neck and hot pickups, built for hard rock and metal.</li>
</ul>
<h2>Pickups: single coils or humbuckers</h2>
<p><strong>Single coils</strong> sound clear and bright; <strong>humbuckers</strong> sound fatter and hum less with distortion. An <strong>HSS</strong> layout gives you both and is the most versatile choice for a beginner.</p>
<h2>How much to spend</h2>
<p>Between <strong>{p150} and {p300}</strong> you'll find guitars that sound good and last for years: Yamaha Pacifica, Squier, Ibanez GIO, Epiphone or Harley Benton, among others. An electric needs an <strong>amp</strong> (or a small headphone amp); if you're starting from scratch, a starter pack is often cheaper.</p>
<p>The same model can vary by tens of pounds between shops. guitle compares the price in {shops} shops every day and keeps its price history.</p>
</section>""",
     "grids": [("electrica", 300, 12, 3, True, "Electric guitars under {p300} sold by the most shops (today's prices)")],
     "faqs": [("Which electric guitar should a beginner buy?", "A Stratocaster-style guitar with HSS pickups between {p150} and {p300}: Yamaha Pacifica, Squier and Ibanez GIO are very common first guitars."),
              ("Do I need an amp to play electric guitar?", "Yes: without an amp you'll barely hear it. A small practice amp or a headphone amp is enough to start."),
              ("Is an electric guitar starter pack worth it?", "If you're starting from scratch, yes: guitar, amp and accessories cost less than buying them separately.")]},
    {"slug": "classical-or-acoustic-guitar", "title": "Classical or acoustic guitar: which to choose",
     "desc": "The difference between classical and acoustic guitars, which to choose as a beginner, children's sizes and models with today's prices.",
     "body": """<section class="hub-sec guia">
<h2>It's all in the strings</h2>
<p>A <strong>classical</strong> guitar has <strong>nylon</strong> strings: soft on the fingers, with a warm tone and a wider neck. An <strong>acoustic</strong> has <strong>steel</strong> strings: brighter and louder, but harder on the fingers at first.</p>
<ul>
<li><strong>Classical:</strong> classical music, flamenco, bossa nova, and for children or lessons with a teacher.</li>
<li><strong>Acoustic:</strong> pop, rock, folk and accompanying singing.</li>
</ul>
<h2>Sizes</h2>
<p>Classical guitars come in <strong>4/4</strong> for adults, <strong>3/4</strong> for children of about 8 to 11 and <strong>1/2</strong> for younger ones. An <strong>electro-acoustic</strong> has a preamp so you can plug it into an amp.</p>
<h2>How much to spend</h2>
<p>Good classicals start around <strong>{p100}–{p200}</strong> and acoustics around <strong>{p150}–{p300}</strong>. A solid top sounds better and improves with age. guitle compares the price in {shops} shops every day.</p>
</section>""",
     "grids": [("clasica", 200, 8, 3, True, "Classical guitars under {p200} sold by the most shops (today's prices)"),
               ("acustica", 300, 8, 3, True, "Acoustic guitars under {p300} sold by the most shops (today's prices)")],
     "faqs": [("Is a classical or an acoustic guitar better for beginners?", "Classical is more comfortable thanks to the nylon strings; acoustic is better if you want to play pop, rock or folk."),
              ("What size guitar does a child need?", "Roughly 1/2 up to 7-8 years old, 3/4 from 8 to 11 and 4/4 from 12."),
              ("Can I put steel strings on a classical guitar?", "No: a classical guitar isn't built for that tension and the neck or bridge can be damaged.")]},
    {"slug": "first-bass-guitar", "title": "How to choose your first bass guitar",
     "desc": "4 or 5 strings, Precision or Jazz Bass and how much to spend on your first bass, with the best sellers under {p400}.",
     "body": """<section class="hub-sec guia">
<h2>4 or 5 strings</h2>
<p>Start with a <strong>4-string</strong> bass: it's the standard in almost every style. A <strong>5-string</strong> adds a low string, popular in metal and modern funk, but has a wider neck.</p>
<ul>
<li><strong>Precision style (P):</strong> round, punchy tone, simple and effective.</li>
<li><strong>Jazz Bass style (J):</strong> two pickups and a slimmer neck, with a more defined tone.</li>
<li><strong>Short scale:</strong> frets closer together, more comfortable for small hands.</li>
</ul>
<p>Between <strong>{p200} and {p400}</strong> there are very good basses to start on. A bass needs a bass amp: the low end can damage a guitar amp.</p>
</section>""",
     "grids": [("bajo", 400, 12, 3, True, "Basses under {p400} sold by the most shops (today's prices)")],
     "faqs": [("Which bass should a beginner buy?", "A 4-string Precision, Jazz Bass or PJ style bass between {p200} and {p400}."),
              ("Can I plug a bass into a guitar amp?", "It's not recommended: the low frequencies can damage the speaker. You need a bass amp.")]},
    {"slug": "first-guitar-amp", "title": "Which guitar amp to buy as a beginner",
     "desc": "How many watts, modelling or valve and how much to spend on your first amp, with the best sellers under {p300}.",
     "body": """<section class="hub-sec guia">
<h2>At home, a little goes a long way</h2>
<p>For practising at home, a <strong>10 to 30 watt</strong> amp is plenty; what matters is that it sounds good at low volume and has a <strong>headphone output</strong>.</p>
<ul>
<li><strong>Modelling (digital):</strong> imitates many amps and has built-in effects: the most practical way to start (Boss Katana, Fender Mustang, Line 6, Blackstar…).</li>
<li><strong>Valve:</strong> the classic rock and blues sound, pricier and made to be played loud.</li>
</ul>
<p>Between <strong>{p100} and {p300}</strong> there are very complete practice amps.</p>
</section>""",
     "grids": [("ampli", 300, 12, 3, False, "Amps under {p300} sold by the most shops (today's prices)")],
     "faqs": [("Which guitar amp is best for home?", "A 10 to 30 watt amp with a headphone output; a digital modelling amp is the most practical to start with.")]},
    {"slug": "guitar-starter-packs", "title": "Guitar starter packs: when are they worth it",
     "desc": "What a guitar starter pack includes, when it beats buying separately, and the best-selling packs with today's prices.",
     "body": """<section class="hub-sec guia">
<h2>What's in a pack</h2>
<p>An electric guitar pack usually includes a <strong>guitar, small amp, gig bag, cable, strap, picks and tuner</strong>. It's <strong>worth it</strong> if you're starting from scratch; <strong>less so</strong> if you already have an amp or want a specific guitar. Look mostly at the guitar: it's what lasts.</p>
</section>""",
     "grids": [("pack", 400, 12, 2, False, "Packs under {p400} sold by the most shops (today's prices)")],
     "faqs": [("Is a guitar starter pack worth it for a beginner?", "Yes if you're starting from scratch: it's cheaper than buying each piece separately.")]},
]
