"""Tema de Obsidian (1.x) desde los tokens: `theme.css` con las dos variantes en un solo archivo.

Obsidian carga el `theme.css` de `.obsidian/themes/<Nombre>/` y elige la variante por la clase del cuerpo
(`.theme-light`, `.theme-dark`); el tema solo redefine **variables de Obsidian 1.x** (las de su `app.css`), sin
selectores de la interfaz, así que sobrevive a los cambios de la aplicación y no depende de Minimal ni de Style
Settings. Lo que define:

- La escala de neutros `--color-base-00…100`, de la que Obsidian deriva fondos, bordes, campos y textos: los fondos de
  vista para la nota, los de ventana para las barras laterales (como en Plasma), los bordes y los tres textos.
- El acento por variante (rojo oscuro en el oscuro, el azul de WhiteSur en el claro): `--accent-h/s/l` y los
  `--color-accent*`, más el texto de acento y los enlaces en `enlace`.
- Los ocho colores con nombre (`--color-red…pink` y sus `-rgb`) desde los ANSI de la terminal: de ellos salen
  llamadas, resaltados, lienzos y los colores de los iconos del tema. El naranja es el tono de advertencia de los
  semánticos (Lliphi no tiene un naranja ANSI).
- Los estados (error, advertencia, éxito), la tipografía (Inter y JetBrains Mono), los radios, la sintaxis del código
  con la tabla única de los editores, encabezados de color (h1 rojo … h6 morado) y los avisos y tooltips.
- Las llamadas que lleva la plantilla de Zotero Integration (`> [!tipo|#ffd400]`): cada color de anotación de Zotero
  toma el color del tema con el mismo nombre (antes, el fragmento `callouts.css`).

Ningún color se escribe aquí: los hexes salen de `tokens/tokens.json` y la prueba lo comprueba."""
from __future__ import annotations

import colorsys
from pathlib import Path

from nucleo import VERSION, escribir, hexa, registro, semanticos

sintaxis = registro.codigo("editores").sintaxis   # la tabla única de sintaxis de los editores (modulo.json)

CLASE = {"claro": ".theme-light", "oscuro": ".theme-dark"}

# color con nombre de Obsidian → (grupo, clave) del maestro; el grupo `terminal` da los ANSI
NOMBRADOS = {"red": ("terminal", "color1"), "orange": ("semanticos", "estado.advertencia"),
             "yellow": ("terminal", "color3"), "green": ("terminal", "color2"), "cyan": ("terminal", "color6"),
             "blue": ("terminal", "color4"), "purple": ("terminal", "color5"), "pink": ("terminal", "color13")}

# escala de neutros de Obsidian → semántico de Lliphi (de fondo de la nota a texto normal)
ESCALA = {"00": "fondo.vista", "05": "fondo.vista-alterno", "10": "fondo.vista-alterno", "20": "fondo.ventana",
          "25": "fondo.ventana-alterno", "30": "borde.sutil", "35": "fondo.tooltip", "40": "borde.separador",
          "50": "texto.inactivo", "60": "texto.inactivo", "70": "texto.secundario", "100": "texto.normal"}
ESCALA_CLARO = {"35": "borde.separador"}   # en el claro, el tono del tooltip es oscuro: el borde intermedio es el separador

# colores de anotación de Zotero (los que escribe la plantilla de Zotero Integration) → color con nombre del tema
ZOTERO = {"#ffd400": "yellow", "#ff6666": "red", "#5fb236": "green", "#2ea8e5": "blue", "#a28ae5": "purple",
          "#e56eee": "pink", "#f19837": "orange", "#aaaaaa": None}

# papel de Obsidian → papel de la tabla de sintaxis
CODIGO = {"normal": "variable", "comment": "comentario", "function": "funcion", "keyword": "palabra-clave",
          "string": "cadena", "value": "numero", "property": "tipo", "tag": "etiqueta", "operator": "operador",
          "punctuation": "puntuacion", "important": "atributo"}

ENCABEZADOS = ("red", "orange", "yellow", "green", "blue", "purple")

# fondo de los botones de peligro (con texto blanco): en el oscuro el error de los semánticos es un rojo claro para
# texto, y el único rojo de la variante que admite texto blanco es el de Nothing, el acento
FONDO_ERROR = {"claro": "estado.error", "oscuro": "acento.base"}


