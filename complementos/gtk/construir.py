"""Colores de Lliphi para las aplicaciones GTK 3 y GTK 4 (incluido libadwaita) sobre lo que ya pone KDE (decisiones 4.37).

En Plasma, `kde-gtk-config` deja las aplicaciones GTK en el tema Breeze y escribe en `~/.config/gtk-{3,4}.0/colors.css`
los colores del esquema de KDE con el sufijo `_breeze` (`@define-color theme_bg_color_breeze …`), que Breeze lee; en
cada cambio de esquema lo reescribe y añade `@import 'colors.css';` a `gtk.css` sin tocar lo demás. Pero el esquema de
Lliphi es la línea base de WhiteSur (decisiones 4.4: grises #363636…), mientras que las aplicaciones Qt se ven con los
neutros de los tokens, que pone Kvantum (#1b1c1e…). Este complemento no cambia de tema GTK: añade una hoja propia que
se importa después de `colors.css` y redefine esos mismos colores desde los tokens, como Kvantum.

- `gtk-3.0/lliphi-<variante>.css`: los colores `_breeze` de Breeze (GTK 3 no tiene consultas de medios, así que va
  uno por variante; `gtk.css` importa el de la variante y `fondo-variante` cambia esa línea al cambiar de variante) y la
  caja de herramientas flotante de Xournal++ (`#floatingToolbox`, `#pdfFloatingToolGrid`), que Xournal++ pinta en blanco
  con su propia hoja.
- `gtk-4.0/lliphi.css`: las dos variantes en un solo archivo, con `@media (prefers-color-scheme: dark)`, que GTK 4.20+
  resuelve con la preferencia `color-scheme` del portal (la pone KDE según el esquema). Lleva los colores con nombre de
  libadwaita (`window_bg_color`, `accent_bg_color`…; libadwaita 1.9 los define igual, dentro de la misma consulta) y
  las variables CSS que los reflejan (`--accent-bg-color`…), porque el libadwaita de Ubuntu fija `--accent-bg-color`
  con un valor directo; y los `_breeze` de Breeze para GTK 4 sin libadwaita.

Ningún hex se escribe aquí: los derivados (selección sin foco, bordes de etiqueta, estados insensibles) se escriben
como `mix()` de GTK sobre dos colores de los tokens. `resueltos()` da los mismos colores ya mezclados, para las
pruebas de contraste.
"""
from __future__ import annotations

from pathlib import Path

from nucleo import escribir, semanticos

CABECERA = "/* GENERADO por herramientas/generar.py desde tokens/ (complementos/gtk); no editar */\n"

# Un color es un token semántico ("fondo.ventana"), una mezcla ("mix", a, b, f): a·(1−f) + b·f, como mix() de GTK, o
# un diccionario {"claro": …, "oscuro": …} de los anteriores. Los alias de POR_VARIANTE nombran los que se repiten.
POR_VARIANTE = {
    # etiquetas: en el claro, claras como las de Kvantum (decisiones 4.34); en el oscuro, las del esquema
    "etiqueta.fondo": {"claro": "fondo.ventana", "oscuro": "fondo.tooltip"},
    "etiqueta.texto": {"claro": "texto.normal", "oscuro": "texto.tooltip"},
    # tarjetas y menús emergentes: blancos en el claro, un escalón sobre la ventana en el oscuro
    "superficie": {"claro": "fondo.vista", "oscuro": "fondo.ventana-alterno"},
    # fondo de un botón destructivo con texto blanco: el estado.error del oscuro es un rojo claro, para texto (decisiones 5.1)
    "peligro.fondo": {"claro": "estado.error", "oscuro": "acento.base"},
    # texto sobre el éxito y la advertencia: blanco sobre los del claro, el fondo oscuro sobre los del oscuro
    "sobre-estado": {"claro": "texto.sobre-acento", "oscuro": "fondo.vista"},
}

# la fila elegida de una ventana sin foco, con seleccion.texto encima: en el oscuro, el rojo a media luz; en el claro, el
# azul entero (a media luz con el fondo claro, el texto blanco no se leía: comprobado en pantalla)
SIN_FOCO = {"claro": "seleccion.fondo", "oscuro": ("mix", "seleccion.fondo", "fondo.vista", 0.5)}

