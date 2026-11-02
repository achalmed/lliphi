"""Temas de navegador desde los tokens: Zen Browser (`userChrome.css` y `user.js`) y Google Chrome (dos temas).

**Zen** (basado en Firefox) pinta su interfaz con variables CSS propias (`--zen-*`) que en parte calcula en tiempo de
ejecución desde el degradado del espacio de trabajo y escribe en línea en `:root`, `#zen-browser-background` y
`#zen-toolbar-background`. Un `userChrome.css` es una hoja de usuario: sus `!important` ganan a las de Zen y a los
estilos en línea, así que redefine esas variables (y las de Firefox de paneles, menús y foco) sin selectores de la
interfaz más allá de los elementos que reciben las variables. La variante la elige `prefers-color-scheme` del
documento de la ventana, que sigue al sistema cuando Zen está en modo automático (`zen.view.window.scheme = 2`): por
eso el `user.js` lo fija, junto con `toolkit.legacyUserProfileCustomizations.stylesheets`, sin el que Zen no carga
`userChrome.css`. No se usa un tema WebExtension (Zen ignora casi todos sus colores al pintar con el degradado) ni un
«Zen Mod» (Zen los regenera desde su tienda: uno local no sobrevive).

**Chrome** no tiene variante oscura en un tema: un `manifest.json` con `theme.colors` fija los colores y Chrome deja
de seguir al sistema. Por eso son dos temas sin empaquetar, Lliphi Claro y Lliphi Oscuro; se carga el de la variante
que se use (decisiones 5.3).

Ningún color se escribe aquí: los hexes salen de `tokens/tokens.json` y las pruebas lo comprueban."""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import VERSION, escribir, semanticos

# ---------------------------------------------------------------- Zen

# variable propia de Lliphi → semántico de cada variante (las de Zen y Firefox se definen sobre estas)
LLIPHI = {"ventana": "fondo.ventana", "ventana-alterno": "fondo.ventana-alterno", "vista": "fondo.vista",
          "vista-alterno": "fondo.vista-alterno", "boton": "fondo.boton", "texto": "texto.normal",
          "texto-secundario": "texto.secundario", "texto-inactivo": "texto.inactivo", "borde": "borde.separador",
          "borde-sutil": "borde.sutil", "acento": "acento.base", "acento-hover": "hover", "sobre-acento": "texto.sobre-acento",
          "seleccion-fondo": "seleccion.fondo", "seleccion-texto": "seleccion.texto", "foco": "foco", "enlace": "enlace",
          "tooltip-fondo": "fondo.tooltip", "tooltip-texto": "texto.tooltip"}
# la pestaña activa de la barra lateral: en el claro, el blanco de la vista sobre el gris de la ventana; en el oscuro,
# el gris de los botones (la vista es más oscura que la ventana y la pestaña se hundiría)
PESTANA = {"claro": "fondo.vista", "oscuro": "fondo.boton"}

