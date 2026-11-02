"""Aplicación en RStudio (decisiones 5.40): `editor_theme` de `rstudio-prefs.json` toma el tema de la variante; lo demás
del archivo no se toca. El archivo se respalda antes de instalar. Si RStudio nunca se abrió (no hay carpeta), no se
crea nada: el tema ya está en `themes/` y se elige en Tools → Global Options → Appearance."""
from __future__ import annotations

import json
import os
from pathlib import Path


def carpeta(config: Path) -> Path:
    return Path(os.environ.get("RSTUDIO_CONFIG_HOME") or config / "rstudio")


def fijar_tema(prefs: Path, tema: str) -> None:
    """Escribe `editor_theme` y conserva lo demás; en el archivo real, para no romper un enlace de dotfiles."""
    datos = json.loads(prefs.read_text(encoding="utf-8")) if prefs.exists() else {}
    datos["editor_theme"] = tema
    real = prefs.resolve()
    real.parent.mkdir(parents=True, exist_ok=True)
    temporal = real.with_name(real.name + ".lliphi")
    temporal.write_text(json.dumps(datos, indent=4, ensure_ascii=False), encoding="utf-8")
    temporal.replace(real)


def respaldos(ctx) -> list:
    prefs = carpeta(ctx.CONFIG) / "rstudio-prefs.json"
    return [(prefs, "reponer", "preferencias de RStudio")] if prefs.is_relative_to(ctx.CONFIG) else []


def aplicar(ctx) -> int:
    if "rstudio" not in ctx.modulos:
        return 0
    base = carpeta(ctx.CONFIG)
    tema = ctx.marca["nombre_esquema"][ctx.variante]
    if not base.is_dir():
        ctx.decir("RStudio: sin configuración propia (no se ha abierto); elige el tema en Tools → Global Options → Appearance")
        return 0
    fijar_tema(base / "rstudio-prefs.json", tema)
    ctx.decir(f"RStudio: tema {tema} (se ve al abrir RStudio de nuevo)")
    return 0
