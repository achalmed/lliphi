"""Dependencias de terceros del módulo de iconos y cursores, instaladas en el usuario (`instalar.py dependencias`):

- Cursores: WhiteSur-cursors (GPL-3.0; vinceliuice; KDE Store 1411743), línea base del autor (docs/linea-base.md). El
  repositorio no publica versiones: se toma `dist/` del tarball de la rama principal.
- Iconos (mejora 3, decisiones 4.7 y 4.15): Papirus (Papirus, Papirus-Dark, Papirus-Light; GPL-3.0;
  PapirusDevelopmentTeam) tal como se publica, y el tema superpuesto `Papirus-Dark-Lliphi` con las carpetas rojas
  para el oscuro (enlaces simbólicos a las `folder-red-*` de Papirus); heredan de Breeze.
- Bandeja (decisiones 4.35): el superpuesto `<tema>-Lliphi` de cada tema de iconos de Lliphi (Colloid), construido
  aquí desde el tema instalado (no se descarga nada): sus iconos simbólicos de estado, aplicaciones y dispositivos en
  22 px con el dibujo en 16 centrado (`con_margen`), en carpetas de tamaño fijo 22 que solo se usan a ese tamaño.
- Opcional (`--opcionales`; probado en 0.2.0 y fuera de la línea base): cursores Bibata Modern Classic e Ice (GPL-3.0; ful1e5).

Se descargan de GitHub a `$XDG_DATA_HOME/icons/`; nada en `/usr`. Lo descargado no se redistribuye en este
repositorio: se cita y se enlaza (licencias en el sitio). Antes vivía en `herramientas/dependencias.py`."""
from __future__ import annotations

import configparser
import io
import json
import re
import shutil
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

from nucleo.descargas import HOME, ICONOS, api, descargar

PAPIRUS = {"repo": "PapirusDevelopmentTeam/papirus-icon-theme", "temas": ["Papirus", "Papirus-Dark", "Papirus-Light"], "licencia": "GPL-3.0-only"}
BIBATA = {"repo": "ful1e5/Bibata_Cursor", "activos": {"Bibata-Modern-Classic.tar.xz": "Bibata-Modern-Classic", "Bibata-Modern-Ice.tar.xz": "Bibata-Modern-Ice"}, "licencia": "GPL-3.0-only"}
WHITESUR_CURSORES = {"repo": "vinceliuice/WhiteSur-cursors", "tema": "WhiteSur-cursors", "licencia": "GPL-3.0-only"}
# Carpetas en el acento de cada variante (decisiones 4.12 y 4.15). Papirus-Dark comparte con Papirus los tamaños grandes
# por enlaces, así que no se pueden colorear distinto modificando sus archivos: Papirus se deja tal cual (carpetas azules,
# las de su versión publicada, para el claro) y el oscuro usa un tema superpuesto pequeño, Papirus-Dark-Lliphi, que hereda
# de Papirus-Dark y solo declara sus carpetas de lugares con enlaces a las rojas de Papirus.
# El color y los nombres están en ajustes.json (lo edita Lliphi Studio).
_AJUSTES = json.loads((Path(__file__).resolve().parent / "ajustes.json").read_text(encoding="utf-8"))
COLOR_ORIGINAL = _AJUSTES["color_original"]     # el de la versión publicada de Papirus
SUPERPUESTO = _AJUSTES["superpuesto"]


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


SVG = "http://www.w3.org/2000/svg"
for _prefijo, _uri in (("", SVG), ("xlink", "http://www.w3.org/1999/xlink"), ("inkscape", "http://www.inkscape.org/namespaces/inkscape"),
                       ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"), ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
                       ("cc", "http://creativecommons.org/ns#"), ("dc", "http://purl.org/dc/elements/1.1/")):
    ET.register_namespace(_prefijo, _uri)
CONTEXTO = {"status": "Status", "apps": "Applications", "devices": "Devices", "actions": "Actions", "places": "Places",
            "emblems": "Emblems", "categories": "Categories", "mimetypes": "MimeTypes"}
GEOMETRIA = {"width", "height", "viewBox", "version", "x", "y", "enable-background", "id"}


def _numero(valor: str | None) -> float | None:
    m = re.match(r"\s*([0-9.]+)", valor or "")
    return float(m.group(1)) if m else None


def con_margen(texto: str, tamano: int = 22, contenido: int = 16) -> str:
    """Un icono en un lienzo de `tamano` con su lienzo original reducido a `contenido` y centrado, como los iconos de ese
    tamaño del tema (16 dentro de 22: 3 px de margen). Lo que no es geometría del `<svg>` raíz (clase, relleno, estilo,
    color) pasa al grupo que envuelve el dibujo, para que siga heredándose; la hoja `current-color-scheme` se queda donde
    estaba y Plasma sigue recoloreando el icono."""
    raiz = ET.fromstring(texto)
    caja = [float(x) for x in re.split(r"[\s,]+", raiz.get("viewBox", "").strip()) if x] or \
        [0.0, 0.0, _numero(raiz.get("width")) or 16.0, _numero(raiz.get("height")) or 16.0]
    x0, y0, ancho, alto = caja
    escala = contenido / max(ancho, alto)
    dx, dy = (tamano - ancho * escala) / 2, (tamano - alto * escala) / 2
    grupo = ET.Element(f"{{{SVG}}}g", {"transform": f"translate({dx:g} {dy:g}) scale({escala:g}) translate({-x0:g} {-y0:g})"})
    for clave in [k for k in raiz.attrib if k not in GEOMETRIA and not k.startswith("{")]:
        grupo.set(clave, raiz.attrib.pop(clave))
    for hijo in list(raiz):
        raiz.remove(hijo)
        grupo.append(hijo)
    raiz.append(grupo)
    raiz.set("width", str(tamano)); raiz.set("height", str(tamano)); raiz.set("viewBox", f"0 0 {tamano} {tamano}")
    return ET.tostring(raiz, encoding="unicode") + "\n"


