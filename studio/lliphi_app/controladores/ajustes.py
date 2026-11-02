"""studio/lliphi_app/controladores/ajustes.py — «Configurar Lliphi Studio…»: la variante de la sesión de prueba, la
terminal y el intérprete de las órdenes, sobre QSettings."""
from __future__ import annotations

from gui_comun.qt import QObject, QSettings, Property, Signal, Slot

from lliphi_app.servicios import proyecto


class Ajustes(QObject):
    cambiado = Signal()
    guardado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._s = QSettings()

    def _get(self, clave: str, defecto: str = "") -> str:
        return str(self._s.value(clave, defecto) or defecto)

    def _set(self, clave: str, v) -> None:
        if str(v) != self._get(clave):
            self._s.setValue(clave, v)
            self.cambiado.emit()

    terminal = Property(str, lambda self: self._get("sistema/terminal", "konsole"), lambda self, v: self._set("sistema/terminal", (v or "").strip() or "konsole"), notify=cambiado)
    variante = Property(str, lambda self: self._get("sesion/variante", "oscuro") if self._get("sesion/variante", "oscuro") in ("claro", "oscuro") else "oscuro",
                        lambda self, v: self._set("sesion/variante", v if v in ("claro", "oscuro") else "oscuro"), notify=cambiado)

    @Property(str, constant=True)
    def interprete(self) -> str:
        return proyecto.python()

    @Property(bool, constant=True)
    def hayVenv(self) -> bool:
        return proyecto.hay_venv()

    @Property(str, constant=True)
    def ordenVenv(self) -> str:
        return proyecto.orden_crear_venv()

    @Property(str, constant=True)
    def raiz(self) -> str:
        return str(proyecto.raiz())

    @Property(str, constant=True)
    def version(self) -> str:
        return proyecto.version()

    @Slot()
    def guardar(self) -> None:
        self.cambiado.emit()
        self.guardado.emit()
