---
tipo: doc
estado: activo
titulo: 'Análisis de los dos temas de partida (Nothing y WhiteSur-dark) en disco: inventario, mecánica, contraste, licencias y decisiones'
---
# Análisis de los temas de partida: Nothing y WhiteSur-dark

Fase 2 del encargo. Análisis en solo lectura de los paquetes instalados en `~/.local/share` el 2026-10-18 (Plasma
6.6.6), hecho por un agente de la sesión y comprobado al azar por el director (recuento del rojo fijo, `widgetStyle`,
fuente de Apple, SVG idénticos a Breeze: todo coincide). Los radios y márgenes medidos sobre el render llevan «≈».
Lo que no está en disco se dice como tal.

## 0. Hallazgos principales

| # | hallazgo | evidencia |
|---|---|---|
| 1 | **Nothing es en gran parte Breeze recoloreado.** Su `desktoptheme` copia los 43 widgets de Breeze `default`; de sus 111 SVG, 60 son idénticos byte a byte (descomprimidos) a los de `/usr/share/plasma/desktoptheme/default`. | `tasks.svgz` de Nothing y el de Breeze tienen los mismos 225 ids; la única diferencia es que los trazos `ColorScheme-ButtonFocus` fijan `fill:#eb3131`. |
| 2 | **Nothing fija el acento rojo `#eb3131` en el código**: 258 apariciones en 19 SVG (`tasks` 80, `viewitem` 36, `containment-controls` 20, `tabbar` 18, `glowbar` 16…). | No sigue el color de acento del sistema. El fondo `#1b1b1d` también está fijo (120 apariciones) con opacidad 1. |
| 3 | **El Aurorae de Nothing es un fork del de WhiteSur.** | Mismo lienzo 355×310, mismas capas e ids autogenerados (`6utrh-9`, `hrh-6`, `decoration-toplefthaerty-5`). |
| 4 | **El `defaults` de Nothing copia la estructura del de WhiteSur** y usa su cursor `WhiteSur-cursors`. | Mismo paquete KDE Store 1411743 que WhiteSur declara como dependencia. |
| 5 | **Nothing tiene dos paletas que no se hablan**: `color-schemes/Nothing.colors` (Window `27,27,29`) y `desktoptheme/Nothing/colors` (botón `240,10,23`, grises de Catppuccin Macchiato). | Los hex `cad3f5`, `939ab7`, `8087a2`, `b8c0e0`, `181926` son de esa paleta (conocimiento del agente, no un archivo local). |
| 6 | **WhiteSur-dark exige Kvantum, que no está instalado.** | `defaults`: `widgetStyle=kvantum-dark`; no existen `~/.config/Kvantum` ni el plugin de estilo (solo `breeze6.so` y `oxygen6.so`). |
| 7 | **Imitación literal de Apple.** | Splash con el logo de Apple (`splash/images/logo.svg`, renderizado), appmenu global en el panel, semáforos rojo/verde/amarillo; Nothing usa la fuente `SFNS Display` (Apple, no instalada) en el reloj. |

## 1. Inventario de componentes

### 1.1 Nothing (jomada; KDE Store 2116667)

| capa | archivos | contenido |
|---|---|---|
| look-and-feel | `plasma/look-and-feel/Nothing/{metadata.json, contents/defaults, contents/layouts/org.kde.plasma.desktop-layout.js, contents/previews/}` | v1.8, «GPL 3+», 7 dependencias `kns://` (esquema, tema Plasma, Aurorae, cursor, 3 fondos). **No trae** splash, lockscreen, logout, osd ni switcher, ni declara `X-KDE-fallbackPackage`. |
| desktoptheme | `plasma/desktoptheme/Nothing/` (1,5 MB) | v1.5, «LGPL». `colors`, `plasmarc`, 111 SVG (widgets 43, icons 66, dialogs 1, weather 1). Sin `solid/`, `translucent/` ni `opaque/`. |
| esquema | `color-schemes/Nothing.colors` | §1.3. Sin `[Colors:Header]`; `Complementary` incompleto. |
| Aurorae | `aurorae/themes/Nothing/{Nothingrc, decoration.svg, close, maximize, minimize, restore, alldesktops, keepabove, keepbelow}.svg` | §1.4; `GPL_V3`. |
| Konsole | `konsole/Nothing.colorscheme` | fondo `27,27,29`, texto `255,255,255`, `Opacity=0.8`, `Blur=true`; paleta atípica: Color0 (negro) = azul `38,64,211`, Color4 (azul) = rojo `235,49,49`. |
| fondos | `wallpapers/Nothing1` (5521×2487), `Nothing2`, `Nothing3` | CC BY-SA 4.0, jomada. |
| iconos, cursores | no trae | `defaults` fija `breeze-dark` y `WhiteSur-cursors`. |

