---
tipo: doc
estado: activo
titulo: 'Autocrítica (2026-10-18): por qué 0.1.0 parece Breeze recoloreado, qué hay y qué falta de Nothing y WhiteSur, y el cambio de enfoque'
---
# Autocrítica

El autor, al ver 0.1.0 en su escritorio: «esto parece Breeze con algunos detalles en rojo». Tiene razón. Esta página
dice por qué, pieza por pieza, y qué cambia a partir de ahora.

## 1. Qué hay realmente de cada referencia en 0.1.0

| rasgo | Nothing | WhiteSur | en 0.1.0 | veredicto |
|---|---|---|---|---|
| superficies casi negras de tono único | `#1b1b1d` | — | `#1b1c1e` en esquema y estilo | **presente** |
| acento rojo | `#eb3131` fijo en 258 SVG | — | `#c93436` como token, sigue al sistema | presente, mejor resuelto |
| barra superior fina + dock flotante que se oculta | sí | panel + dock 64 px | sí (36 px + dock 56 px) | presente |
| **translucidez y desenfoque** (vidrio) | Konsole 0.8 con blur; paneles opacos | panel 0.45, diálogo 0.65, blur | **ninguna**: todo opaco (decisión 2.5) | **falta**: es lo que más define a WhiteSur |
| **decoración de ventanas propia** | Aurorae: botones circulares con glifo al pasar | Aurorae: radio 12, borde 1 px, sombra grande | **Breeze** coloreada (decisión 3.1) | **falta**: es lo primero que se ve de un tema |
| **estilo de Plasma con SVG propios** | 51 SVG modificados (color), 60 de Breeze | 34 widgets reescritos: tareas con 6 estados, botones, fondos translúcidos | solo 5 fondos (panel, diálogo, tooltip, widget, translúcido); tareas, botones, campos, pestañas, listas, barras: **Breeze** | **falta**: el escritorio se dibuja con lo de Breeze |
| **iconos propios** | breeze-dark | WhiteSur (62 MB, carpetas azules) | carpetas rojas sobre Breeze (lote 2); todo lo demás Breeze | parcial |
| **estilo de widgets Qt** | Breeze | Kvantum translúcido | Breeze sin ajustes (menús opacos) | igual que Nothing; **sin el vidrio** de WhiteSur |
| fondo de pantalla | tres fotos propias | Big Sur | degradado con dos franjas tenues | presente pero anodino |
| splash, bloqueo, cierre de sesión | ninguno | copia de Breeze | heredado de Breeze | igual que las referencias, pero sin identidad |
| Konsole | opacidad 0.8 + blur | — | opaco | **falta** |
| estética «hacker»/tecnológica (puntos, retícula, mono) | implícita en su sobriedad | — | nada | **falta** |

Conclusión: de las dos referencias se tomaron la paleta y la disposición, y se descartó lo que da **forma**: el vidrio,
la decoración, los widgets del shell y los iconos. Un esquema de color sobre Breeze es, por definición, Breeze.

## 2. Por qué pasó

Decisiones 2.5, 3.1, 3.2 y 3.4 de `decisiones.md` privilegiaron estabilidad (Aurorae recién reescrito, Kvantum frágil,
contraste sobre fondos claros) y «heredar el mínimo». Son buenas razones para un esquema de color; son malas razones
para un tema que debe **verse**. El criterio del encargo era «la calidad visual es prioritaria» y «no des por terminado
un componente porque el archivo se instaló». Se cumplió lo segundo y no lo primero.

## 3. Cambio de enfoque (0.2.0: «Lliphi cristal»)

Fusión declarada: **el vidrio y el refinamiento de WhiteSur sobre la noche y el rojo de Nothing, con una capa tecnológica
propia** (retícula de puntos, hairlines luminosas, un punto rojo como firma, tipografía mono en el reloj y en los
detalles). Sin semáforos, sin logotipos, sin iconos ajenos.

| pieza | antes (0.1.0) | ahora (0.2.0) | cómo se comprueba |
|---|---|---|---|
| panel | opaco, radio 10 | **vidrio**: fondo al 55 % (oscuro) / 72 % (claro) con `[BlurBehindEffect]` y `[ContrastEffect]`, hairline superior luminosa, retícula de puntos al 6 %, radio 14 flotante | captura con una ventana clara detrás: se ve el desenfoque, no la ventana |
| diálogos, menús del shell, lanzador, notificaciones, tooltips | opacos | vidrio al 70 % con blur, borde hairline, sombra 32 px, radio 12 | lanzador abierto sobre una ventana |
| tareas del panel | Breeze | propias: cápsulas con indicador de 2 px en acento, estado activo con relleno al 14 %, atención con pulso rojo, 6 estados | dock con tres apps |
| botones, campos, pestañas, listas, deslizadores, barras del shell | Breeze | propias: radio 6, hairline, foco en acento de 2 px, campos en vidrio más oscuro | widgets del lanzador y de Preferencias rápidas |
| decoración de ventanas | Breeze | **Aurorae propia**: radio 10, barra de 30 px, anillos de 14 px (cerrar se vuelve rojo al pasar), sombra 40 px activa | Dolphin y Kate, activa e inactiva |
| iconos | Breeze + carpetas rojas | **línea fina propia** para lugares, dispositivos, categorías del lanzador, estado del panel y el lanzador (relámpago) con punto rojo | Dolphin, Kickoff y bandeja |
| menús de las aplicaciones Qt | opacos | Breeze con `MenuOpacity=78` (translúcidos con blur, de serie en Breeze) | menú de Kate |
| Konsole | opaco | opacidad 0.86 con blur | Konsole sobre el fondo |
| fondo | degradado | campo de puntos con relámpago de línea y halo | escritorio limpio |
| splash | Breeze | propio: marca + barra de puntos | reinicio de sesión |

Lo que **no** se promete: desenfoque donde KWin no lo aplique (sin compositor OpenGL no hay blur: se documenta),
Kvantum (sigue opcional) y SDDM/Plymouth (root).

## 4. Cómo se demuestra

Comparación visual **antes/después** con los mismos cinco casos de `validacion.md` (escritorio, lanzador, Dolphin +
Konsole + notificación, Preferencias, Kate) en las dos variantes, capturadas en una sesión real de Plasma 6.6, y una
hoja `muestras/comparacion-0.1-0.2.png` que las pone lado a lado. Después, aplicación en la sesión del autor.
