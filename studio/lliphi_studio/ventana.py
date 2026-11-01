"""La ventana de Lliphi Studio: el marco común de los studios (gui-comun) sobre las órdenes de Lliphi.

Nueve secciones: Dashboard, Color, Plasma, Ventanas, Iconos, Pantallas, Disposición, Vista en vivo y Construir y
desplegar. La ventana lee el proyecto y escribe solo los `ajustes.json` de los módulos; todo lo demás lo hacen
`generar.py`, `instalar.py`, `paleta.py` y `sesion.py`, con la salida en la consola de abajo. Nada toca el escritorio
real sin simular primero y confirmar.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Callable

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QStackedWidget, QWidget

from gui_comun.diseno import icono_trazo
from gui_comun.theming import aplicar_tema, disenador_de
from gui_comun.widgets.console_dock import ConsoleDock
from gui_comun.widgets.marco import montar_studio
from gui_comun.widgets.paleta import Comando
from gui_comun.workers.function_worker import FunctionWorker
from gui_comun.workers.process_worker import ProcessWorker

from lliphi_studio import proyecto

APP_VERSION = "1.0.0"
ACENTO = "carmesi"
# el logo: una gota de color sobre una ventana (tema de escritorio)
LOGO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#888888" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="15" rx="2.5"/>'
        '<path d="M3 8.5h18"/><path d="M12 11.2c-1.6 1.9-2.4 3.1-2.4 4a2.4 2.4 0 0 0 4.8 0c0-.9-.8-2.1-2.4-4z"/></svg>')

# (id, nombre en la barra lateral, icono, módulo de la página)
PAGINAS = (("dashboard", "Dashboard", "inicio", "dashboard"),
           ("color", "Color", "paleta", "color"),
           ("plasma", "Plasma", "capas", "plasma"),
           ("ventanas", "Ventanas", "ventana", "ventanas"),
           ("iconos", "Iconos y cursores", "cursor", "iconos"),
           ("pantallas", "Pantallas", "pantalla", "pantallas"),
           ("disposicion", "Disposición", "panel", "disposicion"),
           ("vivo", "Vista en vivo", "ojo", "vivo"),
           ("despliegue", "Construir y desplegar", "cohete", "despliegue"))


class Ajustes:
    def __init__(self) -> None:
        self.q = QSettings()

    def theme(self) -> str:
        return str(self.q.value("ui/tema", "oscuro"))   # como la inspiración (Qt Design Studio): oscuro de partida

    def set_theme(self, tema: str) -> None:
        self.q.setValue("ui/tema", tema)


class Ventana:
    """Envoltorio de la QMainWindow con la forma que `gui_comun.widgets.marco.montar_studio` espera."""

    def __init__(self, solo: tuple[str, ...] | None = None) -> None:
        app = QApplication.instance()
        self.settings = Ajustes()
        self.disenador = disenador_de(app) or aplicar_tema(app, self.settings.theme(), acento=ACENTO)
        self.ui = QMainWindow()
        self.ui.setWindowTitle(f"Lliphi Studio {APP_VERSION}")
        central = QWidget()
        fila = QHBoxLayout(central)
        fila.setContentsMargins(0, 0, 0, 0)
        self.ui.sidebar = QListWidget()
        self.ui.stack = QStackedWidget()
        fila.addWidget(self.ui.sidebar)
        fila.addWidget(self.ui.stack, 1)
        self.ui.setCentralWidget(central)
        self.ui.statusbar = self.ui.statusBar()
        self.console = ConsoleDock(self.ui)
        self.ui.addDockWidget(Qt.BottomDockWidgetArea, self.console)
        self._workers: list = []
        self.controllers: dict[str, SimpleNamespace] = {}
        self._page_order: list[str] = []
        self.paginas: dict[str, object] = {}
        import importlib
        for id_, nombre, icono, modulo in PAGINAS:
            if solo and id_ not in solo:
                continue
            try:
                clase_pagina = importlib.import_module(f"lliphi_studio.paginas.{modulo}").Pagina
            except ModuleNotFoundError as e:   # una sección que aún no existe en esta copia no impide abrir las demás
                if e.name != f"lliphi_studio.paginas.{modulo}":
                    raise
                continue
            pagina = clase_pagina(self)
            self.paginas[id_] = pagina
            self._pagina(id_, nombre, icono, pagina.widget)
        self.ui.sidebar.currentRowChanged.connect(self._al_cambiar)
        self.marco = montar_studio(self, nombre="Lliphi Studio", subtitulo="El centro de control de Lliphi",
                                   logo_svg=LOGO, disenador=self.disenador, primarios={}, peligro=())
        for id_, nombre, icono, _ in PAGINAS:
            if id_ in self.paginas:
                self.marco.comandos_extra.append(Comando(nombre, lambda i=id_: self.navigate(i), grupo="Secciones",
                                                         icono=icono_trazo(icono)))
        for m in proyecto.modulos():
            if m.id in proyecto.SECCION:
                self.marco.comandos_extra.append(Comando(f"Módulo {m.nombre}", lambda i=proyecto.SECCION[m.id]: self.navigate(i),
                                                         grupo="Módulos", icono=icono_trazo("paquete")))
        self.disenador.cambiado.connect(lambda _t: self._repintar())
        self.ui.sidebar.setCurrentRow(0)

    # ----------------------------------------------------------------------------------------------------- API
    def tokens(self) -> dict:
        return self.disenador.tokens

    def show(self) -> None:
        self.ui.show()

    def navigate(self, page_id: str) -> None:
        if page_id in self._page_order:
            self.ui.sidebar.setCurrentRow(self._page_order.index(page_id))

    def correr(self, argv: list[str], nombre: str, al_terminar: Callable[[int], None] | None = None) -> ProcessWorker:
        """Una orden en la consola (cwd: la raíz del proyecto); al terminar, refresca el Dashboard."""
        worker = ProcessWorker(argv, cwd=str(proyecto.raiz()), description=nombre)
        self.console.attach_process_worker(worker, nombre)
        self.console.show()
        if al_terminar:
            worker.finished_with_code.connect(al_terminar)
        worker.finished_with_code.connect(lambda _c: self._refrescar_tablero())
        self._workers.append(worker)
        worker.start()
        return worker

    def cadena(self, pasos: list[tuple[list[str], str]], al_terminar: Callable[[int], None] | None = None) -> None:
        """Varias órdenes en fila; se detiene en la primera que falle."""
        if not pasos:
            if al_terminar:
                al_terminar(0)
            return
        (argv, nombre), resto = pasos[0], pasos[1:]
        def siguiente(codigo: int) -> None:
            if codigo != 0:
                self.marco.avisar(f"{nombre}: salió {codigo}", "La cadena se detuvo; el detalle está en la consola.", "error")
                if al_terminar:
                    al_terminar(codigo)
                return
            self.cadena(resto, al_terminar)
        self.correr(argv, nombre, siguiente)

    def en_segundo_plano(self, fn: Callable, al_listo: Callable[[object], None], *args) -> FunctionWorker:
        """Una lectura lenta (órdenes con --json, recorrer carpetas) sin bloquear la ventana ni ocupar la consola."""
        w = FunctionWorker(lambda *a, **_cb: fn(*a), *args, description="lectura")   # sin progreso ni cancelación
        w.result_ready.connect(al_listo)
        w.failed.connect(lambda e: self.ui.statusbar.showMessage(f"No se pudo leer: {e}", 8000))
        w.finished.connect(lambda: self._workers.remove(w) if w in self._workers else None)
        self._workers.append(w)
        w.start()
        return w

    def run_function_worker(self, worker, nombre: str) -> None:   # lo pide el marco
        self.console.attach_function_worker(worker, nombre)
        self._workers.append(worker)
        worker.start()

    def confirmar(self, titulo: str, texto: str) -> bool:
        return QMessageBox.question(self.ui, titulo, texto) == QMessageBox.Yes

    # -------------------------------------------------------------------------------------------------- privado
    def _refrescar_tablero(self) -> None:
        for p in self.paginas.values():
            if hasattr(p, "al_cambiar_proyecto"):
                p.al_cambiar_proyecto()

    def _repintar(self) -> None:
        for p in self.paginas.values():
            if hasattr(p, "repintar"):
                p.repintar()

    def _pagina(self, id_: str, nombre: str, icono: str, widget) -> None:
        self.controllers[id_] = SimpleNamespace(widget=widget)
        self._page_order.append(id_)
        self.ui.stack.addWidget(widget)
        self.ui.sidebar.addItem(QListWidgetItem(icono_trazo(icono), nombre))

    def _al_cambiar(self, fila: int) -> None:
        self.ui.stack.setCurrentIndex(fila)
        pagina = self.paginas.get(self._page_order[fila]) if 0 <= fila < len(self._page_order) else None
        if pagina is not None and hasattr(pagina, "al_mostrar"):
            pagina.al_mostrar()

    def _open_preferences(self) -> None:
        self.navigate("despliegue")

    def _about(self) -> None:
        QMessageBox.about(self.ui, "Acerca de Lliphi Studio",
                          f"<b>Lliphi Studio</b> {APP_VERSION}<br><br>El centro de control visual de Lliphi: paleta, estilo "
                          "de Plasma, decoración, iconos y cursores, pantallas, disposición, sesión de prueba y despliegue. "
                          "No reemplaza a Inkscape ni a las herramientas de KDE: las integra. Escribe solo los "
                          "<code>ajustes.json</code> de los módulos; lo demás lo hacen las órdenes de Lliphi.")
