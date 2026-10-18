"""Datos del sitio oficial, generados desde los tokens y los módulos: variables SCSS (una por variante),
el catálogo de módulos (JSON y una página por módulo desde `modulos/<id>/INSTALL.md`) y las capturas.

Escribe bajo `sitio/generado/` (dentro del proyecto Quarto); los archivos que empiezan por `_` son inclusiones. Solo biblioteca estándar."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import RAIZ, VERSION, escribir, semanticos

MODULOS = RAIZ / "modulos"
CAPTURAS = RAIZ / "muestras" / "capturas"


def scss(tokens: dict, variante: str) -> str:
    t = semanticos(tokens, variante)
    r = {k: v["$value"]["value"] for k, v in tokens["radio"].items() if isinstance(v, dict) and "$value" in v}
    lineas = ["// GENERADO por herramientas/generar.py desde tokens/; no editar", "/*-- scss:defaults --*/"]
    for k, v in t.items():
        lineas.append(f"$ll-{k.replace('.', '-')}: {v};")
    lineas += [f"$ll-radio-control: {r['control']}px;", f"$ll-radio-menu: {r['menu']}px;", f"$ll-radio-ventana: {r['ventana']}px;",
               f'$ll-fuente: {", ".join(chr(34) + f + chr(34) for f in tokens["tipografia"]["interfaz"]["$value"])};',
               f'$ll-mono: {", ".join(chr(34) + f + chr(34) for f in tokens["tipografia"]["monoespaciada"]["$value"])};',
               # mapeo a Bootstrap (cosmo)
               "$body-bg: $ll-fondo-ventana;", "$body-color: $ll-texto-normal;", "$primary: $ll-acento-base;",
               "$link-color: $ll-enlace;", "$border-color: $ll-borde-separador;", "$font-family-sans-serif: $ll-fuente;",
               "$font-family-monospace: $ll-mono;", "$card-bg: $ll-fondo-vista;", "$navbar-bg: $ll-fondo-encabezado;",
               "$navbar-fg: $ll-texto-normal;", "$footer-bg: $ll-fondo-encabezado;", "$code-bg: $ll-fondo-vista;",
               "$border-radius: $ll-radio-control;", "$btn-border-radius: $ll-radio-control;",
               "$input-bg: $ll-fondo-vista;", "$input-border-color: $ll-borde-separador;", "$input-focus-border-color: $ll-foco;",
               "$table-border-color: $ll-borde-separador;", "$toc-color: $ll-texto-secundario;", "$toc-active-border: $ll-acento-base;"]
    return "\n".join(lineas) + "\n"


def leer_modulo(carpeta: Path) -> dict:
    meta = json.loads((carpeta / "modulo.json").read_text(encoding="utf-8"))
    meta["instalar"] = (carpeta / "INSTALL.md").read_text(encoding="utf-8")
    meta["id"] = carpeta.name
    return meta


def pagina_modulo(m: dict, marca: dict) -> str:
    capturas = "".join(f"\n![{c}]({c})" for c in m.get("capturas", []))
    return f"""---
title: "{m['nombre']}"
subtitle: "{m['resumen']}"
---

| | |
|---|---|
| estado | **{m['estado']}** |
| tecnología | {m['tecnologia']} |
| desde la versión | {m['desde']} |
| archivos | {', '.join('`' + a + '`' for a in m['archivos'])} |
| licencia | {m.get('licencia', marca['licencia_activos'])} |
{capturas}

{m['instalar']}

## Código, incidencias y cambios

- Código: [`generado/{m['carpeta']}`]({marca['repositorio']}/tree/main/generado/{m['carpeta']}) y su generador
  [`herramientas/destinos/{m['generador']}`]({marca['repositorio']}/blob/main/herramientas/destinos/{m['generador']}).
- Incidencias: [{marca['repositorio']}/issues]({marca['repositorio']}/issues?q=label%3A{m['id']}).
- Cambios: [registro de cambios](../../cambios.qmd).
"""


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    base = destino
    escribir(base / "_cambios.md", (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8").split("\n", 1)[1], hechos)
    for v in ("claro", "oscuro"):
        escribir(base / f"_tokens-{v}.scss", scss(tokens, v), hechos)
    modulos = [leer_modulo(c) for c in sorted(MODULOS.iterdir()) if (c / "modulo.json").exists()]
    escribir(base / "catalogo.json", json.dumps({"version": VERSION, "modulos": [{k: v for k, v in m.items() if k != "instalar"} for m in modulos]},
                                               ensure_ascii=False, indent=2) + "\n", hechos)
    for m in modulos:
        escribir(base / "catalogo" / f"{m['id']}.qmd", pagina_modulo(m, marca), hechos)
    filas = ["| módulo | qué entrega | estado | desde |", "|---|---|---|---|"]
    for m in modulos:
        filas.append(f"| [{m['nombre']}](generado/catalogo/{m["id"]}.qmd) | {m['resumen']} | {m['estado']} | {m['desde']} |")
    escribir(base / "_catalogo-tabla.md", "\n".join(filas) + "\n", hechos)
    if CAPTURAS.exists():
        for c in sorted(CAPTURAS.glob("*.png")):
            d = base / "capturas" / c.name
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(c, d)
            hechos.append(d)
    for b in ("boceto-claro.png", "boceto-oscuro.png"):
        o = RAIZ / "muestras" / b
        if o.exists():
            d = base / "capturas" / b
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(o, d); hechos.append(d)
    return hechos
