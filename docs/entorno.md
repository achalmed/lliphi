---
tipo: doc
estado: activo
titulo: 'Inventario del entorno de desarrollo y de prueba (fase 1 del prompt de ecosistema de temas)'
---
# Inventario del entorno

Lo que había en la máquina del autor el 2026-10-18, comprobado con órdenes y no supuesto. Se vuelve a
comprobar cuando cambie la distribución o Plasma. Rutas relativas a `~`.

## Sistema

| qué | valor | cómo se comprobó |
|---|---|---|
| distribución | Ubuntu 26.04.1 LTS (Kubuntu), núcleo 7.0.0-38 | `lsb_release -ds`, `uname -r` |
| Plasma | 6.6.6 | `plasmashell --version` |
| Qt | 6.10.2 | `qtpaths6 --qt-version` |
| KDE Frameworks | 6.24.0 | `dpkg -l libkf6coreaddons6` |
| sesión | Wayland (`XDG_SESSION_TYPE=wayland`, `XDG_CURRENT_DESKTOP=KDE`), KWin Wayland 6.6.6 | variables de entorno |
| pantalla | eDP-1, 1920×1080 a 60 Hz, escala 1 | `kscreen-doctor -o` |
| gestor de sesión | SDDM 0.21 (temas en `/usr/share/sddm/themes`: breeze, kubuntu, WhiteSur-dark) | `dpkg -l sddm` |
| arranque | Plymouth 24.004 | `dpkg -l plymouth` |
| RAM | 15 GiB, de los que quedaban 2,5 GiB disponibles al inspeccionar | `free -h` |
| disco | 35 GB libres de 234 (85 % usado) | `df -h ~` |
| usuarios | `achalmaedison` (1000) y `prueba-tema` (1001, creado el 2026-10-18 para la validación limpia de la fase 7) | `/etc/passwd` |
| virtualización | `qemu-system-x86_64` y `docker` presentes; sin `virt-manager`, `distrobox` ni `podman` | `command -v` |
| `sudo` | pide contraseña interactiva: el asistente no puede usarlo; el autor ejecuta lo privilegiado | `sudo -n true` |

## Tema en uso al inspeccionar

| componente | valor | archivo |
|---|---|---|
| tema global | `com.github.vinceliuice.WhiteSur-dark` | `kdeglobals` `[KDE] LookAndFeelPackage` |
| esquema de color | WhiteSurDark | `kdeglobals` `[General] ColorScheme` |
| estilo de Plasma | WhiteSur-dark | `plasmarc` `[Theme] name` |
| decoración | Aurorae, `__aurorae__svg__WhiteSur-dark` | `kwinrc` `[org.kde.kdecoration2]` |
| iconos | WhiteSur-dark | `kdeglobals` `[Icons] Theme` |
| cursores | WhiteSur-cursors | `kcminputrc` `[Mouse] cursorTheme` |
| estilo de widgets | Breeze | `kdeglobals` `[KDE] widgetStyle` |
| GTK | tema Breeze, iconos WhiteSur-dark, fuente Noto Sans 10, oscuro preferido | `~/.config/gtk-3.0/settings.ini` |

Antes de instalar nada se respaldan `kdeglobals`, `plasmarc`, `kwinrc`, `kcminputrc`, `gtk-3.0/settings.ini`,
`gtk-4.0/settings.ini`, `ksplashrc`, `kscreenlockerrc` y `plasma-org.kde.plasma.desktop-appletsrc`.

## Rutas de instalación de usuario (XDG)

`XDG_DATA_HOME` y `XDG_CONFIG_HOME` no están definidas: valen `~/.local/share` y `~/.config`. `XDG_DATA_DIRS`
incluye los `exports` de Flatpak, `/usr/local/share`, `/usr/share` y el escritorio de snap.

| componente | ruta de usuario | existe | ruta de sistema |
|---|---|---|---|
| tema global (look-and-feel) | `.local/share/plasma/look-and-feel/` | sí: `Nothing`, `com.github.vinceliuice.WhiteSur-dark` | `/usr/share/plasma/look-and-feel/` (breeze, breezedark, breezetwilight, oxygen, kubuntu) |
| estilo de Plasma | `.local/share/plasma/desktoptheme/` | sí: `Nothing`, `WhiteSur-dark` | `/usr/share/plasma/desktoptheme/` |
| esquemas de color | `.local/share/color-schemes/` | sí: `Nothing`, `WhiteSur`, `WhiteSurAlt`, `WhiteSurDark` | `/usr/share/color-schemes/` |
| decoraciones Aurorae | `.local/share/aurorae/themes/` | sí: `Nothing` y 11 variantes de WhiteSur | no existe en el sistema |
| iconos | `.local/share/icons/` y `.icons/` | sí: Colloid-Grey (3), WhiteSur (3); cursores WhiteSur | `/usr/share/icons/` (breeze, breeze-dark, Adwaita, Oxygen…) |
| fondos | `.local/share/wallpapers/` | sí | `/usr/share/wallpapers/` |
| Konsole | `.local/share/konsole/` | sí: `Nothing.colorscheme`, perfil propio | — |
| Kvantum | `.config/Kvantum/` | no (paquete `qt6-style-kvantum` 1.1.5 disponible, no instalado) | — |
| GTK | `.themes/`, `.local/share/themes/` | no | `/usr/share/themes/` |
| SDDM, Plymouth | — (solo sistema) | — | `/usr/share/sddm/themes/`, `/usr/share/plymouth/themes/` |

## Herramientas

