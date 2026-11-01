"""Dependencias de terceros del módulo de iconos y cursores, instaladas en el usuario (`instalar.py dependencias`):

- Cursores: WhiteSur-cursors (GPL-3.0; vinceliuice; KDE Store 1411743), línea base del autor (docs/linea-base.md). El
  repositorio no publica versiones: se toma `dist/` del tarball de la rama principal.
- Iconos (mejora 3, decisiones 4.7 y 4.15): Papirus (Papirus, Papirus-Dark, Papirus-Light; GPL-3.0;
  PapirusDevelopmentTeam) tal como se publica, y el tema superpuesto `Papirus-Dark-Lliphi` con las carpetas rojas
  para el oscuro (enlaces simbólicos a las `folder-red-*` de Papirus); heredan de Breeze.
- Opcional (`--opcionales`; probado en 0.2.0 y fuera de la línea base): cursores Bibata Modern Classic e Ice (GPL-3.0; ful1e5).

Se descargan de GitHub a `$XDG_DATA_HOME/icons/`; nada en `/usr`. Lo descargado no se redistribuye en este
repositorio: se cita y se enlaza (licencias en el sitio). Antes vivía en `herramientas/dependencias.py`."""
from __future__ import annotations

import io
import re
import shutil
import subprocess
import tarfile
from pathlib import Path

from nucleo.descargas import HOME, ICONOS, api, descargar

PAPIRUS = {"repo": "PapirusDevelopmentTeam/papirus-icon-theme", "temas": ["Papirus", "Papirus-Dark", "Papirus-Light"], "licencia": "GPL-3.0-only"}
BIBATA = {"repo": "ful1e5/Bibata_Cursor", "activos": {"Bibata-Modern-Classic.tar.xz": "Bibata-Modern-Classic", "Bibata-Modern-Ice.tar.xz": "Bibata-Modern-Ice"}, "licencia": "GPL-3.0-only"}
WHITESUR_CURSORES = {"repo": "vinceliuice/WhiteSur-cursors", "tema": "WhiteSur-cursors", "licencia": "GPL-3.0-only"}
# Carpetas en el acento de cada variante (decisiones 4.12 y 4.15). Papirus-Dark comparte con Papirus los tamaños grandes
# por enlaces, así que no se pueden colorear distinto modificando sus archivos: Papirus se deja tal cual (carpetas azules,
# las de su versión publicada, para el claro) y el oscuro usa un tema superpuesto pequeño, Papirus-Dark-Lliphi, que hereda
# de Papirus-Dark y solo declara sus carpetas de lugares con enlaces a las rojas de Papirus.
COLOR_ORIGINAL = "blue"                 # el de la versión publicada de Papirus
SUPERPUESTO = {"id": "Papirus-Dark-Lliphi", "base": "Papirus-Dark", "color": "red", "nombre": "Papirus Dark (Lliphi, carpetas rojas)"}


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


def _enlazar_carpetas(places: Path, color: str, destino: Path, aplicar: bool) -> int:
    """En `destino`, `folder-*.svg` → `places/folder-<color>-*.svg` (y `folder.svg`, `folder-open.svg`)."""
    n = 0
    pares = [(f, f.name.replace(f"folder-{color}-", "folder-")) for f in places.glob(f"folder-{color}-*.svg")]
    pares += [(places / f"folder-{color}{nombre[6:]}.svg", f"{nombre}.svg") for nombre in ("folder", "folder-open")]
    for fuente, nombre in pares:
        if not fuente.exists() or nombre == fuente.name:
            continue
        if aplicar:
            enlace = destino / nombre
            if enlace.is_symlink() or enlace.exists():
                enlace.unlink()
            enlace.symlink_to(fuente if destino != places else fuente.name)
        n += 1
    return n


def carpetas_en_color(aplicar: bool) -> None:
    """Papirus vuelve a sus carpetas de origen (azules) y se crea el superpuesto con las rojas para el oscuro."""
    import configparser
    n = 0
    for tema in PAPIRUS["temas"]:   # deshace lo que hacía la mejora 3 (rojo dentro de Papirus): versión publicada
        for places in (ICONOS / tema).glob("*/places"):
            if not places.is_symlink():
                n += _enlazar_carpetas(places, COLOR_ORIGINAL, places, aplicar)
    print(f"  {'carpetas' if aplicar else 'SIM carpetas'} de Papirus a su color de origen ({COLOR_ORIGINAL}): {n} enlaces")
    base = ICONOS / SUPERPUESTO["base"]
    cfg = configparser.ConfigParser(strict=False, interpolation=None); cfg.optionxform = str
    cfg.read(base / "index.theme", encoding="utf-8")
    raiz = ICONOS / SUPERPUESTO["id"]
    patron = re.compile(rf"^(folder|user)-{COLOR_ORIGINAL}(-.*)?\.svg$")   # carpetas y carpetas de usuario (user-home…)
    usados, m = [], 0
    # todo icono (lugares, tipos de archivo como inode-directory, carpetas de usuario…) que acaba en una carpeta azul
    for d in cfg["Icon Theme"]["Directories"].split(","):
        carpeta = base / d
        if not carpeta.is_dir():
            continue
        enlaces = []
        for f in carpeta.iterdir():
            if not f.is_symlink():
                continue
            final = f.resolve()
            if (mt := patron.match(final.name)) and (roja := final.with_name(f"{mt.group(1)}-{SUPERPUESTO['color']}{mt.group(2) or ''}.svg")).exists():
                enlaces.append((f.name, roja))
        if enlaces:
            usados.append(d); m += len(enlaces)
            if aplicar:
                (raiz / d).mkdir(parents=True, exist_ok=True)
                for nombre, roja in enlaces:
                    enlace = raiz / d / nombre
                    if enlace.is_symlink() or enlace.exists():
                        enlace.unlink()
                    enlace.symlink_to(roja)
    if aplicar:
        lineas = ["[Icon Theme]", f"Name={SUPERPUESTO['nombre']}", "Comment=Papirus-Dark con las carpetas en el rojo de Lliphi (herramientas/dependencias.py)",
                  f"Inherits={SUPERPUESTO['base']},breeze-dark,hicolor", f"Directories={','.join(usados)}", "Hidden=false", ""]
        for d in usados:
            lineas += [f"[{d}]", *[f"{k}={v}" for k, v in cfg[d].items()], ""]
        (raiz / "index.theme").write_text("\n".join(lineas), encoding="utf-8")
    print(f"  {'tema' if aplicar else 'SIM tema'} {SUPERPUESTO['id']} ({len(usados)} carpetas del tema, carpetas {SUPERPUESTO['color']}): {m} enlaces")
    if aplicar and shutil.which("gtk-update-icon-cache"):
        for tema in [*PAPIRUS["temas"], SUPERPUESTO["id"]]:
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


def instalar(aplicar: bool, opcionales: bool = False) -> None:
    ICONOS.mkdir(parents=True, exist_ok=True)
    whitesur_cursores(aplicar)
    papirus(aplicar)          # mejora 3 (decisiones 4.7): Papirus con carpetas rojas es parte de la línea base
    if opcionales:
        bibata(aplicar)
