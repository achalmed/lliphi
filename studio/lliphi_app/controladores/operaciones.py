"""studio/lliphi_app/controladores/operaciones.py — la operación actual (del catálogo `servicios.operaciones`): F5 (la
orden de Lliphi en simulación o de solo lectura, o el plan que la ventana calcula) y Ctrl+Intro (la orden que escribe
o instala, tras confirmar en QML con la orden exacta, lo que toca y el respaldo con su UNDO.sh) por
`gui_comun.tareas.proceso` (una a la vez; la salida íntegra en el panel inferior; Esc cancela); el plan y el registro
por operación en la caché del studio; el registro de cada destino. Al terminar «verificar», los estados de todos
los destinos se actualizan; al terminar una instalación, se relee la instalación."""
from __future__ import annotations

import json
import time
from pathlib import Path

from gui_comun.qt import QObject, QSettings, Property, Signal, Slot

from lliphi_app.servicios import operaciones as ops
from lliphi_app.servicios import proyecto


class Operaciones(QObject):
    cambiado = Signal()
    corridaCambiada = Signal()
    terminada = Signal(str, bool, int)      # id, aplicar, código
    aviso = Signal(str, str)

    def __init__(self, espacio, destinos, ajustes, consola, tareas, cache: Path | None = None, parent=None):
        super().__init__(parent)
        self.espacio, self.destinos, self.ajustes, self.consola, self.tareas = espacio, destinos, ajustes, consola, tareas
        self._s = QSettings()
        self._cache = (cache or destinos._cache) / "operaciones"
        guardada = str(self._s.value("operacion/actual", "generar") or "generar")
        self._actual = guardada if ops.operacion(guardada) else "generar"
        self._respaldo = ""
        self._worker = None
        self._lineas: list[str] = []
        self._inicio = 0.0
        self._argv: list[str] = []
        destinos.actualCambiado.connect(self.cambiado)
        destinos.cambiado.connect(self.cambiado)
        tareas.cambiada.connect(self.cambiado)
        tareas.linea.connect(self._linea)

    # ------------------------------------------------------------ la operación actual
    def _op(self) -> ops.Operacion | None:
        return ops.operacion(self._actual)

    @Property("QVariantList", constant=True)
    def lista(self) -> list:
        grupos = dict(ops.GRUPOS)
        return [{"id": o.id, "titulo": o.titulo, "descripcion": o.descripcion, "grupo": grupos[o.grupo], "icono": o.icono} for o in ops.OPERACIONES]

    @Property(int, notify=cambiado)
    def indiceActual(self) -> int:
        return next((i for i, o in enumerate(ops.OPERACIONES) if o.id == self._actual), -1)

    @Slot(int)
    def fijarPorIndice(self, i: int) -> None:
        if 0 <= i < len(ops.OPERACIONES):
            self.fijar(ops.OPERACIONES[i].id)

    @Slot(str)
    def fijar(self, id_: str) -> None:
        if ops.operacion(id_) is None:
            return
        if id_ != self._actual:
            self._actual = id_
            self._s.setValue("operacion/actual", id_)
        self.cambiado.emit()
        self.corridaCambiada.emit()

    @Property(str, notify=cambiado)
    def actual(self) -> str:
        return self._actual

    @Property(str, notify=cambiado)
    def titulo(self) -> str:
        o = self._op()
        return o.titulo if o else ""

    @Property(str, notify=cambiado)
    def descripcion(self) -> str:
        o = self._op()
        return o.descripcion if o else ""

    @Property(str, notify=cambiado)
    def grupo(self) -> str:
        o = self._op()
        return dict(ops.GRUPOS)[o.grupo] if o else ""

    @Property(str, notify=cambiado)
    def verbo(self) -> str:
        o = self._op()
        return o.verbo if o else "Simular"

    @Property(bool, notify=cambiado)
    def escribe(self) -> bool:
        o = self._op()
        return bool(o and o.escribe)

    @Property(bool, notify=cambiado)
    def instala(self) -> bool:
        o = self._op()
        return bool(o and o.instala)

    @Property(bool, notify=cambiado)
    def sobreDestino(self) -> bool:
        o = self._op()
        return bool(o and o.sobre_destino)

    @Property(bool, notify=cambiado)
    def tieneSimular(self) -> bool:
        o = self._op()
        return bool(o and (o.simular is not None or o.plan is not None))

    @Property(str, notify=cambiado)
    def queToca(self) -> str:
        o = self._op()
        return o.toca if o else ""

    @Property(str, notify=cambiado)
    def respaldo(self) -> str:
        return self._respaldo

    @Slot(str)
    def fijarRespaldo(self, carpeta: str) -> None:
        if carpeta != self._respaldo:
            self._respaldo = carpeta
            self.cambiado.emit()
            self.corridaCambiada.emit()

    def contexto(self) -> ops.Contexto:
        return ops.Contexto(raiz=proyecto.raiz(), id=self.destinos.id, variante=self.ajustes.variante, respaldo=self._respaldo)

    @Property(str, notify=cambiado)
    def ordenSimular(self) -> str:
        o = self._op()
        if o is None:
            return ""
        if o.simular is None:
            return "(el plan lo calcula la ventana sin correr nada)" if o.plan else "(sin modo de solo lectura: con Ctrl+Intro se aplica)"
        try:
            return o.simular(self.contexto()).texto()
        except Exception as e:      # noqa: BLE001
            return f"(no se puede armar la orden: {e})"

    @Property(str, notify=cambiado)
    def ordenAplicar(self) -> str:
        o = self._op()
        if o is None or o.aplicar is None:
            return ""
        try:
            return o.aplicar(self.contexto()).texto()
        except Exception as e:      # noqa: BLE001
            return f"(no se puede armar la orden: {e})"

    # ----------------------------------------------------------- disponibilidad
    @Property(bool, notify=cambiado)
    def enCurso(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    @Property(str, notify=cambiado)
    def motivoNoSimular(self) -> str:
        o = self._op()
        if o is None:
            return "No hay operación elegida."
        if self.tareas.activa:
            return "Hay una orden en curso (Esc la cancela)."
        if o.sobre_destino and not self.destinos.hayActual:
            return "Elige primero un destino en la tabla."
        if o.id == "generar" and self.destinos.hayActual and not self.destinos.generable:
            return "Este destino es externo (terceros): no se genera; se instala con «Dependencias de terceros»."
        if o.id == "instalar" and self.destinos.hayActual and not self.destinos.instalable:
            return "Este destino no se instala por sí solo (es un componente del tema global o un externo)."
        if o.id == "revertir" and not self._respaldo:
            return "Elige un respaldo (Herramientas › Respaldos y volver atrás…)."
        if o.simular is None and o.plan is None:
            return "Esta operación no tiene modo de solo lectura: con Ctrl+Intro se aplica."
        return ""

    @Property(bool, notify=cambiado)
    def puedeSimular(self) -> bool:
        return self.motivoNoSimular == ""

    @Property(str, notify=cambiado)
    def motivoNoAplicar(self) -> str:
        o = self._op()
        if o is None or o.aplicar is None:
            return "Esta operación no tiene modo «aplicar»: con F5 se ejecuta."
        if self.tareas.activa:
            return "Hay una orden en curso (Esc la cancela)."
        if o.sobre_destino and not self.destinos.hayActual:
            return "Elige primero un destino en la tabla."
        if o.id == "generar" and self.destinos.hayActual and not self.destinos.generable:
            return "Este destino es externo: no se genera."
        if o.id == "instalar" and self.destinos.hayActual and not self.destinos.instalable:
            return "Este destino no se instala por sí solo."
        if o.id == "revertir" and not self._respaldo:
            return "Elige un respaldo (Herramientas › Respaldos y volver atrás…)."
        return ""

    @Property(bool, notify=cambiado)
    def puedeAplicar(self) -> bool:
        return self.motivoNoAplicar == ""

    @Property(str, notify=cambiado)
    def textoConfirmacion(self) -> str:
        o = self._op()
        if o is None:
            return ""
        lineas = [f"Orden: {self.ordenAplicar}", "", f"Esta operación {o.toca}."]
        if o.sobre_destino and self.destinos.hayActual:
            lineas.append(f"Destino: {self.destinos.nombre} ({self.destinos.id}).")
        if o.instala and o.id != "revertir":
            lineas.append("Reversible: el instalador respalda con SHA-256 lo que cambia y deja UNDO.sh en ~/.local/state/lliphi/respaldos/<fecha>/ "
                          "(Herramientas › Respaldos y volver atrás…).")
        if o.id == "revertir":
            lineas.append(f"Respaldo: {self._respaldo}")
        if o.id == "sesion_arrancar":
            lineas.append("Consume RAM (un Plasma entero) y deja cientos de MB en $XDG_CACHE_HOME/lliphi/sesiones/; sesion.py cerrar la termina.")
        return "\n".join(lineas)

    # ------------------------------------------------------------------ correr
    @Slot(result=bool)
    def simular(self) -> bool:
        o = self._op()
        if o is None or not self.puedeSimular:
            self.aviso.emit(self.motivoNoSimular, "aviso")
            return False
        if o.simular is None:
            texto = o.plan(self.contexto())
            self._escribir(o.id, False, f"# {time.strftime('%Y-%m-%d %H:%M:%S')} · plan · {o.titulo}\n\n{texto}\n")
            for linea in texto.splitlines():
                self.consola.escribir(linea, "info")
            self.aviso.emit(f"Plan de «{o.titulo}» en la pestaña Operación" + (": aplica con Ctrl+Intro." if o.aplicar else "."), "informacion")
            self.corridaCambiada.emit()
            return True
        return self._lanzar(o, o.simular(self.contexto()), aplicar=False)

    @Slot(result=bool)
    def aplicar(self) -> bool:
        o = self._op()
        if o is None or not self.puedeAplicar:
            self.aviso.emit(self.motivoNoAplicar, "aviso")
            return False
        return self._lanzar(o, o.aplicar(self.contexto()), aplicar=True)

    def _lanzar(self, o: ops.Operacion, orden: ops.Orden, aplicar: bool) -> bool:
        argv = [str(a) for a in orden.argv]
        programa = Path(argv[1]) if len(argv) > 1 and argv[1].endswith(".py") else None
        if programa is not None and not programa.is_file():
            self.aviso.emit(f"No existe {programa}.", "error")
            return False
        self._argv, self._lineas, self._inicio = argv, [], time.monotonic()
        destino = self.destinos.id if o.sobre_destino else ""
        verbo = "Aplicando" if aplicar else ("Simulando" if o.escribe else "Ejecutando")
        nombre = f"{verbo}: {o.titulo}" + (f" · {destino}" if destino else "")
        self._worker = self.tareas.proceso(nombre, argv, cwd=str(orden.cwd), entorno={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
                                           al_terminar=lambda codigo, i=o.id, a=aplicar, d=destino: self._fin(codigo, i, a, d))
        self.cambiado.emit()
        self.corridaCambiada.emit()
        return True

    def _linea(self, texto: str, nivel: str) -> None:
        if self._worker is not None:
            self._lineas.append(texto)

    def _fin(self, codigo: int, id_: str, aplicar: bool, destino: str) -> None:
        self._worker = None
        segundos = time.monotonic() - self._inicio
        o = ops.operacion(id_)
        titulo = o.titulo if o else id_
        lineas = self._lineas[1:] if self._lineas and self._lineas[0].startswith("$ ") else self._lineas
        cuerpo = "\n".join(lineas) + "\n"
        cabecera = (f"# {time.strftime('%Y-%m-%d %H:%M:%S')} · {'aplicado' if aplicar else 'simulación'} · {titulo}" + (f" · {destino}" if destino else "") + "\n"
                    f"# {' '.join(Path(a).name if a.startswith('/') else a for a in self._argv)}\n# código de salida {codigo} · {segundos:.1f} s\n\n")
        self._escribir(id_, aplicar, cabecera + cuerpo)
        self.destinos.anotar(destino, cabecera + cuerpo)
        if id_ == "verificar":
            datos = None
            for linea in reversed(lineas):
                if linea.strip().startswith("{"):
                    try:
                        datos = json.loads(linea.strip())
                    except ValueError:
                        datos = None
                    break
            if datos is not None:
                self.destinos.registrar_verificacion(list(datos.get("diferencias", [])))
                n = len(datos.get("diferencias", []))
                self.consola.escribir(f"[verificar] {datos.get('archivos', '?')} archivos · {n} diferencia(s) · {'al día' if not n else 'DERIVA'}", "ok" if not n else "warn")
                for x in datos.get("diferencias", []):
                    self.consola.escribir("  " + x, "warn")
                self.aviso.emit("Todo lo generado está al día con los tokens." if not n else f"{n} diferencia(s): mira «Desfasado» en la navegación y la pestaña Diferencias.",
                                "positivo" if not n else "aviso")
            else:
                self.aviso.emit(f"Verificar terminó con código {codigo} sin informe: revisa la salida (F4).", "error")
        elif codigo == 0:
            que = "aplicada" if aplicar else ("simulada" if o and o.escribe else "ejecutada")
            self.aviso.emit(f"{titulo} {que} en {segundos:.1f} s" + (": revisa la salida y aplica con Ctrl+Intro." if not aplicar and o and o.aplicar else "."),
                            "positivo" if aplicar else "informacion")
        else:
            self.aviso.emit(f"{titulo} terminó con código {codigo} ({segundos:.1f} s): revisa la salida (F4).", "error")
        if aplicar or id_ in ("estado", "comprobar", "verificar"):
            if id_ in ("generar", "generar_todo", "paleta", "empaquetar"):
                self.destinos.recargar()
            if o and (o.instala or id_ in ("estado", "comprobar", "dependencias")):
                self.destinos.leer_instalacion()
        self.cambiado.emit()
        self.corridaCambiada.emit()
        self.terminada.emit(id_, aplicar, codigo)

    @Slot()
    def cancelar(self) -> None:
        if self.enCurso:
            self.tareas.cancelar()

    # ------------------------------------------------------------- plan y registro
    def _archivo(self, id_: str, aplicar: bool) -> Path:
        return self._cache / f"{id_}.{'registro' if aplicar else 'plan'}.txt"

    def _escribir(self, id_: str, aplicar: bool, texto: str) -> None:
        try:
            self._cache.mkdir(parents=True, exist_ok=True)
            self._archivo(id_, aplicar).write_text(texto, encoding="utf-8")
        except OSError as e:
            self.consola.registrar("warn", f"No se pudo guardar el {'registro' if aplicar else 'plan'}: {e}")

    def _leer(self, aplicar: bool) -> str:
        o = self._op()
        if o is None:
            return ""
        try:
            return self._archivo(o.id, aplicar).read_text(encoding="utf-8")
        except OSError:
            return ""

    @Property(str, notify=corridaCambiada)
    def plan(self) -> str:
        return self._leer(False)

    @Property(str, notify=corridaCambiada)
    def registro(self) -> str:
        return self._leer(True)

    def entradas_paleta(self, _texto: str) -> list[dict]:
        grupos = dict(ops.GRUPOS)
        return [{"nombre": f"op.ir.{o.id}", "texto": f"Operación: {o.titulo}", "grupo": grupos[o.grupo], "icono": o.icono, "ejecutar": lambda i=o.id: self.fijar(i)}
                for o in ops.OPERACIONES]
