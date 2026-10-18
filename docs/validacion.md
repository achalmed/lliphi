---
tipo: doc
estado: activo
titulo: 'Validación (fase 7): instalación en una sesión limpia, capturas reales por variante y caso, defectos y límites'
---
# Validación

Fase 7 del encargo, 2026-10-18, Plasma 6.6.6 (Wayland). Método: una **sesión de Plasma anidada** en una ventana
de 1600×900 (`kwin_wayland --xwayland --exit-with-session=startplasma-wayland` bajo `dbus-run-session`) con un
`HOME` aparte en `/tmp/casa-lliphi`, de modo que la configuración del autor no se toca. En ese `HOME` se instaló
el primer lote con `herramientas/instalar.py --aplicar` (respaldo, manifiesto y `UNDO.sh` comprobados), se aplicó
cada variante con `plasma-apply-lookandfeel`, `plasma-apply-colorscheme` y `plasma-apply-wallpaperimage` **con el
DBus de la sesión anidada**, y se capturó desde dentro con `spectacle -b -n`. El usuario `prueba-tema` queda
disponible para una segunda validación con inicio de sesión real (SDDM, splash, bloqueo).

## 1. Capturas reales (`../muestras/capturas/`)

| caso | oscuro | claro | qué se comprueba |
|---|---|---|---|
| escritorio con panel superior y dock | `oscuro-01-escritorio.png` | `claro-01-escritorio.png` | panel fino de 36 px, dock flotante centrado, fondo con variante oscura |
| lanzador (Kickoff) | `oscuro-02-lanzador.png` | `claro-02-lanzador.png` | selección y foco en rojo, superficies por planos, texto legible |
| Dolphin + Konsole + notificación | `oscuro-03-…png` | `claro-03-…png` | selección en listas, foco en elemento, notificación de Plasma (tooltip/dialogs del estilo) |
| Preferencias del sistema → Colores | `oscuro-04-…png` | `claro-04-…png` | el esquema aparece y se aplica; encabezados; acento del esquema |
| Kate | `oscuro-05-kate.png` | `claro-05-kate.png` | aplicación Qt grande: menús, pestañas, barras |

Las vistas previas de los paquetes globales (`generado/look-and-feel/*/contents/previews/`) son ya estas
capturas (caso 02), no el boceto.

## 2. Resultado por componente

| componente | estado | observación |
|---|---|---|
| esquemas `LliphiClaro` / `LliphiOscuro` | **probado** | aparecen en el KCM de colores y se aplican; selección, foco, enlaces y estados con los colores de los tokens |
| tema global (`org.lliphi.claro` / `.oscuro`) | **probado** | `plasma-apply-lookandfeel -a` aplica esquema, estilo, iconos, cursores y decoración; la disposición (`--resetLayout`) crea el panel superior y el dock |
| estilo de Plasma `lliphi` (sigue el esquema) | **probado** | panel, lanzador, notificación y tooltip con los SVG propios; sigue el esquema y el acento |
| decoración Breeze coloreada | **probado** | barra de título con `[WM]` y `Colors:Header`; botones a la derecha |
| Konsole | probado parcialmente | el esquema se instala y se elige en el perfil; la paleta ANSI no se verificó sobre texto real |
| fondo `org.lliphi.horizonte` | **probado con salvedad** | `Image=org.lliphi.horizonte` por nombre no se resolvió («unknown wallpaper provider»); por **ruta del paquete** sí. El `defaults` y el layout pasan a usar la ruta (`~/.local/share/wallpapers/<Id>`) hasta entender la resolución por nombre |
| GTK generado por Plasma | no verificado | no se abrió una aplicación GTK en la sesión anidada |
| escalas 150 % y 200 % | no verificado | la sesión anidada corre a escala 1 |
| SDDM, splash, bloqueo | no verificado | fuera del primer lote; piden inicio de sesión real |

## 3. Defectos encontrados y corregidos durante la validación

1. `instalar.py` fallaba al escribir `sumas.json` cuando el `HOME` no tenía nada que respaldar (carpeta no creada). Corregido.
2. Reinstalar sobre una instalación idéntica sin manifiesto se tomaba por conflicto. Corregido: lo idéntico nunca es conflicto.
3. El fondo por nombre de paquete no carga (ver tabla). Corregido en los generadores: ruta del paquete.
4. **Incidente de método**: la primera orden `plasma-apply-lookandfeel --resetLayout` se ejecutó con el `HOME` de prueba
   pero con el DBus de la sesión del autor; no alteró su escritorio (comprobado con captura y `appletsrc`), pero pudo
   hacerlo. Regla desde entonces: toda orden `plasma-apply-*` se ejecuta con el `DBUS_SESSION_BUS_ADDRESS` de la
   sesión de prueba (se lee del entorno de su `plasmashell`), nunca con el del autor.

