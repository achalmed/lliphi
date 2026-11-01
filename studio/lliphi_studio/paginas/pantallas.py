"""Splash Studio: las pantallas de carga, de salida, de bloqueo y de inicio de sesión (módulo `carga-bloqueo` y
complemento `sddm`).

La pantalla de carga de Lliphi solo usa QtQuick, así que se ve **de verdad** dentro de la ventana (un `QQuickWidget`
carga su `Splash.qml` con su animación). La salida, el bloqueo y SDDM usan módulos de KDE que no carga el Qt de esta
ventana: se ven en una maqueta con sus imágenes reales y, de verdad, con la herramienta de KDE que les toca:
`ksplashqml --test --window` (no toca la configuración), `sddm-greeter-qt6 --test-mode`, y la salida y el bloqueo solo
dentro de la sesión de prueba (`ksmserver-logout-greeter`, `kscreenlocker_greet --testing`), nunca en la tuya.
"""
from __future__ import annotations

import difflib
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QProcess, QRectF, Qt, QUrl
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from gui_comun.diseno import clase, icono_trazo, variante

from lliphi_studio import proyecto
from lliphi_studio.comun import Editor, Lienzo, nota

LIBEXEC = (Path("/usr/lib/x86_64-linux-gnu/libexec"), Path("/usr/libexec"), Path("/usr/lib/libexec"))
CASOS = (("carga", "Pantalla de carga"), ("salida", "Pantalla de salida"), ("bloqueo", "Bloqueo de pantalla"),
         ("sddm", "Inicio de sesión (SDDM)"))
CAPTURAS = {"carga": ("carga", "pantallas"), "salida": ("salida", "pantallas"), "bloqueo": ("bloqueo",),
            "sddm": ("inicio-de-sesion", "sddm")}


def libexec(nombre: str) -> str | None:
    return next((str(d / nombre) for d in LIBEXEC if (d / nombre).exists()), shutil.which(nombre))


def tema_global(var: str) -> Path:
    return proyecto.raiz() / "generado" / "global" / proyecto.marca()["id_global"][var]


class Maqueta(Lienzo):
    """La salida, el bloqueo y SDDM con sus imágenes reales (la carga se ve de verdad en el QML)."""

    def __init__(self, tokens):
        super().__init__(tokens)
        self.caso, self.var = "salida", "oscuro"
        self.tablero = False
        self._img: dict[str, QPixmap] = {}

    def imagen(self, ruta: Path | None) -> QPixmap | None:
        if not ruta or not ruta.exists():
            return None
        if str(ruta) not in self._img:
            self._img[str(ruta)] = QPixmap(str(ruta)).scaledToWidth(1280, Qt.SmoothTransformation)
        return self._img[str(ruta)]

    def pintar(self, p: QPainter, rect: QRectF) -> None:
        pantalla = self._pantalla(rect)
        if self.caso == "salida":
            fondo = self.imagen(tema_global(self.var) / "contents" / "logout" / "background.png")
        elif self.caso == "bloqueo":
            fondo = self.imagen(proyecto.fondo("oscuro"))   # el bloqueo usa la imagen oscura en las dos variantes (decisiones 4.16)
        else:
            fondo = self.imagen(proyecto.raiz() / "generado" / "sddm" / "lliphi" / "background.png")
        if fondo:
            p.drawPixmap(pantalla, fondo, QRectF(fondo.rect()))
        else:
            p.fillRect(pantalla, QColor("#111216"))
        k = pantalla.width() / 1280
        f = QFont("Inter")
        blanco = QColor("#eaebed")
        acento = QColor(proyecto.tokens()["semanticos"]["oscuro"]["acento"]["base"]["$value"]["hex"])
        if self.caso == "salida":
            p.fillRect(pantalla, QColor(0, 0, 0, 90))
            for i, texto in enumerate(("Dormir", "Reiniciar", "Apagar", "Cerrar sesión")):
                cx = pantalla.center().x() + (i - 1.5) * 150 * k
                r = 46 * k
                p.setPen(Qt.NoPen)
                p.setBrush(QColor(255, 255, 255, 40) if i != 2 else acento)
                p.drawEllipse(QRectF(cx - r, pantalla.center().y() - r, 2 * r, 2 * r))
                f.setPixelSize(int(15 * k))
                p.setFont(f)
                p.setPen(blanco)
                p.drawText(QRectF(cx - 80 * k, pantalla.center().y() + r + 10 * k, 160 * k, 24 * k), Qt.AlignCenter, texto)
            f.setPixelSize(int(17 * k))
            p.setFont(f)
            p.drawText(QRectF(pantalla.x(), pantalla.y() + pantalla.height() * 0.22, pantalla.width(), 30 * k), Qt.AlignCenter,
                       "Apagando en 30 segundos")
        elif self.caso == "bloqueo":
            ahora = datetime.now()
            f.setPixelSize(int(96 * k))
            f.setWeight(QFont.Light)
            p.setFont(f)
            p.setPen(blanco)
            p.drawText(QRectF(pantalla.x(), pantalla.y() + pantalla.height() * 0.22, pantalla.width(), 120 * k), Qt.AlignCenter, f"{ahora:%H:%M}")
            f.setPixelSize(int(20 * k))
            f.setWeight(QFont.Normal)
            p.setFont(f)
            p.drawText(QRectF(pantalla.x(), pantalla.y() + pantalla.height() * 0.22 + 120 * k, pantalla.width(), 30 * k),
                       Qt.AlignCenter, ahora.strftime("%A, %d de %B").capitalize())
            campo = QRectF(pantalla.center().x() - 150 * k, pantalla.y() + pantalla.height() * 0.62, 300 * k, 40 * k)
            p.setBrush(QColor(255, 255, 255, 30))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(campo, 8 * k, 8 * k)
            p.setPen(QColor(255, 255, 255, 150))
            f.setPixelSize(int(15 * k))
            p.setFont(f)
            p.drawText(campo.adjusted(14 * k, 0, 0, 0), Qt.AlignVCenter, "Contraseña")
        p.setPen(QColor(self.tokens()["texto_tenue"]))
        f = QFont(self.font())
        f.setPointSizeF(8)
        p.setFont(f)
        p.drawText(QRectF(pantalla.x(), pantalla.bottom() + 4, pantalla.width(), 16), Qt.AlignRight,
                   "maqueta con las imágenes reales; la de verdad, con el botón de la derecha")

    def _pantalla(self, rect: QRectF) -> QRectF:
        w = min(rect.width() - 20, (rect.height() - 34) * 16 / 9)
        h = w * 9 / 16
        return QRectF(rect.center().x() - w / 2, 10, w, h)


