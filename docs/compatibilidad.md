---
tipo: doc
estado: activo
titulo: 'Matriz de compatibilidad por distribución y versión de Plasma'
---
# Compatibilidad

Lo común a todo Plasma 6 se separa de lo que depende de una versión. «Probado» significa comprobado en un
escritorio real con capturas en `../muestras/`; «esperado» es lo que la documentación de KDE indica y no se ha
probado aquí. Se actualiza en cada fase de validación.

## 1. Por componente y versión de Plasma

| componente | Plasma 6.0–6.1 | 6.2–6.5 | **6.6 (probado aquí)** | depende de |
|---|---|---|---|---|
| esquema de color `.colors` | esperado | esperado | **probado** (sesión anidada, 2026-10-18) | KColorScheme (estable desde KF5) |
| tema global (look-and-feel con fallback a Breeze) | esperado | esperado | **probado** (sesión anidada, 2026-10-18) | `kpackagetool6`, `plasma-apply-lookandfeel` |
| estilo de Plasma (hereda de Breeze; `plasmarc` con `[ContrastEffect]`, `[AdaptiveTransparency]`) | esperado | esperado | **probado** (sesión anidada, 2026-10-18) | `AdaptiveTransparency` no documentado: se prueba |
| decoración Breeze coloreada | esperado | esperado | **probado** (sesión anidada, 2026-10-18) | `[WM]`, `Colors:Header` |
| Konsole `.colorscheme` | esperado | esperado | pendiente | Konsole ≥ 22 |
| Alacritty `[colors]` (TOML) | independiente de Plasma | — | experimental (no instalado aquí; TOML válido con todas las secciones `colors.*`, 2026-10-18) | Alacritty ≥ 0.13 (configuración TOML; `general.import` desde 0.14) |
| Kitty `.conf` (`color0..15`, selección, cursor, pestañas) | independiente de Plasma | — | experimental (no instalado aquí; 37 claves y cabecera `## name:`, 2026-10-18) | Kitty ≥ 0.26 (`include`, `kitten themes`) |
| VS Code (extensión de tema: `colors`, `tokenColors`, `semanticTokenColors`) | independiente de Plasma | — | experimental (VS Code no instalado aquí; la misma extensión está probada en Positron) | VS Code ≥ 1.80 (`editorIndentGuide.background1`, `activityBarTop.*`) |
| Positron y VSCodium (la misma extensión, en `~/.positron/extensions/` y `~/.vscode-oss/extensions/`) | independiente de Plasma | — | **probado** en Positron 2026.06.0 (sesión anidada, 2026-10-18: interfaz, sintaxis y terminal en las dos variantes); VSCodium no instalado aquí (experimental) | Positron ≥ 2025.x y VSCodium ≥ 1.80 (base de VS Code ≥ 1.80); el instalador los cubre solo si existe su carpeta |
| Zed (`themes/<id>.json`, esquema v0.2.0) | independiente de Plasma | — | experimental (no instalado aquí; JSON válido por estructura, 2026-10-18) | Zed ≥ 0.130 (temas de usuario en `~/.config/zed/themes/`) |
| LibreOffice «Colores de la aplicación» (`.oxt` de configuración y fragmento `.xcu`) y paletas `.soc` | independiente de Plasma | — | **probado** en LibreOffice 26.2.6 (perfil desechable en KWin virtual, 2026-11-01: extensión instalada con `unopkg`, los dos esquemas en Writer y las dos paletas en el diálogo de área de Draw; `validacion.md` §10); Calc, Impress y la IDE de BASIC, sin mirar | LibreOffice ≥ 24.8 (lista de 91 entradas tomada del esquema de 26.2; versiones anteriores ignoran las que no conocen); la interfaz la da Plasma salvo que se active `LibreOfficeTheme` |
| Obsidian (`theme.css` en `.obsidian/themes/Lliphi/`, variables de `app.css` en `.theme-light` y `.theme-dark`) | independiente de Plasma | — | **probado** en Obsidian 1.14.5 (vault del autor, 2026-11-01: variables medidas en las dos variantes, Tema de iconos, Tableros, Captura y llamadas de Zotero) | Obsidian ≥ 1.14 (`--callout-color` como color, no como terna RGB) |
| Zen Browser (`userChrome.css` sobre las variables `--zen-*` y de Firefox con `prefers-color-scheme`; `user.js`) | independiente de Plasma (sigue al modo del sistema por el portal) | — | **probado** en Zen 1.24b, Flatpak (sesión anidada, 2026-11-01: colores medidos en las dos variantes y cambio en vivo al cambiar el esquema) | Zen ≥ 1.24 (nombres de variables de Zen; pueden cambiar entre versiones) |
| Google Chrome (tema de extensión, Manifest V3, `theme.colors`) | independiente de Plasma (no sigue al sistema) | — | **probado** en Chrome 156 (perfil desechable en la sesión anidada, 2026-11-01: los dos temas cargados por DevTools; el oscuro, levemente reinterpretado por Material 3) | Chrome ≥ 120 (Manifest V3) |
| Telegram Desktop (`.tdesktop-theme`: zip con `colors.tdesktop-theme` y `tiled.png`) | independiente de Plasma | — | **implementado** para Telegram 7.3.3 (Snap): las 586 claves de su paleta, comprobadas por las pruebas; arranque aislado en KWin virtual, sin ver el tema aplicado (hace falta una cuenta) | Telegram Desktop ≥ 7.3 (una versión más nueva deja sus colores por omisión en las claves que añada); sigue al sistema con «Modo nocturno automático» |
| fondo con `images_dark/` | no (solo `images/`) | no | **probado** por ruta del paquete; por nombre no resolvió | `images_dark/` llega en 6.6; antes se usa la imagen clara |
| acento declarado por el fondo | esperado | esperado | pendiente | `X-KDE-PlasmaImageWallpaper-AccentColor` |
| iconos de carpeta (`lliphi`, `lliphi-oscuro`; heredan de Breeze; `FollowsColorScheme`) | esperado | esperado | **probado** (Dolphin en sesión anidada, 2026-10-18: 22, 32 y 64 px escalable, dos variantes; defecto 1 de `validacion.md` §5.3) | KIconLoader (KF 6) recolorea `current-color-scheme`; GTK ve los colores de respaldo del SVG |
| GTK generado por Plasma | esperado | esperado | pendiente | `kde-gtk-config`, `breeze-gtk` |
| decoración Aurorae `lliphi` / `lliphi-claro` (marco de WhiteSur y botones de Nothing recoloreados, GPL-3.0-or-later) | no (el motor SVG V2 llega en 6.6; antes queda la decoración Breeze coloreada) | no | **probado** (sesión anidada, 2026-10-18: Dolphin y Kate en las dos variantes, `validacion.md` §6) | `kwin-style-aurorae` ≥ 6.6 (`library=org.kde.kwin.aurorae.v2`) |
| «guardar como tema global» de 6.6 | — | — | no se usa | bug 516318 |

