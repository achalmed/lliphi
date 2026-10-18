---
tipo: doc
estado: activo
titulo: 'Dirección artística (fase 4): principios, paleta OKLCH, tokens semánticos, contraste medido, tipografía, geometría y estados'
---
# Dirección artística

Fase 4 del encargo, 2026-10-18. Propuesta del director para aprobación del autor. La fuente de verdad es
`herramientas/paleta.py` (que escribe `tokens/tokens.json`); esta página explica las decisiones. El nombre
«Llampu» es provisional hasta que el autor lo apruebe (`docs/nombre.md`); vive en `tokens/marca.json`.

## 1. Principios

1. **Suavidad con estructura.** Superficies neutras de poca saturación, jerarquía por luminosidad (vista > ventana >
   botón) y bordes de 1 px tenues en vez de sombras pesadas. Lo que Nothing hace plano y WhiteSur hace translúcido,
   aquí se hace por planos.
2. **Un acento, y que siga al sistema.** Un verde azulado sereno (matiz 195) con dos luminosidades por variante; el
   esquema deja que Plasma lo sustituya por el acento del usuario o del fondo sin romper el contraste.
3. **Dos variantes, una lógica.** Mismos tokens semánticos, mismos radios, espacios y estados; cambian solo las
   primitivas. El día es papel cálido (matiz 80); la noche es pizarra fría (matiz 255): la marca cuenta el paso del
   día sin cambiar de forma.
4. **Legible antes que bonito.** Todo par texto/fondo ≥ 4.5:1 (WCAG 2.2, 1.4.3) y todo foco, acento y borde de
   control ≥ 3:1 (1.4.11), medido por el script y verificado como prueba.
5. **Nada de Apple ni de nadie.** Sin semáforos, sin logotipos, sin fuentes propietarias, sin SVG ajenos: la
   originalidad está en las proporciones, los radios, la paleta y los estados.
6. **Mínimo que hereda.** Lo que Breeze ya hace bien (iconos, decoración, GTK generado) no se reemplaza; se colorea.

## 2. Paleta

Primitivas en OKLCH (luminosidad, croma, matiz) convertidas a sRGB con mapeo de gama. Las semánticas son las
que consumen los generadores; `herramientas/paleta.py` imprime la tabla completa con hex, `R,G,B` y OKLCH.

| token semántico | claro | oscuro | papel |
|---|---|---|---|
| `fondo.vista` | `#fdfcf9` (L 0.99) | `#101419` (L 0.19) | contenido: listas, editores, campos |
| `fondo.ventana` | `#f1eeea` (L 0.95) | `#1b1f26` (L 0.245) | ventanas, diálogos, paneles |
| `fondo.boton` | `#e7e4df` (L 0.92) | L 0.32 | controles |
| `fondo.encabezado` | = ventana | L 0.22 (más profundo) | barras de título y herramientas |
| `fondo.tooltip` | `#2b2823` (inverso) | L 0.34 | tooltips |
| `fondo.complementario` | `#101419` | `#101419` | bloqueo y cierre de sesión: siempre oscuro |
| `texto.normal` | `#25211b` (L 0.25) | L 0.935 | texto |
| `texto.secundario` | L 0.42 | L 0.80 | metadatos |
| `texto.inactivo` | L 0.53 | L 0.68 | deshabilitado, marcadores |
| `acento.base` = `seleccion.fondo` | `#007272` (L 0.50 C 0.085) | `#008181` (L 0.545 C 0.10) | selección, acento |
| `acento.suave` = `hover` | L 0.575 | L 0.68 | pasar el ratón; foco en el oscuro |
| `acento.texto` = `enlace` | L 0.44 | L 0.76 | enlaces, texto activo |
| `foco` | = acento.base | = acento.suave | anillo de foco: el acento de mayor contraste de cada variante |
| `estado.error` | oklch(0.52 0.17 25) | oklch(0.74 0.15 25) | negativo |
| `estado.advertencia` | oklch(0.52 0.12 70) | oklch(0.80 0.12 75) | neutral |
| `estado.exito` | oklch(0.50 0.13 150) | oklch(0.76 0.13 150) | positivo |
| `estado.info` | oklch(0.52 0.12 250) | oklch(0.76 0.10 250) | información |
| `borde.separador` | L 0.86 | L 0.38 | separadores |