def _carpeta_tema(tema: str) -> Path | None:
    return next((d / tema for d in (ICONOS, HOME / ".icons", Path("/usr/share/icons")) if (d / tema / "index.theme").exists()), None)


def bandeja(aplicar: bool, silencio: bool = False) -> list[str]:
    """Construye `<tema><sufijo>` para cada tema de iconos de las variantes (decisiones 4.35) y devuelve los creados."""
    aj = _AJUSTES.get("bandeja", {})
    if not aj.get("activo"):
        return []
    creados = []
    for base in dict.fromkeys(_AJUSTES["iconos"].values()):
        origen = _carpeta_tema(base)
        destino_id = f"{base}{aj['sufijo']}"
        if origen is None:
            if not silencio:
                print(f"  {destino_id}: falta {base}; no se construye")
            continue
        cfg = configparser.ConfigParser(strict=False, interpolation=None); cfg.optionxform = str
        cfg.read(origen / "index.theme", encoding="utf-8")
        carpetas = {}
        for d in cfg["Icon Theme"].get("Directories", "").split(","):
            contexto, _, tipo = d.strip().partition("/")
            if tipo == "symbolic" and contexto in aj["contextos"] and (origen / d).is_dir():
                carpetas[contexto] = sorted(f for f in (origen / d).iterdir() if f.suffix == ".svg")
        n = sum(len(v) for v in carpetas.values())
        if not silencio:
            print(f"  {'tema' if aplicar else 'SIM tema'} {destino_id}: {n} iconos simbólicos en {aj['tamano']} px con el dibujo en "
                  f"{aj['contenido']} ({', '.join(carpetas)}), sobre {base}")
        if not aplicar:
            continue
        raiz = ICONOS / destino_id
        if raiz.is_symlink():          # p. ej. en la sesión de prueba, un enlace al tema del usuario: no se sigue
            raiz.unlink()
        elif raiz.exists():
            shutil.rmtree(raiz)
        directorios, fallos = [], 0
        for contexto, archivos in carpetas.items():
            d = f"{contexto}/symbolic-{aj['tamano']}"
            (raiz / d).mkdir(parents=True, exist_ok=True)
            directorios.append(d)
            for f in archivos:
                try:
                    (raiz / d / f.name).write_text(con_margen(f.resolve().read_text(encoding="utf-8"), aj["tamano"], aj["contenido"]), encoding="utf-8")
                except (ET.ParseError, OSError, ValueError):
                    fallos += 1      # se queda el de la base
        kde = [f"{k}={v}" for k, v in cfg["Icon Theme"].items() if k not in ("Name", "Comment", "Inherits", "Directories", "ScaledDirectories", "Hidden", "Example")]
        lineas = ["[Icon Theme]", f"Name={base} (Lliphi)", f"Comment={base} con los iconos simbólicos de la bandeja a la medida del resto (Lliphi)",
                  f"Inherits={base},{cfg['Icon Theme'].get('Inherits', 'hicolor')}", *kde, f"Directories={','.join(directorios)}", "Hidden=false", ""]
        for d in directorios:
            lineas += [f"[{d}]", f"Size={aj['tamano']}", f"Context={CONTEXTO.get(d.split('/')[0], 'Status')}", "Type=Fixed", ""]
        (raiz / "index.theme").write_text("\n".join(lineas), encoding="utf-8")
        if shutil.which("gtk-update-icon-cache"):
            subprocess.run(["gtk-update-icon-cache", "-f", "-q", str(raiz)], capture_output=True)
        creados.append(destino_id)
        if not silencio and fallos:
            print(f"    {fallos} iconos no se pudieron leer: se usan los de {base}")
    return creados


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


def colloid() -> None:
    """Colloid Grey (los iconos de Lliphi, decisiones 4.22) se instala con el guion de su autor, que construye las
    variantes desde las fuentes: aquí solo se comprueba y se dice cómo; Lliphi no ejecuta código descargado."""
    temas = list(dict.fromkeys(_AJUSTES["iconos"].values()))
    faltan = [t for t in temas if not (ICONOS / t / "index.theme").exists() and not (Path("/usr/share/icons") / t / "index.theme").exists()]
    if not faltan:
        print(f"  {', '.join(temas)} ya están en {ICONOS}")
        return
    print(f"  faltan {', '.join(faltan)} (Colloid, GPL-3.0; vinceliuice/Colloid-icon-theme). Instálalo con el guion de su autor:\n"
          "    git clone https://github.com/vinceliuice/Colloid-icon-theme && cd Colloid-icon-theme && ./install.sh -t grey\n"
          f"  mientras tanto se aplica la reserva ({', '.join(_AJUSTES.get('reserva', {}).values())})")


def instalar(aplicar: bool, opcionales: bool = False) -> None:
    ICONOS.mkdir(parents=True, exist_ok=True)
    colloid()
    bandeja(aplicar)          # el superpuesto de la bandeja sobre Colloid (decisiones 4.35)
    whitesur_cursores(aplicar)
    papirus(aplicar)          # la reserva (mejora 3, decisiones 4.7 y 4.22): Papirus y su superpuesto de carpetas rojas
    if opcionales:
        bibata(aplicar)
