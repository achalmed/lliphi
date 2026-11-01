"""Plasma Studio: explorador y previsualización del estilo de Plasma (módulo `estilo`).

Biblioteca: los SVG del estilo por carpeta. Lienzo: el marco elegido (panel, diálogo, botón, tooltip…) compuesto a
cualquier tamaño, como lo hace Plasma, con Lliphi Oscuro, Lliphi Claro y la base de WhiteSur lado a lado; o la rejilla de
todos los elementos con nombre. Propiedades: los marcos y elementos del archivo, el tamaño, los colores del esquema y la
copia para Inkscape. Abajo: el SVG, el diff contra la base (el recoloreo) y los colores que usa.

Esta versión explora y compara: el estilo sale de WhiteSur recoloreado por `modulos/estilo/construir.py`; para dibujar,
Inkscape abre una copia en la caché del studio.
"""
from __future__ import annotations

import difflib

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QPushButton, QSpinBox, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo

from lliphi_studio import pintor, proyecto, svgplasma
from lliphi_studio.comun import Editor, Lienzo, nota
from lliphi_studio.paginas.color import muestra

ORIGEN = {"oscuro": "WhiteSur-dark", "claro": "WhiteSur"}
ESQUEMA = {"oscuro": "LliphiOscuro", "claro": "LliphiClaro"}


def carpeta(variante: str, base: bool = False):
    if base:
        return proyecto.raiz() / "fuentes" / "base" / "WhiteSur-kde" / "plasma" / "desktoptheme" / ORIGEN[variante]
    return proyecto.raiz() / "generado" / "estilo" / f"{proyecto.marca()['id']}-{variante}"


