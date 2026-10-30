"""Webs de guitle en otros países (guitle.com/pt/, guitle.com/fr/…): una carpeta por país, con su idioma y su moneda.

España es la web de siempre (raíz del sitio). Cada país tiene su propio catálogo (scraper.catalog --cat pt) con las
tiendas que venden allí y sus precios; aquí se generan, a partir de esos JSON, la portada, las páginas del catálogo,
la página de cada guitarra, la de los avisos de precio, el aviso legal y el sitemap del país. Los textos de cada
idioma están en T; el catálogo y la ficha (catalogo.js, producto.js) los reciben en window.GUITLE_T.

Para añadir un país: su catálogo en scraper.catalog (CATALOGS, con "site"), su entrada en SITES y, si su idioma es
nuevo, sus textos en T.

    python -m scraper.intl [--site pt]
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

from . import pages

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://guitle.com"
GUITAR_KINDS = ("electrica", "acustica", "clasica", "portuguesa")

# Por país: idioma, moneda, catálogo (carpeta de data/catalog) y, por categoría, el nombre de su página y de su JSON.
SITES = {
    "pt": {"country": "Portugal", "lang": "pt-PT", "t": "pt", "cur": "EUR", "catalog": "pt",
           "kinds": {"electrica": "eletricas", "acustica": "acusticas", "clasica": "classicas", "portuguesa": "portuguesas"},
           "amazon": "https://www.amazon.es/s?k={q}&tag=guitle-21"},
    "fr": {"country": "France", "lang": "fr-FR", "t": "fr", "cur": "EUR", "catalog": "fr",
           "kinds": {"electrica": "electriques", "acustica": "folk", "clasica": "classiques"},
           "amazon": None},
    "it": {"country": "Italia", "lang": "it-IT", "t": "it", "cur": "EUR", "catalog": "it",
           "kinds": {"electrica": "elettriche", "acustica": "acustiche", "clasica": "classiche"},
           "amazon": None},
    # Equipo en otro catálogo ("demas", scraper.catalog.EQUIPO_COUNTRIES); sus páginas salen cuando tiene productos.
    "de": {"country": "Deutschland", "lang": "de-DE", "t": "de", "cur": "EUR", "catalog": "de", "extra_catalogs": ["demas"],
           "kinds": {"electrica": "e-gitarren", "acustica": "westerngitarren", "clasica": "konzertgitarren", "bajo": "baesse",
                     "ampli": "verstaerker", "pedal": "effektpedale", "teclado": "keyboards", "micro": "mikrofone",
                     "estuche": "koffer-taschen", "varios": "zubehoer"},
           "amazon": None},
    "br": {"country": "Brasil", "lang": "pt-BR", "t": "br", "cur": "BRL", "catalog": "br", "extra_catalogs": ["brmas"],
           "kinds": {"electrica": "guitarras", "acustica": "violoes", "clasica": "violoes-nylon", "bajo": "baixos",
                     "ampli": "amplificadores", "pedal": "pedais", "teclado": "teclados", "micro": "microfones",
                     "estuche": "cases", "varios": "acessorios"},
           "amazon": None},
    "ie": {"country": "Ireland", "lang": "en-IE", "t": "en", "cur": "EUR", "catalog": "ie",
           "kinds": {"electrica": "electric-guitars", "acustica": "acoustic-guitars", "clasica": "classical-guitars"},
           "amazon": None,
           "t_over": {"homeDesc": "guitle compares guitar prices: electric, acoustic and classical guitars in the shops that sell in "
                                  "Ireland, with the price history of every model.",
                      "steps": ["Every day we check the price, stock and photo of every guitar in the shops that sell in Ireland.",
                                "We keep the price history so you can tell whether a price is genuinely good or usually lower.",
                                "If you like, we'll email you when the price drops."],
                      "js": {"targetLabel": "Target price in euros"}},
           "legal_replace": [("the Information Commissioner's Office (ICO)", "the Data Protection Commission (DPC)"),
                             (" and its UK Extension", "")]},
    "at": {"country": "Österreich", "lang": "de-AT", "t": "de", "cur": "EUR", "catalog": "at",
           "kinds": {"electrica": "e-gitarren", "acustica": "westerngitarren", "clasica": "konzertgitarren"},
           "amazon": None,
           "t_over": {"homeDesc": "guitle vergleicht Gitarrenpreise: E-Gitarren, Westerngitarren und Konzertgitarren in den Shops, "
                                  "die nach Österreich liefern, mit dem Preisverlauf jedes Modells.",
                      "steps": ["Jeden Tag prüfen wir Preis, Verfügbarkeit und Foto jeder Gitarre in den Shops, die nach Österreich liefern.",
                                "Wir speichern den Preisverlauf, damit du siehst, ob ein Preis wirklich gut ist oder sonst niedriger liegt.",
                                "Auf Wunsch schicken wir dir eine E-Mail, wenn der Preis fällt."]},
           "legal_replace": [("oder der Aufsichtsbehörde deines Bundeslandes", "oder der österreichischen Datenschutzbehörde")]},
    "nl": {"country": "Nederland", "lang": "nl-NL", "t": "nl", "cur": "EUR", "catalog": "nl",
           "kinds": {"electrica": "elektrische-gitaren", "acustica": "akoestische-gitaren", "clasica": "klassieke-gitaren"},
           "amazon": None},
    "uk": {"country": "United Kingdom", "lang": "en-GB", "t": "en", "cur": "GBP", "catalog": "uk",
           "kinds": {"electrica": "electric-guitars", "acustica": "acoustic-guitars", "clasica": "classical-guitars"},
           "amazon": None},
}
# España, para los enlaces entre países (hreflang y el pie de página).
SPAIN = {"country": "España", "lang": "es-ES", "path": "/"}

T = {
    "pt": {
        "tagline": "guitarras ao melhor preço", "homeLabel": "guitle, início",
        "homeTitle": "guitle · comparador de preços de guitarras",
        "homeDesc": "O guitle é um comparador de preços de guitarras: elétricas, acústicas, clássicas e portuguesas nas lojas "
                    "que vendem em Portugal, com o histórico de preços de cada modelo.",
        "h1": "A tua guitarra, <span>ao melhor preço</span><small>Comparador de preços de guitarras</small>",
        "searchPh": "Pesquisa: strat, les paul, yamaha, alhambra…", "searchBtn": "Pesquisar", "searchLabel": "Pesquisar guitarra",
        "guitars": "guitarras", "storesWord": "lojas", "catalog": "Catálogo",
        "dealsH": "Maiores diferenças entre lojas", "dealsBadge": "−{p} % vs. a mais cara",
        "catsH": "Explorar por categoria", "soon": "em breve", "storesH": "Lojas que comparamos",
        "howH": "Como funciona",
        "steps": ["Todos os dias revemos o preço, o stock e a foto de cada guitarra nas lojas que vendem em Portugal.",
                  "Guardamos o histórico para saberes se um preço é mesmo bom ou se costuma estar mais baixo.",
                  "Se quiseres, avisamos-te por email quando o preço baixar."],
        "affiliate": "Alguns links para lojas são de afiliado: se comprares, o guitle pode receber uma comissão, sem custo para ti.",
        "legal": "Aviso legal", "privacy": "Privacidade", "cookies": "Cookies", "otherCountries": "guitle noutros países:",
        "updated": "Dados atualizados a {d}", "home": "Início",
        "kinds": {"electrica": ("Guitarras elétricas", "Elétricas", "Pesquisa nas elétricas: modelo, marca, cor…"),
                  "acustica": ("Guitarras acústicas", "Acústicas", "Pesquisa nas acústicas: modelo, marca, madeira…"),
                  "clasica": ("Guitarras clássicas", "Clássicas", "Pesquisa nas clássicas: modelo, marca, flamenca…"),
                  "portuguesa": ("Guitarras portuguesas", "Portuguesas", "Pesquisa nas guitarras portuguesas: modelo, Lisboa, Coimbra…")},
        "anyPrice": "Qualquer preço", "upTo": "Até {v}", "over": "Mais de {v}", "brandLabel": "Marca", "priceLabel": "Preço",
        "showLabel": "Mostrar", "showAll": "Todas", "showMulti": "Em várias lojas", "showStock": "Em stock",
        "showLow": "No preço mínimo", "showLh": "Só canhotas", "loading": "A carregar o catálogo…", "sortLabel": "Ordenar",
        "sorts": ["Mais lojas", "Preço mais baixo", "Preço mais alto", "Maior poupança entre lojas", "Nome"], "moreBtn": "Ver mais",
        "sections": "Secções", "searchAria": "Pesquisar",
        "bestPrice": "melhor preço", "inStock": "em stock", "noStock": "sem stock", "goLong": "Ir à loja", "goShort": "Ir",
        "store": "loja", "stores": "lojas", "lh": "canhota", "storesH3": "Lojas", "historyH3": "Histórico de preços",
        "amazon": "Preferes comprar na Amazon? <a href=\"{u}\" target=\"_blank\" rel=\"sponsored noopener\">Procurar este modelo na Amazon</a>",
        "titleFrom": "{name}: preço desde {price} {where}", "inN": "em {n} lojas", "inS": "em {s}",
        "whereMany": "em {s} · {n} lojas", "whereDiff": ", até {d} de diferença",
        "desc": "{name} desde {price} em {s}. Compara o preço em {n} {stores} ({list}) e vê o histórico para saberes se é boa altura para comprar.",
        "alertTitle": "Aviso de preço", "alertWait": "Um momento…", "alertSaving": "Estamos a guardar a tua resposta.",
        "alertGo": "Ir para o guitle", "alertBad": ["Link inválido", "Copia o link completo do email e tenta outra vez."],
        "alertDone": ["Aviso confirmado!", "Escrevemos-te assim que o preço baixar. Cada email tem um link para cancelares."],
        "alertGone": ["Aviso apagado", "Não vais voltar a receber emails deste aviso. Apagámos o teu email da nossa lista."],
        "alertMissing": ["Não encontrámos o aviso", "Talvez já estivesse confirmado ou apagado, ou passaram mais de 7 dias sem o confirmares. "
                                                     "Se precisares de ajuda, escreve-nos para hola@guitle.com."],
        "js": {"loadErr": "Não foi possível carregar o catálogo.", "allBrands": "Todas as marcas", "all": "Todas", "low": "Mínimo",
               "save": "Poupa {v}", "lh": "canhota", "store": "loja", "stores": "lojas", "empty": "Não há {many} com esses filtros.",
               "more": "Ver mais ({n} restantes)", "meta": "{a} de {b} {many} · {m} comparáveis em várias lojas · atualizado a {d}",
               "best": "melhor preço", "inStock": "em stock", "noStock": "sem stock", "goLong": "Ir à loja", "goShort": "Ir",
               "close": "Fechar", "inAt": "em {s}", "saveMax": " · até {v} menos do que na mais cara", "atLow": "No mínimo registado",
               "lowTag": "Mínimo registado: {v}", "storesH": "Lojas", "evolH": "Evolução do preço",
               "histErr": "Não foi possível carregar o histórico.", "histSoon": "O histórico vai-se completando com as próximas leituras.",
               "many": "guitarras",
               "types": {"Semihueca": "Semi-acústica", "Moderna / Metal": "Moderna / Metal", "Otras": "Outras",
                         "Auditorio / Concierto": "Auditório / Concerto", "12 cuerdas": "12 cordas",
                         "Tamaño reducido": "Tamanho reduzido", "Clásica": "Clássica", "Electroclásica": "Eletroclássica"},
               "wait": "Seguimos este modelo há {n} {days}", "day": "dia", "days": "dias",
               "waitSub": "O veredicto será mais fiável com algumas semanas de histórico.",
               "min": "Preço mínimo registado", "minSub": "Nunca a vimos mais barata.", "minBelow": " Está {p} % abaixo da média de 30 dias.",
               "good": "Boa altura: {p} % abaixo do preço médio", "goodSub": "Média dos últimos 30 dias: {avg}.",
               "bad": "Agora está {p} % mais cara do que o habitual",
               "badSub": "Se não tens pressa, espera: a média de 30 dias é {avg} e o mínimo, {min}.",
               "normal": "Preço normal", "normalSub": "Em linha com a média de 30 dias ({avg}). Mínimo registado: {min}.",
               "today": "preço hoje", "lowest": "mínimo histórico ({d})", "highest": "máximo histórico", "avg": "média {n} dias",
               "since": "Seguimos este modelo desde {d}.", "noHist": "Ainda não há histórico de preços.", "pvp": "PVP oficial",
               "bestLine": "Melhor preço", "alertOpen": "Avisa-me se baixar de preço", "emailPh": "o.teu@email.com",
               "emailLabel": "O teu email", "targetPh": "Preço máx. (opcional)", "targetLabel": "Preço-alvo em euros",
               "alertBtn": "Avisar-me",
               "alertLegal": "Grátis e sem registo. Ao carregares em «Avisar-me» aceitas a <a href=\"/pt/legal.html#privacidade\">política "
                             "de privacidade</a>: usamos o teu email só para este aviso e cancelas com um clique.",
               "alertOk": "<b>Feito!</b> Dentro de minutos vais receber um email em {email} para confirmares o aviso (vê também no spam).",
               "alertErr": "Não foi possível guardar o aviso. Verifica o email e tenta outra vez."},
        "mail": {"tagline": "guitarras ao melhor preço",
                 "footer": "O guitle compara todos os dias os preços das lojas de música. Recebes este email porque pediste um aviso "
                           "em guitle.com. Responsável: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Privacidade", "confirmSubject": "Confirma o teu aviso de preço no guitle",
                 "confirmTitle": "Confirma o teu aviso de preço", "asked": "Pediste que te avisássemos quando baixar de preço{target}:",
                 "below": " para menos de <b>{v}</b>", "confirmAsk": "Confirma que queres receber o aviso neste endereço:",
                 "confirmBtn": "Confirmar o aviso",
                 "notYou": "Se não foste tu, não faças nada: sem confirmação, o aviso apaga-se sozinho em 7 dias e não voltas a ter notícias nossas.",
                 "dropSubject": "Baixou: {name} para {price}", "dropTitle": "Baixou de preço!", "nowAt": "em {s} · antes {v}",
                 "seeAll": "Ver preços em todas as lojas",
                 "check": "Os preços mudam todos os dias: confirma na loja antes de comprar. Já não te interessa?",
                 "stop": "Deixar de receber este aviso"},
    },
    "fr": {
        "tagline": "guitares au meilleur prix", "homeLabel": "guitle, accueil",
        "homeTitle": "guitle · comparateur de prix de guitares",
        "homeDesc": "guitle est un comparateur de prix de guitares : électriques, folk et classiques dans les magasins qui vendent "
                    "en France, avec l'historique des prix de chaque modèle.",
        "h1": "Votre guitare, <span>au meilleur prix</span><small>Comparateur de prix de guitares</small>",
        "searchPh": "Recherche : strat, les paul, yamaha, ibanez…", "searchBtn": "Rechercher", "searchLabel": "Rechercher une guitare",
        "guitars": "guitares", "storesWord": "magasins", "catalog": "Catalogue",
        "dealsH": "Les plus gros écarts entre magasins", "dealsBadge": "−{p} % vs. le plus cher",
        "catsH": "Explorer par catégorie", "soon": "bientôt", "storesH": "Magasins comparés",
        "howH": "Comment ça marche",
        "steps": ["Chaque jour, nous relevons le prix, le stock et la photo de chaque guitare dans les magasins qui vendent en France.",
                  "Nous gardons l'historique pour que vous sachiez si un prix est vraiment bon ou s'il est souvent plus bas.",
                  "Si vous le souhaitez, nous vous prévenons par e-mail quand le prix baisse."],
        "affiliate": "Certains liens vers les magasins sont des liens affiliés : si vous achetez, guitle peut toucher une commission, "
                     "sans surcoût pour vous.",
        "legal": "Mentions légales", "privacy": "Confidentialité", "cookies": "Cookies", "otherCountries": "guitle dans d'autres pays :",
        "updated": "Données mises à jour le {d}", "home": "Accueil",
        "kinds": {"electrica": ("Guitares électriques", "Électriques", "Recherche parmi les électriques : modèle, marque, couleur…"),
                  "acustica": ("Guitares folk et acoustiques", "Folk", "Recherche parmi les folk : modèle, marque, bois…"),
                  "clasica": ("Guitares classiques", "Classiques", "Recherche parmi les classiques : modèle, marque, flamenca…")},
        "anyPrice": "Tous les prix", "upTo": "Jusqu'à {v}", "over": "Plus de {v}", "brandLabel": "Marque", "priceLabel": "Prix",
        "showLabel": "Afficher", "showAll": "Toutes", "showMulti": "Dans plusieurs magasins", "showStock": "En stock",
        "showLow": "À leur prix le plus bas", "showLh": "Gauchères uniquement", "loading": "Chargement du catalogue…",
        "sortLabel": "Trier", "sorts": ["Plus de magasins", "Prix croissant", "Prix décroissant", "Plus gros écart entre magasins", "Nom"],
        "moreBtn": "Voir plus", "sections": "Rubriques", "searchAria": "Rechercher",
        "bestPrice": "meilleur prix", "inStock": "en stock", "noStock": "épuisé", "goLong": "Voir le magasin", "goShort": "Voir",
        "store": "magasin", "stores": "magasins", "lh": "gaucher", "storesH3": "Magasins", "historyH3": "Historique des prix",
        "amazon": "", "titleFrom": "{name} : prix à partir de {price} {where}", "inN": "dans {n} magasins", "inS": "chez {s}",
        "whereMany": "chez {s} · {n} magasins", "whereDiff": ", jusqu'à {d} d'écart",
        "desc": "{name} à partir de {price} chez {s}. Comparez son prix dans {n} {stores} ({list}) et consultez l'historique pour savoir "
                "si c'est le bon moment pour acheter.",
        "alertTitle": "Alerte prix", "alertWait": "Un instant…", "alertSaving": "Nous enregistrons votre réponse.",
        "alertGo": "Aller sur guitle", "alertBad": ["Lien invalide", "Copiez le lien complet de l'e-mail et réessayez."],
        "alertDone": ["Alerte confirmée !", "Nous vous écrirons dès que le prix baissera. Chaque e-mail contient un lien de désinscription."],
        "alertGone": ["Alerte supprimée", "Vous ne recevrez plus d'e-mails pour cette alerte. Votre adresse a été effacée de notre liste."],
        "alertMissing": ["Alerte introuvable", "Elle a peut-être déjà été confirmée ou supprimée, ou plus de 7 jours se sont écoulés sans "
                                                "confirmation. Besoin d'aide ? Écrivez-nous à hola@guitle.com."],
        "js": {"loadErr": "Impossible de charger le catalogue.", "allBrands": "Toutes les marques", "all": "Toutes", "low": "Prix bas",
               "save": "−{v}", "lh": "gaucher", "store": "magasin", "stores": "magasins",
               "empty": "Aucune {many} avec ces filtres.", "more": "Voir plus ({n} restantes)",
               "meta": "{a} sur {b} {many} · {m} comparables dans plusieurs magasins · mis à jour le {d}", "best": "meilleur prix",
               "inStock": "en stock", "noStock": "épuisé", "goLong": "Voir le magasin", "goShort": "Voir", "close": "Fermer",
               "inAt": "chez {s}", "saveMax": " · jusqu'à {v} de moins que le plus cher", "atLow": "À son prix le plus bas",
               "lowTag": "Prix le plus bas relevé : {v}", "storesH": "Magasins", "evolH": "Évolution du prix",
               "histErr": "Impossible de charger l'historique.", "histSoon": "L'historique se complétera au fil des prochains relevés.",
               "many": "guitares",
               "types": {"Semihueca": "Demi-caisse", "Moderna / Metal": "Moderne / Metal", "Otras": "Autres",
                         "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12 cordes",
                         "Tamaño reducido": "Taille réduite", "Clásica": "Classique", "Flamenca": "Flamenco",
                         "Electroclásica": "Électro-classique"},
               "wait": "Nous suivons ce modèle depuis {n} {days}", "day": "jour", "days": "jours",
               "waitSub": "Le verdict sera plus fiable après quelques semaines d'historique.",
               "min": "Prix le plus bas relevé", "minSub": "Nous ne l'avons jamais vue moins chère.",
               "minBelow": " {p} % sous sa moyenne sur 30 jours.",
               "good": "Bon moment : {p} % sous son prix moyen", "goodSub": "Moyenne des 30 derniers jours : {avg}.",
               "bad": "Elle est actuellement {p} % plus chère que d'habitude",
               "badSub": "Si vous n'êtes pas pressé, attendez : sa moyenne sur 30 jours est de {avg} et son prix le plus bas, {min}.",
               "normal": "Prix normal", "normalSub": "Dans la moyenne des 30 derniers jours ({avg}). Prix le plus bas relevé : {min}.",
               "today": "prix du jour", "lowest": "plus bas historique ({d})", "highest": "plus haut historique",
               "avg": "moyenne {n} jours", "since": "Suivi depuis le {d}",
               "noHist": "Pas encore d'historique de prix.", "pvp": "Prix officiel", "bestLine": "Meilleur prix",
               "alertOpen": "Prévenez-moi si le prix baisse", "emailPh": "vous@exemple.fr", "emailLabel": "Votre e-mail",
               "targetPh": "Prix max. (facultatif)", "targetLabel": "Prix cible en euros", "alertBtn": "Me prévenir",
               "alertLegal": "Gratuit et sans inscription. En cliquant sur « Me prévenir », vous acceptez la "
                             "<a href=\"/fr/legal.html#confidentialite\">politique de confidentialité</a> : votre e-mail ne sert qu'à "
                             "cette alerte et vous vous désinscrivez en un clic.",
               "alertOk": "<b>C'est fait !</b> Vous allez recevoir dans quelques minutes un e-mail à {email} pour confirmer l'alerte "
                          "(pensez à vérifier vos spams).",
               "alertErr": "Impossible d'enregistrer l'alerte. Vérifiez l'e-mail et réessayez."},
        "mail": {"tagline": "guitares au meilleur prix",
                 "footer": "guitle compare chaque jour les prix des magasins de musique. Vous recevez cet e-mail car vous avez demandé "
                           "une alerte sur guitle.com. Responsable : Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Confidentialité", "confirmSubject": "Confirmez votre alerte prix guitle",
                 "confirmTitle": "Confirmez votre alerte prix", "asked": "Vous avez demandé à être prévenu quand le prix baisse{target} :",
                 "below": " sous <b>{v}</b>", "confirmAsk": "Confirmez que vous souhaitez recevoir l'alerte à cette adresse :",
                 "confirmBtn": "Confirmer l'alerte",
                 "notYou": "Si ce n'est pas vous, ne faites rien : sans confirmation, l'alerte s'efface d'elle-même au bout de 7 jours.",
                 "dropSubject": "Le prix a baissé : {name} à {price}", "dropTitle": "Le prix a baissé !", "nowAt": "chez {s} · avant {v}",
                 "seeAll": "Voir les prix dans tous les magasins",
                 "check": "Les prix changent chaque jour : vérifiez-le sur le site du magasin avant d'acheter. Ça ne vous intéresse plus ?",
                 "stop": "Ne plus recevoir cette alerte"},
    },
    "it": {
        "tagline": "chitarre al miglior prezzo", "homeLabel": "guitle, home",
        "homeTitle": "guitle · comparatore di prezzi di chitarre",
        "homeDesc": "guitle è un comparatore di prezzi di chitarre: elettriche, acustiche e classiche nei negozi che vendono in "
                    "Italia, con lo storico dei prezzi di ogni modello.",
        "h1": "La tua chitarra, <span>al miglior prezzo</span><small>Comparatore di prezzi di chitarre</small>",
        "searchPh": "Cerca: strat, les paul, yamaha, ibanez…", "searchBtn": "Cerca", "searchLabel": "Cerca una chitarra",
        "guitars": "chitarre", "storesWord": "negozi", "catalog": "Catalogo",
        "dealsH": "Le differenze più grandi tra negozi", "dealsBadge": "−{p} % vs. il più caro",
        "catsH": "Esplora per categoria", "soon": "presto", "storesH": "Negozi che confrontiamo",
        "howH": "Come funziona",
        "steps": ["Ogni giorno controlliamo prezzo, disponibilità e foto di ogni chitarra nei negozi che vendono in Italia.",
                  "Conserviamo lo storico, così sai se un prezzo è davvero buono o se di solito è più basso.",
                  "Se vuoi, ti avvisiamo via e-mail quando il prezzo scende."],
        "affiliate": "Alcuni link ai negozi sono link di affiliazione: se acquisti, guitle può ricevere una commissione, senza costi per te.",
        "legal": "Note legali", "privacy": "Privacy", "cookies": "Cookie", "otherCountries": "guitle in altri paesi:",
        "updated": "Dati aggiornati al {d}", "home": "Home",
        "kinds": {"electrica": ("Chitarre elettriche", "Elettriche", "Cerca tra le elettriche: modello, marca, colore…"),
                  "acustica": ("Chitarre acustiche", "Acustiche", "Cerca tra le acustiche: modello, marca, legno…"),
                  "clasica": ("Chitarre classiche", "Classiche", "Cerca tra le classiche: modello, marca, flamenco…")},
        "anyPrice": "Qualsiasi prezzo", "upTo": "Fino a {v}", "over": "Oltre {v}", "brandLabel": "Marca", "priceLabel": "Prezzo",
        "showLabel": "Mostra", "showAll": "Tutte", "showMulti": "In più negozi", "showStock": "Disponibili",
        "showLow": "Al prezzo minimo", "showLh": "Solo mancine", "loading": "Caricamento del catalogo…", "sortLabel": "Ordina",
        "sorts": ["Più negozi", "Prezzo più basso", "Prezzo più alto", "Maggior risparmio tra negozi", "Nome"], "moreBtn": "Mostra altre",
        "sections": "Sezioni", "searchAria": "Cerca",
        "bestPrice": "miglior prezzo", "inStock": "disponibile", "noStock": "non disponibile", "goLong": "Vai al negozio", "goShort": "Vai",
        "store": "negozio", "stores": "negozi", "lh": "mancina", "storesH3": "Negozi", "historyH3": "Storico dei prezzi",
        "amazon": "", "titleFrom": "{name}: prezzo da {price} {where}", "inN": "in {n} negozi", "inS": "da {s}",
        "whereMany": "da {s} · {n} negozi", "whereDiff": ", fino a {d} di differenza",
        "desc": "{name} da {price} da {s}. Confronta il prezzo in {n} {stores} ({list}) e guarda lo storico per capire se è il momento "
                "giusto per comprare.",
        "alertTitle": "Avviso di prezzo", "alertWait": "Un momento…", "alertSaving": "Stiamo salvando la tua risposta.",
        "alertGo": "Vai su guitle", "alertBad": ["Link non valido", "Copia il link completo dell'e-mail e riprova."],
        "alertDone": ["Avviso confermato!", "Ti scriveremo appena il prezzo scende. Ogni e-mail contiene un link per disiscriverti."],
        "alertGone": ["Avviso eliminato", "Non riceverai più e-mail per questo avviso. Abbiamo cancellato il tuo indirizzo dalla lista."],
        "alertMissing": ["Avviso non trovato", "Forse era già confermato o eliminato, o sono passati più di 7 giorni senza conferma. "
                                               "Per aiuto scrivici a hola@guitle.com."],
        "js": {"loadErr": "Impossibile caricare il catalogo.", "allBrands": "Tutte le marche", "all": "Tutte", "low": "Minimo",
               "save": "Risparmi {v}", "lh": "mancina", "store": "negozio", "stores": "negozi",
               "empty": "Nessuna {many} con questi filtri.", "more": "Mostra altre ({n} rimanenti)",
               "meta": "{a} di {b} {many} · {m} confrontabili in più negozi · aggiornato al {d}", "best": "miglior prezzo",
               "inStock": "disponibile", "noStock": "non disponibile", "goLong": "Vai al negozio", "goShort": "Vai", "close": "Chiudi",
               "inAt": "da {s}", "saveMax": " · fino a {v} in meno rispetto al più caro", "atLow": "Al minimo registrato",
               "lowTag": "Minimo registrato: {v}", "storesH": "Negozi", "evolH": "Andamento del prezzo",
               "histErr": "Impossibile caricare lo storico.", "histSoon": "Lo storico si completerà con le prossime rilevazioni.",
               "many": "chitarre",
               "types": {"Semihueca": "Semi-hollow", "Moderna / Metal": "Moderna / Metal", "Otras": "Altre",
                         "Auditorio / Concierto": "Auditorium / Concerto", "12 cuerdas": "12 corde",
                         "Tamaño reducido": "Misura ridotta", "Clásica": "Classica", "Flamenca": "Flamenco",
                         "Electroclásica": "Classica elettrificata"},
               "wait": "Seguiamo questo modello da {n} {days}", "day": "giorno", "days": "giorni",
               "waitSub": "Il verdetto sarà più affidabile con qualche settimana di storico.",
               "min": "Prezzo minimo registrato", "minSub": "Non l'abbiamo mai vista più economica.",
               "minBelow": " È il {p} % sotto la media degli ultimi 30 giorni.",
               "good": "Buon momento: {p} % sotto il prezzo medio", "goodSub": "Media degli ultimi 30 giorni: {avg}.",
               "bad": "Ora costa il {p} % più del solito",
               "badSub": "Se non hai fretta, aspetta: la media di 30 giorni è {avg} e il minimo {min}.",
               "normal": "Prezzo nella norma", "normalSub": "In linea con la media di 30 giorni ({avg}). Minimo registrato: {min}.",
               "today": "prezzo oggi", "lowest": "minimo storico ({d})", "highest": "massimo storico", "avg": "media {n} giorni",
               "since": "La seguiamo dal {d}", "noHist": "Non c'è ancora uno storico dei prezzi.", "pvp": "Prezzo ufficiale",
               "bestLine": "Miglior prezzo", "alertOpen": "Avvisami se il prezzo scende", "emailPh": "tu@esempio.it",
               "emailLabel": "La tua e-mail", "targetPh": "Prezzo max. (facoltativo)", "targetLabel": "Prezzo obiettivo in euro",
               "alertBtn": "Avvisami",
               "alertLegal": "Gratis e senza registrazione. Cliccando su «Avvisami» accetti l'<a href=\"/it/legal.html#privacy\">informativa "
                             "sulla privacy</a>: useremo la tua e-mail solo per questo avviso e ti disiscrivi con un clic.",
               "alertOk": "<b>Fatto!</b> Tra pochi minuti riceverai un'e-mail a {email} per confermare l'avviso (controlla anche lo spam).",
               "alertErr": "Impossibile salvare l'avviso. Controlla l'e-mail e riprova."},
        "mail": {"tagline": "chitarre al miglior prezzo",
                 "footer": "guitle confronta ogni giorno i prezzi dei negozi di musica. Ricevi questa e-mail perché hai chiesto un avviso "
                           "su guitle.com. Titolare: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Privacy", "confirmSubject": "Conferma il tuo avviso di prezzo su guitle",
                 "confirmTitle": "Conferma il tuo avviso di prezzo", "asked": "Hai chiesto di essere avvisato quando il prezzo scende{target}:",
                 "below": " sotto <b>{v}</b>", "confirmAsk": "Conferma di voler ricevere l'avviso a questo indirizzo:",
                 "confirmBtn": "Conferma l'avviso",
                 "notYou": "Se non sei stato tu, non fare nulla: senza conferma, l'avviso si cancella da solo dopo 7 giorni.",
                 "dropSubject": "Prezzo sceso: {name} a {price}", "dropTitle": "Il prezzo è sceso!", "nowAt": "da {s} · prima {v}",
                 "seeAll": "Vedi i prezzi in tutti i negozi",
                 "check": "I prezzi cambiano ogni giorno: verifica sul sito del negozio prima di acquistare. Non ti interessa più?",
                 "stop": "Non ricevere più questo avviso"},
    },
    "en": {
        "tagline": "guitars at the best price", "homeLabel": "guitle, home",
        "homeTitle": "guitle · guitar price comparison",
        "homeDesc": "guitle compares guitar prices: electric, acoustic and classical guitars across UK music shops, with the price "
                    "history of every model.",
        "h1": "Your guitar, <span>at the best price</span><small>Guitar price comparison</small>",
        "searchPh": "Search: strat, les paul, yamaha, ibanez…", "searchBtn": "Search", "searchLabel": "Search for a guitar",
        "guitars": "guitars", "storesWord": "shops", "catalog": "Catalogue",
        "dealsH": "Biggest price gaps between shops", "dealsBadge": "−{p}% vs. the dearest",
        "catsH": "Browse by category", "soon": "coming soon", "storesH": "Shops we compare",
        "howH": "How it works",
        "steps": ["Every day we check the price, stock and photo of every guitar in the shops that sell in the UK.",
                  "We keep the price history so you can tell whether a price is genuinely good or usually lower.",
                  "If you like, we'll email you when the price drops."],
        "affiliate": "Some links to shops are affiliate links: if you buy, guitle may earn a commission at no extra cost to you.",
        "legal": "Legal notice", "privacy": "Privacy", "cookies": "Cookies", "otherCountries": "guitle in other countries:",
        "updated": "Data updated on {d}", "home": "Home",
        "kinds": {"electrica": ("Electric guitars", "Electric", "Search electric guitars: model, brand, colour…"),
                  "acustica": ("Acoustic guitars", "Acoustic", "Search acoustic guitars: model, brand, tonewood…"),
                  "clasica": ("Classical guitars", "Classical", "Search classical guitars: model, brand, flamenco…")},
        "anyPrice": "Any price", "upTo": "Up to {v}", "over": "Over {v}", "brandLabel": "Brand", "priceLabel": "Price",
        "showLabel": "Show", "showAll": "All", "showMulti": "In several shops", "showStock": "In stock",
        "showLow": "At their lowest price", "showLh": "Left-handed only", "loading": "Loading catalogue…", "sortLabel": "Sort",
        "sorts": ["Most shops", "Lowest price", "Highest price", "Biggest saving between shops", "Name"], "moreBtn": "Show more",
        "sections": "Sections", "searchAria": "Search",
        "bestPrice": "best price", "inStock": "in stock", "noStock": "out of stock", "goLong": "Go to shop", "goShort": "Go",
        "store": "shop", "stores": "shops", "lh": "left-handed", "storesH3": "Shops", "historyH3": "Price history",
        "amazon": "", "titleFrom": "{name}: price from {price} {where}", "inN": "in {n} shops", "inS": "at {s}",
        "whereMany": "at {s} · {n} shops", "whereDiff": ", up to {d} difference",
        "desc": "{name} from {price} at {s}. Compare its price in {n} {stores} ({list}) and check the price history to see if "
                "it's a good time to buy.",
        "alertTitle": "Price alert", "alertWait": "One moment…", "alertSaving": "We're saving your answer.",
        "alertGo": "Go to guitle", "alertBad": ["Invalid link", "Copy the full link from the email and try again."],
        "alertDone": ["Alert confirmed!", "We'll email you as soon as the price drops. Every email has an unsubscribe link."],
        "alertGone": ["Alert deleted", "You won't get any more emails for this alert. We've removed your address from our list."],
        "alertMissing": ["Alert not found", "It may already have been confirmed or deleted, or more than 7 days passed without "
                                            "confirmation. Need help? Email us at hola@guitle.com."],
        "js": {"loadErr": "Couldn't load the catalogue.", "allBrands": "All brands", "all": "All", "low": "Lowest",
               "save": "Save {v}", "lh": "left-handed", "store": "shop", "stores": "shops",
               "empty": "No {many} match those filters.", "more": "Show more ({n} left)",
               "meta": "{a} of {b} {many} · {m} comparable across shops · updated {d}", "best": "best price",
               "inStock": "in stock", "noStock": "out of stock", "goLong": "Go to shop", "goShort": "Go", "close": "Close",
               "inAt": "at {s}", "saveMax": " · up to {v} less than the dearest", "atLow": "At its lowest recorded price",
               "lowTag": "Lowest recorded: {v}", "storesH": "Shops", "evolH": "Price history",
               "histErr": "Couldn't load the price history.", "histSoon": "The price history will fill in over the coming days.",
               "many": "guitars",
               "types": {"ST": "S-style", "T": "T-style", "Semihueca": "Semi-hollow", "Offset / Retro": "Offset / Retro",
                         "Moderna / Metal": "Modern / Metal", "Otras": "Other", "Auditorio / Concierto": "Auditorium / Concert",
                         "12 cuerdas": "12-string", "Tamaño reducido": "Small body", "Clásica": "Classical",
                         "Flamenca": "Flamenco", "Electroclásica": "Electro-classical"},
               "wait": "We've been tracking this model for {n} {days}", "day": "day", "days": "days",
               "waitSub": "The verdict gets more reliable after a few weeks of history.",
               "min": "Lowest price on record", "minSub": "We've never seen it cheaper.", "minBelow": " {p}% below its 30-day average.",
               "good": "Good time to buy: {p}% below its average price", "goodSub": "30-day average: {avg}.",
               "bad": "It's {p}% dearer than usual right now",
               "badSub": "If you're not in a hurry, wait: its 30-day average is {avg} and its lowest, {min}.",
               "normal": "Normal price", "normalSub": "In line with its 30-day average ({avg}). Lowest on record: {min}.",
               "today": "price today", "lowest": "all-time low ({d})", "highest": "all-time high", "avg": "{n}-day average",
               "since": "Tracked since {d}", "noHist": "No price history yet.", "pvp": "RRP", "bestLine": "Best price",
               "alertOpen": "Tell me if the price drops", "emailPh": "you@example.com", "emailLabel": "Your email",
               "targetPh": "Max. price (optional)", "targetLabel": "Target price in pounds", "alertBtn": "Alert me",
               "alertLegal": "Free, no sign-up. By clicking “Alert me” you accept our <a href=\"/uk/legal.html#privacy\">privacy "
                             "policy</a>: we'll only use your email for this alert, and you can unsubscribe with one click.",
               "alertOk": "<b>Done!</b> In a few minutes you'll get an email at {email} to confirm the alert (check your spam folder too).",
               "alertErr": "We couldn't save the alert. Check the email address and try again."},
        "mail": {"tagline": "guitars at the best price",
                 "footer": "guitle compares music shop prices every day. You're getting this email because you asked for an alert "
                           "on guitle.com. Data controller: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Privacy", "confirmSubject": "Confirm your guitle price alert",
                 "confirmTitle": "Confirm your price alert", "asked": "You asked us to tell you when the price drops{target}:",
                 "below": " below <b>{v}</b>", "confirmAsk": "Please confirm you want to receive the alert at this address:",
                 "confirmBtn": "Confirm the alert",
                 "notYou": "If this wasn't you, do nothing: unconfirmed alerts are deleted automatically after 7 days.",
                 "dropSubject": "Price drop: {name} now {price}", "dropTitle": "The price has dropped!", "nowAt": "at {s} · was {v}",
                 "seeAll": "See prices in every shop",
                 "check": "Prices change daily: check on the shop's site before buying. No longer interested?",
                 "stop": "Stop this alert"},
    },
    "de": {
        "tagline": "Gitarren zum besten Preis", "homeLabel": "guitle, Startseite",
        "homeTitle": "guitle · Gitarren-Preisvergleich",
        "homeDesc": "guitle vergleicht Gitarrenpreise: E-Gitarren, Westerngitarren und Konzertgitarren in den Shops, die nach "
                    "Deutschland liefern, mit dem Preisverlauf jedes Modells.",
        "h1": "Deine Gitarre, <span>zum besten Preis</span><small>Gitarren-Preisvergleich</small>",
        "searchPh": "Suche: Strat, Les Paul, Yamaha, Ibanez…", "searchBtn": "Suchen", "searchLabel": "Gitarre suchen",
        "guitars": "Gitarren", "storesWord": "Shops", "catalog": "Katalog",
        "dealsH": "Die größten Preisunterschiede zwischen Shops", "dealsBadge": "−{p} % ggü. dem teuersten",
        "catsH": "Nach Kategorie stöbern", "soon": "bald", "storesH": "Shops im Vergleich",
        "howH": "So funktioniert's",
        "steps": ["Jeden Tag prüfen wir Preis, Verfügbarkeit und Foto jeder Gitarre in den Shops, die nach Deutschland liefern.",
                  "Wir speichern den Preisverlauf, damit du siehst, ob ein Preis wirklich gut ist oder sonst niedriger liegt.",
                  "Auf Wunsch schicken wir dir eine E-Mail, wenn der Preis fällt."],
        "affiliate": "Einige Links zu Shops sind Affiliate-Links: Wenn du kaufst, kann guitle eine Provision erhalten – ohne Mehrkosten für dich.",
        "legal": "Impressum", "privacy": "Datenschutz", "cookies": "Cookies", "otherCountries": "guitle in anderen Ländern:",
        "updated": "Daten aktualisiert am {d}", "home": "Startseite",
        "kinds": {"electrica": ("E-Gitarren", "E-Gitarren", "In E-Gitarren suchen: Modell, Marke, Farbe…"),
                  "acustica": ("Westerngitarren", "Western", "In Westerngitarren suchen: Modell, Marke, Holz…"),
                  "clasica": ("Konzertgitarren", "Konzert", "In Konzertgitarren suchen: Modell, Marke, Flamenco…"),
                  "bajo": ("E-Bässe und Akustikbässe", "Bässe", "In Bässen suchen: Modell, Marke, 5-Saiter…"),
                  "ampli": ("Gitarren- und Bassverstärker", "Verstärker", "In Verstärkern suchen: Modell, Marke, Combo, Topteil…"),
                  "pedal": ("Effektpedale", "Effekte", "In Effektpedalen suchen: Modell, Marke, Effekt…"),
                  "teclado": ("Keyboards und Digitalpianos", "Keyboards", "In Keyboards suchen: Modell, Marke…"),
                  "micro": ("Mikrofone", "Mikrofone", "In Mikrofonen suchen: Modell, Marke, Typ…"),
                  "estuche": ("Koffer und Gigbags", "Koffer", "In Koffern und Gigbags suchen: Modell, Marke…"),
                  "varios": ("Gitarrenzubehör", "Zubehör", "Im Zubehör suchen: Saiten, Plektren, Gurte, Kabel…")},
        # Lo que se cuenta en cada categoría de equipo (portada y lista) y, si no son solo guitarras, el total.
        "nouns": {"bajo": "Bässe", "ampli": "Verstärker", "pedal": "Pedale", "teclado": "Keyboards", "micro": "Mikrofone",
                  "estuche": "Koffer", "varios": "Artikel"},
        "allWord": "Produkte",
        "anyPrice": "Jeder Preis", "upTo": "Bis {v}", "over": "Über {v}", "brandLabel": "Marke", "priceLabel": "Preis",
        "showLabel": "Anzeigen", "showAll": "Alle", "showMulti": "In mehreren Shops", "showStock": "Auf Lager",
        "showLow": "Zum Tiefstpreis", "showLh": "Nur Linkshänder", "loading": "Katalog wird geladen…", "sortLabel": "Sortieren",
        "sorts": ["Meiste Shops", "Niedrigster Preis", "Höchster Preis", "Größte Ersparnis zwischen Shops", "Name"],
        "moreBtn": "Mehr anzeigen", "sections": "Bereiche", "searchAria": "Suchen",
        "bestPrice": "Bestpreis", "inStock": "auf Lager", "noStock": "nicht auf Lager", "goLong": "Zum Shop", "goShort": "Shop",
        "store": "Shop", "stores": "Shops", "lh": "Linkshänder", "storesH3": "Shops", "historyH3": "Preisverlauf",
        "amazon": "", "titleFrom": "{name}: Preis ab {price} {where}", "inN": "in {n} Shops", "inS": "bei {s}",
        "whereMany": "bei {s} · {n} Shops", "whereDiff": ", bis zu {d} Unterschied",
        "desc": "{name} ab {price} bei {s}. Vergleiche den Preis in {n} {stores} ({list}) und sieh dir den Preisverlauf an, um zu "
                "wissen, ob jetzt ein guter Zeitpunkt zum Kauf ist.",
        "alertTitle": "Preisalarm", "alertWait": "Einen Moment…", "alertSaving": "Wir speichern deine Antwort.",
        "alertGo": "Zu guitle", "alertBad": ["Ungültiger Link", "Kopiere den vollständigen Link aus der E-Mail und versuche es erneut."],
        "alertDone": ["Preisalarm bestätigt!", "Wir schreiben dir, sobald der Preis fällt. Jede E-Mail enthält einen Abmeldelink."],
        "alertGone": ["Preisalarm gelöscht", "Du bekommst zu diesem Alarm keine E-Mails mehr. Deine Adresse wurde aus unserer Liste gelöscht."],
        "alertMissing": ["Preisalarm nicht gefunden", "Vielleicht war er schon bestätigt oder gelöscht, oder es sind mehr als 7 Tage ohne "
                                                      "Bestätigung vergangen. Hilfe? Schreib uns an hola@guitle.com."],
        "js": {"loadErr": "Der Katalog konnte nicht geladen werden.", "allBrands": "Alle Marken", "all": "Alle", "low": "Tiefstpreis",
               "save": "Spare {v}", "lh": "Linkshänder", "store": "Shop", "stores": "Shops",
               "empty": "Keine {many} mit diesen Filtern.", "more": "Mehr anzeigen (noch {n})",
               "meta": "{a} von {b} {many} · {m} in mehreren Shops vergleichbar · aktualisiert am {d}", "best": "Bestpreis",
               "inStock": "auf Lager", "noStock": "nicht auf Lager", "goLong": "Zum Shop", "goShort": "Shop", "close": "Schließen",
               "inAt": "bei {s}", "saveMax": " · bis zu {v} günstiger als der teuerste", "atLow": "Auf dem Tiefstpreis",
               "lowTag": "Tiefstpreis: {v}", "storesH": "Shops", "evolH": "Preisverlauf",
               "histErr": "Der Preisverlauf konnte nicht geladen werden.", "histSoon": "Der Preisverlauf füllt sich mit den nächsten Abfragen.",
               "many": "Gitarren",
               "types": {"ST": "ST-Modelle", "T": "T-Modelle", "Semihueca": "Halbakustik", "Moderna / Metal": "Modern / Metal",
                         "Otras": "Andere", "Auditorio / Concierto": "Auditorium / Konzert", "12 cuerdas": "12-saitig",
                         "Tamaño reducido": "Kleine Größe", "Clásica": "Klassisch", "Flamenca": "Flamenco",
                         "Electroclásica": "Elektro-Klassik",
                         "4 cuerdas": "4-Saiter", "5 cuerdas": "5-Saiter", "6 cuerdas o más": "6-Saiter und mehr",
                         "Acústico": "Akustikbass", "Fretless": "Fretless", "Escala corta": "Short Scale", "Combo": "Combos",
                         "Cabezal": "Topteile", "Pantalla": "Boxen", "Para bajo": "Für Bass", "Para acústica": "Für Akustikgitarre",
                         "De auriculares y portátil": "Kopfhörer- und Mini-Amps", "Para eléctrica": "Für E-Gitarre",
                         "Para clásica": "Für Konzertgitarre", "Overdrive y distorsión": "Overdrive und Distortion",
                         "Modulación": "Modulation", "Compresor": "Kompressor", "Wah y volumen": "Wah und Volume",
                         "Octavador y pitch": "Oktaver und Pitch", "Ecualizador": "Equalizer", "Puerta de ruido": "Noise Gate",
                         "Sintetizador": "Synthesizer", "Afinador": "Stimmgerät", "Multiefectos": "Multieffekte",
                         "Reverb": "Hall", "Piano digital": "Digitalpianos", "Teclado portátil": "Keyboards",
                         "Piano de escenario": "Stagepianos", "Controlador MIDI": "MIDI-Controller", "Piano acústico": "Klaviere",
                         "Dinámico": "Dynamisch", "Condensador": "Kondensator", "Inalámbrico": "Funk",
                         "Para instrumento": "Instrumentenmikrofone", "De cinta": "Bändchen", "Cuerdas": "Saiten",
                         "Púas": "Plektren", "Correas": "Gurte", "Cables": "Kabel", "Afinadores": "Stimmgeräte",
                         "Cejillas": "Kapodaster", "Soportes": "Ständer", "Pastillas": "Tonabnehmer", "Recambios": "Ersatzteile",
                         "Mantenimiento": "Pflege"},
               "wait": "Wir beobachten dieses Modell seit {n} {days}", "day": "Tag", "days": "Tagen",
               "waitSub": "Die Einschätzung wird nach ein paar Wochen Preisverlauf zuverlässiger.",
               "min": "Niedrigster erfasster Preis", "minSub": "So günstig haben wir sie noch nie gesehen.",
               "minBelow": " {p} % unter dem 30-Tage-Durchschnitt.",
               "good": "Guter Zeitpunkt: {p} % unter dem Durchschnittspreis", "goodSub": "Durchschnitt der letzten 30 Tage: {avg}.",
               "bad": "Gerade {p} % teurer als üblich",
               "badSub": "Wenn du es nicht eilig hast, warte: Der 30-Tage-Durchschnitt liegt bei {avg}, der Tiefstpreis bei {min}.",
               "normal": "Normaler Preis", "normalSub": "Im Rahmen des 30-Tage-Durchschnitts ({avg}). Tiefstpreis: {min}.",
               "today": "Preis heute", "lowest": "Tiefstpreis ({d})", "highest": "Höchstpreis", "avg": "Durchschnitt {n} Tage",
               "since": "Beobachtet seit {d}", "noHist": "Noch kein Preisverlauf.", "pvp": "UVP", "bestLine": "Bestpreis",
               "alertOpen": "Benachrichtige mich, wenn der Preis fällt", "emailPh": "du@beispiel.de", "emailLabel": "Deine E-Mail",
               "targetPh": "Max. Preis (optional)", "targetLabel": "Zielpreis in Euro", "alertBtn": "Benachrichtigen",
               "alertLegal": "Kostenlos und ohne Anmeldung. Mit Klick auf „Benachrichtigen“ akzeptierst du die "
                             "<a href=\"/de/legal.html#datenschutz\">Datenschutzerklärung</a>: Wir nutzen deine E-Mail nur für diesen "
                             "Alarm, abmelden kannst du dich mit einem Klick.",
               "alertOk": "<b>Erledigt!</b> In wenigen Minuten bekommst du eine E-Mail an {email}, um den Alarm zu bestätigen "
                          "(schau auch im Spam-Ordner nach).",
               "alertErr": "Der Alarm konnte nicht gespeichert werden. Prüfe die E-Mail-Adresse und versuche es erneut."},
        "mail": {"tagline": "Gitarren zum besten Preis",
                 "footer": "guitle vergleicht täglich die Preise von Musikgeschäften. Du erhältst diese E-Mail, weil du auf guitle.com "
                           "einen Preisalarm angefordert hast. Verantwortlich: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Datenschutz", "confirmSubject": "Bestätige deinen guitle-Preisalarm",
                 "confirmTitle": "Bestätige deinen Preisalarm", "asked": "Du möchtest benachrichtigt werden, wenn der Preis fällt{target}:",
                 "below": " unter <b>{v}</b>", "confirmAsk": "Bitte bestätige, dass du den Alarm an diese Adresse erhalten möchtest:",
                 "confirmBtn": "Alarm bestätigen",
                 "notYou": "Wenn du das nicht warst, tu nichts: Unbestätigte Alarme werden nach 7 Tagen automatisch gelöscht.",
                 "dropSubject": "Preis gesunken: {name} jetzt {price}", "dropTitle": "Der Preis ist gesunken!", "nowAt": "bei {s} · vorher {v}",
                 "seeAll": "Preise in allen Shops ansehen",
                 "check": "Preise ändern sich täglich: Prüfe sie vor dem Kauf im Shop. Kein Interesse mehr?",
                 "stop": "Diesen Alarm abbestellen"},
    },
    "br": {
        "tagline": "guitarras e violões pelo melhor preço", "homeLabel": "guitle, início",
        "homeTitle": "guitle · comparador de preços de guitarras e violões",
        "homeDesc": "O guitle compara preços de guitarras e violões nas lojas de música do Brasil, com o histórico de preços de cada modelo.",
        "h1": "Sua guitarra, <span>pelo melhor preço</span><small>Comparador de preços de guitarras e violões</small>",
        "searchPh": "Busque: strat, les paul, tagima, giannini…", "searchBtn": "Buscar", "searchLabel": "Buscar guitarra ou violão",
        "guitars": "instrumentos", "storesWord": "lojas", "catalog": "Catálogo",
        "dealsH": "Maiores diferenças entre lojas", "dealsBadge": "−{p}% vs. a mais cara",
        "catsH": "Explore por categoria", "soon": "em breve", "storesH": "Lojas que comparamos",
        "howH": "Como funciona",
        "steps": ["Todos os dias conferimos o preço, o estoque e a foto de cada guitarra e violão nas lojas do Brasil.",
                  "Guardamos o histórico para você saber se um preço é bom de verdade ou se costuma estar mais baixo.",
                  "Se quiser, avisamos você por e-mail quando o preço baixar."],
        "affiliate": "Alguns links para lojas são de afiliado: se você comprar, o guitle pode receber uma comissão, sem custo para você.",
        "legal": "Aviso legal", "privacy": "Privacidade", "cookies": "Cookies", "otherCountries": "guitle em outros países:",
        "updated": "Dados atualizados em {d}", "home": "Início",
        "kinds": {"electrica": ("Guitarras", "Guitarras", "Busque nas guitarras: modelo, marca, cor…"),
                  "acustica": ("Violões de aço e folk", "Violões aço", "Busque nos violões: modelo, marca, madeira…"),
                  "clasica": ("Violões de nylon", "Violões nylon", "Busque nos violões de nylon: modelo, marca…"),
                  "bajo": ("Contrabaixos", "Baixos", "Busque nos baixos: modelo, marca, cordas…"),
                  "ampli": ("Amplificadores", "Amplis", "Busque nos amplificadores: modelo, marca, potência…"),
                  "pedal": ("Pedais de efeito", "Pedais", "Busque nos pedais: modelo, marca, efeito…"),
                  "teclado": ("Teclados e pianos", "Teclados", "Busque nos teclados: modelo, marca…"),
                  "micro": ("Microfones", "Microfones", "Busque nos microfones: modelo, marca, tipo…"),
                  "estuche": ("Cases, bags e capas", "Cases", "Busque nos cases e bags: modelo, marca…"),
                  "varios": ("Acessórios", "Acessórios", "Busque nos acessórios: cordas, palhetas, correias, cabos…")},
        "anyPrice": "Qualquer preço", "upTo": "Até {v}", "over": "Acima de {v}", "brandLabel": "Marca", "priceLabel": "Preço",
        "showLabel": "Mostrar", "showAll": "Todos", "showMulti": "Em várias lojas", "showStock": "Em estoque",
        "showLow": "No menor preço", "showLh": "Só canhotos", "loading": "Carregando o catálogo…", "sortLabel": "Ordenar",
        "sorts": ["Mais lojas", "Menor preço", "Maior preço", "Maior economia entre lojas", "Nome"], "moreBtn": "Ver mais",
        "sections": "Seções", "searchAria": "Buscar",
        "bestPrice": "melhor preço", "inStock": "em estoque", "noStock": "sem estoque", "goLong": "Ir para a loja", "goShort": "Ir",
        "store": "loja", "stores": "lojas", "lh": "canhoto", "storesH3": "Lojas", "historyH3": "Histórico de preços",
        "amazon": "", "titleFrom": "{name}: preço a partir de {price} {where}", "inN": "em {n} lojas", "inS": "na {s}",
        "whereMany": "na {s} · {n} lojas", "whereDiff": ", até {d} de diferença",
        "desc": "{name} a partir de {price} na {s}. Compare o preço em {n} {stores} ({list}) e veja o histórico para saber se é "
                "uma boa hora para comprar.",
        "alertTitle": "Alerta de preço", "alertWait": "Um momento…", "alertSaving": "Estamos salvando sua resposta.",
        "alertGo": "Ir para o guitle", "alertBad": ["Link inválido", "Copie o link completo do e-mail e tente de novo."],
        "alertDone": ["Alerta confirmado!", "Vamos te avisar assim que o preço baixar. Cada e-mail tem um link para cancelar."],
        "alertGone": ["Alerta apagado", "Você não vai mais receber e-mails deste alerta. Apagamos seu e-mail da nossa lista."],
        "alertMissing": ["Não encontramos o alerta", "Talvez já estivesse confirmado ou apagado, ou passaram mais de 7 dias sem "
                                                    "confirmação. Precisa de ajuda? Escreva para hola@guitle.com."],
        "js": {"loadErr": "Não foi possível carregar o catálogo.", "allBrands": "Todas as marcas", "all": "Todos", "low": "Menor preço",
               "save": "Economize {v}", "lh": "canhoto", "store": "loja", "stores": "lojas", "empty": "Não há {many} com esses filtros.",
               "more": "Ver mais ({n} restantes)", "meta": "{a} de {b} {many} · {m} comparáveis em várias lojas · atualizado em {d}",
               "best": "melhor preço", "inStock": "em estoque", "noStock": "sem estoque", "goLong": "Ir para a loja", "goShort": "Ir",
               "close": "Fechar", "inAt": "na {s}", "saveMax": " · até {v} a menos que na mais cara", "atLow": "No menor preço registrado",
               "lowTag": "Menor preço registrado: {v}", "storesH": "Lojas", "evolH": "Evolução do preço",
               "histErr": "Não foi possível carregar o histórico.", "histSoon": "O histórico vai se completando com as próximas leituras.",
               "many": "instrumentos",
               "types": {"Semihueca": "Semi-acústica", "Moderna / Metal": "Moderna / Metal", "Otras": "Outros",
                         "Auditorio / Concierto": "Auditório / Concerto", "12 cuerdas": "12 cordas", "Tamaño reducido": "Tamanho reduzido",
                         "Clásica": "Clássico", "Flamenca": "Flamenco", "Electroclásica": "Elétrico nylon",
                         "4 cuerdas": "4 cordas", "5 cuerdas": "5 cordas", "6 cuerdas o más": "6 cordas ou mais",
                         "Acústico": "Acústico", "Escala corta": "Escala curta", "Combo": "Combo / cubo", "Cabezal": "Cabeçote",
                         "Pantalla": "Caixa", "Para bajo": "Para baixo", "Para acústica": "Para violão",
                         "De auriculares y portátil": "Portátil / fone", "Para eléctrica": "Para guitarra",
                         "Para clásica": "Para violão nylon", "Overdrive y distorsión": "Overdrive e distorção",
                         "Modulación": "Modulação", "Compresor": "Compressor", "Wah y volumen": "Wah e volume",
                         "Octavador y pitch": "Oitavador e pitch", "Ecualizador": "Equalizador", "Puerta de ruido": "Noise gate",
                         "Sintetizador": "Sintetizador", "Afinador": "Afinador", "Multiefectos": "Pedaleiras e multiefeitos",
                         "Piano digital": "Piano digital", "Teclado portátil": "Teclado arranjador", "Piano de escenario": "Stage piano",
                         "Controlador MIDI": "Controlador MIDI", "Piano acústico": "Piano acústico", "Dinámico": "Dinâmico",
                         "Condensador": "Condensador", "Inalámbrico": "Sem fio", "Para instrumento": "Para instrumento",
                         "De cinta": "De fita", "Cuerdas": "Cordas", "Púas": "Palhetas", "Correas": "Correias", "Cables": "Cabos",
                         "Afinadores": "Afinadores", "Cejillas": "Capotrastes", "Soportes": "Suportes", "Pastillas": "Captadores",
                         "Recambios": "Peças de reposição", "Mantenimiento": "Limpeza e manutenção"},
               "wait": "Acompanhamos este modelo há {n} {days}", "day": "dia", "days": "dias",
               "waitSub": "O veredito fica mais confiável com algumas semanas de histórico.",
               "min": "Menor preço registrado", "minSub": "Nunca vimos mais barato.", "minBelow": " {p}% abaixo da média de 30 dias.",
               "good": "Boa hora: {p}% abaixo do preço médio", "goodSub": "Média dos últimos 30 dias: {avg}.",
               "bad": "Agora está {p}% mais caro que o normal",
               "badSub": "Se não tiver pressa, espere: a média de 30 dias é {avg} e o mínimo, {min}.",
               "normal": "Preço normal", "normalSub": "Na média dos últimos 30 dias ({avg}). Menor preço registrado: {min}.",
               "today": "preço hoje", "lowest": "menor preço ({d})", "highest": "maior preço", "avg": "média {n} dias",
               "since": "Acompanhado desde {d}", "noHist": "Ainda não há histórico de preços.", "pvp": "Preço oficial",
               "bestLine": "Melhor preço", "alertOpen": "Me avise se o preço baixar", "emailPh": "voce@email.com.br",
               "emailLabel": "Seu e-mail", "targetPh": "Preço máx. (opcional)", "targetLabel": "Preço desejado em reais",
               "alertBtn": "Me avisar",
               "alertLegal": "Grátis e sem cadastro. Ao clicar em «Me avisar» você aceita a <a href=\"/br/legal.html#privacidade\">política "
                             "de privacidade</a>: usamos seu e-mail só para este alerta e você cancela com um clique.",
               "alertOk": "<b>Pronto!</b> Em alguns minutos você vai receber um e-mail em {email} para confirmar o alerta (veja também o spam).",
               "alertErr": "Não foi possível salvar o alerta. Confira o e-mail e tente de novo."},
        "mail": {"tagline": "guitarras e violões pelo melhor preço",
                 "footer": "O guitle compara todos os dias os preços das lojas de música. Você recebe este e-mail porque pediu um alerta "
                           "em guitle.com. Responsável: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Privacidade", "confirmSubject": "Confirme seu alerta de preço no guitle",
                 "confirmTitle": "Confirme seu alerta de preço", "asked": "Você pediu para ser avisado quando o preço baixar{target}:",
                 "below": " para menos de <b>{v}</b>", "confirmAsk": "Confirme que quer receber o alerta neste endereço:",
                 "confirmBtn": "Confirmar o alerta",
                 "notYou": "Se não foi você, não faça nada: sem confirmação, o alerta é apagado sozinho em 7 dias.",
                 "dropSubject": "Baixou: {name} por {price}", "dropTitle": "O preço baixou!", "nowAt": "na {s} · antes {v}",
                 "seeAll": "Ver preços em todas as lojas",
                 "check": "Os preços mudam todo dia: confira na loja antes de comprar. Não tem mais interesse?",
                 "stop": "Parar de receber este alerta"},
    },
    "nl": {
        "tagline": "gitaren voor de beste prijs", "homeLabel": "guitle, home",
        "homeTitle": "guitle · gitaarprijzen vergelijken",
        "homeDesc": "guitle vergelijkt gitaarprijzen: elektrische, akoestische en klassieke gitaren in de winkels die in Nederland "
                    "verkopen, met de prijsgeschiedenis van elk model.",
        "h1": "Jouw gitaar, <span>voor de beste prijs</span><small>Gitaarprijzen vergelijken</small>",
        "searchPh": "Zoek: strat, les paul, yamaha, ibanez…", "searchBtn": "Zoeken", "searchLabel": "Gitaar zoeken",
        "guitars": "gitaren", "storesWord": "winkels", "catalog": "Catalogus",
        "dealsH": "De grootste prijsverschillen tussen winkels", "dealsBadge": "−{p}% t.o.v. de duurste",
        "catsH": "Bekijk per categorie", "soon": "binnenkort", "storesH": "Winkels die we vergelijken",
        "howH": "Zo werkt het",
        "steps": ["Elke dag controleren we de prijs, voorraad en foto van elke gitaar in de winkels die in Nederland verkopen.",
                  "We bewaren de prijsgeschiedenis, zodat je ziet of een prijs echt goed is of meestal lager ligt.",
                  "Als je wilt, mailen we je zodra de prijs daalt."],
        "affiliate": "Sommige links naar winkels zijn affiliatelinks: als je iets koopt, kan guitle een commissie krijgen, zonder extra kosten voor jou.",
        "legal": "Juridische informatie", "privacy": "Privacy", "cookies": "Cookies", "otherCountries": "guitle in andere landen:",
        "updated": "Gegevens bijgewerkt op {d}", "home": "Home",
        "kinds": {"electrica": ("Elektrische gitaren", "Elektrisch", "Zoek in elektrische gitaren: model, merk, kleur…"),
                  "acustica": ("Akoestische gitaren", "Akoestisch", "Zoek in akoestische gitaren: model, merk, hout…"),
                  "clasica": ("Klassieke gitaren", "Klassiek", "Zoek in klassieke gitaren: model, merk, flamenco…")},
        "anyPrice": "Elke prijs", "upTo": "Tot {v}", "over": "Meer dan {v}", "brandLabel": "Merk", "priceLabel": "Prijs",
        "showLabel": "Tonen", "showAll": "Alle", "showMulti": "In meerdere winkels", "showStock": "Op voorraad",
        "showLow": "Op de laagste prijs", "showLh": "Alleen linkshandig", "loading": "Catalogus laden…", "sortLabel": "Sorteren",
        "sorts": ["Meeste winkels", "Laagste prijs", "Hoogste prijs", "Grootste besparing tussen winkels", "Naam"],
        "moreBtn": "Meer tonen", "sections": "Secties", "searchAria": "Zoeken",
        "bestPrice": "beste prijs", "inStock": "op voorraad", "noStock": "niet op voorraad", "goLong": "Naar de winkel", "goShort": "Naar",
        "store": "winkel", "stores": "winkels", "lh": "linkshandig", "storesH3": "Winkels", "historyH3": "Prijsgeschiedenis",
        "amazon": "", "titleFrom": "{name}: prijs vanaf {price} {where}", "inN": "in {n} winkels", "inS": "bij {s}",
        "whereMany": "bij {s} · {n} winkels", "whereDiff": ", tot {d} verschil",
        "desc": "{name} vanaf {price} bij {s}. Vergelijk de prijs in {n} {stores} ({list}) en bekijk de prijsgeschiedenis om te zien "
                "of het een goed moment is om te kopen.",
        "alertTitle": "Prijsalert", "alertWait": "Een moment…", "alertSaving": "We slaan je antwoord op.",
        "alertGo": "Naar guitle", "alertBad": ["Ongeldige link", "Kopieer de volledige link uit de e-mail en probeer het opnieuw."],
        "alertDone": ["Prijsalert bevestigd!", "We mailen je zodra de prijs daalt. Elke e-mail bevat een afmeldlink."],
        "alertGone": ["Prijsalert verwijderd", "Je ontvangt geen e-mails meer voor deze alert. Je adres is van onze lijst verwijderd."],
        "alertMissing": ["Prijsalert niet gevonden", "Misschien was hij al bevestigd of verwijderd, of zijn er meer dan 7 dagen verstreken "
                                                     "zonder bevestiging. Hulp nodig? Mail ons op hola@guitle.com."],
        "js": {"loadErr": "De catalogus kon niet worden geladen.", "allBrands": "Alle merken", "all": "Alle", "low": "Laagste prijs",
               "save": "Bespaar {v}", "lh": "linkshandig", "store": "winkel", "stores": "winkels",
               "empty": "Geen {many} met deze filters.", "more": "Meer tonen (nog {n})",
               "meta": "{a} van {b} {many} · {m} vergelijkbaar in meerdere winkels · bijgewerkt op {d}", "best": "beste prijs",
               "inStock": "op voorraad", "noStock": "niet op voorraad", "goLong": "Naar de winkel", "goShort": "Naar", "close": "Sluiten",
               "inAt": "bij {s}", "saveMax": " · tot {v} goedkoper dan de duurste", "atLow": "Op de laagste prijs ooit",
               "lowTag": "Laagste prijs: {v}", "storesH": "Winkels", "evolH": "Prijsverloop",
               "histErr": "De prijsgeschiedenis kon niet worden geladen.", "histSoon": "De prijsgeschiedenis vult zich de komende dagen.",
               "many": "gitaren",
               "types": {"ST": "ST-modellen", "T": "T-modellen", "Semihueca": "Semi-akoestisch", "Moderna / Metal": "Modern / Metal",
                         "Otras": "Overige", "Auditorio / Concierto": "Auditorium / Concert", "12 cuerdas": "12-snarig",
                         "Tamaño reducido": "Klein formaat", "Clásica": "Klassiek", "Flamenca": "Flamenco",
                         "Electroclásica": "Elektrisch klassiek"},
               "wait": "We volgen dit model sinds {n} {days}", "day": "dag", "days": "dagen",
               "waitSub": "Het oordeel wordt betrouwbaarder na een paar weken prijsgeschiedenis.",
               "min": "Laagste prijs ooit", "minSub": "We hebben hem nog nooit goedkoper gezien.", "minBelow": " {p}% onder het 30-daags gemiddelde.",
               "good": "Goed moment: {p}% onder de gemiddelde prijs", "goodSub": "Gemiddelde van de afgelopen 30 dagen: {avg}.",
               "bad": "Nu {p}% duurder dan normaal",
               "badSub": "Geen haast? Wacht dan: het 30-daags gemiddelde is {avg} en de laagste prijs {min}.",
               "normal": "Normale prijs", "normalSub": "In lijn met het 30-daags gemiddelde ({avg}). Laagste prijs: {min}.",
               "today": "prijs vandaag", "lowest": "laagste prijs ({d})", "highest": "hoogste prijs", "avg": "gemiddelde {n} dagen",
               "since": "Gevolgd sinds {d}", "noHist": "Nog geen prijsgeschiedenis.", "pvp": "Adviesprijs", "bestLine": "Beste prijs",
               "alertOpen": "Laat me weten als de prijs daalt", "emailPh": "jij@voorbeeld.nl", "emailLabel": "Je e-mail",
               "targetPh": "Max. prijs (optioneel)", "targetLabel": "Doelprijs in euro", "alertBtn": "Waarschuw me",
               "alertLegal": "Gratis en zonder account. Door op „Waarschuw me” te klikken ga je akkoord met het "
                             "<a href=\"/nl/legal.html#privacy\">privacybeleid</a>: we gebruiken je e-mail alleen voor deze alert en je "
                             "meldt je met één klik af.",
               "alertOk": "<b>Klaar!</b> Over een paar minuten krijg je een e-mail op {email} om de alert te bevestigen (kijk ook in je spam).",
               "alertErr": "De alert kon niet worden opgeslagen. Controleer het e-mailadres en probeer het opnieuw."},
        "mail": {"tagline": "gitaren voor de beste prijs",
                 "footer": "guitle vergelijkt elke dag de prijzen van muziekwinkels. Je krijgt deze e-mail omdat je op guitle.com een "
                           "prijsalert hebt aangevraagd. Verantwoordelijke: Manuel Lorente Gálvez, hola@guitle.com.",
                 "privacy": "Privacy", "confirmSubject": "Bevestig je guitle-prijsalert",
                 "confirmTitle": "Bevestig je prijsalert", "asked": "Je wilt een bericht ontvangen als de prijs daalt{target}:",
                 "below": " onder <b>{v}</b>", "confirmAsk": "Bevestig dat je de alert op dit adres wilt ontvangen:",
                 "confirmBtn": "Alert bevestigen",
                 "notYou": "Was jij dit niet? Doe dan niets: onbevestigde alerts worden na 7 dagen automatisch verwijderd.",
                 "dropSubject": "Prijs gedaald: {name} nu {price}", "dropTitle": "De prijs is gedaald!", "nowAt": "bij {s} · eerst {v}",
                 "seeAll": "Bekijk de prijzen in alle winkels",
                 "check": "Prijzen veranderen dagelijks: controleer de prijs in de winkel voordat je koopt. Geen interesse meer?",
                 "stop": "Deze alert stopzetten"},
    },
}


def strings(code):
    """Textos de un país: los de su idioma con los cambios propios del país ("t_over"; p. ej. Irlanda usa el inglés
    del Reino Unido pero habla de Irlanda). Los enlaces a su aviso legal apuntan a su carpeta."""
    t = json.loads(json.dumps(T[SITES[code]["t"]]))
    for key, value in SITES[code].get("t_over", {}).items():
        if isinstance(value, dict):
            t[key].update(value)
        else:
            t[key] = value
    t["js"]["alertLegal"] = re.sub(r"/[a-z]{2}/legal\.html", f"/{code}/legal.html", t["js"]["alertLegal"])
    return t


# Lo que va en el pie de cada web: España y los demás países.
def _countries():
    return [(SPAIN["country"], "/")] + [(s["country"], f"/{code}/") for code, s in SITES.items()]


def money(v, site):
    """Precio con el formato del país: 1 299 € (francés, portugués), 1.299 € (alemán, italiano), € 1.299 (neerlandés),
    €1,299 (Irlanda), £1,299 (Reino Unido), R$ 1.299,00 (Brasil)."""
    whole, cents = int(round(v * 100)) // 100, int(round(v * 100)) % 100
    lang, dec = SITES[site]["lang"], f"{cents:02d}" if cents else ""
    if SITES[site]["cur"] == "GBP":
        return f"£{whole:,}" + (f".{dec}" if dec else "")
    if SITES[site]["cur"] == "BRL":
        return f"R$\u00a0{whole:,}".replace(",", ".") + f",{cents:02d}"
    if lang == "en-IE":
        return f"€{whole:,}" + (f".{dec}" if dec else "")
    if lang.startswith("nl"):
        return f"€\u00a0{whole:,}".replace(",", ".") + (f",{dec}" if dec else "")
    txt = f"{whole:,}".replace(",", "." if lang[:2] in ("de", "it", "es") else "\u202f")
    return f"{txt},{dec}\u00a0€" if dec else f"{txt}\u00a0€"


def _load(path):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _json_path(code, kind):
    """JSON del catálogo del país para una categoría (el nombre lo fija scraper.catalog, CATALOGS[...]["files"])."""
    from .catalog import CATALOGS
    # Las guitarras en el catálogo del país; el equipo, si lo hay, en otro ("brmas").
    for cat in [SITES[code]["catalog"]] + SITES[code].get("extra_catalogs", []):
        if kind in CATALOGS[cat]["files"]:
            return f"data/catalog/{cat}/{CATALOGS[cat]['files'][kind]}"
    raise KeyError(kind)


def _history_path(code, kind):
    """Histórico de precios del catálogo de la categoría (el equipo, "brmas", "demas"…, tiene el suyo)."""
    return _json_path(code, kind).rsplit("/", 1)[0] + "/history.json"


def catalogs(code):
    """Categoría → JSON del catálogo del país (solo las que ya tienen guitarras)."""
    out = {}
    for kind in SITES[code]["kinds"]:
        data = _load(_json_path(code, kind))
        if data and data.get("products"):
            out[kind] = data
    return out


def _alternates():
    """EAN → {país: URL de su página}, para enlazar la misma guitarra entre países (hreflang)."""
    out = {}
    for kind, k in pages.KINDS.items():
        for p in (_load(k["src"]) or {}).get("products", []):
            if p.get("ean") and p.get("slug"):
                out.setdefault(p["ean"], {})["es"] = f"{SITE}/g/{p['slug']}.html"
    for code in SITES:
        for kind in SITES[code]["kinds"]:
            for p in (_load(_json_path(code, kind)) or {}).get("products", []):
                if p.get("ean") and p.get("slug"):
                    out.setdefault(p["ean"], {})[code] = f"{SITE}/{code}/g/{p['slug']}.html"
    return out


def _hreflang(links):
    langs = {"es": SPAIN["lang"]} | {c: s["lang"] for c, s in SITES.items()}
    tags = [f'<link rel="alternate" hreflang="{langs[c]}" href="{u}">' for c, u in sorted(links.items())]
    if "es" in links:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{links["es"]}">')
    return "\n".join(tags) if len(links) > 1 else ""


esc = lambda v: html.escape(str(v or ""), quote=True)


def _logo(code, t):
    return (f'<h1 style="flex:1;margin:0"><a class="logo" href="/{code}/" aria-label="{esc(t["homeLabel"])}"><img src="/icons/icon.svg" '
            f'alt=""><span class="stack"><span class="word">gu<span class="i">ı</span>tle</span><span class="tag">{esc(t["tagline"])}'
            f'</span></span></a></h1>')


def _foot(code, t):
    here = SITES[code]["country"]
    others = " · ".join(f'<a href="{u}">{esc(n)}</a>' for n, u in _countries() if n != here)
    return (f'<footer class="site-foot">\n    <span>{esc(t["affiliate"])}</span>\n'
            f'    <span><a href="/{code}/legal.html#aviso">{esc(t["legal"])}</a> · <a href="/{code}/legal.html#{_anchor(code)}">'
            f'{esc(t["privacy"])}</a> · <a href="/{code}/legal.html#cookies">{esc(t["cookies"])}</a></span>\n'
            f'    <span>{esc(t["otherCountries"])} {others}</span>\n  </footer>')


def _anchor(code):
    return {"pt": "privacidade", "fr": "confidentialite", "it": "privacy", "en": "privacy", "de": "datenschutz", "br": "privacidade", "nl": "privacy"}.get(SITES[code]["t"], "privacidad")


def _head(code, title, desc, canonical, extra=""):
    s = SITES[code]
    return f"""<!doctype html>
