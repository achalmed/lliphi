"""Color Studio: el editor de la paleta (módulo `esquema`).

Biblioteca: los neutros, los acentos, los estados y la terminal de las dos variantes. Lienzo: la interfaz de muestra con
la variante clara y la oscura lado a lado (ventana, vista con selección, botones, foco, enlace, estados, tooltip y la
terminal de 16 colores), con simulación de daltonismo. Propiedades: L, C y H de cada color y el acento de cada variante.
Abajo: el borrador, el diff contra el proyecto, la tabla de contraste y dónde se usa cada color.

Se edita un borrador (`$XDG_STATE_HOME/lliphi-studio/borradores/esquema.json`); las cifras salen de `paleta.py
--ajustes <borrador> --json`. «Guardar y construir» escribe `modulos/esquema/ajustes.json` (solo si todos los pares
cumplen) y corre `paleta.py --aplicar`, `generar.py --aplicar` y `generar.py validar`.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QHeaderView, QLabel, QListWidget,
                               QListWidgetItem, QMessageBox, QSlider, QTableWidget, QTableWidgetItem, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo

from lliphi_studio import color, proyecto
from lliphi_studio.comun import Editor, Lienzo, nota

VARIANTES = ("claro", "oscuro")
NOMBRE_ACENTO = {"base": "acento", "suave": "acento-suave", "texto": "acento-texto"}


def muestra(hex_: str, tam: int = 14) -> QIcon:
    pm = QPixmap(tam, tam)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(hex_))
    p.setPen(QPen(QColor(128, 128, 128, 110), 1))
    p.drawRoundedRect(QRectF(0.5, 0.5, tam - 1, tam - 1), 3, 3)
    p.end()
    return QIcon(pm)


def obtener(datos: dict, ruta: tuple):
    for k in ruta:
        datos = datos[k]
    return datos


def poner(datos: dict, ruta: tuple, valor) -> None:
    for k in ruta[:-1]:
        datos = datos[k]
    datos[ruta[-1]] = valor


class Maqueta(Lienzo):
    """La interfaz de muestra de las dos variantes con los colores del informe de la paleta."""

    def __init__(self, tokens):
        super().__init__(tokens)
        self.informe: dict | None = None
        self.daltonismo: str | None = None
        self.tablero = False
        self.setMinimumSize(560, 430)

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        t = self.tokens()
        if not self.informe:
            p.setPen(QColor(t["texto_tenue"]))
            p.drawText(rect, Qt.AlignCenter, "Calculando la paleta…")
            return
        p.scale(self.zoom, self.zoom)
        ancho = (rect.width() / self.zoom - 30) / 2
        for i, v in enumerate(VARIANTES):
            self._variante(p, QRectF(10 + i * (ancho + 10), 10, ancho, rect.height() / self.zoom - 20), v)

    def _c(self, hex_: str) -> QColor:
        return QColor(color.simular(hex_, self.daltonismo))

    def _variante(self, p: QPainter, r: QRectF, v: str) -> None:
        s = {k: x["hex"] for k, x in self.informe["variantes"][v]["semanticos"].items()}
        term = {k: x["hex"] for k, x in self.informe["variantes"][v]["terminal"].items()}
        c = self._c
        f = QFont(self.font())
        f.setPointSizeF(9)
        p.setFont(f)
        # ventana
        p.setPen(QPen(c(s["borde.separador"]), 1))
        p.setBrush(c(s["fondo.ventana"]))
        p.drawRoundedRect(r, 10, 10)
        cab = QRectF(r.x(), r.y(), r.width(), 30)
        p.setBrush(c(s["fondo.encabezado"]))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(cab, 10, 10)
        p.drawRect(QRectF(cab.x(), cab.y() + 15, cab.width(), 15))
        for j, k in enumerate(("estado.error", "texto.inactivo", "texto.inactivo")):
            p.setBrush(c(s[k]))
            p.drawEllipse(QRectF(r.x() + 12 + j * 16, r.y() + 10, 10, 10))
        p.setPen(c(s["texto.normal"]))
        f.setBold(True)
        p.setFont(f)
        p.drawText(cab, Qt.AlignCenter, f"Lliphi {v.capitalize()}")
        f.setBold(False)
        p.setFont(f)
        p.setPen(QPen(c(s["borde.separador"]), 1))
        p.drawLine(cab.bottomLeft(), cab.bottomRight())
        # vista con filas y selección
        vista = QRectF(r.x() + 12, r.y() + 42, r.width() * 0.46, 150)
        p.setBrush(c(s["fondo.vista"]))
        p.drawRoundedRect(vista, 6, 6)
        filas = (("Documentos", "fondo.vista", "texto.normal"), ("Imágenes", "fondo.vista-alterno", "texto.normal"),
                 ("Seleccionado", "seleccion.fondo", "seleccion.texto"), ("Música", "fondo.vista-alterno", "texto.normal"),
                 ("Inactivo", "fondo.vista", "texto.inactivo"))
        for j, (texto, fondo, tinta) in enumerate(filas):
            fr = QRectF(vista.x() + 4, vista.y() + 6 + j * 28, vista.width() - 8, 26)
            p.setPen(Qt.NoPen)
            p.setBrush(c(s[fondo]))
            p.drawRoundedRect(fr, 4, 4)
            p.setPen(c(s[tinta]))
            p.drawText(fr.adjusted(10, 0, 0, 0), Qt.AlignVCenter, texto)
        # controles
        x = vista.right() + 14
        w = r.right() - 12 - x
        y = r.y() + 42
        for texto, borde, grosor in (("Botón", "borde.sutil", 1), ("Al pasar", "hover", 1.5), ("Con foco", "foco", 2)):
            br = QRectF(x, y, w, 26)
            p.setBrush(c(s["fondo.boton"]))
            p.setPen(QPen(c(s[borde]), grosor))
            p.drawRoundedRect(br, 6, 6)
            p.setPen(c(s["texto.normal"]))
            p.drawText(br, Qt.AlignCenter, texto)
            y += 32
        br = QRectF(x, y, w, 26)
        p.setPen(Qt.NoPen)
        p.setBrush(c(s["acento.base"]))
        p.drawRoundedRect(br, 6, 6)
        p.setPen(c(s["texto.sobre-acento"]))
        p.drawText(br, Qt.AlignCenter, "Aceptar")
        y += 34
        p.setPen(c(s["enlace"]))
        fu = QFont(f)
        fu.setUnderline(True)
        p.setFont(fu)
        p.drawText(QRectF(x, y, w, 18), Qt.AlignLeft | Qt.AlignVCenter, "Un enlace")
        p.setFont(f)
        p.setPen(c(s["texto.secundario"]))
        p.drawText(QRectF(x, y + 18, w, 18), Qt.AlignLeft | Qt.AlignVCenter, "Texto secundario")
        # estados
        y = vista.bottom() + 12
        xx = r.x() + 12
        for k, texto in (("estado.error", "Error"), ("estado.advertencia", "Aviso"), ("estado.exito", "Hecho"), ("estado.info", "Info")):
            p.setBrush(c(s[k]))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(xx, y + 5, 9, 9))
            p.setPen(c(s[k]))
            p.drawText(QRectF(xx + 13, y, 70, 20), Qt.AlignVCenter, texto)
            xx += 74
        tip = QRectF(xx + 6, y - 2, min(150, r.right() - xx - 18), 24)
        if tip.width() > 60:
            p.setBrush(c(s["fondo.tooltip"]))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(tip, 5, 5)
            p.setPen(c(s["texto.tooltip"]))
            p.drawText(tip, Qt.AlignCenter, "Tooltip")
        # terminal
        tr = QRectF(r.x() + 12, y + 32, r.width() - 24, r.bottom() - y - 44)
        if tr.height() < 60:
            return
        p.setBrush(c(term["fondo"]))
        p.setPen(QPen(c(s["borde.separador"]), 1))
        p.drawRoundedRect(tr, 6, 6)
        fm = QFont("JetBrains Mono")
        fm.setStyleHint(QFont.Monospace)
        fm.setPointSizeF(8.5)
        p.setFont(fm)
        p.setPen(c(term["texto"]))
        p.drawText(QRectF(tr.x() + 8, tr.y() + 6, tr.width(), 16), Qt.AlignVCenter, "$ lliphi --paleta")
        celda = (tr.width() - 16) / 8
        for n in range(16):
            cr = QRectF(tr.x() + 8 + (n % 8) * celda, tr.y() + 26 + (n // 8) * 22, celda - 4, 18)
            p.setPen(Qt.NoPen)
            p.setBrush(c(term[f"color{n}"]))
            p.drawRoundedRect(cr, 3, 3)
        nombres = ("negro", "rojo", "verde", "amarillo", "azul", "magenta", "cian", "blanco")
        yy = tr.y() + 74
        for n in range(1, 7):
            if yy + 14 > tr.bottom():
                break
            p.setPen(c(term[f"color{n}"]))
            p.drawText(QRectF(tr.x() + 8, yy, tr.width() / 2, 14), Qt.AlignVCenter, f"{nombres[n]}  normal")
            p.setPen(c(term[f"color{n + 8}"]))
            p.drawText(QRectF(tr.x() + tr.width() / 2, yy, tr.width() / 2, 14), Qt.AlignVCenter, f"{nombres[n]}  intenso")
            yy += 15


class Deslizador(QWidget):
    """Un valor con su deslizador y su caja numérica, sincronizados."""

    def __init__(self, minimo: float, maximo: float, paso: float, decimales: int, al_cambiar):
        super().__init__()
        self.escala = 10 ** decimales
        fila = QHBoxLayout(self)
        fila.setContentsMargins(0, 0, 0, 0)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(round(minimo * self.escala), round(maximo * self.escala))
        self.caja = QDoubleSpinBox()
        self.caja.setRange(minimo, maximo)
        self.caja.setSingleStep(paso)
        self.caja.setDecimals(decimales)
        self.caja.setFixedWidth(84)
        fila.addWidget(self.slider, 1)
        fila.addWidget(self.caja)
        self._al_cambiar = al_cambiar
        self.slider.valueChanged.connect(lambda n: self._fijar(n / self.escala, desde_slider=True))
        self.caja.valueChanged.connect(lambda x: self._fijar(x, desde_slider=False))
        self._quieto = False

    def valor(self) -> float:
        return self.caja.value()

    def poner(self, x: float) -> None:
        self._quieto = True
        self.caja.setValue(x)
        self.slider.setValue(round(x * self.escala))
        self._quieto = False

    def _fijar(self, x: float, desde_slider: bool) -> None:
        if self._quieto:
            return
        self._quieto = True
        if desde_slider:
            self.caja.setValue(x)
        else:
            self.slider.setValue(round(x * self.escala))
        self._quieto = False
        self._al_cambiar()


class Pagina:
    def __init__(self, v):
        self.v = v
        self.datos = proyecto.leer_borrador("esquema")
        self.informe: dict | None = None
        self.ruta: tuple | None = None

        # biblioteca
        self.arbol = QTreeWidget()
        self.arbol.setHeaderHidden(True)
        self.arbol.currentItemChanged.connect(self._elegir)
        # lienzo
        self.lienzo = Maqueta(v.tokens)
        # propiedades
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.titulo = QLabel("Elige un color")
        self.titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        pv.addWidget(self.titulo)
        self.rol = clase(QLabel(""), "tenue")
        self.rol.setWordWrap(True)
        pv.addWidget(self.rol)
        self.chip = QLabel()
        self.chip.setFixedHeight(46)
        pv.addWidget(self.chip)
        form = QFormLayout()
        self.d_l = Deslizador(0, 1, 0.005, 3, self._cambio)
        self.d_c = Deslizador(0, 0.37, 0.002, 3, self._cambio)
        self.d_h = Deslizador(0, 360, 1, 2, self._cambio)
        self.d_x = Deslizador(0, 1, 0.01, 3, self._cambio)
        form.addRow("L (luz)", self.d_l)
        form.addRow("C (croma)", self.d_c)
        form.addRow("H (matiz)", self.d_h)
        form.addRow("valor", self.d_x)
        self.form = form
        pv.addLayout(form)
        self.hex = clase(QLabel(""), "suave")
        self.hex.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pv.addWidget(self.hex)
        pv.addSpacing(8)
        pv.addWidget(clase(QLabel("Acento de cada variante"), "suave"))
        self.acento = {}
        fa = QFormLayout()
        for var in VARIANTES:
            cb = QComboBox()
            cb.addItems(list(self.datos["acentos"]))
            cb.currentTextChanged.connect(lambda nombre, var=var: self._acento(var, nombre))
            self.acento[var] = cb
            fa.addRow(var, cb)
        pv.addLayout(fa)
        self.resumen = nota("")
        pv.addWidget(self.resumen)
        pv.addStretch(1)

        self.editor = Editor("Color", "La paleta OKLCH de Lliphi: neutros, acentos, estados y terminal; contraste WCAG medido "
                             "por paleta.py en las dos variantes.", self.arbol, self.lienzo, props, v.tokens)
        self.daltonismo = QComboBox()
        self.daltonismo.addItem("visión típica", None)
        for k in color.DALTONISMO:
            self.daltonismo.addItem(k, k)
        self.daltonismo.currentIndexChanged.connect(self._daltonismo)
        self.editor.acciones.addWidget(self.daltonismo)
        self.editor.boton("Descartar", "volver", self._descartar)
        self.editor.boton("Informe", "terminal", self._informe_consola)
        self.editor.boton("Guardar y construir…", "verificar", self._guardar, "primario")
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels(["variante", "texto", "fondo", "razón", "mínimo", "criterio"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().hide()
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.editor.pestana(self.tabla, "Contraste", "verificar")
        self.usos = QListWidget()
        self.editor.pestana(self.usos, "Dónde se usa", "buscar")
        self.widget = self.editor
        self._tiempo = QTimer()
        self._tiempo.setSingleShot(True)
        self._tiempo.setInterval(350)
        self._tiempo.timeout.connect(self._calcular)
        self._calculando = False
        self._pendiente = False
        self._llenar_arbol()
        self._acentos_a_combos()
        self._mostrar_codigo()
        self.seleccionar(("acentos", self.datos["acento"]["oscuro"], "oscuro", "base"))
        self._calcular()

    def seleccionar(self, ruta: tuple) -> bool:
        """Elige en la biblioteca el valor de esa ruta (p. ej. el acento base del oscuro)."""
        pila = [self.arbol.topLevelItem(i) for i in range(self.arbol.topLevelItemCount())]
        while pila:
            x = pila.pop()
            pila += [x.child(i) for i in range(x.childCount())]
            dato = x.data(0, Qt.UserRole)
            if dato and tuple(dato[0]) == tuple(ruta):
                self.arbol.setCurrentItem(x)
                return True
        return False

    # ---------------------------------------------------------------- biblioteca
    def _llenar_arbol(self) -> None:
        self.arbol.clear()
        d = self.datos
        h = d["matiz_neutro"]
        def hoja(padre, texto, ruta, tipo, hex_=None):
            it = QTreeWidgetItem(padre, [texto])
            it.setData(0, Qt.UserRole, (ruta, tipo))
            if hex_:
                it.setIcon(0, muestra(hex_))
            return it
        raiz = QTreeWidgetItem(self.arbol, ["Neutros"])
        hoja(raiz, f"matiz de los neutros ({h:g}°)", ("matiz_neutro",), "matiz")
        for var in VARIANTES:
            g = QTreeWidgetItem(raiz, [var])
            for k, (l, c) in d["neutros"][var].items():
                hoja(g, f"{k} · {d['roles'][var].get(k, '')}", ("neutros", var, k), "lc", color.oklch_a_hex(l, c, h))
        raiz = QTreeWidgetItem(self.arbol, ["Acentos"])
        for nombre, acento in d["acentos"].items():
            g = QTreeWidgetItem(raiz, [nombre + ("  ✓" if nombre in d["acento"].values() else "")])
            for var in VARIANTES:
                for k, lch in acento[var].items():
                    hoja(g, f"{var} · {k}", ("acentos", nombre, var, k), "lch", color.oklch_a_hex(*lch))
        raiz = QTreeWidgetItem(self.arbol, ["Estados"])
        for var in VARIANTES:
            g = QTreeWidgetItem(raiz, [var])
            for k, lch in d["estados"][var].items():
                hoja(g, k, ("estados", var, k), "lch", color.oklch_a_hex(*lch))
        raiz = QTreeWidgetItem(self.arbol, ["Terminal"])
        g = QTreeWidgetItem(raiz, ["matices ANSI"])
        for k, hue in d["terminal"]["matices"].items():
            hoja(g, f"{k} ({hue:g}°)", ("terminal", "matices", k), "matiz", color.oklch_a_hex(0.65, 0.13, hue))
        for var in VARIANTES:
            g = QTreeWidgetItem(raiz, [var])
            for k, x in d["terminal"][var].items():
                if isinstance(x, list):
                    hoja(g, k, ("terminal", var, k), "lc", color.oklch_a_hex(x[0], x[1], h))
                else:
                    hoja(g, f"{k} = {x:g}", ("terminal", var, k), "croma" if k == "croma" else "luz")
        self.arbol.expandToDepth(1)

    def _refrescar_iconos(self) -> None:
        """Repinta las muestras de la biblioteca sin reconstruirla (no se pierde la selección)."""
        h = self.datos["matiz_neutro"]
        it = self.arbol.invisibleRootItem()
        pila = [it.child(i) for i in range(it.childCount())]
        while pila:
            x = pila.pop()
            pila += [x.child(i) for i in range(x.childCount())]
            dato = x.data(0, Qt.UserRole)
            if not dato:
                continue
            ruta, tipo = dato
            val = obtener(self.datos, ruta)
            if tipo == "lch":
                x.setIcon(0, muestra(color.oklch_a_hex(*val)))
            elif tipo == "lc":
                x.setIcon(0, muestra(color.oklch_a_hex(val[0], val[1], h)))
            elif ruta[:2] == ("terminal", "matices"):
                x.setIcon(0, muestra(color.oklch_a_hex(0.65, 0.13, val)))
                x.setText(0, f"{ruta[-1]} ({val:g}°)")
            elif ruta == ("matiz_neutro",):
                x.setText(0, f"matiz de los neutros ({val:g}°)")
            elif tipo in ("croma", "luz"):
                x.setText(0, f"{ruta[-1]} = {val:g}")

    def _elegir(self, it, _prev=None) -> None:
        dato = it.data(0, Qt.UserRole) if it else None
        if not dato:
            return
        self.ruta, self.tipo = dato
        val = obtener(self.datos, self.ruta)
        self.titulo.setText(" · ".join(str(x) for x in self.ruta[1:]) or self.ruta[0])
        rol = ""
        if self.ruta[0] == "neutros":
            rol = self.datos["roles"][self.ruta[1]].get(self.ruta[2], "")
        elif self.ruta[0] == "acentos":
            activo = self.datos["acento"][self.ruta[2]] == self.ruta[1]
            rol = f"acento {self.ruta[1]} de la variante {self.ruta[2]}" + (" (en uso)" if activo else " (no elegido: no afecta a la paleta)")
        elif self.ruta == ("matiz_neutro",):
            rol = "el matiz de todos los neutros y de los negros y blancos de la terminal"
        elif self.ruta[0] == "terminal":
            rol = "terminal: " + {"matices": "matiz del color ANSI (normal e intenso)", "normal": "luz de los colores normales",
                                  "intensa": "luz de los colores intensos (8–15)", "croma": "croma de los colores ANSI"}.get(
                self.ruta[1] if self.ruta[1] == "matices" else self.ruta[2], "negro y blanco de la terminal")
        self.rol.setText(rol)
        lch = self.tipo in ("lch", "lc")
        for w, visible in ((self.d_l, lch), (self.d_c, lch), (self.d_h, self.tipo == "lch"), (self.d_x, not lch)):
            w.setVisible(visible)
            self.form.labelForField(w).setVisible(visible)
        if lch:
            self.d_l.poner(val[0])
            self.d_c.poner(val[1])
            if self.tipo == "lch":
                self.d_h.poner(val[2])
        else:
            rango = {"matiz": (0, 360, 1, 2), "croma": (0, 0.37, 0.005, 3), "luz": (0, 1, 0.01, 3)}[self.tipo]
            self.d_x.caja.setRange(rango[0], rango[1])
            self.d_x.slider.setRange(round(rango[0] * self.d_x.escala), round(rango[1] * self.d_x.escala))
            self.d_x.poner(float(val))
        self._pintar_chip()
        self._mostrar_usos()

    # ---------------------------------------------------------------- edición
    def _cambio(self) -> None:
        if not self.ruta:
            return
        if self.tipo == "lch":
            poner(self.datos, self.ruta, [round(self.d_l.valor(), 3), round(self.d_c.valor(), 3), round(self.d_h.valor(), 2)])
        elif self.tipo == "lc":
            poner(self.datos, self.ruta, [round(self.d_l.valor(), 3), round(self.d_c.valor(), 3)])
        else:
            x = self.d_x.valor()
            poner(self.datos, self.ruta, int(x) if self.tipo == "matiz" and x == int(x) else round(x, 3))
        self._tras_cambiar()

    def _acento(self, var: str, nombre: str) -> None:
        if nombre and self.datos["acento"][var] != nombre:
            self.datos["acento"][var] = nombre
            self._tras_cambiar()

    def _tras_cambiar(self) -> None:
        proyecto.guardar_borrador("esquema", self.datos)
        self._refrescar_iconos()
        self._pintar_chip()
        self._mostrar_codigo()
        self._tiempo.start()

    def _pintar_chip(self) -> None:
        if not self.ruta:
            return
        val = obtener(self.datos, self.ruta)
        if self.tipo == "lch":
            l, c, h = val
        elif self.tipo == "lc":
            (l, c), h = val, self.datos["matiz_neutro"]
        elif self.tipo == "matiz":
            l, c, h = 0.65, 0.13, val
        else:
            self.chip.setStyleSheet("")
            self.hex.setText("")
            return
        hx = color.oklch_a_hex(l, c, h)
        gama = color.en_gama(l, c, h)
        self.chip.setStyleSheet(f"background: {color.simular(hx, self.daltonismo.currentData())}; border-radius: 8px;")
        self.hex.setText(f"{hx} · oklch({l:.3f} {c:.3f} {h:g})" + ("" if gama else " · fuera de sRGB: se reduce el croma"))

    def _daltonismo(self) -> None:
        self.lienzo.daltonismo = self.daltonismo.currentData()
        self.lienzo.update()
        self._pintar_chip()

    def _acentos_a_combos(self) -> None:
        for var, cb in self.acento.items():
            cb.blockSignals(True)
            cb.setCurrentText(self.datos["acento"][var])
            cb.blockSignals(False)

    # ---------------------------------------------------------------- informe
    def _calcular(self) -> None:
        if self._calculando:
            self._pendiente = True
            return
        self._calculando = True
        ruta = proyecto.guardar_borrador("esquema", self.datos)
        self.v.en_segundo_plano(lambda r: proyecto.correr_json("paleta", "--ajustes", str(r)), self._con_informe, ruta)

    def _con_informe(self, informe) -> None:
        self._calculando = False
        if self._pendiente:
            self._pendiente = False
            self._calcular()
        if not informe:
            self.resumen.setText("No se pudo calcular la paleta (¿falta <code>.venv</code> con coloraide?).")
            return
        self.informe = informe
        self.lienzo.informe = informe
        self.lienzo.update()
        t = self.v.tokens()
        filas = [(v, p) for v in VARIANTES for p in informe["variantes"][v]["pares"]]
        malos = [x for x in filas if not x[1]["cumple"] and not x[1]["informativo"]]
        self.tabla.setRowCount(len(filas))
        for i, (v, p) in enumerate(sorted(filas, key=lambda x: (x[1]["cumple"] or x[1]["informativo"], x[0]))):
            for j, val in enumerate((v, p["texto"], p["fondo"], f"{p['razon']:.2f}", f"{p['minimo']}", p["criterio"])):
                celda = QTableWidgetItem(val)
                if j == 3:
                    ok = p["cumple"] or p["informativo"]
                    celda.setForeground(QBrush(QColor(t["exito"] if p["cumple"] else (t["aviso"] if ok else t["error"]))))
                self.tabla.setItem(i, j, celda)
        self.resumen.setText(f"<b>{'Todos los pares cumplen' if not malos else f'{len(malos)} par(es) no cumplen'}</b> "
                             f"({sum(1 for _ in filas)} medidos en las dos variantes)."
                             + ("" if not malos else "<br>" + "<br>".join(f"{v}: {p['texto']} / {p['fondo']} = {p['razon']}"
                                                                          f" (mín. {p['minimo']})" for v, p in malos[:5])))
        self.editor.pestanas.setTabText(2, "Contraste" + (f" ({len(malos)} ✗)" if malos else " ✓"))

    def _informe_consola(self) -> None:
        ruta = proyecto.guardar_borrador("esquema", self.datos)
        self.v.correr(proyecto.orden("paleta", "--ajustes", str(ruta)), "Paleta del borrador (informe)")

    def _mostrar_codigo(self) -> None:
        self.editor.codigo.setPlainText(proyecto.volcar("esquema", self.datos))
        diff = proyecto.diff_ajustes("esquema", self.datos)
        self.editor.diff.setPlainText(diff or "El borrador es igual a modulos/esquema/ajustes.json.")
        self.editor.pestanas.setTabText(1, "Cambios" + (f" ({sum(l.startswith('+') and not l.startswith('+++') for l in diff.splitlines())})" if diff else ""))

    def _mostrar_usos(self) -> None:
        self.usos.clear()
        if not self.ruta:
            return
        tok = proyecto.tokens()["primitivas"]
        hex_ = None
        if self.ruta[0] in ("neutros", "estados"):
            hex_ = tok[self.ruta[1]].get(self.ruta[2], {}).get("$value", {}).get("hex")
        elif self.ruta[0] == "acentos" and proyecto.tokens()["acento"][self.ruta[2]] == self.ruta[1]:
            hex_ = tok[self.ruta[2]][NOMBRE_ACENTO[self.ruta[3]]]["$value"]["hex"]
        if not hex_:
            self.usos.addItem("Este valor no es un color de la paleta del proyecto (o su acento no está elegido).")
            return
        usos = color.usos(proyecto.raiz() / "generado", hex_)
        self.usos.addItem(QListWidgetItem(muestra(hex_), f"{hex_} (lo que hay hoy en tokens/tokens.json): "
                                          f"{sum(len(x) for x in usos.values())} archivo(s) en {len(usos)} módulo(s)"))
        for mod, archivos in usos.items():
            for a in archivos:
                self.usos.addItem(QListWidgetItem(icono_trazo("documento"), f"generado/{a}"))

    # ---------------------------------------------------------------- guardar
    def _descartar(self) -> None:
        if proyecto.diff_ajustes("esquema", self.datos) and not self.v.confirmar("Descartar", "¿Volver a la paleta del proyecto? Se pierde el borrador."):
            return
        proyecto.descartar_borrador("esquema")
        self.datos = proyecto.leer_ajustes("esquema")
        self._llenar_arbol()
        self._acentos_a_combos()
        self._mostrar_codigo()
        self.seleccionar(("acentos", self.datos["acento"]["oscuro"], "oscuro", "base"))
        self._calcular()

    def seleccionar(self, ruta: tuple) -> bool:
        """Elige en la biblioteca el valor de esa ruta (p. ej. el acento base del oscuro)."""
        pila = [self.arbol.topLevelItem(i) for i in range(self.arbol.topLevelItemCount())]
        while pila:
            x = pila.pop()
            pila += [x.child(i) for i in range(x.childCount())]
            dato = x.data(0, Qt.UserRole)
            if dato and tuple(dato[0]) == tuple(ruta):
                self.arbol.setCurrentItem(x)
                return True
        return False

    def _guardar(self) -> None:
        diff = proyecto.diff_ajustes("esquema", self.datos)
        if not diff:
            self.v.marco.avisar("Sin cambios", "El borrador es igual a la paleta del proyecto.", "info")
            return
        if not self.informe:
            self.v.marco.avisar("Espera al informe", "La paleta del borrador aún se está midiendo.", "aviso")
            return
        if not self.informe["ok"]:
            self.v.marco.avisar("No se guarda", "Hay pares de contraste que no cumplen (pestaña Contraste): la paleta de "
                                "Lliphi exige 4,5:1 en texto y 3:1 en controles y foco.", "error")
            return
        caja = QMessageBox(QMessageBox.Question, "Guardar la paleta",
                           "Escribe modulos/esquema/ajustes.json y reconstruye: paleta.py --aplicar (tokens.json), "
                           "generar.py --aplicar (todo lo generado, porque todo sale de los tokens) y generar.py validar.\n\n"
                           "Nada se instala en tu escritorio. ¿Seguir?", QMessageBox.Yes | QMessageBox.No, self.v.ui)
        caja.setDetailedText(diff)
        if caja.exec() != QMessageBox.Yes:
            return
        proyecto.guardar_ajustes("esquema", self.datos)
        proyecto.descartar_borrador("esquema")
        self._mostrar_codigo()
        self.v.cadena([(proyecto.orden("paleta", "--aplicar"), "Paleta (tokens.json)"),
                       (proyecto.orden("generar", "--aplicar"), "Construir"),
                       (proyecto.orden("generar", "validar"), "Validar")],
                      lambda c: c == 0 and self.v.marco.avisar("Paleta guardada y construida",
                                                               "Pruébala en la Vista en vivo («Recargar») o instálala desde "
                                                               "Construir y desplegar.", "ok"))

    def al_cambiar_proyecto(self) -> None:
        self._mostrar_codigo()

    def repintar(self) -> None:
        self.lienzo.update()
