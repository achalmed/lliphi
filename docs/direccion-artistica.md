---
tipo: doc
estado: activo
titulo: 'Dirección artística (fase 4): principios, paleta OKLCH, tokens semánticos, contraste medido, tipografía, geometría y estados'
---
# Dirección artística

Fase 4 del encargo, 2026-10-18. Propuesta del director para aprobación del autor. La fuente de verdad es
`herramientas/paleta.py` (que escribe `tokens/tokens.json`); esta página explica las decisiones. Primera propuesta
(acento verde azulado) rechazada por el autor el 2026-10-18 por no ser la fusión de Nothing y WhiteSur que pidió;
esta es la segunda.

## 1. Principios

1. **La fusión que pidió el autor.** De Nothing: superficies casi negras de tono único (`#1b1c1e`, el `#1b1b1d` de
   Nothing llevado a OKLCH), un solo acento rojo, barra superior fina y dock flotante que se oculta. De WhiteSur:
   la jerarquía de planos (vista > ventana > botón), los radios redondeados, los márgenes de 8 px, el borde de 1 px
   tenue y la familia claro/oscuro con escalas. De ninguno: el semáforo, el logo y la fuente de Apple, el appmenu
   global, Kvantum, los cursores WhiteSur y los colores fijos en los SVG.
2. **Un acento, y que siga al sistema.** El rojo es el acento principal (`rojo` en `herramientas/paleta.py`), medido
   para cumplir 4.5:1 con texto claro. Los otros dos (`azul`, el de WhiteSur; `verde-azul`) se generan con
   `--acento` como variantes; y como el esquema sigue el acento de Plasma 6, el usuario puede cambiarlo desde
   Preferencias sin tocar el tema.
3. **Dos variantes, una lógica.** Mismos tokens semánticos, radios, espacios y estados; cambian solo las primitivas.
   Los neutros comparten un matiz frío apenas perceptible (270, croma ≤ 0.006): el oscuro es la noche de Nothing;
   el claro, el gris suave de WhiteSur claro.
4. **Legible antes que bonito.** Todo par texto/fondo ≥ 4.5:1 (WCAG 2.2, 1.4.3) y todo foco, acento y borde de
   control ≥ 3:1 (1.4.11), medido por el script y verificado como prueba.
5. **Mínimo que hereda.** Lo que Breeze ya hace bien (iconos, decoración, GTK generado) no se reemplaza; se colorea.

## 2. Paleta

Primitivas en OKLCH (luminosidad, croma, matiz) convertidas a sRGB con mapeo de gama. `herramientas/paleta.py`
imprime la tabla completa con hex, `R,G,B` y OKLCH; aquí, los tokens que más pesan.

| token semántico | claro | oscuro | papel |
|---|---|---|---|
| `fondo.vista` | `#fbfcfd` (L 0.99) | `#101012` (L 0.175) | contenido: listas, editores, campos |
| `fondo.ventana` | `#ecedef` (L 0.945) | `#1b1c1e` (L 0.225) | ventanas, diálogos, paneles |
| `fondo.boton` | `#e0e1e5` (L 0.91) | `#2e2f32` (L 0.305) | controles |
| `fondo.encabezado` | = ventana | = vista (más profundo) | barras de título y herramientas |
| `fondo.tooltip` | L 0.26 (inverso) | L 0.32 | tooltips |
| `fondo.complementario` | `#101012` | `#101012` | bloqueo y cierre de sesión: siempre oscuro |
| `texto.normal` | `#1d1f24` (L 0.24) | `#eaebed` (L 0.94) | texto |
| `texto.secundario` | L 0.42 | L 0.80 | metadatos |
| `texto.inactivo` | L 0.515 | L 0.68 | deshabilitado, marcadores |
| `acento.base` = `seleccion.fondo` | `#c53133` (L 0.545 C 0.185 H 25) | `#c93436` (L 0.555) | selección, acento |
| `acento.suave` = `hover` | `#da534f` (L 0.62) | `#ef6661` (L 0.68) | pasar el ratón; foco en el oscuro |
| `acento.texto` = `enlace` | `#b51e26` (L 0.50) | `#ff958d` (L 0.78) | enlaces, texto activo |
| `foco` | = acento.base | = acento.suave | anillo de foco: el acento de mayor contraste de cada variante |
| `estado.error` | oklch(0.52 0.17 25) | oklch(0.74 0.15 25) | negativo |
| `estado.advertencia` | oklch(0.52 0.12 70) | oklch(0.80 0.12 75) | neutral |
| `estado.exito` | oklch(0.50 0.13 150) | oklch(0.76 0.13 150) | positivo |
| `estado.info` | oklch(0.52 0.12 250) | oklch(0.76 0.10 250) | información |
| `borde.separador` | L 0.85 | L 0.365 | separadores |

Decisiones de color:

- **El rojo de Nothing (`#eb3131`, 4.11:1 con texto blanco) baja a L 0.545–0.555** para cumplir 4.5:1 como fondo de
  selección con texto claro en las dos variantes (5.1:1 y 4.9:1); el tono se conserva (matiz 25).
- **El foco no es el mismo color en las dos variantes**: en el oscuro usa `acento.suave` (`#ef6661`) para llegar a
  4.3:1 sobre el botón; en el claro el acento base ya da 4.2:1.
- **El error (negativo) comparte matiz con el acento**; se distingue por contexto (texto o borde, nunca fondo
  pleno) y porque el acento no se usa como texto de aviso.