## 4. Límites que quedan

- Iconos de carpeta de Breeze en azul junto al acento rojo: coherente pero no ideal; un módulo de iconos (lote 3)
  podría recolorear solo las carpetas.
- La lámina de widgets (`herramientas/lamina.py`) no reproduce el foco del esquema fuera de Plasma; las capturas
  reales lo confirman en el escritorio.
- Validación con inicio de sesión real (usuario `prueba-tema`), escalas y aplicaciones GTK: pendiente para el autor
  o para una sesión posterior.

## 5. Lote 2 (2026-10-18): iconos de carpeta, editores y terminales

Mismo método con tres cambios, todos en el `HOME` aparte `/tmp/casa-lliphi-l2` y con el DBus de la sesión de prueba:

1. **Compositor externo virtual.** `kwin_wayland --virtual --xwayland --width 1600 --height 900
   --exit-with-session=startplasma-wayland` bajo `dbus-run-session`. Con `--exit-with-session`, `startplasma-wayland`
   arranca su propio `kwin_wayland_wrapper`: hay **dos KWin anidados** (el externo, dueño de `org.kde.KWin` en el bus de
   prueba, y el interno, que contiene la sesión de Plasma). Con el externo en ventana sobre la pantalla del autor, las
   capturas salían negras en cuanto esa ventana dejaba de verse; con `--virtual` no dependen de la pantalla del autor
   ni se le muestra nada.
2. **Captura.** Spectacle pide `CaptureScreen("<nombre de pantalla>")` a `org.kde.KWin.ScreenShot2` del bus, que es
   el externo; para que el nombre coincida hay que lanzarlo con el display del externo (`WAYLAND_DISPLAY=wayland-1
   spectacle -b -n -o …`) y poner antes la ventana del interno a pantalla completa (script de KWin por DBus sobre
   `org.kde.KWin`: `w.fullScreen = true`). Las aplicaciones se abren en el display interno (`wayland-2`) y se
   maximizan con un script cargado en el KWin interno por su nombre único de bus (`:1.N`, el de su PID).
3. **Pantalla despierta.** La sesión de prueba apaga su salida por inactividad (DPMS) y la captura sale negra o
   lavada; `kscreen-doctor --dpms on` sobre `wayland-2` antes de cada captura, y `powerdevilrc` sin acciones por
   inactividad en el `HOME` de prueba.

Instalación: `instalar.py --aplicar` con `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME` y `XDG_STATE_HOME` de prueba y una
carpeta `.positron/` vacía creada antes, de modo que el instalador cubrió también Positron (base condicional) y omitió
VSCodium, que no existe, diciéndolo. Variante oscura sembrada en `kdeglobals`/`plasmarc`; variante clara aplicada con
`plasma-apply-lookandfeel -a org.lliphi.claro` y `kwriteconfig6 --file kdeglobals --group Icons --key Theme lliphi`
más la señal `org.kde.KIconLoader.iconChanged`, todo con el DBus de la sesión de prueba.

### 5.1 Capturas (`../muestras/capturas/`)

| caso | oscuro | claro | qué se comprueba |
|---|---|---|---|
| Dolphin, vista de iconos a 32 px y lugares a 22 px | `oscuro-06-dolphin-iconos-carpeta.png` | `claro-06-dolphin-iconos-carpeta.png` | carpetas en el acento, distintivos de los lugares, lista de lugares, tema aplicado |
| Dolphin, iconos grandes (64 px escalable, dibujado a ~96 px) | `oscuro-07-dolphin-iconos-grandes.png` | `claro-07-dolphin-iconos-grandes.png` | alineación de los distintivos y nitidez del SVG escalable |
| Positron 2026.06.0 con la extensión instalada y `workbench.colorTheme` | `oscuro-08-positron.png` | `claro-08-positron.png` | interfaz (editor, barras, pestañas, terminal integrada) y sintaxis de Python |