<html lang="{s['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2a78d6">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(desc)}">' if desc else ''}
<link rel="canonical" href="{SITE}{canonical}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/icons/icon.svg">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="stylesheet" href="/fonts/inter.css">
{extra}"""


def _gt(t, kind=None):
    js = t["js"] | ({"many": t["nouns"][kind]} if kind in t.get("nouns", {}) else {})  # qué se cuenta en la lista
    return f'<script>window.GUITLE_T = {json.dumps(js, ensure_ascii=False)};</script>'


# --- Página de cada guitarra ---------------------------------------------------------------------------------

def _rows(product, names, colors, code, t):
    best = product["items"][0]["p"]
    out = []
    for n, i in enumerate(product["items"]):
        store = esc(names.get(i["s"], i["s"]))
        go = f'href="{esc(i["u"])}" target="_blank" rel="sponsored noopener"' if i.get("u") else ""
        name = f'<a class="store-link" {go}>{store}</a>' if go else store
        stock = (f'<span class="tag">{esc(t["inStock"])}</span>' if i.get("st") is True
                 else f'<span class="tag warn">{esc(t["noStock"])}</span>' if i.get("st") is False else "")
        diff = esc(t["bestPrice"]) if n == 0 else "+" + money(round(i["p"] - best, 2), code)
        button = (f'<a class="go" {go}><span class="go-long">{esc(t["goLong"])}</span><span class="go-short">{esc(t["goShort"])}</span></a>'
                  if go else "")
        out.append(f'<tr class="{"best-row" if n == 0 else ""}"><td><span class="swatch" style="background:var({colors.get(i["s"], "--reference")})"></span>{name}</td>'
                   f'<td class="num"><strong>{money(i["p"], code)}</strong></td><td class="num muted col-diff">{diff}</td><td>{stock}</td>'
                   f'<td class="num">{button}</td></tr>')
    return "\n".join(out)


def _product(code, kind, product, names, alternates):
    s, t = SITES[code], strings(code)
    label, _, _ = t["kinds"][kind]
    name, brand, slug = product["name"], product.get("brand") or "", product["slug"]
    colors = {st: pages.PALETTE[n % len(pages.PALETTE)] for n, st in enumerate(sorted({i["s"] for i in product["items"]}))}
    stores = sorted({names.get(i["s"], i["s"]) for i in product["items"]})
    n = len(stores)
    prices = [i["p"] for i in product["items"]]
    best = product["items"][0]
    best_store = names.get(best["s"], best["s"])
    where = (t["whereMany"].format(s=best_store, n=n) + (t["whereDiff"].format(d=money(round(max(prices) - min(prices)), code))
                                                         if max(prices) - min(prices) >= 1 else "")
             if n > 1 else t["inS"].format(s=best_store))
    title = t["titleFrom"].format(name=name, price=money(best["p"], code),
                                  where=t["inN"].format(n=n) if n > 1 else t["inS"].format(s=best_store))
    desc = t["desc"].format(name=name, price=money(best["p"], code), s=best_store, n=n,
                            stores=t["store"] if n == 1 else t["stores"], list=", ".join(stores[:4]) + ("…" if n > 4 else ""))
    url = f"/{code}/g/{slug}.html"
    img = f"/img/p/{product['th']}" if product.get("th") else None
    ld = {"@context": "https://schema.org", "@type": "Product", "name": name,
          "brand": {"@type": "Brand", "name": brand} if brand else None, "category": label,
          "image": SITE + img if img else None, "gtin13": product.get("ean"), "url": SITE + url,
          "offers": {"@type": "AggregateOffer", "priceCurrency": s["cur"], "lowPrice": min(prices), "highPrice": max(prices),
                     "offerCount": len(product["items"])}}
    ld = {key: v for key, v in ld.items() if v}
    history = "/" + _history_path(code, kind)
    typ = product.get("type")
    typ = t["js"]["types"].get(typ, typ) if typ and typ != "Otras" else ""
    amazon = (f'\n    <p class="muted small amazon">{t["amazon"].format(u=esc(s["amazon"].format(q=quote_plus(name))))}</p>'
              if s.get("amazon") and t.get("amazon") else "")
    alt = _hreflang(alternates.get(product.get("ean"), {})) if product.get("ean") else ""
    head = _head(code, f"{title} · guitle", desc, url, f"""{alt + chr(10) if alt else ''}<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
{f'<meta property="og:image" content="{SITE}{img}">' if img else ''}
<link rel="stylesheet" href="/catalogo.css">
<link rel="stylesheet" href="/producto.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script src="/vendor/chart.umd.min.js"></script>
{_gt(t)}
</head>""")
    data = {"names": {i["s"]: names.get(i["s"], i["s"]) for i in product["items"]}, "colors": colors} | (
        {"hk": product["hk"]} if product.get("hk") else {})
    page = s["kinds"][kind]
    return f"""{head}
