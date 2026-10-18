
Formato de Keep a Changelog 1.1.0; versiones según SemVer 2.0.0. La versión del proyecto vive en `VERSION`.

## [Unreleased]

### Added
- Módulo `terminales`: esquemas para Alacritty (`[colors]` en TOML) y Kitty (`.conf`) en claro y oscuro, con los
  dieciséis ANSI de Konsole y la selección, el cursor y los enlaces del esquema de Plasma; el instalador admite
  destinos en `$XDG_CONFIG_HOME` (`alacritty/themes/`, `kitty/themes/`).

## [0.1.0] - 2026-10-18

### Added
- Tokens de diseño (DTCG 2025.10, color en OKLCH) con contraste medido; variantes clara y oscura y acento rojo.
- Generadores: esquemas de color de Plasma, temas globales, estilo de Plasma que sigue el esquema del sistema,
  esquemas de Konsole y paquete de fondos con variante oscura.
- Instalador en Python con simulación por defecto, respaldo verificado, manifiesto y `UNDO.sh`.
- Pruebas: tokens, contraste, deriva de lo generado, estructura de paquetes, instalación reversible y REUSE.
- Sitio oficial (Quarto) con galería de capturas reales, catálogo generado de `modulos/`, guías e integración
  propuesta con el hub del autor; integración continua; empaquetado por módulo con `SHA256SUMS`.
