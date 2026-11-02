# Navegadores: Zen Browser y Chrome (`navegadores`)

Lliphi Claro y Lliphi Oscuro en los dos navegadores del autor: **Zen Browser** (basado en Firefox), que cambia solo
entre las dos variantes cuando cambia el modo del sistema, y **Google Chrome**, con un tema por variante.

Es un **complemento**: no es parte de un `Plasma/LookAndFeel`. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); por qué estos formatos y cómo se tradujeron los tokens:
decisión 5.3 de [`docs/decisiones.md`](../../docs/decisiones.md).

## Responsabilidad y formato

- `generado/navegadores/zen/userChrome.css`: redefine, con `!important` de hoja de usuario, las variables de color de
  Zen (`--zen-*`) y de Firefox (paneles, menús, foco, barra de direcciones) sobre unas variables propias
  (`--lliphi-*`), una tabla por variante; `@media (prefers-color-scheme: dark)` elige la oscura. Gana también a lo que
  Zen escribe en línea desde el degradado del espacio de trabajo, que queda en el gris de la ventana. Las ventanas
  privadas conservan el aspecto de Zen, para que se distingan.
- `generado/navegadores/zen/user.js`: `toolkit.legacyUserProfileCustomizations.stylesheets = true` (sin ella Zen no
  carga `userChrome.css`) y `zen.view.window.scheme = 2` (Zen sigue el modo del sistema; con 0 o 1 lo fija).
- `generado/navegadores/chrome/lliphi-claro/` y `lliphi-oscuro/`: dos temas de Chrome sin empaquetar
  (`manifest.json` de Manifest V3 con `theme.colors`). Chrome no admite una variante oscura dentro de un tema.
- El instalador pone lo de Zen en el perfil predeterminado (el de `installs.ini`, también el del Flatpak
  `app.zen_browser.zen`; con `ZEN_PERFIL` se elige otro) y los temas de Chrome en `$XDG_DATA_HOME/lliphi/chrome/`.
  Chrome no deja instalar un tema sin pasos manuales: `INSTALL.md`.

| papel | Zen | Chrome | sale de |
|---|---|---|---|
| barra lateral, franja de pestañas | `--zen-main-browser-background` | `frame`, `background_tab` | `fondo.ventana` |
| pestaña activa | `--tab-background-color-selected` | `toolbar` | `fondo.vista` (claro) · `fondo.boton` (Zen, oscuro) |
| barra de direcciones | `--zen-toolbar-element-bg`, `--toolbar-field-*` | `omnibox_background` | `fondo.ventana-alterno` · `fondo.vista` · `fondo.ventana` |
| textos | `--toolbox-textcolor`, `--tab-text-color-selected` | `tab_text`, `toolbar_text`, `bookmark_text` | `texto.normal`, `texto.secundario` |
| menús y paneles | `--arrowpanel-*`, `--panel-*` | — | `fondo.vista`, `texto.normal`, `borde.separador` |
| foco, selección, acento | `--focus-outline-color`, `--urlbarView-highlight-*`, `--zen-primary-color` | — (Chrome usa su acento) | `foco`, `seleccion.*`, `acento.base` |
| enlaces | `--link-color` | `ntp_link` | `enlace` |
| tipografía | Inter en `:root` | — (no se puede elegir) | `tipografia.interfaz` |

En Chrome, el motor Material 3 reinterpreta un poco los colores del tema (en el oscuro, la franja sale `#212223` en
vez de `#1b1c1e`) y el anillo de foco toma su propio acento: el tema fija los fondos y textos, no el acento.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos navegadores            # simula
.venv/bin/python herramientas/generar.py --modulos navegadores --aplicar
.venv/bin/python -m pytest -q pruebas -k navegadores
```

Para verlo sin tocar el perfil real, en la sesión de prueba (`herramientas/sesion.py`): Zen con
`sesion.py ejecutar -- flatpak run app.zen_browser.zen --no-remote` (la primera vez crea su perfil; después
`sesion.py recargar --modulos navegadores` y otra vez Zen), y `plasma-apply-colorscheme LliphiOscuro` dentro para ver
el cambio en vivo.

Pruebas: `test_navegadores_zen` (las dos tablas contra los semánticos, cada variable de Zen sobre una de Lliphi,
`color-scheme`, Inter, el `user.js` y el contraste ≥ 4,5:1 de cada texto sobre su fondo), `test_navegadores_chrome`
(Manifest V3, ternas válidas, cada color del maestro, contraste) y `test_instalar_navegadores` (perfil de
`installs.ini`, un `userChrome.css` ajeno no se pisa, Zen se omite si no hay perfil, `UNDO.sh` lo retira).
