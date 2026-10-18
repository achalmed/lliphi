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
| esquema de color `.colors` | esperado | esperado | pendiente de probar | KColorScheme (estable desde KF5) |
| tema global (look-and-feel con fallback a Breeze) | esperado | esperado | pendiente | `kpackagetool6`, `plasma-apply-lookandfeel` |
| estilo de Plasma (hereda de Breeze; `plasmarc` con `[ContrastEffect]`, `[AdaptiveTransparency]`) | esperado | esperado | pendiente | `AdaptiveTransparency` no documentado: se prueba |
| decoración Breeze coloreada | esperado | esperado | pendiente | `[WM]`, `Colors:Header` |
| Konsole `.colorscheme` | esperado | esperado | pendiente | Konsole ≥ 22 |
| fondo con `images_dark/` | no (solo `images/`) | no | pendiente | `images_dark/` llega en 6.6; antes se usa la imagen clara |
| acento declarado por el fondo | esperado | esperado | pendiente | `X-KDE-PlasmaImageWallpaper-AccentColor` |
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

Esquemas de color, Konsole, tokens, instalador (rutas XDG), sitio y documentación. Lo que sí: paquetes de fondo con
`images_dark/`, funciones de 6.6 y cualquier Aurorae.