### 1.2 WhiteSur-dark (vinceliuice; KDE Store 1400424)

| capa | archivos | contenido |
|---|---|---|
| look-and-feel | `…/com.github.vinceliuice.WhiteSur-dark/contents/{defaults, layouts/, splash/{Splash.qml, images/}, logout/{Logout.qml, LogoutButton.qml, timer.js}, previews/}` | «GPLv3», `X-KDE-fallbackPackage=org.kde.breeze.desktop`; 7 dependencias `kns://` (SDDM e iconos incluidos). **No trae lockscreen.** Logout y splash son copia de Breeze (SPDX `GPL-2.0-or-later`, Aleix Pol). |
| desktoptheme | `plasma/desktoptheme/WhiteSur-dark/` (1,4 MB) | v6.2.0, «GPL-3.0». `colors`, `plasmarc`, 116 SVG (widgets 34, icons 77, dialogs 1, weather 1, `solid/` 3); `translucent/` existe vacío. |
| esquemas | `color-schemes/{WhiteSur, WhiteSurDark, WhiteSurAlt}.colors` | `WhiteSurAlt` solo cambia `ForegroundNormal` de 36 a 54 en tres grupos. |
| Aurorae | 11 carpetas (`WhiteSur`, `-dark`, `-Sharp`, `-Sharp-dark`, `-dark-opaque`, `×1.25`, `×1.5` y combinaciones) | 10 archivos cada una; §4. |
| iconos | `icons/WhiteSur` (11 434 archivos + 15 258 enlaces, 62 MB), `WhiteSur-dark` (7 311 + 5 824, 32 MB), `WhiteSur-light` (1 455 + 1 817, 7 MB) | `Inherits=hicolor,breeze`, `FollowsColorScheme=true`; 36 enlaces rotos (`weather-clear-night-*`) en dos familias. |
| cursores | `~/.icons/WhiteSur-cursors` (3,2 MB) | 48 archivos + 64 enlaces; `index.theme` mínimo. |
| fondo | `wallpapers/WhiteSur/contents/images/3840x2160.png` | CC BY-SA 4.0, estilo Big Sur. |
| Konsole | no trae | — |

### 1.3 Esquemas de color: valores clave

| grupo / clave | Nothing | WhiteSurDark | Breeze Dark |
|---|---|---|---|
| Window fondo | 27,27,29 `#1b1b1d` | 54,54,54 `#363636` | 32,35,38 |
| View fondo (alterno) | 27,27,29 (27,27,29) | 36,36,36 (48,48,48) | 20,22,24 (29,31,34) |
| texto Window | 252,253,253 | 252,252,252 | 252,252,252 |
| botón fondo | 50,50,54 | 101,101,101 | — |
| selección fondo / texto | 235,49,49 / 254,254,254 | 49,91,239 / 255,255,255 | 61,174,233 / 252,252,252 |
| `DecorationFocus` | 39,39,42 | 49,91,239 | 61,174,233 |
| `DecorationHover` | 235,49,49 | 49,91,239 | 61,174,233 |
| Header | ausente | 54,54,54 (inactivo 51,51,51) | — |
| Tooltip fondo | 39,39,42 | 51,51,51 | — |
| `[WM]` activo fondo / texto | 27,27,29 / 237,240,242 | 51,51,51 / 252,252,252 | — |
| `[KDE] contrast` | 4 | 4 | — |
| efectos | `Inactive`: `ColorAmount=-0.95`, activo | `Inactive` desactivado | — |

