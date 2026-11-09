"""Publicación diaria en las cuentas de Instagram de otros países (@guitle.br, @guitle.fr, @guitle.it…), en su idioma,
con su catálogo, sus tiendas y su moneda. Cada día: un post (chollo o top 5, alternando), 3 stories de chollos y un
Reel de chollos por categoría con música libre de derechos y el crédito del autor (CLAUDE.md).

Mismas plantillas que España (brand/social.js y brand/reel.js), con los textos y la moneda del país en plan.json.
Cada cuenta publica con su token (variable de entorno del país en social/cuentas.json).

Por la tarde (--tarde), dos Reels más con su música: la cuenta atrás del Black Friday («apunta este precio») y uno sobre
guitle (qué es, misma guitarra a distinto precio, descuentos inflados, histórico de precios), rotando de tema cada día.
Así cada cuenta publica 3 Reels al día, como @guitle.es.

Uso:
    python -m scraper.paises fr it                    # genera social/<fecha>/<país>/ sin publicar
    python -m scraper.paises fr it --publish          # genera, sube a la rama actual y publica (mediodía)
    python -m scraper.paises fr it --tarde --publish  # Reels de la tarde
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from . import instagram as ig
from . import musica_libre as musica
from .catalog import load
from .fetch import Fetcher

ROOT = ig.ROOT
MESES = {
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
}

# Configuración por país: catálogos, moneda, franja de precios, rangos de los tops y textos.
PAISES = {
    "br": {
        "lang": "pt", "web": "guitle.com/br", "logo": "br/", "temas": musica.TEMAS_BR,
        "catalogs": {"electrica": "data/catalog/br/guitarras.json", "acustica": "data/catalog/br/violoes.json",
                     "clasica": "data/catalog/br/violoes-nylon.json"},
        "money": {"locale": "pt-BR", "prefix": "R$ ", "suffix": ""}, "rango": (800, 4500),
        "tops": [("electrica", 800, 2000), ("acustica", 500, 1500), ("electrica", 2000, 4500), ("clasica", 400, 1500)],
        "kinds": {"electrica": "Elétrica", "acustica": "Violão", "clasica": "Violão de nylon"},
        "plural": {"electrica": "guitarras elétricas", "acustica": "violões", "clasica": "violões de nylon"},
        "hashtags": {"electrica": "#guitarraeletrica", "acustica": "#violao", "clasica": "#violaodenylon"},
        "base_tags": "#guitarra #guitarrista #promoção #ofertas",
        "t": {"cholloHoy": "Promoção do dia", "cholloDia": "Promoção do dia", "en": "em", "precioDel": "Preço de",
              "comparadoEn": "comparada em", "tiendas": "lojas", "enlaceBio": "Link na bio",
              "masVendidas": "As mais vendidas nas lojas, com o melhor preço de hoje.", "desliza": "Arraste →",
              "laVenden": "Vendida em", "conCual": "Com qual você fica?",
              "cuentanos": "Conta pra gente nos comentários e salve este post pra quando for comprar.",
              "comparaEn": "Compare preços em", "comparaAntes": "Compare antes de comprar",
              "siguenos": "Siga a gente pra mais promoções"},
        "menos": "{x} a menos que em qualquer outra loja", "hook": "Promoções de hoje",
        "rango_txt": ("até {hi}", "de {lo} a {hi}"),
        "cap_chollo": ("🔥 Promoção do dia: {name}\n💶 {price} em {store}, comparada em {n} lojas.\n📉 {why}.\n\n"
                       "🔎 Compare o preço em {web} (link na bio).\nPreço de {fecha}; pode mudar.\n\n{tags}"),
        "cap_top": ("🎸 {title}: as mais vendidas nas lojas, com o melhor preço de hoje 👇\n\n{lines}\n\n"
                    "Com qual você fica? Conta pra gente nos comentários 💬\n🔎 Compare preços em {web} (link na bio). Preços de {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Promoções de hoje 👇\n\n{lines}\n\nQual você levaria? 💬\n"
                     "🔎 Compare preços em {web} (link na bio). Preços de {fecha}; podem mudar.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} em {store}", "linea_reel": "{icon} {kind}: {name} por {price} em {store} ({why})",
        "fecha": lambda d: f"{d.day} de {MESES['pt'][d.month - 1]}",
    },
    "fr": {
        "lang": "fr", "web": "guitle.com/fr", "logo": "fr/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/fr/electriques.json", "acustica": "data/catalog/fr/folk.json",
                     "clasica": "data/catalog/fr/classiques.json"},
        "money": {"locale": "fr-FR", "prefix": "", "suffix": " €"}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "Électrique", "acustica": "Folk", "clasica": "Classique"},
        "plural": {"electrica": "guitares électriques", "acustica": "guitares folk", "clasica": "guitares classiques"},
        "hashtags": {"electrica": "#guitareelectrique", "acustica": "#guitarefolk", "clasica": "#guitareclassique"},
        "base_tags": "#guitare #guitariste #bonplan #promo",
        "t": {"cholloHoy": "Bon plan du jour", "cholloDia": "Bon plan du jour", "en": "chez", "precioDel": "Prix du",
              "comparadoEn": "comparée dans", "tiendas": "magasins", "enlaceBio": "Lien en bio",
              "masVendidas": "Les plus vendues en magasin, avec leur meilleur prix du jour.", "desliza": "Fais glisser →",
              "laVenden": "Vendue dans", "conCual": "Laquelle tu choisis ?",
              "cuentanos": "Dis-le-nous en commentaire et garde ce post pour ton prochain achat.",
              "comparaEn": "Compare les prix sur", "comparaAntes": "Compare avant d’acheter",
              "siguenos": "Abonne-toi pour plus de bons plans"},
        "menos": "{x} de moins que dans les autres magasins", "hook": "Bons plans du jour",
        "rango_txt": ("à moins de {hi}", "de {lo} à {hi}"),
        "cap_chollo": ("🔥 Bon plan du jour : {name}\n💶 {price} chez {store}, comparée dans {n} magasins.\n📉 {why}.\n\n"
                       "🔎 Compare son prix sur {web} (lien en bio).\nPrix du {fecha} ; il peut changer.\n\n{tags}"),
        "cap_top": ("🎸 {title} : les plus vendues en magasin, avec leur meilleur prix du jour 👇\n\n{lines}\n\n"
                    "Laquelle tu choisis ? Dis-le-nous en commentaire 💬\n🔎 Compare les prix sur {web} (lien en bio). Prix du {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Bons plans du jour 👇\n\n{lines}\n\nTu prendrais laquelle ? 💬\n"
                     "🔎 Compare les prix sur {web} (lien en bio). Prix du {fecha} ; ils peuvent changer.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name} : {price} chez {store}", "linea_reel": "{icon} {kind} : {name} à {price} chez {store} ({why})",
        "fecha": lambda d: f"{'1er' if d.day == 1 else d.day} {MESES['fr'][d.month - 1]}",
    },
    "it": {
        "lang": "it", "web": "guitle.com/it", "logo": "it/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/it/elettriche.json", "acustica": "data/catalog/it/acustiche.json",
                     "clasica": "data/catalog/it/classiche.json"},
        "money": {"locale": "it-IT", "prefix": "", "suffix": " €"}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "Elettrica", "acustica": "Acustica", "clasica": "Classica"},
        "plural": {"electrica": "chitarre elettriche", "acustica": "chitarre acustiche", "clasica": "chitarre classiche"},
        "hashtags": {"electrica": "#chitarraelettrica", "acustica": "#chitarraacustica", "clasica": "#chitarraclassica"},
        "base_tags": "#chitarra #chitarrista #offerte #sconti",
        "t": {"cholloHoy": "Offerta del giorno", "cholloDia": "Offerta del giorno", "en": "da", "precioDel": "Prezzo del",
              "comparadoEn": "confrontata in", "tiendas": "negozi", "enlaceBio": "Link in bio",
              "masVendidas": "Le più vendute nei negozi, con il miglior prezzo di oggi.", "desliza": "Scorri →",
              "laVenden": "Venduta in", "conCual": "Quale scegli?",
              "cuentanos": "Diccelo nei commenti e salva questo post per quando comprerai.",
              "comparaEn": "Confronta i prezzi su", "comparaAntes": "Confronta prima di comprare",
              "siguenos": "Seguici per altre offerte"},
        "menos": "{x} in meno che negli altri negozi", "hook": "Offerte di oggi",
        "rango_txt": ("sotto i {hi}", "da {lo} a {hi}"),
        "cap_chollo": ("🔥 Offerta del giorno: {name}\n💶 {price} da {store}, confrontata in {n} negozi.\n📉 {why}.\n\n"
                       "🔎 Confronta il prezzo su {web} (link in bio).\nPrezzo del {fecha}; può cambiare.\n\n{tags}"),
        "cap_top": ("🎸 {title}: le più vendute nei negozi, con il miglior prezzo di oggi 👇\n\n{lines}\n\n"
                    "Quale scegli? Diccelo nei commenti 💬\n🔎 Confronta i prezzi su {web} (link in bio). Prezzi del {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Offerte di oggi 👇\n\n{lines}\n\nQuale prenderesti? 💬\n"
                     "🔎 Confronta i prezzi su {web} (link in bio). Prezzi del {fecha}; possono cambiare.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} da {store}", "linea_reel": "{icon} {kind}: {name} a {price} da {store} ({why})",
        "fecha": lambda d: f"{d.day} {MESES['it'][d.month - 1]}",
    },
    "de": {
        "lang": "de", "web": "guitle.com/de", "logo": "de/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/de/e-gitarren.json", "acustica": "data/catalog/de/westerngitarren.json",
                     "clasica": "data/catalog/de/konzertgitarren.json"},
        "money": {"locale": "de-DE", "prefix": "", "suffix": " €"}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "E-Gitarre", "acustica": "Westerngitarre", "clasica": "Konzertgitarre"},
        "plural": {"electrica": "E-Gitarren", "acustica": "Westerngitarren", "clasica": "Konzertgitarren"},
        "hashtags": {"electrica": "#egitarre", "acustica": "#westerngitarre", "clasica": "#konzertgitarre"},
        "base_tags": "#gitarre #gitarrist #angebote #deals",
        "t": {"cholloHoy": "Deal des Tages", "cholloDia": "Deal des Tages", "en": "bei", "precioDel": "Preis vom",
              "comparadoEn": "verglichen in", "tiendas": "Shops", "enlaceBio": "Link in der Bio",
              "masVendidas": "Die meistverkauften in den Shops, mit dem besten Preis von heute.", "desliza": "Wischen →",
              "laVenden": "Erhältlich in", "conCual": "Welche nimmst du?",
              "cuentanos": "Schreib es in die Kommentare und speichere den Post für deinen nächsten Kauf.",
              "comparaEn": "Preise vergleichen auf", "comparaAntes": "Erst vergleichen, dann kaufen",
              "siguenos": "Folge uns für mehr Deals"},
        "menos": "{x} günstiger als in allen anderen Shops", "hook": "Deals von heute",
        "rango_txt": ("unter {hi}", "von {lo} bis {hi}"),
        "cap_chollo": ("🔥 Deal des Tages: {name}\n💶 {price} bei {store}, verglichen in {n} Shops.\n📉 {why}.\n\n"
                       "🔎 Vergleiche den Preis auf {web} (Link in der Bio).\nPreis vom {fecha}; kann sich ändern.\n\n{tags}"),
        "cap_top": ("🎸 {title}: die meistverkauften in den Shops, mit dem besten Preis von heute 👇\n\n{lines}\n\n"
                    "Welche nimmst du? Schreib es in die Kommentare 💬\n🔎 Preise vergleichen auf {web} (Link in der Bio). Preise vom {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Deals von heute 👇\n\n{lines}\n\nWelche würdest du nehmen? 💬\n"
                     "🔎 Preise vergleichen auf {web} (Link in der Bio). Preise vom {fecha}; können sich ändern.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} bei {store}", "linea_reel": "{icon} {kind}: {name} für {price} bei {store} ({why})",
        "fecha": lambda d: f"{d.day}. {MESES['de'][d.month - 1]}",
    },
    "uk": {
        "lang": "en", "web": "guitle.com/uk", "logo": "uk/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/uk/electric.json", "acustica": "data/catalog/uk/acoustic.json",
                     "clasica": "data/catalog/uk/classical.json"},
        "money": {"locale": "en-GB", "prefix": "£", "suffix": ""}, "rango": (130, 650),
        "tops": [("electrica", 130, 250), ("acustica", 130, 250), ("electrica", 250, 450), ("clasica", 130, 250),
                 ("electrica", 450, 650), ("acustica", 250, 650), ("clasica", 250, 650)],
        "kinds": {"electrica": "Electric", "acustica": "Acoustic", "clasica": "Classical"},
        "plural": {"electrica": "electric guitars", "acustica": "acoustic guitars", "clasica": "classical guitars"},
        "hashtags": {"electrica": "#electricguitar", "acustica": "#acousticguitar", "clasica": "#classicalguitar"},
        "base_tags": "#guitar #guitarist #guitardeals #ukguitar",
        "t": {"cholloHoy": "Deal of the day", "cholloDia": "Deal of the day", "en": "at", "precioDel": "Price on",
              "comparadoEn": "compared across", "tiendas": "shops", "enlaceBio": "Link in bio",
              "masVendidas": "The best sellers in UK shops, with today’s best price.", "desliza": "Swipe →",
              "laVenden": "Sold in", "conCual": "Which one would you pick?",
              "cuentanos": "Tell us in the comments and save this post for your next purchase.",
              "comparaEn": "Compare prices on", "comparaAntes": "Compare before you buy",
              "siguenos": "Follow us for more deals"},
        "menos": "{x} less than any other shop", "hook": "Today’s deals",
        "rango_txt": ("under {hi}", "from {lo} to {hi}"),
        "cap_chollo": ("🔥 Deal of the day: {name}\n💷 {price} at {store}, compared across {n} shops.\n📉 {why}.\n\n"
                       "🔎 Compare its price on {web} (link in bio).\nPrice on {fecha}; it may change.\n\n{tags}"),
        "cap_top": ("🎸 {title}: the best sellers in UK shops, with today’s best price 👇\n\n{lines}\n\n"
                    "Which one would you pick? Tell us in the comments 💬\n🔎 Compare prices on {web} (link in bio). Prices on {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Today’s deals 👇\n\n{lines}\n\nWhich one would you get? 💬\n"
                     "🔎 Compare prices on {web} (link in bio). Prices on {fecha}; they may change.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} at {store}", "linea_reel": "{icon} {kind}: {name} for {price} at {store} ({why})",
        "fecha": lambda d: f"{d.day} {MESES['en'][d.month - 1]}",
    },
    "pt": {
        "lang": "pt", "txt": "pt-pt", "web": "guitle.com/pt", "logo": "pt/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/pt/eletricas.json", "acustica": "data/catalog/pt/acusticas.json",
                     "clasica": "data/catalog/pt/classicas.json"},
        "money": {"locale": "pt-PT", "prefix": "", "suffix": " €"}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "Elétrica", "acustica": "Acústica", "clasica": "Clássica"},
        "plural": {"electrica": "guitarras elétricas", "acustica": "guitarras acústicas", "clasica": "guitarras clássicas"},
        "hashtags": {"electrica": "#guitarraeletrica", "acustica": "#guitarraacustica", "clasica": "#guitarraclassica"},
        "base_tags": "#guitarra #guitarrista #promoção #portugal",
        "t": {"cholloHoy": "Promoção do dia", "cholloDia": "Promoção do dia", "en": "na", "precioDel": "Preço de",
              "comparadoEn": "comparada em", "tiendas": "lojas", "enlaceBio": "Link na bio",
              "masVendidas": "As mais vendidas nas lojas, com o melhor preço de hoje.", "desliza": "Desliza →",
              "laVenden": "À venda em", "conCual": "Com qual ficas?",
              "cuentanos": "Diz-nos nos comentários e guarda este post para quando fores comprar.",
              "comparaEn": "Compara preços em", "comparaAntes": "Compara antes de comprar",
              "siguenos": "Segue-nos para mais promoções"},
        "menos": "{x} a menos do que em qualquer outra loja", "hook": "Promoções de hoje",
        "rango_txt": ("até {hi}", "de {lo} a {hi}"),
        "cap_chollo": ("🔥 Promoção do dia: {name}\n💶 {price} na {store}, comparada em {n} lojas.\n📉 {why}.\n\n"
                       "🔎 Compara o preço em {web} (link na bio).\nPreço de {fecha}; pode mudar.\n\n{tags}"),
        "cap_top": ("🎸 {title}: as mais vendidas nas lojas, com o melhor preço de hoje 👇\n\n{lines}\n\n"
                    "Com qual ficas? Diz-nos nos comentários 💬\n🔎 Compara preços em {web} (link na bio). Preços de {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Promoções de hoje 👇\n\n{lines}\n\nQual levavas? 💬\n"
                     "🔎 Compara preços em {web} (link na bio). Preços de {fecha}; podem mudar.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} na {store}", "linea_reel": "{icon} {kind}: {name} por {price} na {store} ({why})",
        "fecha": lambda d: f"{d.day} de {MESES['pt'][d.month - 1]}",
    },
    "ie": {
        "lang": "en", "txt": "en-ie", "web": "guitle.com/ie", "logo": "ie/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/ie/electric.json", "acustica": "data/catalog/ie/acoustic.json",
                     "clasica": "data/catalog/ie/classical.json"},
        "money": {"locale": "en-IE", "prefix": "€", "suffix": ""}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "Electric", "acustica": "Acoustic", "clasica": "Classical"},
        "plural": {"electrica": "electric guitars", "acustica": "acoustic guitars", "clasica": "classical guitars"},
        "hashtags": {"electrica": "#electricguitar", "acustica": "#acousticguitar", "clasica": "#classicalguitar"},
        "base_tags": "#guitar #guitarist #guitardeals #ireland",
        "t": {"cholloHoy": "Deal of the day", "cholloDia": "Deal of the day", "en": "at", "precioDel": "Price on",
              "comparadoEn": "compared across", "tiendas": "shops", "enlaceBio": "Link in bio",
              "masVendidas": "The best sellers in Irish shops, with today’s best price.", "desliza": "Swipe →",
              "laVenden": "Sold in", "conCual": "Which one would you pick?",
              "cuentanos": "Tell us in the comments and save this post for your next purchase.",
              "comparaEn": "Compare prices on", "comparaAntes": "Compare before you buy",
              "siguenos": "Follow us for more deals"},
        "menos": "{x} less than any other shop", "hook": "Today’s deals",
        "rango_txt": ("under {hi}", "from {lo} to {hi}"),
        "cap_chollo": ("🔥 Deal of the day: {name}\n💶 {price} at {store}, compared across {n} shops.\n📉 {why}.\n\n"
                       "🔎 Compare its price on {web} (link in bio).\nPrice on {fecha}; it may change.\n\n{tags}"),
        "cap_top": ("🎸 {title}: the best sellers in Irish shops, with today’s best price 👇\n\n{lines}\n\n"
                    "Which one would you pick? Tell us in the comments 💬\n🔎 Compare prices on {web} (link in bio). Prices on {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Today’s deals 👇\n\n{lines}\n\nWhich one would you get? 💬\n"
                     "🔎 Compare prices on {web} (link in bio). Prices on {fecha}; they may change.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} at {store}", "linea_reel": "{icon} {kind}: {name} for {price} at {store} ({why})",
        "fecha": lambda d: f"{d.day} {MESES['en'][d.month - 1]}",
    },
    "nl": {
        "lang": "nl", "web": "guitle.com/nl", "logo": "nl/", "temas": musica.TEMAS,
        "catalogs": {"electrica": "data/catalog/nl/elektrische-gitaren.json", "acustica": "data/catalog/nl/akoestische-gitaren.json",
                     "clasica": "data/catalog/nl/klassieke-gitaren.json"},
        "money": {"locale": "nl-NL", "prefix": "€ ", "suffix": ""}, "rango": (150, 750),
        "tops": [("electrica", 150, 300), ("acustica", 150, 300), ("electrica", 300, 500), ("clasica", 150, 300),
                 ("electrica", 500, 750), ("acustica", 300, 750), ("clasica", 300, 750)],
        "kinds": {"electrica": "Elektrisch", "acustica": "Akoestisch", "clasica": "Klassiek"},
        "plural": {"electrica": "elektrische gitaren", "acustica": "akoestische gitaren", "clasica": "klassieke gitaren"},
        "hashtags": {"electrica": "#elektrischegitaar", "acustica": "#akoestischegitaar", "clasica": "#klassiekegitaar"},
        "base_tags": "#gitaar #gitarist #aanbieding #deals",
        "t": {"cholloHoy": "Deal van de dag", "cholloDia": "Deal van de dag", "en": "bij", "precioDel": "Prijs van",
              "comparadoEn": "vergeleken in", "tiendas": "winkels", "enlaceBio": "Link in bio",
              "masVendidas": "De bestsellers in de winkels, met de beste prijs van vandaag.", "desliza": "Swipe →",
              "laVenden": "Te koop in", "conCual": "Welke kies jij?",
              "cuentanos": "Laat het weten in de reacties en bewaar deze post voor als je gaat kopen.",
              "comparaEn": "Vergelijk prijzen op", "comparaAntes": "Vergelijk voor je koopt",
              "siguenos": "Volg ons voor meer deals"},
        "menos": "{x} goedkoper dan in elke andere winkel", "hook": "Deals van vandaag",
        "rango_txt": ("onder {hi}", "van {lo} tot {hi}"),
        "cap_chollo": ("🔥 Deal van de dag: {name}\n💶 {price} bij {store}, vergeleken in {n} winkels.\n📉 {why}.\n\n"
                       "🔎 Vergelijk de prijs op {web} (link in bio).\nPrijs van {fecha}; kan veranderen.\n\n{tags}"),
        "cap_top": ("🎸 {title}: de bestsellers in de winkels, met de beste prijs van vandaag 👇\n\n{lines}\n\n"
                    "Welke kies jij? Laat het weten in de reacties 💬\n🔎 Vergelijk prijzen op {web} (link in bio). Prijzen van {fecha}.\n\n{tags}"),
        "cap_reel": ("🔥 Deals van vandaag 👇\n\n{lines}\n\nWelke zou jij nemen? 💬\n"
                     "🔎 Vergelijk prijzen op {web} (link in bio). Prijzen van {fecha}; kunnen veranderen.\n\n{tags}"),
        "linea_top": "{i}️⃣ {name}: {price} bij {store}", "linea_reel": "{icon} {kind}: {name} voor {price} bij {store} ({why})",
        "fecha": lambda d: f"{d.day} {MESES['nl'][d.month - 1]}",
    },
}


# En los chollos y tops, la bio lleva a la página «Chollos de hoy» de la web (guitle.com/<país>/hoy/, scraper/hoy.py)
BIO_HOY = {"pt": "(todas as promoções de hoje no link da bio 👆)", "fr": "(tous les bons plans du jour via le lien en bio 👆)",
           "it": "(tutte le offerte di oggi nel link in bio 👆)", "de": "(alle Deals von heute über den Link in der Bio 👆)",
           "en": "(all today’s deals via the link in bio 👆)", "nl": "(alle deals van vandaag via de link in bio 👆)"}
for _cfg in PAISES.values():
    for _k in ("cap_chollo", "cap_top", "cap_reel"):
        _cfg[_k] = re.sub(r"\((?:link na bio|lien en bio|link in bio|Link in der Bio)\)", BIO_HOY[_cfg["lang"]], _cfg[_k])


def dinero(cfg):
    m = cfg["money"]
    sep = "." if m["locale"] in ("pt-BR", "it-IT", "de-DE") else " "
    def fmt(v):
        if m["locale"] == "en-GB":  # 1,234.50
            s = f"{v:,.2f}"
            return m["prefix"] + (s[:-3] if s.endswith(".00") else s) + m["suffix"]
        s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", sep)
        s = s[:-3] if s.endswith(",00") else s
        return m["prefix"] + s + m["suffix"]
    return fmt


def recientes(cc, user):
    """Nombres ya publicados en esa cuenta (textos de Instagram y planes de los últimos días) para no repetir."""
    txt = ig.recent_captions(user)
    for f in sorted((ig.OUT).glob(f"*/{cc}/plan.json"))[-10:] + sorted(ig.OUT.glob(f"*/{cc}/reel-*/plan.json"))[-10:]:
        d = load(f, {})
        post = d.get("post") or {}
        txt += "\n" + "\n".join(p["name"] for p in d.get("stories", []) + post.get("picks", []))
        if post.get("deal"):
            txt += "\n" + post["deal"]["name"]
    return txt


def plan_pais(cc, day, recent):
    cfg = PAISES[cc]
    money = dinero(cfg)
    folder = ig.OUT / day.isoformat() / cc
    folder.mkdir(parents=True, exist_ok=True)
    cats = {k: ROOT / v for k, v in cfg["catalogs"].items()}
    lo, hi = cfg["rango"]
    prods = ig.products(lo, hi, catalogs=cats)
    fetcher = Fetcher(delay=(0.5, 1.0))
    deals = ig.rank_deals(prods, recent, menos=lambda x: cfg["menos"].format(x=money(x)))
    if len(deals) < 12:
        # Pocos chollos (p. ej. Italia): se completan con guitarras que hoy están más baratas en una tienda que en todas
        # las demás, con ese dato real como motivo
        ya = {p["slug"] for p in deals}
        extra = sorted((p for p in prods if p["slug"] not in ya and p["name"] not in recent and p["next"] > p["price"]
                        and p["max"] <= 1.45 * p["price"]), key=lambda p: -(p["next"] - p["price"]) / p["price"])
        deals += [{**p, "why": cfg["menos"].format(x=money(p["next"] - p["price"]))} for p in extra[:20]]
    stories = ig.with_photos(deals, ig.STORIES + 1, fetcher, folder, "chollo-")
    fecha = cfg["fecha"](day)
    n = day.toordinal()
    if n % 2 == 0 and stories:
        d = stories[0]
        post = {"type": "chollo", "deal": d, "caption": cfg["cap_chollo"].format(
            name=d["name"], price=money(d["price"]), store=d["store"], n=d["stores"], why=d["why"], web=cfg["web"], fecha=fecha,
            tags=f"{cfg['base_tags']} {cfg['hashtags'][d['kind']]} {ig.tag(d['brand'])}")}
        stories = stories[1:]
    else:
        kind, tlo, thi = cfg["tops"][(n // 2) % len(cfg["tops"])]
        picks = sorted(ig.with_photos(ig.top_of(prods, kind, tlo, thi, recent), 5, fetcher, folder, "top-"), key=lambda p: p["price"])
        rango = (cfg["rango_txt"][0] if tlo <= lo else cfg["rango_txt"][1]).format(lo=money(tlo), hi=money(thi))
        title = f"{len(picks)} {cfg['plural'][kind]} {rango}"
        lines = "\n".join(cfg["linea_top"].format(i=i, name=p["name"], price=money(p["price"]), store=p["store"])
                          for i, p in enumerate(picks, 1))
        post = {"type": "top", "title": title, "kind": kind, "picks": picks, "caption": cfg["cap_top"].format(
            title=title[0].upper() + title[1:], lines=lines, web=cfg["web"], fecha=fecha,
            tags=f"{cfg['base_tags']} {cfg['hashtags'][kind]} " + " ".join(dict.fromkeys(ig.tag(p["brand"]) for p in picks)))}
    t = {**cfg["t"], "web": cfg["web"], "kinds": cfg["kinds"]}
    data = {"date": day.isoformat(), "fecha": fecha, "post": post, "stories": stories[:ig.STORIES],
            "t": t, "money": cfg["money"], "logo": cfg["logo"]}
    (folder / "plan.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "social.js"), str(folder)], check=True, cwd=ROOT)

    reel_chollos(cc, day, folder, deals, prods, recent, post, stories, fetcher, fecha, t)
    return folder, data


def extras_baratas(cfg, prods, recent, ya):
    """Guitarras que hoy están más baratas en una tienda que en todas las demás (diferencia creíble), con ese dato real
    como motivo; sirven para completar cuando hay pocos chollos."""
    money = dinero(cfg)
    extra = sorted((p for p in prods if p["slug"] not in ya and p["name"] not in recent and p["next"] > p["price"]
                    and p["max"] <= 1.45 * p["price"]), key=lambda p: -(p["next"] - p["price"]) / p["price"])
    return [{**p, "why": cfg["menos"].format(x=money(p["next"] - p["price"]))} for p in extra]


def reel_chollos(cc, day, folder, deals, prods, recent, post, stories, fetcher, fecha, t):
    """Reel de chollos de mediodía: 2 eléctricas, 1 acústica y 1 clásica (sin repetir las del post ni las stories). Si no
    hay bastantes con foto revisada, se repiten las de las stories y, por último, vale cualquier tipo de guitarra (también
    las que hoy están más baratas en una tienda que en todas las demás), nunca la del post."""
    cfg = PAISES[cc]
    money = dinero(cfg)
    # Reel: 2 eléctricas, 1 acústica y 1 clásica (sin repetir las del post ni las stories)
    usados = {p["slug"] for p in stories} | {p["slug"] for p in post.get("picks", [])} | ({post["deal"]["slug"]} if post.get("deal") else set())
    sub = folder / "reel-1-chollos"
    sub.mkdir(parents=True, exist_ok=True)
    picks = []
    def elegir(evitar, huecos):
        for k in huecos:
            for p in deals:
                if p["kind"] == k and p["slug"] not in evitar and all(p["slug"] != q["slug"] and p["brand"] != q["brand"] for q in picks):
                    got = ig.with_photos([p], 1, fetcher, sub, f"g{len(picks)}-")
                    if got:
                        picks.append({**got[0], "label": cfg["kinds"][k]})
                        break
    elegir(usados, ["electrica", "electrica", "acustica", "clasica"])
    sin_post = {p["slug"] for p in post.get("picks", [])} | ({post["deal"]["slug"]} if post.get("deal") else set())
    if len(picks) < 3:  # pocos chollos ese día: se pueden repetir las guitarras de las stories, nunca la del post
        elegir(sin_post, ["electrica", "acustica", "electrica", "clasica"][: 4 - len(picks)])
    if len(picks) < 3:  # aún pocos (fotos sin revisar): cualquier tipo, ampliando con las más baratas que en otras tiendas
        deals = deals + extras_baratas(cfg, prods, recent, {p["slug"] for p in deals})
        for _ in range(4 - len(picks)):
            antes = len(picks)
            for k in ("electrica", "acustica", "clasica"):
                if len(picks) < 4:
                    elegir(sin_post, [k])
            if len(picks) == antes:
                break
    orden = {"electrica": 0, "acustica": 1, "clasica": 2}
    picks.sort(key=lambda p: orden[next(k for k, v in cfg["kinds"].items() if v == p["label"])])
    if len(picks) >= 3:
        icons = ["🎸", "⚡", "🪵", "🎼"]
        lines = "\n".join(cfg["linea_reel"].format(icon=icons[i], kind=p["label"], name=p["name"], price=money(p["price"]),
                                                   store=p["store"], why=(p["why"][0].lower() if p["why"][1:2].islower() else p["why"][0]) + p["why"][1:]) for i, p in enumerate(picks))
        caption = cfg["cap_reel"].format(lines=lines, web=cfg["web"], fecha=fecha,
                                         tags=f"{cfg['base_tags']} " + " ".join(dict.fromkeys(ig.tag(p["brand"]) for p in picks)))
        reel = {"fecha": fecha, "post": {"type": "top", "title": cfg["hook"].lower(), "hook": cfg["hook"], "picks": picks},
                "stories": [], "t": t, "money": cfg["money"], "logo": cfg["logo"]}
        (sub / "plan.json").write_text(json.dumps(reel, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        subprocess.run(["node", str(ROOT / "brand" / "reel.js"), str(sub)], check=True, cwd=ROOT)
        credito = musica.poner(sub / "reel.mp4", day.toordinal() + list(PAISES).index(cc), cfg["temas"])
        (sub / "texto.txt").write_text(f"{caption}\n\n{credito}\n", encoding="utf-8")


def rehacer_reel_chollos(cc, day, recent, token=None):
    """Si el Reel de chollos de mediodía no se generó (pocas fotos revisadas), lo rehace con el plan ya publicado
    (mismo post y stories) y, con token, lo publica solo a él."""
    folder = ig.OUT / day.isoformat() / cc
    hecho = load(folder / "published.json", {})
    if str(hecho.get("reel") or "").startswith("https://"):
        return "ya publicado"
    cfg = PAISES[cc]
    money = dinero(cfg)
    data = load(folder / "plan.json", {})
    lo, hi = cfg["rango"]
    prods = ig.products(lo, hi, catalogs={k: ROOT / v for k, v in cfg["catalogs"].items()})
    deals = ig.rank_deals(prods, recent, menos=lambda x: cfg["menos"].format(x=money(x)))
    sub = folder / "reel-1-chollos"
    for f in sub.glob("*"):
        f.unlink()
    reel_chollos(cc, day, folder, deals, prods, recent, data["post"], data["stories"], Fetcher(delay=(0.5, 1.0)),
                 data["fecha"], data["t"])
    if not (sub / "reel.mp4").exists():
        return "sin reel: pocas guitarras con foto revisada"
    if not token:
        return str(sub / "reel.mp4")
    ig.TOKEN = token
    try:
        user = ig.api("GET", "me", fields="user_id")["user_id"]
        rel = folder.relative_to(ROOT).as_posix()
        ig.git("add", rel)
        ig.git("commit", "-q", "-m", f"social: Reel de chollos {cc} {day.isoformat()}")
        branch = ig.git("rev-parse", "--abbrev-ref", "HEAD")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        base = f"{ig.REPO_RAW}/{ig.git('rev-parse', 'HEAD')}/{rel}/"
        for _ in range(20):
            if requests.head(base + "reel-1-chollos/reel.mp4", timeout=30).status_code == 200:
                break
            time.sleep(5)
        caption = (sub / "texto.txt").read_text(encoding="utf-8").strip()
        handles = ig.cuentas(ig.marcas_reel(sub))
        hecho["reel"] = ig.publish(user, ig.container_etiq(user, handles, tries=100, media_type="REELS",
                                   caption=ig.menciones(caption, handles), video_url=base + "reel-1-chollos/reel.mp4",
                                   share_to_feed="true"))
        (folder / "published.json").write_text(json.dumps(hecho, indent=1) + "\n", encoding="utf-8")
        ig.git("add", rel)
        ig.git("commit", "-q", "-m", f"social: publicado Reel de chollos {cc} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        return hecho["reel"]
    finally:
        ig.TOKEN = None


def publicar(cc, day, folder, data, token):
    """Sube la carpeta del día al repo y publica post, Reel y stories en la cuenta del país."""
    ig.TOKEN = token
    try:
        user = ig.api("GET", "me", fields="user_id")["user_id"]
        rel = folder.relative_to(ROOT).as_posix()
        ig.git("add", rel)
        ig.git("commit", "-q", "-m", f"social: publicación de Instagram {cc} {day.isoformat()}")
        branch = ig.git("rev-parse", "--abbrev-ref", "HEAD")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        base = f"{ig.REPO_RAW}/{ig.git('rev-parse', 'HEAD')}/{rel}/"
        for _ in range(20):
            if requests.head(base + "post-1.jpg", timeout=30).status_code == 200:
                break
            time.sleep(5)
        done = {"post": None, "reel": None, "stories": []}
        # Si una ejecución anterior se cortó a medias, no se repite lo que ya está publicado hoy
        hoy = [m for m in ig.api("GET", f"{user}/media", fields="caption,permalink,timestamp", limit=25)["data"]
               if m.get("timestamp", "")[:10] == day.isoformat()]
        ya = lambda caption: next((m["permalink"] for m in hoy if (m.get("caption") or "")[:60] == caption[:60]), None)
        # Solo cuentan las stories de hoy (las de ayer siguen activas 24 h)
        stories_activas = [x for x in ig.api("GET", f"{user}/stories", fields="id,timestamp").get("data", [])
                           if x.get("timestamp", "")[:10] == day.isoformat()]
        slides = sorted(p.name for p in folder.glob("post-*.jpg"))
        post = data["post"]
        caption = ig.menciones(post["caption"], ig.cuentas(ig.marcas_post(post)))
        if ya(post["caption"]):
            done["post"] = ya(post["caption"])
        elif len(slides) == 1:
            done["post"] = ig.publish(user, ig.container_etiq(user, ig.cuentas(ig.marcas_post(post, 0)), image_url=base + slides[0],
                                                              caption=caption))
        else:
            kids = [ig.container_etiq(user, ig.cuentas(ig.marcas_post(post, i)), image_url=base + s, is_carousel_item="true")
                    for i, s in enumerate(slides)]
            done["post"] = ig.publish(user, ig.container(user, media_type="CAROUSEL", children=",".join(kids), caption=caption))
        if (folder / "reel-1-chollos" / "reel.mp4").exists():
            caption = (folder / "reel-1-chollos" / "texto.txt").read_text(encoding="utf-8").strip()
            handles = ig.cuentas(ig.marcas_reel(folder / "reel-1-chollos"))
            done["reel"] = ya(caption) or ig.publish(user, ig.container_etiq(
                user, handles, tries=100, media_type="REELS", caption=ig.menciones(caption, handles),
                video_url=base + "reel-1-chollos/reel.mp4", share_to_feed="true"))
        for i, s in enumerate(sorted(folder.glob("story-*.jpg"))):
            if cc in SUAVE:  # primera semana de una cuenta nueva: sin stories, para no parecer automática
                break
            if i >= len(stories_activas):
                done["stories"].append(ig.publish(user, ig.container_etiq(user, ig.cuentas(data["stories"][i:i + 1]),
                                                                          media_type="STORIES", image_url=base + s.name)))
        (folder / "published.json").write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
        ig.git("add", rel)
        ig.git("commit", "-q", "-m", f"social: publicado {cc} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        return done
    finally:
        ig.TOKEN = None


# --- Reels de la tarde: cuenta atrás del Black Friday y Reel sobre guitle, en el idioma de cada país -------------

TXT = {
    "pt": {
        "top_hook": "Top do dia",
        "reel": {"bfFaltan": "Faltam", "bfDia": "dia", "bfDias": "dias", "bfApunta": "Anota este preço", "bfHoy": "Hoje, {fecha}",
                 "bfOtras": "Nas outras {n} lojas:", "bfRango": "de {a} a {b}", "bfBajara": "Vai baixar de verdade na Black Friday?",
                 "bfDecimos": "Em 27 de novembro a gente te conta, com o histórico de preços.", "bfGuarda": "Salve 📌"},
        "cap_bf": ("⏳ Faltam {days} {dias} para a Black Friday.\n📌 Anota este preço: {name} por {price} hoje em {store} "
                   "(nas outras lojas, de {next} a {max}).\nEm 27 de novembro a gente conta se o desconto é real ou inflado. "
                   "Salve e siga a gente 👀"),
        "que": ("O que é o guitle?", "O comparador de preços de guitarras", "{n} guitarras em {s} lojas",
                "Conferimos todos os preços, todo dia", "A gente mostra onde está mais barata", "Grátis e sem cadastro",
                "🎸 O que é o guitle? O comparador de preços de guitarras: {n} guitarras em {s} lojas do Brasil, conferidas todo dia.\n"
                "Procure a sua e veja onde está mais barata. Grátis e sem cadastro.\n🔎 {web} (link na bio)"),
        "misma": ("Você sabia?", "A mesma guitarra pode custar bem mais dependendo da loja", "{d} de diferença", "Compare antes de comprar",
                  "😮 A mesma guitarra, {d} de diferença dependendo da loja: {name}, de {lo} a {hi} hoje.\n"
                  "Por isso existe o guitle: comparamos cada guitarra em todas as lojas, todo dia.\n🔎 {web} (link na bio)"),
        "inflados": ("Cuidado na Black Friday", "Tem desconto que é mentira", "Sobem o preço… e depois “baixam”", "Exemplo",
                     "O guitle mostra isso com o histórico de preços", "Confira antes de comprar em {web}",
                     "⚠️ Cuidado com os descontos inflados: algumas lojas sobem o preço semanas antes e depois “baixam”… pro preço de sempre.\n"
                     "No guitle guardamos o preço de cada guitarra todo dia, então você vê na hora.\n🔎 {web} (link na bio)"),
        "momento": ("Antes de comprar", "É uma boa hora pra comprar?", "Veja o histórico de preços", "Exemplo", "Hoje: mínimo",
                    "No guitle você vê o histórico de cada guitarra", "Grátis, na página dela em {web}",
                    "📉 É uma boa hora pra comprar aquela guitarra? Veja o histórico de preços: se hoje está no mínimo, vai fundo!\n"
                    "No guitle você tem isso grátis na página de cada guitarra.\n🔎 {web} (link na bio)"),
        "desc": "−10%",
    },
    "fr": {
        "top_hook": "Top du jour",
        "reel": {"bfFaltan": "Plus que", "bfDia": "jour", "bfDias": "jours", "bfApunta": "Note ce prix", "bfHoy": "Aujourd’hui, {fecha}",
                 "bfOtras": "Dans les {n} autres magasins :", "bfRango": "de {a} à {b}", "bfBajara": "Va-t-il vraiment baisser au Black Friday ?",
                 "bfDecimos": "Le 27 novembre, on te le dit, historique des prix à l’appui.", "bfGuarda": "Enregistre-le 📌"},
        "cap_bf": ("⏳ Plus que {days} {dias} avant le Black Friday.\n📌 Note ce prix : {name} à {price} aujourd’hui chez {store} "
                   "(ailleurs, de {next} à {max}).\nLe 27 novembre, on te dira si la promo est réelle ou gonflée. "
                   "Enregistre ce Reel et abonne-toi 👀"),
        "que": ("C’est quoi guitle ?", "Le comparateur de prix de guitares", "{n} guitares dans {s} magasins",
                "On vérifie tous les prix, chaque jour", "On te dit où elle est la moins chère", "Gratuit et sans inscription",
                "🎸 C’est quoi guitle ? Le comparateur de prix de guitares : {n} guitares dans {s} magasins en France, vérifiées chaque jour.\n"
                "Cherche la tienne et vois où elle est la moins chère. Gratuit et sans inscription.\n🔎 {web} (lien en bio)"),
        "misma": ("Le savais-tu ?", "La même guitare peut coûter bien plus cher selon le magasin", "{d} d’écart", "Compare avant d’acheter",
                  "😮 La même guitare, {d} d’écart selon le magasin : {name}, de {lo} à {hi} aujourd’hui.\n"
                  "C’est pour ça que guitle existe : on compare chaque guitare dans tous les magasins, chaque jour.\n🔎 {web} (lien en bio)"),
        "inflados": ("Attention au Black Friday", "Certaines promos sont fausses", "Ils montent le prix… puis le « baissent »", "Exemple",
                     "guitle le repère grâce à l’historique des prix", "Vérifie avant d’acheter sur {web}",
                     "⚠️ Attention aux fausses promos : certains magasins montent le prix quelques semaines avant, puis le « baissent »… "
                     "au prix habituel.\nSur guitle, on enregistre le prix de chaque guitare chaque jour : tu le vois tout de suite.\n"
                     "🔎 {web} (lien en bio)"),
        "momento": ("Avant d’acheter", "C’est le bon moment pour l’acheter ?", "Regarde son historique de prix", "Exemple",
                    "Auj. : minimum", "Sur guitle, chaque guitare a son historique", "Gratuit, sur sa fiche {web}",
                    "📉 C’est le bon moment pour acheter cette guitare ? Regarde son historique de prix : si elle est à son minimum "
                    "aujourd’hui, fonce !\nSur guitle, c’est gratuit sur la fiche de chaque guitare.\n🔎 {web} (lien en bio)"),
        "desc": "−10 %",
    },
    "it": {
        "top_hook": "Top del giorno",
        "reel": {"bfFaltan": "Mancano", "bfDia": "giorno", "bfDias": "giorni", "bfApunta": "Segnati questo prezzo", "bfHoy": "Oggi, {fecha}",
                 "bfOtras": "Negli altri {n} negozi:", "bfRango": "da {a} a {b}", "bfBajara": "Scenderà davvero al Black Friday?",
                 "bfDecimos": "Il 27 novembre te lo diciamo, con lo storico dei prezzi.", "bfGuarda": "Salvalo 📌"},
        "cap_bf": ("⏳ Mancano {days} {dias} al Black Friday.\n📌 Segnati questo prezzo: {name} a {price} oggi da {store} "
                   "(negli altri negozi, da {next} a {max}).\nIl 27 novembre ti diremo se lo sconto è vero o gonfiato. "
                   "Salvalo e seguici 👀"),
        "que": ("Cos’è guitle?", "Il comparatore di prezzi di chitarre", "{n} chitarre in {s} negozi",
                "Controlliamo tutti i prezzi, ogni giorno", "Ti diciamo dove costa meno", "Gratis e senza registrazione",
                "🎸 Cos’è guitle? Il comparatore di prezzi di chitarre: {n} chitarre in {s} negozi in Italia, controllate ogni giorno.\n"
                "Cerca la tua e scopri dove costa meno. Gratis e senza registrazione.\n🔎 {web} (link in bio)"),
        "misma": ("Lo sapevi?", "La stessa chitarra può costare molto di più a seconda del negozio", "{d} di differenza",
                  "Confronta prima di comprare",
                  "😮 La stessa chitarra, {d} di differenza a seconda del negozio: {name}, da {lo} a {hi} oggi.\n"
                  "Per questo esiste guitle: confrontiamo ogni chitarra in tutti i negozi, ogni giorno.\n🔎 {web} (link in bio)"),
        "inflados": ("Attenzione al Black Friday", "Ci sono sconti finti", "Alzano il prezzo… e poi lo «scontano»", "Esempio",
                     "guitle lo scopre con lo storico dei prezzi", "Controlla prima di comprare su {web}",
                     "⚠️ Attenzione agli sconti gonfiati: alcuni negozi alzano il prezzo qualche settimana prima e poi lo «scontano»… "
                     "al prezzo di sempre.\nSu guitle salviamo il prezzo di ogni chitarra ogni giorno, così lo vedi subito.\n"
                     "🔎 {web} (link in bio)"),
        "momento": ("Prima di comprare", "È il momento giusto per comprarla?", "Guarda lo storico dei prezzi", "Esempio",
                    "Oggi: minimo", "Su guitle trovi lo storico di ogni chitarra", "Gratis, nella sua scheda su {web}",
                    "📉 È il momento giusto per comprare quella chitarra? Guarda lo storico dei prezzi: se oggi è al minimo, vai!\n"
                    "Su guitle lo trovi gratis nella scheda di ogni chitarra.\n🔎 {web} (link in bio)"),
        "desc": "−10%",
    },
    "de": {
        "top_hook": "Top des Tages",
        "reel": {"bfFaltan": "Noch", "bfDia": "Tag", "bfDias": "Tage", "bfApunta": "Merk dir diesen Preis", "bfHoy": "Heute, {fecha}",
                 "bfOtras": "In den anderen {n} Shops:", "bfRango": "von {a} bis {b}", "bfBajara": "Wird sie am Black Friday wirklich günstiger?",
                 "bfDecimos": "Am 27. November sagen wir es dir – mit dem Preisverlauf.", "bfGuarda": "Speichern 📌"},
        "cap_bf": ("⏳ Noch {days} {dias} bis zum Black Friday.\n📌 Merk dir diesen Preis: {name} für {price} heute bei {store} "
                   "(in anderen Shops {next} bis {max}).\nAm 27. November sagen wir dir, ob der Rabatt echt oder aufgeblasen ist. "
                   "Speichern und folgen 👀"),
        "que": ("Was ist guitle?", "Der Preisvergleich für Gitarren", "{n} Gitarren in {s} Shops",
                "Wir prüfen alle Preise, jeden Tag", "Wir zeigen dir, wo sie am günstigsten ist", "Kostenlos und ohne Anmeldung",
                "🎸 Was ist guitle? Der Preisvergleich für Gitarren: {n} Gitarren in {s} Shops in Deutschland, jeden Tag geprüft.\n"
                "Such deine und sieh, wo sie am günstigsten ist. Kostenlos und ohne Anmeldung.\n🔎 {web} (Link in der Bio)"),
        "misma": ("Wusstest du?", "Dieselbe Gitarre kann je nach Shop viel mehr kosten", "{d} Unterschied", "Erst vergleichen, dann kaufen",
                  "😮 Dieselbe Gitarre, {d} Unterschied je nach Shop: {name}, heute von {lo} bis {hi}.\n"
                  "Deshalb gibt es guitle: Wir vergleichen jede Gitarre in allen Shops, jeden Tag.\n🔎 {web} (Link in der Bio)"),
        "inflados": ("Vorsicht am Black Friday", "Manche Rabatte sind gelogen", "Erst Preis rauf … dann „reduziert“", "Beispiel",
                     "guitle erkennt es am Preisverlauf", "Vor dem Kauf prüfen auf {web}",
                     "⚠️ Vorsicht vor aufgeblasenen Rabatten: Manche Shops erhöhen den Preis ein paar Wochen vorher und „reduzieren“ ihn "
                     "dann … auf den normalen Preis.\nBei guitle speichern wir jeden Tag den Preis jeder Gitarre – du siehst es sofort.\n"
                     "🔎 {web} (Link in der Bio)"),
        "momento": ("Vor dem Kauf", "Ist jetzt ein guter Moment zum Kaufen?", "Schau dir den Preisverlauf an", "Beispiel",
                    "Heute: Tiefstpreis", "Bei guitle hat jede Gitarre ihren Preisverlauf", "Kostenlos, auf ihrer Seite bei {web}",
                    "📉 Ist jetzt ein guter Moment für diese Gitarre? Schau dir den Preisverlauf an: Wenn sie heute am günstigsten ist, "
                    "schlag zu!\nBei guitle findest du ihn kostenlos auf der Seite jeder Gitarre.\n🔎 {web} (Link in der Bio)"),
        "desc": "−10 %",
    },
    "en": {
        "top_hook": "Today’s top",
        "reel": {"bfFaltan": "Only", "bfDia": "day left", "bfDias": "days left", "bfApunta": "Note this price", "bfHoy": "Today, {fecha}",
                 "bfOtras": "In the other {n} shops:", "bfRango": "from {a} to {b}", "bfBajara": "Will it really drop on Black Friday?",
                 "bfDecimos": "On 27 November we’ll tell you, with its price history.", "bfGuarda": "Save it 📌"},
        "cap_bf": ("⏳ {days} {dias} to Black Friday.\n📌 Note this price: {name} at {price} today at {store} "
                   "(other shops: {next} to {max}).\nOn 27 November we’ll tell you if its discount is real or inflated. "
                   "Save this and follow us 👀"),
        "dias_cap": ("day", "days"),
        "que": ("What is guitle?", "The guitar price comparison site", "{n} guitars across {s} shops",
                "We check every price, every day", "We show you where it’s cheapest", "Free, no sign-up",
                "🎸 What is guitle? The guitar price comparison site: {n} guitars across {s} UK shops, checked every day.\n"
                "Find yours and see where it’s cheapest. Free, no sign-up.\n🔎 {web} (link in bio)"),
        "misma": ("Did you know?", "The same guitar can cost a lot more depending on the shop", "{d} difference", "Compare before you buy",
                  "😮 Same guitar, {d} difference depending on the shop: {name}, from {lo} to {hi} today.\n"
                  "That’s why guitle exists: we compare every guitar across every shop, every day.\n🔎 {web} (link in bio)"),
        "inflados": ("Black Friday warning", "Some discounts are fake", "They raise the price… then “cut” it", "Example",
                     "guitle spots it with the price history", "Check before you buy on {web}",
                     "⚠️ Watch out for inflated discounts: some shops raise the price a few weeks before, then “cut” it… back to the "
                     "usual price.\nAt guitle we record every guitar’s price every day, so you’ll spot it straight away.\n"
                     "🔎 {web} (link in bio)"),
        "momento": ("Before you buy", "Is now a good time to buy it?", "Check its price history", "Example", "Today: lowest",
                    "guitle shows the price history of every guitar", "Free, on its page at {web}",
                    "📉 Is now a good time to buy that guitar? Check its price history: if it’s at its lowest today, go for it!\n"
                    "On guitle it’s free on every guitar’s page.\n🔎 {web} (link in bio)"),
        "desc": "−10%",
    },
}
TXT["en-ie"] = {**TXT["en"], "que": TXT["en"]["que"][:6] + (TXT["en"]["que"][6].replace("UK shops", "Irish shops"),)}
TXT["pt-pt"] = {
    "top_hook": "Top do dia",
    "reel": {"bfFaltan": "Faltam", "bfDia": "dia", "bfDias": "dias", "bfApunta": "Aponta este preço", "bfHoy": "Hoje, {fecha}",
             "bfOtras": "Nas outras {n} lojas:", "bfRango": "de {a} a {b}", "bfBajara": "Vai mesmo baixar na Black Friday?",
             "bfDecimos": "A 27 de novembro dizemos-te, com o histórico de preços.", "bfGuarda": "Guarda 📌"},
    "cap_bf": ("⏳ Faltam {days} {dias} para a Black Friday.\n📌 Aponta este preço: {name} a {price} hoje na {store} "
               "(nas outras lojas, de {next} a {max}).\nA 27 de novembro dizemos-te se o desconto é real ou inflacionado. "
               "Guarda e segue-nos 👀"),
    "que": ("O que é o guitle?", "O comparador de preços de guitarras", "{n} guitarras em {s} lojas",
            "Verificamos todos os preços, todos os dias", "Mostramos-te onde está mais barata", "Grátis e sem registo",
            "🎸 O que é o guitle? O comparador de preços de guitarras: {n} guitarras em {s} lojas em Portugal, verificadas todos os dias.\n"
            "Procura a tua e vê onde está mais barata. Grátis e sem registo.\n🔎 {web} (link na bio)"),
    "misma": ("Sabias?", "A mesma guitarra pode custar bem mais consoante a loja", "{d} de diferença", "Compara antes de comprar",
              "😮 A mesma guitarra, {d} de diferença consoante a loja: {name}, de {lo} a {hi} hoje.\n"
              "É para isso que existe o guitle: comparamos cada guitarra em todas as lojas, todos os dias.\n🔎 {web} (link na bio)"),
    "inflados": ("Cuidado na Black Friday", "Há descontos que são mentira", "Sobem o preço… e depois “baixam”", "Exemplo",
                 "O guitle deteta-o com o histórico de preços", "Confirma antes de comprar em {web}",
                 "⚠️ Cuidado com os descontos inflacionados: algumas lojas sobem o preço semanas antes e depois “baixam”… para o "
                 "preço de sempre.\nNo guitle guardamos o preço de cada guitarra todos os dias, por isso vês logo.\n🔎 {web} (link na bio)"),
    "momento": ("Antes de comprar", "É boa altura para a comprar?", "Vê o histórico de preços", "Exemplo", "Hoje: mínimo",
                "No guitle cada guitarra tem o seu histórico", "Grátis, na página dela em {web}",
                "📉 É boa altura para comprar aquela guitarra? Vê o histórico de preços: se hoje está no mínimo, avança!\n"
                "No guitle tens isso grátis na página de cada guitarra.\n🔎 {web} (link na bio)"),
    "desc": "−10%",
}
TXT["nl"] = {
    "top_hook": "Top van vandaag",
    "reel": {"bfFaltan": "Nog", "bfDia": "dag", "bfDias": "dagen", "bfApunta": "Onthoud deze prijs", "bfHoy": "Vandaag, {fecha}",
             "bfOtras": "In de andere {n} winkels:", "bfRango": "van {a} tot {b}", "bfBajara": "Wordt hij echt goedkoper op Black Friday?",
             "bfDecimos": "Op 27 november vertellen we het je, met de prijshistorie.", "bfGuarda": "Bewaar 📌"},
    "cap_bf": ("⏳ Nog {days} {dias} tot Black Friday.\n📌 Onthoud deze prijs: {name} voor {price} vandaag bij {store} "
               "(in andere winkels {next} tot {max}).\nOp 27 november vertellen we je of de korting echt is of opgeblazen. "
               "Bewaar en volg ons 👀"),
    "que": ("Wat is guitle?", "De prijsvergelijker voor gitaren", "{n} gitaren in {s} winkels",
            "We checken alle prijzen, elke dag", "We laten zien waar hij het goedkoopst is", "Gratis en zonder account",
            "🎸 Wat is guitle? De prijsvergelijker voor gitaren: {n} gitaren in {s} Nederlandse winkels, elke dag gecheckt.\n"
            "Zoek de jouwe en zie waar hij het goedkoopst is. Gratis en zonder account.\n🔎 {web} (link in bio)"),
    "misma": ("Wist je dat?", "Dezelfde gitaar kan per winkel veel meer kosten", "{d} verschil", "Vergelijk voor je koopt",
              "😮 Dezelfde gitaar, {d} verschil per winkel: {name}, vandaag van {lo} tot {hi}.\n"
              "Daarom bestaat guitle: we vergelijken elke gitaar in alle winkels, elke dag.\n🔎 {web} (link in bio)"),
    "inflados": ("Let op met Black Friday", "Sommige kortingen zijn nep", "Eerst de prijs omhoog… dan “afgeprijsd”", "Voorbeeld",
                 "guitle ziet het aan de prijshistorie", "Check het voor je koopt op {web}",
                 "⚠️ Let op opgeblazen kortingen: sommige winkels verhogen de prijs een paar weken eerder en “prijzen” hem dan af… "
                 "naar de normale prijs.\nBij guitle slaan we elke dag de prijs van elke gitaar op, dus je ziet het meteen.\n"
                 "🔎 {web} (link in bio)"),
    "momento": ("Voor je koopt", "Is het nu een goed moment om te kopen?", "Bekijk de prijshistorie", "Voorbeeld",
                "Vandaag: laagste", "Bij guitle heeft elke gitaar zijn prijshistorie", "Gratis, op zijn pagina op {web}",
                "📉 Is het nu een goed moment voor die gitaar? Bekijk de prijshistorie: is hij vandaag het goedkoopst, sla je slag!\n"
                "Bij guitle vind je die gratis op de pagina van elke gitaar.\n🔎 {web} (link in bio)"),
    "desc": "−10%",
}

ESCALA = {"en-GB": 0.85, "pt-BR": 4}  # para las gráficas de ejemplo, en la moneda de cada país


def _render(sub, plan, caption, cfg, n):
    (sub / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["node", str(ROOT / "brand" / "reel.js"), str(sub)], check=True, cwd=ROOT)
    credito = musica.poner(sub / "reel.mp4", n, cfg["temas"])
    (sub / "texto.txt").write_text(f"{caption}\n\n{credito}\n", encoding="utf-8")


def reels_tarde(cc, day, recent):
    """Genera reel-2-black-friday (hasta el Black Friday) y reel-3-guitle en social/<fecha>/<país>/."""
    cfg = PAISES[cc]
    T = TXT[cfg.get("txt", cfg["lang"])]
    money = dinero(cfg)
    folder = ig.OUT / day.isoformat() / cc
    cats = {k: ROOT / v for k, v in cfg["catalogs"].items()}
    lo, hi = cfg["rango"]
    prods = ig.products(lo, hi, catalogs=cats)
    fetcher = Fetcher(delay=(0.5, 1.0))
    fecha = cfg["fecha"](day)
    base = {"fecha": fecha, "stories": [], "t": {**cfg["t"], "web": cfg["web"], "kinds": cfg["kinds"], **T["reel"]},
            "money": cfg["money"], "logo": cfg["logo"]}
    # Un tema de música distinto en cada uno de los 3 Reels del día de la cuenta
    musica_n = day.toordinal() + list(PAISES).index(cc)
    # Precios con diferencias absurdas entre tiendas suelen ser fichas mal emparejadas: fuera (CLAUDE.md)
    fiables = [p for p in prods if p["max"] <= 2 * p["price"]]
    hechos = []

    listo = lambda sub: (sub / "reel.mp4").exists() and (sub / "texto.txt").exists()  # ya generado (y revisado): no se rehace
    days = (ig.BLACK_FRIDAY - day).days
    if not ig.dia_bf(day):  # días sin cuenta atrás: top 5 por precio (otro rango que el del post)
        sub = folder / "reel-2-top"
        if listo(sub):
            hechos.append(sub.name)
        else:
            sub.mkdir(parents=True, exist_ok=True)
            j = (day.toordinal() + 4) % len(cfg["tops"])  # cada día otro, y nunca el del post
            del_post = (day.toordinal() // 2) % len(cfg["tops"])
            picks = []
            # Si el rango del día no tiene 3 guitarras con foto revisada, se prueban los siguientes
            for k in range(len(cfg["tops"])):
                jj = (j + k) % len(cfg["tops"])
                if jj == del_post:
                    continue
                for f in sub.glob("g*.webp"):
                    f.unlink()
                kind, tlo, thi = cfg["tops"][jj]
                picks = sorted(ig.with_photos(ig.top_of(fiables, kind, tlo, thi, recent), 5, fetcher, sub, "g"),
                               key=lambda p: p["price"])
                if len(picks) >= 3:
                    break
            if len(picks) >= 3:
                rango = (cfg["rango_txt"][0] if tlo <= lo else cfg["rango_txt"][1]).format(lo=money(tlo), hi=money(thi))
                title = f"{len(picks)} {cfg['plural'][kind]} {rango}"
                lines = "\n".join(cfg["linea_top"].format(i=i, name=p["name"], price=money(p["price"]), store=p["store"])
                                  for i, p in enumerate(picks, 1))
                cap = cfg["cap_top"].format(title=title[0].upper() + title[1:], lines=lines, web=cfg["web"], fecha=fecha,
                                            tags=f"{cfg['base_tags']} {cfg['hashtags'][kind]} "
                                            + " ".join(dict.fromkeys(ig.tag(p["brand"]) for p in picks)))
                _render(sub, {**base, "post": {"type": "top", "title": title, "hook": T["top_hook"], "picks": picks}},
                        cap, cfg, musica_n + 1)
                hechos.append(sub.name)
    elif listo(folder / "reel-2-black-friday"):
        hechos.append("reel-2-black-friday")
    else:
        sub = folder / "reel-2-black-friday"
        sub.mkdir(parents=True, exist_ok=True)
        kind = ["electrica", "acustica", "electrica", "clasica"][(day.toordinal() + list(PAISES).index(cc)) % 4]
        pool = sorted((p for p in fiables if p["kind"] == kind and p["name"] not in recent and p["stores"] >= 4),
                      key=lambda p: -p["stores"])
        got = ig.with_photos(pool, 1, fetcher, sub, "g")
        if not got:  # pocos catálogos (Italia, Portugal): cualquier tipo de guitarra y desde 3 tiendas
            pool = sorted((p for p in fiables if p["name"] not in recent and p["stores"] >= 3), key=lambda p: -p["stores"])
            got = ig.with_photos(pool, 1, fetcher, sub, "g")
        if got:
            p = got[0]
            dias = T.get("dias_cap", (T["reel"]["bfDia"], T["reel"]["bfDias"]))[days != 1]
            cap = T["cap_bf"].format(days=days, dias=dias, name=p["name"], price=money(p["price"]), store=p["store"],
                                     next=money(p["next"]), max=money(p["max"]))
            tags = f"#blackfriday #blackfriday2026 {cfg['base_tags']} {cfg['hashtags'][p['kind']]} {ig.tag(p['brand'])}"
            _render(sub, {**base, "post": {"type": "bf", "days": days, "deal": p}}, f"{cap}\n\n{tags}", cfg, musica_n + 1)
            hechos.append(sub.name)

    sub = folder / "reel-3-guitle"
    if listo(sub):
        return hechos + [sub.name]
    sub.mkdir(parents=True, exist_ok=True)
    datos = load(ROOT / "data/catalog/paises.json", {}).get(cc, {})
    sep = {"en-GB": ",", "fr-FR": " "}.get(cfg["money"]["locale"], ".")
    n = f"{datos.get('guitars', 0):,}".replace(",", sep)
    tiendas = sorted({x.replace(" (eBay)", "") for path in cats.values() for x in load(path, {}).get("stores", {}).values()})
    s = datos.get("stores") or len(tiendas)
    chips = tiendas if len(tiendas) <= 24 else tiendas[:22] + [f"+{len(tiendas) - 22}"]
    k = ESCALA.get(cfg["money"]["locale"], 1)
    pts = lambda vals: [v if k == 1 else int(round(v * k, -1)) - 1 for v in vals]
    web, tags = cfg["web"], cfg["base_tags"]
    topics = []
    q = T["que"]
    showcase = ig.with_photos(sorted(fiables, key=lambda p: -p["stores"]), 5, fetcher, sub, "g")
    # Portada con guitarra (nunca solo texto): fila de guitarras, o la comparada en «misma guitarra»
    fila = {"type": "guitars", "photos": [p["photo"] for p in showcase]} if showcase else None
    if showcase:
        topics.append(("que", [
            {"hook": "guitle", "title": q[0], "sub": q[1], "visual": {"type": "guitars", "photos": [p["photo"] for p in showcase]}},
            {"title": q[2].format(n=n, s=s), "sub": q[3], "size": 120},
            {"title": q[4], "sub": q[5], "size": 120}], q[6].format(n=n, s=s, web=web) + f"\n\n{tags}"))
    cands = [p for p in fiables if p["stores"] >= 5 and p["max"] <= 1.45 * p["price"]  # diferencias creíbles
             and ig.foto_revisada(p)]  # y con foto: la guitarra comparada va en la portada
    if cands:
        ex = max(cands, key=lambda p: p["max"] - p["price"])
        foto_ex = ig.with_photos([ex], 1, fetcher, sub, "ex")
        rows = ex["rows"][:3] + ex["rows"][-1:] if len(ex["rows"]) > 4 else ex["rows"]
        tienda = {"pt": "Loja", "fr": "Magasin", "it": "Negozio", "de": "Shop", "en": "Shop"}[cfg["lang"]]
        rows = [[f"{tienda} {'ABCD'[i]}", r[1]] for i, r in enumerate(rows)]  # en los Reels sobre guitle, tiendas sin nombre
        m, d = T["misma"], money(ex["max"] - ex["price"])
        topics.append(("misma", [
            {"hook": m[0], "title": m[1], "visual": {"type": "photo", "photo": foto_ex[0]["photo"]} if foto_ex else fila},
            {"title": ex["name"], "size": 76, "visual": {"type": "prices", "rows": rows}},
            {"title": m[2].format(d=d), "sub": m[3], "size": 130}],
            m[4].format(d=d, name=ex["name"], lo=money(ex["price"]), hi=money(ex["max"]), web=web)
            + f"\n\n{tags} {cfg['hashtags'][ex['kind']]} {ig.tag(ex['brand'])}"))
    f, c = T["inflados"], pts([899, 899, 899, 999, 999, 999, 899, 899])
    topics.append(("inflados", [
        {"hook": f[0], "title": f[1], "visual": fila},
        {"title": f[2], "sub": f[3], "size": 96, "visual": {"type": "chart", "points": c,
         "marks": [[1, money(c[1]), "#1f9d55"], [4, money(c[4]), "#d64545"], [7, f"«{T['desc']}»", "#d64545"]]}},
        {"title": f[4], "sub": f[5].format(web=web)}], f[6].format(web=web) + f"\n\n#blackfriday {tags}"))
    h, c = T["momento"], pts([829, 829, 799, 829, 789, 789, 769, 749])
    topics.append(("momento", [
        {"hook": h[0], "title": h[1], "visual": fila},
        {"title": h[2], "sub": h[3], "size": 100, "visual": {"type": "chart", "points": c,
         "marks": [[0, money(c[0]), "#52514e"], [7, h[4], "#1f9d55"]]}},
        {"title": h[5], "sub": h[6].format(web=web)}], h[7].format(web=web) + f"\n\n{tags}"))
    # Cada cuenta, un tema distinto el mismo día (España va con el índice 0)
    title, slides, caption = topics[(day.toordinal() + list(PAISES).index(cc) + 1) % len(topics)]
    _render(sub, {**base, "post": {"type": "guitle", "topic": title, "slides": slides}}, caption, cfg, musica_n + 2)
    hechos.append(sub.name)
    return hechos


def publicar_tarde(cc, day, names, token):
    """Sube los Reels de la tarde al repo y los publica en la cuenta del país (sin repetir los ya publicados hoy)."""
    folder = ig.OUT / day.isoformat() / cc
    ig.TOKEN = token
    try:
        user = ig.api("GET", "me", fields="user_id")["user_id"]
        rel = folder.relative_to(ROOT).as_posix()
        branch = ig.git("rev-parse", "--abbrev-ref", "HEAD")
        ig.git("add", rel)
        if ig.git("diff", "--cached", "--name-only"):
            ig.git("commit", "-q", "-m", f"social: Reels de la tarde {cc} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        base = f"{ig.REPO_RAW}/{ig.git('rev-parse', 'HEAD')}/{rel}/"
        hoy = [m for m in ig.api("GET", f"{user}/media", fields="caption,permalink,timestamp", limit=25)["data"]
               if m.get("timestamp", "")[:10] == day.isoformat()]
        ya = lambda caption: next((m["permalink"] for m in hoy if (m.get("caption") or "")[:60] == caption[:60]), None)
        pt = folder / "published-tarde.json"
        done = json.loads(pt.read_text(encoding="utf-8")) if pt.exists() else {}
        names = [n for n in names if not str(done.get(n, "")).startswith("https://")]
        for name in names:
            url = base + f"{name}/reel.mp4"
            for _ in range(20):
                if requests.head(url, timeout=30).status_code == 200:
                    break
                time.sleep(5)
            caption = (folder / name / "texto.txt").read_text(encoding="utf-8").strip()
            handles = ig.cuentas(ig.marcas_reel(folder / name))
            try:
                done[name] = ya(caption) or ig.publish(user, ig.container_etiq(
                    user, handles, tries=100, media_type="REELS", caption=ig.menciones(caption, handles),
                    video_url=url, share_to_feed="true"))
            except Exception as exc:  # si uno falla, se publica el otro
                done[name] = f"error: {exc}"
        (folder / "published-tarde.json").write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
        ig.git("add", rel)
        ig.git("commit", "-q", "-m", f"social: publicados los Reels de la tarde {cc} {day.isoformat()}")
        ig.git("push", "-q", "origin", f"HEAD:{branch}")
        return done
    finally:
        ig.TOKEN = None


SUAVE = set()  # cuentas en su primera semana (--suave)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+", choices=sorted(PAISES))
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--tarde", action="store_true", help="Reels de la tarde: cuenta atrás del Black Friday y Reel sobre guitle")
    ap.add_argument("--solo", choices=["reel-2", "reel-3"], help="con --tarde: publica solo ese Reel (reel-2: Black Friday o top; reel-3: guitle)")
    ap.add_argument("--reel-chollos", action="store_true",
                    help="rehace y publica solo el Reel de chollos de mediodía si no salió (sin tocar post ni stories)")
    ap.add_argument("--suave", default="", help="países en su primera semana (p. ej. pt): post y Reel, sin stories")
    ap.add_argument("--espera", type=int, default=0, help="minutos máximos de espera al azar entre cuentas (para no publicar en ráfaga)")
    args = ap.parse_args(argv)
    SUAVE.update(x for x in args.suave.split(",") if x)
    day = datetime.fromisoformat(args.date).date() if args.date else datetime.now(timezone.utc).date()
    cuentas = load(ROOT / "social" / "cuentas.json", {})
    out = {}
    for n, cc in enumerate(args.paises):
        folder = ig.OUT / day.isoformat() / cc
        ya = not args.tarde and not args.reel_chollos and (folder / "published.json").exists()
        if args.publish and ya:
            out[cc] = "ya publicado"
            continue
        if args.publish and args.espera and n:
            time.sleep(random.randint(60, args.espera * 60))
        token = os.environ.get(cuentas.get(cc, {}).get("token_env", ""))
        if not token:
            out[cc] = "sin token"
            continue
        try:
            ig.TOKEN = token
            user = ig.api("GET", "me", fields="user_id")["user_id"]
            recent = recientes(cc, user)
        finally:
            ig.TOKEN = None
        if args.reel_chollos:
            out[cc] = rehacer_reel_chollos(cc, day, recent, token if args.publish else None)
            continue
        if args.tarde:
            hechos = load(folder / "published-tarde.json", {})
            names = [x for x in reels_tarde(cc, day, recent) if (not args.solo or x.startswith(args.solo + "-"))
                     and not str(hechos.get(x, "")).startswith("https://")]
            if args.publish and not names:
                out[cc] = "ya publicado"
                continue
            out[cc] = publicar_tarde(cc, day, names, token) if args.publish else names
            continue
        folder, data = plan_pais(cc, day, recent)
        out[cc] = {"post": data["post"]["type"], "stories": [s["name"] for s in data["stories"]]}
        if args.publish:
            out[cc] = publicar(cc, day, folder, data, token)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if any(v == "sin token" for v in out.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