<body data-ean="{esc(product.get('ean') or '')}" data-best="{best['p']}" data-history="{history}" data-site="{code}" data-cur="{s['cur']}">
<script type="application/json" id="stores-data">{json.dumps(data, ensure_ascii=False)}</script>
<main>
  <div class="topbar">
    <div class="row">
      {_logo(code, t)}
      <a class="navlink" href="/{code}/{page}.html">{esc(label)}</a>
    </div>
  </div>
  <nav class="crumbs"><a href="/{code}/">{esc(t['home'])}</a> › <a href="/{code}/{page}.html">{esc(label)}</a></nav>
  <article class="product">
    {f'<div class="pimg"><img src="{img}" alt="{esc(name)}"></div>' if img else ''}
    <div class="pinfo">
      <div class="muted">{esc(brand)}{' · ' + esc(typ) if typ else ''}{' · ' + esc(t['lh']) if product.get('lh') else ''}</div>
      <h2 class="pname">{esc(name)}</h2>
      <div id="price" class="big">{money(best['p'], code)}</div>
      <div id="where" class="muted">{esc(where)}</div>
      <div id="verdict" class="verdict hidden"></div>
      {f'<div class="muted small">EAN {esc(product["ean"])}</div>' if product.get('ean') else ''}
    </div>
  </article>
  <section><h3>{esc(t['storesH3'])}</h3><div class="table-wrap"><table id="stores">{_rows(product, names, colors, code, t)}</table></div>{amazon}</section>
  <section><h3>{esc(t['historyH3'])}</h3>
    <div class="stats" id="stats"></div>
    <div class="chart-box"><canvas id="chart"></canvas></div>
    <p class="muted small" id="chart-note"></p>
  </section>
  {_foot(code, t)}
