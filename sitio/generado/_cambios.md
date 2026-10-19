
Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

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
