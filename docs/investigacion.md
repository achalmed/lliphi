---
tipo: doc
estado: activo
titulo: 'Investigación (fase 2): matriz de referencias, mecánica de temas en Plasma 6, estándares y lecciones'
---
# Investigación

Fase 2 del encargo, 2026-10-18. Complementa `analisis-temas-de-partida.md` (Nothing y WhiteSur en disco). Lo
obtuvo un agente de la sesión por web y lo comprobó el director en la máquina (Plasma 6.6.6): `kwin-style-aurorae`
6.6.6, `breeze-dark` reducido a `colors` + `metadata.json` + `plasmarc`, los `.knsrc` y sus órdenes de adopción,
el `~/.config/gtk-4.0/colors.css` que genera Plasma, `images_dark/` en el fondo «Next». Lo que no se pudo verificar
está en §6. Las fuentes de KDE Developer, freedesktop, Design Tokens, REUSE y SPDX están en Calibre (ids
10520–10534); el resto se cita por URL.

## 1. Matriz de referencias

| proyecto · categoría | rasgos destacados | inspiración visual | buena práctica técnica | compatibilidad | licencia y reutilización | límites | lección |
|---|---|---|---|---|---|---|---|
| **Dracula** · ecosistema (517 repos, sitio Next.js) | paleta de 11 colores con roles; un repo por aplicación; plantilla `dracula/template` (README, INSTALL, LICENSE, sample, screenshot); catálogo web alimentado por `INSTALL.md` y metadatos de GitHub vía Redis; Dracula PRO de pago | sobriedad de una paleta pequeña; claro «Alucard» como pareja del oscuro | la paleta es la única fuente que todos citan; página por app con instalación, repo e issues | editores y terminales; en KDE solo una carpeta `kde/` heredada dentro de `dracula/gtk`, sin tema global | MIT (índice, plantilla, Konsole); `dracula/gtk` GPL-3.0 | sin derivación de superficies ni estados; dos valores para «Current Line» (README ≠ spec); gobierno de revisión no publicado | tokens → generado por app; catálogo sin documentación duplicada; criterios de aceptación escritos |
| **Seduction Linux / jomada** · temas globales (Nothing, Ned, Bart, Carl, Lenny) | oscuro con transparencia y desenfoque, un acento, contorno resaltado en la ventana activa, esquema, Aurorae, Konsole y dos fondos por tema | coherencia entre panel, ventanas, Konsole y fondo | — | Plasma 6, KDE Store | GPL 3+ y CC BY-SA 4.0; sin repositorio git | copia Breeze y WhiteSur; colores fijos en SVG; depende de Colloid y WhiteSur-cursors; sin claro (salvo Ned) | lo que falta en su modelo es lo que aporta este proyecto: repositorio, tokens, pruebas y sitio |
| **WhiteSur-kde** (vinceliuice) · tema global por script | `install.sh` con opciones; variantes y escalas por duplicación de carpetas; iconos de 62 MB | proporciones de panel y dock; borde de 1 px tenue; márgenes de 8 px | generación por script (Colloid, Graphite, Layan comparten el patrón) | Plasma 6; exige Kvantum | GPL-3.0 | imitación literal de macOS; sombra de texto blanca; `translucent/` vacío | variantes por parámetros, no por copias; no exigir Kvantum |
| **Breeze** (KDE) · base del sistema | `breeze-dark` = `colors` + `metadata.json` + `plasmarc`: hereda todo lo demás; SVG con `<style id="current-color-scheme">`; decoración coloreada por `[WM]` y `Colors:Header` | — | el mínimo que hereda; iconos monocromos que siguen el esquema | la referencia en Plasma 6.6 | LGPL (estilo) y GPLv2+ (look-and-feel) | — | empezar por el mínimo que hereda de Breeze |
| **Catppuccin** · paleta + ports | 4 variantes × 26 colores; `whiskers` renderiza plantillas `.tera` a `generated/` y `just check` falla si lo generado difiere; `catppuccin/kde` con esquemas, look-and-feel y splash, sin Kvantum | — | **el modelo de generación**: fuente única, plantillas por app, comprobación de deriva | Plasma 6 | MIT | docs no accesibles al verificar | fuente → plantillas → generado con prueba de deriva (coincide con «generado no se edita») |
| **Nord** · paleta | 16 colores sobrios | frialdad contenida | — | ports de la comunidad | MIT | casi inactivo (2023) | una paleta pequeña envejece bien |
| **Rosé Pine**, **Everforest**, **Tokyo Night**, **Gruvbox** · paletas de editor | identidad clara; repo central de portado (Rosé Pine) | — | repo central que coordina los ports | editores | MIT / Apache-2.0 | no cubren escritorio | — |
| **Papirus**, **Tela** · iconos | completos y «pixel perfect» | — | `Inherits` y contextos de la spec freedesktop | Plasma, GTK | GPL-3.0 | pesados; GPL contagia si se derivan | heredar de `breeze`, entregar solo lo que cambia |
| **Colloid / Graphite** (vinceliuice) · temas GTK+KDE | `install.sh -t color -c claro/oscuro --tweaks nord/dracula/…` compila SCSS con `sassc` | — | parámetros en vez de copias | GTK 3/4, Plasma | GPL-3.0 | temas GTK propios compiten con lo que Plasma ya genera | GTK vía el mecanismo de Plasma (`breeze-gtk`) |
| **Lightly / Darkly / Klassy** · estilos de widgets Qt en C++ | aspecto moderno; Klassy con ramas por versión de Plasma y exige ≥ 6.6 | — | — | se recompilan en cada Plasma/Qt | NOASSERTION / sin `LICENSES/` | Lightly archivado 2026-05; coste de ramas por versión | no depender de estilos compilados |
| **Kvantum** · motor de estilo Qt por SVG | `.kvconfig` + `.svg`; 1.1.8 | — | — | Qt 6; 1.1.7 corrigió regresiones con Qt 6.11 en Wayland | GPL | frágil ante cada Qt; instala como root; duplica la paleta | módulo opcional, nunca requisito |
| **Utterly Nord**, **Sweet** · temas globales | transparencia y desenfoque; neón | — | — | Plasma 6 | GPL-2.0 / GPL-3.0 | — | — |

