
Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

### Fixed
- **La extensión de VS Code, Positron y VSCodium se instala con `--install-extension`** (decisiones 5.9): `editores`
  genera `lliphi.vsix` y el instalador la registra con la orden de cada editor del PATH (y la retira el `UNDO.sh`), en
  lugar de copiar la carpeta, que Positron daba por desinstalada y no mostraba los temas. Nuevos ganchos del instalador
  para los `aplicar.py`: `tras_instalar()` y `al_desinstalar()`.

### Added
- **Kate, TeXstudio y Vim/Neovim** (decisiones 5.5–5.8): tres complementos nuevos. `kate`: Lliphi Claro y Lliphi Oscuro
  como temas de KSyntaxHighlighting, con el fondo y la selección de la paleta de Kvantum, para que Kate (y KWrite y
  KDevelop) cambie solo de tema al cambiar de variante. `texstudio`: los 88 formatos de resaltado en `[formats]` (claro)
  y `[formatsDark]` (oscuro), que TeXstudio elige por la paleta, como perfil `lliphi.txsprofile` y con un `aplicar.py`
  que solo sustituye esas secciones de `texstudio.ini`. `vim`: el esquema `lliphi` para Vim y Neovim, con las dos
  variantes según `background`, el fondo y la terminal de Konsole y, en Neovim, Tree-sitter, LSP y diagnósticos. Los
  tres usan la tabla de sintaxis de los editores.
- **Positron entero** (decisiones 5.4): las 37 claves `positron*` que llevaban un color fijo de Positron (cuadrícula de
  datos, barras de acciones, diálogos, estado del intérprete, gráficos del explorador de datos, bienvenida) toman su
  color de los tokens; la consola, el fondo y los ANSI de la terminal integrada.

### Changed
- **Arquitectura modular** (docs/arquitectura.md, docs/migracion-modular.md): un tema global integrador (`global/`), seis
  módulos (`modulos/`: `esquema`, `estilo`, `decoracion`, `iconos-cursores`, `carga-bloqueo`, `disposicion`) y los
  complementos fuera del tema global (`complementos/`: `fondos`, `kvantum`, `konsole`, `terminales`, `editores`,
  `libreoffice`, `sddm`). Cada uno se describe en su `modulo.json` y tiene su `README.md`; el núcleo
  (`herramientas/nucleo/`) los descubre, así que desaparecen las tres tablas de módulos de `generar.py` e `instalar.py`.
- El tema global compone `contents/defaults` con lo que aporta cada módulo e integra la pantalla de carga, la de salida
  y la disposición, que KDE solo lee de dentro del paquete; ya no escribe identificadores ajenos.
- `generado/` se ordena por módulo (`generado/<id>/`, lo mismo que va en su tarball). Lo que se instala no cambia: los
  181 archivos instalados son idénticos a los de 0.3.0.
- La paleta pasa a `modulos/esquema/paleta.py`; las dependencias de terceros, a los `externas.py` de `global` (tipografía) e
  `iconos-cursores` (iconos y cursores); el inicio de sesión, a `complementos/sddm/`.

- **Iconos Colloid Grey** (decisiones 4.22): `Colloid-Grey-Light` en el claro y `Colloid-Grey-Dark` en el oscuro, con
  Papirus como reserva; el lanzador lleva el logotipo de Plasma (`plasma-symbolic`) en lugar del de Apple que Colloid
  pone en `start-here`.
- **Sin azules de WhiteSur en el oscuro y mejoras también en el claro** (decisiones 4.21): los botones pulsados, por
  omisión y activados de Kvantum (y pestañas, grupos e iconos) toman el acento de la variante; en el claro, la barra de
  herramientas en el color del título y el dock sin sombra y más opaco.
- **Menú abierto en el acento** (decisiones 4.20): en el oscuro, el elemento abierto de la barra de menús toma el rojo
  del elemento elegido dentro del menú, como ya pasaba en el claro.
- **Kvantum, un solo tema `Lliphi`** con el claro y el oscuro (`LliphiDark`) en su carpeta (decisiones 4.19): cambiar
  de variante desde Preferencias del sistema cambia también Kvantum; antes quedaba el Kvantum de la variante anterior.
