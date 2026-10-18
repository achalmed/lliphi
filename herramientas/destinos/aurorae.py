"""Decoración de ventanas de Lliphi, DERIVADA del tema Aurorae «Nothing» (jomada, Seducción Linux, GPL-3.0-or-later;
`fuentes/base/Nothing-aurorae`), por decisión del autor (2026-10-18): los botones circulares con glifo al pasar el
ratón y el marco sobrio de Nothing, recoloreados con los tokens de Lliphi y sin la sombra blanca del texto.

Variantes: `lliphi` (oscuro) y `lliphi-claro`. La posición de los botones la fija el instalador en `kwinrc`
(`ButtonsOnRight=IAX`). Lo derivado es GPL-3.0-or-later (REUSE.toml)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import RAIZ, VERSION, autores, escribir, semanticos

BASE = RAIZ / "fuentes" / "base" / "Nothing-aurorae"

# hex fijos de Nothing → token; el marco oscuro de Nothing es #1b1b1d (título) con bordes #111216 y #202b30
MAPA = {
    "oscuro": {"#1b1b1d": "fondo.encabezado", "#111216": "fondo.vista", "#202b30": "borde.separador",
               "#eb3131": "acento.base", "#d46969": "acento.suave", "#a82323": "acento.texto"},
    "claro": {"#1b1b1d": "fondo.encabezado", "#111216": "borde.separador", "#202b30": "borde.separador",
              "#eb3131": "acento.base", "#d46969": "acento.suave", "#a82323": "acento.texto",
              "#e6e6df": "fondo.boton", "#dadad3": "borde.separador", "#f4f0ed": "fondo.vista", "#e5e5de": "fondo.boton",
              "#dadad4": "borde.separador", "#d1d1ca": "borde.separador", "#f5f5ee": "fondo.vista"},
}


def rgb(hex_: str) -> str:
    h = hex_.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        mapa = {h: t[tok] for h, tok in MAPA[variante].items()}
        id_ = marca["id"] if variante == "oscuro" else f"{marca['id']}-claro"
        base = destino / "aurorae" / id_
        for svg in sorted(BASE.glob("*.svg")):
            texto = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), svg.read_text(encoding="utf-8", errors="ignore"))
            escribir(base / svg.name, texto, hechos)
        rc = (BASE / "Nothingrc").read_text(encoding="utf-8")
        rc = re.sub(r"^ActiveTextColor=.*$", f"ActiveTextColor={rgb(t['texto.normal'])}", rc, flags=re.M)
        rc = re.sub(r"^InactiveTextColor=.*$", f"InactiveTextColor={rgb(t['texto.inactivo'])}", rc, flags=re.M)
        rc = re.sub(r"^UseTextShadow=.*$", "UseTextShadow=false", rc, flags=re.M)
        rc = re.sub(r"^TitleHeight=.*$", "TitleHeight=18", rc, flags=re.M)
        rc = re.sub(r"^ButtonSpacing=.*$", "ButtonSpacing=6", rc, flags=re.M)
        escribir(base / f"{id_}rc", "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/Nothing-aurorae; no editar\n" + rc, hechos)
        nombre = marca["nombre_esquema"][variante]
        escribir(base / "metadata.json", json.dumps({
            "KPackageStructure": "KWin/Aurorae",
            "KPlugin": {"Authors": autores(marca) + [{"Name": "jomada (Nothing, base GPL-3.0-or-later)", "Email": ""}],
                        "Category": "Plasma 6 Window Decorations", "ServiceTypes": ["KWin/Aurorae"], "EnabledByDefault": True,
                        "Name": nombre, "Description": f"Decoración de {marca['nombre']}, derivada de Nothing", "Id": id_,
                        "Version": VERSION, "License": "GPL-3.0-or-later", "X-KDE-PluginInfo-blur": False, "X-KPackage-Dependencies": []},
        }, ensure_ascii=False, indent=4) + "\n", hechos)
        escribir(base / "metadata.desktop", "\n".join([
            "[Desktop Entry]", f"Name={nombre}", f"Comment=Decoración de {marca['nombre']}, derivada de Nothing", "Type=Service",
            "X-KDE-ServiceTypes=KWin/Aurorae", f"X-KDE-PluginInfo-Name={id_}", f"X-KDE-PluginInfo-Version={VERSION}",
            f"X-KDE-PluginInfo-Author={marca['autor']}", "X-KDE-PluginInfo-License=GPL-3.0-or-later", "X-KDE-PluginInfo-EnabledByDefault=true", ""]), hechos)
    return hechos
