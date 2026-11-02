# GTK 3, GTK 4 y libadwaita (`gtk`)

Las aplicaciones GTK (GIMP aparte, que tiene su tema: complemento `gimp`) con los colores de Lliphi, los mismos que
Kvantum da a las de Qt (decisiones 4.37). No es un tema GTK: es una hoja de colores que se importa desde
`~/.config/gtk-3.0/gtk.css` y `~/.config/gtk-4.0/gtk.css` sobre el tema Breeze que pone KDE.

## Por qué así y no un tema propio derivado de WhiteSur-gtk

- **libadwaita no lee temas GTK.** Las aplicaciones GTK 4 con libadwaita (la mayoría de las nuevas) usan siempre su
  hoja; solo atienden a `gtk.css` del usuario. Un tema WhiteSur-gtk no les llegaría; esta hoja, sí.
- **KDE ya hace la mitad del trabajo.** `kde-gtk-config` deja Breeze en GTK y, en cada cambio de esquema, reescribe
  `colors.css` con los colores del esquema (`theme_bg_color_breeze`…) y añade `@import 'colors.css';` a `gtk.css` sin
  tocar lo demás. Lo único que falla es el origen: el esquema de Lliphi es la línea base de WhiteSur (grises #363636,
  decisión 4.4) y las aplicaciones Qt se ven con los neutros de los tokens que pone Kvantum (#1b1c1e). Esta hoja se
  importa después de `colors.css` y redefine esos mismos colores desde los tokens.
- **Reversible y pequeño.** Tres archivos CSS y una línea en cada `gtk.css`; sin `sassc` ni recursos rasterizados, sin
  cambiar `gtk-theme-name` (que gestiona `kde-gtk-config`) y sin romperlo: si se quita la línea, todo vuelve a ser lo
  que KDE genera.

Lo que se pierde: la forma de los controles es la de Breeze, no la de WhiteSur (Kvantum). Para GTK es la opción
mantenida por KDE y la que mejor se integra (decoraciones CSD, `colorreload-gtk-module`).

## Formato y estructura

- `gtk-3.0/lliphi-claro.css`, `gtk-3.0/lliphi-oscuro.css`: los 84 colores `*_breeze` que escribe `kde-gtk-config`, uno
  por variante (GTK 3 no tiene consultas de medios), y la caja de herramientas flotante de Xournal++.
- `gtk-4.0/lliphi.css`: las dos variantes con `@media (prefers-color-scheme: dark)` (GTK ≥ 4.20): los colores con
  nombre de libadwaita 1.9 (`window_bg_color`, `accent_bg_color`…) y sus variables (`--accent-bg-color`…: el libadwaita
  de Ubuntu fija esa variable directamente, con el naranja de Yaru), y los `*_breeze` de Breeze para GTK 4.
- Los derivados (selección sin foco, estados insensibles, borde de las etiquetas) se escriben como `mix()` de GTK sobre
  dos colores de los tokens: ningún hex fuera del maestro.

## Claro y oscuro

- **GTK 4 y libadwaita** cambian solos: KDE da `color-scheme` (prefer-dark / prefer-light) por el portal
  (`org.freedesktop.appearance`) según el esquema, y la hoja resuelve la consulta de medios.
- **GTK 3**: `kde-gtk-config` cambia `gtk-application-prefer-dark-theme` y `colors.css`; la línea de `gtk.css` que elige
  `lliphi-claro.css` u `lliphi-oscuro.css` la cambia `fondo-variante` (su vigilancia), solo si ya importa una hoja de
  Lliphi. Las ventanas abiertas de GTK 3 toman la nueva al volver a abrirse.
- `color-scheme` de GSettings (`org.gnome.desktop.interface`) lo ponen `aplicar.py` y `fondo-variante`, para lo que lo
  lea de ahí y no del portal.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos gtk --aplicar
python3 herramientas/instalar.py --modulos gtk            # simula la instalación
```

Pruebas: `test_gtk_hojas`, `test_gtk_contraste`, `test_gtk_importacion`, `test_fondo_sigue_a_la_variante` (GTK 3).
