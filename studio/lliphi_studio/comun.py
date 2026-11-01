"""Piezas comunes de las páginas: la disposición de editor (biblioteca · lienzo · propiedades · código), el lienzo con
zoom, el visor de código con resaltado de diff y JSON, y las tarjetas de orden con «Simular» y «Aplicar»."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QSizePolicy, QSplitter,
                               QTabWidget, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo, variante
from gui_comun.widgets.tarjetas import Tarjeta, encabezado


def mono() -> QFont:
    f = QFont("JetBrains Mono")
    f.setStyleHint(QFont.Monospace)
    f.setPointSize(9)
    return f


class Resaltado(QSyntaxHighlighter):
    """Colorea un diff (+, -, @@) y, en JSON, claves y números."""

    def __init__(self, documento, tokens: Callable[[], dict]):
        super().__init__(documento)
        self.tokens = tokens

    def highlightBlock(self, texto: str) -> None:
        t = self.tokens()
        def fmt(color: str, negrita: bool = False) -> QTextCharFormat:
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if negrita:
                f.setFontWeight(QFont.Bold)
            return f
        if texto.startswith("+") and not texto.startswith("+++"):
            self.setFormat(0, len(texto), fmt(t["exito"]))
        elif texto.startswith("-") and not texto.startswith("---"):
            self.setFormat(0, len(texto), fmt(t["error"]))
        elif texto.startswith("@@") or texto.startswith("+++") or texto.startswith("---"):
            self.setFormat(0, len(texto), fmt(t["info"], True))
        else:
            import re
            for m in re.finditer(r'"[^"]*"(?=\s*:)', texto):
                self.setFormat(m.start(), m.end() - m.start(), fmt(t["acento"]))
            for m in re.finditer(r"(?<![\w#])-?\d+(\.\d+)?", texto):
                self.setFormat(m.start(), m.end() - m.start(), fmt(t["info"]))
            for m in re.finditer(r"//.*$|#.*$", texto):
                if not texto[m.start():].startswith("#") or texto.lstrip().startswith("#"):
                    self.setFormat(m.start(), m.end() - m.start(), fmt(t["texto_tenue"]))


class Codigo(QPlainTextEdit):
    def __init__(self, tokens: Callable[[], dict], solo_lectura: bool = True):
        super().__init__()
        self.setReadOnly(solo_lectura)
        self.setFont(mono())
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.resaltado = Resaltado(self.document(), tokens)


class Editor(QWidget):
    """La disposición de Qt Design Studio: biblioteca a la izquierda, lienzo al centro, propiedades a la derecha y, abajo,
    el código (el borrador, el diff contra el proyecto, lo generado). Arriba, el título y la barra de acciones."""

    def __init__(self, titulo: str, subtitulo: str, biblioteca: QWidget, lienzo: QWidget, propiedades: QWidget,
                 tokens: Callable[[], dict]):
        super().__init__()
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(20, 14, 20, 10)
        raiz.setSpacing(8)
        cabeza = QHBoxLayout()
        cabeza.addWidget(encabezado(titulo, subtitulo), 1)
        self.acciones = QHBoxLayout()
        self.acciones.setSpacing(6)
        cabeza.addLayout(self.acciones)
        raiz.addLayout(cabeza)
        self.vertical = QSplitter(Qt.Vertical)
        self.horizontal = QSplitter(Qt.Horizontal)
        for w, ancho in ((biblioteca, 250), (lienzo, 640), (propiedades, 300)):
            marco = QFrame()
            clase(marco, "tarjeta")
            marco.setAttribute(Qt.WA_StyledBackground, True)
            v = QVBoxLayout(marco)
            v.setContentsMargins(8, 8, 8, 8)
            v.addWidget(w)
            self.horizontal.addWidget(marco)
        self.horizontal.setSizes([250, 640, 300])
        self.horizontal.setStretchFactor(1, 1)
        self.vertical.addWidget(self.horizontal)
        self.pestanas = QTabWidget()
        self.codigo = Codigo(tokens)
        self.diff = Codigo(tokens)
        self.pestanas.addTab(self.codigo, icono_trazo("codigo"), "Código")
        self.pestanas.addTab(self.diff, icono_trazo("texto"), "Cambios")
        self.vertical.addWidget(self.pestanas)
        self.vertical.setSizes([560, 170])
        self.vertical.setStretchFactor(0, 1)
        raiz.addWidget(self.vertical, 1)

    def boton(self, texto: str, icono: str, al_clic: Callable[[], None], tipo: str | None = None) -> QPushButton:
        b = QPushButton(icono_trazo(icono), f" {texto}")
        if tipo:
            variante(b, tipo)
        b.clicked.connect(al_clic)
        self.acciones.addWidget(b)
        return b

    def pestana(self, widget: QWidget, nombre: str, icono: str = "documento") -> None:
        self.pestanas.addTab(widget, icono_trazo(icono), nombre)


class Lienzo(QWidget):
    """Superficie de previsualización con zoom (Ctrl + rueda) y un fondo de tablero tenue. Las subclases pintan en
    `pintar(p, rect)`, con `rect` ya escalado al zoom."""

    zoom_cambiado = Signal(float)

    def __init__(self, tokens: Callable[[], dict]):
        super().__init__()
        self.tokens = tokens
        self.zoom = 1.0
        self.tablero = True
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def wheelEvent(self, e) -> None:
        if e.modifiers() & Qt.ControlModifier:
            self.zoom = max(0.25, min(6.0, self.zoom * (1.15 if e.angleDelta().y() > 0 else 1 / 1.15)))
            self.zoom_cambiado.emit(self.zoom)
            self.update()
        else:
            super().wheelEvent(e)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        t = self.tokens()
        p.fillRect(self.rect(), QColor(t["consola"]))
        if self.tablero:
            p.setPen(Qt.NoPen)
            c = QColor(t["borde"])
            c.setAlpha(70)
            p.setBrush(c)
            paso = 16
            for y in range(0, self.height(), paso):
                for x in range((y // paso) % 2 * paso, self.width(), paso * 2):
                    p.drawRect(x, y, paso, paso)
        p.save()
        self.pintar(p, QRectF(self.rect()))
        p.restore()
        p.end()

    def pintar(self, p: QPainter, rect: QRectF) -> None:   # para las subclases
        pass


class TarjetaOrden(Tarjeta):
    """Una orden de Lliphi: qué hace y sus botones («Simular» sin escribir; «Aplicar» tras confirmar)."""

    def __init__(self, titulo: str, texto: str, icono: str = "terminal"):
        super().__init__()
        cabeza = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(icono_trazo(icono).pixmap(20, 20))
        cabeza.addWidget(ic)
        t = QLabel(titulo)
        t.setStyleSheet("font-weight: 600; font-size: 14px;")
        cabeza.addWidget(t, 1)
        self.cuerpo.addLayout(cabeza)
        d = clase(QLabel(texto), "tenue")
        d.setWordWrap(True)
        d.setTextFormat(Qt.RichText)
        self.cuerpo.addWidget(d)
        self.extra = QHBoxLayout()
        self.cuerpo.addLayout(self.extra)
        self.botones = QHBoxLayout()
        self.botones.addStretch(1)
        self.cuerpo.addLayout(self.botones)

    def boton(self, texto: str, al_clic: Callable[[], None], tipo: str | None = None, icono: str | None = None) -> QPushButton:
        b = QPushButton(icono_trazo(icono), f" {texto}") if icono else QPushButton(texto)
        if tipo:
            variante(b, tipo)
        b.clicked.connect(al_clic)
        self.botones.addWidget(b)
        return b


def nota(texto: str) -> QLabel:
    l = clase(QLabel(texto), "tenue")
    l.setWordWrap(True)
    l.setTextFormat(Qt.RichText)
    l.setTextInteractionFlags(Qt.TextBrowserInteraction)
    l.setOpenExternalLinks(True)
    return l


def envolver(panel: QWidget) -> QWidget:
    """Un panel de propiedades con desplazamiento vertical (para ventanas bajas o con la consola abierta)."""
    from PySide6.QtWidgets import QScrollArea
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    area.setWidget(panel)
    return area
