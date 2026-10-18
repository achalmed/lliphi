---
tipo: doc
estado: activo
titulo: 'Nombre de la marca: candidatos, búsqueda de colisiones y recomendación (fase 3)'
---
# Nombre de la marca

Fase 3 del encargo, 2026-10-18. La elección es del autor. Cada candidato se buscó en KDE Store (API OCS, sin filtro
de categoría), GitHub (`gh api search/repositories`, por nombre), PyPI, npm, el subdominio `<nombre>.netlify.app`
y una búsqueda web general. Criterios: original, pronunciable en español y en inglés, sin marca ni tema previo, con
sentido para una estética serena y mínima, y en sintonía con el ecosistema del autor (los tokens de
`identidad-visual` ya usan quechua: `puka`, `qillu`).

## Candidatos

| nombre | lengua y sentido | KDE Store | GitHub (repos con el nombre) | PyPI | npm | `.netlify.app` | web | veredicto |
|---|---|---|---|---|---|---|---|---|
| **Lliphi** | quechua: suave, liso, apacible | 0 | 3, sin relación (un apellido) | libre | libre | libre | nada | **recomendado**: libre en todo y describe la estética |
| **Sosiego** | español: calma, serenidad | 0 | 11, triviales (0 estrellas) | libre | libre | **ocupado** | nada | buena segunda opción; el sitio iría como sección del hub o `sosiego-tema` |
| Yuraq | quechua: blanco | 0 | 16, triviales | libre | libre | libre | solo montañas | libre, pero «blanco» describe mal la variante oscura |
| Qasi | quechua: calmo, tranquilo | 0 | 2 487 (ruido: Qasim, qasino…) | **ocupado** | libre | libre | nada | ruido de búsqueda alto |
| Sumaq | quechua: bello | 0 | 227 (hoteles, marcas peruanas) | libre | libre | — | genérico en Perú | demasiado usado |
| Sereno | español | **4 en la tienda** | 653 | libre | ocupado | — | — | descartado |
| Tenue | español: sutil | 1 | `Kometia-Themes/Tenue` es un tema | libre | libre | — | — | descartado: tema homónimo |
| Illa | quechua: luz, amuleto | 2 (fondos) | 1 632; ILLA Cloud es un producto conocido | libre | ocupado | — | — | descartado: marca conocida |
| Wayra | quechua: viento | 0 | 227 | libre | libre | — | aceleradora Wayra (Telefónica) | descartado: marca conocida |
| Umbral | español | 0 | 775; `umbral-night-theme` existe | ocupado | ocupado | — | — | descartado |

## Decisión

**El autor eligió «Lliphi» el 2026-10-18** («relámpago» en quechua; Laime Ajacopa, *Diccionario bilingüe
quechua–castellano*, 2007: «lliphi, illapa, chuqi illa. s. Relámpago»; «lliphipiy. s. Resplandor, fulgor»). Había
elegido primero «Llampu» y pidió el mismo día un nombre que dijera «rayo» o «destello». Segunda búsqueda de
colisiones (misma batería): **Lliphi** libre en KDE Store, GitHub (0 repos), PyPI, npm y `lliphi.netlify.app`;
**Illapa** («rayo», el apu) descartado porque `illapa.netlify.app` es una empresa peruana de soluciones eléctricas y
npm lo ocupa una utilidad SQL; **Illariy** («fulgurar, alborear») e **Lliphipiy** («resplandor») libres pero menos
precisos o más largos; **K'achachacha** («destello») demasiado largo. Grafía: la del quechua sureño (ph aspirada);
en quechua chanka se escribiría sin aspiración, lo que se anota en el sitio.

## Recomendación (previa a la decisión)

**Lliphi**, con las variantes **Lliphi Claro** y **Lliphi Oscuro** (en la tienda, «Lliphi Light» y «Lliphi Dark»
como alias en inglés). Identificadores: carpeta y repositorio `lliphi`, paquetes `org.lliphi.<componente>` o
`lliphi-<componente>`, sitio `lliphi.netlify.app` o `achalmaedison.netlify.app/lliphi`. Lo que no se ha podido
comprobar: registros de marca (INDECOPI, EUIPO, USPTO); una búsqueda web general no muestra ningún producto con ese
nombre.