class LienzoPlasma(Lienzo):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.columnas: list[tuple[str, object, str]] = []   # (título, renderizador, variante)
        self.sobre_fondo = True
        self._fondos: dict[str, QPixmap] = {}
        self.prefijo: str | None = None
        self.elemento: str | None = None
        self.ancho, self.alto = 320, 200
        self.modo = "marco"

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        t = self.tokens()
        f = QFont(self.font())
        f.setPointSizeF(8.5)
        p.setFont(f)
        if not self.columnas:
            p.setPen(QColor(t["texto_tenue"]))
            p.drawText(rect, Qt.AlignCenter, "Elige un SVG del estilo en la biblioteca")
            return
        if self.modo == "elementos":
            self._rejilla(p, rect, self.columnas[0][1], t)
            return
        n = len(self.columnas)
        ancho_col = (rect.width() - 20) / n
        for i, (titulo, r, var) in enumerate(self.columnas):
            col = QRectF(10 + i * ancho_col, 10, ancho_col - 10, rect.height() - 20)
            if self.sobre_fondo:
                pm = self._fondo(var)
                if pm is not None:
                    zona_f = col.adjusted(0, 22, 0, 0)
                    p.save()
                    p.setClipRect(zona_f)
                    escala = max(zona_f.width() / pm.width(), zona_f.height() / pm.height())
                    p.drawPixmap(QRectF(zona_f.x(), zona_f.y(), pm.width() * escala, pm.height() * escala), pm, QRectF(pm.rect()))
                    p.restore()
            p.setPen(QColor(t["texto_suave"]))
            p.drawText(QRectF(col.x(), col.y(), col.width(), 18), Qt.AlignCenter, titulo)
            zona = col.adjusted(8, 26, -8, -8)
            k = min(zona.width() / self.ancho, zona.height() / self.alto, 1.0) * self.zoom
            w, h = self.ancho * k, self.alto * k
            destino = QRectF(zona.center().x() - w / 2, zona.center().y() - h / 2, w, h)
            if self.prefijo is not None and self.prefijo in svgplasma.marcos(svgplasma.elementos(r.texto)):
                pintor.marco(p, r, self.prefijo, destino, k)
            elif self.elemento:
                pintor.elemento(p, r, self.elemento, destino)
            p.setPen(QPen(QColor(t["borde_fuerte"]), 1, Qt.DotLine))
            p.setBrush(Qt.NoBrush)
            p.drawRect(destino)

    def _fondo(self, var: str) -> QPixmap | None:
        if var not in self._fondos:
            ruta = proyecto.fondo(var)
            self._fondos[var] = QPixmap(str(ruta)).scaledToWidth(960, Qt.SmoothTransformation) if ruta else None
        return self._fondos[var]

    def _rejilla(self, p: QPainter, rect: QRectF, r, t: dict) -> None:
        ids = svgplasma.elementos(r.texto)
        celda = 110 * self.zoom
        por_fila = max(1, int((rect.width() - 10) // celda))
        for i, id_ in enumerate(ids):
            x, y = 6 + (i % por_fila) * celda, 6 + (i // por_fila) * (celda + 4)
            if y > rect.height():
                break
            caja = QRectF(x, y, celda - 8, celda - 22)
            p.setPen(QPen(QColor(t["borde"]), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(caja, 4, 4)
            pintor.elemento(p, r, id_, caja.adjusted(6, 6, -6, -6))
            p.setPen(QColor(t["acento"] if id_ == self.elemento else t["texto_tenue"]))
            p.drawText(QRectF(x, y + celda - 22, celda - 8, 16), Qt.AlignCenter,
                       p.fontMetrics().elidedText(id_, Qt.ElideMiddle, int(celda - 10)))


class Pagina:
    def __init__(self, v):
        self.v = v
        self.ruta_rel: str | None = None
        bib = QWidget()
        bv = QVBoxLayout(bib)
        bv.setContentsMargins(0, 0, 0, 0)
        self.variante = QComboBox()
        self.variante.addItem("Lliphi Oscuro", "oscuro")
        self.variante.addItem("Lliphi Claro", "claro")
        self.variante.currentIndexChanged.connect(self._llenar)
        bv.addWidget(self.variante)
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Filtrar (panel, button, tooltip…)")
        self.filtro.textChanged.connect(self._filtrar)
        bv.addWidget(self.filtro)
        self.arbol = QTreeWidget()
        self.arbol.setHeaderHidden(True)
        self.arbol.currentItemChanged.connect(self._elegir)
        bv.addWidget(self.arbol, 1)
        self.lienzo = LienzoPlasma(v.tokens)
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.titulo = QLabel("—")
        self.titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        self.titulo.setWordWrap(True)
        pv.addWidget(self.titulo)
        self.info = nota("")
        pv.addWidget(self.info)
        modo = QHBoxLayout()
        self.modo = QComboBox()
        self.modo.addItem("Marco compuesto", "marco")
        self.modo.addItem("Todos los elementos", "elementos")
        self.modo.currentIndexChanged.connect(self._cambiar_modo)
        modo.addWidget(self.modo, 1)
        pv.addLayout(modo)
        pv.addWidget(clase(QLabel("Marcos (nueve piezas)"), "suave"))
        self.lista_marcos = QListWidget()
        self.lista_marcos.setMaximumHeight(140)
        self.lista_marcos.currentItemChanged.connect(self._elegir_marco)
        pv.addWidget(self.lista_marcos)
        pv.addWidget(clase(QLabel("Elementos sueltos"), "suave"))
        self.lista_sueltos = QListWidget()
        self.lista_sueltos.setMaximumHeight(120)
        self.lista_sueltos.currentItemChanged.connect(self._elegir_suelto)
        pv.addWidget(self.lista_sueltos)
        form = QFormLayout()
        self.s_ancho, self.s_alto = QSpinBox(), QSpinBox()
        for s, val in ((self.s_ancho, 320), (self.s_alto, 200)):
            s.setRange(8, 1600)
            s.setValue(val)
            s.valueChanged.connect(self._tamano)
        form.addRow("ancho", self.s_ancho)
        form.addRow("alto", self.s_alto)
        pv.addLayout(form)
        self.con_colores = QCheckBox("Colores del esquema de la variante (como Plasma)")
        self.con_colores.setChecked(True)
        self.con_colores.toggled.connect(self._cargar)
        pv.addWidget(self.con_colores)
        self.fondo = QCheckBox("Sobre el fondo de Lliphi (lo translúcido)")
        self.fondo.setChecked(True)
        self.fondo.toggled.connect(lambda x: (setattr(self.lienzo, "sobre_fondo", x), self.lienzo.update()))
        pv.addWidget(self.fondo)
        self.comparar = QCheckBox("Comparar las dos variantes y la base de WhiteSur")
        self.comparar.setChecked(True)
        self.comparar.toggled.connect(self._cargar)
        pv.addWidget(self.comparar)
        fila = QHBoxLayout()
        b = QPushButton(icono_trazo("abrir"), " Copia en Inkscape")
        b.clicked.connect(self._inkscape)
        fila.addWidget(b)
        b = QPushButton(icono_trazo("abrir"), " Base")
        b.setToolTip("Abre en Inkscape una copia del SVG de WhiteSur del que deriva")
        b.clicked.connect(lambda: self._inkscape(base=True))
        fila.addWidget(b)
        pv.addLayout(fila)
        pv.addStretch(1)
        self.editor = Editor("Plasma", "El estilo de Plasma de Lliphi: cada SVG con sus marcos de nueve piezas compuestos como "
                             "los dibuja Plasma, las dos variantes y la base de WhiteSur lado a lado.",
                             bib, self.lienzo, props, v.tokens)
        self.editor.boton("Recargar", "sincronizar", self._llenar)
        self.editor.boton("Construir (simular)", "capas",
                          lambda: v.correr(proyecto.orden("generar", "--modulos", "estilo"), "Construir estilo (simulación)"))
        self.editor.pestanas.setTabText(0, "SVG")
        self.editor.pestanas.setTabText(1, "Recoloreo (diff contra WhiteSur)")
        self.colores = QListWidget()
        self.editor.pestana(self.colores, "Colores", "paleta")
        self.widget = self.editor
        self._llenar()

    def _llenar(self) -> None:
        self.arbol.clear()
        var = self.variante.currentData()
        primero = None
        for sub, archivos in svgplasma.archivos(carpeta(var)).items():
            g = QTreeWidgetItem(self.arbol, [sub])
            for a in archivos:
                it = QTreeWidgetItem(g, [a.name])
                it.setData(0, Qt.UserRole, str(a.relative_to(carpeta(var))))
                if a.name == "panel-background.svg":
                    primero = it
        self.arbol.expandAll()
        if primero:
            self.arbol.setCurrentItem(primero)

    def _filtrar(self, texto: str) -> None:
        for i in range(self.arbol.topLevelItemCount()):
            g = self.arbol.topLevelItem(i)
            visibles = 0
            for j in range(g.childCount()):
                oculto = texto.lower() not in g.child(j).text(0).lower()
                g.child(j).setHidden(oculto)
                visibles += not oculto
            g.setHidden(visibles == 0)

    def _elegir(self, it, _prev=None) -> None:
        rel = it.data(0, Qt.UserRole) if it else None
        if rel:
            self.ruta_rel = rel
            self._cargar()

    def _renderizador(self, var: str, base: bool = False):
        ruta = carpeta(var, base) / self.ruta_rel
        if not ruta.exists() and ruta.with_suffix(".svgz").exists():   # WhiteSur trae algunos comprimidos
            ruta = ruta.with_suffix(".svgz")
        if not ruta.exists():
            return None, None
        texto = svgplasma.leer(ruta)
        if self.con_colores.isChecked():
            texto = svgplasma.con_esquema(texto, svgplasma.esquema(proyecto.raiz() / "generado" / "esquema" / f"{ESQUEMA[var]}.colors"))
        r = pintor.renderizador(texto)
        r.texto = texto
        return r, ruta

    def _cargar(self) -> None:
        if not self.ruta_rel:
            return
        var = self.variante.currentData()
        r, ruta = self._renderizador(var)
        if r is None:
            return
        columnas = [(f"Lliphi {var.capitalize()}", r, var)]
        if self.comparar.isChecked():
            otra = "claro" if var == "oscuro" else "oscuro"
            r2, _ = self._renderizador(otra)
            if r2:
                columnas.append((f"Lliphi {otra.capitalize()}", r2, otra))
            rb, _ = self._renderizador(var, base=True)
            if rb:
                columnas.append((f"{ORIGEN[var]} (base)", rb, var))
        self.lienzo.columnas = columnas
        ids = svgplasma.elementos(r.texto)
        marcos = svgplasma.marcos(ids)
        sueltos = svgplasma.sueltos(ids)
        self.titulo.setText(self.ruta_rel)
        instalado = proyecto.data_home() / "plasma" / "desktoptheme" / ruta.parent.relative_to(proyecto.raiz() / "generado" / "estilo")
        self.info.setText(f"{len(ids)} elementos · {len(marcos)} marco(s) · {ruta.stat().st_size // 1024 + 1} KB<br>"
                          f"tema <code>{carpeta(var).name}</code>{' · instalado en tu usuario' if instalado.exists() else ''}")
        self.lista_marcos.blockSignals(True)
        self.lista_marcos.clear()
        for m in marcos:
            self.lista_marcos.addItem(m or "(sin prefijo)")
        self.lista_marcos.blockSignals(False)
        self.lista_sueltos.blockSignals(True)
        self.lista_sueltos.clear()
        self.lista_sueltos.addItems(sueltos)
        self.lista_sueltos.blockSignals(False)
        if marcos:
            preferido = "" if "" in marcos else ("normal" if "normal" in marcos else marcos[0])
            self.lienzo.prefijo = preferido
            self.lienzo.elemento = None
            self.lista_marcos.setCurrentRow(marcos.index(preferido))
        else:
            self.lienzo.prefijo = None
            self.lienzo.elemento = sueltos[0] if sueltos else (ids[0] if ids else None)
        self.editor.codigo.setPlainText(r.texto if len(r.texto) < 400_000 else r.texto[:400_000] + "\n…")
        base = carpeta(var, True) / self.ruta_rel
        base = base if base.exists() else base.with_suffix(".svgz")
        if base.exists():
            diff = "".join(difflib.unified_diff(svgplasma.leer(base).splitlines(True), svgplasma.leer(ruta).splitlines(True),
                                                f"WhiteSur/{self.ruta_rel}", f"lliphi/{self.ruta_rel}", n=1))
            self.editor.diff.setPlainText(diff or "Idéntico a la base de WhiteSur.")
        else:
            self.editor.diff.setPlainText("No hay archivo de la base con este nombre (propio de Lliphi).")
        self.colores.clear()
        for h in svgplasma.colores_usados(svgplasma.leer(ruta)):
            self.colores.addItem(QListWidgetItem(muestra(h), h))
        self.lienzo.update()

    def _elegir_marco(self, it, _prev=None) -> None:
        if it:
            self.lienzo.prefijo = "" if it.text() == "(sin prefijo)" else it.text()
            self.lienzo.elemento = None
            self.modo.setCurrentIndex(0)
            self.lienzo.update()

    def _elegir_suelto(self, it, _prev=None) -> None:
        if it:
            self.lienzo.prefijo = None
            self.lienzo.elemento = it.text()
            self.lienzo.update()

    def _cambiar_modo(self) -> None:
        self.lienzo.modo = self.modo.currentData()
        self.lienzo.update()

    def _tamano(self) -> None:
        self.lienzo.ancho, self.lienzo.alto = self.s_ancho.value(), self.s_alto.value()
        self.lienzo.update()

    def _inkscape(self, base: bool = False) -> None:
        if not self.ruta_rel:
            return
        var = self.variante.currentData()
        origen = carpeta(var, base) / self.ruta_rel
        copia = pintor.copia_para_inkscape(origen, f"estilo-{'base-' if base else ''}{var}")
        if pintor.abrir_en_inkscape(copia):
            self.v.marco.avisar("Inkscape abre una copia", str(copia), "info")
        else:
            self.v.marco.avisar("No está Inkscape", f"La copia quedó en {copia}", "aviso")

    def repintar(self) -> None:
        self.lienzo.update()
