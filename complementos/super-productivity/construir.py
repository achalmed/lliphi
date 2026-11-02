"""Tema de Super Productivity (≥ 18) desde los tokens: `lliphi.css` con Lliphi Claro y Lliphi Oscuro en un solo
archivo (decisiones 5.49).

Formato (comprobado el 2026-11-02 en el código de Super Productivity 18.10.0: `electron/main-window.ts`,
`src/app/core/theme/` y `src/styles/_css-variables.scss`). La aplicación acepta CSS propio por dos vías, y el mismo
archivo vale para las dos:

- `styles.css` en su carpeta de datos (`~/.config/superProductivity/`): al cargar la ventana lo inyecta con
  `webContents.insertCSS`. Es la que usa el instalador: un archivo que se copia y se retira, sin abrir la aplicación.
  Las hojas inyectadas así van **antes** que las de la aplicación en la cascada: a igual especificidad pierden.
- Un tema «de usuario» (Ajustes → General → «Instalar tema…»): lo valida (sin `url()`, `src()` ni `@import`), lo
  guarda en su IndexedDB y lo pone como un `<style>` al final de `<head>`; se llama como el archivo, «Lliphi».

Con «Modo oscuro: Sistema» (lo predeterminado) la aplicación pone la clase `isDarkTheme` en `<body>` según
`prefers-color-scheme`, que en Plasma da el portal (el esquema de color claro u oscuro): el tema sigue solo y en vivo a
la variante. Lo que define, en las capas de la aplicación y con un selector más específico que el suyo (por la vía de
`insertCSS`):

- Los primitivos de su «contrato de temas» (`--surface-0…4`, `--ink*`, `--separator`, `--divider`, `--scrim`,
  `--bg-overlay`) y los de la categoría B (tareas, notas, paneles, barras de desplazamiento, detalles), en
  `html body:not(.isDarkTheme)` y `html body.isDarkTheme`: el claro no puede ir en `body` a secas, porque ganaría a los
  alias de la aplicación (especificidad cero) también en el oscuro. Los fondos siguen a Plasma: la ventana para el
  fondo de la aplicación y la vista para las tareas y tarjetas en el claro; en el oscuro, la vista (lo más hondo) de
  fondo y la ventana alterna para las tarjetas, siempre más claras que el fondo.
- La escala de grises fija del oscuro (`--dark0…dark24`), que muchos componentes usan directamente, en los neutros
  oscuros de Lliphi.
- La paleta de Material (`--palette-primary|accent|warn-50…900`, `A100…A700` y sus contrastes, en sus tres formas
  `-no-rgb`, `-rgb` y la normal): la pone la aplicación en línea en `<html>` con el color del proyecto, de modo que
  aquí va en `:root` con `!important` (lo único que vence a un estilo en línea) y la del oscuro en
  `:root:has(> body.isDarkTheme)`. El primario y el acento son el acento de Lliphi, y la advertencia el error de los
  semánticos; la escala se mezcla en sRGB con el texto sobre el acento (hacia el claro) y el fondo complementario
  (hacia el oscuro), y el contraste de cada paso es el de esos dos que más contraste da.
- Los contenedores y textos de Angular Material que la aplicación deja fijos (`#424242`, `white`…): diálogos, menús,
  listas desplegables, calendarios, tarjetas, tablas, avisos y descripciones emergentes.
- Lo común, en `html:root`: JetBrains Mono para el código y los radios de Lliphi. La letra de la interfaz es la de la
  aplicación (Material la escribe literal, no en variables).

Ningún color se escribe aquí: los hexes salen de `tokens/tokens.json` y la prueba lo comprueba."""
from __future__ import annotations

from pathlib import Path

from nucleo import VERSION, escribir, semanticos

# `html` delante: un punto más de especificidad que la aplicación, que gana también desde `insertCSS`
SELECTOR = {"claro": "html body:not(.isDarkTheme)", "oscuro": "html body.isDarkTheme"}
COMUN = "html:root"
RAIZ_CSS = {"claro": ":root", "oscuro": ":root:has(> body.isDarkTheme)"}

