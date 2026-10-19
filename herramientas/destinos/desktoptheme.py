"""Estilo de Plasma de Lliphi, DERIVADO de WhiteSur-kde (Vince Liuice, GPL-3.0; `fuentes/base/WhiteSur-kde`).

Decisión del autor (2026-10-18, docs/decisiones.md 3.11): no dibujar desde cero; tomar el estilo de Plasma de WhiteSur
(vidrio, radios, sombras, 38 SVG pulidos), quitarle lo que imita a Apple y recolorearlo con los tokens de Lliphi.
Qué se hace con la base:

- `colors` se retira: el estilo sigue el esquema de color del sistema (y el acento del usuario) en vez de la paleta
  fija de WhiteSur; los SVG de WhiteSur ya usan el `current-color-scheme` de Plasma para texto y fondos.
- Los hex fijos que quedan en los SVG (el negro translúcido del panel, los grises de los botones, el azul de Google
  de los indicadores) se sustituyen por los tokens de la variante.
- `metadata.json` y `plasmarc` son de Lliphi (desenfoque y contraste activos; fondo de Lliphi).
- Dos variantes porque la base las tiene: `lliphi-oscuro` ← WhiteSur-dark, `lliphi-claro` ← WhiteSur.
Lo derivado es GPL-3.0-or-later (REUSE.toml).
"""
from __future__ import annotations

import gzip
import json
import re
import shutil
from pathlib import Path

from . import RAIZ, VERSION, aplanar, autores, escribir, rgb, semanticos
from .esquema import con_acento

BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "plasma" / "desktoptheme"
ORIGEN = {"oscuro": "WhiteSur-dark", "claro": "WhiteSur"}

# hex fijo de WhiteSur → token semántico de Lliphi (los colores de marcador de Plasma —magenta, cian, verde, naranja—
# y los del stylesheet de Breeze no se tocan: Plasma los sustituye o los ignora)
MAPA = {"oscuro": {}, "claro": {}}   # línea base del autor: WhiteSur tal cual, sin recolorear (salvo el acento de `colors`)


def recolorear(texto: str, mapa: dict[str, str]) -> str:
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), texto)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    ef = {k: v["$value"] for k, v in tokens.get("efectos", {}).items() if isinstance(v, dict) and "$value" in v}
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        mapa = {h: t[tok] for h, tok in MAPA[variante].items()}
        id_ = f"{marca['id']}-{variante}"
        base = destino / "desktoptheme" / id_
        origen = BASE / ORIGEN[variante]
        for f in sorted(origen.rglob("*")):
            if not f.is_file() or f.name in ("plasmarc", "metadata.json", "metadata.desktop"):
                continue
            rel = f.relative_to(origen)
            if f.suffix == ".svgz":
                texto = gzip.open(f).read().decode("utf-8", errors="ignore")
                escribir(base / rel.with_suffix(".svg"), recolorear(texto, mapa), hechos)   # sin comprimir: diff legible
            elif f.name == "colors":
                # mejora 8 (decisiones 4.13): el `colors` de WhiteSur con solo el acento de la variante (rojo en el
                # oscuro, azul de WhiteSur en el claro), igual que el esquema de la mejora 1; lo demás, byte a byte
                trgb = {k: rgb(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}
                escribir(base / rel, con_acento(f.read_text(encoding="utf-8"), trgb), hechos)
            elif f.suffix == ".svg":
                escribir(base / rel, recolorear(f.read_text(encoding="utf-8", errors="ignore"), mapa), hechos)
            else:
                (base / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(f, base / rel); hechos.append(base / rel)
        escribir(base / "metadata.json", json.dumps({
            "KPlugin": {"Authors": autores(marca) + [{"Name": "Vince Liuice (WhiteSur-kde, base GPL-3.0)", "Email": ""}],
                        "Category": "", "Description": f"{marca['descripcion']} Derivado del estilo de Plasma WhiteSur-kde.",
                        "EnabledByDefault": True, "Id": id_, "License": "GPL-3.0-or-later",
                        "Name": marca["nombre_esquema"][variante], "Version": VERSION, "Website": marca["sitio"]},
            "X-Plasma-API": "5.0"}, ensure_ascii=False, indent=4) + "\n", hechos)
        escribir(base / "plasmarc", "\n".join([
            "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/WhiteSur-kde; no editar", "",
            "[Settings]", "FallbackTheme=default", "",
            "[Wallpaper]", f"defaultWallpaperTheme={marca['id_fondo']}", "defaultFileSuffix=.png", "defaultWidth=1920", "defaultHeight=1080", "",
            "[ContrastEffect]", "enabled=true", f"contrast={ef.get('contraste', 0.35)}", f"intensity={ef.get('intensidad', 1.0)}", f"saturation={ef.get('saturacion', 1.15)}", "",
            "[BlurBehindEffect]", "enabled=true", "",
            "[AdaptiveTransparency]", "enabled=true", ""]), hechos)
    return hechos