## 2. Mecánica de cada categoría en Plasma 6.6 (lo que decide la arquitectura)

| categoría | archivos y tecnología | lo controla KDE | instalar / aplicar / quitar (usuario) | límite |
|---|---|---|---|---|
| tema global (look-and-feel) | `metadata.json` (`KPackageStructure: Plasma/LookAndFeel`, `KPlugin.Id`), `contents/defaults` (`[archivo][grupo]`: `kdeglobals` KDE/General/Icons, `plasmarc` Theme, `[Wallpaper]`, `kcminputrc` Mouse, `kwinrc` kdecoration2, `[KSplash]`), `layouts/*.js`, `previews/`, opcionales `splash/`, `logout/`, `lockscreen/LockScreen.qml`; `X-KDE-fallbackPackage`, `X-KPackage-Dependencies: kns://…` | sí: fija cada componente al aplicarse; 6.6 añade «guardar como tema global» (`KLookAndFeelManifest::snapshot`, bug 516318) | `kpackagetool6 -t Plasma/LookAndFeel -i/-u/-r`; `plasma-apply-lookandfeel -a <id>` (`--resetLayout`, `-k`); KNS adopta con `plasma-apply-lookandfeel --apply` | la disposición borra el escritorio actual (opt-in); `[KDE] LookAndFeelPackage` y `DefaultLight/DarkLookAndFeel` en `kdeglobals` |
| estilo de Plasma (desktoptheme) | `metadata.json`, `plasmarc` (`[ContrastEffect]`, `[BlurBehindEffect]`, `[AdaptiveTransparency]`, `[Wallpaper]`, `[Settings] FallbackTheme`), `colors` (esquema sin `ColorEffects`), `widgets/`, `dialogs/`, `opaque/`, `translucent/`, `solid/`, `icons/`; SVG con `hint-*`, `shadow-*`, `mask-*`, `floating-hint-*` y `<style id="current-color-scheme">` con 11 clases `ColorScheme-*` | sí | `~/.local/share/plasma/desktoptheme/<Id>`; `plasma-apply-desktoptheme` | lo que falta cae a Breeze; subir `Version` invalida la caché |
| esquema de color | `.colors`: `[Colors:View/Window/Button/Selection/Tooltip/Complementary/Header(+Inactive)]` × 12 claves `R,G,B`; `[General]`, `[KDE] contrast`, `[WM]`, `[ColorEffects:Disabled/Inactive]`; opcional `TintFactor` | sí; el acento (`[General] AccentColor`, del esquema, del fondo o personalizado) reescribe `ForegroundActive`, `ForegroundLink`, `DecorationFocus`, `DecorationHover` y la selección en siete grupos, mezclando en OKLab si hay `TintFactor` | `~/.local/share/color-schemes/`; `plasma-apply-colorscheme <nombre> [-a acento]` | el esquema debe tolerar que Plasma pise sus roles de acento |
| decoración de ventanas | Aurorae: carpeta con `decoration.svg`, un SVG por botón, `<tema>rc` (`[General]`, `[Layout]`), `metadata.desktop`; **6.6 reescribió Aurorae**: motor SVG nuevo (V2) y QML aislado en V1 con futuro incierto. Alternativa: Breeze coloreada por `[WM]` y `Colors:Header` | sí | `~/.local/share/aurorae/themes/`; KNS adopta con `plasma-apply-aurorae` (no está en el PATH de esta máquina) | baja estabilidad en 2026: **el primer lote usa Breeze con los colores del esquema** |
| iconos | freedesktop Icon Theme: `index.theme` (`Inherits`, `Directories`, `Context`, `Type`); Breeze monocromo con `.ColorScheme-Text` y `fill: currentColor` | parcial: Plasma tiñe los monocromos | `~/.local/share/icons/`; KNS adopta con `plasma-changeicons` | un tema propio entrega solo lo que cambia y hereda `breeze`/`hicolor` |
| cursores | Xcursor (`xcursorgen` desde PNG por tamaño 16–256; `clickgen` desde SVG), `index.theme` con `Name` = carpeta, `cursors/` con alias | sí | `~/.local/share/icons/<Tema>/` (`~/.icons` obsoleto); `plasma-apply-cursortheme` | X11 y Wayland |
| fondos | paquete: `metadata.json`, `contents/images/<AnchoxAlto>.png`, `images_dark/` (6.6), `screenshot.png`; acento por fondo con `X-KDE-PlasmaImageWallpaper-AccentColor` `{Light, Dark}` | sí | `~/.local/share/wallpapers/`; `plasma-apply-wallpaperimage` | — |
| splash, bloqueo, cierre de sesión | `[KSplash] Theme` + `contents/splash/Splash.qml`; `contents/lockscreen/LockScreen.qml` (6: `onPromptChanged`, `authenticator.startAuthenticating()`); `contents/logout/`; colores de `[Colors:Complementary]` | sí, desde el paquete global | con el paquete global | ninguno de los temas de esta máquina trae lockscreen; heredar de Breeze al principio |
| Konsole | `.colorscheme` INI: `[Background]`, `[Foreground]`, `[Color0..7]` con `Faint` e `Intense`, `[General]` (`Opacity`, `Blur`, `Description`) | no (Konsole) | `~/.local/share/konsole/`; se elige en el perfil | ideal para generar desde la paleta |
| aplicaciones Qt | Breeze lee el esquema; Kvantum (`.kvconfig` + `.svg`) y qt6ct son opcionales | sí con Breeze | — | Kvantum frágil: módulo opcional |
| GTK | `kde-gtk-config` sincroniza fuentes, iconos, cursor, oscuro y botones (GSettings en Wayland); `breeze-gtk` genera `gtk-3.0/gtk.css`, `gtk-4.0/gtk.css` y `assets/` **desde el esquema** (SCSS con `sassc` y pycairo); en esta máquina `~/.config/gtk-4.0/colors.css` lo escribe Plasma | sí: el esquema basta | ninguna acción propia | libadwaita no admite temas completos; el portal expone `color-scheme`, `accent-color` y `contrast` |
| SDDM, Plymouth | SDDM: `Main.qml`, `metadata.desktop`, `theme.conf` (`theme.conf.user`), `sddm-greeter --test-mode`; Plymouth: `.plymouth` + script | sí, desde el paquete global | `/usr/share/sddm/themes/` y `/usr/share/plymouth/themes/`: **root** (`sddmthemeinstaller`, `kplymouththemeinstaller`) | módulo posterior; el instalador de usuario no los toca |
| editores, navegadores, productividad, ciencia | cada aplicación tiene su formato (JSON de VS Code, `.toml` de Zed, CSS de Firefox, temas de RStudio/Positron, Zen) | no | por aplicación | módulos posteriores generados desde la misma paleta |
| KDE Store / KNS | categorías «Global Themes (Plasma 6)», «Plasma Theme», «KDE Color Scheme KDE4», «Window Decoration Aurorae», «KDE Icon Theme», «X11 Mouse Theme», «KDE Wallpaper», «SDDM Theme», «Plymouth Themes»; ficha con `Source`, licencia y versión | — | subida manual en pling/opendesktop | procedimiento de alta no verificado |