</main>
<script src="/producto.js"></script>
<script src="/c.js" defer></script>
</body>
</html>
"""


# --- Páginas del catálogo -------------------------------------------------------------------------------------

def _list(code, kind, kinds):
    s, t = SITES[code], strings(code)
    label, short, ph = t["kinds"][kind]
    page = s["kinds"][kind]
    nav = "".join(f'<a href="/{code}/{s["kinds"][k]}.html"{" class=\"on\"" if k == kind else ""}>{esc(t["kinds"][k][1])}</a>'
                  for k in s["kinds"] if k in kinds)
    m = lambda v: money(v, code)
    ranges = [("0-300", t["upTo"].format(v=m(300))), ("300-600", f"{m(300)} – {m(600)}"), ("600-1000", f"{m(600)} – {m(1000)}"),
              ("1000-2000", f"{m(1000)} – {m(2000)}"), ("2000-", t["over"].format(v=m(2000)))]
    sorts = zip(("stores", "price", "price-desc", "save", "name"), t["sorts"])
    head = _head(code, f"{label} · guitle", None, f"/{code}/{page}.html",
                 f'<script src="/vendor/chart.umd.min.js"></script>\n<link rel="stylesheet" href="/catalogo.css">\n{_gt(t, kind)}\n</head>')
    return f"""{head}