Valores medidos en las capturas contra `tokens/tokens.json`: Dolphin oscuro, vista `#101012`, ventana y paneles
`#1b1c1e`, selección activa y cuerpo de la carpeta `#c93436`, solapa `#d46061`, distintivo `#faf4f4`; Dolphin claro,
vista `#fbfcfd`, ventana `#ecedef`, carpeta `#c53133`, solapa `#d15d5f`. Positron oscuro: editor, barra de actividad,
título y estado `#101012`, explorador y panel de sesión `#1b1c1e`, borde superior de la pestaña activa `#c93436`,
cadenas `#69c27e`, números `#d0a43a`; Positron claro: editor `#fbfcfd`, explorador `#ecedef`, borde de pestaña
`#c43032`, cadenas `#007835`, números `#7e5e00`, funciones `#345fb2`. Todo coincide con los semánticos y los ANSI.

### 5.2 Resultado por componente

| componente | estado | observación |
|---|---|---|
| iconos `lliphi` / `lliphi-oscuro` | **probado** | KIconLoader tiñe las carpetas con el acento (`FollowsColorScheme`) en las dos variantes; los distintivos (casa, documento, flecha, imagen, nota, reproducir, monitor, plantilla, compartir, red) se ven desde 22 px; a 64 px escalable el dibujo es nítido y alineado; lo que no es carpeta sigue siendo Breeze |
| extensión de VS Code en Positron | **probado** (Positron 2026.06.0) | `package.json` y los dos temas cargan; interfaz y sintaxis conformes a la tabla única; `tab.activeBorderTop` en rojo; terminal integrada con el fondo del esquema |
| VS Code, VSCodium | no probado | no están instalados en esta máquina; la extensión es la misma que carga Positron (base VS Code ≥ 1.80) |
| Zed | no probado | no está instalado; `lliphi.json` válido por estructura (esquema v0.2.0, dos temas, 145 claves de estilo) |
| Alacritty | no probado | no está instalado; los `.toml` cargan con `tomllib` y traen `colors.{primary,cursor,vi_mode_cursor,selection,search,hints,footer_bar,line_indicator,normal,bright}` |
| Kitty | no probado | no está instalado; los `.conf` traen 37 claves y la cabecera `## name:` para `kitten themes` |
| LibreOffice | no probado aquí | queda para el autor (`estado.md`) |
| escala 150 % | no verificado | la sesión anidada corre a escala 1; se cubrió con la vista de iconos grandes (64 px escalable a ~96 px) |

### 5.3 Defectos y observaciones

1. **Carpeta sobre la fila seleccionada** (`herramientas/destinos/iconos.py`). En el panel de lugares de Dolphin, con la
   fila activa y seleccionada, el cuerpo de la carpeta (`ColorScheme-Highlight`, `#c93436`) se funde con el fondo de la
   selección (el mismo acento): solo la solapa y el distintivo blanco la delatan (`oscuro-06`, fila «Home» en el primer
   intento; con la selección inactiva, `#551a1b` o `#e8c3c3`, se ve bien). KFilePlacesView no pide a KIconLoader el
   estado «seleccionado», que es el que invertiría los colores. Opciones, a decidir en el generador: un contorno de 1 px
   en `ColorScheme-HighlightedText` a baja opacidad alrededor del cuerpo, o dibujar el cuerpo con el acento suave y la
   solapa con el acento base. Breeze no lo sufre porque su carpeta es azul sobre selección azul más clara.
2. **Transición de tema**: tras `plasma-apply-lookandfeel -a org.lliphi.claro`, el dock tardó cerca de un minuto en
   recolorearse (una captura intermedia lo mostró en `#303538` con el panel ya en `#ecedef`); después, `#ecedef` como
   el panel. No es del lote 2; se anota por si se repite en una sesión real.
3. **Distintivos a 16 px**: no se dibujan (por diseño, desde 22 px); en la lista de lugares de Dolphin, a 22 px, son
   legibles pero pequeños. Sin acción.
4. **Método**: `pgrep -f`/`pkill -f` con el texto de una orden coinciden con la propia shell que la contiene; en la
   validación se mata por PID tras comprobar `HOME=/tmp/casa-lliphi-l2` en `/proc/<pid>/environ`, y el compositor
   externo solo con el patrón anclado `^kwin_wayland --virtual --xwayland --width 1600`. La sesión del autor no se
   tocó en ningún momento (su `kwin_wayland --socket wayland-0` siguió vivo; ninguna orden `plasma-apply-*` usó su bus).