# primitivos y categoría B de la aplicación → semántico de Lliphi, por variante
FONDOS = {
    "claro": {"--surface-0": "fondo.ventana-alterno", "--surface-1": "fondo.ventana", "--surface-2": "fondo.vista",
              "--surface-3": "fondo.vista", "--surface-4": "fondo.vista",
              "--bg-drag-col": "fondo.ventana-alterno", "--bg-slightly-lighter": "fondo.vista-alterno",
              "--bg-super-light": "fondo.vista", "--selected-task-bg-color": "fondo.vista",
              "--sub-task-c-bg-in-selected": "fondo.vista-alterno", "--standard-note-bg": "fondo.vista",
              "--standard-note-bg-hovered": "fondo.vista-alterno", "--task-detail-bg": "fondo.vista",
              "--task-detail-bg-hover": "fondo.vista-alterno", "--right-panel-bg-mobile": "fondo.vista",
              "--bottom-panel-bg": "fondo.vista", "--sidenav-hover-bg": "fondo.ventana-alterno"},
    "oscuro": {"--surface-0": "fondo.vista", "--surface-1": "fondo.vista", "--surface-2": "fondo.ventana-alterno",
               "--surface-3": "fondo.boton", "--surface-4": "fondo.tooltip",
               "--bg-drag-col": "fondo.ventana", "--bg-slightly-lighter": "fondo.ventana-alterno",
               "--bg-super-light": "borde.separador", "--selected-task-bg-color": "fondo.boton",
               "--task-c-selected-bg": "fondo.boton", "--sub-task-c-bg": "fondo.ventana-alterno",
               "--sub-task-c-bg-done": "fondo.ventana", "--task-c-bg-done": "fondo.ventana",
               "--sub-task-c-bg-in-selected": "fondo.boton", "--standard-note-bg": "fondo.ventana-alterno",
               "--standard-note-bg-hovered": "fondo.boton", "--task-detail-bg": "fondo.ventana-alterno",
               "--task-detail-bg-hover": "fondo.boton", "--schedule-event-bg-in-side-panel": "fondo.boton",
               "--bottom-panel-bg": "fondo.ventana", "--sidenav-hover-bg": "fondo.ventana-alterno"},
}
COMUNES = {"--ink-strong": "texto.normal", "--ink": "texto.normal", "--ink-muted": "texto.inactivo",
           "--text-color-less-intense": "texto.secundario", "--text-color-more-intense": "texto.normal",
           "--standard-note-fg": "texto.normal", "--task-detail-value-color": "texto.secundario",
           "--improvement-text": "texto.normal", "--improvement-button-text": "texto.normal",
           "--brand": "acento.texto", "--focus-ring": "foco",
           "--separator": "borde.separador", "--divider": "borde.separador", "--extra-border-color": "borde.sutil",
           "--grid-color": "borde.sutil", "--color-success": "estado.exito", "--color-warning": "estado.advertencia",
           "--color-danger": "estado.error", "--success-green": "estado.exito"}

# la escala gris fija del oscuro (`:root` de la aplicación) → neutro oscuro de Lliphi
GRISES = {"--dark0": "fondo.vista", "--dark0-5": "fondo.vista-alterno", "--dark1": "fondo.ventana",
          "--dark2": "fondo.ventana", "--dark3": "fondo.ventana-alterno", "--dark4": "fondo.ventana-alterno",
          "--dark4-5": "fondo.ventana-alterno", "--dark5": "fondo.ventana-alterno", "--dark6": "fondo.boton",
          "--dark8": "fondo.boton", "--dark10": "fondo.boton", "--dark12": "fondo.tooltip", "--dark16": "fondo.tooltip",
          "--dark24": "borde.separador"}