- **Título y barra de herramientas en una sola banda** (mejora 12, decisiones 4.18): en el oscuro, Kvantum pinta la
  barra de herramientas (y con ella la de menús) opaca en el gris de la ventana, el mismo que el título de la
  decoración; el resto de la ventana sigue translúcido (`complementos/kvantum/ajustes.json`); el claro no cambia.
- **Dock de Lliphi** (mejora 11, decisiones 4.17): fondo de paneles del oscuro más opaco (88 %, gris de la ventana) y
  sin la sombra que manchaba las puntas; mosaicos de tareas propios (fondito claro tras cada aplicación, la activa
  teñida del acento con su barra) y paginador de números
  con un trazo encima (acento en el activo), desde `modulos/estilo/ajustes.json`; el dock suma el paginador.
  `sesion.py arrancar --escritorios N` y un reintento si el shell recién arrancado aún escribía su configuración.

### Added
- **Sitios web: DuckDuckGo y GitHub** (decisiones 5.12): complemento `sitios-web` con un estilo de usuario por sitio
  (`duckduckgo.user.css`, `github.user.css`; UserCSS para Stylus en Zen y Chrome, o `userContent.css` en Zen) que
  redefine solo las variables del sitio (Primer en GitHub; `--theme-col-*`, `--sds-color-*` y `--ds-*` en DuckDuckGo)
  con Lliphi Claro y Lliphi Oscuro según el modo; el código de GitHub con la sintaxis de los editores y los diffs con
  los estados. Para DuckDuckGo sin extensión, sus ajustes de apariencia por variante (`duckduckgo/ajustes.json`) y unos
  marcadores importables (`duckduckgo/marcadores.html`).
- **GTK 3, GTK 4 y libadwaita** (complemento `gtk`, decisiones 4.37): las aplicaciones GTK con los neutros y el acento de
  los tokens, los mismos que Kvantum da a Qt, sobre el Breeze y los colores de `kde-gtk-config` (antes, los grises de
  WhiteSur del esquema y el naranja de Yaru en libadwaita); GTK 4 cambia solo de variante con `prefers-color-scheme`, y
  GTK 3 lo cambia `fondo-variante`, que también pone `color-scheme` en GSettings.
- **Xournal++** (complemento `xournalpp`, decisiones 5.20): paleta de bolígrafos `Lliphi.gpl` (trece colores legibles
  sobre papel) y los colores de alrededor de las páginas, de la selección y del recoloreado del modo oscuro.
- **GIMP** (complemento `gimp`, decisiones 5.21): tema «Lliphi» con sus variantes clara y oscura, derivado del Default de
  GIMP 3.2 (GPL-3.0-or-later, `fuentes/base/GIMP-Default/`), que sigue al escritorio con el esquema «Sistema»; y las
  paletas `Lliphi Claro.gpl` y `Lliphi Oscuro.gpl`.
- **Calibre** (complemento `calibre`, decisiones 5.22): paletas «Lliphi Claro» y «Lliphi Oscuro» para su propio estilo
  (siguen al escritorio en vivo) y dos esquemas del visor; el esquema «Sistema» del visor ya sigue a Lliphi. Solo
  preferencias de la interfaz, con respaldo; la biblioteca no se toca.
- **RStudio, GNU Octave y Spyder** (decisiones 5.40–5.43), tres complementos nuevos: temas `.rstheme` de RStudio (editor,
  interfaz, consola de R y terminal con los ANSI de Konsole); los colores de Octave en sus dos modos (claro en el primero,
  oscuro en el segundo) fusionados en `octave-gui.ini`; esquemas de Spyder con interfaz automática y los dieciséis ANSI
  en la consola IPython. La vigilancia de `fondo-variante` ejecuta los programas de `variante.d/`, con los que los tres
  siguen a la variante al abrirse de nuevo.