## 6. Cristal (0.2.0): qué hizo falta para que la translucidez fuera real

Medido en la sesión del autor (Plasma 6.6.6, Wayland, efecto `blur` cargado, sin efecto `contrast`: en este KWin ya
no existe como efecto aparte) con el lanzador abierto sobre una ventana oscura, variante clara, píxel del fondo del
lanzador: opaco = `#eceef0` (236,237,239); translúcido = ≈ (213,214,216).

| intento | resultado | lección |
|---|---|---|
| `translucent/dialogs/background.svg` al 0.85 y normal al 0.97, con `opaque/` al 1.0 | 236: opaco | — |
| sin `opaque/` | 236: opaco | no era `opaque/` |
| normal y `translucent/` al 0.5 | 236: opaco | Plasma no usaba ninguno de los dos para el lanzador |
| **`solid/dialogs/background.svg` con el cristal** | **213: translúcido con desenfoque** | Kickoff (y el panel en modo opaco) piden la variante `solid`; si el tema no la trae, Plasma cae a la `solid/` de Breeze, opaca, teñida con el esquema. WhiteSur entrega una `solid/` translúcida: por eso se ve de cristal |
| sesión anidada (`kwin_wayland` en ventana) | el lanzador de Breeze también sale opaco | la anidada no sirve para validar translucidez; solo la sesión real |

Decisión: el estilo entrega el mismo cristal en `widgets/`, `translucent/` y `solid/`, y no entrega `opaque/`. QtSvg
renderiza la opacidad de los SVG generados igual que la de Breeze (alfa 216 para 0.85, medido con `QSvgRenderer`).
Límite: sin compositor con `blur`, el cristal se ve sin desenfoque (el contraste de `plasmarc` solo actúa con blur).

## 6. Decoración Aurorae (2026-10-18)

Mismo método del §5 (`kwin_wayland --virtual --xwayland --width 1600 --height 900 --exit-with-session=startplasma-wayland`
bajo `dbus-run-session`, `HOME` aparte en `/tmp/casa-lliphi-aur`, todo `plasma-apply-*`, `kwriteconfig6` y `qdbus6` con el
DBus de esa sesión; cierre por PID tras comprobar `HOME=` en `/proc/<pid>/environ` y, para el KWin externo, por ser hijo
del `dbus-run-session` propio). Dolphin y Kate abiertas en el display interno, colocadas con un script de KWin cargado en
el KWin interno por su nombre único de bus (`:1.N`, el de su PID), y capturadas desde el externo con Spectacle.

| caso | oscuro | claro | qué se comprueba |
|---|---|---|---|
| Dolphin (activa) sobre Kate (inactiva), decoración `__aurorae__svg__lliphi` / `-claro` | `oscuro-09-decoracion.png` | `claro-09-decoracion.png` | marco con esquinas redondeadas y sombra de WhiteSur, barra de 30 px con el título centrado, botones circulares de Nothing a la derecha (`IAX`): gris, gris y cerrar en el acento; en la inactiva, al 50 % |

Resultado: **probado** en las dos variantes (Plasma 6.6.6, motor V2). La decoración es la derivada (decisión 3.15):
`fuentes/aurorae/base/` recoloreado por `herramientas/destinos/aurorae.py`.

### 6.1 Lo aprendido del motor V2 (`aurorae` 6.6.6, `v2/decoration.cpp`, `decorationbutton.cpp`, `decorationtheme.cpp`)

1. **Dos plugins.** Desde 6.6 el paquete trae `org.kde.kwin.aurorae.so` (V1, solo decoraciones QML como Plastik) y
   `org.kde.kwin.aurorae.v2.so` (motor SVG). Los temas SVG se registran como `__aurorae__svg__<carpeta>` y el KCM escribe
   `library=org.kde.kwin.aurorae.v2` (así quedó el `kwinrc` del autor con WhiteSur-dark); con `library=org.kde.kwin.aurorae`
   el tema SVG no se encuentra. Los `defaults` de los temas globales y el instalador usan `.v2`.
2. **`metadata.desktop` manda.** El proveedor de temas (`decorationthemeprovider.cpp`) lista solo carpetas de
   `aurorae/themes/` con `metadata.desktop`; `metadata.json` se añade para KPackage, pero no sustituye al `.desktop`.