`desktoptheme/Nothing/colors` es otra paleta (botón `240,10,23`, texto `202,211,245`, Tooltip `30,32,48`, Selection
`212,21,21`); `desktoptheme/WhiteSur-dark/colors` es casi igual a `WhiteSurDark.colors`.

### 1.4 Aurorae

| valor (`*rc`) | Nothing | WhiteSur-dark |
|---|---|---|
| bordes L/R/B | 2 / 2 / 7 px | 1 / 1 / 12 px |
| `TitleHeight` | 15 | 16 |
| `TitleEdge` T/B/L/R | 4 / 4 / 7 / 7 | 8 / 8 / 16 / 16 |
| botones | 12×12, separación 8 | 16×16, separación 10 |
| orden y lado | `LeftButtons=XIA` (cerrar, maximizar, minimizar a la izquierda) | igual; `defaults` impone `ButtonsOnLeft=XAI` |
| padding (sombra) T/B/L/R | 35 / 90 / 76 / 76 | 36 / 95 / 76 / 76 |
| fondo del título | `#1b1b1d` fijo | `#363636` activo, `#2d2d2d` inactivo |
| texto del título | 202,211,245 / inactivo 154,161,188 | 225,225,225 / inactivo 120,120,120 |
| sombra de texto | blanca, offset 1 (sin sentido en oscuro) | igual |
| esquina (render) | ≈4 px | ≈11–12 px con borde de 1 px |
| botones SVG | círculos con cinco estados; cierre rojo con degradado | semáforo macOS rojo, verde, amarillo |

## 2. `defaults` y `layouts`

| | Nothing | WhiteSur-dark |
|---|---|---|
| esquema | `Nothing` | `WhiteSurDark` |
| estilo de widgets | `Breeze` | `kvantum-dark` (no instalado) |
| iconos | `breeze-dark` | `WhiteSur-dark` |
| cursor | `WhiteSur-cursors` | `WhiteSur-cursors` |
| decoración | `__aurorae__svg__Nothing` | `__aurorae__svg__WhiteSur-dark` + `ButtonsOnLeft=XAI` |
| tema Plasma | `Nothing` | `WhiteSur-dark` |
| fondo | `Nothing1` | no lo fija |
| switchers | `org.kde.breeze.desktop` | `org.kde.breeze.desktop` |

- **Layout de Nothing** (JS serializado, 153 líneas): panel superior fino (`height` 1.625 unidades, ≈32 px, centrado, longitud 120) con kickoff, appmenu, reloj (`SFNS Display` 15) y bandeja; dock inferior flotante (`height` 3.25, ≈65 px, `hiding windowscover`) solo con `icontasks`. La clave `floating` aparece dos veces con valores contradictorios (error).
- **Layout de WhiteSur** (JS imperativo): panel superior `2*floor(gridUnit*2.5/2)` con kickoff, appmenu, bandeja, reloj y `showdesktop`; dock inferior `fit`, `dodgewindows`, alto 64, `icontasks` con cuatro lanzadores.

## 3. Mecánica visual de los SVG

| elemento | Nothing | WhiteSur-dark | Breeze `default` |
|---|---|---|---|
| `widgets/panel-background` | un solo juego de losas; fondo `#1b1b1d` opaco; radio ≈12–14 px; hints 3/3/3/3 | tres juegos (normal, `north-`, `south-`); negro con opacidad 0.45; radio ≈12 (16 en `south-`); hints 8/8/8/8; hairline blanca 0.1 | `currentColor`, radio 6, hints 4/4/4/4 |
| `widgets/background` | opaco, borde 1 px `#26272a`, radio ≈4; **sin `hint-*-margin`** | `#1a1a1a` al 0.96, radio ≈10–12, hints de **24 px** (incluye sombra) | `currentColor`, radio ≈4 |
| `dialogs/background` | opaco, radio ≈4, hints 4/4/4/4, sombra 30 | 0.65, radio 12, hints 8/8/8/8 | — |
| `widgets/tooltip` | como el fondo | radio 12, hints 8/8/8/8 | — |
| `widgets/tasks` | Breeze con rojo fijo | reescrito: 30 ids, seis estados, hints 2/2/2/2 | con `north-`, `west-`, `east-` |
| `widgets/button` | tres estados; **sin `focus`**, `flat` ni `disabled` | 48 ids como Breeze, `focus` presente | 128 ids |

