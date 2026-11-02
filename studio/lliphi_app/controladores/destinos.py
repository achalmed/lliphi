"""studio/lliphi_app/controladores/destinos.py — la tabla de destinos (el tema global, los módulos y los complementos,
de sus `modulo.json`) con su estado generado (la última `generar.py verificar --json`, en la caché del studio) y su
estado de instalación (el manifiesto e `instalar.py estado --json`, releído en segundo plano); el destino actual con
su Resumen (Markdown), la paleta de los tokens como datos, sus diferencias y su registro; los respaldos del
instalador y las sesiones de prueba de la caché."""
from __future__ import annotations

from pathlib import Path

from gui_comun.modelos import ModeloFiltrado, ModeloTabla
from gui_comun.qt import QObject, QStandardPaths, Property, Signal, Slot

from lliphi_app.servicios import destinos as svc
from lliphi_app.servicios import proyecto

COLUMNAS = [("Destino", "destino"), ("Rol", "rol"), ("Clase", "clase"), ("Formato", "formato"), ("Generado", "archivos"), ("Al día", "generado"),
            ("Instalación", "instalacion"), ("Última construcción", "construccion")]


def cache_del_studio() -> Path:
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation) or (Path.home() / ".cache" / "lliphi-studio"))


class Destinos(QObject):
    cambiado = Signal()                 # la tabla, los estados, los contadores
    actualCambiado = Signal()
    registroCambiado = Signal()
    seleccionar = Signal(int)
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, tareas, cache: Path | None = None, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.tareas = espacio, consola, tareas
        self._cache = cache or cache_del_studio()
        self._tabla = ModeloTabla(COLUMNAS, parent=self)
        self._modelo = ModeloFiltrado(self._tabla, parent=self)
        self._modulos: dict[str, proyecto.Modulo] = {}
        self._orden: list[str] = []
        self._filas: dict[str, dict] = {}
        self._verificacion = svc.Verificacion(self._cache / "verificacion.json")
        self._instalacion: dict = {"instalado": False, "modulos": [], "rutas": []}
        self._actual = ""
        self._registros: dict[str, str] = {}
        self._paleta: list = []
        self._modelo.aceptar_con(self._acepta)
        espacio.filtroCambiado.connect(lambda: self._modelo.aceptar_con(self._acepta))
        self.recargar()

    modelo = Property(QObject, lambda self: self._modelo, constant=True)

    # ------------------------------------------------------------------ la tabla
    def _acepta(self, fila_origen: int) -> bool:
        f = self._tabla.fila(fila_origen)
        if self.espacio.rol and f.get("rol_id") != self.espacio.rol:
            return False
        e = self.espacio.estado
        if not e:
            return True
        if e in svc.TEXTO_GENERADO:
            return f.get("clave_generado") == e
        return f.get("clave_instalacion") == e

    @Slot()
    def recargar(self) -> None:
        """Relee los manifiestos, lo generado y la verificación guardada (F6, o tras una orden); la instalación, en segundo plano."""
        try:
            lista = proyecto.modulos()
        except Exception as e:      # noqa: BLE001
            self.consola.registrar("error", f"No se pudieron leer los módulos: {e}")
            lista = []
        self._modulos = {m.id: m for m in lista}
        self._orden = [m.id for m in lista]
        self._verificacion = svc.Verificacion(self._cache / "verificacion.json")
        try:
            self._paleta = svc.paleta(proyecto.tokens())
        except Exception:       # noqa: BLE001
            self._paleta = []
        self._filas = {m.id: svc.fila(m, self._verificacion, self._instalacion) for m in lista}
        self._tabla.poner([self._filas[i] for i in self._orden])
        self.cambiado.emit()
        if self._actual and self._actual not in self._modulos:
            self._fijar_actual("")
        elif self._actual:
            self.actualCambiado.emit()

    def leer_instalacion_ahora(self) -> None:
        """`instalar.py estado --json` en este hilo (las pruebas y las capturas)."""
        self._instalacion = svc.leer_estado_instalacion()
        self._refrescar_filas()

    def leer_instalacion(self) -> None:
        """`instalar.py estado --json` en segundo plano (al arrancar y tras instalar o desinstalar)."""
        def listo(datos):
            if isinstance(datos, dict):
                self._instalacion = datos
                self._refrescar_filas()
        self.tareas.funcion("Leyendo la instalación", lambda progress_cb=None, cancel_cb=None, message_cb=None: svc.leer_estado_instalacion(), al_terminar=listo, silenciosa=True)

    def registrar_verificacion(self, diferencias: list[str]) -> None:
        self._verificacion.registrar(diferencias)
        self._refrescar_filas()

    def _refrescar_filas(self) -> None:
        for i, id_ in enumerate(self._orden):
            m = self._modulos.get(id_)
            if m is None:
                continue
            self._filas[id_] = svc.fila(m, self._verificacion, self._instalacion)
            self._tabla.actualizar(i, **self._filas[id_])
        self.cambiado.emit()
        if self._actual:
            self.actualCambiado.emit()

    @Property(int, notify=cambiado)
    def total(self) -> int:
        return len(self._modulos)

    @Property("QVariantMap", notify=cambiado)
    def contadores(self) -> dict:
        c = {k: 0 for k in list(svc.TEXTO_GENERADO) + list(svc.TEXTO_INSTALACION) + ["global", "modulo", "complemento"]}
        for f in self._filas.values():
            c[f["clave_generado"]] += 1
            c[f["clave_instalacion"]] += 1
            c[f["rol_id"]] = c.get(f["rol_id"], 0) + 1
        return c

    @Property(str, notify=cambiado)
    def resumen(self) -> str:
        c = self.contadores
        return (f"{self.total} destinos · {c['al_dia']} al día · {c['desfasado']} desfasados · {c['sin_comprobar']} sin comprobar · "
                f"{c['instalado']} instalados · {c['modificado']} modificados")

    @Property(str, notify=cambiado)
    def fechaVerificacion(self) -> str:
        import time
        if not self._verificacion.fecha:
            return "nunca en este studio"
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(self._verificacion.fecha)) + ("" if self._verificacion.vigente else " · las fuentes cambiaron después")

    @Property("QVariantList", notify=cambiado)
    def filasRoles(self) -> list:
        c = self.contadores
        return [{"nombre": "rol", "texto": "Todos", "icono": "view-list-tree", "contador": self.total}] + [
            {"nombre": f"rol.{r}", "texto": t, "icono": svc.ICONO_ROL[r], "contador": c.get(r, 0)}
            for r, t in (("global", "Tema global"), ("modulo", "Módulos"), ("complemento", "Complementos"))]

    @Property("QVariantList", notify=cambiado)
    def filasEstados(self) -> list:
        c = self.contadores
        iconos = {"al_dia": "data-success", "desfasado": "data-error", "sin_comprobar": "data-information", "instalado": "install", "modificado": "data-warning", "sin_instalar": "edit-none"}
        return [{"nombre": f"estado.{e}", "texto": t, "icono": iconos[e], "contador": c.get(e, 0)}
                for e, t in (("al_dia", "Generado al día"), ("desfasado", "Desfasado"), ("sin_comprobar", "Sin comprobar"), ("instalado", "Instalado"), ("modificado", "Modificado"), ("sin_instalar", "Sin instalar"))]

    @Property("QVariantList", notify=cambiado)
    def ids(self) -> list:
        return list(self._orden)

    @Property(bool, notify=cambiado)
    def hayInstalacion(self) -> bool:
        return bool(self._instalacion.get("instalado"))

    @Property(str, notify=cambiado)
    def textoInstalacion(self) -> str:
        i = self._instalacion
        if not i.get("instalado"):
            return "Lliphi no está instalado en esta sesión"
        rutas = i.get("rutas", [])
        mal = sum(1 for r in rutas if not r.get("ok", True))
        return f"Lliphi {i.get('version', '?')} instalado el {str(i.get('fecha', '?'))[:16].replace('T', ' ')} · {len(i.get('modulos', []))} destinos · {len(rutas)} rutas" + (f" · {mal} modificadas" if mal else " · todas intactas")

    # ------------------------------------------------------------------ el destino actual
    @Slot(int)
    def fijarFila(self, fila: int) -> None:
        if fila < 0 or fila >= self._modelo.rowCount():
            return
        self._fijar_actual(self._tabla.fila(self._modelo.filaOrigen(fila)).get("id", ""))

    @Slot(str, result=int)
    def filaDe(self, id_: str) -> int:
        for i, f in enumerate(self._tabla.todas()):
            if f.get("id") == id_:
                return self._modelo.filaVisible(i)
        return -1

    @Slot(str, result=bool)
    def irA(self, id_: str) -> bool:
        if id_ not in self._modulos:
            return False
        if self.filaDe(id_) < 0:
            self.espacio.fijarEstado("")
            self.espacio.fijarRol("")
        self._fijar_actual(id_)
        self.seleccionar.emit(self.filaDe(id_))
        return True

    def _fijar_actual(self, id_: str) -> None:
        self._actual = id_ if id_ in self._modulos else ""
        self.actualCambiado.emit()
        self.registroCambiado.emit()

    def _m(self) -> proyecto.Modulo | None:
        return self._modulos.get(self._actual)

    @Property(bool, notify=actualCambiado)
    def hayActual(self) -> bool:
        return self._m() is not None

    @Property(str, notify=actualCambiado)
    def id(self) -> str:
        return self._actual

    @Property(str, notify=actualCambiado)
    def nombre(self) -> str:
        m = self._m()
        return m.nombre if m else ""

    @Property(str, notify=actualCambiado)
    def resumenCorto(self) -> str:
        m = self._m()
        return m.datos.get("resumen", "") if m else ""

    @Property(str, notify=actualCambiado)
    def rol(self) -> str:
        m = self._m()
        return m.rol if m else ""

    @Property(str, notify=actualCambiado)
    def textoRol(self) -> str:
        m = self._m()
        return svc.TEXTO_ROL.get(m.rol, m.rol) if m else ""

    @Property(str, notify=actualCambiado)
    def icono(self) -> str:
        m = self._m()
        return svc.ICONO_ROL.get(m.rol, "package-x-generic") if m else ""

    @Property(str, notify=actualCambiado)
    def textoGenerado(self) -> str:
        return self._filas.get(self._actual, {}).get("generado", "")

    @Property(str, notify=actualCambiado)
    def nivelGenerado(self) -> str:
        return self._filas.get(self._actual, {}).get("nivel_generado", "")

    @Property(str, notify=actualCambiado)
    def textoEstadoInstalacion(self) -> str:
        return self._filas.get(self._actual, {}).get("instalacion", "")

    @Property(str, notify=actualCambiado)
    def nivelInstalacion(self) -> str:
        return self._filas.get(self._actual, {}).get("nivel_instalacion", "")

    @Property(bool, notify=actualCambiado)
    def instalable(self) -> bool:
        return self._filas.get(self._actual, {}).get("clave_instalacion", "no_instalable") != "no_instalable"

    @Property(bool, notify=actualCambiado)
    def generable(self) -> bool:
        m = self._m()
        return bool(m) and m.clase != "externo"

    @Property(str, notify=actualCambiado)
    def carpetaGenerado(self) -> str:
        m = self._m()
        return str(m.generado) if m else str(proyecto.raiz() / "generado")

    @Property(str, notify=actualCambiado)
    def carpeta(self) -> str:
        m = self._m()
        return str(m.carpeta) if m else str(proyecto.raiz())

    @Property(str, notify=actualCambiado)
    def archivoAjustes(self) -> str:
        m = self._m()
        return str(m.ajustes) if m and m.ajustes.is_file() else ""

    @Property(str, notify=actualCambiado)
    def archivoManifiesto(self) -> str:
        m = self._m()
        return str(m.carpeta / "modulo.json") if m else ""

    @Property(str, notify=actualCambiado)
    def resumenMarkdown(self) -> str:
        m = self._m()
        return svc.resumen_markdown(m, self._filas[self._actual], self._instalacion) if m else ""

    @Property(str, notify=actualCambiado)
    def diferencias(self) -> str:
        if not self._actual:
            return ""
        d = self._verificacion.diferencias.get(self._actual, [])
        if not self._verificacion.fecha:
            return ""
        cabecera = f"# verificar · {self.fechaVerificacion}\n\n"
        return cabecera + ("\n".join(d) + "\n" if d else "generado/" + self._actual + "/ coincide con una construcción nueva desde los tokens.\n")

    @Property(int, notify=actualCambiado)
    def nDiferencias(self) -> int:
        return len(self._verificacion.diferencias.get(self._actual, [])) if self._actual else 0

    @Property("QVariantList", notify=cambiado)
    def paleta(self) -> list:
        return list(self._paleta)

    # ------------------------------------------------------------------ el registro por destino
    def anotar(self, id_: str, texto: str) -> None:
        self._registros[id_] = texto
        if id_ == self._actual:
            self.registroCambiado.emit()

    @Property(str, notify=registroCambiado)
    def registro(self) -> str:
        return self._registros.get(self._actual, "") if self._actual else self._registros.get("", "")

    # ------------------------------------------------------------------ respaldos y sesiones
    @Property("QVariantList", notify=cambiado)
    def respaldos(self) -> list:
        try:
            return [{"carpeta": str(r.carpeta), "nombre": r.carpeta.name, "archivos": r.archivos, "undo": str(r.undo)} for r in proyecto.respaldos()]
        except Exception:       # noqa: BLE001
            return []

    @Property("QVariantList", notify=cambiado)
    def sesiones(self) -> list:
        """Las sesiones de prueba que quedaron en la caché (nombre y peso): se borran a mano, nunca desde aquí."""
        base = Path(proyecto.os.environ.get("XDG_CACHE_HOME") or proyecto.home() / ".cache") / proyecto.marca().get("id", "lliphi") / "sesiones"
        salida = []
        if base.is_dir():
            for d in sorted(base.iterdir(), reverse=True):
                if d.is_dir():
                    peso = sum(p.stat().st_size for p in d.rglob("*") if p.is_file())
                    salida.append({"nombre": d.name, "carpeta": str(d), "peso": f"{peso / 1024 / 1024:.0f} MB"})
        return salida

    def entradas_paleta(self, _texto: str) -> list[dict]:
        return [{"nombre": f"destino.{m.id}", "texto": f"{m.nombre} ({m.id})", "grupo": svc.TEXTO_ROL.get(m.rol, m.rol), "icono": svc.ICONO_ROL.get(m.rol, ""),
                 "ejecutar": lambda i=m.id: self.irA(i)} for m in self._modulos.values()]