## 2. Por distribución

| distribución | Plasma | sesión | notas |
|---|---|---|---|
| **Kubuntu 26.04 LTS** (máquina del autor) | 6.6.6, Qt 6.10.2, KF 6.24 | Wayland | referencia; rutas XDG por defecto; sin Kvantum |
| Kubuntu 24.04 LTS | 5.27 | — | **fuera de alcance**: el proyecto es Plasma 6 |
| KDE neon (user) | última estable | Wayland | esperado idéntico a Kubuntu 26.04 |
| Fedora KDE 43 | 6.5–6.6 | Wayland | esperado; `kpackagetool6` en `kf6-kpackage`; SELinux no afecta a `~/.local` |
| Arch / EndeavourOS / Manjaro | rodante | Wayland | esperado; verificar `plasma-apply-*` en `plasma-workspace` |
| openSUSE Tumbleweed | rodante | Wayland | esperado |
| Debian 13 | 6.3 | Wayland/X11 | esperado; sin `images_dark/` |
| X11 (cualquiera) | 6.x | X11 | esperado igual: nada del proyecto depende del protocolo gráfico |

## 3. Lo que no depende de la versión

Esquemas de color, Konsole, Alacritty, Kitty, VS Code, Positron, VSCodium, Zed, LibreOffice, iconos de carpeta, tokens, instalador (rutas XDG), sitio y documentación. Lo que sí: paquetes de fondo con
`images_dark/`, funciones de 6.6 y la decoración Aurorae (motor V2 de 6.6).