- Ninguno sigue el esquema del sistema en sus fondos principales: ambos fijan el hex. Nothing conserva `currentColor` en 75 de 111 SVG heredados de Breeze y pisa a mano los acentos.
- WhiteSur es translúcido por SVG (0.45 panel, 0.65 diálogo, 0.96 widget); Nothing es opaco por SVG.
- `plasmarc`: ambos `[ContrastEffect] contrast=0.2`, `saturation=10` (Breeze: 1.0 y 1.5), `[AdaptiveTransparency] enabled=true`; ninguno define `[BlurBehind]`.
- Las sombras se dibujan en el propio SVG (grupos `shadow-*`, hints de 10 a 30 px).

## 4. Variantes y escalas

- WhiteSur resuelve las variantes **duplicando archivos**: 11 carpetas Aurorae con los mismos 10 archivos; en `×1.25` y `×1.5` el `rc` es idéntico (mismo md5) y solo cambia el lienzo de `decoration.svg` (900×320, 1100×400); `Sharp` cambia `BorderBottom=1` y `PaddingBottom=86`; `opaque` solo cambia `decoration.svg`.
- Nothing no tiene variantes ni escalas.
- Un diseño propio genera las variantes desde una sola fuente; la duplicación es lo que hace WhiteSur, no un modelo.

## 5. Juicio de diseño

| | bueno y reutilizable como idea | imitación o defecto |
|---|---|---|
| **Nothing** | fondo de tono único cálido-neutro con un solo acento; barra superior fina y dock flotante que se oculta; esquinas casi rectas en ventanas (≈4 px); Konsole al 0.8 | monocromo extremo (Window = View, ratio 1.00); rojo fijo que ignora el acento; foco casi invisible; botón sin `focus`; sin splash, lockscreen ni logout; fuente de Apple; botones a la izquierda estilo macOS; dos paletas incoherentes; Konsole con Color0 azul y Color4 rojo |
| **WhiteSur-dark** | proporciones (panel ≈44–48 px, dock 64 con `dodgewindows`); borde de 1 px muy tenue que separa planos; márgenes de 8 px; jerarquía Window 54 / View 36 / Botón 101 (ratios 1.28 y 2.07); tareas con seis estados; título de 16 px | semáforo a la izquierda, logo de Apple, appmenu global, `kvantum-dark`, fondo Big Sur, carpetas azules; azul `49,91,239` fijo; sombra blanca de texto; `translucent/` vacío |

## 6. Contraste (WCAG 2.2, 1.4.3 texto 4.5:1 y 1.4.11 no textual 3:1)

| par | Nothing.colors | Nothing `desktoptheme/colors` | WhiteSurDark | Breeze Dark |
|---|---|---|---|---|
| Window texto / fondo | 16.88 | 11.59 | 11.78 | 15.39 |
| Window texto inactivo / fondo | 15.47 | **2.66** | 4.62 | 6.64 |
| View texto / fondo | 17.05 | 15.77 | 15.13 | 17.68 |
| botón texto / fondo | 12.66 | **4.05** | 5.68 | 13.67 |
| selección texto / fondo | **4.15** | 4.92 | 5.42 | **2.43** |
| tooltip | 14.62 | 16.10 | 12.32 | 13.67 |
| enlace sobre Window | **4.00** | 4.84 | **2.23** | 5.19 |
| título activo / fondo (Aurorae) | 11.59 | — | 9.24 | — |
| título inactivo / fondo | 6.71 | — | **3.12** | — |
| foco / fondo (1.4.11) | **1.15** | 4.84 | **2.23** | 6.34 |
| Window / View (jerarquía) | 1.00 | 1.00 | 1.28 | 1.15 |