def rgb(hex6: str) -> str:
    h = hex6.lstrip("#")
    return ", ".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def hsl(hex6: str) -> tuple[int, int, int]:
    r, g, b = (int(hex6.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360), round(s * 100), round(l * 100)


def familia(fuentes: list[str]) -> str:
    return ", ".join(f if f in ("sans-serif", "serif", "monospace") else f'"{f}"' for f in fuentes)


def nombrados(tokens: dict, variante: str) -> dict[str, str]:
    """Color con nombre de Obsidian → hex de la variante."""
    s = semanticos(tokens, variante)
    t = {k: hexa(v) for k, v in tokens["terminal"][variante].items()}
    return {n: (t[k] if g == "terminal" else s[k]) for n, (g, k) in NOMBRADOS.items()}


def variables(tokens: dict, variante: str) -> dict[str, str]:
    """Variable de Obsidian → valor, para el bloque de una variante (solo colores)."""
    s = semanticos(tokens, variante)
    t = {k: hexa(v) for k, v in tokens["terminal"][variante].items()}
    escala = ESCALA | (ESCALA_CLARO if variante == "claro" else {})
    v: dict[str, str] = {f"--color-base-{k}": s[sem] for k, sem in escala.items()}
    for nombre, h in nombrados(tokens, variante).items():
        v[f"--color-{nombre}"] = h
        v[f"--color-{nombre}-rgb"] = rgb(h)
    h_, s_, l_ = hsl(s["acento.base"])
    v |= {"--accent-h": str(h_), "--accent-s": f"{s_}%", "--accent-l": f"{l_}%",
          "--color-accent": s["acento.base"], "--color-accent-1": s["acento.suave"], "--color-accent-2": s["acento.texto"],
          "--interactive-accent": s["acento.base"], "--interactive-accent-hover": s["hover"],
          "--text-accent": s["enlace"], "--text-accent-hover": s["acento.suave"], "--text-on-accent": s["texto.sobre-acento"],
          "--text-error": s["estado.error"], "--text-warning": s["estado.advertencia"], "--text-success": s["estado.exito"],
          "--background-modifier-error": s[FONDO_ERROR[variante]], "--background-modifier-error-hover": s[FONDO_ERROR[variante]],
          "--background-modifier-error-rgb": rgb(s[FONDO_ERROR[variante]]), "--background-modifier-warning": s["estado.advertencia"],
          "--background-modifier-warning-hover": s["estado.advertencia"], "--background-modifier-success": s["estado.exito"],
          "--background-modifier-success-rgb": rgb(s["estado.exito"]),
          "--background-modifier-message": s["fondo.tooltip"], "--tooltip-color": s["texto.tooltip"],
          "--notice-color": s["texto.tooltip"]}
    x = sintaxis(s, t)
    v |= {f"--code-{papel}": x[papel_lliphi] for papel, papel_lliphi in CODIGO.items()}
    v["--code-background"] = s["fondo.vista-alterno"]
    return v


def comunes(tokens: dict) -> dict[str, str]:
    """Lo que no cambia con la variante: tipografía, radios, anchos, encabezados y llamadas."""
    tip, radio = tokens["tipografia"], tokens["radio"]
    px = lambda clave: f"{radio[clave]['$value']['value']}{radio[clave]['$value']['unit']}"  # noqa: E731
    v = {"--font-interface-theme": familia(tip["interfaz"]["$value"]), "--font-text-theme": familia(tip["interfaz"]["$value"]),
         "--font-monospace-theme": familia(tip["monoespaciada"]["$value"]),
         "--radius-s": px("control"), "--radius-m": px("menu"), "--radius-l": px("ventana"), "--radius-xl": px("panel-flotante"),
         "--input-radius": px("control"), "--file-line-width": "40rem",
         "--link-decoration": "none", "--link-external-decoration": "none",
         "--callout-quote": "var(--color-base-50)", "--tooltip-background": "var(--background-modifier-message)",
         "--notice-background": "var(--background-modifier-message)"}
    v |= {f"--h{i}-color": f"var(--color-{c})" for i, c in enumerate(ENCABEZADOS, 1)}
    return v


def bloque(selector: str, valores: dict[str, str]) -> str:
    return selector + " {\n" + "".join(f"  {k}: {v};\n" for k, v in valores.items()) + "}\n"


def texto_css(tokens: dict, marca: dict) -> str:
    partes = [f"/* {marca['nombre']} para Obsidian: {marca['nombre_esquema']['claro']} y {marca['nombre_esquema']['oscuro']}.\n"
              f"   GENERADO por herramientas/generar.py (complementos/obsidian, {marca['nombre']} {VERSION}) desde tokens/; no editar.\n"
              f"   {marca['repositorio']} · código {marca['licencia_codigo']}, colores {marca['licencia_activos']} */\n",
              bloque("body", comunes(tokens))]
    for variante in ("claro", "oscuro"):
        partes.append(f"\n/* {marca['nombre_esquema'][variante]} */\n" + bloque(CLASE[variante], variables(tokens, variante)))
    partes.append("\n/* Llamadas de Zotero Integration: el color de la anotación (> [!tipo|#ffd400]) toma el color del tema */\n")
    for hex_zotero, nombre in ZOTERO.items():
        color = f"var(--color-{nombre})" if nombre else "var(--color-base-50)"
        partes.append(bloque(f'.callout[data-callout-metadata="{hex_zotero}" i]', {"--callout-color": color}))
    return "".join(partes)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / "theme.css", texto_css(tokens, marca), hechos)
    return hechos