# variable de Zen o de Firefox → variable de Lliphi (en `:root` y en los dos fondos que Zen escribe en línea)
ZEN = {
    "--zen-primary-color": "acento",
    "--zen-branding-paper": "vista", "--zen-branding-dark": "vista",
    "--zen-colors-primary": "ventana-alterno", "--zen-colors-secondary": "boton", "--zen-colors-tertiary": "vista",
    "--zen-colors-hover-bg": "ventana-alterno", "--zen-colors-primary-foreground": "texto",
    "--zen-colors-border": "borde", "--zen-colors-border-contrast": "borde-sutil", "--zen-colors-input-bg": "vista",
    "--zen-dialog-background": "vista", "--zen-urlbar-background": "vista",
    "--zen-main-browser-background": "ventana", "--zen-main-browser-background-toolbar": "ventana",
    "--zen-main-browser-background-old": "ventana", "--zen-main-browser-background-toolbar-old": "ventana",
    "--zen-themed-toolbar-bg-transparent": "ventana",
    "--zen-toolbar-element-bg": "ventana-alterno", "--zen-toolbar-element-bg-hover": "boton",
    "--zen-sidebar-themed-icon-fill": "texto-secundario", "--zen-sidebar-notification-bg": "vista",
    "--toolbox-textcolor": "texto", "--toolbox-textcolor-inactive": "texto-secundario", "--toolbar-color": "texto",
    "--toolbar-field-color": "texto", "--toolbar-field-background-color": "vista",
    "--toolbar-field-focus-background-color": "vista", "--toolbar-field-focus-border-color": "foco",
    "--toolbarbutton-background-color-hover": "ventana-alterno", "--toolbarbutton-background-color-active": "boton",
    "--tab-background-color-selected": "pestana", "--tab-text-color-selected": "texto",
    "--tab-background-color-hover": "ventana-alterno",
    "--arrowpanel-background": "vista", "--arrowpanel-color": "texto", "--arrowpanel-border-color": "borde",
    "--panel-background-color": "vista", "--panel-text-color": "texto", "--panel-border-color": "borde",
    "--panel-separator-color": "borde",
    "--urlbarView-highlight-background": "seleccion-fondo", "--urlbarView-highlight-color": "seleccion-texto",
    "--urlbarView-hover-background": "ventana-alterno",
    "--focus-outline-color": "foco", "--link-color": "enlace",
    "--color-accent-primary": "acento", "--color-accent-primary-hover": "acento-hover",
    "--button-background-color-primary": "acento", "--button-primary-hover-bgcolor": "acento-hover",
    "--button-primary-color": "sobre-acento", "--button-text-color-primary": "sobre-acento",
}
# los elementos que reciben las variables: la raíz, los dos fondos con estilos en línea de Zen y los que redefinen
# alguna de la tabla en las hojas de Zen 1.24 y Firefox 159 (el espacio de trabajo da su propia pestaña activa; los
# menús y paneles, sus variables de panel). Las ventanas privadas conservan el aspecto de Zen, para que se distingan
RAIZ_ZEN = ":root:not([zen-private-window='true'])"
INTERIORES = ("#zen-browser-background", "#zen-toolbar-background", "zen-workspace", ".zen-library-space",
              "#tabbrowser-tabs", "#tabbrowser-arrowscrollbox-periphery", ".tabbrowser-tab", "panel", "menupopup",
              "#ctrlTab-panel", "#confirmation-hint")
ELEMENTOS = f"{RAIZ_ZEN}, {RAIZ_ZEN} :is({', '.join(INTERIORES)})"
# los que llevan `color-scheme`, para que lo que Zen y Firefox pintan con `light-dark()` siga a la misma variante
# (el degradado de un espacio de trabajo puede forzar el contrario en `#browser`: zen-should-be-dark-mode)
ESQUEMA = "#main-window, #main-window #browser, panel, menupopup, #tabbrowser-tabpanels browser[type='content']"


def zen_variables(tokens: dict, variante: str) -> dict[str, str]:
    """Variable de Lliphi (`--lliphi-*`) → hex de la variante."""
    s = semanticos(tokens, variante)
    v = {f"--lliphi-{k}": s[sem] for k, sem in LLIPHI.items()}
    v["--lliphi-pestana"] = s[PESTANA[variante]]
    return v


def familia(fuentes: list[str]) -> str:
    return ", ".join(f if f in ("sans-serif", "serif", "monospace") else f'"{f}"' for f in fuentes)


def bloque(selector: str, valores: dict[str, str], sangria: str = "") -> str:
    return (f"{sangria}{selector} {{\n" + "".join(f"{sangria}  {k}: {v} !important;\n" for k, v in valores.items())
            + f"{sangria}}}\n")


def texto_userchrome(tokens: dict, marca: dict) -> str:
    claro, oscuro = marca["nombre_esquema"]["claro"], marca["nombre_esquema"]["oscuro"]
    partes = [f"/* {marca['nombre']} para Zen Browser: {claro} y {oscuro}, según el modo del sistema.\n"
              f"   GENERADO por herramientas/generar.py (complementos/navegadores, {marca['nombre']} {VERSION}) desde tokens/; no editar.\n"
              f"   {marca['repositorio']} · código {marca['licencia_codigo']}, colores {marca['licencia_activos']} */\n",
              f"\n/* {claro} */\n", bloque(":root", zen_variables(tokens, "claro")),
              bloque(ESQUEMA, {"color-scheme": "light"}), "\n@media (prefers-color-scheme: dark) {\n",
              f"  /* {oscuro} */\n", bloque(":root", zen_variables(tokens, "oscuro"), "  "),
              bloque(ESQUEMA, {"color-scheme": "dark"}, "  "), "}\n",
              "\n/* Zen y Firefox sobre las variables de Lliphi (el degradado del espacio de trabajo queda en el gris de la ventana) */\n",
              bloque(ELEMENTOS, {k: f"var(--lliphi-{v})" for k, v in ZEN.items()}),
              "\n/* Inter en la interfaz */\n",
              bloque(":root", {"font-family": familia(tokens["tipografia"]["interfaz"]["$value"])}),
              "\n/* la selección de texto y las etiquetas emergentes */\n",
              bloque("::selection", {"background-color": "var(--lliphi-seleccion-fondo)", "color": "var(--lliphi-seleccion-texto)"}),
              bloque("tooltip", {"background-color": "var(--lliphi-tooltip-fondo)", "color": "var(--lliphi-tooltip-texto)",
                                 "border-color": "var(--lliphi-tooltip-fondo)"})]
    return "".join(partes)