| herramienta | versión | para qué |
|---|---|---|
| `kpackagetool6` 2.0 | sí | instalar y quitar paquetes de Plasma (look-and-feel, desktoptheme) en el usuario |
| `plasma-apply-lookandfeel`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `plasma-apply-cursortheme`, `plasma-apply-wallpaperimage` | sí | aplicar cada componente sin interfaz |
| `kreadconfig6`, `kwriteconfig6` | sí | leer y escribir la configuración |
| `spectacle` 6.6.6 | sí | capturas |
| Inkscape 1.4.3, GIMP 3.2.2 | sí | SVG de decoraciones, iconos y fondos |
| Python 3.13.9 con PyYAML 6.0.3 y Pillow 12.3; pytest 8.4.2 | sí | tokens, generadores y pruebas |
| Node 24.18, npm 11.16, pnpm 12.14 | sí | sitio, si hiciera falta |
| Quarto 1.9.38 | sí | el hub `web` y, si se elige, el sitio del tema |
| git 2.53, `gh` 2.46 autenticado como `achalmed` por SSH | sí | repositorio y publicación (la publicación la ejecuta el autor) |
| ShellCheck | sí | instaladores |
| Konsole 25.12.3, Dolphin, Kate | sí | aplicaciones de prueba |
| no están | `kvantummanager`, `code`, `rsvg-convert`, `optipng`, `scour`, `hugo`, `netlify` (CLI), `coloraide` (Python) | se instalan si un módulo los necesita |

Tipografías libres presentes: IBM Plex Sans y Plex Mono, Fira Code Nerd Font, Hack, Cantarell, DejaVu, Noto Sans
(la de la interfaz). Inter y Atkinson no están.

## Temas de partida

| id | nombre en la tienda | autor | tipo | versión | licencia (etiqueta y `metadata.json`) | cambió | archivo |
|---|---|---|---|---|---|---|---|
| 1400424 | «Apple MacOS [WhiteSur-Dark]» | vinceliuice | Global Themes (Plasma 6) | sin versión en la tienda; 0.1 en el paquete | `gplv3` / GPLv3; repositorio `github.com/vinceliuice/WhiteSur-kde` | 2025-11-05 | `com.github.vinceliuice.WhiteSur-dark.tar.gz`, 1,8 MB |
| 2116667 | «Nothing» | jomada | Global Themes (Plasma 6) | 1.8 | `gplv3` / GPL 3+; sitio `seduccionlinux.wordpress.com` | 2026-03-21 | `Nothing.tar.gz`, 168 KB |

Hallazgos:

- Los dos están instalados en `~/.local/share` y el de WhiteSur está en uso: la fase 2 los examina en disco, sin descargar nada.
- La página de la tienda (`store.kde.org/p/<id>`) responde con una comprobación antibots; la API OCS
  (`api.opendesktop.org/ocs/v1/content/data/<id>?format=json`) sí entrega los metadatos y el enlace de descarga.
- **Nothing es obra del mismo autor que Seduction Linux**: su `metadata.json` apunta a `seduccionlinux.wordpress.com`.
  Las dos referencias «complementarias» del encargo son una sola fuente.
- **WhiteSur es, por definición de su autor, «MacOS like»**. El encargo pide no parecerse a macOS: de WhiteSur se
  toman cualidades (geometría suave, coherencia entre componentes, familia de variantes y escalas ×1.25 y ×1.5), no
  su parecido con Apple. Lo decide la fase 2.
- Ninguno de los dos paquetes trae `LICENSE` dentro del tarball; la licencia consta en la tienda y en el `metadata.json`.

## Acceso a las referencias

Todas respondieron 200 el 2026-10-18: la tienda (con antibots), la API OCS, `draculatheme.com`,
`seduccionlinux.wordpress.com`, `achalmaedison.netlify.app`, `github.com`, `invent.kde.org`,
`develop.kde.org/docs/plasma/theme/` y `specifications.freedesktop.org/icon-theme-spec/`.

## Ecosistema del autor que toca el proyecto

- `meta/workspace.yml`: no hay proyecto de temas; esta carpeta no está declarada todavía (alta tras el nombre).
- `~/.dotfiles/kde` (paquete stow): `kdeglobals`, `kwinrc`, `plasmarc`, `dolphinrc`, `kglobalshortcutsrc`,
  `plasma-localerc`, `mimeapps.list`. La selección del tema vive ahí; el repositorio del tema no la toca.
- `web` (Quarto 1.9, Netlify, 11 blogs satélite como submódulos en `_pubs/`, tema compartido por enlaces duros).
- `identidad-visual`: maestro de tokens `tokens/colors.json` y generadores por destino (patrón a imitar).

## Riesgos y bloqueos

| riesgo | efecto | mitigación |
|---|---|---|
| 2,5 GiB de RAM libres durante la inspección | una segunda sesión de Plasma (usuario `prueba-tema`) convive justa con la del autor | cerrar aplicaciones pesadas antes de abrir la sesión de prueba; la VM con QEMU queda como alternativa |
| `sudo` interactivo | SDDM, Plymouth, `/usr/share` e instalación de paquetes quedan fuera del asistente | el asistente deja los comandos; el autor los ejecuta |
| disco al 85 % | una VM de 20 GB no cabe con holgura | se decide en la fase 7 |
| la tienda bloquea el navegador sin JavaScript | no se leen reseñas ni capturas desde el terminal | la API OCS y el paquete en disco bastan |
| Kvantum no instalado | el estilo de widgets Qt del primer lote será Breeze con el esquema de color propio | se evalúa Kvantum como módulo posterior |
| 12 GiB de RAM en uso durante la inspección | agentes en paralelo pueden agotar la memoria | como mucho dos agentes, y uno cuando se renderice o se capture |
