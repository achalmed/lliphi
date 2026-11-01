"""Vista en vivo: la sesión de prueba de Lliphi (`herramientas/sesion.py`), un Plasma anidado con su propio HOME donde se
instala y se aplica el tema sin tocar tu escritorio.

Arrancar (en una ventana o virtual), recargar lo que cambió (reinstala y vuelve a aplicar, todo o unos módulos),
cambiar de variante, abrir aplicaciones dentro, capturar (la captura se ve aquí y puede guardarse en
`muestras/capturas/`) y cerrar. El estado se lee de `sesion.py estado --json`, con el `LockedHint` de tu sesión real.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                               QPushButton, QSpinBox, QVBoxLayout, QWidget)

from gui_comun.diseno import clase, icono_trazo, variante

from lliphi_studio import proyecto
from lliphi_studio.comun import envolver, Editor, Lienzo, nota

APLICACIONES = (("Dolphin", "dolphin"), ("Konsole", "konsole"), ("Preferencias del sistema", "systemsettings"),
                ("Kate", "kate"), ("Spectacle", "spectacle"), ("Bienvenida de Plasma", "plasma-welcome"))


class LienzoCaptura(Lienzo):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.imagen: QPixmap | None = None
        self.mensaje = "Sin sesión de prueba. Arráncala con el botón de la derecha."

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        if self.imagen is None or self.imagen.isNull():
            p.setPen(QColor(self.tokens()["texto_tenue"]))
            p.drawText(rect.adjusted(20, 20, -20, -20), Qt.AlignCenter | Qt.TextWordWrap, self.mensaje)
            return
        k = min((rect.width() - 20) / self.imagen.width(), (rect.height() - 20) / self.imagen.height()) * self.zoom
        w, h = self.imagen.width() * k, self.imagen.height() * k
        p.drawPixmap(QRectF(rect.center().x() - w / 2, rect.center().y() - h / 2, w, h), self.imagen, QRectF(self.imagen.rect()))


class Pagina:
    def __init__(self, v):
        self.v = v
        self.estado: dict = {}
        self.ultima: Path | None = None
        # biblioteca: aplicaciones y acciones dentro
        bib = QWidget()
        bv = QVBoxLayout(bib)
        bv.setContentsMargins(0, 0, 0, 0)
        bv.addWidget(clase(QLabel("Abrir dentro"), "suave"))
        for nombre, orden in APLICACIONES:
            b = QPushButton(icono_trazo("abrir"), f" {nombre}")
            b.setStyleSheet("text-align: left;")
            b.clicked.connect(lambda _=False, o=orden: self._abrir(o))
            bv.addWidget(b)
        bv.addSpacing(10)
        bv.addWidget(clase(QLabel("Otra orden"), "suave"))
        self.otra = QLineEdit()
        self.otra.setPlaceholderText("p. ej. kcmshell6 kcm_colors")
        self.otra.returnPressed.connect(lambda: self.otra.text().strip() and self._abrir(*self.otra.text().split()))
        bv.addWidget(self.otra)
        bv.addSpacing(10)
        bv.addWidget(nota("Todo lo que se abre aquí corre con el entorno del <code>plasmashell</code> de prueba; "
                          "<code>sesion.py</code> se niega si su HOME no es el de prueba."))
        bv.addStretch(1)
        self.lienzo = LienzoCaptura(v.tokens)
        # propiedades: estado y control
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.lbl_estado = QLabel("—")
        self.lbl_estado.setStyleSheet("font-weight: 600; font-size: 14px;")
        pv.addWidget(self.lbl_estado)
        self.detalle = nota("")
        pv.addWidget(self.detalle)
        form = QFormLayout()
        self.variante = QComboBox()
        self.variante.addItem("Lliphi Oscuro", "oscuro")
        self.variante.addItem("Lliphi Claro", "claro")
        form.addRow("variante", self.variante)
        self.disposicion = QCheckBox("aplicar también la disposición")
        form.addRow("", self.disposicion)
        self.virtual = QCheckBox("virtual (sin ventana; solo capturas)")
        form.addRow("", self.virtual)
        tam = QHBoxLayout()
        self.ancho, self.alto = QSpinBox(), QSpinBox()
        for s, x in ((self.ancho, 1600), (self.alto, 900)):
            s.setRange(640, 3840)
            s.setValue(x)
            tam.addWidget(s)
        form.addRow("ventana", tam)
        self.modulos = QComboBox()
        self.modulos.addItem("todo", "")
        for m in proyecto.modulos():
            self.modulos.addItem(m.id, m.id)
        form.addRow("recargar", self.modulos)
        pv.addLayout(form)
        self.b_arrancar = variante(QPushButton(icono_trazo("jugar"), " Arrancar"), "primario")
        self.b_arrancar.clicked.connect(self._arrancar)
        self.b_recargar = QPushButton(icono_trazo("sincronizar"), " Recargar y aplicar")
        self.b_recargar.clicked.connect(self._recargar)
        self.b_capturar = QPushButton(icono_trazo("imagen"), " Capturar")
        self.b_capturar.clicked.connect(lambda: self.capturar(mostrar=True))
        self.b_guardar = QPushButton(icono_trazo("descarga"), " Guardar captura en muestras…")
        self.b_guardar.clicked.connect(self._guardar_captura)
        self.b_cerrar = variante(QPushButton(icono_trazo("quitar"), " Cerrar la sesión de prueba"), "peligro")
        self.b_cerrar.clicked.connect(self._cerrar)
        for b in (self.b_arrancar, self.b_recargar, self.b_capturar, self.b_guardar, self.b_cerrar):
            pv.addWidget(b)
        self.auto = QCheckBox("capturar tras cada recarga")
        self.auto.setChecked(True)
        pv.addWidget(self.auto)
        pv.addStretch(1)
        props = envolver(props)
        self.editor = Editor("Vista en vivo", "Un Plasma de verdad, anidado y con su propio HOME, donde se instala y se aplica "
                             "Lliphi sin tocar tu escritorio (herramientas/sesion.py).", bib, self.lienzo, props, v.tokens)
        self.editor.boton("Simular arranque", "terminal", lambda: v.correr(proyecto.orden("sesion", "arrancar", *self._args()),
                                                                            "Sesión de prueba (simulación)"))
        self.editor.pestanas.setTabText(0, "Registro de la sesión")
        self.editor.pestanas.setTabText(1, "Estado (JSON)")
        self.widget = self.editor
        self.reloj = QTimer()
        self.reloj.setInterval(5000)
        self.reloj.timeout.connect(self.refrescar)
        self.reloj.start()
        self._leyendo = False
        self.refrescar()

    # ----------------------------------------------------------------
    def _args(self) -> list[str]:
        a = ["--variante", self.variante.currentData(), "--ancho", str(self.ancho.value()), "--alto", str(self.alto.value())]
        return a + (["--disposicion"] if self.disposicion.isChecked() else []) + (["--virtual"] if self.virtual.isChecked() else [])

    def refrescar(self) -> None:
        if self._leyendo or not self.widget.isVisible() and self.estado:
            return
        self._leyendo = True
        self.v.en_segundo_plano(lambda: proyecto.correr_json("sesion", "estado") or {}, self._pintar)

    def _pintar(self, e: dict) -> None:
        self._leyendo = False
        self.estado = e or {}
        activa = bool(self.estado.get("activa"))
        self.lbl_estado.setText("Sesión de prueba activa" if activa else "Sin sesión de prueba")
        if activa:
            self.detalle.setText(f"variante <b>{self.estado.get('variante')}</b> · {self.estado.get('ancho')}×{self.estado.get('alto')}"
                                 f"{' · virtual' if self.estado.get('virtual') else ' · en una ventana'}<br>desde {self.estado.get('inicio')}"
                                 f"<br>HOME <code>{str(self.estado.get('casa', '')).replace(str(proyecto.home()), '~')}</code>"
                                 f"<br>plasmashell {self.estado.get('plasmashell')} · LockedHint de tu sesión: "
                                 f"<b>{self.estado.get('locked_hint')}</b>")
        else:
            self.detalle.setText("Arrancar crea un HOME aparte en la caché, instala Lliphi dentro, arranca un Plasma anidado "
                                 f"y aplica la variante. Tu sesión no cambia (LockedHint: <b>{self.estado.get('locked_hint')}</b>).")
            if self.lienzo.imagen is None:
                self.lienzo.mensaje = "Sin sesión de prueba. Arráncala con el botón de la derecha."
        for b in (self.b_recargar, self.b_capturar, self.b_cerrar):
            b.setEnabled(activa)
        self.b_arrancar.setEnabled(not activa)
        import json
        self.editor.diff.setPlainText(json.dumps(self.estado, ensure_ascii=False, indent=2))
        log = Path(self.estado.get("casa", "")).parent / "sesion.log" if self.estado.get("casa") else None
        if log and log.exists():
            self.editor.codigo.setPlainText("\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-300:]))
        self.lienzo.update()

    def al_mostrar(self) -> None:
        self.refrescar()

    def _arrancar(self) -> None:
        if not self.v.confirmar("Arrancar la sesión de prueba",
                                "Crea un HOME aparte en ~/.cache/lliphi/sesiones/, instala Lliphi dentro y arranca un Plasma "
                                "anidado " + ("virtual (sin ventana)" if self.virtual.isChecked() else "en una ventana")
                                + " con la variante elegida. Tarda unos 20 segundos. Tu escritorio no cambia.\n\n¿Arrancar?"):
            return
        self.lienzo.mensaje = "Arrancando la sesión de prueba…"
        self.lienzo.update()
        self.v.correr(proyecto.orden("sesion", "arrancar", *self._args(), "--aplicar"), "Sesión de prueba",
                      lambda c: (self.refrescar(), c == 0 and QTimer.singleShot(3000, lambda: self.capturar(mostrar=True))))

    def _recargar(self) -> None:
        args = ["--variante", self.variante.currentData()]
        if self.modulos.currentData():
            args += ["--modulos", self.modulos.currentData()]
        if self.disposicion.isChecked():
            args.append("--disposicion")
        self.v.correr(proyecto.orden("sesion", "recargar", *args), "Recargar la sesión de prueba",
                      lambda c: c == 0 and self.auto.isChecked() and QTimer.singleShot(2500, lambda: self.capturar(mostrar=True)))

    def _abrir(self, *orden: str) -> None:
        if not self.estado.get("activa"):
            self.v.marco.avisar("Sin sesión de prueba", "Arráncala primero.", "aviso")
            return
        self.v.correr(proyecto.orden("sesion", "ejecutar", "--", *orden), f"Abrir {orden[0]} en la sesión de prueba")

    def capturar(self, mostrar: bool = False) -> None:
        def listo(codigo: int) -> None:
            casa = self.estado.get("casa")
            carpeta = Path(casa).parent / "capturas" if casa else None
            capturas = sorted(carpeta.glob("*.png"), key=lambda p: p.stat().st_mtime) if carpeta and carpeta.is_dir() else []
            if codigo == 0 and capturas:
                self.ultima = capturas[-1]
                self.lienzo.imagen = QPixmap(str(self.ultima))
                self.lienzo.update()
                if mostrar:
                    self.v.navigate("vivo")
        self.v.correr(proyecto.orden("sesion", "capturar"), "Capturar la sesión de prueba", listo)

    def _guardar_captura(self) -> None:
        if not self.ultima or not self.ultima.exists():
            self.v.marco.avisar("Sin captura", "Captura primero.", "aviso")
            return
        var = self.estado.get("variante", "oscuro")
        n = len(list((proyecto.raiz() / "muestras" / "capturas").glob(f"{var}-*.png"))) + 1
        nombre, ok = QInputDialog.getText(self.v.ui, "Guardar captura", "Nombre en muestras/capturas/ (variante-NN-caso.png):",
                                          text=f"{var}-{n:02d}-studio.png")
        if ok and nombre.strip():
            destino = proyecto.raiz() / "muestras" / "capturas" / Path(nombre.strip()).name
            if destino.exists() and not self.v.confirmar("Ya existe", f"{destino.name} ya existe. ¿Reemplazarla?"):
                return
            shutil.copy2(self.ultima, destino)
            self.v.marco.avisar("Captura guardada", str(destino.relative_to(proyecto.raiz())), "ok")

    def _cerrar(self) -> None:
        if self.v.confirmar("Cerrar la sesión de prueba", "Termina solo los procesos cuyo HOME es el de prueba y comprueba el "
                            "LockedHint de tu sesión. El HOME de prueba se conserva en la caché. ¿Cerrar?"):
            self.v.correr(proyecto.orden("sesion", "cerrar"), "Cerrar la sesión de prueba", lambda _c: self.refrescar())

    def repintar(self) -> None:
        self.lienzo.update()