- **RStudio: la ventana entera en Lliphi** (decisiones 5.44): el `.rstheme` pinta también las barras, las pestañas
  (la elegida con la raya del acento) y los divisores, que quedaban con los grises de «Modern» o «Sky» o con el gris
  azulado de RStudio en oscuro. El menú «RStudio theme» no admite temas propios: basta con elegir Lliphi en «Editor theme».
- **Telegram Desktop** (decisiones 5.30): complemento `telegram`, con `Lliphi Claro.tdesktop-theme` y
  `Lliphi Oscuro.tdesktop-theme`. Tienen las 586 claves de color de Telegram 7.3.3 (paleta de lib_ui en
  `fuentes/base/telegram-palette/`, GPL-3.0-or-later), todas desde los tokens: el acento en la selección, los botones y
  los mensajes propios (un tinte del acento), los estados en enlaces, errores y «en línea», y un fondo de chat liso.
  Telegram alterna solo entre los dos con su modo nocturno automático en «Sistema» (`complementos/telegram/INSTALL.md`).
- **Ningún azul fijo en el estilo de Plasma** (decisiones 4.36): la barra del volumen y del brillo, el botón pulsado, el
  calendario y otros controles siguen el acento (rojo en el oscuro); antes, WhiteSur dejaba el azul escrito.
- **Iconos de la bandeja del mismo tamaño** (decisiones 4.35): superpuestos `Colloid-Grey-Light-Lliphi` y
  `Colloid-Grey-Dark-Lliphi` con los iconos simbólicos de Colloid a 22 px con el margen de sus iconos de 22.
- **Etiquetas emergentes legibles en el claro** (decisiones 4.34): Kvantum claro las dibuja claras y ahora con texto
  oscuro; antes el texto era casi blanco (afectaba a toda aplicación Qt y a los botones de la ventana).
- **Decoración clara: cerrar en azul, minimizar y maximizar visibles, y un botón de menú de aplicación propio**
  (decisiones 4.33), también en el oscuro; las etiquetas emergentes del estilo claro vuelven a leerse.
- **Lliphi Claro con panel claro** (decisiones 4.32): el estilo de Plasma del claro pasa de WhiteSur (panel, dock y menús
  en gris oscuro) a WhiteSur-alt (los mismos dibujos, claros); el dock del claro toma su propio gris de ventana.
- **Kvantum oscuro: deslizador y barra de progreso inactivos con el rojo entero** (decisiones 4.31), como el claro con el
  azul; WhiteSur los dejaba a media opacidad.
- **Alacritty, Kitty y la terminal integrada de los editores, con la paleta de Konsole** (decisiones 4.30): las mismas
  dieciséis ANSI de Nothing (rojo en el oscuro, azul en el claro) que Konsole; la sintaxis de los editores no cambia.
- **Konsole sobre el esquema de Nothing y siguiendo a la variante** (decisiones 4.28 y 4.29): Lliphi Oscuro es el
  esquema «Nothing» (jomada, GPL-3.0-or-later) con su rojo en carpetas, claves y logotipos; Lliphi Claro es su espejo
  en azul, con cada color ≥ 4,5:1 sobre el fondo claro. La vigilancia de `fondo-variante` cambia el esquema del perfil
  y de las ventanas abiertas al pasar entre Lliphi Claro y Lliphi Oscuro; un perfil con un esquema ajeno no se toca.
- **Fondo predeterminado: «Lliphi Relámpago · @achalmaedison»** (decisiones 4.27), azul en el claro y rojo en el
  oscuro, en el instalador, la disposición del tema global y el estilo de Plasma; la disposición pone la imagen de su
  variante. Horizonte sigue en el bloqueo y el inicio de sesión.
- **El fondo sigue a la variante** (`complementos/fondo-variante/`, decisiones 4.26): al cambiar entre Lliphi Claro y
  Lliphi Oscuro con el tema global o con el esquema de color, cada escritorio con un fondo de Lliphi pasa a la imagen
  de la variante del mismo fondo; arranca con la sesión y no toca un fondo ni un esquema ajenos.
- **Fondos firmados** «Lliphi Forma · @achalmaedison» y «Lliphi Relámpago · @achalmaedison» (decisiones 4.25): la
  firma del autor pequeña y tenue en la matriz de puntos; se conservan los sin firma.
