"""DuckDuckGo: el estilo redefine las variables de sus sistemas de diseño; aparte, sus ajustes con los colores.

La página de resultados y la de inicio pintan casi todo con variables de tres generaciones de su sistema de diseño:
`--theme-col-*` (fondo de la página, cabecera, buscador, títulos, fragmentos, URL, tarjetas, botones), `--sds-color-*`
(menús de los resultados, enlaces secundarios) y `--ds-*` (pestañas, botones de la marca, Duck.ai), que DuckDuckGo
define en `:root` y redefine en `html.dark-bg`, `html.set-theme--dark`… según su tema; el estilo las redefine en
`:root` con `!important`. Su tema oscuro pinta además el fondo de la página y el de la cabecera con un gris fijo: dos
reglas los devuelven a sus variables. La variante sigue a `prefers-color-scheme`, igual que el tema «Predeterminado»
de DuckDuckGo (sin `kae`), que es el que conviene dejar para que lo que no va por variables siga al mismo modo.

**Ajustes sin extensión.** DuckDuckGo guarda su apariencia como parámetros de URL o en su nube (`kae` tema, `k7`
fondo, `kj` cabecera, `k8` texto, `k9` enlaces, `kaa` visitados, `kx` URL, `k21` fondo de módulos y menús, `kt` y
`ka` las fuentes del texto y de los títulos; los colores en hex sin `#`). Un juego de ajustes fija los colores y no
sigue al sistema, así que hay uno por variante: `duckduckgo/ajustes.json` (parámetros, página de inicio, página de
ajustes ya rellena para guardarlos y plantilla de buscador) y `duckduckgo/marcadores.html`, para importarlos como
marcadores en Zen o en Chrome."""
from __future__ import annotations

import html
import json
from urllib.parse import urlencode

from nucleo import semanticos

NOMBRE = "DuckDuckGo"
DOMINIOS = ("duckduckgo.com",)
DESCRIPCION = "Lliphi Claro y Lliphi Oscuro en DuckDuckGo (variables --theme-col-*), según el modo claro u oscuro del sistema."
AMBITOS = {"claro": [("(prefers-color-scheme: light)", ":root")], "oscuro": [("(prefers-color-scheme: dark)", ":root")]}
FONDO = "--theme-col-bg-page"

# (texto, fondo) que deben llegar a 4,5:1; los botones deshabilitados quedan fuera (WCAG 1.4.3 los exime)
CONTRASTE = [("--theme-col-txt-snippet", "--theme-col-bg-page"), ("--theme-col-txt-title", "--theme-col-bg-page"),
             ("--theme-col-txt-title-visited", "--theme-col-bg-page"), ("--theme-col-txt-url", "--theme-col-bg-page"),
             ("--theme-col-txt-url-domain", "--theme-col-bg-page"), ("--theme-col-txt-header-link", "--theme-col-bg-header"),
             ("--theme-col-txt-search-input", "--theme-col-bg-search"), ("--theme-col-txt-card", "--theme-col-bg-card"),
             ("--theme-col-txt-card-body-light", "--theme-col-bg-card"), ("--theme-col-txt-card-aside", "--theme-col-bg-card"),
             ("--theme-col-txt-card-title", "--theme-col-bg-card-header"), ("--theme-col-txt-msg", "--theme-col-bg-page"),
             ("--theme-col-txt-button-primary", "--theme-col-bg-button-primary"),
             ("--theme-col-txt-button-primary", "--theme-col-bg-button-primary-hover"),
             ("--theme-col-txt-button-secondary", "--theme-col-bg-button-secondary"),
             ("--theme-col-txt-button-ghost", "--theme-col-bg-page"), ("--theme-col-txt-textarea", "--theme-col-bg-textarea"),
             ("--theme-col-txt-button-tab", "--theme-col-bg-button-tab"),
             ("--theme-col-txt-button-tab-active", "--theme-col-bg-button-tab-active"),
             ("--theme-col-txt-large-tab", "--theme-col-bg-page"), ("--theme-col-txt-qna-answer", "--theme-col-bg-page"),
             ("--sds-color-text-01", "--sds-color-background-01"), ("--sds-color-text-03", "--sds-color-background-container-01"),
             ("--sds-color-text-04", "--sds-color-background-01"), ("--sds-color-text-link-01", "--sds-color-background-01"),
             ("--sds-color-text-on-color", "--sds-color-background-accent-01"),
             ("--sds-color-text-on-color", "--sds-color-background-accent-01-state-01"),
             ("--ds-text-primary", "--ds-surface-canvas"), ("--ds-text-secondary", "--ds-surface-primary"),
             ("--ds-text-secondary", "--ds-surface-tertiary"), ("--ds-link-primary", "--ds-surface-canvas"),
             ("--ds-link-header", "--ds-surface-canvas"), ("--ds-link-secondary", "--ds-surface-canvas"),
             ("--ds-accent-primary-content-color", "--ds-accent-primary"),
             ("--ds-destructive-primary-content-color", "--ds-destructive-primary"),
             ("--ds-button-primary-branding-content-color", "--ds-button-primary-branding-background-color"),
             ("--ds-button-primary-branding-content-color", "--ds-button-primary-branding-hover-background-color")]

