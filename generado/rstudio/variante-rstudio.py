#!/usr/bin/env python3
"""Lliphi en RStudio sigue a la variante. GENERADO por herramientas/generar.py desde complementos/rstudio; no editar.

RStudio no cambia de tema al pasar el escritorio entre claro y oscuro. Si su tema (`editor_theme` de
`rstudio-prefs.json`) es «Lliphi Claro» o «Lliphi Oscuro», este programa pone el de la variante pedida; si es otro, no toca
nada. RStudio lee ese archivo al arrancar (comprobado con 2026.05.1: abierto, no lo relee): el cambio se ve al abrirlo
de nuevo. Si con RStudio abierto cambias alguna preferencia, puede volver a escribir el tema que tenía.

Uso:  variante-rstudio.py claro|oscuro              # simula: dice qué cambiaría
      variante-rstudio.py claro|oscuro --aplicar    # lo cambia
Lo llama la vigilancia de fondo-variante (seguir-variante.py) en cada cambio de variante. Solo biblioteca estándar.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TEMAS = {"claro": "Lliphi Claro", "oscuro": "Lliphi Oscuro"}
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
PREFS = Path(os.environ.get("RSTUDIO_CONFIG_HOME") or CONFIG / "rstudio") / "rstudio-prefs.json"


def main(argv: list[str]) -> int:
    if len(argv) < 1 or argv[0] not in TEMAS:
        print(__doc__.split("\n\n")[-1], file=sys.stderr)
        return 1
    var, escribir = argv[0], "--aplicar" in argv
    if not PREFS.exists():
        return 0
    try:
        prefs = json.loads(PREFS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"RStudio: no se pudo leer {PREFS}: {e}", file=sys.stderr)
        return 1
    actual = prefs.get("editor_theme")
    if actual not in TEMAS.values() or actual == TEMAS[var]:
        return 0                                  # otro tema, o ya es el de la variante
    print(f"{'' if escribir else 'SIM '}RStudio: {actual} → {TEMAS[var]}")
    if escribir:
        prefs["editor_theme"] = TEMAS[var]
        real = PREFS.resolve()                    # el archivo real: un enlace de dotfiles (stow) se conserva
        temporal = real.with_name(real.name + ".lliphi")
        temporal.write_text(json.dumps(prefs, indent=4, ensure_ascii=False), encoding="utf-8")
        temporal.replace(real)                    # de una vez: RStudio nunca lee un archivo a medias
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