<body data-src="/{_json_path(code, kind)}" data-history="/{_history_path(code, kind)}" data-kind="{kind}" data-img="/img/p/" data-cur="{s['cur']}">
<main>
  <div class="topbar">
    <div class="row">
      {_logo(code, t)}
    </div>
    <nav class="sections" aria-label="{esc(t['sections'])}">{nav}</nav>
    <input class="search" id="q" type="search" placeholder="{esc(ph)}" autocomplete="off" aria-label="{esc(t['searchAria'])}">
    <div class="chips" id="types"></div>
    <div class="filters">
      <select id="brand" aria-label="{esc(t['brandLabel'])}"></select>
      <select id="range" aria-label="{esc(t['priceLabel'])}">
        <option value="">{esc(t['anyPrice'])}</option>{''.join(f'<option value="{v}">{esc(l)}</option>' for v, l in ranges)}
      </select>
      <select id="show" aria-label="{esc(t['showLabel'])}">
        <option value="">{esc(t['showAll'])}</option><option value="multi">{esc(t['showMulti'])}</option><option value="stock">{esc(t['showStock'])}</option><option value="low">{esc(t['showLow'])}</option><option value="lh">{esc(t['showLh'])}</option>
      </select>
    </div>
  </div>
  <div class="meta"><span id="meta">{esc(t['loading'])}</span>
    <label>{esc(t['sortLabel'])} <select id="sort">{''.join(f'<option value="{v}">{esc(l)}</option>' for v, l in sorts)}</select></label>
  </div>
  <div id="grid" class="grid"></div>
  <button class="more hidden" id="more">{esc(t['moreBtn'])}</button>
  {_foot(code, t)}
