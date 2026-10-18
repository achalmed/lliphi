#!/usr/bin/env python3
"""Dependencias de terceros que Lliphi usa tal cual (lo mejor que ya existe), instaladas en el usuario.

Línea base (docs/linea-base.md):
- Cursores: WhiteSur-cursors (GPL-3.0; vinceliuice; KDE Store 1411743). El repositorio no publica versiones: se toma
  `dist/` del tarball de la rama principal.
- Tipografías: Inter (OFL) y Hack (MIT) vienen de la distribución (`fonts-inter`, `fonts-hack`); aquí solo se comprueban.
Opcionales (`--opcionales`; piezas probadas en 0.2.0 que el autor dejó fuera de la línea base):
- Iconos: Papirus (Papirus, Papirus-Dark, Papirus-Light; GPL-3.0; PapirusDevelopmentTeam) con las carpetas en el
  color del acento, como hace `papirus-folders` (se enlazan los `folder-red-*` sobre los `folder-*`).
- Cursores: Bibata Modern Classic (oscuro) y Modern Ice (claro) (GPL-3.0; ful1e5).

Se descargan de GitHub a `$XDG_DATA_HOME/icons/`; nada en `/usr`. Lo descargado no se redistribuye en este
repositorio: se cita y se enlaza (docs/licencias en el sitio).

Uso:  python3 herramientas/dependencias.py                         # simula: qué descargaría y dónde
      python3 herramientas/dependencias.py --aplicar               # descarga e instala lo que falte de la línea base
      python3 herramientas/dependencias.py --aplicar --opcionales  # además Papirus y Bibata
Solo biblioteca estándar (urllib, tarfile).
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

HOME = Path.home()
DATA = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local" / "share")
ICONOS = DATA / "icons"

PAPIRUS = {"repo": "PapirusDevelopmentTeam/papirus-icon-theme", "temas": ["Papirus", "Papirus-Dark", "Papirus-Light"], "licencia": "GPL-3.0-only"}
BIBATA = {"repo": "ful1e5/Bibata_Cursor", "activos": {"Bibata-Modern-Classic.tar.xz": "Bibata-Modern-Classic", "Bibata-Modern-Ice.tar.xz": "Bibata-Modern-Ice"}, "licencia": "GPL-3.0-only"}
WHITESUR_CURSORES = {"repo": "vinceliuice/WhiteSur-cursors", "tema": "WhiteSur-cursors", "licencia": "GPL-3.0-only"}
COLOR_CARPETAS = "red"   # el acento de Lliphi; papirus-folders admite red, orange, yellow, green, teal, blue, violet, …


def api(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lliphi", "Accept": "application/vnd.github+json"}), timeout=60) as r:
        return json.load(r)


def descargar(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lliphi"}), timeout=600) as r:
        return r.read()


def papirus(aplicar: bool) -> None:
    faltan = [t for t in PAPIRUS["temas"] if not (ICONOS / t / "index.theme").exists()]
    if not faltan:
        print(f"  Papirus ya está en {ICONOS} ({', '.join(PAPIRUS['temas'])})")
    else:
        rel = api(f"https://api.github.com/repos/{PAPIRUS['repo']}/releases/latest")
        print(f"  {'descargar' if aplicar else 'SIM descargar'} Papirus {rel['tag_name']} ({PAPIRUS['licencia']}) → {ICONOS}/{{{','.join(faltan)}}}")
        if aplicar:
            datos = descargar(rel["tarball_url"])
            with tarfile.open(fileobj=io.BytesIO(datos), mode="r:gz") as tar:
                raiz = tar.getmembers()[0].name.split("/")[0]
                miembros = [m for m in tar.getmembers() if any(m.name.startswith(f"{raiz}/{t}/") for t in faltan)]
                for m in miembros:
                    m.name = m.name.split("/", 1)[1]
                tar.extractall(ICONOS, members=miembros, filter="data")
            print(f"  Papirus instalado: {len(miembros)} archivos")
    carpetas_en_color(aplicar)


def carpetas_en_color(aplicar: bool) -> None:
    """Como papirus-folders: en cada tamaño de places/, `folder-*.svg` pasa a enlazar `folder-<color>-*.svg`."""
    n = 0
    for tema in PAPIRUS["temas"]:
        for places in (ICONOS / tema).glob("*/places"):
            for fuente in places.glob(f"folder-{COLOR_CARPETAS}-*.svg"):
                destino = places / fuente.name.replace(f"folder-{COLOR_CARPETAS}-", "folder-")
                if destino.name == fuente.name:
                    continue
                if aplicar:
                    if destino.is_symlink() or destino.exists():
                        destino.unlink()
                    destino.symlink_to(fuente.name)
                n += 1
            # la carpeta base y la abierta
            for nombre in ("folder", "folder-open"):
                fuente = places / f"folder-{COLOR_CARPETAS}{nombre[6:]}.svg"
                if fuente.exists():
                    destino = places / f"{nombre}.svg"
                    if aplicar:
                        if destino.is_symlink() or destino.exists():
                            destino.unlink()
                        destino.symlink_to(fuente.name)
                    n += 1
    print(f"  {'carpetas' if aplicar else 'SIM carpetas'} de Papirus en «{COLOR_CARPETAS}»: {n} enlaces")
    if aplicar and shutil.which("gtk-update-icon-cache"):
        for tema in PAPIRUS["temas"]:
            subprocess.run(["gtk-update-icon-cache", "-f", "-q", str(ICONOS / tema)], capture_output=True)


def bibata(aplicar: bool) -> None:
    faltan = {a: t for a, t in BIBATA["activos"].items() if not (ICONOS / t / "cursors").exists()}
    if not faltan:
        print(f"  Bibata ya está en {ICONOS} ({', '.join(BIBATA['activos'].values())})"); return
    rel = api(f"https://api.github.com/repos/{BIBATA['repo']}/releases/latest")
    urls = {a["name"]: a["browser_download_url"] for a in rel["assets"]}
    for activo, tema in faltan.items():
        print(f"  {'descargar' if aplicar else 'SIM descargar'} {tema} {rel['tag_name']} ({BIBATA['licencia']}) → {ICONOS}/{tema}")
        if aplicar and activo in urls:
            with tarfile.open(fileobj=io.BytesIO(descargar(urls[activo])), mode="r:xz") as tar:
                tar.extractall(ICONOS, filter="data")


def whitesur_cursores(aplicar: bool) -> None:
    tema = WHITESUR_CURSORES["tema"]
    donde = [d for d in (ICONOS / tema, HOME / ".icons" / tema) if (d / "cursors").is_dir()]
    if donde:
        print(f"  {tema} ya está en {donde[0]}"); return
    print(f"  {'descargar' if aplicar else 'SIM descargar'} {tema} (rama principal, {WHITESUR_CURSORES['licencia']}) → {ICONOS}/{tema}")
    if not aplicar:
        return
    datos = descargar(f"https://api.github.com/repos/{WHITESUR_CURSORES['repo']}/tarball")
    with tarfile.open(fileobj=io.BytesIO(datos), mode="r:gz") as tar:
        raiz = tar.getmembers()[0].name.split("/")[0]
        miembros = [m for m in tar.getmembers() if m.name.startswith(f"{raiz}/dist/") and m.name != f"{raiz}/dist"]
        for m in miembros:
            m.name = tema + "/" + m.name.split("/", 2)[2]
        tar.extractall(ICONOS, members=miembros, filter="data")
    print(f"  {tema} instalado: {len(miembros)} archivos")


def fuentes() -> None:
    r = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout.splitlines()
    for f, paquete in (("Inter", "fonts-inter"), ("Hack", "fonts-hack")):
        hay = any(f in linea.split(",") for linea in r)
        print(f"  {'ok ' if hay else 'FALTA'} tipografía {f}" + ("" if hay else f" (sudo apt install {paquete})"))


def main() -> int:
    aplicar = "--aplicar" in sys.argv
    print(f"{'Instalando' if aplicar else 'SIMULACIÓN de'} dependencias en {ICONOS}")
    ICONOS.mkdir(parents=True, exist_ok=True)
    whitesur_cursores(aplicar)
    fuentes()
    if "--opcionales" in sys.argv:
        papirus(aplicar)
        bibata(aplicar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