# contenedores y textos de Angular Material que la aplicación deja fijos → semántico de Lliphi
MATERIAL = {
    "fondo.vista": ("--mat-app-background-color", "--mat-sidenav-content-background-color"),
    "superficie-2": ("--mat-card-elevated-container-color", "--mat-card-filled-container-color",
                     "--mat-card-outlined-container-color", "--mat-expansion-container-background-color",
                     "--mat-table-background-color", "--mat-tree-container-background-color",
                     "--mat-paginator-container-background-color", "--mat-stepper-container-color",
                     "--mat-bottom-sheet-container-background-color", "--mat-sidenav-container-background-color",
                     "--mat-toolbar-container-background-color"),
    "superficie-3": ("--mat-dialog-container-color", "--mat-menu-container-color", "--mat-select-panel-background-color",
                     "--mat-autocomplete-background-color", "--mat-datepicker-calendar-container-background-color",
                     "--mat-timepicker-container-background-color"),
    "fondo.boton": ("--mat-button-filled-container-color", "--mat-button-protected-container-color",
                    "--mat-button-tonal-container-color", "--mat-button-toggle-background-color"),
    "campo": ("--mat-form-field-filled-container-color",),
    "texto.normal": ("--mat-app-text-color", "--mat-menu-item-label-text-color", "--mat-menu-item-icon-color",
                     "--mat-option-label-text-color", "--mat-optgroup-label-text-color",
                     "--mat-select-enabled-trigger-text-color", "--mat-form-field-filled-input-text-color",
                     "--mat-form-field-outlined-input-text-color", "--mat-list-list-item-label-text-color",
                     "--mat-expansion-header-text-color", "--mat-expansion-container-text-color",
                     "--mat-dialog-subhead-color", "--mat-checkbox-label-text-color", "--mat-slide-toggle-label-text-color",
                     "--mat-table-header-headline-color", "--mat-table-row-item-label-text-color",
                     "--mat-tree-node-text-color", "--mat-datepicker-calendar-date-text-color",
                     "--mat-datepicker-calendar-container-text-color", "--mat-bottom-sheet-container-text-color",
                     "--mat-sidenav-container-text-color", "--mat-sidenav-content-text-color",
                     "--mat-button-toggle-text-color"),
    "texto.secundario": ("--mat-dialog-supporting-text-color", "--mat-form-field-filled-label-text-color",
                         "--mat-form-field-outlined-label-text-color", "--mat-list-list-item-supporting-text-color",
                         "--mat-expansion-header-description-color", "--mat-expansion-header-indicator-color",
                         "--mat-select-enabled-arrow-color", "--mat-form-field-enabled-select-arrow-color",
                         "--mat-card-subtitle-text-color", "--mat-datepicker-calendar-header-text-color",
                         "--mat-datepicker-calendar-body-label-text-color", "--mat-datepicker-toggle-icon-color",
                         "--mat-list-list-item-leading-icon-color", "--mat-list-list-item-trailing-icon-color"),
    "texto.inactivo": ("--mat-select-placeholder-text-color", "--mat-form-field-filled-input-text-placeholder-color",
                       "--mat-form-field-outlined-input-text-placeholder-color"),
    "fondo.tooltip": ("--mat-tooltip-container-color", "--mat-snack-bar-container-color"),
    "texto.tooltip": ("--mat-tooltip-supporting-text-color", "--mat-snack-bar-supporting-text-color"),
}
SUPERFICIE = {"superficie-2": "--surface-2", "superficie-3": "--surface-3"}
# el campo de formulario relleno: en el claro, el gris de los botones sobre el diálogo blanco; en el oscuro, hundido
# (el diálogo ya es del gris de los botones)
CAMPO = {"claro": "fondo.boton", "oscuro": "fondo.ventana-alterno"}

# paso de la escala de Material → (hacia qué extremo, cuánto): «claro» mezcla con el texto sobre el acento, «oscuro»
# con el fondo complementario; 500 es el color mismo
PASOS = {"50": ("claro", 0.90), "100": ("claro", 0.76), "200": ("claro", 0.58), "300": ("claro", 0.38),
         "400": ("claro", 0.18), "500": ("claro", 0.0), "600": ("oscuro", 0.12), "700": ("oscuro", 0.24),
         "800": ("oscuro", 0.36), "900": ("oscuro", 0.48), "A100": ("claro", 0.62), "A200": ("claro", 0.36),
         "A400": ("claro", 0.10), "A700": ("oscuro", 0.20)}
PALETAS = {"primary": "acento.base", "accent": "acento.base", "warn": "estado.error"}


def mezclar(a: str, b: str, t: float) -> str:
    """`a` con una fracción `t` de `b`, en sRGB."""
    x = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    y = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(p + (q - p) * t):02x}" for p, q in zip(x, y))