BREEZE = {  # nombre de color de Breeze (sin el sufijo _breeze) → color de Lliphi; la lista es la de kde-gtk-config
    "theme_fg_color": "texto.normal", "theme_text_color": "texto.normal", "theme_bg_color": "fondo.ventana",
    "theme_base_color": "fondo.vista", "content_view_bg": "fondo.vista",
    "theme_view_hover_decoration_color": "hover", "theme_view_active_decoration_color": "foco",
    "theme_hovering_selected_bg_color": "hover",
    "theme_selected_bg_color": "seleccion.fondo", "theme_selected_fg_color": "seleccion.texto",
    "borders": "borde.separador", "unfocused_borders": "borde.separador",
    "insensitive_borders": "borde.sutil", "unfocused_insensitive_borders": "borde.sutil",
    "insensitive_bg_color": "fondo.ventana", "insensitive_fg_color": "texto.inactivo",
    "insensitive_base_color": "fondo.vista-alterno", "insensitive_base_fg_color": "texto.inactivo",
    "insensitive_selected_bg_color": "fondo.ventana-alterno", "insensitive_selected_fg_color": "texto.inactivo",
    "insensitive_unfocused_bg_color": "fondo.ventana", "insensitive_unfocused_fg_color": "texto.inactivo",
    "insensitive_unfocused_selected_bg_color": "fondo.ventana-alterno", "insensitive_unfocused_selected_fg_color": "texto.inactivo",
    "link_color": "enlace", "link_visited_color": "visitado",
    "error_color": "estado.error", "error_color_backdrop": "estado.error",
    "error_color_insensitive": ("mix", "estado.error", "fondo.ventana", 0.5),
    "error_color_insensitive_backdrop": ("mix", "estado.error", "fondo.ventana", 0.5),
    "success_color": "estado.exito", "success_color_backdrop": "estado.exito",
    "success_color_insensitive": ("mix", "estado.exito", "fondo.ventana", 0.5),
    "success_color_insensitive_backdrop": ("mix", "estado.exito", "fondo.ventana", 0.5),
    "warning_color": "estado.advertencia", "warning_color_backdrop": "estado.advertencia",
    "warning_color_insensitive": ("mix", "estado.advertencia", "fondo.ventana", 0.5),
    "warning_color_insensitive_backdrop": ("mix", "estado.advertencia", "fondo.ventana", 0.5),
    # botones
    "theme_button_background_normal": "fondo.boton", "theme_button_background_backdrop": "fondo.boton",
    "theme_button_background_insensitive": "fondo.ventana-alterno", "theme_button_background_backdrop_insensitive": "fondo.ventana-alterno",
    "theme_button_decoration_hover": "hover", "theme_button_decoration_hover_backdrop": "hover",
    "theme_button_decoration_focus": "foco", "theme_button_decoration_focus_backdrop": "foco",
    "theme_button_decoration_hover_insensitive": ("mix", "hover", "fondo.ventana", 0.5),
    "theme_button_decoration_hover_backdrop_insensitive": ("mix", "hover", "fondo.ventana", 0.5),
    "theme_button_decoration_focus_insensitive": ("mix", "foco", "fondo.ventana", 0.5),
    "theme_button_decoration_focus_backdrop_insensitive": ("mix", "foco", "fondo.ventana", 0.5),
    "theme_button_foreground_normal": "texto.normal", "theme_button_foreground_backdrop": "texto.normal",
    "theme_button_foreground_insensitive": "texto.inactivo", "theme_button_foreground_backdrop_insensitive": "texto.inactivo",
    "theme_button_foreground_active": "seleccion.texto", "theme_button_foreground_active_backdrop": "seleccion.texto",
    "theme_button_foreground_active_insensitive": "texto.inactivo", "theme_button_foreground_active_backdrop_insensitive": "texto.inactivo",
    # barra de título (CSD) y cabecera: el color de la ventana, una sola banda con la barra de herramientas (4.18)
    "theme_titlebar_background": "fondo.ventana", "theme_titlebar_background_light": "fondo.ventana",
    "theme_titlebar_background_backdrop": "fondo.ventana", "theme_titlebar_foreground": "texto.normal",
    "theme_titlebar_foreground_backdrop": "texto.inactivo", "theme_titlebar_foreground_insensitive": "texto.inactivo",
    "theme_titlebar_foreground_insensitive_backdrop": "texto.inactivo",
    "theme_header_background": "fondo.ventana", "theme_header_background_light": "fondo.ventana",
    "theme_header_background_backdrop": "fondo.ventana", "theme_header_foreground": "texto.normal",
    "theme_header_foreground_backdrop": "texto.inactivo", "theme_header_foreground_insensitive": "texto.inactivo",
    "theme_header_foreground_insensitive_backdrop": "texto.inactivo",
    # ventana sin foco
    "theme_unfocused_fg_color": "texto.normal", "theme_unfocused_text_color": "texto.normal",
    "theme_unfocused_bg_color": "fondo.ventana", "theme_unfocused_base_color": "fondo.vista",
    "theme_unfocused_selected_bg_color": SIN_FOCO, "theme_unfocused_selected_bg_color_alt": SIN_FOCO,
    "theme_unfocused_selected_fg_color": "seleccion.texto",
    "theme_unfocused_view_bg_color": "fondo.vista-alterno", "theme_unfocused_view_text_color": "texto.inactivo",
    # etiquetas emergentes
    "tooltip_background": "etiqueta.fondo", "tooltip_text": "etiqueta.texto",
    "tooltip_border": ("mix", "etiqueta.fondo", "etiqueta.texto", 0.2),
}

