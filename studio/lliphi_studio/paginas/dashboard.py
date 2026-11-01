"""Dashboard: el estado de los seis módulos (y del tema global y los complementos), las versiones, las dependencias y la
construcción. Lo lento (validar, verificar y el estado de la instalación, con `--json`) se lee en segundo plano."""
from __future__ import annotations

import math
from datetime import datetime

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from gui_comun.diseno import clase, icono_trazo, variante
from gui_comun.widgets.tarjetas import Cifra, ListaConVacio, Tarjeta, encabezado, pagina_desplazable, rejilla_pareja

from lliphi_studio import proyecto

TIPOS = {"construccion": "usa su código", "integra": "lo lleva dentro", "referencia": "nombra su id"}


def leer_todo() -> dict:
    """Lo que se tarda en saber (se llama en segundo plano)."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(3) as ex:   # validar y verificar construyen todo: en paralelo tardan la mitad
        validar = ex.submit(proyecto.correr_json, "generar", "validar")
        verificar = ex.submit(proyecto.correr_json, "generar", "verificar")
        estado = ex.submit(proyecto.correr_json, "instalar", "estado")
        return {"git": proyecto.git(), "versiones": proyecto.versiones(), "validar": validar.result(),
                "verificar": verificar.result(), "estado": estado.result()}


def problemas_de(id_: str, datos: dict, m: proyecto.Modulo) -> tuple[list[str], list[str], list[str]]:
    """(errores de validación, avisos, diferencias de lo generado) que tocan a un módulo."""
    v = datos.get("validar") or {}
    err = [e["texto"] for e in v.get("errores", []) if e["modulo"] == id_]
    av = [e["texto"] for e in v.get("avisos", []) if e["modulo"] == id_]
    dif_todas = (datos.get("verificar") or {}).get("diferencias", [])
    destino = m.datos.get("integracion", {}).get("en") or id_
    dif = [d for d in dif_todas if d.startswith(f"{destino}/")]
    if m.clase == "componente":   # del tema global, solo lo que cae en las rutas del componente
        rutas = m.datos.get("integracion", {}).get("rutas", [])
        dif = [d for d in dif if any(r.split("/")[1] in d for r in rutas)]
    return err, av, dif


class TarjetaModulo(Tarjeta):
    def __init__(self, pagina, m: proyecto.Modulo):
        super().__init__()
        self.pagina, self.m = pagina, m
        cabeza = QHBoxLayout()
        ic = QLabel()
        ic.setPixmap(icono_trazo({"paquete": "paquete", "componente": "capas", "externo": "enlace"}[m.clase]).pixmap(20, 20))
        cabeza.addWidget(ic)
        t = QLabel(m.nombre)
        t.setStyleSheet("font-weight: 600; font-size: 14px;")
        cabeza.addWidget(t, 1)
        self.chip = clase(QLabel(m.datos.get("estado", "")), "tenue")
        cabeza.addWidget(self.chip)
        self.cuerpo.addLayout(cabeza)
        ficha = clase(QLabel(f"<code>{m.id}</code> · {m.clase} · {m.formato} · desde {m.datos.get('desde', '?')}"), "suave")
        ficha.setTextFormat(Qt.RichText)
        ficha.setWordWrap(True)
        self.cuerpo.addWidget(ficha)
        self.estado = clase(QLabel("leyendo…"), "tenue")
        self.estado.setWordWrap(True)
        self.estado.setTextFormat(Qt.RichText)
        self.cuerpo.addWidget(self.estado)
        botones = QHBoxLayout()
        botones.addStretch(1)
        b = QPushButton("Construir (simular)")
        b.clicked.connect(lambda: pagina.v.correr(proyecto.orden("generar", "--modulos", m.id), f"Construir {m.id} (simulación)"))
        botones.addWidget(b)
        if m.id in proyecto.SECCION:
            ab = variante(QPushButton(icono_trazo("abrir"), " Abrir"), "primario")
            ab.clicked.connect(lambda: pagina.v.navigate(proyecto.SECCION[m.id]))
            botones.addWidget(ab)
        self.cuerpo.addLayout(botones)

    def pintar(self, datos: dict) -> None:
        t = self.pagina.v.tokens()
        err, av, dif = problemas_de(self.m.id, datos, self.m)
        instalados = (datos.get("estado") or {}).get("modulos") or []
        herramientas = self.m.herramientas()
        faltan = [h for h, ok in herramientas.items() if not ok]
        ultima = self.m.ultima_construccion()
        def punto(ok: bool, aviso: bool = False) -> str:
            color = t["exito"] if ok else (t["aviso"] if aviso else t["error"])
            return f"<span style='color:{color}'>●</span>"
        lineas = [f"{punto(not err, bool(av) and not err)} validación: " + ("sin errores" if not err else "; ".join(err[:2]))
                  + (f" · {len(av)} aviso(s)" if av else ""),
                  f"{punto(not dif)} generado: " + ("al día" if not dif else f"{len(dif)} diferencia(s)"),
                  f"{punto(self.m.clase != 'paquete' or self.m.id in instalados, True)} instalado: "
                  + ({"componente": "va dentro del tema global", "externo": "terceros (instalar.py dependencias)"}.get(self.m.clase)
                     or ("sí" if self.m.id in instalados else "no"))]
        if herramientas:
            lineas.append(f"{punto(not faltan, True)} herramientas: " + (", ".join(herramientas) if not faltan else "faltan " + ", ".join(faltan)))
        if ultima:
            lineas.append(f"construido el {datetime.fromtimestamp(ultima):%Y-%m-%d %H:%M}")
        if self.m.ajustes.exists():
            lineas.append(f"editable: <code>{self.m.ajustes.relative_to(proyecto.raiz())}</code>")
        self.estado.setText("<br>".join(lineas))


class Grafo(QWidget):
    """Las dependencias entre módulos: el tema global arriba, los seis módulos al medio y los complementos abajo; el
    color de la arista dice su tipo y el borde del nodo, si el módulo está bien."""

    def __init__(self, pagina):
        super().__init__()
        self.pagina = pagina
        self.datos: dict = {}
        self.setMinimumHeight(330)

    def paintEvent(self, _e) -> None:
        t = self.pagina.v.tokens()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        mods = proyecto.modulos()
        filas = [[m for m in mods if m.rol == r] for r in ("global", "modulo", "complemento")]
        w, h = self.width(), self.height()
        ancho_nodo = min(118, (w - 40) / max(len(f) for f in filas) - 10)
        pos: dict[str, QRectF] = {}
        for i, fila in enumerate(filas):
            y = 34 + i * (h - 104) / 2
            paso = (w - 20) / len(fila)
            for j, m in enumerate(fila):
                x = 10 + paso * j + (paso - ancho_nodo) / 2
                pos[m.id] = QRectF(x, y, ancho_nodo, 30)
        colores = {"construccion": QColor(t["info"]), "integra": QColor(t["acento"]), "referencia": QColor(t["texto_tenue"])}
        for de, a, tipo in proyecto.aristas():
            if de not in pos or a not in pos:
                continue
            r1, r2 = pos[de], pos[a]
            c = QColor(colores[tipo])
            c.setAlpha(170)
            p.setPen(QPen(c, 1.6, Qt.SolidLine if tipo != "referencia" else Qt.DashLine))
            p1 = QPointF(r1.center().x(), r1.bottom() if r2.top() > r1.bottom() else (r1.top() if r2.bottom() < r1.top() else r1.center().y()))
            p2 = QPointF(r2.center().x(), r2.top() if r2.top() > r1.bottom() else (r2.bottom() if r2.bottom() < r1.top() else r2.center().y()))
            camino = QPainterPath(p1)
            if abs(p1.y() - p2.y()) < 2:   # en la misma fila: un arco por debajo
                camino.cubicTo(QPointF(p1.x(), p1.y() + 40), QPointF(p2.x(), p2.y() + 40), p2)
            else:
                medio = (p1.y() + p2.y()) / 2
                camino.cubicTo(QPointF(p1.x(), medio), QPointF(p2.x(), medio), p2)
            p.setBrush(Qt.NoBrush)
            p.drawPath(camino)
            ang = math.atan2(p2.y() - camino.pointAtPercent(0.95).y(), p2.x() - camino.pointAtPercent(0.95).x())
            for d in (-0.45, 0.45):
                p.drawLine(p2, QPointF(p2.x() - 7 * math.cos(ang + d), p2.y() - 7 * math.sin(ang + d)))
        f = QFont(self.font())
        f.setPointSizeF(8.5)
        p.setFont(f)
        for m in mods:
            r = pos[m.id]
            err, av, dif = problemas_de(m.id, self.datos, m) if self.datos else ([], [], [])
            borde = QColor(t["error"] if err else (t["aviso"] if (dif or av) else (t["exito"] if self.datos else t["borde_fuerte"])))
            p.setPen(QPen(borde, 1.6))
            p.setBrush(QColor(t["superficie_2"] if m.rol != "modulo" else t["superficie"]))
            p.drawRoundedRect(r, 7, 7)
            p.setPen(QColor(t["texto"] if m.rol == "modulo" else t["texto_suave"]))
            p.drawText(r, Qt.AlignCenter, m.id)
        y = 10
        x = 12
        for tipo, texto in TIPOS.items():
            p.setPen(QPen(colores[tipo], 2, Qt.SolidLine if tipo != "referencia" else Qt.DashLine))
            p.drawLine(QPointF(x, y), QPointF(x + 22, y))
            p.setPen(QColor(t["texto_tenue"]))
            p.drawText(QPointF(x + 28, y + 4), f"{tipo}: {texto}")
            x += p.fontMetrics().horizontalAdvance(f"{tipo}: {texto}") + 56
        p.end()


class Pagina:
    def __init__(self, v):
        self.v = v
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(14)
        cabeza = QHBoxLayout()
        cabeza.addWidget(encabezado("Dashboard", "Los seis módulos de Lliphi, el tema global que los integra y los complementos: "
                                                 "validación, deriva de lo generado, instalación, dependencias y versiones."), 1)
        b = QPushButton(icono_trazo("sincronizar"), " Actualizar")
        b.clicked.connect(self.refrescar)
        cabeza.addWidget(b)
        raiz.addLayout(cabeza)
        cifras = rejilla_pareja(5)
        self.c_version = Cifra("Versión", "—", "")
        self.c_modulos = Cifra("Módulos", "—", "")
        self.c_valida = Cifra("Validación", "—", "")
        self.c_deriva = Cifra("Generado", "—", "")
        self.c_instalado = Cifra("Instalado", "—", "")
        for i, c in enumerate((self.c_version, self.c_modulos, self.c_valida, self.c_deriva, self.c_instalado)):
            cifras.addWidget(c, 0, i)
        raiz.addLayout(cifras)
        rejilla = rejilla_pareja(3)
        self.tarjetas: dict[str, TarjetaModulo] = {}
        seis = [m for m in proyecto.modulos() if m.rol == "modulo"]
        for i, m in enumerate(seis):
            t = TarjetaModulo(self, m)
            self.tarjetas[m.id] = t
            rejilla.addWidget(t, i // 3, i % 3)
        raiz.addLayout(rejilla)
        tg = Tarjeta("Dependencias entre módulos")
        self.grafo = Grafo(self)
        tg.cuerpo.addWidget(self.grafo)
        raiz.addWidget(tg)
        fila = rejilla_pareja(3)
        tr = Tarjeta("Tema global y complementos")
        self.lista_resto = ListaConVacio("—")
        self.lista_resto.setMinimumHeight(230)
        tr.cuerpo.addWidget(self.lista_resto)
        fila.addWidget(tr, 0, 0)
        tv = Tarjeta("Versiones y entorno")
        self.lista_versiones = ListaConVacio("—")
        tv.cuerpo.addWidget(self.lista_versiones)
        fila.addWidget(tv, 0, 1)
        tgit = Tarjeta("Repositorio")
        self.lista_git = ListaConVacio("Sin cambios: el repositorio está al día.")
        tgit.cuerpo.addWidget(self.lista_git)
        fila.addWidget(tgit, 0, 2)
        raiz.addLayout(fila)
        raiz.addStretch(1)
        self.widget = pagina_desplazable(contenido)
        self.datos: dict = {}
        self._leyendo = False
        self.refrescar()

    def refrescar(self) -> None:
        if self._leyendo:
            return
        self._leyendo = True
        self.v.ui.statusbar.showMessage("Leyendo validación, deriva e instalación…", 4000)
        self.v.en_segundo_plano(leer_todo, self._pintar)

    def al_cambiar_proyecto(self) -> None:
        self.refrescar()

    def repintar(self) -> None:
        if self.datos:
            self._pintar(self.datos)

    def _pintar(self, datos: dict) -> None:
        self._leyendo = False
        self.datos = datos
        mods = proyecto.modulos()
        g = datos["git"]
        self.c_version.poner(proyecto.version(), f"última etiqueta {g.etiqueta or '—'}")
        self.c_modulos.poner(str(len(mods)), f"6 módulos · tema global · {sum(m.rol == 'complemento' for m in mods)} complementos")
        v = datos.get("validar")
        if v:
            self.c_valida.poner("válido" if v["valido"] else f"{len(v['errores'])} error(es)", f"{len(v['avisos'])} aviso(s)")
        else:
            self.c_valida.poner("?", "no se pudo validar (¿.venv?)")
        d = datos.get("verificar")
        if d:
            self.c_deriva.poner("al día" if d["al_dia"] else f"{len(d['diferencias'])} dif.", f"{d['archivos']} archivos generados")
        else:
            self.c_deriva.poner("?", "no se pudo verificar")
        e = datos.get("estado") or {}
        if e.get("instalado"):
            mal = sum(not r["ok"] for r in e.get("rutas", []))
            self.c_instalado.poner(e.get("version", "?"), f"el {str(e.get('fecha', ''))[:10]} · {len(e.get('modulos', []))} módulos"
                                   + (f" · {mal} modificado(s)" if mal else ""))
        else:
            self.c_instalado.poner("no", "instalar.py --aplicar (Construir y desplegar)")
        for t in self.tarjetas.values():
            t.pintar(datos)
        self.grafo.datos = datos
        self.grafo.update()
        lista = self.lista_resto.lista
        lista.clear()
        for m in mods:
            if m.rol == "modulo":
                continue
            err, av, dif = problemas_de(m.id, datos, m)
            icono = "quitar" if err else ("info" if dif or av else "verificar")
            texto = f"{m.nombre} ({m.id}) · {m.datos.get('estado', '')}" + (f"\n{len(dif)} diferencia(s) en lo generado" if dif else "") \
                + (f"\n{err[0]}" if err else "")
            lista.addItem(QListWidgetItem(icono_trazo(icono), texto))
        self.lista_resto.actualizar()
        lista = self.lista_versiones.lista
        lista.clear()
        for k, val in datos["versiones"].items():
            lista.addItem(QListWidgetItem(icono_trazo("info"), f"{k}: {val}"))
        lista.addItem(QListWidgetItem(icono_trazo("terminal"), f"Python de las órdenes: {proyecto.python()}"))
        self.lista_versiones.actualizar()
        lista = self.lista_git.lista
        lista.clear()
        lista.addItem(QListWidgetItem(icono_trazo("enlace"), f"rama {g.rama} · {g.adelante} commit(s) sin subir"
                                      + (f" · {g.atras} por bajar" if g.atras else "")))
        for c in g.cambios[:40]:
            lista.addItem(QListWidgetItem(icono_trazo("texto"), c))
        if len(g.cambios) > 40:
            lista.addItem(QListWidgetItem(icono_trazo("mas"), f"y {len(g.cambios) - 40} más"))
        self.lista_git.actualizar()