- **Fondo «Lliphi Relámpago»** (`org.lliphi.relampago`, decisiones 4.24): el relámpago en semitono de puntos, el nombre
  en matriz de puntos y la paleta; azul en el claro y rojo en el oscuro.
- **Fondo «Lliphi Forma»** (`org.lliphi.forma`, decisiones 4.23), claro y oscuro: cuadrados de vidrio esmerilado, un
  semicírculo en el rojo de Lliphi y una píldora con matriz de puntos, en 1080p, 1440p y 4K.
- **Lliphi Studio** (`studio/`): la ventana opcional de la familia de studios (PySide6 sobre `gui-comun` 1.4.0, acento
  carmesí) con nueve secciones: Dashboard, Color (editor de la paleta con contraste y daltonismo), Plasma (marcos de
  nueve piezas comparados con WhiteSur), Ventanas (Aurorae), Iconos y cursores (Xcursor animado, organizador),
  Pantallas (la carga de verdad en su QML), Disposición, Vista en vivo y Construir y desplegar. Escribe solo los
  `ajustes.json` de los módulos; 16 pruebas propias sobre una copia del proyecto.
- **Sesión de prueba** (`herramientas/sesion.py`): la receta de `docs/validacion.md` §8–§9 como orden: Plasma anidado
  con su propio HOME en la caché, sin systemd ni bloqueo, con `arrancar`, `estado`, `recargar`, `ejecutar`, `guion`,
  `capturar` y `cerrar`; se niega a correr nada fuera del HOME de prueba.
- **Ajustes declarativos** (`ajustes.json`) en `esquema` (la paleta OKLCH), `decoracion` (rc, título, botones),
  `disposicion` (paneles y widgets) e `iconos-cursores` (temas y color del superpuesto), sin cambio en lo generado salvo
  el script de disposición, que ahora recorre los paneles. `paleta.py --ajustes --json`, `generar.py verificar|validar
  --json` e `instalar.py estado --json`.
- LibreOffice: una **paleta** `.soc` por variante (como la de Dracula para LibreOffice) con los neutros, el acento, los
  estados y los dieciséis ANSI, para los selectores de color de los documentos; va suelta y dentro de `lliphi.oxt`
  (carpeta `palette/` registrada en las rutas de paletas con `paletas.xcu`). Prueba `test_libreoffice_paletas`.
  Validado en LibreOffice 26.2.6 (decisión 5.2).
- Complemento `obsidian` (decisión 5.1): `generado/obsidian/theme.css`, un tema de Obsidian 1.x con las dos variantes
  que solo redefine variables de la aplicación (neutros, acento, los ocho colores con nombre desde los ANSI, estados,
  Inter y JetBrains Mono, radios, la sintaxis de los editores y las llamadas de Zotero); se publica con su versión en
  `achalmed/obsidian-lliphi`. Prueba `test_obsidian_tema` (34 en total).
- Complemento `navegadores` (decisión 5.3): Lliphi en **Zen Browser**, un `userChrome.css` que redefine las variables
  de Zen y de Firefox y cambia solo entre Lliphi Claro y Lliphi Oscuro con el modo del sistema, más un `user.js` que lo
  carga y pone Zen en modo automático; y en **Google Chrome**, dos temas sin empaquetar (uno por variante) que se cargan
  desde `~/.local/share/lliphi/chrome/`. Base de instalación `zen` (el perfil que abre Zen, también el del Flatpak).
  Pruebas `test_navegadores_zen`, `test_navegadores_chrome` y `test_instalar_navegadores`.
- `generar.py validar`: manifiestos, dependencias sin ciclos y declaradas, estructura real de cada formato de KDE y que
  cada identificador que declara el tema global exista en el módulo que lo entrega; `generar.py lista`.
- `instalar.py comprobar` (lo instalado está completo, es de esta versión y `kpackagetool6` lo reconoce),
  `instalar.py dependencias` e `instalar.py sddm`; `dependencias.py` e `instalar_sddm.py` quedan como atajos.
- Nueve pruebas de la arquitectura (33 en total) y el paso `validar` en la integración continua.