ADWAITA = {  # colores con nombre de libadwaita 1.9 → color de Lliphi (su variable CSS es el nombre con guiones)
    "accent_bg_color": "acento.base", "accent_fg_color": "texto.sobre-acento", "accent_color": "acento.texto",
    "destructive_bg_color": "peligro.fondo", "destructive_fg_color": "texto.sobre-acento", "destructive_color": "estado.error",
    "error_bg_color": "peligro.fondo", "error_fg_color": "texto.sobre-acento", "error_color": "estado.error",
    "success_bg_color": "estado.exito", "success_fg_color": "sobre-estado", "success_color": "estado.exito",
    "warning_bg_color": "estado.advertencia", "warning_fg_color": "sobre-estado", "warning_color": "estado.advertencia",
    "window_bg_color": "fondo.ventana", "window_fg_color": "texto.normal",
    "view_bg_color": "fondo.vista", "view_fg_color": "texto.normal",
    "headerbar_bg_color": "fondo.ventana", "headerbar_fg_color": "texto.normal", "headerbar_backdrop_color": "fondo.ventana",
    "headerbar_border_color": "texto.normal",
    "sidebar_bg_color": "fondo.ventana-alterno", "sidebar_fg_color": "texto.normal", "sidebar_backdrop_color": "fondo.ventana",
    "sidebar_border_color": "borde.separador",
    "secondary_sidebar_bg_color": "fondo.ventana", "secondary_sidebar_fg_color": "texto.normal",
    "secondary_sidebar_backdrop_color": "fondo.ventana", "secondary_sidebar_border_color": "borde.separador",
    "card_bg_color": "superficie", "card_fg_color": "texto.normal",
    "dialog_bg_color": "fondo.ventana", "dialog_fg_color": "texto.normal",
    "popover_bg_color": "superficie", "popover_fg_color": "texto.normal",
    "thumbnail_bg_color": "superficie", "thumbnail_fg_color": "texto.normal",
}

# pares (texto, fondo) que deben leerse (≥ 4,5:1); los prueba test_gtk_contraste
PARES_BREEZE = (("theme_fg_color", "theme_bg_color"), ("theme_text_color", "theme_base_color"),
                ("theme_selected_fg_color", "theme_selected_bg_color"), ("theme_button_foreground_normal", "theme_button_background_normal"),
                ("theme_titlebar_foreground", "theme_titlebar_background"), ("theme_unfocused_selected_fg_color", "theme_unfocused_selected_bg_color"),
                ("tooltip_text", "tooltip_background"), ("link_color", "theme_base_color"))
PARES_ADWAITA = (("window_fg_color", "window_bg_color"), ("view_fg_color", "view_bg_color"), ("accent_fg_color", "accent_bg_color"),
                 ("destructive_fg_color", "destructive_bg_color"), ("success_fg_color", "success_bg_color"),
                 ("warning_fg_color", "warning_bg_color"), ("headerbar_fg_color", "headerbar_bg_color"),
                 ("sidebar_fg_color", "sidebar_bg_color"), ("card_fg_color", "card_bg_color"), ("popover_fg_color", "popover_bg_color"),
                 ("accent_color", "view_bg_color"), ("error_color", "view_bg_color"))


def _token(s: dict[str, str], variante: str, clave: str) -> str:
    return s[POR_VARIANTE[clave][variante]] if clave in POR_VARIANTE else s[clave]


def _forma(valor, variante: str):
    """El color de una variante: un token (alias incluidos) o una mezcla."""
    return valor[variante] if isinstance(valor, dict) else valor


def css_color(s: dict[str, str], variante: str, valor) -> str:
    """El valor CSS de un color: el hex del token, o `mix(#a, #b, f)` (GTK 3 y 4)."""
    valor = _forma(valor, variante)
    if isinstance(valor, tuple):
        _, a, b, f = valor
        return f"mix({_token(s, variante, a)}, {_token(s, variante, b)}, {f})"
    return _token(s, variante, valor)


