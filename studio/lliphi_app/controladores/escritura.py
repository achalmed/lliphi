"""studio/lliphi_app/controladores/escritura.py — generar, instalar y desinstalar en seis pasos visibles (reingeniería
2026-11-02, `docs/reingenieria.md` §3.2; `servicios/pasos.py`). Expuesto a QML como `studio.escritura`.

    planificar(tipo, ids)   pasos 1–3: el plan, los afectados y los conflictos (no escribe nada)
    ejecutar()              paso 4: la orden de Lliphi con --aplicar, ya confirmada (la confirmación es la de la acción
                            `escr.ejecutar`, con su estado de operación: instalación, eliminación o escritura)
                            → paso 5: la verificación, aparte del éxito → paso 6: el informe, guardado en la caché
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from gui_comun.qt import QObject, Property, Signal, Slot

from lliphi_app.servicios import pasos as svc

PASOS = ("Plan", "Afectados", "Conflictos", "Ejecutar", "Verificar", "Informe")


class Escritura(QObject):
    cambiado = Signal()
    terminada = Signal(str, int)     # tipo, código
    aviso = Signal(str, str)

    def __init__(self, destinos, consola, tareas, cache: Path, parent=None):
        super().__init__(parent)
        self.destinos, self.consola, self.tareas = destinos, consola, tareas
        self._cache = Path(cache)
        self._plan: svc.Plan | None = None
        self._alcanzado = 0          # 0 sin plan · 3 planificado · 4 ejecutado · 5 verificado · 6 informe
        self._codigo: int | None = None
        self._verificacion: tuple[bool, str] | None = None
        self._informe = ""
        self._ruta_informe = ""
        self._inicio = 0.0

    @Property("QVariantList", constant=True)
    def pasos(self) -> list:
        return list(PASOS)

    @Property(bool, notify=cambiado)
    def hayPlan(self) -> bool:
        return self._plan is not None

    @Property("QVariantMap", notify=cambiado)
    def plan(self) -> dict:
        return self._plan.como_dict() if self._plan else {}

    @Property(int, notify=cambiado)
    def alcanzado(self) -> int:
        return self._alcanzado

    @Property("QVariantList", notify=cambiado)
    def cuentas(self) -> list:
        if not self._plan:
            return ["", "", "", "", "", ""]
        ver = "" if self._verificacion is None else ("pasa" if self._verificacion[0] else "no pasa")
        return ["", str(len(self._plan.afectados)), str(len(self._plan.conflictos)) if self._plan.conflictos else "0",
                "" if self._codigo is None else ("bien" if self._codigo == 0 else f"código {self._codigo}"), ver, ""]

    @Property("QVariantMap", notify=cambiado)
    def resultado(self) -> dict:
        return {"codigo": -1 if self._codigo is None else self._codigo, "verificado": None if self._verificacion is None else self._verificacion[0],
                "detalle": self._verificacion[1] if self._verificacion else "", "informe": self._informe, "rutaInforme": self._ruta_informe}

    @Property(bool, notify=cambiado)
    def puedeEjecutar(self) -> bool:
        return self._plan is not None and not self._plan.bloqueado and self._alcanzado == 3 and not self.tareas.activa

    def consecuencias(self) -> str:
        if not self._plan:
            return "Prepare antes un plan (pasos 1–3)."
        p = self._plan
        cambian = [a for a in p.afectados if a["accion"] not in ("igual", "ya está", "no se toca")]
        texto = f"{p.titulo}: {len(cambian)} ruta(s) cambian de {len(p.afectados)}. {p.descripcion}"
        avisos = [c for c in p.conflictos if not c["bloquea"]]
        if avisos:
            texto += f" {len(avisos)} aviso(s) en Conflictos."
        return texto + f"\n\nOrden: {p.orden.texto()}"

    def operacion(self) -> str:
        return svc.ESTADO_OPERACION[self._plan.tipo] if self._plan else "escritura"

    # ------------------------------------------------------------------ pasos 1–3
    @Slot(str, "QVariantList")
    def planificar(self, tipo: str, ids: list) -> None:
        ids = [str(i) for i in ids or []]
        try:
            if tipo == "instalar":
                self._plan = svc.planificar_instalar(ids)
            elif tipo == "desinstalar":
                self._plan = svc.planificar_desinstalar()
            elif tipo == "generar":
                self._plan = svc.planificar_generar(ids, self.destinos._verificacion)
            else:
                return
        except Exception as e:        # noqa: BLE001
            self._plan = None
            self.aviso.emit(f"No se pudo preparar el plan: {e}", "error")
            self.cambiado.emit()
            return
        self._alcanzado, self._codigo, self._verificacion, self._informe, self._ruta_informe = 3, None, None, "", ""
        self.cambiado.emit()

    @Slot()
    def descartar(self) -> None:
        self._plan, self._alcanzado = None, 0
        self.cambiado.emit()

    # ------------------------------------------------------------------ paso 4 → 5 → 6
    @Slot()
    def ejecutar(self) -> None:
        if not self.puedeEjecutar:
            self.aviso.emit("Con un conflicto que bloquea no se ejecuta: resuélvalo y vuelva a planificar." if self._plan and self._plan.bloqueado
                            else "Prepare antes el plan.", "aviso")
            return
        p = self._plan
        self._inicio = time.monotonic()
        self.tareas.proceso(p.titulo, [str(a) for a in p.orden.argv], cwd=str(p.orden.cwd), operacion=self.operacion(),
                            entorno={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"},
                            error={"descripcion": f"«{p.titulo}» no terminó bien", "recurso": p.orden.texto(),
                                   "accion": "Lea la salida (F4). El instalador sale con 2 si falta una dependencia y con 3 si hay un "
                                             "archivo ajeno; lo instalado se revierte con el UNDO.sh del último respaldo."},
                            al_terminar=self._ejecutado)

    def _ejecutado(self, codigo: int) -> None:
        self._codigo = codigo
        self._alcanzado = 4
        self.cambiado.emit()
        p = self._plan
        if codigo != 0:
            self._cerrar()
            return
        if p.tipo == "generar":                # que lo generado coincide con una construcción nueva: generar.py verificar
            self._lineas: list[str] = []
            w = self.tareas.proceso("Verificar lo generado", [str(a) for a in self._orden_verificar().argv], cwd=str(p.orden.cwd),
                                    operacion="lectura", error=False, al_terminar=self._verificado_generar)
            w.line.connect(self._linea_verificar)
            return
        self._verificacion = svc.verificar_instalar(p) if p.tipo == "instalar" else svc.verificar_desinstalar(p)
        self._cerrar()

    def _orden_verificar(self):
        from lliphi_app.servicios import operaciones as ops, proyecto
        return ops.Orden(proyecto.orden("generar", "verificar", "--json"), proyecto.raiz())

    def _linea_verificar(self, texto: str, _err: bool = False) -> None:
        self._lineas.append(texto)

    def _verificado_generar(self, _codigo: int = 0) -> None:
        datos = None
        for linea in reversed(self._lineas):
            if linea.strip().startswith("{"):
                try:
                    datos = json.loads(linea.strip())
                except ValueError:
                    pass
                break
        if datos is None:
            self._verificacion = (False, "generar.py verificar no devolvió su informe")
        else:
            difs = list(datos.get("diferencias", []))
            self.destinos.registrar_verificacion(difs)
            ids = set(self._plan.ids)
            mias = [d for d in difs if not ids or d.partition("/")[0] in ids]
            self._verificacion = (not mias, "lo generado coincide con una construcción nueva" if not mias else f"{len(mias)} diferencia(s): {', '.join(mias[:3])}")
        self._cerrar()

    def _cerrar(self) -> None:
        p = self._plan
        self._informe = svc.informe(p, self._codigo or 0, self._verificacion, time.monotonic() - self._inicio)
        try:
            carpeta = self._cache / "informes"
            carpeta.mkdir(parents=True, exist_ok=True)
            ruta = carpeta / f"{time.strftime('%Y-%m-%d_%H%M%S')}-{p.tipo}.md"
            ruta.write_text(self._informe, encoding="utf-8")
            self._ruta_informe = str(ruta)
        except OSError:
            self._ruta_informe = ""
        self._alcanzado = 6
        self.destinos.recargar()
        self.destinos.leer_instalacion()
        self.cambiado.emit()
        self.terminada.emit(p.tipo, self._codigo if self._codigo is not None else -1)
        if self._codigo == 0 and self._verificacion and self._verificacion[0]:
            self.aviso.emit(f"{p.titulo}: hecho y verificado ({self._verificacion[1]}).", "positivo")
        elif self._codigo == 0:
            self.aviso.emit(f"{p.titulo}: terminó, pero la verificación no pasa: {self._verificacion[1] if self._verificacion else ''}", "aviso")