- **El tooltip es inverso en el claro** (oscuro sobre gris) y una superficie elevada en el oscuro.
- **Variantes de acento**: `azul` (oklch 0.50/0.56, 0.17, 262: el azul de WhiteSur llevado a 4.5:1) y `verde-azul`
  (195) existen en el script y se publican como esquemas adicionales si el autor lo pide.

## 3. Contraste medido

Salida de `herramientas/paleta.py` (WCAG 2.1/2.2, sin redondeo). Los pares «jerarquía» son informativos.

```
== claro
  ok  texto.normal / fondo.ventana                14.01    4.5   1.4.3
  ok  texto.normal / fondo.vista                  15.99    4.5   1.4.3
  ok  texto.normal / fondo.boton                  12.59    4.5   1.4.3
  ok  texto.normal / fondo.encabezado             14.01    4.5   1.4.3
  ok  texto.secundario / fondo.ventana             7.21    4.5   1.4.3
  ok  texto.inactivo / fondo.ventana               4.79    4.5   1.4.3
  ok  texto.inactivo / fondo.vista                 5.47    4.5   1.4.3
  ok  texto.tooltip / fondo.tooltip               15.10    4.5   1.4.3
  ok  texto.complementario / fondo.complementario  15.91    4.5   1.4.3
  ok  seleccion.texto / seleccion.fondo            5.33    4.5   1.4.3
  ok  enlace / fondo.ventana                       5.63    4.5   1.4.3
  ok  enlace / fondo.vista                         6.42    4.5   1.4.3
  ok  estado.error / fondo.ventana                 5.12    4.5   1.4.3
  ok  estado.advertencia / fondo.ventana           4.81    4.5   1.4.3
  ok  estado.exito / fondo.ventana                 4.81    4.5   1.4.3
  ok  estado.info / fondo.ventana                  4.68    4.5   1.4.3
  ok  estado.error / fondo.vista                   5.84    4.5   1.4.3
  ok  foco / fondo.ventana                         4.64    3.0   1.4.11
  ok  foco / fondo.vista                           5.29    3.0   1.4.11
  ok  foco / fondo.boton                           4.17    3.0   1.4.11
  ok  hover / fondo.ventana                        3.36    3.0   1.4.11
  ok  hover / fondo.boton                          3.02    3.0   1.4.11
  ok  acento.base / fondo.ventana                  4.64    3.0   1.4.11
  ok  borde.separador / fondo.ventana              1.35    1.2   jerarquía (informativo)
  ok  fondo.vista / fondo.ventana                  1.14   1.05   jerarquía (informativo)
  ok  fondo.boton / fondo.ventana                  1.11   1.05   jerarquía (informativo)
== oscuro
  ok  texto.normal / fondo.ventana                14.34    4.5   1.4.3
  ok  texto.normal / fondo.vista                  15.91    4.5   1.4.3
  ok  texto.normal / fondo.boton                  11.24    4.5   1.4.3
  ok  texto.normal / fondo.encabezado             15.91    4.5   1.4.3
  ok  texto.secundario / fondo.ventana             9.15    4.5   1.4.3
  ok  texto.inactivo / fondo.ventana               5.94    4.5   1.4.3
  ok  texto.inactivo / fondo.vista                 6.58    4.5   1.4.3
  ok  texto.tooltip / fondo.tooltip               10.64    4.5   1.4.3
  ok  texto.complementario / fondo.complementario  15.91    4.5   1.4.3
  ok  seleccion.texto / seleccion.fondo            5.11    4.5   1.4.3
  ok  enlace / fondo.ventana                       8.11    4.5   1.4.3
  ok  enlace / fondo.vista                         9.00    4.5   1.4.3
  ok  estado.error / fondo.ventana                 6.96    4.5   1.4.3
  ok  estado.advertencia / fondo.ventana           9.02    4.5   1.4.3
  ok  estado.exito / fondo.ventana                 8.38    4.5   1.4.3
  ok  estado.info / fondo.ventana                  8.01    4.5   1.4.3
  ok  estado.error / fondo.vista                   7.72    4.5   1.4.3
  ok  foco / fondo.ventana                         5.50    3.0   1.4.11
  ok  foco / fondo.vista                           6.10    3.0   1.4.11
  ok  foco / fondo.boton                           4.31    3.0   1.4.11
  ok  hover / fondo.ventana                        5.50    3.0   1.4.11
  ok  hover / fondo.boton                          4.31    3.0   1.4.11
  ok  acento.base / fondo.ventana                  3.28    3.0   1.4.11
  ok  borde.separador / fondo.ventana              1.61    1.2   jerarquía (informativo)
  ok  fondo.vista / fondo.ventana                  1.11   1.05   jerarquía (informativo)
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

`muestras/boceto-claro.png` y `muestras/boceto-oscuro.png`: boceto del escritorio (panel fino, lanzador, ventana
redondeada, notificación, tooltip, dock flotante) dibujado con los tokens por `herramientas/boceto.py`; **no es una
captura**. `muestras/claro.png` y `muestras/oscuro.png`: widgets reales de Qt con el estilo Breeze y el esquema generado
(`herramientas/lamina.py`, sin pantalla). Límite de la lámina: fuera de una sesión de Plasma el estilo no lee el
color de foco del esquema, por eso el deslizador y la barra de progreso salen en azul Breeze; en el escritorio real
siguen al esquema (se comprueba en la fase 7).

## 8. Lo que decide el autor

1. La paleta corregida (rojo de Nothing sobre neutros casi negros y grises suaves): aprobación o cambio de acento
   (`--acento azul|verde-azul`, o un matiz nuevo).
2. El nombre: **Llampu**, aprobado el 2026-10-18.
