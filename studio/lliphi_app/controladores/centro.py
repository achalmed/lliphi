"""studio/lliphi_app/controladores/centro.py — la mesa de diseño y las áreas (reingeniería 2026-11-02,
`docs/reingenieria.md` §3.1; rediseño del 2026-11-18, decisiones 5.51). Expuesto a QML como `studio.centro`.

La mesa: el sistema de diseño de los tokens (`sistema`: las rampas a la izquierda y la maqueta del escritorio a la derecha)
y, al pie, los destinos por área con el estado de lo generado (`grupos`, `cambios`). Los tokens se vigilan: cuando
`paleta.py` (o cualquiera) reescribe `tokens/tokens.json`, la mesa se relee sola y la maqueta se repinta en vivo.

La página de un área enseña lo suyo (la paleta con color real en el sistema de diseño; las fuentes en la tipografía; los
fondos; los temas de iconos) y las tarjetas de sus destinos con lo generado, la instalación, la compatibilidad y, del
destino elegido, lo instalado frente a lo generado archivo por archivo y la diferencia del archivo elegido. Lee lo que
ya leen los destinos (`Destinos`: la verificación guardada y el estado de la instalación), sin repetirlo.
"""
from __future__ import annotations

from gui_comun.qt import QFileSystemWatcher, QObject, QTimer, Property, Signal, Slot

from lliphi_app.servicios import areas, diseno, proyecto

PENDIENTES = ("desfasado", "sin_generar")       # lo que «Generar lo que cambió» regenera


