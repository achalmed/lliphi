"""Temas de iconos y de cursores freedesktop, sin Qt: qué temas hay, su cadena `Inherits`, dónde está un icono (con la
búsqueda del estándar: tamaño exacto, escalable, después los temas heredados y `hicolor`) y los cursores Xcursor
(cada imagen con su tamaño, punto activo y retardo de animación)."""
from __future__ import annotations

import configparser
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path

from lliphi_studio import proyecto

EXTENSIONES = (".svg", ".png", ".svgz", ".xpm")
CURSORES_COMUNES = ("default", "left_ptr", "pointer", "hand2", "text", "xterm", "wait", "watch", "progress", "help",
                    "crosshair", "move", "fleur", "not-allowed", "grab", "grabbing", "copy", "alias", "context-menu",
                    "col-resize", "row-resize", "n-resize", "e-resize", "ne-resize", "nw-resize", "zoom-in", "zoom-out",
                    "all-scroll", "cell", "vertical-text")
COLORES_PAPIRUS = ("adwaita", "black", "blue", "bluegrey", "breeze", "brown", "carmine", "cyan", "darkcyan", "deeporange",
                   "green", "grey", "indigo", "magenta", "nordic", "orange", "palebrown", "paleorange", "pink", "red",
                   "teal", "violet", "white", "yaru", "yellow")


def bases() -> list[Path]:
    return [proyecto.data_home() / "icons", proyecto.home() / ".icons", Path("/usr/share/icons")]


@dataclass
class Directorio:
    ruta: str
    tam: int
    contexto: str
    tipo: str
    escala: int = 1
    minimo: int = 0
    maximo: int = 0


@dataclass
class Tema:
    id: str
    carpeta: Path
    nombre: str
    comentario: str = ""
    hereda: list[str] = field(default_factory=list)
    directorios: list[Directorio] = field(default_factory=list)
    cursores: bool = False

    @property
    def contextos(self) -> list[str]:
        return sorted({d.contexto for d in self.directorios if d.contexto})


def leer_tema(carpeta: Path) -> Tema | None:
    indice = carpeta / "index.theme"
    if not indice.exists():
        return Tema(carpeta.name, carpeta, carpeta.name, cursores=True) if (carpeta / "cursors").is_dir() else None
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    try:
        cfg.read(indice, encoding="utf-8")
    except configparser.Error:
        return None
    g = cfg["Icon Theme"] if cfg.has_section("Icon Theme") else {}
    dirs = []
    for d in (g.get("Directories", "") + "," + g.get("ScaledDirectories", "")).split(","):
        d = d.strip()
        if d and cfg.has_section(d):
            s = cfg[d]
            tam = int(s.get("Size", "0") or 0)
            dirs.append(Directorio(d, tam, s.get("Context", ""), s.get("Type", "Threshold"), int(s.get("Scale", "1") or 1),
                                   int(s.get("MinSize", tam) or tam), int(s.get("MaxSize", tam) or tam)))
    return Tema(carpeta.name, carpeta.resolve(), g.get("Name", carpeta.name), g.get("Comment", ""),
                [x.strip() for x in g.get("Inherits", "").split(",") if x.strip()], dirs, (carpeta / "cursors").is_dir())


def temas() -> dict[str, Tema]:
    """Los temas de iconos y cursores visibles para el usuario (el primero que aparece en las bases gana)."""
    salida: dict[str, Tema] = {}
    for base in bases():
        for c in sorted(base.iterdir()) if base.is_dir() else []:
            if c.is_dir() and c.name not in salida and (t := leer_tema(c)) is not None:
                salida[c.name] = t
    return salida


def cadena(tema: str, todos: dict[str, Tema] | None = None) -> list[str]:
    """El tema y los que hereda, en el orden de búsqueda, acabando en hicolor."""
    todos = todos or temas()
    orden, pendientes = [], [tema]
    while pendientes:
        t = pendientes.pop(0)
        if t in orden or t not in todos:
            continue
        orden.append(t)
        pendientes += todos[t].hereda
    orden = [t for t in orden if t != "hicolor"]   # hicolor, siempre al final (el estándar)
    return orden + (["hicolor"] if "hicolor" in todos else [])