</main>
<div class="sheet-bg" id="bg"></div>
<div class="sheet" id="sheet" role="dialog" aria-modal="true"></div>
<script src="/catalogo.js"></script>
<script src="/c.js" defer></script>
</body>
</html>
"""


# --- Portada ----------------------------------------------------------------------------------------------------

def _index_css():
    """Los estilos de la portada española (index.html), para que todas las portadas se vean igual."""
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    return re.search(r"<style>.*?</style>", text, re.S).group(0)


def _card(code, p, names, t):
    best = p["items"][0]
    top = max(i["p"] for i in p["items"])
    pct = round((top - best["p"]) / top * 100)
    n = len({i["s"] for i in p["items"]})
    return (f'<a class="card" href="/{code}/g/{esc(p["slug"])}.html"><span class="badge">{esc(t["dealsBadge"].format(p=pct))}</span>'
            f'<div class="img">{f"<img src=\"/img/p/{esc(p["th"])}\" alt=\"\" loading=\"lazy\">" if p.get("th") else ""}</div>'
            f'<div class="body"><span class="name">{esc(p["name"])}</span><span class="price"><strong>{money(best["p"], code)}</strong></span>'
            f'<span class="where">{esc(t["whereMany"].format(s=names.get(best["s"], best["s"]), n=n))}</span></div></a>')


ICON_KIND = {"electrica": "guitarra", "acustica": "acustica", "clasica": "clasica", "portuguesa": "acustica", "bajo": "bajo",
             "ampli": "ampli", "pedal": "pedal", "teclado": "teclado", "micro": "micro", "estuche": "estuche", "varios": "varios"}


def _index(code, cats):
    s, t = SITES[code], strings(code)
    names = {k: v for d in cats.values() for k, v in d["stores"].items()}
    allp = [p for d in cats.values() for p in d["products"] if p.get("slug")]
    # Mayores diferencias entre tiendas: guitarras con foto en dos o más tiendas; más del 40 % suele ser un mal emparejado.
    def gap(p):
        top = max(i["p"] for i in p["items"])
        return (top - p["items"][0]["p"]) / top
    deals = sorted((p for p in allp if p.get("th") and len({i["s"] for i in p["items"]}) >= 2 and 0.03 <= gap(p) <= 0.4),
                   key=gap, reverse=True)[:4]
    # Iconos de las categorías: los mismos de la portada española.
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    icons = dict(re.findall(r"^\s{4}(\w+): '(.*?)',$", text, re.M))
    tiles = "".join(f'<a class="catcard" href="/{code}/{s["kinds"][k]}.html"><b><svg class="fill" viewBox="0 0 24 24" aria-hidden="true">'
                    f'{icons.get(ICON_KIND[k], "")}</svg></b><span>{esc(t["kinds"][k][1])}</span>'
                    f'<small>{len(cats[k]["products"]):,} {esc(t.get("nouns", {}).get(k, t["guitars"]))}</small></a>'.replace(",", " ")
                    for k in s["kinds"] if k in cats)
    first = s["kinds"][next(iter(cats))] if cats else next(iter(s["kinds"].values()))
    updated = max((d["updated"] for d in cats.values()), default="")
    langs = {"es": "/"} | {c: f"/{c}/" for c in SITES}
    alt = _hreflang({c: SITE + u for c, u in langs.items()})
    head = _head(code, t["homeTitle"], t["homeDesc"], f"/{code}/", f"""{alt}
