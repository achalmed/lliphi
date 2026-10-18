# Registro de cambios

Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

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

## [0.1.0] - 2026-10-18

### Added
- Tokens de diseño (DTCG 2025.10, color en OKLCH) con contraste medido; variantes clara y oscura y acento rojo.
- Generadores: esquemas de color de Plasma, temas globales, estilo de Plasma que sigue el esquema del sistema,
  esquemas de Konsole y paquete de fondos con variante oscura.
- Instalador en Python con simulación por defecto, respaldo verificado, manifiesto y `UNDO.sh`.
- Pruebas: tokens, contraste, deriva de lo generado, estructura de paquetes, instalación reversible y REUSE.
- Sitio oficial (Quarto) con galería de capturas reales, catálogo generado de `modulos/`, guías e integración
  propuesta con el hub del autor; integración continua; empaquetado por módulo con `SHA256SUMS`.