- Rojo `#eb3131` sobre `27,27,29`: 4.11 (falla como texto; pasa como gráfico).
- Konsole de Nothing: texto 17.20; fallan Color0 (2.26), Color4 (4.11), Color5 (4.14) y tres «Intense».
- WhiteSur con transparencia (solo alfa, sin desenfoque): texto sobre el panel al 0.45 cae a **3.27** con fondo blanco; diálogo al 0.65, 5.26; widget al 0.96, 15.29.
- Ni el rojo de Nothing (4.15) ni el azul de Breeze (2.43) bastan como fondo de selección con texto blanco; el azul de WhiteSur (5.42) sí.

## 7. Licencias y procedencia

| pieza | licencia declarada | observación |
|---|---|---|
| Nothing look-and-feel | «GPL 3+» | sin cabeceras SPDX |
| Nothing desktoptheme | «LGPL» | derivado de Breeze `default` (LGPL) con rojo propio y grises de Catppuccin (MIT) |
| Nothing Aurorae | `GPL_V3` | fork del de WhiteSur |
| Nothing fondos | CC BY-SA 4.0 | atribución y misma licencia |
| WhiteSur look-and-feel | «GPLv3»; `logout/*` SPDX `GPL-2.0-or-later` | el logout es de KDE, no de vinceliuice |
| WhiteSur desktoptheme y Aurorae | «GPL-3.0» / `GPL_V3` | repo `vinceliuice/WhiteSur-kde` |
| WhiteSur fondo | CC BY-SA 4.0 | — |
| Breeze | `default` «LGPL»; look-and-feel «GPLv2+» | base del sistema |
| logo de Apple, `SFNS Display` | no libres | marca registrada y fuente propietaria |

Consecuencias: reutilizar código o SVG de cualquiera de los dos obliga a GPLv3 (o compatible) para el resultado; lo
que es solo inspiración (proporciones, valores, disposición, la idea de un acento único) queda libre; no se tocan el
logo de Apple, la fuente de Apple, el semáforo ni los fondos de ambos.

## 8. Decisiones propuestas

- **Esquema de color único y coherente → rediseñar.** Una sola paleta alimenta `.colors`, `desktoptheme/colors`, Aurorae y Konsole.
- **Jerarquía de planos → conservar la idea de WhiteSur** (Window > View > Botón, ratios ≈1.3 y 2) y descartar el monocromo plano de Nothing.
- **Acento → rediseñar.** Un solo acento con ≥ 4.5:1 como fondo de selección con texto claro, que siga el acento del sistema (`currentColor`) y no un hex fijo.
- **Foco visible → rediseñar.** `DecorationFocus` ≥ 3:1 y estado `focus` en `button.svgz`.
- **Barra superior fina + dock flotante que se oculta → conservar la geometría como idea**; reloj con una fuente libre instalada (Inter o IBM Plex Sans); sin la clave `floating` duplicada.
- **Radios → rediseñar.** Escala única (≈4 px controles, ≈8–10 px ventanas y paneles).
- **Márgenes de 8 px y borde de 1 px tenue → conservar**; rediseñar los 24 px de `widgets/background` y declarar siempre `hint-*-margin`.
- **Translucidez → rediseñar.** Opacidades que mantengan ≥ 4.5:1 sobre fondo claro, o panel opaco y translucidez solo en menús.
- **Variantes y escalas → generar desde una sola fuente**, nunca duplicar archivos.
- **Semáforo a la izquierda, appmenu global, logo de Apple, `kvantum-dark`, fondo Big Sur, carpetas azules → descartar** por encargo y por marca.
- **Botones de ventana → rediseñar**: orden y lado propios, sin sombra blanca de texto.
- **Splash, lockscreen y logout → heredar de Breeze con `X-KDE-fallbackPackage`** hasta diseñar los propios.
- **Konsole → rediseñar**: paleta ANSI con significado y ≥ 4.5:1 también en «Intense».
- **Iconos y cursores → no depender de WhiteSur**: `breeze-dark`/`breeze` y `breeze_cursors` al principio.
- **Heredar de Breeze solo lo no modificado, y declararlo**: Nothing copia 60 SVG idénticos que bastaría heredar.