<meta property="og:site_name" content="guitle">
<meta property="og:title" content="{esc(t['homeTitle'])}">
<meta property="og:url" content="{SITE}/{code}/">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "guitle", "url": f"{SITE}/{code}/", "inLanguage": s["lang"]})}</script>
{_index_css()}
</head>""")
    n_stores = len({i["s"] for p in allp for i in p["items"]})
    word = t["guitars"] if set(cats) <= set(GUITAR_KINDS) else t.get("allWord", t["guitars"])
    return f"""{head}
<body>
<main>
  <header class="top">
    <div class="stats"><span><strong>{len([p for p in allp if True]):,}</strong>{esc(word)}</span><span><strong>{n_stores}</strong>{esc(t['storesWord'])}</span></div>
    <nav><a href="/{code}/{first}.html">{esc(t['catalog'])}</a></nav>
  </header>

  <div class="hero">
    <a class="logo mark" href="/{code}/" aria-label="{esc(t['homeLabel'])}"><img src="/icons/icon.svg" alt=""><span class="word">gu<span class="i">ı</span>tle</span></a>
    <h1>{t['h1']}</h1>
    <form class="search" action="/{code}/{first}.html" method="get" role="search">
      <input name="q" type="search" placeholder="{esc(t['searchPh'])}" aria-label="{esc(t['searchLabel'])}" autocomplete="off">
      <button type="submit">{esc(t['searchBtn'])}</button>
    </form>
  </div>
{f'''
  <section>
    <div class="sec-head"><h2>{esc(t['dealsH'])}</h2></div>
    <div class="row">{''.join(_card(code, p, names, t) for p in deals)}</div>
  </section>
''' if deals else ''}
  <section>
    <div class="sec-head"><h2>{esc(t['catsH'])}</h2></div>
    <div class="cats">{tiles}</div>
  </section>

  <section class="split">
    <div class="panel">
      <h3>{esc(t['storesH'])}</h3>
      <div class="stores">{''.join(f'<span>{esc(n)}</span>' for n in sorted(set(names.values())))}</div>
    </div>
    <div class="panel">
      <h3>{esc(t['howH'])}</h3>
      {''.join(f'<p class="muted" style="margin:6px 0"><b>{i}.</b> {esc(step)}</p>' for i, step in enumerate(t['steps'], 1))}
    </div>
  </section>

  <footer><span>{esc(t['updated'].format(d=f'{updated[8:10]}/{updated[5:7]}/{updated[:4]}'))}</span><span><a href="/{code}/legal.html#aviso">{esc(t['legal'])}</a> · <a href="/{code}/legal.html#{_anchor(code)}">{esc(t['privacy'])}</a> · <a href="/{code}/legal.html#cookies">{esc(t['cookies'])}</a></span>
    <span style="flex-basis:100%">{esc(t['affiliate'])}</span>
    <span style="flex-basis:100%">{esc(t['otherCountries'])} {' · '.join(f'<a href="{u}">{esc(n)}</a>' for n, u in _countries() if n != s['country'])}</span></footer>
