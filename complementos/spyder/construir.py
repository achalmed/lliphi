"""Spyder (decisiones 5.42): dos esquemas de sintaxis, «<nombre> Claro» (`<id>/claro`) y «<nombre> Oscuro»
(`<id>/oscuro`), con los que Spyder pinta el editor, la consola IPython, el historial y la ayuda, y la interfaz en
automático, que con `ui_theme = automatic` se pone clara u oscura según el texto del esquema elegido.

Formato (comprobado el 2026-11-01 en Spyder 6.1.0 de Anaconda, `spyder/config/appearance.py`, `config/gui.py` y
`plugins/appearance/confpage.py`): la sección `[appearance]` de `$XDG_CONFIG_HOME/spyder-py3/config/spyder.ini` guarda
cada esquema como `<esquema>/<clave>` con las 17 claves de `COLOR_SCHEME_KEYS` (fondos: `background`, `currentline`,
`currentcell`, `occurrence`, `ctrlclick`, `sideareas`, `matched_p`, `unmatched_p`; texto: `normal`, `keyword`,
`magic`, `builtin`, `definition`, `comment`, `string`, `number`, `instance`, cada una `('#rrggbb', negrita, cursiva)`),
la lista `names` de los esquemas y el elegido en `selected`. Los esquemas de Lliphi van en `names`, como los de Spyder:
`custom_names` exige nombres `custom-<n>` (crear un esquema nuevo falla con otro nombre).

La consola IPython (qtconsole) toma la sintaxis, el fondo y el texto del esquema, pero sus dieciséis colores ANSI son
fijos (`QtAnsiCodeProcessor.darkbg_color_map`); sí atiende la secuencia OSC 4 de xterm (`ESC ] 4 ; n ; rgb:… BEL`), que
cambia uno. `consola.py` las escribe al arrancar cada consola con los colores de Konsole (`konsole.ansi`) de la variante
del esquema elegido; Spyder lo ejecuta con `startup/run_file` (las líneas de `startup/run_lines` se ejecutan ocultas y
qtconsole descarta su salida). Si el esquema elegido no es de Lliphi, no escribe nada.

La sintaxis sale de la tabla de los editores (`editores.sintaxis`). Ningún color se escribe aquí. Se generan
`spyder-lliphi.py`, el programa que escribe los esquemas en `spyder.ini` (con Spyder cerrado: Spyder reescribe el archivo
entero) y cambia de esquema al cambiar la variante, y `consola.py`."""
from __future__ import annotations

import json
from pathlib import Path
from pprint import pformat

from nucleo import escribir, registro

sintaxis = registro.codigo("editores").sintaxis
paleta = registro.codigo("editores").paleta
ansi = registro.codigo("konsole").ansi

CARPETA = Path(__file__).resolve().parent
PROGRAMA, CONSOLA = "spyder-lliphi.py", "consola.py"

# clave de Spyder → (papel de la tabla de sintaxis, negrita, cursiva)
TEXTO = {"normal": ("variable", False, False), "keyword": ("palabra-clave", False, False),
         "magic": ("atributo", False, False), "builtin": ("funcion", False, False),
         "definition": ("funcion", True, False), "comment": ("comentario", False, True),
         "string": ("cadena", False, False), "number": ("numero", False, False),
         "instance": ("atributo", False, True)}


def esquema(tokens: dict, marca: dict, variante: str) -> dict[str, object]:
    """Las 17 claves de un esquema de Spyder más su nombre visible."""
    s, t = paleta(tokens, variante)
    x = sintaxis(s, t)
    e: dict[str, object] = {
        "name": marca["nombre_esquema"][variante],
        "background": s["fondo.vista"], "currentline": s["fondo.vista-alterno"], "currentcell": s["fondo.ventana"],
        "occurrence": s["borde.separador"], "ctrlclick": s["enlace"], "sideareas": s["fondo.vista"],
        "matched_p": s["borde.separador"], "unmatched_p": s["estado.error"],
    }
    e.update({clave: (x[papel], negrita, cursiva) for clave, (papel, negrita, cursiva) in TEXTO.items()})
    return e


def nombre(marca: dict, variante: str) -> str:
    return f"{marca['id']}/{variante}"


def texto_programa(tokens: dict, marca: dict) -> str:
    esquemas = {nombre(marca, v): esquema(tokens, marca, v) for v in ("claro", "oscuro")}
    return ((CARPETA / "variante.py").read_text(encoding="utf-8").replace("@NOMBRE@", marca["nombre"]).replace("@ID@", marca["id"])
            .replace("@CLARO@", marca["nombre_esquema"]["claro"]).replace("@OSCURO@", marca["nombre_esquema"]["oscuro"])
            .replace('"@ESQUEMAS@"', pformat(esquemas, width=118, sort_dicts=False)))


def texto_consola(tokens: dict, marca: dict) -> str:
    colores = {nombre(marca, v): [ansi(tokens, v)[f"color{i}"] for i in range(16)] for v in ("claro", "oscuro")}
    return ((CARPETA / "consola.py").read_text(encoding="utf-8").replace("@NOMBRE@", marca["nombre"])
            .replace('"@COLORES@"', json.dumps(colores, ensure_ascii=False)))


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    escribir(destino / PROGRAMA, texto_programa(tokens, marca), hechos)
    (destino / PROGRAMA).chmod(0o755)
    escribir(destino / CONSOLA, texto_consola(tokens, marca), hechos)
    return hechos