## 3. Estándares del repositorio

- **Design Tokens Format Module 2025.10** (final del W3C Community Group, 2025-10-28): `$value`, `$type` explícito o heredado, `$description`, `$extensions`, `$deprecated`, grupos, `$root`, `$extends`, alias `{grupo.token}`, color `{"colorSpace":"oklch","components":[L,C,H],"alpha":1,"hex":"#…"}`. Herramientas: Style Dictionary 5.x (soporte 2025.10 en curso), Terrazzo (`lint`, `check`). Ninguna emite `.colors`, `.colorscheme` ni CSS de GTK: el generador es propio (Python), el estándar sirve para intercambio.
- **REUSE 3.3**: `LICENSES/<SPDX>.txt`, `REUSE.toml` (`version = 1`, `[[annotations]]` con `path`, `precedence`, `SPDX-FileCopyrightText`, `SPDX-License-Identifier`), cabeceras por archivo o `.license` adyacente; `reuse lint` en la verificación. Criterio: código original MIT; activos gráficos CC BY-SA 4.0 (como los fondos de KDE); nada derivado de temas GPL para no contagiar.
- **Contraste**: WCAG 2.2 1.4.3 (texto 4.5:1; grande 3:1; sin redondeo) y 1.4.11 (componentes y foco 3:1 frente a lo adyacente); APCA solo informativo (beta 0.1.9). Espacio de trabajo OKLCH (CSS Color 4, aún CRD); `coloraide` 8.13.1 (MIT, Oklch, mapeo de gama, contraste WCAG) como biblioteca; Plasma ya tiñe en OKLab.

