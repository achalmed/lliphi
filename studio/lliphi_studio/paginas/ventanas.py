"""Window Studio: editor y previsualizador de la decoración Aurorae (módulo `decoracion`).

Lienzo: dos ventanas con la decoración real (marco de nueve piezas de `decoration.svg`, con su sombra; botones con sus
estados al pasar y al pulsar con el ratón; título con la fuente y los colores del `rc`), la activa delante y la inactiva
detrás, en la variante elegida. Propiedades: las claves del `rc` (alturas, márgenes, alineación, sombra), los colores
del título (tokens), y los botones de cada lado. Abajo: el borrador, el diff, el `rc` que saldría y la tira de estados
de cada botón.

Se edita un borrador de `modulos/decoracion/ajustes.json`; el `rc` que se dibuja es el de la base de Nothing con los
ajustes encima (lo mismo que hace `construir.py`). «Guardar y construir» escribe los ajustes y reconstruye la decoración
y el tema global (que lleva la posición de los botones).
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                               QMessageBox, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo

from lliphi_studio import pintor, proyecto, svgplasma
from lliphi_studio.comun import Editor, Lienzo, nota
from lliphi_studio.paginas.color import muestra
from lliphi_studio.paginas.plasma import ESQUEMA

VARIANTE_TEMA = {"oscuro": "", "claro": "-claro"}
NUMERICAS = ("TitleHeight", "TitleEdgeTop", "TitleEdgeBottom", "TitleEdgeLeft", "TitleEdgeRight", "TitleBorderLeft",
             "TitleBorderRight", "ButtonWidth", "ButtonHeight", "ButtonSpacing", "ButtonMarginTop", "BorderLeft",
             "BorderRight", "BorderBottom", "PaddingTop", "PaddingBottom", "PaddingLeft", "PaddingRight")
ELECCIONES = {"TitleAlignment": ("Left", "Center", "Right"), "TitleVerticalAlignment": ("Top", "Center", "Bottom")}
BOOLEANAS = ("UseTextShadow", "Shadow")


def carpeta_tema(var: str) -> Path:
    return proyecto.raiz() / "generado" / "decoracion" / f"{proyecto.marca()['id']}{VARIANTE_TEMA[var]}"


def rc_base() -> dict[str, str]:
    return {k: v for k, (_g, v) in svgplasma.rc_plano(svgplasma.leer_rc(
        proyecto.raiz() / "fuentes" / "base" / "Nothing-aurorae" / "Nothingrc")).items()}


def semanticos(var: str) -> dict[str, str]:
    salida = {}
    def plano(d, pre=""):
        for k, x in d.items():
            if isinstance(x, dict) and "$value" in x:
                salida[pre + k] = x["$value"]["hex"]
            elif isinstance(x, dict):
                plano(x, pre + k + ".")
    plano(proyecto.tokens()["semanticos"][var])
    return salida


def rc_efectivo(ajustes: dict, var: str) -> dict[str, str]:
    """El rc que saldría con estos ajustes: el de la base con los colores del título y las claves de los ajustes."""
    rc = rc_base()
    s = semanticos(var)
    for clave, token in ajustes["titulo"].items():
        h = s.get(token, "#808080").lstrip("#")
        rc[clave] = ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    rc.update(ajustes["rc"])
    return rc


class LienzoVentanas(Lienzo):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.var = "oscuro"
        self.ajustes: dict = {}
        self.deco = None
        self.botones: dict[str, object] = {}
        self.fondo_ventana = "#2b2b2b"
        self.vista = "#1e1e1e"
        self.texto = "#ffffff"
        self.zoom = 1.6
        self.raton: QPointF | None = None
        self.pulsado = False
        self._zonas: list[tuple[QRectF, str]] = []
        self.setMouseTracking(True)

    def cargar(self, var: str, ajustes: dict) -> None:
        self.var, self.ajustes = var, ajustes
        tema = carpeta_tema(var)
        self.deco = pintor.renderizador(svgplasma.leer(tema / "decoration.svg"))
        self.botones = {letra: pintor.renderizador(svgplasma.leer(tema / f"{archivo}.svg"))
                        for letra, (archivo, _) in svgplasma.BOTONES.items() if archivo and (tema / f"{archivo}.svg").exists()}
        esquema = svgplasma.esquema(proyecto.raiz() / "generado" / "esquema" / f"{ESQUEMA[var]}.colors")
        self.fondo_ventana, self.vista, self.texto = esquema["Background"], esquema["ViewBackground"], esquema["Text"]
        self.update()

    def mouseMoveEvent(self, e) -> None:
        self.raton = e.position()
        self.update()

    def mousePressEvent(self, e) -> None:
        self.pulsado = True
        self.update()

    def mouseReleaseEvent(self, e) -> None:
        self.pulsado = False
        self.update()

    def leaveEvent(self, _e) -> None:
        self.raton = None
        self.update()

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        if not self.deco or not self.ajustes:
            return
        rc = rc_efectivo(self.ajustes, self.var)
        n = lambda k: int(float(rc.get(k, "0")))   # noqa: E731
        z = self.zoom
        p.scale(z, z)
        self._zonas = []
        ancho, alto = rect.width() / z, rect.height() / z
        w, h = min(560, ancho * 0.62), min(330, alto * 0.62)
        inactiva = QRectF(ancho * 0.08, alto * 0.10, w * 0.92, h * 0.88)
        activa = QRectF(ancho - w - ancho * 0.08, alto - h - alto * 0.08, w, h)
        self._ventana(p, inactiva, rc, n, False, "Konsole")
        self._ventana(p, activa, rc, n, True, f"Inicio — Dolphin · {proyecto.marca()['nombre']} {self.var.capitalize()}")

    def _ventana(self, p: QPainter, v: QRectF, rc: dict, n, activa: bool, titulo: str) -> None:
        z = self.zoom
        prefijo = "decoration" if activa else "decoration-inactive"
        exterior = v.adjusted(-n("PaddingLeft"), -n("PaddingTop"), n("PaddingRight"), n("PaddingBottom"))
        if rc.get("Shadow", "true") != "true":
            exterior = v
        pintor.marco(p, self.deco, prefijo if self.deco.elementExists(f"{prefijo}-center") else "decoration", exterior)
        barra = n("TitleEdgeTop") + n("TitleHeight") + n("TitleEdgeBottom")
        cliente = QRectF(v.left() + n("BorderLeft"), v.top() + barra, v.width() - n("BorderLeft") - n("BorderRight"),
                         v.height() - barra - n("BorderBottom"))
        p.fillRect(cliente, QColor(self.fondo_ventana))
        lateral = QRectF(cliente.left(), cliente.top(), cliente.width() * 0.26, cliente.height())
        p.fillRect(QRectF(cliente.left() + lateral.width(), cliente.top(), cliente.width() - lateral.width(), cliente.height()),
                   QColor(self.vista))
        f = QFont("Inter")
        f.setPixelSize(7)
        p.setFont(f)
        p.setPen(QColor(self.texto))
        for i, t in enumerate(("Inicio", "Documentos", "Descargas", "Imágenes", "Música")):
            p.drawText(QRectF(lateral.left() + 6, lateral.top() + 8 + i * 13, lateral.width() - 8, 12), Qt.AlignVCenter, t)
        # botones
        izquierda = self.ajustes["botones"]["izquierda"]
        derecha = self.ajustes["botones"]["derecha"]
        bw, bh, esp = n("ButtonWidth"), n("ButtonHeight"), n("ButtonSpacing")
        y = v.top() + n("TitleEdgeTop") + n("ButtonMarginTop")
        x = v.left() + n("TitleEdgeLeft")
        fin_izq = x
        for letra in izquierda:
            self._boton(p, letra, QRectF(x, y, bw, bh), activa)
            x += bw + esp
            fin_izq = x
        x = v.right() - n("TitleEdgeRight") - bw
        inicio_der = v.right() - n("TitleEdgeRight")
        for letra in reversed(derecha):
            self._boton(p, letra, QRectF(x, y, bw, bh), activa)
            inicio_der = x
            x -= bw + esp
        # título
        zona = QRectF(fin_izq + n("TitleBorderLeft"), v.top() + n("TitleEdgeTop"),
                      inicio_der - fin_izq - n("TitleBorderLeft") - n("TitleBorderRight"), n("TitleHeight"))
        ft = QFont("Inter")
        ft.setPixelSize(max(8, int(n("TitleHeight") * 0.62)))
        ft.setWeight(QFont.Medium)
        p.setFont(ft)
        alin = {"Left": Qt.AlignLeft, "Center": Qt.AlignHCenter, "Right": Qt.AlignRight}.get(rc.get("TitleAlignment"), Qt.AlignHCenter)
        valin = {"Top": Qt.AlignTop, "Center": Qt.AlignVCenter, "Bottom": Qt.AlignBottom}.get(rc.get("TitleVerticalAlignment"), Qt.AlignVCenter)
        if rc.get("UseTextShadow") == "true":
            sombra = rc.get("ActiveTextShadowColor" if activa else "InactiveTextShadowColor", "0,0,0").split(",")
            p.setPen(QColor(*[int(x) for x in sombra[:3]], int(sombra[3]) if len(sombra) > 3 else 255))
            p.drawText(zona.translated(n("TextShadowOffsetX"), n("TextShadowOffsetY")), alin | valin, titulo)
        p.setPen(QColor(svgplasma.rgb_a_hex(rc.get("ActiveTextColor" if activa else "InactiveTextColor", "128,128,128"))))
        p.drawText(zona, alin | valin, p.fontMetrics().elidedText(titulo, Qt.ElideRight, int(zona.width())))

    def _boton(self, p: QPainter, letra: str, r: QRectF, activa: bool) -> None:
        z = self.zoom
        estado = "active" if activa else "inactive"
        if activa and self.raton is not None and QRectF(r.x() * z, r.y() * z, r.width() * z, r.height() * z).contains(self.raton):
            estado = "pressed" if self.pulsado else "hover"
        rend = self.botones.get(letra)
        if rend is None:
            p.setPen(QPen(QColor(self.texto), 1))
            p.drawEllipse(r.adjusted(1, 1, -1, -1))
            return
        id_ = f"{estado}-center" if rend.elementExists(f"{estado}-center") else "active-center"
        pintor.elemento(p, rend, id_, r)
        self._zonas.append((r, letra))


class TiraBotones(QWidget):
    """Cada botón de la decoración con sus cinco estados (activo, al pasar, pulsado, inactivo, desactivado)."""

    def __init__(self, pagina):
        super().__init__()
        self.pagina = pagina
        self.setMinimumHeight(220)

    def paintEvent(self, _e) -> None:
        t = self.pagina.v.tokens()
        lz = self.pagina.lienzo
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(lz.fondo_ventana))
        f = QFont(self.font())
        f.setPointSizeF(8)
        p.setFont(f)
        for j, estado in enumerate(svgplasma.ESTADOS_BOTON):
            p.setPen(QColor(lz.texto))
            p.drawText(QRectF(130 + j * 70, 4, 70, 16), Qt.AlignCenter, estado)
        for i, (letra, rend) in enumerate(lz.botones.items()):
            y = 24 + i * 28
            p.setPen(QColor(lz.texto))
            p.drawText(QRectF(8, y, 120, 24), Qt.AlignVCenter, f"{letra} · {svgplasma.BOTONES[letra][1]}")
            for j, estado in enumerate(svgplasma.ESTADOS_BOTON):
                if rend.elementExists(f"{estado}-center"):
                    pintor.elemento(p, rend, f"{estado}-center", QRectF(155 + j * 70, y + 2, 20, 20))
        p.end()


class Pagina:
    def __init__(self, v):
        self.v = v
        self.datos = proyecto.leer_borrador("decoracion")
        bib = QWidget()
        bv = QVBoxLayout(bib)
        bv.setContentsMargins(0, 0, 0, 0)
        self.variante = QComboBox()
        self.variante.addItem("Lliphi Oscuro (lliphi)", "oscuro")
        self.variante.addItem("Lliphi Claro (lliphi-claro)", "claro")
        self.variante.currentIndexChanged.connect(self._cargar)
        bv.addWidget(self.variante)
        bv.addWidget(clase(QLabel("Archivos del tema"), "suave"))
        self.archivos = QListWidget()
        self.archivos.currentItemChanged.connect(self._archivo)
        bv.addWidget(self.archivos, 1)
        b = QPushButton(icono_trazo("abrir"), " Copia en Inkscape")
        b.clicked.connect(self._inkscape)
        bv.addWidget(b)
        self.lienzo = LienzoVentanas(v.tokens)
        # propiedades
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        pv.addWidget(nota("Pasa el ratón por los botones de la ventana activa (y pulsa) para ver sus estados. Ctrl + rueda: zoom."))
        form = QFormLayout()
        self.campos: dict[str, QWidget] = {}
        base = rc_base()
        for clave in ("TitleAlignment", "TitleVerticalAlignment"):
            cb = QComboBox()
            cb.addItems(ELECCIONES[clave])
            cb.currentTextChanged.connect(lambda x, k=clave: self._rc(k, x))
            self.campos[clave] = cb
            form.addRow(clave, cb)
        for clave in BOOLEANAS:
            ch = QCheckBox()
            ch.toggled.connect(lambda x, k=clave: self._rc(k, "true" if x else "false"))
            self.campos[clave] = ch
            form.addRow(clave, ch)
        for clave in NUMERICAS:
            if clave not in base:
                continue
            sp = QSpinBox()
            sp.setRange(0, 200)
            sp.valueChanged.connect(lambda x, k=clave: self._rc(k, str(x)))
            self.campos[clave] = sp
            form.addRow(clave, sp)
        tokens = sorted(semanticos("oscuro"))
        for clave in ("ActiveTextColor", "InactiveTextColor"):
            cb = QComboBox()
            cb.addItems(tokens)
            cb.currentTextChanged.connect(lambda x, k=clave: self._titulo(k, x))
            self.campos[clave] = cb
            form.addRow(f"{clave} (token)", cb)
        self.izq, self.der = QLineEdit(), QLineEdit()
        for campo, lado in ((self.izq, "izquierda"), (self.der, "derecha")):
            campo.setMaxLength(12)
            campo.textEdited.connect(lambda x, l=lado: self._botones(l, x))
            form.addRow(f"botones a la {lado}", campo)
        pv.addLayout(form)
        pv.addWidget(nota("Letras: " + " · ".join(f"<b>{l}</b> {d}" for l, (_a, d) in svgplasma.BOTONES.items())))
        pv.addStretch(1)
        envoltura = QScrollArea()
        envoltura.setWidgetResizable(True)
        envoltura.setWidget(props)
        envoltura.setFrameShape(QScrollArea.NoFrame)
        envoltura.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.editor = Editor("Ventanas", "La decoración Aurorae de Lliphi (derivada de Nothing): la ventana activa y la "
                             "inactiva con su marco, sombra, botones y título reales; las claves del rc y los botones.",
                             bib, self.lienzo, envoltura, v.tokens)
        self.editor.boton("Descartar", "volver", self._descartar)
        self.editor.boton("Guardar y construir…", "verificar", self._guardar, "primario")
        self.rc_salida = self.editor.codigo.__class__(v.tokens)
        self.editor.pestana(self.rc_salida, "rc que saldría", "texto")
        self.tira = TiraBotones(self)
        self.editor.pestana(self.tira, "Botones", "ventana")
        self.widget = self.editor
        self._cargar()

    def _cargar(self) -> None:
        var = self.variante.currentData()
        self.lienzo.cargar(var, self.datos)
        self.archivos.clear()
        for f in sorted(carpeta_tema(var).iterdir()):
            it = QListWidgetItem(icono_trazo("imagen" if f.suffix == ".svg" else "texto"), f.name)
            it.setData(Qt.UserRole, str(f))
            self.archivos.addItem(it)
        self._a_campos()
        self._mostrar()

    def _a_campos(self) -> None:
        rc = rc_efectivo(self.datos, self.variante.currentData())
        for k, w in self.campos.items():
            w.blockSignals(True)
            if isinstance(w, QSpinBox):
                w.setValue(int(float(rc.get(k, 0))))
            elif isinstance(w, QCheckBox):
                w.setChecked(rc.get(k) == "true")
            elif k in self.datos["titulo"]:
                w.setCurrentText(self.datos["titulo"][k])
            else:
                w.setCurrentText(rc.get(k, ""))
            w.blockSignals(False)
        self.izq.setText(self.datos["botones"]["izquierda"])
        self.der.setText(self.datos["botones"]["derecha"])

    def _rc(self, clave: str, valor: str) -> None:
        if rc_base().get(clave) == valor:
            self.datos["rc"].pop(clave, None)   # igual que la base: no hace falta en los ajustes
        else:
            self.datos["rc"][clave] = valor
        self._tras_cambiar()

    def _titulo(self, clave: str, token: str) -> None:
        self.datos["titulo"][clave] = token
        self._tras_cambiar()

    def _botones(self, lado: str, texto: str) -> None:
        limpio = "".join(c for c in texto.upper() if c in svgplasma.BOTONES)
        self.datos["botones"][lado] = limpio
        self._tras_cambiar()

    def _tras_cambiar(self) -> None:
        proyecto.guardar_borrador("decoracion", self.datos)
        self.lienzo.ajustes = self.datos
        self.lienzo.update()
        self._mostrar()

    def _mostrar(self) -> None:
        self.editor.codigo.setPlainText(proyecto.volcar("decoracion", self.datos))
        diff = proyecto.diff_ajustes("decoracion", self.datos)
        self.editor.diff.setPlainText(diff or "El borrador es igual a modulos/decoracion/ajustes.json.")
        rc = rc_efectivo(self.datos, self.variante.currentData())
        self.rc_salida.setPlainText("\n".join(f"{k}={v}" for k, v in rc.items()))
        self.tira.update()

    def _archivo(self, it, _prev=None) -> None:
        if it:
            ruta = Path(it.data(Qt.UserRole))
            if ruta.suffix in (".svg", "") or ruta.name.endswith("rc") or ruta.suffix in (".json", ".desktop"):
                self.editor.codigo.setPlainText(ruta.read_text(encoding="utf-8", errors="replace")[:300_000])
                self.editor.pestanas.setCurrentIndex(0)

    def _inkscape(self) -> None:
        it = self.archivos.currentItem()
        ruta = Path(it.data(Qt.UserRole)) if it else carpeta_tema(self.variante.currentData()) / "decoration.svg"
        if ruta.suffix != ".svg":
            ruta = carpeta_tema(self.variante.currentData()) / "decoration.svg"
        copia = pintor.copia_para_inkscape(ruta, f"decoracion-{self.variante.currentData()}")
        self.v.marco.avisar("Inkscape abre una copia" if pintor.abrir_en_inkscape(copia) else "No está Inkscape", str(copia), "info")

    def _descartar(self) -> None:
        proyecto.descartar_borrador("decoracion")
        self.datos = proyecto.leer_ajustes("decoracion")
        self._cargar()

    def _guardar(self) -> None:
        diff = proyecto.diff_ajustes("decoracion", self.datos)
        if not diff:
            self.v.marco.avisar("Sin cambios", "El borrador es igual a los ajustes del proyecto.", "info")
            return
        if not self.datos["botones"]["izquierda"] + self.datos["botones"]["derecha"]:
            self.v.marco.avisar("Sin botones", "La ventana se quedaría sin cerrar ni minimizar.", "error")
            return
        caja = QMessageBox(QMessageBox.Question, "Guardar la decoración",
                           "Escribe modulos/decoracion/ajustes.json y reconstruye la decoración y el tema global "
                           "(generar.py --modulos decoracion,global --aplicar) y valida. Nada se instala en tu "
                           "escritorio. ¿Seguir?", QMessageBox.Yes | QMessageBox.No, self.v.ui)
        caja.setDetailedText(diff)
        if caja.exec() != QMessageBox.Yes:
            return
        proyecto.guardar_ajustes("decoracion", self.datos)
        proyecto.descartar_borrador("decoracion")
        self._mostrar()
        self.v.cadena([(proyecto.orden("generar", "--modulos", "decoracion,global", "--aplicar"), "Construir decoración"),
                       (proyecto.orden("generar", "validar"), "Validar")])

    def repintar(self) -> None:
        self.lienzo.update()
        self.tira.update()
