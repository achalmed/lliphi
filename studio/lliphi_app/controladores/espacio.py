"""studio/lliphi_app/controladores/espacio.py — lo transversal: el rol y el estado que filtran la tabla (la
navegación), el resumen y el contexto de la barra de estado, y las acciones sobre una ruta (abrir con el sistema,
Dolphin, terminal, portapapeles). Los filtros se recuerdan en QSettings."""
from __future__ import annotations

import os
import shutil
import subprocess

from gui_comun.qt import QGuiApplication, QObject, QSettings, Property, Signal, Slot

from lliphi_app.servicios import destinos as svc

ESTADOS = (("al_dia", "Generado al día"), ("desfasado", "Desfasado"), ("sin_comprobar", "Sin comprobar"),
           ("instalado", "Instalado"), ("modificado", "Modificado"), ("sin_instalar", "Sin instalar"))
TEXTO_ESTADO = dict(ESTADOS)


class Espacio(QObject):
    filtroCambiado = Signal()
    resumenCambiado = Signal()
    contextoCambiado = Signal()
    aviso = Signal(str, str)

    def __init__(self, consola, ajustes=None, escritorio=None, parent=None):
        super().__init__(parent)
        self.escritorio = escritorio                 # gui-comun 3.0: abrir con su aplicación y mostrar en Dolphin
        self.consola, self.ajustes = consola, ajustes
        self._s = QSettings()
        self._rol = str(self._s.value("ventana/rol", "") or "")
        if self._rol not in svc.TEXTO_ROL:
            self._rol = ""
        self._estado = str(self._s.value("ventana/estado", "") or "")
        if self._estado not in TEXTO_ESTADO:
            self._estado = ""
        self._resumen = self._contexto = ""

    @Property(str, notify=filtroCambiado)
    def rol(self) -> str:
        return self._rol

    @Property(str, notify=filtroCambiado)
    def textoRol(self) -> str:
        return {"global": "Tema global", "modulo": "Módulos", "complemento": "Complementos"}.get(self._rol, "Todos los destinos")

    @Slot(str)
    def fijarRol(self, rol: str) -> None:
        rol = rol if rol in svc.TEXTO_ROL else ""
        if rol != self._rol:
            self._rol = rol
            self._s.setValue("ventana/rol", rol)
            self.filtroCambiado.emit()

    @Property(str, notify=filtroCambiado)
    def estado(self) -> str:
        return self._estado

    @Property(str, notify=filtroCambiado)
    def textoEstado(self) -> str:
        return TEXTO_ESTADO.get(self._estado, "Todos los estados")

    @Slot(str)
    def fijarEstado(self, estado: str) -> None:
        estado = estado if estado in TEXTO_ESTADO else ""
        if estado != self._estado:
            self._estado = estado
            self._s.setValue("ventana/estado", estado)
            self.filtroCambiado.emit()

    @Property(str, notify=filtroCambiado)
    def nombreNavegacion(self) -> str:
        if self._estado:
            return f"estado.{self._estado}"
        return f"rol.{self._rol}" if self._rol else "rol"

    @Property(str, notify=filtroCambiado)
    def textoFiltro(self) -> str:
        partes = []
        if self._rol:
            partes.append(self.textoRol.lower())
        if self._estado:
            partes.append(TEXTO_ESTADO[self._estado].lower())
        return " · ".join(partes) or "todos los destinos"

    # ------------------------------------------------------------- barra de estado
    @Property(str, notify=resumenCambiado)
    def resumen(self) -> str:
        return self._resumen

    @Slot(str)
    def fijarResumen(self, texto: str) -> None:
        if texto != self._resumen:
            self._resumen = texto
            self.resumenCambiado.emit()

    @Property(str, notify=contextoCambiado)
    def contexto(self) -> str:
        return self._contexto

    @Slot(str)
    def fijarContexto(self, texto: str) -> None:
        if texto != self._contexto:
            self._contexto = texto
            self.contextoCambiado.emit()

    # ------------------------------------------------------------- sobre una ruta
    @Slot(str)
    def abrir(self, ruta: str) -> None:
        if ruta and os.path.exists(ruta):
            if self.escritorio is not None:
                self.escritorio.abrirConAplicacion(ruta)
            else:
                subprocess.Popen(["xdg-open", ruta])
            self.consola.registrar("info", f"Abierto con el sistema: {ruta}")
        else:
            self.aviso.emit(f"No existe: {ruta or '(nada seleccionado)'}", "aviso")

    @Slot(str)
    def abrirEnlace(self, url: str) -> None:
        if url:
            subprocess.Popen(["xdg-open", url])

    @Slot(str)
    def abrirDolphin(self, ruta: str) -> None:
        """Dolphin con la ruta señalada (`dolphin --select`, por `Escritorio`); sin él, la carpeta con xdg-open."""
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if os.path.exists(ruta) and self.escritorio is not None:
            self.escritorio.mostrarEnDolphin(ruta)
        elif os.path.isdir(carpeta):
            subprocess.Popen(["xdg-open", carpeta])
        else:
            self.aviso.emit(f"No existe la carpeta: {carpeta}", "aviso")

    def _terminal(self) -> str:
        preferido = (self.ajustes.terminal if self.ajustes is not None else "konsole") or "konsole"
        for candidato in (preferido, "konsole", "x-terminal-emulator"):
            if shutil.which(candidato):
                return candidato
        return ""

    @Slot(str)
    def abrirTerminal(self, ruta: str) -> None:
        carpeta = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if not os.path.isdir(carpeta):
            return
        terminal = self._terminal()
        if terminal == "konsole":
            subprocess.Popen(["konsole", "--workdir", carpeta])
        elif terminal:
            subprocess.Popen([terminal], cwd=carpeta)
        else:
            self.aviso.emit("No se encontró un emulador de terminal (konsole).", "aviso")

    @Slot(str)
    def copiar(self, texto: str) -> None:
        if texto:
            QGuiApplication.clipboard().setText(texto)
            self.consola.registrar("info", f"Copiado: {texto}")

    def entradas_paleta(self, _texto: str) -> list[dict]:
        salida = [{"nombre": "ir.todos", "texto": "Ver todos los destinos", "grupo": "Vistas", "icono": "view-list-tree", "ejecutar": lambda: (self.fijarEstado(""), self.fijarRol(""))}]
        salida += [{"nombre": f"ir.rol.{r}", "texto": f"Ver {t.lower() if r != 'global' else 'el tema global'}", "grupo": "Vistas", "icono": svc.ICONO_ROL[r],
                    "ejecutar": lambda r=r: (self.fijarEstado(""), self.fijarRol(r))} for r, t in (("global", "Tema global"), ("modulo", "Módulos"), ("complemento", "Complementos"))]
        salida += [{"nombre": f"ir.estado.{e}", "texto": f"Ver los destinos: {t.lower()}", "grupo": "Vistas", "icono": "view-filter", "ejecutar": lambda e=e: self.fijarEstado(e)}
                   for e, t in ESTADOS]
        return salida
