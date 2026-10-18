#!/usr/bin/env python3
"""Lámina de muestras: widgets reales de Qt con el estilo Breeze y un esquema de color generado.

Renderiza sin pantalla (`QT_QPA_PLATFORM=offscreen`) una galería de widgets (menú, barra de
herramientas, botones, campos, listas con selección, pestañas, deslizador, progreso, texto,
estados deshabilitados) con el esquema `.colors` indicado, y guarda un PNG. Para que Breeze lea
el esquema se crea un `kdeglobals` temporal con su contenido y se apunta `XDG_CONFIG_HOME` a él.

Uso:  /usr/bin/python3 herramientas/lamina.py generado/color-schemes/LliphiClaro.colors muestras/claro.png
Requiere el PyQt6 del sistema (construido contra el Qt del sistema, como el plugin Breeze).
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def preparar_entorno(esquema: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="lamina-"))
    texto = esquema.read_text(encoding="utf-8")
    nombre = next(l.split("=", 1)[1] for l in texto.splitlines() if l.startswith("ColorScheme="))
    # kdeglobals = el esquema entero (sus grupos [Colors:*]) + la selección del esquema
    (tmp / "kdeglobals").write_text(texto + f"\n[General]\nColorScheme={nombre}\n\n[KDE]\nwidgetStyle=Breeze\n", encoding="utf-8")
    (tmp / "kdeglobals").chmod(0o600)
    os.environ["XDG_CONFIG_HOME"] = str(tmp)
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("QT_SCALE_FACTOR", "2")
    return tmp


def paleta_desde_esquema(esquema: Path):
    """QPalette con los grupos del esquema: fuera de una sesión de Plasma no hay plugin de plataforma
    que la construya, así que se hace aquí lo que hace plasma-integration."""
    from PyQt6 import QtGui
    import configparser
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    cp.optionxform = str
    cp.read(esquema, encoding="utf-8")

    def c(grupo, clave):
        r, g, b = (int(x) for x in cp[grupo][clave].split(","))
        return QtGui.QColor(r, g, b)

    R = QtGui.QPalette.ColorRole
    G = QtGui.QPalette.ColorGroup
    pal = QtGui.QPalette()
    roles = {
        R.Window: ("Colors:Window", "BackgroundNormal"), R.WindowText: ("Colors:Window", "ForegroundNormal"),
        R.Base: ("Colors:View", "BackgroundNormal"), R.AlternateBase: ("Colors:View", "BackgroundAlternate"),
        R.Text: ("Colors:View", "ForegroundNormal"), R.Button: ("Colors:Button", "BackgroundNormal"),
        R.ButtonText: ("Colors:Button", "ForegroundNormal"), R.Highlight: ("Colors:Selection", "BackgroundNormal"),
        R.HighlightedText: ("Colors:Selection", "ForegroundNormal"), R.ToolTipBase: ("Colors:Tooltip", "BackgroundNormal"),
        R.ToolTipText: ("Colors:Tooltip", "ForegroundNormal"), R.Link: ("Colors:Window", "ForegroundLink"),
        R.LinkVisited: ("Colors:Window", "ForegroundVisited"), R.PlaceholderText: ("Colors:View", "ForegroundInactive"),
        R.Mid: ("Colors:Window", "ForegroundInactive"), R.Dark: ("Colors:Window", "ForegroundInactive"),
        R.Light: ("Colors:Window", "BackgroundAlternate"), R.Midlight: ("Colors:Window", "BackgroundAlternate"),
        R.Shadow: ("Colors:Window", "ForegroundNormal"), R.BrightText: ("Colors:Selection", "ForegroundNormal"),
    }
    for rol, (grupo, clave) in roles.items():
        for g in (G.Active, G.Inactive, G.Disabled):
            pal.setColor(g, rol, c(grupo, clave))
    inactivo = c("Colors:Window", "ForegroundInactive")
    for rol in (R.WindowText, R.Text, R.ButtonText, R.HighlightedText):
        pal.setColor(G.Disabled, rol, inactivo)
    pal.setColor(G.Disabled, R.Highlight, c("Colors:Window", "BackgroundAlternate"))
    return pal


def galeria(titulo: str):
    from PyQt6 import QtCore, QtGui, QtWidgets as W

    ventana = W.QMainWindow()
    ventana.setWindowTitle(titulo)
    menu = ventana.menuBar()
    for m in ("Archivo", "Editar", "Ver", "Ayuda"):
        menu.addMenu(m)
    barra = ventana.addToolBar("Principal")
    for icono, texto in (("document-new", "Nuevo"), ("document-open", "Abrir"), ("document-save", "Guardar")):
        barra.addAction(QtGui.QIcon.fromTheme(icono), texto)
    barra.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    central = W.QWidget()
    ventana.setCentralWidget(central)
    rejilla = W.QGridLayout(central)
    rejilla.setContentsMargins(16, 12, 16, 12)
    rejilla.setHorizontalSpacing(16)

    # columna 1: controles
    caja = W.QGroupBox("Controles")
    f = W.QFormLayout(caja)
    fila = W.QHBoxLayout()
    b1 = W.QPushButton("Aceptar"); b1.setDefault(True)
    b2 = W.QPushButton("Cancelar")
    b3 = W.QPushButton("Deshabilitado"); b3.setEnabled(False)
    b4 = W.QPushButton("Activado"); b4.setCheckable(True); b4.setChecked(True)
    for b in (b1, b2, b3, b4):
        fila.addWidget(b)
    f.addRow("Botones", fila)
    campo = W.QLineEdit("Texto con foco"); campo.setFocus()
    f.addRow("Campo", campo)
    campo2 = W.QLineEdit(); campo2.setPlaceholderText("Marcador de posición")
    f.addRow("Campo vacío", campo2)
    combo = W.QComboBox(); combo.addItems(["Opción uno", "Opción dos"])
    f.addRow("Lista desplegable", combo)
    casillas = W.QHBoxLayout()
    c1 = W.QCheckBox("Marcada"); c1.setChecked(True)
    c2 = W.QCheckBox("Sin marcar")
    c3 = W.QCheckBox("Inactiva"); c3.setChecked(True); c3.setEnabled(False)
    r1 = W.QRadioButton("Radio"); r1.setChecked(True)
    for c in (c1, c2, c3, r1):
        casillas.addWidget(c)
    f.addRow("Casillas", casillas)
    desl = W.QSlider(QtCore.Qt.Orientation.Horizontal); desl.setValue(60)
    f.addRow("Deslizador", desl)
    prog = W.QProgressBar(); prog.setValue(45)
    f.addRow("Progreso", prog)
    spin = W.QSpinBox(); spin.setValue(12)
    f.addRow("Número", spin)
    enlace = W.QLabel('Texto normal, <a href="#">un enlace</a> y <span style="color: palette(mid)">texto secundario</span>.')
    enlace.setOpenExternalLinks(False)
    f.addRow("Texto", enlace)
    inactivo = W.QLabel("Texto inactivo"); inactivo.setEnabled(False)
    f.addRow("Inactivo", inactivo)
    rejilla.addWidget(caja, 0, 0)

    # columna 2: vistas
    pestanas = W.QTabWidget()
    lista = W.QListWidget(); lista.setAlternatingRowColors(True)
    for i, t in enumerate(("Documentos", "Imágenes", "Música", "Vídeos", "Descargas", "Proyectos")):
        lista.addItem(t)
    lista.setCurrentRow(2)
    pestanas.addTab(lista, "Lista")
    arbol = W.QTreeWidget(); arbol.setHeaderLabels(["Nombre", "Tamaño", "Fecha"]); arbol.setAlternatingRowColors(True)
    for n, s, d in (("informe.pdf", "1,2 MB", "2026-10-18"), ("datos.csv", "340 KB", "2026-10-17"), ("notas.md", "12 KB", "2026-10-16")):
        arbol.addTopLevelItem(W.QTreeWidgetItem([n, s, d]))
    arbol.setCurrentItem(arbol.topLevelItem(1))
    pestanas.addTab(arbol, "Árbol")
    texto = W.QTextEdit(); texto.setPlainText("Área de texto sobre el fondo de vista.\nSegunda línea.")
    pestanas.addTab(texto, "Texto")
    rejilla.addWidget(pestanas, 0, 1)

    estado = ventana.statusBar(); estado.showMessage("Barra de estado · 3 elementos")
    ventana.resize(980, 460)
    return ventana


def main() -> int:
    esquema, salida = Path(sys.argv[1]), Path(sys.argv[2])
    preparar_entorno(esquema)
    from PyQt6 import QtWidgets as W
    app = W.QApplication([])
    app.setStyle("Breeze")
    app.setPalette(paleta_desde_esquema(esquema))
    if app.style().objectName().lower() != "breeze":
        print("aviso: el estilo Breeze no cargó; estilo:", app.style().objectName())
    from PyQt6 import QtGui
    QtGui.QIcon.setThemeName("breeze" if "Claro" in esquema.name else "breeze-dark")
    ventana = galeria(f"{esquema.stem} · Breeze")
    ventana.show()
    app.processEvents()
    pix = ventana.grab()
    salida.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(salida))
    print(f"escrito {salida} ({pix.width()}×{pix.height()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