3. **`reconfigure` no relee los SVG de un tema ya cargado** (KSvg conserva los renderizadores y la caché de píxeles por
   ruta). Para ver un cambio hay que cambiar a otro tema y volver (`theme=…-claro` → `reconfigure` → `theme=…` →
   `reconfigure`) o usar otra carpeta. En la validación cada experimento usó un nombre de tema nuevo.
4. **Estados de los botones.** `select()` elige, para la ventana activa, `pressed` → `hover` → `deactivated` → `active`; para
   la inactiva, `pressed-inactive`/`pressed` → `hover-inactive`/`hover` → `deactivated-inactive`/`deactivated` → `inactive` →
   `active`. `Hovered` incluye el «hover de grupo» (`ButtonGroupHover` en `[General]`, nuevo en 6.6: al pasar sobre un
   botón se iluminan todos). Comprobado con botones de diagnóstico de colores planos en catorce variantes.
5. **Un grupo cuyo único hijo es un trazo sin relleno (`fill="none"`, solo `stroke`) no se renderiza como tal**: KSvg/QtSvg
   devolvió para él el dibujo de otro estado (la primera versión dibujada, con anillos de solo trazo en `inactive-center`,
   mostraba el aspecto de `hover` en las ventanas inactivas; con un `<rect>` invisible de 14 × 14 dentro del grupo, con el
   círculo relleno o con un radio menor desaparecía). Los botones de Nothing son formas rellenas y no lo sufren.
6. **Sombra.** V2 pinta el FrameSvg entero (incluido el relleno `Padding*`) en una imagen, recorta el rectángulo interior
   y la entrega a KWin como `DecorationShadow` con `innerShadowRect`; la decoración visible se pinta aparte desplazada
   `-Padding`. Las piezas `hint-*-margin` solo sirven al borde interior (`innerborder`). El tamaño del borde del usuario
   (`BorderSize`) acota `BorderLeft/Right/Bottom` (`Normal` → entre 4 y 6 px; `None`/`NoSides` → 0).
7. **Escala.** Todas las medidas del rc se multiplican por `dpi/96` de la pantalla primaria; los botones, además, por
   `ButtonSize` de `auroraerc` (`1 + (n-1)·0,2`).
8. **Desenfoque.** Si el SVG trae `mask-*` (WhiteSur lo trae), V2 pide a KWin desenfoque tras la decoración; con el marco
   opaco de Lliphi no se ve nada. No se afirma nada sobre decoraciones translúcidas: no se probaron.
9. **`plasma-apply-lookandfeel -a`** aplicó esquema, estilo e iconos de los `defaults` pero no escribió
   `[kwinrc][org.kde.kdecoration2]` en la sesión anidada; el instalador escribe esas claves con `kwriteconfig6` y llama a
   `org.kde.KWin.reconfigure` cuando aplica el tema con el módulo `decoracion` instalado.

## 7. 0.2.0 derivado de lo existente (2026-10-18, tarde)

Tras el rechazo del autor a lo dibujado desde cero, 0.2.0 se construye de bases existentes (docs/decisiones.md §4):

| pieza | base | comprobado |
|---|---|---|
| estilo de Plasma `lliphi-oscuro` / `lliphi-claro` | WhiteSur-kde (desktoptheme), recoloreado, sin `colors` | sesión anidada: panel, dock flotante, lanzador, notificación (`oscuro-15`, `oscuro-16`); sesión del autor: cristal con desenfoque (§6) |
| Kvantum `LliphiOscuro` / `LliphiClaro` | WhiteSur-kde (Kvantum), colores del kvconfig y hex del svg desde los tokens | sesión del autor: Dolphin con ventana translúcida y controles de WhiteSur |
| decoración `lliphi` / `lliphi-claro` | Nothing (Aurorae), recoloreada, sin sombra de texto, título 18 px | sesión anidada: Dolphin con los botones circulares de Nothing a la derecha y cerrar en acento (`oscuro-15`) |
| iconos | Papirus-Dark / Papirus-Light con carpetas en rojo (`dependencias.py`) | sesión del autor: carpetas rojas en Dolphin |
| cursores | Bibata Modern Classic / Ice | aplicado en la sesión del autor |
| tipografía | Hack 10 (interfaz, terminal, títulos en negrita) | sesión del autor y anidada |

Límites: la anidada no muestra el desenfoque (§6); la variante clara de 0.2.0 solo se ha visto en el lanzador de cristal
de la sesión real (`claro-14`), no en Dolphin ni en la decoración. Hoja comparativa: `muestras/comparacion-0.1-0.2.png`.