TRANSPARENTE = "00"


def variables(p) -> dict[str, str]:
    s = p.s
    v = {
        # página, cabecera y buscador
        "--theme-col-bg-page": s["fondo.vista"], "--theme-col-bg-page-transparent": p.alfa("fondo.vista", TRANSPARENTE),
        "--theme-col-bg-header": s["fondo.vista"], "--theme-col-bg-header-transparent": p.alfa("fondo.vista", TRANSPARENTE),
        "--theme-col-header-divider": s["borde.sutil"], "--theme-col-metabar-bg": s["fondo.vista"],
        "--theme-col-metabar-transparent": p.alfa("fondo.vista", TRANSPARENTE),
        "--theme-col-bg-search": s["fondo.ventana"], "--theme-col-txt-search-input": s["texto.normal"],
        "--theme-col-txt-search-button": s["texto.inactivo"], "--theme-col-bg-search-bar-separator": s["borde.separador"],
        "--theme-col-txt-header-link": s["texto.secundario"], "--theme-col-txt-header-link-hover": s["texto.normal"],
        "--theme-col-bg-page-alt-1": s["fondo.vista-alterno"], "--theme-col-bg-page-alt-2": s["fondo.ventana"],
        "--theme-col-bg-page-alt-3": s["fondo.ventana-alterno"],
        "--theme-col-bg-txt-1": s["texto.normal"], "--theme-col-bg-txt-2": s["texto.secundario"], "--theme-col-bg-txt-3": s["texto.inactivo"],
        # resultados: el título es un enlace (el acento de texto), el fragmento el texto normal, la URL el tenue
        "--result-item-bg": s["fondo.vista"], "--result-item-bg-transparent": p.alfa("fondo.vista", TRANSPARENTE),
        "--theme-col-txt-title": s["enlace"], "--theme-col-txt-title-visited": s["visitado"],
        "--theme-col-txt-snippet": s["texto.normal"], "--theme-col-txt-url": s["texto.inactivo"],
        "--theme-col-txt-url-domain": s["texto.secundario"], "--theme-col-txt-url-path": s["texto.inactivo"],
        "--theme-col-bg-result-item-divider": s["fondo.vista"],
        # superficies, separadores, tarjetas y módulos
        "--theme-col-bg-ui": s["fondo.ventana"], "--theme-col-bg-ui-transparent": p.alfa("fondo.ventana", TRANSPARENTE),
        "--theme-col-bg-ui-active": s["fondo.ventana-alterno"], "--theme-col-border-ui": s["borde.separador"],
        "--theme-col-separator": s["borde.sutil"], "--theme-col-separator-active": s["borde.separador"],
        "--theme-col-bg-card": s["fondo.ventana"], "--theme-col-bg-card-header": s["fondo.ventana-alterno"],
        "--theme-col-card-inner-border": s["borde.separador"], "--theme-col-border-card-nested": s["borde.separador"],
        "--theme-border-card-hover": s["borde.separador"],
        "--theme-col-txt-card": s["texto.normal"], "--theme-col-txt-card-title": s["texto.normal"],
        "--theme-col-txt-card-subtitle": s["texto.secundario"], "--theme-col-txt-card-body": s["texto.normal"],
        "--theme-col-txt-card-body-light": s["texto.secundario"], "--theme-col-txt-card-aside": s["texto.secundario"],
        "--theme-col-txt-tertiary": s["texto.inactivo"], "--theme-col-icon": s["texto.secundario"], "--theme-col-txt-msg": s["texto.secundario"],
        "--theme-col-bg-modal": s["fondo.ventana"], "--theme-col-bg-header-modal": s["fondo.ventana"],
        "--theme-col-modal-border": s["borde.separador"], "--theme-col-modal-header-border": s["borde.separador"],
        "--theme-col-bg-ext-dropdown": s["fondo.ventana"], "--theme-col-menu-promo-border": s["borde.sutil"],
        "--theme-col-bg-textarea": s["fondo.vista"], "--theme-col-txt-textarea": s["texto.normal"],
        "--theme-col-txt-textarea-placeholder": s["texto.inactivo"], "--theme-col-border-input-alternate": s["borde.separador"],
        "--theme-col-bg-pill": s["fondo.boton"], "--theme-col-txt-large-tab": s["texto.secundario"],
        "--theme-col-border-large-tab-selected": s["acento.base"], "--theme-col-txt-bar": s["texto.secundario"],
        "--theme-col-bg-bar": s["fondo.boton"], "--theme-col-image-preload": s["fondo.ventana"],
        "--theme-col-missing-asset": s["fondo.ventana-alterno"], "--theme-col-border-dashed": s["borde.separador"],
        "--sds-color-border-utility": s["borde.separador"], "--sds-color-border-utility-state-01": s["borde.separador"],
        "--sds-color-border-utility-state-02": s["texto.inactivo"],
        # botones: el principal en el acento; los demás en los grises de la ventana
        "--theme-col-bg-button-primary": s["acento.base"], "--theme-col-bg-button-primary-hover": p.relleno["acento-pasar"],
        "--theme-col-bg-button-primary-active": p.relleno["acento-pasar"], "--theme-col-bg-button-primary-disabled": s["fondo.boton"],
        "--theme-col-txt-button-primary": s["texto.sobre-acento"], "--theme-col-txt-button-primary-disabled": s["texto.inactivo"],
        "--theme-col-bg-button-secondary": s["fondo.boton"], "--theme-col-bg-button-secondary-hover": s["fondo.ventana-alterno"],
        "--theme-col-bg-button-secondary-active": s["borde.separador"], "--theme-col-bg-button-secondary-disabled": s["fondo.ventana"],
        "--theme-col-txt-button-secondary": s["texto.normal"], "--theme-col-txt-button-secondary-disabled": s["texto.inactivo"],
        "--theme-col-bg-button-tertiary-hover": s["fondo.ventana-alterno"], "--theme-col-bg-button-tertiary-active": s["fondo.boton"],
        "--theme-col-border-button-tertiary": s["borde.separador"], "--theme-col-border-button-tertiary-hover": s["texto.inactivo"],
        "--theme-col-border-button-tertiary-active": s["texto.secundario"], "--theme-col-border-button-tertiary-disabled": s["borde.sutil"],
        "--theme-col-txt-button-tertiary": s["texto.normal"], "--theme-col-txt-button-tertiary-disabled": s["texto.inactivo"],
        "--theme-col-bg-button-ghost-hover": s["fondo.ventana-alterno"], "--theme-col-bg-button-ghost-active": s["fondo.boton"],
        "--theme-col-txt-button-ghost": s["enlace"], "--theme-col-txt-button-ghost-hover": s["enlace"],
        "--theme-col-txt-button-ghost-active": s["enlace"], "--theme-col-txt-button-ghost-disabled": s["texto.inactivo"],
        "--theme-col-bg-button-ghostsecondary-hover": s["fondo.ventana-alterno"],
        "--theme-col-bg-button-ghostsecondary-active": s["fondo.boton"], "--theme-col-border-button-ghostsecondary": s["borde.separador"],
        "--theme-col-border-button-ghostsecondary-hover": s["borde.separador"],
        "--theme-col-border-button-ghostsecondary-active": s["texto.inactivo"], "--theme-col-txt-button-ghostsecondary": s["texto.secundario"],
        "--theme-col-bg-button-tab": s["fondo.boton"], "--theme-col-txt-button-tab": s["texto.normal"],
        "--theme-col-bg-button-tab-hover": s["fondo.ventana-alterno"], "--theme-col-bg-button-tab-active": s["texto.normal"],
        "--theme-col-txt-button-tab-active": s["fondo.vista"],
        "--theme-col-bg-expandcollapse": s["fondo.ventana"], "--theme-col-bg-expandcollapse-hover": s["fondo.ventana-alterno"],
        "--theme-col-txt-expandcollapse": s["texto.secundario"], "--theme-col-border-expandcollapse": s["borde.sutil"],
        "--theme-col-bg-button-expandcollapse": s["fondo.boton"], "--theme-col-bg-button-expandcollapse-hover": s["fondo.ventana-alterno"],
        "--theme-col-bg-button-expandcollapse-active": s["borde.separador"], "--theme-col-border-button-expandcollapse": s["fondo.boton"],
        "--theme-col-icon-button-expandcollapse": s["texto.normal"],
        # preguntas y respuestas, enlaces sueltos, estados y foco
        "--theme-col-txt-qna-answer": s["texto.normal"], "--theme-col-txt-qna-details": s["texto.inactivo"],
        "--theme-col-border-qna-list-sep": s["borde.sutil"], "--theme-col-bg-button-qna": s["fondo.boton"],
        "--theme-col-bg-button-qna-hover": s["fondo.ventana-alterno"], "--theme-col-border-button-qna": s["fondo.boton"],
        "--theme-col-border-button-qna-hover": s["borde.separador"], "--theme-col-icon-qna": s["texto.normal"],
        "--theme-col-about-link": s["enlace"], "--theme-col-module-link-new-ux": s["enlace"], "--theme-col-sports-team-link": s["enlace"],
        "--theme-col-success": s["estado.exito"], "--theme-col-error": s["estado.error"],
        "--theme-col-glow": p.alfa("acento.base", "33"), "--col-result-focus-outline": s["foco"],
        "--col-tooltip-bg": s["fondo.tooltip"],
    }
    # el sistema de diseño nuevo de DuckDuckGo (`--ds-*`): pestañas, enlaces de la cabecera, menús, avisos
    r = p.relleno
    v |= {
        "--ds-surface-canvas": s["fondo.vista"], "--ds-surface-primary": s["fondo.ventana"], "--ds-surface-secondary": s["fondo.ventana"],
        "--ds-surface-tertiary": s["fondo.ventana-alterno"], "--ds-surface-contrast": s["texto.normal"],
        "--ds-surface-decoration-primary": s["borde.sutil"], "--ds-surface-decoration-secondary": s["borde.separador"],
        "--ds-surface-decoration-tertiary": s["texto.inactivo"],
        "--ds-text-primary": s["texto.normal"], "--ds-text-secondary": s["texto.secundario"], "--ds-text-tertiary": s["texto.inactivo"],
        "--ds-icons-secondary": s["texto.secundario"],
        "--ds-container-primary-border-color": s["borde.sutil"], "--ds-container-secondary-background-color": s["fondo.vista-alterno"],
        "--ds-container-secondary-border-color": s["borde.sutil"], "--ds-container-tertiary-background-color": s["fondo.ventana"],
        "--ds-container-tertiary-border-color": s["borde.separador"],
        "--ds-control-primary-background-color": s["fondo.boton"], "--ds-control-primary-border-color": s["borde.separador"],
        "--ds-control-raised-primary-background-color": s["fondo.ventana"], "--ds-control-secondary-background-color": s["fondo.ventana-alterno"],
        "--ds-control-secondary-border-color": s["texto.inactivo"], "--ds-control-tertiary-background-color": s["borde.separador"],
        "--ds-control-tertiary-border-color": s["texto.secundario"], "--ds-control-subtle-primary-border-color": s["borde.sutil"],
        "--ds-control-subtle-secondary-border-color": s["borde.separador"], "--ds-control-subtle-tertiary-border-color": s["texto.inactivo"],
        "--ds-link-primary": s["enlace"], "--ds-link-header": s["enlace"], "--ds-link-primary-visited": s["visitado"],
        "--ds-link-secondary": s["texto.secundario"], "--ds-link-secondary-hover": s["texto.normal"],
        "--ds-accent-primary": s["acento.base"], "--ds-accent-secondary": s["acento.suave"], "--ds-accent-tertiary": s["acento.base"],
        "--ds-accent-primary-inverse": s["acento.base"], "--ds-accent-secondary-inverse": s["acento.base"],
        "--ds-accent-primary-text-color": s["enlace"], "--ds-accent-primary-content-color": s["texto.sobre-acento"],
        "--ds-accent-glow-primary": p.alfa("acento.base", "33"), "--ds-accent-glow-secondary": p.alfa("acento.base", "1f"),
        "--ds-accent-alt-glow-primary": p.alfa("acento.base", "33"), "--ds-accent-alt-glow-secondary": p.alfa("acento.base", "1f"),
        "--ds-destructive-primary": r["error"], "--ds-destructive-secondary": r["error"], "--ds-destructive-tertiary": r["error"],
        "--ds-destructive-primary-text-color": s["estado.error"], "--ds-destructive-primary-content-color": s["texto.sobre-acento"],
        "--ds-destructive-glow-primary": p.alfa("estado.error", "33"), "--ds-destructive-glow-secondary": p.alfa("estado.error", "1f"),
        "--ds-status-green": s["estado.exito"], "--ds-status-green-text": s["estado.exito"],
    }
    # el sistema de diseño intermedio (`--sds-color-*`): menús de los resultados, «Ver la lista completa», migas de Duck.ai
    v |= {
        "--sds-color-background-01": s["fondo.vista"], "--sds-color-background-02": s["fondo.ventana"],
        "--sds-color-background-03": s["fondo.ventana-alterno"], "--sds-color-background-container-01": s["fondo.ventana"],
        "--sds-color-background-container-02": s["fondo.boton"], "--sds-color-background-container-pre": s["fondo.vista-alterno"],
        "--sds-color-background-dark": s["fondo.complementario"], "--sds-color-background-disabled": s["fondo.boton"],
        "--sds-color-background-backdrop": p.alfa("fondo.complementario", "99"), "--sds-color-background-semi": p.alfa("fondo.complementario", "99"),
        "--sds-color-background-accent-01": s["acento.base"], "--sds-color-background-accent-01-state-01": r["acento-pasar"],
        "--sds-color-background-accent-01-alt": s["acento.base"], "--sds-color-background-accent-01-alt-state-01": r["acento-pasar"],
        "--sds-color-background-accent-01-alt-state-02": r["acento-pasar"], "--sds-color-background-accent-02": s["texto.normal"],
        "--sds-color-background-accent-01-transparency-01": p.alfa("acento.base", "26"),
        "--sds-color-background-accent-01-transparency-02": p.alfa("acento.base", "4d"),
        "--sds-color-background-support-accent-state-01": p.alfa("acento.base", "26"),
        "--sds-color-background-support-accent-state-02": p.alfa("acento.base", "4d"),
        "--sds-color-background-destructive": r["error"], "--sds-color-background-destructive-state-01": r["error"],
        "--sds-color-background-destructive-state-02": r["error"],
        "--sds-color-background-support-destructive-state-01": p.alfa("estado.error", "26"),
        "--sds-color-background-support-destructive-state-02": p.alfa("estado.error", "4d"),
        "--sds-color-background-utility": s["fondo.boton"], "--sds-color-background-utility-state-01": s["fondo.ventana-alterno"],
        "--sds-color-background-utility-state-02": s["borde.separador"], "--sds-color-background-utility-alt": s["fondo.ventana"],
        "--sds-color-background-utility-alt-state-01": s["fondo.ventana-alterno"],
        "--sds-color-background-support-utility-state-01": s["fondo.ventana-alterno"],
        "--sds-color-background-support-utility-state-02": s["fondo.boton"],
        "--sds-color-border-01": s["borde.sutil"], "--sds-color-border-accent-01": s["acento.base"],
        "--sds-color-border-destructive": r["error"], "--sds-color-border-disabled": s["borde.sutil"],
        "--sds-color-border-inner-divider": s["borde.sutil"],
        "--sds-color-text-01": s["texto.normal"], "--sds-color-text-02": s["texto.normal"], "--sds-color-text-03": s["texto.secundario"],
        "--sds-color-text-04": s["texto.inactivo"], "--sds-color-text-utility": s["texto.secundario"],
        "--sds-color-text-disabled": s["texto.inactivo"], "--sds-color-text-on-color": s["texto.sobre-acento"],
        "--sds-color-text-accent-01": s["enlace"], "--sds-color-text-accent-01-alt": s["enlace"],
        "--sds-color-text-accent-01-state-01": s["enlace"], "--sds-color-text-accent-01-state-02": s["enlace"],
        "--sds-color-text-accent-02": s["texto.normal"], "--sds-color-text-link-01": s["enlace"],
        "--sds-color-text-link-01-visited": s["visitado"], "--sds-color-text-link-02": s["texto.secundario"],
        "--sds-color-text-link-02-hover": s["texto.normal"], "--sds-color-text-destructive": s["estado.error"],
        "--sds-color-text-success": s["estado.exito"],
    }
    # los botones de la marca (amarillos en DuckDuckGo) son los principales: el acento
    for forzado in ("", "force-dark-"):
        v |= {f"--ds-button-primary-branding-{forzado}background-color": s["acento.base"],
              f"--ds-button-primary-branding-{forzado}hover-background-color": r["acento-pasar"],
              f"--ds-button-primary-branding-{forzado}active-background-color": r["acento-pasar"],
              f"--ds-button-primary-branding-{forzado}content-color": s["texto.sobre-acento"]}
    v["--ds-button-primary-branding-focus-ring-color"] = s["foco"]
    return v


