"""Icon Studio: explorador y organizador de iconos y cursores (módulo `iconos-cursores`).

Biblioteca: los temas de iconos y de cursores del usuario y del sistema, con los que usa Lliphi marcados. Lienzo: los
iconos del tema (por contexto, con búsqueda y a cualquier tamaño) sobre el fondo de la variante, o los cursores con su
animación. Propiedades: la ficha del tema y su cadena `Inherits`, de qué tema sale el icono elegido y cómo se ve en los
demás; el organizador del superpuesto (el color de carpetas de Papirus de la variante oscura), el tema de cada variante y
el de cursores. Se edita un borrador de `modulos/iconos-cursores/ajustes.json`.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListView, QListWidget,
                               QListWidgetItem, QMessageBox, QPushButton, QScrollArea, QSlider, QStackedWidget,
                               QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo

from lliphi_studio import iconos, proyecto
from lliphi_studio.comun import Editor, Lienzo, nota

COMPARAR = ("Papirus", "Papirus-Dark", "Papirus-Dark-Lliphi", "breeze", "breeze-dark")


class LienzoCursores(Lienzo):
    """Los cursores de un tema, animados, al tamaño nominal elegido."""

    def __init__(self, tokens):
        super().__init__(tokens)
        self.tema: iconos.Tema | None = None
        self.tam = 48
        self.cuadros: dict[str, list] = {}
        self.paso = 0
        self.fondo = "#1e1e1e"
        self.reloj = QTimer(self)
        self.reloj.setInterval(40)
        self.reloj.timeout.connect(self._tic)
        self.elegido: str | None = None

    def cargar(self, tema: iconos.Tema) -> None:
        self.tema = tema
        self.cuadros = {}
        for nombre in iconos.cursores(tema)[:60]:
            imagenes = [i for i in iconos.leer_xcursor(tema.carpeta / "cursors" / nombre)]
            if imagenes:
                self.cuadros[nombre] = imagenes
        self.reloj.start()
        self.update()

    def _tic(self) -> None:
        self.paso += 40
        if self.isVisible():
            self.update()

    def mousePressEvent(self, e) -> None:
        celda = 104 * self.zoom
        por_fila = max(1, int(self.width() // celda))
        i = int(e.position().y() // (celda + 6)) * por_fila + int(e.position().x() // celda)
        nombres = list(self.cuadros)
        if 0 <= i < len(nombres):
            self.elegido = nombres[i]
            self.update()

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        t = self.tokens()
        p.fillRect(rect, QColor(self.fondo))
        if not self.cuadros:
            p.setPen(QColor(t["texto_tenue"]))
            p.drawText(rect, Qt.AlignCenter, "Este tema no trae cursores")
            return
        celda = 104 * self.zoom
        por_fila = max(1, int(rect.width() // celda))
        f = QFont(self.font())
        f.setPointSizeF(8)
        p.setFont(f)
        for i, (nombre, imagenes) in enumerate(self.cuadros.items()):
            x, y = (i % por_fila) * celda, (i // por_fila) * (celda + 6)
            if y > rect.height():
                break
            del_tam = [im for im in imagenes if im.nominal == self.tam] or imagenes
            total = sum(max(1, im.retardo) for im in del_tam)
            momento = self.paso % max(1, total)
            cuadro = del_tam[0]
            for im in del_tam:
                momento -= max(1, im.retardo)
                if momento < 0:
                    cuadro = im
                    break
            img = QImage(cuadro.pixeles, cuadro.ancho, cuadro.alto, QImage.Format_ARGB32_Premultiplied)
            caja = QRectF(x + 6, y + 6, celda - 12, celda - 30)
            if nombre == self.elegido:
                p.setPen(QColor(t["acento"]))
                p.drawRoundedRect(caja.adjusted(-3, -3, 3, 3), 6, 6)
            p.drawImage(QRectF(caja.center().x() - cuadro.ancho / 2, caja.center().y() - cuadro.alto / 2, cuadro.ancho, cuadro.alto), img)
            p.setPen(QColor("#ffffff" if QColor(self.fondo).lightness() < 128 else "#222222"))
            p.drawText(QRectF(x, y + celda - 24, celda, 16), Qt.AlignCenter, p.fontMetrics().elidedText(nombre, Qt.ElideRight, int(celda - 6)))


class Pagina:
    def __init__(self, v):
        self.v = v
        self.datos = proyecto.leer_borrador("iconos-cursores")
        self.todos = iconos.temas()
        # biblioteca
        self.arbol = QTreeWidget()
        self.arbol.setHeaderHidden(True)
        self.arbol.currentItemChanged.connect(self._elegir_tema)
        # lienzo: iconos o cursores
        centro = QWidget()
        cv = QVBoxLayout(centro)
        cv.setContentsMargins(0, 0, 0, 0)
        fila = QHBoxLayout()
        self.contexto = QComboBox()
        self.contexto.currentIndexChanged.connect(self._llenar_iconos)
        fila.addWidget(self.contexto)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Buscar icono (folder, dolphin, document…)")
        self.busca.textChanged.connect(self._llenar_iconos)
        fila.addWidget(self.busca, 1)
        self.fondo = QComboBox()
        self.fondo.addItem("sobre el oscuro", "oscuro")
        self.fondo.addItem("sobre el claro", "claro")
        self.fondo.currentIndexChanged.connect(self._fondo)
        fila.addWidget(self.fondo)
        self.tam = QSlider(Qt.Horizontal)
        self.tam.setRange(16, 128)
        self.tam.setValue(48)
        self.tam.setFixedWidth(120)
        self.tam.valueChanged.connect(self._tam)
        fila.addWidget(self.tam)
        cv.addLayout(fila)
        self.pila = QStackedWidget()
        self.rejilla = QListWidget()
        self.rejilla.setViewMode(QListView.IconMode)
        self.rejilla.setResizeMode(QListView.Adjust)
        self.rejilla.setMovement(QListView.Static)
        self.rejilla.setUniformItemSizes(True)
        self.rejilla.setWordWrap(True)
        self.rejilla.currentItemChanged.connect(self._elegir_icono)
        self.pila.addWidget(self.rejilla)
        self.cursores = LienzoCursores(v.tokens)
        self.pila.addWidget(self.cursores)
        cv.addWidget(self.pila, 1)
        # propiedades
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.titulo = QLabel("—")
        self.titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        pv.addWidget(self.titulo)
        self.ficha = nota("")
        pv.addWidget(self.ficha)
        pv.addWidget(clase(QLabel("El mismo icono en otros temas"), "suave"))
        self.comparacion = QHBoxLayout()
        self.etiquetas_cmp = []
        for t in COMPARAR:
            caja = QVBoxLayout()
            img = QLabel()
            img.setFixedSize(52, 52)
            img.setAlignment(Qt.AlignCenter)
            caja.addWidget(img, 0, Qt.AlignHCenter)
            nombre = clase(QLabel(t.replace("Papirus-", "P-")), "tenue")
            nombre.setAlignment(Qt.AlignCenter)
            caja.addWidget(nombre)
            self.comparacion.addLayout(caja)
            self.etiquetas_cmp.append((t, img))
        pv.addLayout(self.comparacion)
        self.icono_info = nota("")
        pv.addWidget(self.icono_info)
        pv.addSpacing(6)
        pv.addWidget(clase(QLabel("Organizador (borrador de ajustes)"), "suave"))
        form = QFormLayout()
        nombres_iconos = sorted(t for t, x in self.todos.items() if x.directorios)
        nombres_cursores = sorted(t for t, x in self.todos.items() if x.cursores)
        self.c_claro, self.c_oscuro, self.c_cursor = QComboBox(), QComboBox(), QComboBox()
        for cb, lista in ((self.c_claro, nombres_iconos), (self.c_oscuro, nombres_iconos), (self.c_cursor, nombres_cursores)):
            cb.addItems(lista)
        self.c_claro.currentTextChanged.connect(lambda x: self._poner(("iconos", "claro"), x))
        self.c_oscuro.currentTextChanged.connect(lambda x: self._poner(("iconos", "oscuro"), x))
        self.c_cursor.currentTextChanged.connect(lambda x: self._poner(("cursores",), x))
        form.addRow("iconos del claro", self.c_claro)
        form.addRow("iconos del oscuro", self.c_oscuro)
        form.addRow("cursores", self.c_cursor)
        pv.addLayout(form)
        pv.addWidget(clase(QLabel(f"Carpetas de {self.datos['superpuesto']['id']} (color de Papirus)"), "tenue"))
        self.muestrario = QListWidget()
        self.muestrario.setViewMode(QListView.IconMode)
        self.muestrario.setIconSize(QSize(34, 34))
        self.muestrario.setGridSize(QSize(66, 62))
        self.muestrario.setMovement(QListView.Static)
        self.muestrario.setResizeMode(QListView.Adjust)
        self.muestrario.setMinimumHeight(190)
        papirus = self.todos.get(self.datos["superpuesto"]["base"].replace("-Dark", "")) or self.todos.get("Papirus")
        for color in iconos.colores_de_carpeta("Papirus", self.todos):
            r = iconos.buscar("Papirus", f"folder-{color}", 64, self.todos) if papirus else None
            it = QListWidgetItem(QIcon(str(r[0])) if r else QIcon(), color)
            it.setData(Qt.UserRole, color)
            self.muestrario.addItem(it)
        self.muestrario.itemClicked.connect(self._color)
        pv.addWidget(self.muestrario)
        botones = QHBoxLayout()
        b = QPushButton(icono_trazo("terminal"), " Superpuesto (simular)")
        b.clicked.connect(lambda: v.correr(proyecto.orden("instalar", "dependencias"), "Dependencias (simulación)"))
        botones.addWidget(b)
        pv.addLayout(botones)
        pv.addStretch(1)
        envoltura = QScrollArea()
        envoltura.setWidgetResizable(True)
        envoltura.setWidget(props)
        envoltura.setFrameShape(QScrollArea.NoFrame)
        envoltura.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor = Editor("Iconos y cursores", "Los temas de iconos y de cursores (Papirus, el superpuesto de carpetas "
                             "de Lliphi, WhiteSur-cursors…): explorar, comparar, ver la animación de cada cursor y organizar "
                             "qué usa cada variante.", self.arbol, centro, envoltura, v.tokens)
        self.editor.boton("Descartar", "volver", self._descartar)
        self.editor.boton("Guardar y construir…", "verificar", self._guardar, "primario")
        self.indice = self.editor.codigo.__class__(v.tokens)
        self.editor.pestana(self.indice, "index.theme", "texto")
        self.widget = self.editor
        self._llenar_arbol()
        self._a_campos()
        self._mostrar()

    # ---------------------------------------------------------------- temas
    def _llenar_arbol(self) -> None:
        self.arbol.clear()
        usados = {self.datos["iconos"]["claro"]: "claro", self.datos["iconos"]["oscuro"]: "oscuro", self.datos["cursores"]: "cursores"}
        grupos = {"Iconos": QTreeWidgetItem(self.arbol, ["Temas de iconos"]), "Cursores": QTreeWidgetItem(self.arbol, ["Temas de cursores"])}
        elegir = None
        for id_, t in self.todos.items():
            for clave, grupo in (("Iconos", t.directorios), ("Cursores", t.cursores)):
                if not grupo:
                    continue
                marca = f"  · Lliphi {usados[id_]}" if id_ in usados else ""
                it = QTreeWidgetItem(grupos[clave], [f"{t.nombre}{marca}"])
                it.setToolTip(0, str(t.carpeta))
                it.setData(0, Qt.UserRole, (id_, clave))
                if id_ == self.datos["iconos"]["oscuro"] and clave == "Iconos":
                    elegir = it
        self.arbol.expandAll()
        if elegir:
            self.arbol.setCurrentItem(elegir)

    def _elegir_tema(self, it, _prev=None) -> None:
        dato = it.data(0, Qt.UserRole) if it else None
        if not dato:
            return
        self.tema_id, tipo = dato
        t = self.todos[self.tema_id]
        self.titulo.setText(t.nombre)
        cad = iconos.cadena(self.tema_id, self.todos)
        usos = [f"iconos del {v}" for v, x in self.datos["iconos"].items() if x == self.tema_id]
        usos += ["cursores de Lliphi"] if self.datos["cursores"] == self.tema_id else []
        corta = str(t.carpeta).replace(str(proyecto.home()), "~")
        self.ficha.setToolTip(str(t.carpeta))
        self.ficha.setText(f"<code>{corta}</code><br>{t.comentario}<br>hereda: {' → '.join(cad[1:]) or '—'}<br>"
                           f"{len(t.directorios)} carpetas · contextos: {', '.join(t.contextos) or '—'}"
                           + (f"<br><b>lo usa Lliphi:</b> {', '.join(usos)}" if usos else ""))
        indice = t.carpeta / "index.theme"
        self.indice.setPlainText(indice.read_text(encoding="utf-8", errors="replace")[:200_000] if indice.exists() else "(sin index.theme)")
        if tipo == "Cursores":
            self.pila.setCurrentWidget(self.cursores)
            self.cursores.cargar(t)
            for w in (self.contexto, self.busca):
                w.setEnabled(False)
            return
        for w in (self.contexto, self.busca):
            w.setEnabled(True)
        self.pila.setCurrentWidget(self.rejilla)
        self.contexto.blockSignals(True)
        self.contexto.clear()
        self.contexto.addItem("todos los contextos", None)
        for c in t.contextos:
            self.contexto.addItem(c, c)
        i = self.contexto.findData("Places")
        self.contexto.setCurrentIndex(max(0, i))
        self.contexto.blockSignals(False)
        self._llenar_iconos()

    def _llenar_iconos(self) -> None:
        if self.pila.currentWidget() is not self.rejilla or not getattr(self, "tema_id", None):
            return
        t = self.todos[self.tema_id]
        filtro = self.busca.text().strip().lower()
        nombres = [n for n in iconos.nombres(t, self.contexto.currentData()) if filtro in n.lower()][:1200]
        self.rejilla.clear()
        tam = self.tam.value()
        self.rejilla.setIconSize(QSize(tam, tam))
        self.rejilla.setGridSize(QSize(max(tam + 40, 96), tam + 40))
        for n in nombres:
            r = iconos.buscar(self.tema_id, n, tam, self.todos)
            if r:
                it = QListWidgetItem(QIcon(str(r[0])), n)
                it.setData(Qt.UserRole, (n, str(r[0]), r[1]))
                it.setToolTip(f"{n}\n{r[0]}")
                self.rejilla.addItem(it)
        self._fondo()

    def _elegir_icono(self, it, _prev=None) -> None:
        if not it:
            return
        nombre, ruta, de = it.data(Qt.UserRole)
        self.icono_info.setText(f"<b>{nombre}</b><br>sale de <b>{de}</b>" + ("" if de == self.tema_id else " (heredado)")
                                + f"<br><code>{Path(ruta).parent.name}/{Path(ruta).name}</code>")
        self.icono_info.setToolTip(ruta)
        for t, img in self.etiquetas_cmp:
            r = iconos.buscar(t, nombre, 48, self.todos) if t in self.todos else None
            img.setPixmap(QIcon(str(r[0])).pixmap(44, 44) if r else QPixmap())
            img.setToolTip(f"{t}: {r[1] if r else 'no lo tiene'}")

    def _fondo(self) -> None:
        var = self.fondo.currentData()
        tok = {k: x["$value"]["hex"] for k, x in proyecto.tokens()["semanticos"][var]["fondo"].items()}
        txt = proyecto.tokens()["semanticos"][var]["texto"]["normal"]["$value"]["hex"]
        self.rejilla.setStyleSheet(f"QListWidget {{ background: {tok['vista']}; color: {txt}; border-radius: 8px; }}")
        self.cursores.fondo = tok["vista"]
        self.cursores.update()

    def _tam(self) -> None:
        self.cursores.tam = min((24, 30, 36, 48), key=lambda x: abs(x - self.tam.value()))
        self._llenar_iconos()

    # ---------------------------------------------------------------- organizador
    def _a_campos(self) -> None:
        for cb, valor in ((self.c_claro, self.datos["iconos"]["claro"]), (self.c_oscuro, self.datos["iconos"]["oscuro"]),
                          (self.c_cursor, self.datos["cursores"])):
            cb.blockSignals(True)
            cb.setCurrentText(valor)
            cb.blockSignals(False)
        for i in range(self.muestrario.count()):
            it = self.muestrario.item(i)
            it.setSelected(it.data(Qt.UserRole) == self.datos["superpuesto"]["color"])

    def _poner(self, ruta: tuple, valor: str) -> None:
        d = self.datos
        for k in ruta[:-1]:
            d = d[k]
        d[ruta[-1]] = valor
        self._tras_cambiar()

    def _color(self, it) -> None:
        color = it.data(Qt.UserRole)
        self.datos["superpuesto"]["color"] = color
        self.datos["superpuesto"]["nombre"] = f"Papirus Dark (Lliphi, carpetas {color})"
        self._tras_cambiar()

    def _tras_cambiar(self) -> None:
        proyecto.guardar_borrador("iconos-cursores", self.datos)
        self._mostrar()

    def _mostrar(self) -> None:
        self.editor.codigo.setPlainText(proyecto.volcar("iconos-cursores", self.datos))
        diff = proyecto.diff_ajustes("iconos-cursores", self.datos)
        self.editor.diff.setPlainText(diff or "El borrador es igual a modulos/iconos-cursores/ajustes.json.")

    def _descartar(self) -> None:
        proyecto.descartar_borrador("iconos-cursores")
        self.datos = proyecto.leer_ajustes("iconos-cursores")
        self._a_campos()
        self._mostrar()
        self._llenar_arbol()

    def _guardar(self) -> None:
        diff = proyecto.diff_ajustes("iconos-cursores", self.datos)
        if not diff:
            self.v.marco.avisar("Sin cambios", "El borrador es igual a los ajustes del proyecto.", "info")
            return
        caja = QMessageBox(QMessageBox.Question, "Guardar iconos y cursores",
                           "Escribe modulos/iconos-cursores/ajustes.json, reconstruye el tema global (que nombra los temas) "
                           "y valida. Si cambiaste el color de las carpetas, el superpuesto se rehace en tu usuario con "
                           "«instalar.py dependencias --aplicar» (en Construir y desplegar). ¿Seguir?",
                           QMessageBox.Yes | QMessageBox.No, self.v.ui)
        caja.setDetailedText(diff)
        if caja.exec() != QMessageBox.Yes:
            return
        proyecto.guardar_ajustes("iconos-cursores", self.datos)
        proyecto.descartar_borrador("iconos-cursores")
        self._mostrar()
        self._llenar_arbol()
        self.v.cadena([(proyecto.orden("generar", "--modulos", "global", "--aplicar"), "Construir tema global"),
                       (proyecto.orden("generar", "validar"), "Validar")])

    def repintar(self) -> None:
        self._fondo()