### Fixed
- LibreOffice: el sombreado de campos e índices de Writer pasa al tono del separador; en el oscuro, el anterior
  (`fondo.ventana-alterno` sobre `fondo.vista`) no se distinguía de la página.
- Disposición del escritorio: el fondo de cada escritorio apuntaba a la carpeta de datos y no a la de fondos
  (`userDataPath("wallpapers")` → `userDataPath("data", "wallpapers")`) y el escritorio quedaba negro al aplicar la
  disposición desde Preferencias; el dock pedía `windowscover`, que Plasma 6 ya no tiene, y no se ocultaba: ahora
  `dodgewindows`, se aparta cuando una ventana llega a él.
- Kvantum se instalaba en `$XDG_DATA_HOME/../../.config/Kvantum`, que falla si las rutas XDG no son las de omisión;
  ahora va a `$XDG_CONFIG_HOME/Kvantum`, y un manifiesto de 0.3.0 con la ruta antigua se sigue reconociendo.
- El instalador respalda las notas del widget de Plasma (`~/.local/share/plasma_notes`) y `UNDO.sh` las devuelve: si un
  cambio de disposición quita el widget, Plasma borra su nota.

## [0.3.0] - 2026-10-19

Lliphi parte ahora de la configuración que el autor eligió en su escritorio (WhiteSur-dark, decoración de Nothing,
Kvantum, cursores WhiteSur) y la mejora en diez pasos, cada uno con captura y su visto bueno (`docs/linea-base.md`).
Regla de color: **rojo de Nothing (#c93436) en el oscuro y azul de WhiteSur (#315bef) en el claro**.

### Added
- Pantallas de carga y de salida derivadas de WhiteSur-dark, con el fondo de Lliphi y el nombre en Inter en lugar del
  logotipo de Apple; antes el tema declaraba una pantalla de carga que no traía (mejora 6).
- Inicio de sesión SDDM derivado de WhiteSur-dark: fondo de Lliphi, Inter y foco en el acento.
  `herramientas/instalar_sddm.py` lo instala con pkexec y deja `UNDO.sh` (mejora 7).
- Tema de iconos superpuesto `Papirus-Dark-Lliphi` (carpetas rojas para el oscuro); Papirus queda como se publica, con
  sus carpetas azules para el claro (mejoras 3 y 10).
- `dependencias.py` instala WhiteSur-cursors, Papirus y JetBrains Mono Nerd Font en el usuario, sin root.
- Bloqueo de pantalla con el fondo oscuro de Lliphi en las dos variantes (mejora 10).

### Changed
- Esquemas y estilo de Plasma: los de WhiteSur con solo el acento sustituido por el de cada variante; todo lo demás se
  copia byte a byte (mejoras 1, 2 y 8). El estilo de Plasma ya no deja interruptores ni deslizadores en azul en el oscuro.
- Decoración: la de Nothing, con el anillo de minimizar en gris, el título en los grises de Lliphi sin sombra y el
  botón de cerrar siempre rojo (mejora 4).
- Konsole: con `--aplicar-tema`, el perfil por defecto toma el esquema y la monoespaciada de Lliphi, con respaldo; un
  perfil enlazado desde dotfiles sigue enlazado (mejoras 5 y 9).
- Tipografía: Inter en la interfaz e Inter Medium en los títulos; JetBrains Mono Nerd Font como única monoespaciada,
  en lugar de Hack e IBM Plex (mejora 9).
- Los esquemas generados por entero desde los tokens se conservan como `Lliphi*-tokens.colors`.

### Fixed
- Los títulos de ventana no tomaban la fuente nueva hasta reiniciar la sesión: el instalador ahora emite `refreshFonts`.
- Variante clara: fondo oscuro en lugar del claro, carpetas rojas en lugar de azules y reloj ilegible en el bloqueo
  (mejora 10, validada en una sesión de Plasma aparte).

## [0.2.0] - 2026-10-18

### Changed
- Cambio de enfoque: el estilo de Plasma y el tema Kvantum derivan de WhiteSur-kde (GPL-3.0) recoloreados con los
  tokens y sin lo que imita a Apple; iconos Papirus (carpetas rojas), cursores Bibata y tipografía IBM Plex como
  dependencias descargadas; retirado el módulo de iconos propio.

### Added
- Módulo `terminales`: esquemas para Alacritty (`[colors]` en TOML) y Kitty (`.conf`) en claro y oscuro, con los
  dieciséis ANSI de Konsole y la selección, el cursor y los enlaces del esquema de Plasma; el instalador admite
  destinos en `$XDG_CONFIG_HOME` (`alacritty/themes/`, `kitty/themes/`).
- Módulo `editores`: extensión mínima de VS Code (dos temas con `colors`, `tokenColors` y `semanticTokenColors`) y
  tema de Zed (v0.2.0, dos variantes en un archivo); la sintaxis sale de los ANSI con una tabla única (palabras
  clave rojo, cadenas verde, números amarillo, funciones azul, comentarios en el texto inactivo). El instalador
  copia la extensión a `~/.vscode/extensions/` (o `$VSCODE_EXTENSIONS`), su única ruta de lectura.
- Módulo `editores`: la misma extensión se instala en Positron (`~/.positron/extensions/` o `$POSITRON_EXTENSIONS`) y
  en VSCodium (`~/.vscode-oss/extensions/` o `$VSCODIUM_EXTENSIONS`) cuando existe la carpeta del editor; si no, el
  instalador omite el par y lo dice en la simulación, sin crearla.
- Módulo `iconos`: dos temas de iconos (`lliphi` hereda de Breeze, `lliphi-oscuro` de Breeze Dark) que entregan solo
  las carpetas, dibujadas aquí en el acento con `ColorScheme-Highlight` y distintivos para los lugares de uso común,
  en 16, 22, 32, 48 y 64 px (este último escalable hasta 512); `FollowsColorScheme` las tiñe con el acento del usuario.
- Módulo `libreoffice`: dos esquemas de «Colores de la aplicación» (Lliphi Claro y Lliphi Oscuro) con las 91 entradas
  del esquema de LibreOffice 26.2 (documento, Writer, Calc, Draw, HTML, autores, BASIC, SQL e interfaz), generados
  desde los semánticos y los ANSI con la tabla de sintaxis de los editores; como extensión `.oxt` reproducible
  (`unopkg add`) y como fragmentos `<oor:items>` para `registrymodifications.xcu`. El instalador no toca LibreOffice.
- Módulo `decoracion`: decoración de ventanas Aurorae en dos temas (`lliphi` oscuro y `lliphi-claro`) derivada de
  WhiteSur-dark (marco, radios, sombra, disposición) y Nothing (botones circulares con glifo al pasar el ratón), ambos
  GPL-3.0-or-later y copiados sin cambios a `fuentes/aurorae/base/` (`ORIGEN.md`); el generador reescribe solo los colores
  con los tokens (cerrar en el acento, el resto en gris, sin semáforo), la barra de 30 px y los botones a la derecha.
  `generado/aurorae/` es GPL-3.0-or-later (`REUSE.toml`); los temas globales pasan a `library=org.kde.kwin.aurorae.v2`,
  `theme=__aurorae__svg__<id>` y botones `IAX` a la derecha; el instalador escribe esas claves en `kwinrc` al aplicar.

## [0.1.0] - 2026-10-18

### Added
- Tokens de diseño (DTCG 2025.10, color en OKLCH) con contraste medido; variantes clara y oscura y acento rojo.
- Generadores: esquemas de color de Plasma, temas globales, estilo de Plasma que sigue el esquema del sistema,
  esquemas de Konsole y paquete de fondos con variante oscura.
- Instalador en Python con simulación por defecto, respaldo verificado, manifiesto y `UNDO.sh`.
- Pruebas: tokens, contraste, deriva de lo generado, estructura de paquetes, instalación reversible y REUSE.
- Sitio oficial (Quarto) con galería de capturas reales, catálogo generado de `modulos/`, guías e integración
  propuesta con el hub del autor; integración continua; empaquetado por módulo con `SHA256SUMS`.