</main>
<script src="/c.js" defer></script>
</body>
</html>
""".replace(f"<strong>{len(allp):,}</strong>", f"<strong>{len(allp):,}</strong>".replace(",", " "))


# --- Avisos de precio (confirmar / darse de baja) ----------------------------------------------------------------

def _alerta(code):
    t = strings(code)
    msgs = {k: t[k] for k in ("alertBad", "alertDone", "alertGone", "alertMissing")}
    head = _head(code, f"{t['alertTitle']} · guitle", None, f"/{code}/alerta.html",
                 '<meta name="robots" content="noindex">\n<link rel="stylesheet" href="/catalogo.css">\n'
                 '<style>.card { background: var(--surface-1); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; '
                 'margin-top: 24px; } .btn { display: inline-block; margin-top: 8px; background: var(--accent); color: #fff; '
                 'text-decoration: none; padding: 9px 16px; border-radius: 999px; font-weight: 600; }</style>\n</head>')
    return f"""{head}
<body>
<main>
  <div class="topbar"><div class="row">{_logo(code, t)}</div></div>
  <div class="card" id="card"><h2>{esc(t['alertWait'])}</h2><p>{esc(t['alertSaving'])}</p></div>
  {_foot(code, t)}
</main>
<script>
// Confirmar (?c=código) o dar de baja (?baja=código) un aviso de precio (igual que /alerta.html).
(async () => {{
  const M = {json.dumps(msgs, ensure_ascii=False)};
  const ALERTS = "https://firestore.googleapis.com/v1/projects/guitle-d48d8/databases/(default)/documents/alertas/";
  const q = new URLSearchParams(location.search);
  const card = document.getElementById("card");
  const show = ([title, text]) => {{ card.innerHTML = `<h2>${{title}}</h2><p>${{text}}</p><a class="btn" href="/{code}/">{esc(t['alertGo'])}</a>`; }};
  const id = (q.get("c") || q.get("baja") || "").replace(/[^A-Za-z0-9_-]/g, "");
  if (id.length < 20) return show(M.alertBad);
  try {{
    if (q.has("c")) {{
      const r = await fetch(`${{ALERTS}}${{id}}?updateMask.fieldPaths=ok&currentDocument.exists=true`, {{
        method: "PATCH", headers: {{ "Content-Type": "application/json" }}, body: JSON.stringify({{ fields: {{ ok: {{ booleanValue: true }} }} }}) }});
      if (!r.ok) throw new Error(r.status);
      show(M.alertDone);
    }} else {{
      const r = await fetch(ALERTS + id, {{ method: "DELETE" }});
      if (!r.ok) throw new Error(r.status);
      show(M.alertGone);
    }}
  }} catch (e) {{
    show(M.alertMissing);
  }}
}})();
</script>
</body>
</html>
"""


# --- Sitemap del país ------------------------------------------------------------------------------------------------

def _sitemap(code, urls):
    body = "\n".join(f"  <url><loc>{SITE}{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def write_site(code):
    """Genera (o deja como están) todas las páginas de un país. Solo se escribe un fichero si cambia."""
    s = SITES[code]
    out = ROOT / code
    cats = catalogs(code)
    if not cats:  # sin guitarras todavía (o una noche mala): no se publica una web vacía
        print(f"web {code}: sin guitarras en el catálogo, no se genera", flush=True)
        write_world()
        return
    alternates = _alternates()
    written, urls, keep = 0, [f"/{code}/"], set()
    for kind, data in cats.items():
        names = data["stores"]
        page = f"{s['kinds'][kind]}.html"
        written += pages._write(out / page, _list(code, kind, cats))
        urls.append(f"/{code}/{page}")
        keep.add(out / page)
        for p in data["products"]:
            if not p.get("slug") or not p.get("items"):
                continue
            path = out / "g" / f"{p['slug']}.html"
            written += pages._write(path, _product(code, kind, p, names, alternates))
            urls.append(f"/{code}/g/{p['slug']}.html")
            keep.add(path)
    for name, text in (("index.html", _index(code, cats)), ("alerta.html", _alerta(code)), ("legal.html", legal(code))):
        written += pages._write(out / name, text)
        keep.add(out / name)
    urls.append(f"/{code}/legal.html")
    # Guitarras que ya no están en el catálogo: su página se borra.
    for f in list(out.glob("g/*.html")):
        if f not in keep:
            f.unlink()
    written += pages._write(ROOT / f"sitemap-{code}.xml", _sitemap(code, urls))
    print(f"web {code}: {len(urls)} páginas ({written} nuevas o cambiadas)", flush=True)
    write_world()


def write_world():
    """data/catalog/paises.json: los países con web y sus cifras (guitarras y tiendas), para la etiqueta de países de la
    portada y el mapa de paises.html. España cuenta con sus catálogos de guitarras."""
    out = {}
    spain = [_load(k["src"]) for kind, k in pages.KINDS.items() if kind in GUITAR_KINDS]
    spain = [d for d in spain if d]
    out["es"] = {"country": SPAIN["country"], "path": "/", "guitars": sum(len(d["products"]) for d in spain),
                 "stores": len({st for d in spain for st in d["stores"]})}
    for code, s in SITES.items():
        cats = catalogs(code)
        guitars = sum(len(d["products"]) for d in cats.values())
        if guitars:
            out[code] = {"country": s["country"], "path": f"/{code}/", "guitars": guitars,
                         "stores": len({st for d in cats.values() for st in d["stores"]})}
    path = ROOT / "data" / "catalog" / "paises.json"
    text = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def legal(code):
    from .intl_legal import LEGAL
    t = strings(code)
    title, body = LEGAL[SITES[code]["t"]]
    for old, new in SITES[code].get("legal_replace", ()):
        body = body.replace(old, new)
    head = _head(code, f"{title} · guitle", None, f"/{code}/legal.html",
                 '<link rel="stylesheet" href="/catalogo.css">\n<style>.legal { max-width: 760px; } .legal h2 { margin-top: 34px; '
                 'scroll-margin-top: 16px; } .legal p, .legal li { color: var(--text-secondary); line-height: 1.6; }</style>\n</head>')
    return f"""{head}
<body>
<main>
  <div class="topbar"><div class="row">{_logo(code, t)}</div></div>
  <div class="legal">
{body}
  </div>
  {_foot(code, t)}
</main>
<script src="/c.js" defer></script>
</body>
</html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", choices=sorted(SITES), help="solo este país (por defecto, todos)")
    args = parser.parse_args(argv)
    for code in ([args.site] if args.site else SITES):
        write_site(code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