class Centro(QObject):
    areaCambiada = Signal()
    cambiado = Signal()               # tarjetas (tras releer o tras una orden)
    destinoCambiado = Signal()        # el destino elegido y sus pares
    parCambiado = Signal()
    aviso = Signal(str, str)

    def __init__(self, destinos, parent=None):
        super().__init__(parent)
        self.destinos = destinos
        self._area = "diseno"
        self._destino = ""
        self._pares: list[dict] = []
        self._par = -1
        self._diferencia: dict = {}
        self._sistema: dict = {}
        self._fuentes: dict = {}
        destinos.cambiado.connect(self._releer)
        # los tokens en vivo: KConfig y paleta.py escriben por archivo temporal y renombrado, así que se vigila también la
        # carpeta y se vuelve a añadir el archivo tras cada aviso; una ráfaga de avisos se agrupa en una relectura
        self._vigia = QFileSystemWatcher(self)
        self._espera = QTimer(self)
        self._espera.setSingleShot(True)
        self._espera.setInterval(300)
        self._espera.timeout.connect(self._tokens_cambiaron)
        self._vigia.fileChanged.connect(lambda *_: self._espera.start())
        self._vigia.directoryChanged.connect(lambda *_: self._espera.start())
        self._vigilar()
        self._releer()

    def _vigilar(self) -> None:
        tokens = proyecto.raiz() / "tokens" / "tokens.json"
        for ruta in (tokens.parent, tokens):
            if ruta.exists() and str(ruta) not in self._vigia.files() + self._vigia.directories():
                self._vigia.addPath(str(ruta))

    def _tokens_cambiaron(self) -> None:
        self._vigilar()
        self.destinos.recargar()          # los estados (la verificación deja de ser vigente) y, por su señal, la mesa

    def _releer(self) -> None:
        try:
            self._sistema = diseno.sistema()
        except Exception as e:        # noqa: BLE001  unos tokens rotos no tumban la ventana
            self._sistema = {"variantes": [], "tipografia": {}, "error": str(e)}
        self._fuentes = {}
        if self._destino:
            self._comparar()
        self.cambiado.emit()

    # ------------------------------------------------------------------ las áreas
    @Property("QVariantList", constant=True)
    def areas(self) -> list:
        return [{k: v for k, v in a.items()} | {"cuantos": len(a["destinos"])} for a in areas.areas()]

    @Property(str, notify=areaCambiada)
    def area(self) -> str:
        return self._area

    @Property("QVariantMap", notify=areaCambiada)
    def datosArea(self) -> dict:
        return areas.area(self._area)

    @Slot(str)
    def fijarArea(self, id_: str) -> None:
        if id_ != self._area and id_ in [a["id"] for a in areas.areas()]:
            self._area = id_
            primero = (areas.area(id_)["destinos"] or [""])[0]
            self.areaCambiada.emit()
            self.fijarDestino(primero)
            self.cambiado.emit()

    @Slot(str)
    def irADestino(self, id_: str) -> None:
        """Lleva al área del destino y lo elige (la paleta de órdenes, `--destino`)."""
        self.fijarArea(areas.area_de(id_))
        self.fijarDestino(id_)

    # ------------------------------------------------------------------ las tarjetas del área
    @Property("QVariantList", notify=cambiado)
    def tarjetas(self) -> list:
        salida = []
        for id_ in areas.area(self._area)["destinos"]:
            m = self.destinos._modulos.get(id_)
            if m is not None:
                salida.append(areas.tarjeta(m, self.destinos._verificacion, self.destinos._instalacion))
        return salida

    @Property("QVariantMap", notify=cambiado)
    def sistema(self) -> dict:
        return self._sistema

    # ------------------------------------------------------------------ el pie de la mesa: los destinos por área
    @Property("QVariantList", notify=cambiado)
    def grupos(self) -> list:
        """Las áreas con destinos (y la tipografía, que no tiene) y, de cada destino, su estado: lo generado y la instalación."""
        filas = self.destinos._filas
        salida = []
        for a in areas.areas():
            if a["id"] == "diseno":
                continue
            lista = []
            for id_ in a["destinos"]:
                f = filas.get(id_)
                if f is None:
                    continue
                lista.append({"id": id_, "nombre": f["destino"], "generado": f["generado"], "clave_generado": f["clave_generado"],
                              "nivel_generado": f["nivel_generado"], "instalacion": f["instalacion"], "clave_instalacion": f["clave_instalacion"],
                              "nivel_instalacion": f["nivel_instalacion"]})
            nota = ""
            if a["id"] == "tipografia":
                familias = (self._sistema.get("tipografia") or {}).get("familias") or {}
                nota = " · ".join(v[0] for v in familias.values() if v)
            salida.append({"id": a["id"], "titulo": a["titulo"], "icono": a["icono"], "que": a["que"], "destinos": lista, "nota": nota})
        return salida

    def pendientes(self) -> list[str]:
        """Los destinos que la última verificación da por desfasados o que no tienen nada en generado/ (y se generan)."""
        return [id_ for id_, f in self.destinos._filas.items() if f["clave_generado"] in PENDIENTES
                and (f["clase"] == "paquete" or id_ == "global")]

    @Property("QVariantMap", notify=cambiado)
    def cambios(self) -> dict:
        """Lo que «Generar lo que cambió» haría: con una verificación vigente, los pendientes; sin ella, verificar antes."""
        vigente = self.destinos._verificacion.vigente
        n = len(self.pendientes()) if vigente else 0
        if not self.destinos._verificacion.fecha:
            texto = "Sin verificar: F5 verifica y prepara lo que cambió"
        elif not vigente:
            texto = "Las fuentes cambiaron desde la última verificación: F5 verifica antes"
        else:
            texto = f"{n} destino(s) por generar" if n else "Lo generado está al día con los tokens"
        return {"vigente": vigente, "n": n, "texto": texto, "nivel": "neutro" if not vigente else "negativo" if n else "positivo"}

    @Property("QVariantList", notify=cambiado)
    def fuentes(self) -> list:
        """Las familias de los tokens con su estado en fontconfig (se consulta al abrir la tipografía)."""
        familias = [f for lista in (self._sistema.get("tipografia", {}).get("familias") or {}).values() for f in lista]
        if not self._fuentes and self._area == "tipografia":
            self._fuentes = areas.fuentes_instaladas(familias)
        return [{"familia": f, "instalada": self._fuentes.get(f), "generica": f in ("sans-serif", "serif", "monospace")} for f in familias]

    @Property("QVariantList", notify=cambiado)
    def fondos(self) -> list:
        return areas.fondos() if self._area == "fondos" else []

    @Property("QVariantMap", notify=cambiado)
    def iconos(self) -> dict:
        return areas.iconos() if self._area == "iconos" else {}

    # ------------------------------------------------------------------ el destino elegido: instalado frente a generado
    @Property(str, notify=destinoCambiado)
    def destino(self) -> str:
        return self._destino

    @Slot(str)
    def fijarDestino(self, id_: str) -> None:
        if id_ == self._destino and self._pares:
            return
        self._destino = id_
        self._comparar()
        self.destinoCambiado.emit()

    def _comparar(self) -> None:
        m = self.destinos._modulos.get(self._destino)
        try:
            self._pares = areas.comparar(self._destino) if m is not None and m.clase == "paquete" else []
        except Exception as e:        # noqa: BLE001
            self._pares = []
            self.aviso.emit(f"No se pudo comparar {self._destino}: {e}", "error")
        primero = next((i for i, p in enumerate(self._pares) if p["estado"] not in ("igual",)), 0 if self._pares else -1)
        self.fijarPar(primero)
        self.destinoCambiado.emit()

    @Property("QVariantList", notify=destinoCambiado)
    def pares(self) -> list:
        return self._pares

    @Property("QVariantMap", notify=destinoCambiado)
    def cuentaPares(self) -> dict:
        c = {k: 0 for k in areas.TEXTO_PAR}
        for p in self._pares:
            c[p["estado"]] += 1
        return c

    @Property(int, notify=parCambiado)
    def par(self) -> int:
        return self._par

    @Slot(int)
    def fijarPar(self, i: int) -> None:
        self._par = i if 0 <= i < len(self._pares) else -1
        if self._par >= 0:
            p = self._pares[self._par]
            self._diferencia = areas.diferencia(p["origen"], p["destino"]) if p["estado"] in ("distinto", "ajeno", "igual") else \
                {"ruta": p["destinoCorto"], "izquierda": "Instalado", "derecha": "Generado", "filas": [], "vacia": True, "binario": False,
                 "notas": [p["texto"].capitalize() + "."], "anadidas": 0, "quitadas": 0, "trozos": 0, "recortado": False}
        else:
            self._diferencia = {}
        self.parCambiado.emit()

    @Property("QVariantMap", notify=parCambiado)
    def diferencia(self) -> dict:
        return self._diferencia

    @Slot(result=str)
    def archivoAjustes(self) -> str:
        m = self.destinos._modulos.get(self._destino)
        return str(m.ajustes) if m is not None and m.ajustes.exists() else ""

    @Slot(str, result=str)
    def carpetaGenerado(self, id_: str) -> str:
        m = self.destinos._modulos.get(id_)
        return str(m.generado) if m is not None and m.generado.exists() else str(proyecto.raiz() / "generado")