def mezclar(a: str, b: str, f: float) -> str:
    """Lo que calcula `mix()` de GTK: a·(1−f) + b·f por canal, en sRGB."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * (1 - f) + y * f):02x}" for x, y in zip(ca, cb))


def resueltos(tokens: dict, variante: str, tabla: dict) -> dict[str, str]:
    """{nombre: hex} con las mezclas ya calculadas (para las pruebas)."""
    s = semanticos(tokens, variante)
    salida = {}
    for nombre, valor in tabla.items():
        valor = _forma(valor, variante)
        if isinstance(valor, tuple):
            _, a, b, f = valor
            salida[nombre] = mezclar(_token(s, variante, a), _token(s, variante, b), f)
        else:
            salida[nombre] = _token(s, variante, valor)
    return salida


def definiciones(tokens: dict, variante: str, tabla: dict, sufijo: str = "", sangria: str = "") -> list[str]:
    s = semanticos(tokens, variante)
    return [f"{sangria}@define-color {n}{sufijo} {css_color(s, variante, v)};" for n, v in tabla.items()]


def variables(tokens: dict, variante: str, tabla: dict, sangria: str = "") -> list[str]:
    """`:root { --accent-bg-color: …; }`: libadwaita ≥ 1.6 lee las variables; el de Ubuntu fija algunas sin pasar por el nombre."""
    s = semanticos(tokens, variante)
    cuerpo = " ".join(f"--{n.replace('_', '-')}: {css_color(s, variante, v)};" for n, v in tabla.items())
    return [f"{sangria}:root {{ {cuerpo} }}"]


def xournalpp(tokens: dict, variante: str) -> list[str]:
    """La caja de herramientas flotante de Xournal++ (su hoja la pinta en blanco, o en gris si está en modo oscuro)."""
    s = semanticos(tokens, variante)
    return [
        "/* Xournal++: caja de herramientas flotante (su xournalpp.css la pinta en blanco; window.darkMode, en gris) */",
        "#floatingToolbox > box, #pdfFloatingToolGrid, window.darkMode #floatingToolbox > box, window.darkMode #pdfFloatingToolGrid {",
        f"  background-color: {s['fondo.ventana']}; box-shadow: 0 0 3px alpha({s['fondo.complementario']}, 0.4); }}",
        "#floatingToolbox button, #pdfFloatingToolGrid button, window.darkMode #floatingToolbox button, window.darkMode #pdfFloatingToolGrid button {",
        f"  background: {s['fondo.boton']}; color: {s['texto.normal']}; border: none; }}",
        "#floatingToolbox button:checked, window.darkMode #floatingToolbox button:checked {",
        f"  background: {s['seleccion.fondo']}; color: {s['seleccion.texto']}; border-color: {s['foco']}; box-shadow: none; }}",
    ]


def texto_gtk3(tokens: dict, marca: dict, variante: str) -> str:
    lineas = [CABECERA.rstrip("\n"),
              f"/* {marca['nombre_esquema'][variante]} para GTK 3 con el tema Breeze: se importa desde gtk.css después de colors.css */",
              "/* (kde-gtk-config); los colores _breeze de aquí mandan sobre los del esquema de KDE. */", ""]
    lineas += definiciones(tokens, variante, BREEZE, "_breeze")
    lineas += [""] + xournalpp(tokens, variante)
    return "\n".join(lineas) + "\n"


def texto_gtk4(tokens: dict, marca: dict) -> str:
    lineas = [CABECERA.rstrip("\n"),
              f"/* {marca['nombre_esquema']['claro']} y {marca['nombre_esquema']['oscuro']} para GTK 4 y libadwaita: se importa desde gtk.css. */",
              "/* La variante la decide la preferencia color-scheme del portal (KDE la pone según el esquema). */", "",
              "/* libadwaita: colores con nombre y sus variables */"]
    lineas += definiciones(tokens, "claro", ADWAITA) + variables(tokens, "claro", ADWAITA)
    lineas += ["@media (prefers-color-scheme: dark) {"] + definiciones(tokens, "oscuro", ADWAITA, sangria="  ")
    lineas += variables(tokens, "oscuro", ADWAITA, sangria="  ") + ["}", "", "/* Breeze para GTK 4 (aplicaciones sin libadwaita) */"]
    lineas += definiciones(tokens, "claro", BREEZE, "_breeze")
    lineas += ["@media (prefers-color-scheme: dark) {"] + definiciones(tokens, "oscuro", BREEZE, "_breeze", sangria="  ") + ["}"]
    return "\n".join(lineas) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for v in ("claro", "oscuro"):
        escribir(destino / "gtk-3.0" / f"{marca['id']}-{v}.css", texto_gtk3(tokens, marca, v), hechos)
    escribir(destino / "gtk-4.0" / f"{marca['id']}.css", texto_gtk4(tokens, marca), hechos)
    return hechos