# preferencia de Zen → valor (el `user.js` se aplica en cada arranque)
PREFERENCIAS = {"toolkit.legacyUserProfileCustomizations.stylesheets": True,   # sin esto Zen no carga userChrome.css
                "zen.view.window.scheme": 2}                                      # 0 oscuro, 1 claro, 2 el del sistema


def texto_userjs(marca: dict) -> str:
    lineas = [f"// {marca['nombre']} para Zen Browser: carga userChrome.css y sigue el modo claro u oscuro del sistema.",
              f"// GENERADO por herramientas/generar.py (complementos/navegadores, {marca['nombre']} {VERSION}); no editar."]
    lineas += [f"user_pref({json.dumps(k)}, {json.dumps(v)});" for k, v in PREFERENCIAS.items()]
    return "\n".join(lineas) + "\n"


# ---------------------------------------------------------------- Chrome

# color de un tema de Chrome → semántico. La barra de herramientas es también la pestaña activa: el color de la vista,
# para que la pestaña se funda con la página; la franja de pestañas, el de la ventana (como las barras de Plasma)
CHROME = {"frame": "fondo.ventana", "frame_inactive": "fondo.ventana-alterno",
          "background_tab": "fondo.ventana", "background_tab_inactive": "fondo.ventana-alterno",
          "toolbar": "fondo.vista", "tab_text": "texto.normal", "tab_background_text": "texto.secundario",
          "tab_background_text_inactive": "texto.secundario", "toolbar_text": "texto.normal", "bookmark_text": "texto.normal",
          "toolbar_button_icon": "texto.secundario", "omnibox_background": "fondo.ventana", "omnibox_text": "texto.normal",
          "ntp_background": "fondo.vista", "ntp_text": "texto.normal", "ntp_link": "enlace", "ntp_header": "fondo.ventana"}
# texto de Chrome → fondo sobre el que se lee (para la prueba de contraste)
CHROME_PARES = {"tab_text": "toolbar", "toolbar_text": "toolbar", "bookmark_text": "toolbar",
                "tab_background_text": "background_tab", "tab_background_text_inactive": "background_tab_inactive",
                "omnibox_text": "omnibox_background", "ntp_text": "ntp_background", "ntp_link": "ntp_background"}


def carpeta_chrome(marca: dict, variante: str) -> str:
    return f"{marca['id']}-{variante}"


def chrome_colores(tokens: dict, variante: str) -> dict[str, str]:
    """Color de Chrome → hex de la variante."""
    s = semanticos(tokens, variante)
    return {k: s[sem] for k, sem in CHROME.items()}


def terna(hex6: str) -> list[int]:
    h = hex6.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def manifiesto_chrome(tokens: dict, marca: dict, variante: str) -> dict:
    nombre = marca["nombre_esquema"][variante]
    return {"manifest_version": 3, "name": nombre, "version": VERSION,
            "description": f"{nombre}: tema de {marca['nombre']} para Chrome, GENERADO desde sus tokens ({marca['repositorio']}).",
            "homepage_url": marca["repositorio"],
            "theme": {"colors": {k: terna(h) for k, h in chrome_colores(tokens, variante).items()}}}


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / "zen" / "userChrome.css", texto_userchrome(tokens, marca), hechos)
    escribir(destino / "zen" / "user.js", texto_userjs(marca), hechos)
    for variante in ("claro", "oscuro"):
        escribir(destino / "chrome" / carpeta_chrome(marca, variante) / "manifest.json",
                 json.dumps(manifiesto_chrome(tokens, marca, variante), indent=2, ensure_ascii=False) + "\n", hechos)
    return hechos