## 4. Decisiones que fija esta investigación

1. Fuente única de tokens en JSON DTCG 2025.10 con color en OKLCH y `hex` de respaldo; todo derivado se genera y una prueba de deriva (modelo Catppuccin) falla si difiere.
2. Tabla de roles → `grupo.clave` del esquema de Plasma, con superficies, bordes y estados derivados por funciones en OKLCH, y prueba de contraste 1.4.3 y 1.4.11 por par.
3. Primer lote mínimo que hereda de Breeze: tema global (`metadata.json` + `defaults` + `layouts` + previews, `X-KDE-fallbackPackage=org.kde.breeze.desktop`), esquema `.colors` claro y oscuro, estilo de Plasma reducido (`metadata.json` + `colors` + `plasmarc` + los pocos SVG propios), Konsole, fondos con `images_dark/` y acento declarado.
4. Decoración: Breeze coloreada por el esquema; Aurorae solo si algún día se hace en SVG (V2), nunca en QML.
5. Sin Kvantum, sin estilos compilados en C++, sin tema GTK propio (lo genera Plasma desde el esquema).
6. Iconos y cursores: heredar `breeze` y `breeze_cursors`; un módulo propio solo entrega lo que cambia.
7. SDDM y Plymouth: módulo posterior con confirmación explícita; el instalador de usuario no toca `/usr`.
8. Variantes por parámetros desde la misma paleta; el acento es entrada, no copia; identificadores `org.<marca>.<variante>` y carpeta = `Id`.
9. Repositorio con REUSE desde el primer commit; todo SVG propio.
10. Instaladores que simulan por defecto, escriben solo en `~/.local/share` y `~/.config`, respaldan y dejan `UNDO.sh`; aplicar con `plasma-apply-*`.
11. Catálogo web al estilo Dracula: una página por pieza desde un `INSTALL.md` normalizado; criterios de aceptación escritos (contraste, licencia, instalación reversible).

## 5. Rasgos de los temas de partida que conviven, se rediseñan o se descartan

Resumen de `analisis-temas-de-partida.md` §8: **conviven** la jerarquía de planos y los márgenes de 8 px de WhiteSur, y la barra fina con dock flotante de Nothing; **se rediseñan** el acento (uno solo, ≥ 4.5:1, que siga al sistema), el foco, los radios, la translucidez, Konsole, los botones de ventana y las variantes; **se descartan** el semáforo, el appmenu global, el logo y la fuente de Apple, Kvantum, el fondo Big Sur, los cursores WhiteSur y la duplicación de archivos.

## 6. No verificado

Alta y subida en KDE Store/pling; Arch Wiki (bloqueada): `qt6ct`, `QT_QPA_PLATFORMTHEME`; guía oficial de Catppuccin (`whiskers.toml`); secciones de un `.kvconfig`; claves exactas que admite `contents/defaults` (`kscreenlockerrc`, SDDM); `AdaptiveTransparency` no está en la documentación pública (solo en el `plasmarc` local); formato de tema Aurorae V2 y si cambió el `rc`; qué captura exactamente la función «guardar tema» de 6.6; licencias que la API de GitHub no detecta (Gruvbox, Klassy, Kvantum, Lightly, Darkly); reconstrucción del initramfs para Plymouth; `cursor-builder`.
