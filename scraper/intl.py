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
}

# Lo que va en el pie de cada web: España y los demás países.
def _countries():
    return [(SPAIN["country"], "/")] + [(s["country"], f"/{code}/") for code, s in SITES.items()]


def money(v, site):
    """Precio con el formato del país: 1 299 € / 721,41 € (portugués y francés)."""
    whole, cents = int(round(v * 100)) // 100, int(round(v * 100)) % 100
    txt = f"{whole:,}".replace(",", " ")
    return f"{txt},{cents:02d} €" if cents else f"{txt} €"


def _load(path):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _json_path(code, kind):
    return f"data/catalog/{SITES[code]['catalog']}/{SITES[code]['kinds'][kind]}.json"


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
    return {"pt": "privacidade", "fr": "confidentialite", "it": "privacy"}.get(SITES[code]["t"], "privacidad")


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


def _gt(t):
    return f'<script>window.GUITLE_T = {json.dumps(t["js"], ensure_ascii=False)};</script>'


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
    s, t = SITES[code], T[SITES[code]["t"]]
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
    history = f"/data/catalog/{s['catalog']}/history.json"
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
    s, t = SITES[code], T[SITES[code]["t"]]
    label, short, ph = t["kinds"][kind]
    page = s["kinds"][kind]
    nav = "".join(f'<a href="/{code}/{s["kinds"][k]}.html"{" class=\"on\"" if k == kind else ""}>{esc(t["kinds"][k][1])}</a>'
                  for k in s["kinds"] if k in kinds)
    m = lambda v: money(v, code)
    ranges = [("0-300", t["upTo"].format(v=m(300))), ("300-600", f"300 – {m(600)}"), ("600-1000", f"600 – {m(1000)}"),
              ("1000-2000", f"{m(1000)} – {m(2000)}"), ("2000-", t["over"].format(v=m(2000)))]
    sorts = zip(("stores", "price", "price-desc", "save", "name"), t["sorts"])
    head = _head(code, f"{label} · guitle", None, f"/{code}/{page}.html",
                 f'<script src="/vendor/chart.umd.min.js"></script>\n<link rel="stylesheet" href="/catalogo.css">\n{_gt(t)}\n</head>')
    return f"""{head}
<body data-src="/{_json_path(code, kind)}" data-history="/data/catalog/{s['catalog']}/history.json" data-kind="{kind}" data-img="/img/p/" data-cur="{s['cur']}">
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


ICON_KIND = {"electrica": "guitarra", "acustica": "acustica", "clasica": "clasica", "portuguesa": "acustica"}


def _index(code, cats):
    s, t = SITES[code], T[SITES[code]["t"]]
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
                    f'<small>{len(cats[k]["products"]):,} {esc(t["guitars"])}</small></a>'.replace(",", " ")
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
    return f"""{head}
<body>
<main>
  <header class="top">
    <div class="stats"><span><strong>{len([p for p in allp if True]):,}</strong>{esc(t['guitars'])}</span><span><strong>{n_stores}</strong>{esc(t['storesWord'])}</span></div>
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
    t = T[SITES[code]["t"]]
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


def legal(code):
    from .intl_legal import LEGAL
    t = T[SITES[code]["t"]]
    title, body = LEGAL[SITES[code]["t"]]
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
