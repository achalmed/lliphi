"""Estilos de usuario para sitios web desde los tokens: un `<sitio>.user.css` por sitio, con las dos variantes.

Un estilo de usuario es CSS que el navegador aplica sobre las páginas de un dominio. Se escribe en el formato
**UserCSS** (la cabecera `==UserStyle==` que leen Stylus y sus parientes) con el cuerpo dentro de
`@-moz-document domain(...)`, que Stylus entiende en Zen y en Chrome y que Firefox entiende sin extensión en
`userContent.css`. Cada estilo solo **redefine las variables CSS del sitio** (las de su sistema de diseño), con
`!important` para ganar a las del sitio sin depender de la especificidad de sus selectores; casi no lleva selectores
de la página, así que resiste los cambios del sitio.

Cada sitio es un archivo de esta carpeta (`duckduckgo.py`, `github.py`) con la misma interfaz:

- `NOMBRE`, `DOMINIOS` y `DESCRIPCION`;
- `AMBITOS[variante]`: dónde vale cada variante, pares `(media, selector)` (DuckDuckGo sigue a `prefers-color-scheme`;
  GitHub, además, a su propio modo claro u oscuro);
- `variables(p)`: variable del sitio → valor, para la `Paleta` de una variante; `reglas(p)`: pocas reglas con
  selector relativo al ámbito (la selección del texto); `comunes(fuentes)`: lo que no cambia con la variante (las familias de la interfaz y la monoespaciada);
- `CONTRASTE` y `FONDO`: los pares texto/fondo que deben llegar a 4,5:1 (los comprueban las pruebas) y la variable del
  fondo de la página, sobre la que se mezclan los fondos translúcidos;
- `extras(tokens, marca)` (opcional): otros archivos del sitio (los ajustes de DuckDuckGo).

Para añadir un sitio basta un archivo nuevo con esa interfaz y su id en `SITIOS`. Ningún color se escribe aquí ni en
los sitios: los hexes salen de `tokens/tokens.json`, a lo sumo con un alfa (`#rrggbbaa`), y las pruebas lo comprueban."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from nucleo import VERSION, escribir, hexa, registro, semanticos

SITIOS = ("duckduckgo", "github")
VARIANTES = ("claro", "oscuro")

sintaxis = registro.codigo("editores").sintaxis   # la tabla única de sintaxis de los editores

# fondos que llevan texto blanco (`texto.sobre-acento`): en el oscuro, los estados de los semánticos son tonos claros
# para texto y no admiten texto blanco, así que los rellenos (insignias, etiquetas de estado) toman los del claro, que
# son los oscuros y saturados; el peligro del oscuro es el rojo de Nothing, como en Obsidian (decisiones 5.1)
RELLENOS = {"acento": ("variante", "acento.base"), "exito": ("claro", "estado.exito"), "advertencia": ("claro", "estado.advertencia"),
            "info": ("claro", "estado.info"), "neutro": ("claro", "texto.inactivo"), "error": {"claro": "estado.error", "oscuro": "acento.base"}}
# el botón principal al pasar el puntero: el acento más oscuro de la variante que aún admite texto blanco
ACENTO_PASAR = {"claro": "acento.texto", "oscuro": "acento.base"}


@dataclass
class Paleta:
    """Los colores de una variante, como los usan los sitios."""
    variante: str
    s: dict[str, str]           # semánticos de la variante
    t: dict[str, str]           # ANSI de la variante (color0…color15)
    tc: dict[str, str]          # ANSI del claro (los rellenos morado y rosa)
    x: dict[str, str]           # papel sintáctico → hex (la tabla de los editores)
    relleno: dict[str, str]     # papel → fondo que admite texto blanco

    def alfa(self, clave: str, aa: str) -> str:
        """Un semántico con alfa (`#rrggbbaa`): el color sigue siendo el del maestro."""
        return self.s[clave] + aa


def paleta(tokens: dict, variante: str) -> Paleta:
    s, sc = semanticos(tokens, variante), semanticos(tokens, "claro")
    t = {k: hexa(v) for k, v in tokens["terminal"][variante].items()}
    tc = {k: hexa(v) for k, v in tokens["terminal"]["claro"].items()}
    relleno = {}
    for papel, origen in RELLENOS.items():
        if isinstance(origen, dict):
            relleno[papel] = s[origen[variante]]
        else:
            relleno[papel] = (s if origen[0] == "variante" else sc)[origen[1]]
    relleno["acento-pasar"] = s[ACENTO_PASAR[variante]]
    relleno["morado"], relleno["rosa"] = tc["color5"], tc["color13"]
    return Paleta(variante, s, t, tc, sintaxis(s, t), relleno)


def sitio(id_: str) -> ModuleType:
    return registro.codigo("sitios-web", id_)


def familia(fuentes: list[str]) -> str:
    return ", ".join(f if f in ("sans-serif", "serif", "monospace") else f'"{f}"' for f in fuentes)


def bloque(selector: str, valores: dict[str, str], sangria: str) -> str:
    """Una regla con cada declaración en `!important` (gana a las del sitio sea cual sea su selector)."""
    return (f"{sangria}{selector} {{\n" + "".join(f"{sangria}  {k}: {v} !important;\n" for k, v in valores.items())
            + f"{sangria}}}\n")


def cabecera(marca: dict, m: ModuleType) -> str:
    # sin URL del repositorio ni usuario: el estilo no lleva datos personales (los guías de instalación dicen de dónde sale)
    return ("/* ==UserStyle==\n"
            f"@name         {marca['nombre']} para {m.NOMBRE}\n"
            f"@namespace    {marca['id']}\n"
            f"@version      {VERSION}\n"
            f"@description  {m.DESCRIPCION}\n"
            f"@author       {marca['nombre']}\n"
            f"@license      {marca['licencia_activos']}\n"
            "@preprocessor default\n"
            "==/UserStyle== */\n"
            f"/* GENERADO por herramientas/generar.py (complementos/sitios-web, {marca['nombre']} {VERSION}) desde tokens/; no editar.\n"
            f"   {marca['nombre_esquema']['claro']} y {marca['nombre_esquema']['oscuro']}: solo variables del sitio, la variante según el modo. */\n")


def texto_estilo(tokens: dict, marca: dict, id_: str) -> str:
    m = sitio(id_)
    dominios = ", ".join(f'domain("{d}")' for d in m.DOMINIOS)
    partes = [cabecera(marca, m), f"@-moz-document {dominios} {{\n"]
    fuentes = {k: familia(tokens["tipografia"][k]["$value"]) for k in ("interfaz", "monoespaciada")}
    for selector, valores in m.comunes(fuentes).items():
        partes.append(bloque(selector, valores, "  "))
    for variante in VARIANTES:
        p = paleta(tokens, variante)
        variables, reglas = m.variables(p), m.reglas(p)
        partes.append(f"\n  /* {marca['nombre_esquema'][variante]} */\n")
        for media, ambito in m.AMBITOS[variante]:
            sangria = "    " if media else "  "
            cuerpo = bloque(ambito, variables, sangria)
            cuerpo += "".join(bloque(f"{ambito} {rel}", valores, sangria) for rel, valores in reglas.items())
            partes.append(f"  @media {media} {{\n{cuerpo}  }}\n" if media else cuerpo)
    partes.append("}\n")
    return "".join(partes)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for id_ in SITIOS:
        escribir(destino / f"{id_}.user.css", texto_estilo(tokens, marca, id_), hechos)
        m = sitio(id_)
        if hasattr(m, "extras"):
            for rel, texto in m.extras(tokens, marca).items():
                escribir(destino / rel, texto, hechos)
    return hechos
