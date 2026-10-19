"""Decoración de ventanas de Lliphi, DERIVADA del tema Aurorae «Nothing» (jomada, Seducción Linux, GPL-3.0-or-later;
`fuentes/base/Nothing-aurorae`), por decisión del autor (2026-10-18): los botones circulares con glifo al pasar el
ratón y el marco sobrio de Nothing. La variante oscura es Nothing tal cual (más una barra de 18 px); la clara se recolorea
con los tokens porque Nothing no tiene variante clara.

Plus de Lliphi sobre Nothing (mejora 4, decisiones 4.8), sin tocar formas ni tamaños de los botones:
- el anillo cian del botón de minimizar (`#9cdde4`) toma el gris del anillo de maximizar (`#bdbab8`): el trío queda en
  rojo y dos neutros, la paleta de Lliphi;
- el título usa los grises de los tokens (`texto.normal`, `texto.inactivo`) en vez del lavanda de Nothing, sin sombra;
  la fuente es la de títulos del sistema (Inter Medium, la fija el instalador).

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
    # oscuro: Nothing tal cual (decisión del autor: «la decoración me gusta más de Nothing así como está»); los plus van
    # en NEUTRO y en el rc
    "oscuro": {},
    "claro": {"#1b1b1d": "fondo.encabezado", "#111216": "borde.separador", "#202b30": "borde.separador",
              # el rojo del botón de cerrar de Nothing se queda tal cual: en el claro el acento es azul (decisiones 4.12)
              "#e6e6df": "fondo.boton", "#dadad3": "borde.separador", "#f4f0ed": "fondo.vista", "#e5e5de": "fondo.boton",
              "#dadad4": "borde.separador", "#d1d1ca": "borde.separador", "#f5f5ee": "fondo.vista"},
}


# hex de Nothing → hex de Nothing: el anillo cian de minimizar pasa al gris del anillo de maximizar (ambas variantes)
NEUTRO = {"#9cdde4": "#bdbab8"}


def rgb(hex_: str) -> str:
    h = hex_.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("oscuro", "claro"):
        t = semanticos(tokens, variante)
        mapa = {**NEUTRO, **{h: t[tok] for h, tok in MAPA[variante].items()}}
        id_ = marca["id"] if variante == "oscuro" else f"{marca['id']}-claro"
        base = destino / "aurorae" / id_
        for svg in sorted(BASE.glob("*.svg")):
            texto = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: mapa.get(m.group(0).lower(), m.group(0)), svg.read_text(encoding="utf-8", errors="ignore"))
            escribir(base / svg.name, texto, hechos)
        rc = (BASE / "Nothingrc").read_text(encoding="utf-8")
        # título en los grises de Lliphi y sin sombra, en las dos variantes (mejora 4)
        rc = re.sub(r"^ActiveTextColor=.*$", f"ActiveTextColor={rgb(t['texto.normal'])}", rc, flags=re.M)
        rc = re.sub(r"^InactiveTextColor=.*$", f"InactiveTextColor={rgb(t['texto.inactivo'])}", rc, flags=re.M)
        rc = re.sub(r"^UseTextShadow=.*$", "UseTextShadow=false", rc, flags=re.M)
        rc = re.sub(r"^TitleHeight=.*$", "TitleHeight=18", rc, flags=re.M)   # plus: barra algo más alta
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