class Pagina:
    def __init__(self, v):
        self.v = v
        self.caso, self.var = "carga", "oscuro"
        self.lista = QListWidget()
        for var in ("oscuro", "claro"):
            for caso, nombre in CASOS:
                if caso == "sddm" and var == "claro":
                    continue
                it = QListWidgetItem(icono_trazo({"carga": "cargando", "salida": "quitar", "bloqueo": "candado",
                                                  "sddm": "usuario"}[caso]),
                                     nombre + ("" if caso == "sddm" else f" · {var}"))
                it.setData(Qt.UserRole, (caso, var))
                self.lista.addItem(it)
        self.lista.currentItemChanged.connect(self._elegir)
        self.pila = QStackedWidget()
        self.qml_caja = QWidget()
        QVBoxLayout(self.qml_caja).setContentsMargins(0, 0, 0, 0)
        self.qml = None
        self.pila.addWidget(self.qml_caja)
        self.maqueta = Maqueta(v.tokens)
        self.pila.addWidget(self.maqueta)
        props = QWidget()
        pv = QVBoxLayout(props)
        pv.setContentsMargins(4, 4, 4, 4)
        self.titulo = QLabel("—")
        self.titulo.setStyleSheet("font-weight: 600; font-size: 14px;")
        pv.addWidget(self.titulo)
        self.info = nota("")
        pv.addWidget(self.info)
        self.b_real = variante(QPushButton(icono_trazo("jugar"), " Ver de verdad"), "primario")
        self.b_real.clicked.connect(self._de_verdad)
        pv.addWidget(self.b_real)
        self.b_reiniciar = QPushButton(icono_trazo("sincronizar"), " Repetir la animación")
        self.b_reiniciar.clicked.connect(self._cargar_qml)
        pv.addWidget(self.b_reiniciar)
        pv.addWidget(clase(QLabel("Archivos"), "suave"))
        self.archivos = QListWidget()
        self.archivos.currentItemChanged.connect(self._archivo)
        pv.addWidget(self.archivos, 1)
        pv.addWidget(clase(QLabel("Capturas reales (muestras/capturas)"), "suave"))
        self.capturas = QListWidget()
        self.capturas.setMaximumHeight(110)
        self.capturas.itemDoubleClicked.connect(lambda it: self._ver_captura(Path(it.data(Qt.UserRole))))
        pv.addWidget(self.capturas)
        self.editor = Editor("Pantallas", "Carga, salida, bloqueo e inicio de sesión de Lliphi: la carga, de verdad en su "
                             "QML; las demás, con sus imágenes reales y con la herramienta de KDE que las muestra.",
                             self.lista, self.pila, props, v.tokens)
        self.editor.pestanas.setTabText(0, "QML")
        self.editor.pestanas.setTabText(1, "Diff contra WhiteSur")
        self.widget = self.editor
        self.lista.setCurrentRow(0)

    # ----------------------------------------------------------------
    def _elegir(self, it, _prev=None) -> None:
        if not it:
            return
        self.caso, self.var = it.data(Qt.UserRole)
        nombre = dict(CASOS)[self.caso]
        self.titulo.setText(nombre + ("" if self.caso == "sddm" else f" · Lliphi {self.var.capitalize()}"))
        carpeta = self._carpeta()
        self.archivos.clear()
        for f in sorted(carpeta.rglob("*")) if carpeta and carpeta.exists() else []:
            if f.is_file() and f.suffix in (".qml", ".js", ".png", ".svg", ".conf", ".desktop", ".jpg"):
                ic = icono_trazo("imagen" if f.suffix in (".png", ".svg", ".jpg") else "codigo")
                x = QListWidgetItem(ic, str(f.relative_to(carpeta)))
                x.setData(Qt.UserRole, str(f))
                self.archivos.addItem(x)
        textos = {
            "carga": ("La carga que ve Plasma al iniciar sesión: <code>contents/splash/Splash.qml</code> del tema global "
                      "(derivada de WhiteSur-dark). «Ver de verdad» la abre con <code>ksplashqml --test --window</code>."),
            "salida": ("El diálogo de salida, <code>contents/logout/</code> del tema global. Usa módulos de KDE: de verdad "
                       "solo en la sesión de prueba (<code>ksmserver-logout-greeter</code>)."),
            "bloqueo": ("En Plasma 6.6 el bloqueo es del paquete de shell; Lliphi pone su fondo (la imagen oscura en las dos "
                        "variantes). De verdad solo en la sesión de prueba (<code>kscreenlocker_greet --testing</code>): "
                        "nunca se bloquea tu sesión."),
            "sddm": ("El inicio de sesión es SDDM (complemento <code>sddm</code>), fuera de tu sesión; «Ver de verdad» usa "
                     "<code>sddm-greeter-qt6 --test-mode</code> en una ventana."),
        }
        self.info.setText(textos[self.caso])
        self.capturas.clear()
        for c in sorted((proyecto.raiz() / "muestras" / "capturas").glob("*.png")) + sorted((proyecto.raiz() / "muestras").glob("*.png")):
            if any(k in c.name for k in CAPTURAS[self.caso]):
                x = QListWidgetItem(icono_trazo("imagen"), c.name)
                x.setData(Qt.UserRole, str(c))
                self.capturas.addItem(x)
        self.b_reiniciar.setVisible(self.caso == "carga")
        if self.caso == "carga":
            self.pila.setCurrentWidget(self.qml_caja)
            self._cargar_qml()
            principal = carpeta / "Splash.qml"
        else:
            self.pila.setCurrentWidget(self.maqueta)
            self.maqueta.caso, self.maqueta.var = self.caso, self.var
            self.maqueta.update()
            principal = carpeta / ("Logout.qml" if self.caso == "salida" else "Main.qml") if carpeta else None
        self._mostrar_qml(principal)

    def _carpeta(self) -> Path | None:
        if self.caso == "carga":
            return tema_global(self.var) / "contents" / "splash"
        if self.caso == "salida":
            return tema_global(self.var) / "contents" / "logout"
        if self.caso == "sddm":
            return proyecto.raiz() / "generado" / "sddm" / "lliphi"
        return proyecto.raiz() / "modulos" / "carga-bloqueo"

    def _cargar_qml(self) -> None:
        """La pantalla de carga de verdad: su QML en un QQuickWidget, con `stage` = 1 para que arranque la animación."""
        from PySide6.QtQuickWidgets import QQuickWidget
        lay = self.qml_caja.layout()
        if self.qml is not None:
            lay.removeWidget(self.qml)
            self.qml.deleteLater()
        self.qml = QQuickWidget()
        self.qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.qml.setClearColor(QColor("#000000"))
        self.qml.setSource(QUrl.fromLocalFile(str(tema_global(self.var) / "contents" / "splash" / "Splash.qml")))
        lay.addWidget(self.qml)
        raiz = self.qml.rootObject()
        if raiz is not None:
            raiz.setProperty("stage", 1)
        errores = [e.toString() for e in self.qml.errors()]
        if errores:
            self.v.marco.avisar("El QML de la carga no cargó", "\n".join(errores[:3]), "error")

    def _mostrar_qml(self, ruta: Path | None) -> None:
        if ruta and ruta.exists():
            self.editor.codigo.setPlainText(ruta.read_text(encoding="utf-8", errors="replace"))
            base = self._base_de(ruta)
            if base and base.exists():
                diff = "".join(difflib.unified_diff(base.read_text(encoding="utf-8", errors="replace").splitlines(True),
                                                    ruta.read_text(encoding="utf-8", errors="replace").splitlines(True),
                                                    f"WhiteSur/{base.name}", f"lliphi/{ruta.name}"))
                self.editor.diff.setPlainText(diff or "Idéntico a la base.")
            else:
                self.editor.diff.setPlainText("Sin base de WhiteSur con la que comparar.")
        else:
            aplicar = proyecto.raiz() / "modulos" / "carga-bloqueo" / "aplicar.py"
            self.editor.codigo.setPlainText(aplicar.read_text(encoding="utf-8") if aplicar.exists() else "")
            self.editor.diff.setPlainText("El bloqueo no tiene QML propio en Plasma 6.6: Lliphi solo pone su fondo.")

    def _base_de(self, ruta: Path) -> Path | None:
        base = proyecto.raiz() / "fuentes" / "base" / "WhiteSur-kde"
        if self.caso == "carga":
            return base / "plasma" / "look-and-feel" / "com.github.vinceliuice.WhiteSur-dark" / "contents" / "splash" / ruta.name
        if self.caso == "salida":
            return base / "plasma" / "look-and-feel" / "com.github.vinceliuice.WhiteSur-dark" / "contents" / "logout" / ruta.name
        if self.caso == "sddm":
            return base / "sddm" / "WhiteSur-dark" / ruta.name
        return None

    def _archivo(self, it, _prev=None) -> None:
        if not it:
            return
        ruta = Path(it.data(Qt.UserRole))
        if ruta.suffix in (".qml", ".js", ".conf", ".desktop"):
            self._mostrar_qml(ruta)
        elif ruta.suffix in (".png", ".jpg", ".svg"):
            self._ver_captura(ruta)

    def _ver_captura(self, ruta: Path) -> None:
        from PySide6.QtWidgets import QDialog
        d = QDialog(self.v.ui)
        d.setWindowTitle(ruta.name)
        lay = QVBoxLayout(d)
        l = QLabel()
        l.setPixmap(QPixmap(str(ruta)).scaled(1100, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lay.addWidget(l)
        d.exec()

    def _de_verdad(self) -> None:
        if self.caso == "carga":
            if not shutil.which("ksplashqml"):
                self.v.marco.avisar("Falta ksplashqml", "Es de plasma-workspace.", "error")
                return
            QProcess.startDetached("ksplashqml", ["--test", "--window", str(tema_global(self.var))])
            self.v.marco.avisar("ksplashqml --test --window", "Se cierra sola; no cambia tu configuración.", "info")
            return
        if self.caso == "sddm":
            if not shutil.which("sddm-greeter-qt6"):
                self.v.marco.avisar("Falta sddm-greeter-qt6", "Es del paquete sddm.", "error")
                return
            QProcess.startDetached("sddm-greeter-qt6", ["--test-mode", "--theme", str(proyecto.raiz() / "generado" / "sddm" / "lliphi")])
            return
        estado = proyecto.correr_json("sesion", "estado") or {}
        if not estado.get("activa"):
            self.v.marco.avisar("Sin sesión de prueba", "La salida y el bloqueo solo se muestran dentro de la sesión de "
                                "prueba: arráncala en la Vista en vivo.", "aviso")
            self.v.navigate("vivo")
            return
        if estado.get("variante") != self.var:
            self.v.marco.avisar("Otra variante", f"La sesión de prueba tiene aplicada la variante {estado.get('variante')}.", "aviso")
        programa = libexec("ksmserver-logout-greeter" if self.caso == "salida" else "kscreenlocker_greet")
        if not programa:
            self.v.marco.avisar("Falta el programa de KDE", "No se encontró en libexec.", "error")
            return
        extra = ["--testing"] if self.caso == "bloqueo" else []
        self.v.correr(proyecto.orden("sesion", "ejecutar", "--", programa, *extra), f"{dict(CASOS)[self.caso]} en la sesión de prueba")

    def repintar(self) -> None:
        self.maqueta.update()
