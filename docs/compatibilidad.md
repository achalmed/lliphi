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
| Alacritty `[colors]` (TOML) | independiente de Plasma | — | pendiente | Alacritty ≥ 0.13 (configuración TOML; `general.import` desde 0.14) |
| Kitty `.conf` (`color0..15`, selección, cursor, pestañas) | independiente de Plasma | — | pendiente | Kitty ≥ 0.26 (`include`, `kitten themes`) |
| VS Code (extensión de tema: `colors`, `tokenColors`, `semanticTokenColors`) | independiente de Plasma | — | pendiente | VS Code ≥ 1.80 (`editorIndentGuide.background1`, `activityBarTop.*`) |
| Positron y VSCodium (la misma extensión, en `~/.positron/extensions/` y `~/.vscode-oss/extensions/`) | independiente de Plasma | — | pendiente | Positron ≥ 2025.x y VSCodium ≥ 1.80 (base de VS Code ≥ 1.80); el instalador los cubre solo si existe su carpeta |
| Zed (`themes/<id>.json`, esquema v0.2.0) | independiente de Plasma | — | pendiente | Zed ≥ 0.130 (temas de usuario en `~/.config/zed/themes/`) |
| fondo con `images_dark/` | no (solo `images/`) | no | **probado** por ruta del paquete; por nombre no resolvió | `images_dark/` llega en 6.6; antes se usa la imagen clara |
| acento declarado por el fondo | esperado | esperado | pendiente | `X-KDE-PlasmaImageWallpaper-AccentColor` |
| iconos de carpeta (`lliphi`, `lliphi-oscuro`; heredan de Breeze; `FollowsColorScheme`) | esperado | esperado | pendiente | KIconLoader (KF 6) recolorea `current-color-scheme`; GTK ve los colores de respaldo del SVG |
| GTK generado por Plasma | esperado | esperado | pendiente | `kde-gtk-config`, `breeze-gtk` |
| Aurorae propio | no se ofrece | no se ofrece | no se ofrece | motor V2 solo desde 6.6 |
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

Esquemas de color, Konsole, Alacritty, Kitty, VS Code, Positron, VSCodium, Zed, iconos de carpeta, tokens, instalador (rutas XDG), sitio y documentación. Lo que sí: paquetes de fondo con
`images_dark/`, funciones de 6.6 y cualquier Aurorae.