def _encaja(d: Directorio, tam: int) -> int:
    if d.tipo == "Scalable" and d.minimo <= tam <= d.maximo:
        return 0
    return abs(d.tam - tam)


def buscar(tema: str, nombre: str, tam: int = 48, todos: dict[str, Tema] | None = None) -> tuple[Path, str] | None:
    """(archivo, tema que lo da) para un icono, o None."""
    todos = todos or temas()
    for t in cadena(tema, todos):
        candidatos = []
        for d in todos[t].directorios:
            for ext in EXTENSIONES:
                p = todos[t].carpeta / d.ruta / f"{nombre}{ext}"
                if p.exists():
                    candidatos.append((_encaja(d, tam), d.escala, p))
                    break
        if candidatos:
            return sorted(candidatos, key=lambda x: (x[0], x[1]))[0][2], t
    return None


def nombres(tema: Tema, contexto: str | None = None, limite: int = 4000) -> list[str]:
    """Los nombres de icono del tema (de un contexto, si se pide), sin repetir."""
    vistos: set[str] = set()
    for d in tema.directorios:
        if contexto and d.contexto != contexto:
            continue
        carpeta = tema.carpeta / d.ruta
        for p in carpeta.iterdir() if carpeta.is_dir() else []:
            if p.suffix in EXTENSIONES:
                vistos.add(p.stem)
        if len(vistos) >= limite:
            break
    return sorted(vistos)[:limite]


def colores_de_carpeta(tema: str = "Papirus", todos: dict[str, Tema] | None = None) -> list[str]:
    """Los colores de carpeta que trae Papirus (`folder-<color>.svg`)."""
    todos = todos or temas()
    if tema not in todos:
        return []
    for d in todos[tema].directorios:
        if d.contexto == "Places" and d.tam >= 48:
            carpeta = todos[tema].carpeta / d.ruta
            hallados = {m.group(1) for p in carpeta.glob("folder-*.svg") if (m := re.fullmatch(r"folder-([a-z]+)", p.stem))}
            return [c for c in COLORES_PAPIRUS if c in hallados]
    return []


# ------------------------------------------------------------------ Xcursor

@dataclass
class Imagen:
    nominal: int
    ancho: int
    alto: int
    xhot: int
    yhot: int
    retardo: int
    pixeles: bytes            # ARGB premultiplicado, little-endian (32 bits por píxel)


def leer_xcursor(ruta: Path) -> list[Imagen]:
    """Las imágenes de un archivo Xcursor (todas las de todos los tamaños nominales, en el orden del archivo)."""
    datos = ruta.read_bytes()
    if datos[:4] != b"Xcur":
        return []
    _cab, _ver, n = struct.unpack_from("<III", datos, 4)
    salida = []
    for i in range(n):
        tipo, _subtipo, pos = struct.unpack_from("<III", datos, 16 + i * 12)
        if tipo != 0xFFFD0002:
            continue
        _hs, _t, nominal, _v, w, h, xh, yh, retardo = struct.unpack_from("<9I", datos, pos)
        inicio = pos + 36
        salida.append(Imagen(nominal, w, h, xh, yh, retardo, datos[inicio:inicio + w * h * 4]))
    return salida


def cursores(tema: Tema) -> list[str]:
    """Los cursores del tema: primero los comunes que tiene, después el resto (sin los alias de un solo carácter)."""
    carpeta = tema.carpeta / "cursors"
    todos = sorted(p.name for p in carpeta.iterdir()) if carpeta.is_dir() else []
    return [c for c in CURSORES_COMUNES if c in todos] + [c for c in todos if c not in CURSORES_COMUNES and len(c) > 2]


def tamanos(imagenes: list[Imagen]) -> list[int]:
    return sorted({i.nominal for i in imagenes})