Decisiones de color:

- **Texto sobre el acento siempre claro** (`#fcfcfc`) en las dos variantes, por eso el acento oscuro sube de croma
  y baja de luminosidad hasta 4.63:1; en el claro queda en 5.63:1.
- **El foco no es el mismo color en las dos variantes**: en el oscuro usa `acento.suave` (L 0.68), porque el acento
  base solo llega a 2.68:1 sobre el botón; en el claro el acento base ya da 4.54:1.
- **El tooltip es inverso en el claro** (oscuro sobre papel) y una superficie elevada en el oscuro.
- **Los colores de estado tienen el mismo matiz en las dos variantes** y solo cambian de luminosidad; en el claro
  son texto legible (≥ 4.5:1), no pastel.

## 3. Contraste medido

Salida de `herramientas/paleta.py` (WCAG 2.1/2.2, sin redondeo). Los pares «jerarquía» son informativos.

```
== claro
  ok  texto.normal / fondo.ventana                13.83    4.5   1.4.3
  ok  texto.normal / fondo.vista                  15.55    4.5   1.4.3
  ok  texto.normal / fondo.boton                  12.63    4.5   1.4.3
  ok  texto.normal / fondo.encabezado             13.83    4.5   1.4.3
  ok  texto.secundario / fondo.ventana             7.32    4.5   1.4.3
  ok  texto.inactivo / fondo.ventana               4.56    4.5   1.4.3
  ok  texto.inactivo / fondo.vista                 5.13    4.5   1.4.3
  ok  texto.tooltip / fondo.tooltip               14.19    4.5   1.4.3
  ok  texto.complementario / fondo.complementario  15.26    4.5   1.4.3
  ok  seleccion.texto / seleccion.fondo            5.63    4.5   1.4.3
  ok  enlace / fondo.ventana                       6.46    4.5   1.4.3
  ok  enlace / fondo.vista                         7.27    4.5   1.4.3
  ok  estado.error / fondo.ventana                 5.19    4.5   1.4.3
  ok  estado.advertencia / fondo.ventana           4.88    4.5   1.4.3
  ok  estado.exito / fondo.ventana                 4.88    4.5   1.4.3
  ok  estado.info / fondo.ventana                  4.75    4.5   1.4.3
  ok  estado.error / fondo.vista                   5.84    4.5   1.4.3
  ok  foco / fondo.ventana                         4.97    3.0   1.4.11
  ok  foco / fondo.vista                           5.59    3.0   1.4.11
  ok  foco / fondo.boton                           4.54    3.0   1.4.11
  ok  hover / fondo.ventana                        3.62    3.0   1.4.11
  ok  hover / fondo.boton                          3.30    3.0   1.4.11
  ok  acento.base / fondo.ventana                  4.97    3.0   1.4.11
  ok  borde.separador / fondo.ventana              1.32    1.2   jerarquía (informativo)
  ok  fondo.vista / fondo.ventana                  1.12   1.05   jerarquía (informativo)
  ok  fondo.boton / fondo.ventana                  1.09   1.05   jerarquía (informativo)
== oscuro
  ok  texto.normal / fondo.ventana                13.40    4.5   1.4.3
  ok  texto.normal / fondo.vista                  15.26    4.5   1.4.3
  ok  texto.normal / fondo.boton                  10.48    4.5   1.4.3
  ok  texto.normal / fondo.encabezado             14.30    4.5   1.4.3
  ok  texto.secundario / fondo.ventana             8.69    4.5   1.4.3
  ok  texto.inactivo / fondo.ventana               5.63    4.5   1.4.3
  ok  texto.inactivo / fondo.vista                 6.41    4.5   1.4.3
  ok  texto.tooltip / fondo.tooltip                9.71    4.5   1.4.3
  ok  texto.complementario / fondo.complementario  15.26    4.5   1.4.3
  ok  seleccion.texto / seleccion.fondo            4.63    4.5   1.4.3
  ok  enlace / fondo.ventana                       7.84    4.5   1.4.3
  ok  enlace / fondo.vista                         8.92    4.5   1.4.3
  ok  estado.error / fondo.ventana                 6.60    4.5   1.4.3
  ok  estado.advertencia / fondo.ventana           8.55    4.5   1.4.3
  ok  estado.exito / fondo.ventana                 7.95    4.5   1.4.3
  ok  estado.info / fondo.ventana                  7.60    4.5   1.4.3
  ok  estado.error / fondo.vista                   7.51    4.5   1.4.3
  ok  foco / fondo.ventana                         5.87    3.0   1.4.11
  ok  foco / fondo.vista                           6.68    3.0   1.4.11
  ok  foco / fondo.boton                           4.59    3.0   1.4.11
  ok  hover / fondo.ventana                        5.87    3.0   1.4.11
  ok  hover / fondo.boton                          4.59    3.0   1.4.11
  ok  acento.base / fondo.ventana                  3.42    3.0   1.4.11
  ok  borde.separador / fondo.ventana              1.62    1.2   jerarquía (informativo)
  ok  fondo.vista / fondo.ventana                  1.14   1.05   jerarquía (informativo)
  ok  fondo.boton / fondo.ventana                  1.28   1.05   jerarquía (informativo)
resultado: todos los pares cumplen
```