def luminancia(hex6: str) -> float:
    c = [int(hex6[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def rgb(hex6: str) -> str:
    return ", ".join(str(int(hex6[i:i + 2], 16)) for i in (1, 3, 5))


def escala(tokens: dict, variante: str, base: str) -> dict[str, tuple[str, str]]:
    """Paso → (color, su contraste) de una paleta de Material que parte del semántico `base`."""
    s = semanticos(tokens, variante)
    extremos = {"claro": s["texto.sobre-acento"], "oscuro": s["fondo.complementario"]}
    salida = {}
    for paso, (hacia, t) in PASOS.items():
        color = mezclar(s[base], extremos[hacia], t)
        sobre = max(extremos.values(), key=lambda e: contraste(color, e))
        salida[paso] = (color, sobre)
    return salida


def paletas(tokens: dict, variante: str) -> dict[str, str]:
    """Variable de la paleta de Material → valor, para `:root` (sin el `!important`)."""
    v: dict[str, str] = {}
    for nombre, base in PALETAS.items():
        for paso, (color, sobre) in escala(tokens, variante, base).items():
            for prefijo, h in ((f"--palette-{nombre}-{paso}", color), (f"--palette-{nombre}-contrast-{paso}", sobre)):
                v[f"{prefijo}-no-rgb"] = rgb(h)
                v[f"{prefijo}-rgb"] = h
                v[prefijo] = h
    return v


def variables(tokens: dict, variante: str) -> dict[str, str]:
    """Variable de la aplicación → valor, para el bloque de `body` de una variante."""
    s = semanticos(tokens, variante)
    v = {k: s[sem] for k, sem in FONDOS[variante].items()}
    v |= {k: s[sem] for k, sem in COMUNES.items()}
    if variante == "oscuro":
        v |= {k: s[sem] for k, sem in GRISES.items()}
    v |= {"--ink-on-channel": rgb(s["texto.normal"]),
          "--scrim": f"rgba({rgb(s['fondo.complementario'])}, 0.6)",
          "--bg-overlay": f"rgba({rgb(v['--surface-1'])}, 0.8)",
          "--sun-yellow": s["estado.advertencia"],
          "--scrollbar-thumb": f"rgba({rgb(s['texto.inactivo'])}, 0.4)",
          "--scrollbar-thumb-hover": f"rgba({rgb(s['texto.inactivo'])}, 0.7)",
          "--scrollbar-track": "transparent",
          "--chip-outline-color": s["borde.separador"]}
    for papel, claves in MATERIAL.items():
        valor = v[SUPERFICIE[papel]] if papel in SUPERFICIE else s[CAMPO[variante]] if papel == "campo" else s[papel]
        v |= {k: valor for k in claves}
    return v


def comunes(tokens: dict) -> dict[str, str]:
    """Lo que no cambia con la variante: la monoespaciada y los radios. La letra de la interfaz no: Angular Material la
    escribe literal en sus reglas de tipografía (`.mat-typography h1 {font: …}`) y en sus variables, y cambiarla solo
    en parte mezclaría dos letras; la de la aplicación empieza por las del sistema."""
    tip, radio = tokens["tipografia"], tokens["radio"]
    px = lambda clave: f"{radio[clave]['$value']['value']}{radio[clave]['$value']['unit']}"  # noqa: E731
    familia = lambda fuentes: ", ".join(f if f in ("sans-serif", "serif", "monospace") else f'"{f}"' for f in fuentes)  # noqa: E731
    return {"--font-mono-stack": familia(tip["monoespaciada"]["$value"]),
            "--radius-sm": px("control"), "--radius-md": px("menu"), "--radius-lg": px("ventana"),
            "--radius-xl": px("panel-flotante")}


def bloque(selector: str, valores: dict[str, str], importante: bool = False) -> str:
    fin = " !important" if importante else ""
    return selector + " {\n" + "".join(f"  {k}: {v}{fin};\n" for k, v in valores.items()) + "}\n"


def texto_css(tokens: dict, marca: dict) -> str:
    partes = [f"/* {marca['nombre']} para Super Productivity: {marca['nombre_esquema']['claro']} y "
              f"{marca['nombre_esquema']['oscuro']} (con «Modo oscuro: Sistema» sigue al escritorio).\n"
              f"   GENERADO por herramientas/generar.py (complementos/super-productivity, {marca['nombre']} {VERSION}) "
              f"desde tokens/; no editar.\n"
              f"   {marca['repositorio']} · código {marca['licencia_codigo']}, colores {marca['licencia_activos']} */\n",
              bloque(COMUN, comunes(tokens))]
    for variante in ("claro", "oscuro"):
        nombre = marca["nombre_esquema"][variante]
        partes.append(f"\n/* {nombre}: la paleta de Material (la aplicación la pone en línea en <html>) */\n"
                      + bloque(RAIZ_CSS[variante], paletas(tokens, variante), importante=True))
        partes.append(f"\n/* {nombre} */\n" + bloque(SELECTOR[variante], variables(tokens, variante)))
    return "".join(partes)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / f"{marca['id']}.css", texto_css(tokens, marca), hechos)
    return hechos
