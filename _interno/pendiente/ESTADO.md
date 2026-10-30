# Dónde nos quedamos (30-10-2026, 8:05 hora de España)

## Publicado (en la rama claude/friendly-fermat-yycain)
- Tiendas nuevas de los directorios de marcas: Francia (31 fuentes), Portugal (9), Italia (27), Alemania (25),
  Austria (8), Países Bajos (13), Reino Unido (36), Irlanda (13), España (Alteisa + arreglos de Microfusa, Fusté,
  Zingla, Abrines, Neomúsica, Partitura, Trino).
- Equipo por país (mecanismo genérico `EQUIPO_COUNTRIES` en scraper/catalog.py): Alemania (demas) y Francia (frmas).
- Portada en móvil: cifras en una fila y menú debajo (como mootle).

## Hecho pero SIN publicar: equipo de Italia, Portugal, Reino Unido/Irlanda y Países Bajos/Austria
Cada país está terminado y probado, pero choca con el de Francia al unirlo (mismas reglas en catalog.py y en el
workflow). Copia de cada commit en esta carpeta, por si se pierde el contenedor:
- equipo-italia.patch (itmas), equipo-portugal.patch (ptmas), equipo-uk-irlanda.patch (ukmas, iemas),
  equipo-paises-bajos-austria.patch (nlmas, atmas).
Todos parten del piloto de Alemania (6f1f30331), no de Francia.

Para seguir: unir cada uno sobre la rama actual (`git am -3` o merge de su rama de agente), juntando las dos versiones
en los conflictos (regex de `_TO_ES_EQUIPO`, `_EQ_DROP`, `_EQ_DROP_CAT`, opciones de tienda "cat" de Francia y
"cat_path"/"path_crumbs" de Italia, y todos los `<país>mas` en la matriz y en "solo" de catalog.yml). Después,
comprobar que España, Brasil, Alemania y Francia clasifican igual y publicar país a país.

## Pendiente después
- Probar desde GitHub las tiendas que bloquean (Bettin, Music Centre, B Sharp, Gear4music.de, Guitarpoint, Musikhammer,
  Schreeven…) antes de descartarlas.
- Directorios de ESP, Cort y Martin (se leen desde GitHub).
- Siguiente tanda de países con 10 agentes; luego Latinoamérica (cada país con su web y su moneda).
- Panel "Crecimiento de guitle": regenerarlo tras cada fase.
- El usuario lanza el catálogo con "todos" a mano para que entren las tiendas nuevas (yo no puedo lanzarlo: 403).