def reglas(p) -> dict[str, dict[str, str]]:
    return {"::selection": {"background-color": p.s["seleccion.fondo"], "color": p.s["seleccion.texto"]},
            ":focus-visible": {"outline-color": p.s["foco"]}}


FUENTES_DS = ("--ds-font-family-product", "--ds-font-button-label-02-font-family", "--ds-font-button-label-03-font-family",
              "--ds-font-label-01-font-family", "--ds-font-title-05-font-family")


def comunes(fuentes: dict[str, str]) -> dict[str, dict[str, str]]:
    """Inter en el texto (las variables `--ds-font-*` y los elementos de texto, que la página antigua no pone en
    variables) y, sin colores propios, las superficies que el tema oscuro de DuckDuckGo pinta con un gris fijo: toman
    las variables de arriba."""
    return {":root": {k: fuentes["interfaz"] for k in FUENTES_DS},
            "body, input, textarea, button, select": {"font-family": fuentes["interfaz"]},
            "html, body, .site-wrapper, .region__body": {"background-color": "var(--theme-col-bg-page)"},
            ".header-wrap": {"background-color": "var(--theme-col-bg-header)"}}


# ---------------------------------------------------------------- ajustes de DuckDuckGo (sin extensión)

TEMA = {"claro": "-1", "oscuro": "d"}   # -1: el tema claro de siempre; d: oscuro
COLORES = {"k7": "fondo.vista", "kj": "fondo.vista", "k8": "texto.normal", "k9": "enlace", "kaa": "visitado",
           "kx": "texto.inactivo", "k21": "fondo.ventana"}
