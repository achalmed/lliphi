"""Dibujar SVG de Plasma y de Aurorae con `QSvgRenderer`: un elemento por su id, un marco de nueve piezas a cualquier
tamaño (esquinas a su tamaño, bordes y centro estirados, como `Plasma::FrameSvg`) y copias para Inkscape."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from PySide6.QtCore import QByteArray, QProcess, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtSvg import QSvgRenderer

from lliphi_studio import proyecto, svgplasma


def renderizador(texto: str) -> QSvgRenderer:
    return QSvgRenderer(QByteArray(texto.encode("utf-8")))


def tam(r: QSvgRenderer, id_: str) -> tuple[float, float]:
    b = r.boundsOnElement(id_) if r.elementExists(id_) else QRectF()
    return b.width(), b.height()


def elemento(p: QPainter, r: QSvgRenderer, id_: str, destino: QRectF, encajar: bool = True) -> None:
    """Un elemento dentro de `destino` (manteniendo la proporción si `encajar`)."""
    if not r.elementExists(id_):
        return
    if encajar:
        w, h = tam(r, id_)
        if w > 0 and h > 0:
            k = min(destino.width() / w, destino.height() / h)
            destino = QRectF(destino.center().x() - w * k / 2, destino.center().y() - h * k / 2, w * k, h * k)
    r.render(p, id_, destino)


def marco(p: QPainter, r: QSvgRenderer, prefijo: str, destino: QRectF, escala: float = 1.0) -> None:
    """El marco `prefijo` sobre `destino`: las esquinas a su tamaño (por `escala`), los bordes y el centro estirados."""
    pz = lambda n: svgplasma.pieza(prefijo, n)   # noqa: E731
    wl, ht = (x * escala for x in tam(r, pz("topleft")))
    wr, _ = (x * escala for x in tam(r, pz("topright")))
    _, hb = (x * escala for x in tam(r, pz("bottomleft")))
    wl, wr = min(wl, destino.width() / 2), min(wr, destino.width() / 2)
    ht, hb = min(ht, destino.height() / 2), min(hb, destino.height() / 2)
    x0, y0, x1, y1 = destino.left(), destino.top(), destino.right(), destino.bottom()
    cw, ch = max(0.0, destino.width() - wl - wr), max(0.0, destino.height() - ht - hb)
    for nombre, rect in (("topleft", QRectF(x0, y0, wl, ht)), ("top", QRectF(x0 + wl, y0, cw, ht)),
                         ("topright", QRectF(x1 - wr, y0, wr, ht)), ("left", QRectF(x0, y0 + ht, wl, ch)),
                         ("center", QRectF(x0 + wl, y0 + ht, cw, ch)), ("right", QRectF(x1 - wr, y0 + ht, wr, ch)),
                         ("bottomleft", QRectF(x0, y1 - hb, wl, hb)), ("bottom", QRectF(x0 + wl, y1 - hb, cw, hb)),
                         ("bottomright", QRectF(x1 - wr, y1 - hb, wr, hb))):
        if rect.width() > 0 and rect.height() > 0 and r.elementExists(pz(nombre)):
            r.render(p, pz(nombre), rect)


def copia_para_inkscape(origen: Path, etiqueta: str) -> Path:
    """Una copia del SVG en la caché del studio (lo generado no se edita; la base de terceros, tampoco)."""
    base = Path(os.environ.get("XDG_CACHE_HOME") or proyecto.home() / ".cache") / "lliphi-studio" / "inkscape" / etiqueta
    base.mkdir(parents=True, exist_ok=True)
    destino = base / origen.name
    shutil.copy2(origen, destino)
    return destino


def abrir_en_inkscape(ruta: Path) -> bool:
    return bool(shutil.which("inkscape")) and QProcess.startDetached("inkscape", [str(ruta)])[0]
