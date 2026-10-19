# Registro de cambios

Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

### Changed
- Mejora 1 sobre la línea base (decisiones 4.5): `LliphiOscuro.colors` y `LliphiClaro.colors` son WhiteSurDark y
  WhiteSur con solo el acento tomado de los tokens (foco, hover, enlace, texto activo y el grupo de selección en rojo);
  cada otro valor se copia byte a byte, lo verifica `test_esquema_linea_base_solo_acento`. Captura de comparación en
  `muestras/comparacion-linea-base-acento.png`; aprobada por el autor.
- Mejora 2 (decisiones 4.6): variante clara equivalente (`org.lliphi.claro` = WhiteSur claro + `LliphiClaro` con el
  acento rojo + `lliphi-claro` + Kvantum `LliphiClaro`) comprobada en sesión anidada; el Kvantum claro no recoloreaba el
  foco ni los deslizadores porque el acento de `WhiteSur.svg` es `#0860f2` (y `#0e4bb4`, `#0852ce`, `#1352c4`, `#77aff1`),
  no `#315bef`: ahora se mapean a los tokens. Capturas `claro-10`, `claro-11` y `muestras/comparacion-linea-base-clara.png`.
- Mejora 3 (decisiones 4.7): los iconos de la línea base pasan de Breeze a **Papirus con las carpetas en rojo**
  (`Papirus-Dark` oscuro, `Papirus` claro; heredan de Breeze): `dependencias.py` los instala por defecto (Bibata sigue en
  `--opcionales`), el tema global los declara en `defaults` y el instalador los aplica con `plasma-changeicons` (si no
  están, Breeze). Captura `oscuro-21` y `muestras/comparacion-linea-base-iconos.png`; aprobada por el autor. Con las tres
  mejoras aprobadas, la línea base queda cerrada (`docs/linea-base.md` §2).
- Línea base fijada por el autor (`docs/linea-base.md`, decisiones 4.4): el tema global reproduce su configuración
  activa, WhiteSur-dark tal cual (esquema `WhiteSurDark` y estilo de Plasma con su `colors`, sin recolorear),
  decoración Nothing, Kvantum Lliphi, iconos `breeze-dark`, cursores WhiteSur-cursors; la única novedad es la
  tipografía: Inter (interfaz) y Hack (monoespaciada). El esquema rojo de los tokens queda como `Lliphi*-tokens.colors`.
- `dependencias.py` instala WhiteSur-cursors por defecto; Papirus y Bibata pasan a `--opcionales`.

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