## 4. Tipografía

| uso | familia | motivo |
|---|---|---|
| interfaz | **Inter** (OFL; instalada), 10 pt; reserva Noto Sans | neutra, métrica estable en pantalla, cifras tabulares |
| monoespaciada | **IBM Plex Mono** (OFL; instalada), 10 pt; reserva Hack | contraste de formas claro; buena en Konsole y editores |
| títulos del sitio | Inter Display | la misma familia, con ópticos para tamaños grandes |

El tema **no impone fuentes** en `defaults`: cambiar la fuente del usuario es intrusivo. El instalador las ofrece
con `--fuentes` y el sitio las documenta. Nada de `SFNS Display` ni de fuentes propietarias.

## 5. Geometría

| magnitud | valor | dónde |
|---|---|---|
| unidad de espaciado | 4 px; escala 4 · 8 · 12 · 16 · 24 · 32 | márgenes de paneles (8), diálogos (12/16), separación de controles (8) |
| radio de controles | 4 px | botones, campos, casillas |
| radio de menús y emergentes | 6 px | menús, tooltips, desplegables |
| radio de ventanas y diálogos | 8 px | marcos, diálogos de Plasma |
| radio del panel flotante | 10 px | panel |
| borde | 1 px, `borde.sutil` (opaco) o texto al 12 % de opacidad | separa planos sin sombra |
| sombra | suave, 0–24 px, texto al 18 % en claro y negro al 45 % en oscuro | emergentes y ventanas |
| alto del panel | 36 px (fino) y dock opcional de 56 px | disposición |
| translucidez | ninguna en panel y ventanas por defecto; menús y tooltips opacos; variante «translúcida» como módulo posterior con contraste medido | evita el 3.27:1 de WhiteSur sobre fondos claros |

## 6. Estados interactivos

| estado | regla |
|---|---|
| reposo | superficie del rol, borde sutil |
| encima (hover) | borde y relleno con `hover` (acento suave) al 100 % en el borde y 12 % en el relleno |
| foco (teclado) | anillo de 2 px con `foco`, nunca tapado (2.4.11), además del estado encima |
| activo / pulsado | relleno `acento.base` con `texto.sobre-acento` |
| seleccionado | `seleccion.fondo` + `seleccion.texto`; inactivo: la misma selección con `acento.suave` al 60 % |
| deshabilitado | texto `texto.inactivo`; relleno sin cambio; sin borde de acento |
| error, advertencia, éxito, info | solo el color de estado en texto o borde, nunca como fondo pleno |

## 7. Muestras

`muestras/claro.png` y `muestras/oscuro.png`: widgets reales de Qt con el estilo Breeze y el esquema generado
(`herramientas/lamina.py`, sin pantalla). Límite de la lámina: fuera de una sesión de Plasma el estilo no lee el
color de foco del esquema, por eso el deslizador y la barra de progreso salen en azul Breeze; en el escritorio real
siguen al esquema (se comprueba en la fase 7).

## 8. Lo que decide el autor

1. La paleta (acento verde azulado 195; papel cálido y pizarra fría), o un acento distinto: el script admite cambiar
   `ACENTO_H` y vuelve a medir.
2. El nombre (`docs/nombre.md`).
