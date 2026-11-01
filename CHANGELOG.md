# Registro de cambios

Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

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

### Added
- LibreOffice: una **paleta** `.soc` por variante (como la de Dracula para LibreOffice) con los neutros, el acento, los
  estados y los dieciséis ANSI, para los selectores de color de los documentos; va suelta y dentro de `lliphi.oxt`
  (carpeta `palette/` registrada en las rutas de paletas con `paletas.xcu`). Prueba `test_libreoffice_paletas`.
  Validado en LibreOffice 26.2.6 (decisión 5.2).
- Complemento `obsidian` (decisión 5.1): `generado/obsidian/theme.css`, un tema de Obsidian 1.x con las dos variantes
  que solo redefine variables de la aplicación (neutros, acento, los ocho colores con nombre desde los ANSI, estados,
  Inter y JetBrains Mono, radios, la sintaxis de los editores y las llamadas de Zotero); se publica con su versión en
  `achalmed/obsidian-lliphi`. Prueba `test_obsidian_tema` (34 en total).
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