BASE = "https://duckduckgo.com/"


def parametros(tokens: dict, variante: str) -> dict[str, str]:
    s = semanticos(tokens, variante)
    fuente = tokens["tipografia"]["interfaz"]["$value"][0]
    return {"kae": TEMA[variante], **{k: s[c].lstrip("#") for k, c in COLORES.items()}, "kt": fuente, "ka": fuente}


def extras(tokens: dict, marca: dict) -> dict[str, str]:
    ajustes: dict[str, dict] = {}
    for variante in ("claro", "oscuro"):
        q = urlencode(parametros(tokens, variante))
        # «ajustes» abre la página de ajustes ya rellena: «Guardar y salir» los deja en las cookies (sin «#»: DuckDuckGo
        # pegaría el fragmento al último parámetro)
        ajustes[variante] = {"nombre": f"DuckDuckGo · {marca['nombre_esquema'][variante]}", "parametros": parametros(tokens, variante),
                             "inicio": f"{BASE}?{q}", "ajustes": f"{BASE}settings?{q}", "buscador": f"{BASE}?q=%s&{q}"}
    datos = {"$comment": "GENERADO por herramientas/generar.py (complementos/sitios-web) desde tokens/; no editar. "
                         "Ajustes de apariencia de DuckDuckGo con los colores de Lliphi, uno por variante.",
             "variantes": ajustes}
    marcadores = "".join(f'        <DT><A HREF="{html.escape(a["inicio"])}">{html.escape(a["nombre"])}</A>\n'
                         f'        <DT><A HREF="{html.escape(a["ajustes"])}">{html.escape("Guardar los ajustes: " + a["nombre"])}</A>\n'
                         for a in ajustes.values())
    pagina = ("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n"
              "<!-- GENERADO por herramientas/generar.py (complementos/sitios-web) desde tokens/; no editar. -->\n"
              '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
              "<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n"
              f"    <DT><H3>{html.escape(marca['nombre'])}</H3>\n    <DL><p>\n{marcadores}    </DL><p>\n</DL><p>\n")
    return {"duckduckgo/ajustes.json": json.dumps(datos, ensure_ascii=False, indent=2) + "\n", "duckduckgo/marcadores.html": pagina}
