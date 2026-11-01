"""Layout Studio: la configuración visual de paneles y widgets (módulo `disposicion`).

Biblioteca: los plasmoides instalados (los paquetes de `plasma/plasmoids` y los compilados en `plugins/plasma/applets`).
Lienzo: la pantalla con el fondo de Lliphi y cada panel con sus widgets como fichas; se elige un panel o un widget con
un clic y se reordena arrastrando. Propiedades: ubicación, alto, ocultar, flotante, longitud y alineación del panel; el
widget con su configuración. Abajo: el borrador, el diff y el `escritorio.js` que saldría (lo escribe el propio
`construir.py` del módulo).

«Probar en la sesión de prueba» ejecuta el script del borrador en el `plasmashell` de la sesión de prueba
(`sesion.py guion`), sin guardar nada ni tocar tu escritorio, y trae la captura. «Guardar y construir» escribe
`modulos/disposicion/ajustes.json` y reconstruye el tema global.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo

from lliphi_studio import iconos, proyecto
from lliphi_studio.comun import envolver, Codigo, Editor, Lienzo, nota

UBICACIONES = ("top", "bottom", "left", "right")
OCULTAR = ("none", "autohide", "dodgewindows", "windowsgobelow")
LONGITUD = ("fill", "fit", "custom")
ALINEACION = ("left", "center", "right")
CONTENEDORES = ("org.kde.desktopcontainment", "org.kde.panel", "org.kde.plasma.folder", "org.kde.plasma.private.systemtray")
NOMBRES = {"org.kde.plasma.kickoff": ("Lanzador", "start-here-kde"), "org.kde.plasma.kicker": ("Menú", "start-here-kde"),
           "org.kde.plasma.kickerdash": ("Tablero", "start-here-kde"), "org.kde.plasma.panelspacer": ("Espaciador", ""),
           "org.kde.plasma.marginsseparator": ("Separador", ""), "org.kde.plasma.digitalclock": ("Reloj", "clock"),
           "org.kde.plasma.systemtray": ("Bandeja", "preferences-desktop-notification"),
           "org.kde.plasma.icontasks": ("Tareas (iconos)", "preferences-system-windows"),
           "org.kde.plasma.taskmanager": ("Tareas", "preferences-system-windows"), "org.kde.plasma.pager": ("Escritorios", "virtual-desktops"),
           "org.kde.plasma.showdesktop": ("Mostrar escritorio", "user-desktop"), "org.kde.plasma.minimizeall": ("Minimizar todo", "window-minimize"),
           "org.kde.plasma.trash": ("Papelera", "user-trash"), "org.kde.plasma.appmenu": ("Menú global", "application-menu"),
           "org.kde.plasma.notifications": ("Notificaciones", "preferences-desktop-notification"),
           "org.kde.plasma.volume": ("Volumen", "audio-volume-high"), "org.kde.plasma.battery": ("Batería", "battery"),
           "org.kde.plasma.networkmanagement": ("Red", "network-wireless"), "org.kde.plasma.weather": ("Tiempo", "weather-clear"),
           "org.kde.plasma.systemmonitor": ("Monitor", "utilities-system-monitor"), "org.kde.milou": ("Búsqueda", "search"),
           "org.kde.plasma.windowlist": ("Lista de ventanas", "window"), "org.kde.plasma.lock_logout": ("Bloquear/salir", "system-lock-screen"),
           "org.kde.plasma.colorpicker": ("Cuentagotas", "color-picker"), "org.kde.plasma.notes": ("Notas", "knotes")}
FICHA = 30


def plasmoides() -> list[str]:
    """Los ids de los plasmoides instalados (paquetes y compilados), sin los contenedores."""
    ids: set[str] = set()
    for base in (proyecto.data_home() / "plasma" / "plasmoids", Path("/usr/share/plasma/plasmoids")):
        ids |= {p.name for p in base.iterdir()} if base.is_dir() else set()
    for base in (Path("/usr/lib/x86_64-linux-gnu/qt6/plugins/plasma/applets"), Path("/usr/lib64/qt6/plugins/plasma/applets"),
                 Path("/usr/lib/qt6/plugins/plasma/applets")):
        ids |= {p.stem for p in base.glob("*.so")} if base.is_dir() else set()
    ids |= set(NOMBRES)
    return sorted(i for i in ids if i not in CONTENEDORES)


def nombre(tipo: str) -> str:
    return NOMBRES.get(tipo, (tipo.split(".")[-1], ""))[0]


def construir_mod():
    """El `construir.py` del módulo (para escribir el script exactamente como lo hará la construcción)."""
    herramientas = str(proyecto.raiz() / "herramientas")
    if herramientas not in sys.path:
        sys.path.insert(0, herramientas)
    ruta = proyecto.raiz() / "modulos" / "disposicion" / "construir.py"
    spec = importlib.util.spec_from_file_location("lliphi_disposicion_construir", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class LienzoDisposicion(Lienzo):
    def __init__(self, pagina):
        super().__init__(pagina.v.tokens)
        self.pagina = pagina
        self.var = "oscuro"
        self._fondo: dict[str, QPixmap] = {}
        self._zonas: list[tuple[QRectF, int, int]] = []   # (rect, panel, widget o -1)
        self._arrastre: tuple[int, int] | None = None
        self._iconos = iconos.temas()
        self.tablero = False
        self.zoom = 1.7   # paneles legibles en el lienzo (Ctrl + rueda cambia la escala)

    def _pix(self) -> QPixmap | None:
        if self.var not in self._fondo:
            ruta = proyecto.fondo(self.var)
            self._fondo[self.var] = QPixmap(str(ruta)).scaledToWidth(1280, Qt.SmoothTransformation) if ruta else None
        return self._fondo[self.var]

    def _icono(self, nombre_icono: str) -> QIcon | None:
        tema = proyecto.leer_ajustes("iconos-cursores")["iconos"][self.var]
        r = iconos.buscar(tema, nombre_icono, 48, self._iconos) if nombre_icono else None
        return QIcon(str(r[0])) if r else None

    def _icono_de(self, tipo: str) -> QIcon | None:
        return self._icono(NOMBRES.get(tipo, ("", ""))[1]) or self._icono(tipo)

    @staticmethod
    def lanzadores(w: dict) -> list[str]:
        """Los iconos de los lanzadores de un gestor de tareas (`launchers` = applications:<id>.desktop,…)."""
        texto = w.get("config", {}).get("General", {}).get("launchers", "")
        return [x.split(":", 1)[-1].removesuffix(".desktop") for x in texto.split(",") if x.strip()]

    def pantalla(self, rect: QRectF) -> QRectF:
        w = min(rect.width() - 24, (rect.height() - 24) * 16 / 9)
        return QRectF(rect.center().x() - w / 2, rect.center().y() - w * 9 / 32, w, w * 9 / 16)

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        t = self.tokens()
        pant = self.pantalla(rect)
        k = pant.width() / 960 * self.zoom          # pantalla de referencia de 960 px (como una de 1920 al 200 %)
        pm = self._pix()
        if pm:
            p.drawPixmap(pant, pm, QRectF(pm.rect()))
        tok = proyecto.tokens()["semanticos"][self.var]
        fondo_panel = QColor(tok["fondo"]["ventana"]["$value"]["hex"])
        fondo_panel.setAlpha(225)
        tinta = QColor(tok["texto"]["normal"]["$value"]["hex"])
        acento = QColor(tok["acento"]["base"]["$value"]["hex"])
        self._zonas = []
        f = QFont("Inter")
        f.setPixelSize(max(8, int(11 * k)))
        p.setFont(f)
        sel = self.pagina.seleccion
        for i, panel in enumerate(self.pagina.datos["paneles"]):
            grueso = panel.get("alto", 2) * 18 * k
            vertical = panel["ubicacion"] in ("left", "right")
            margen = 8 * k if panel.get("flotante") else 0
            fichas = [self._ancho_ficha(w, k, p, grueso) for w in panel["widgets"]]
            largo_total = (pant.height() if vertical else pant.width()) - 2 * margen
            fijo = sum(x for x in fichas if x > 0)
            largo = largo_total if panel.get("longitud", "fill") == "fill" else min(largo_total, fijo + 16 * k + 40 * k * fichas.count(-1))
            alin = panel.get("alineacion", "center")
            inicio = margen + {"left": 0, "center": (largo_total - largo) / 2, "right": largo_total - largo}.get(alin, 0)
            if vertical:
                x = pant.left() + margen if panel["ubicacion"] == "left" else pant.right() - margen - grueso
                r = QRectF(x, pant.top() + inicio, grueso, largo)
            else:
                y = pant.top() + margen if panel["ubicacion"] == "top" else pant.bottom() - margen - grueso
                r = QRectF(pant.left() + inicio, y, largo, grueso)
            p.setPen(QPen(acento, 2) if sel == (i, -1) else Qt.NoPen)
            p.setBrush(fondo_panel)
            p.drawRoundedRect(r, 10 * k if panel.get("flotante") else 0, 10 * k if panel.get("flotante") else 0)
            self._zonas.append((r, i, -1))
            # widgets: los espaciadores reparten lo que sobra
            libre = (r.height() if vertical else r.width()) - fijo - 8 * k
            flex = libre / fichas.count(-1) if fichas.count(-1) else 0
            pos = (r.top() if vertical else r.left()) + 4 * k
            for j, (w, ancho) in enumerate(zip(panel["widgets"], fichas)):
                largo_w = flex if ancho < 0 else ancho
                fr = QRectF(r.left() + 3 * k, pos, r.width() - 6 * k, largo_w) if vertical else QRectF(pos, r.top() + 3 * k, largo_w, r.height() - 6 * k)
                pos += largo_w
                self._zonas.append((fr, i, j))
                if ancho < 0:
                    p.setPen(QPen(QColor(tinta.red(), tinta.green(), tinta.blue(), 70), 1, Qt.DashLine))
                    p.setBrush(Qt.NoBrush)
                    p.drawRoundedRect(fr.adjusted(2, 2, -2, -2), 4, 4)
                    continue
                elegido = sel == (i, j)
                p.setPen(QPen(acento, 1.6) if elegido else Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 28) if elegido else Qt.NoBrush)
                p.drawRoundedRect(fr.adjusted(1, 1, -1, -1), 5, 5)
                lado = min(fr.height(), fr.width()) * 0.62
                apps = self.lanzadores(w) if w["tipo"] in ("org.kde.plasma.icontasks", "org.kde.plasma.taskmanager") else []
                if apps:
                    paso = fr.width() / len(apps)
                    for n, app in enumerate(apps):
                        ic = self._icono(app) or self._icono("application-x-executable")
                        celda = QRectF(fr.left() + n * paso, fr.top(), paso, fr.height())
                        if ic:
                            l2 = min(celda.width(), celda.height()) * 0.72
                            ic.paint(p, QRectF(celda.center().x() - l2 / 2, celda.center().y() - l2 / 2, l2, l2).toRect())
                    continue
                ic = self._icono_de(w["tipo"])
                if ic:
                    ic.paint(p, QRectF(fr.left() + 4 * k, fr.center().y() - lado / 2, lado, lado).toRect())
                p.setPen(tinta)
                texto = nombre(w["tipo"])
                if w["tipo"] == "org.kde.plasma.digitalclock":
                    texto = "10:06"
                p.drawText(fr.adjusted((lado + 8 * k) if ic else 4 * k, 0, -2, 0), Qt.AlignVCenter | Qt.AlignLeft, texto)

    def _ancho_ficha(self, w: dict, k: float, p: QPainter, grueso: float) -> float:
        if w["tipo"] in ("org.kde.plasma.panelspacer",):
            return -1
        if w["tipo"] in ("org.kde.plasma.icontasks", "org.kde.plasma.taskmanager") and self.lanzadores(w):
            return len(self.lanzadores(w)) * grueso
        return p.fontMetrics().horizontalAdvance(nombre(w["tipo"])) + grueso * 0.8 + 8

    def _en(self, pos: QPointF) -> tuple[int, int] | None:
        for r, i, j in reversed(self._zonas):
            if r.contains(pos):
                return i, j
        return None

    def mousePressEvent(self, e) -> None:
        hit = self._en(e.position())
        self.pagina.elegir(hit)
        self._arrastre = hit if hit and hit[1] >= 0 else None

    def mouseReleaseEvent(self, e) -> None:
        if self._arrastre:
            destino = self._en(e.position())
            if destino and destino[0] == self._arrastre[0] and destino[1] >= 0 and destino[1] != self._arrastre[1]:
                self.pagina.mover_widget(self._arrastre, destino[1])
        self._arrastre = None


class Pagina:
    def __init__(self, v):
        self.v = v
        self.datos = proyecto.leer_borrador("disposicion")
        self.seleccion: tuple[int, int] | None = (0, -1)
        # biblioteca
        bib = QWidget()
        bv = QVBoxLayout(bib)
        bv.setContentsMargins(0, 0, 0, 0)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Buscar plasmoide…")
        self.busca.textChanged.connect(self._filtrar)
        bv.addWidget(self.busca)
        self.catalogo = QListWidget()
        for tipo in plasmoides():
            it = QListWidgetItem(icono_trazo("paquete"), f"{nombre(tipo)}\n{tipo}")
            it.setData(Qt.UserRole, tipo)
            self.catalogo.addItem(it)
        self.catalogo.itemDoubleClicked.connect(lambda it: self.anadir_widget(it.data(Qt.UserRole)))
        bv.addWidget(self.catalogo, 1)
        b = QPushButton(icono_trazo("mas"), " Añadir al panel elegido")
        b.clicked.connect(lambda: self.catalogo.currentItem() and self.anadir_widget(self.catalogo.currentItem().data(Qt.UserRole)))
        bv.addWidget(b)
        self.lienzo = LienzoDisposicion(self)
        # propiedades
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.variante = QComboBox()
        self.variante.addItem("Fondo y colores del oscuro", "oscuro")
        self.variante.addItem("Fondo y colores del claro", "claro")
        self.variante.currentIndexChanged.connect(lambda: (setattr(self.lienzo, "var", self.variante.currentData()), self.lienzo.update()))
        pv.addWidget(self.variante)
        self.titulo = QLabel("Panel")
        self.titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        pv.addWidget(self.titulo)
        self.form_panel = QWidget()
        fp = QFormLayout(self.form_panel)
        fp.setContentsMargins(0, 0, 0, 0)
        self.p_ubic, self.p_ocultar, self.p_long, self.p_alin = QComboBox(), QComboBox(), QComboBox(), QComboBox()
        for cb, valores, clave in ((self.p_ubic, UBICACIONES, "ubicacion"), (self.p_ocultar, OCULTAR, "ocultar"),
                                   (self.p_long, LONGITUD, "longitud"), (self.p_alin, ALINEACION, "alineacion")):
            cb.addItems(valores)
            cb.currentTextChanged.connect(lambda x, c=clave: self._panel(c, x))
        self.p_alto = QDoubleSpinBox()
        self.p_alto.setRange(1, 6)
        self.p_alto.setSingleStep(0.5)
        self.p_alto.setSuffix(" × gridUnit")
        self.p_alto.valueChanged.connect(lambda x: self._panel("alto", int(x) if x == int(x) else x))
        self.p_flot = QCheckBox()
        self.p_flot.toggled.connect(lambda x: self._panel("flotante", x))
        fp.addRow("ubicación", self.p_ubic)
        fp.addRow("alto", self.p_alto)
        fp.addRow("ocultar", self.p_ocultar)
        fp.addRow("flotante", self.p_flot)
        fp.addRow("longitud", self.p_long)
        fp.addRow("alineación", self.p_alin)
        pv.addWidget(self.form_panel)
        fila = QHBoxLayout()
        b = QPushButton(icono_trazo("mas"), " Panel")
        b.clicked.connect(self._nuevo_panel)
        fila.addWidget(b)
        b = QPushButton(icono_trazo("quitar"), " Quitar panel")
        b.clicked.connect(self._quitar_panel)
        fila.addWidget(b)
        pv.addLayout(fila)
        self.form_widget = QWidget()
        fw = QVBoxLayout(self.form_widget)
        fw.setContentsMargins(0, 0, 0, 0)
        self.w_tipo = clase(QLabel(""), "suave")
        self.w_tipo.setTextInteractionFlags(Qt.TextSelectableByMouse)
        fw.addWidget(self.w_tipo)
        fw.addWidget(clase(QLabel("configuración ({grupo: {clave: valor}}, JSON)"), "tenue"))
        self.w_config = QPlainTextEdit()
        self.w_config.setMaximumHeight(90)
        fw.addWidget(self.w_config)
        fila = QHBoxLayout()
        for texto, icono, accion in (("", "volver", lambda: self._mover(-1)), ("", "abrir", lambda: self._mover(1)),
                                     (" Aplicar config.", "verificar", self._config), (" Quitar", "quitar", self._quitar_widget)):
            b = QPushButton(icono_trazo(icono), texto)
            b.clicked.connect(accion)
            fila.addWidget(b)
        fw.addLayout(fila)
        pv.addWidget(self.form_widget)
        pv.addWidget(nota("Clic en un panel o en un widget para elegirlo; arrastra un widget sobre otro del mismo panel para "
                          "reordenarlo; doble clic en el catálogo para añadirlo."))
        pv.addStretch(1)
        props = envolver(props)
        self.editor = Editor("Disposición", "Paneles y widgets del escritorio de Lliphi (el script de disposición del tema "
                             "global): edítalos sobre la pantalla y pruébalos en la sesión de prueba sin guardar nada.",
                             bib, self.lienzo, props, v.tokens)
        self.editor.boton("Descartar", "volver", self._descartar)
        self.editor.boton("Probar en la sesión de prueba", "ojo", self._probar)
        self.editor.boton("Guardar y construir…", "verificar", self._guardar, "primario")
        self.js = Codigo(v.tokens)
        self.editor.pestana(self.js, "escritorio.js que saldría", "codigo")
        self.widget = self.editor
        self.elegir((0, -1))
        self._mostrar()

    # ---------------------------------------------------------------- selección y edición
    def elegir(self, sel: tuple[int, int] | None) -> None:
        self.seleccion = sel
        es_panel = sel is not None and sel[1] < 0
        es_widget = sel is not None and sel[1] >= 0
        self.form_widget.setVisible(es_widget)
        if sel is None:
            self.titulo.setText("Elige un panel o un widget")
        else:
            panel = self.datos["paneles"][sel[0]]
            self.titulo.setText(f"Panel {sel[0] + 1} ({panel['ubicacion']})" + (f" · {nombre(panel['widgets'][sel[1]]['tipo'])}" if es_widget else ""))
            for w, valor in ((self.p_ubic, panel["ubicacion"]), (self.p_ocultar, panel["ocultar"]),
                             (self.p_long, panel.get("longitud", "fill")), (self.p_alin, panel.get("alineacion", "center"))):
                w.blockSignals(True)
                w.setCurrentText(valor)
                w.blockSignals(False)
            for w, valor in ((self.p_alto, panel["alto"]), (self.p_flot, panel["flotante"])):
                w.blockSignals(True)
                w.setValue(valor) if isinstance(w, QDoubleSpinBox) else w.setChecked(valor)
                w.blockSignals(False)
            if es_widget:
                w = panel["widgets"][sel[1]]
                self.w_tipo.setText(w["tipo"])
                self.w_config.setPlainText(json.dumps(w.get("config", {}), ensure_ascii=False, indent=1))
        self.form_panel.setEnabled(sel is not None)
        self.lienzo.update()

    def _panel(self, clave: str, valor) -> None:
        if self.seleccion is None:
            return
        panel = self.datos["paneles"][self.seleccion[0]]
        if clave in ("longitud", "alineacion") and valor == {"longitud": "fill", "alineacion": "center"}[clave] and clave not in panel:
            return
        panel[clave] = valor
        self._tras_cambiar()

    def anadir_widget(self, tipo: str) -> None:
        if not self.datos["paneles"]:
            self._nuevo_panel()
        i = self.seleccion[0] if self.seleccion else 0
        lista = self.datos["paneles"][i]["widgets"]
        j = self.seleccion[1] + 1 if self.seleccion and self.seleccion[1] >= 0 else len(lista)
        lista.insert(j, {"tipo": tipo})
        self.seleccion = (i, j)
        self._tras_cambiar()
        self.elegir(self.seleccion)

    def mover_widget(self, origen: tuple[int, int], j: int) -> None:
        lista = self.datos["paneles"][origen[0]]["widgets"]
        lista.insert(j, lista.pop(origen[1]))
        self._tras_cambiar()
        self.elegir((origen[0], j))

    def _mover(self, paso: int) -> None:
        if self.seleccion and self.seleccion[1] >= 0:
            i, j = self.seleccion
            n = len(self.datos["paneles"][i]["widgets"])
            if 0 <= j + paso < n:
                self.mover_widget((i, j), j + paso)

    def _config(self) -> None:
        if not (self.seleccion and self.seleccion[1] >= 0):
            return
        try:
            config = json.loads(self.w_config.toPlainText() or "{}")
            assert isinstance(config, dict) and all(isinstance(x, dict) for x in config.values())
        except (json.JSONDecodeError, AssertionError):
            self.v.marco.avisar("Configuración no válida", 'Debe ser {"Grupo": {"clave": "valor"}}.', "error")
            return
        w = self.datos["paneles"][self.seleccion[0]]["widgets"][self.seleccion[1]]
        if config:
            w["config"] = config
        else:
            w.pop("config", None)
        self._tras_cambiar()

    def _quitar_widget(self) -> None:
        if self.seleccion and self.seleccion[1] >= 0:
            i, j = self.seleccion
            if len(self.datos["paneles"][i]["widgets"]) == 1:
                self.v.marco.avisar("Un panel no queda vacío", "Quita el panel entero si no lo quieres.", "aviso")
                return
            self.datos["paneles"][i]["widgets"].pop(j)
            self._tras_cambiar()
            self.elegir((i, -1))

    def _nuevo_panel(self) -> None:
        libres = [u for u in UBICACIONES if u not in {p["ubicacion"] for p in self.datos["paneles"]}] or ["bottom"]
        self.datos["paneles"].append({"variable": f"panel{len(self.datos['paneles']) + 1}", "ubicacion": libres[0], "alto": 2,
                                      "ocultar": "none", "flotante": False, "widgets": [{"tipo": "org.kde.plasma.icontasks"}]})
        self._tras_cambiar()
        self.elegir((len(self.datos["paneles"]) - 1, -1))

    def _quitar_panel(self) -> None:
        if self.seleccion is not None and len(self.datos["paneles"]) > 1:
            self.datos["paneles"].pop(self.seleccion[0])
            self._tras_cambiar()
            self.elegir((0, -1))

    def _tras_cambiar(self) -> None:
        proyecto.guardar_borrador("disposicion", self.datos)
        self._mostrar()
        self.lienzo.update()

    def _mostrar(self) -> None:
        self.editor.codigo.setPlainText(proyecto.volcar("disposicion", self.datos))
        diff = proyecto.diff_ajustes("disposicion", self.datos)
        self.editor.diff.setPlainText(diff or "El borrador es igual a modulos/disposicion/ajustes.json.")
        try:
            self.js.setPlainText(self.script())
        except (ValueError, KeyError) as e:
            self.js.setPlainText(f"// el borrador no construye: {e}")

    def script(self, variante: str | None = None) -> str:
        # el guion lleva la imagen del fondo de la variante (decisiones 4.27): la de la sesión de prueba o la de la vista
        return construir_mod().script(proyecto.marca(), self.datos, variante or self.variante.currentData())

    def _filtrar(self, texto: str) -> None:
        for i in range(self.catalogo.count()):
            it = self.catalogo.item(i)
            it.setHidden(texto.lower() not in it.text().lower())

    # ---------------------------------------------------------------- probar y guardar
    def _probar(self) -> None:
        estado = proyecto.correr_json("sesion", "estado") or {}
        if not estado.get("activa"):
            self.v.marco.avisar("Sin sesión de prueba", "Arráncala en la Vista en vivo y vuelve: el borrador se prueba dentro, "
                                "sin guardar nada.", "aviso")
            self.v.navigate("vivo")
            return
        try:
            js = self.script(estado.get("variante"))
        except ValueError as e:
            self.v.marco.avisar("El borrador no construye", str(e), "error")
            return
        guion = Path(os.environ.get("XDG_CACHE_HOME") or proyecto.home() / ".cache") / "lliphi-studio" / "disposicion-borrador.js"
        guion.parent.mkdir(parents=True, exist_ok=True)
        # el script de disposición crea paneles nuevos: en la sesión de prueba se quitan antes los que hay
        guion.write_text("var viejos = panels();\nfor (var q = 0; q < viejos.length; q++) viejos[q].remove();\n" + js, encoding="utf-8")
        vivo = self.v.paginas.get("vivo")
        self.v.cadena([(proyecto.orden("sesion", "guion", str(guion)), "Disposición del borrador en la sesión de prueba")],
                      lambda c: c == 0 and vivo is not None and vivo.capturar(mostrar=True))

    def _descartar(self) -> None:
        proyecto.descartar_borrador("disposicion")
        self.datos = proyecto.leer_ajustes("disposicion")
        self.elegir((0, -1))
        self._mostrar()

    def _guardar(self) -> None:
        diff = proyecto.diff_ajustes("disposicion", self.datos)
        if not diff:
            self.v.marco.avisar("Sin cambios", "El borrador es igual a los ajustes del proyecto.", "info")
            return
        try:
            self.script()
        except ValueError as e:
            self.v.marco.avisar("No se guarda", str(e), "error")
            return
        caja = QMessageBox(QMessageBox.Question, "Guardar la disposición",
                           "Escribe modulos/disposicion/ajustes.json, reconstruye el tema global (que lleva el script) y "
                           "valida. Nada se aplica a tu escritorio. ¿Seguir?", QMessageBox.Yes | QMessageBox.No, self.v.ui)
        caja.setDetailedText(diff)
        if caja.exec() != QMessageBox.Yes:
            return
        proyecto.guardar_ajustes("disposicion", self.datos)
        proyecto.descartar_borrador("disposicion")
        self._mostrar()
        self.v.cadena([(proyecto.orden("generar", "--modulos", "disposicion", "--aplicar"), "Construir disposición"),
                       (proyecto.orden("generar", "validar"), "Validar")])

    def repintar(self) -> None:
        self.lienzo.update()
