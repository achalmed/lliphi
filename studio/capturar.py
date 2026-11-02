#!/usr/bin/python3
"""studio/capturar.py — una captura de Lliphi Studio para la documentación sobre una COPIA del proyecto (`muestra.py`)
en una carpeta temporal fuera de la carpeta de inicio, con HOME, configuración, caché, datos y estado temporales
(ninguna ruta de la máquina en pantalla y nada instalado en la sesión real), el esquema de color que se pida, el
destino, la pestaña de detalles y, si se pide, la paleta de órdenes.

    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-oscuro.png --esquema generado/esquema/LliphiOscuro.colors --destino esquema --verificar
    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-claro.png --esquema generado/esquema/LliphiClaro.colors --destino konsole --pestana 1
    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-paleta.png --esquema generado/esquema/LliphiOscuro.colors --paleta "instalar"

Antes de capturar corre de verdad, sobre la copia, «Generar el destino» en simulación (F5) y, con `--verificar`,
«Verificar lo generado» (unos segundos), para que la tabla enseñe los estados. Corre con el Python del sistema; las
órdenes, con el `.venv` del proyecto (enlazado en la copia) si existe.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))


def main() -> int:
    parser = argparse.ArgumentParser(description="Captura de Lliphi Studio sobre una copia del proyecto")
    parser.add_argument("salida")
    parser.add_argument("--esquema", help="archivo .colors de KDE (relanza con XDG_CONFIG_HOME temporal)")
    parser.add_argument("--destino", default="esquema", help="el destino elegido (id del módulo; vacío: ninguno)")
    parser.add_argument("--rol", default="", help="la vista de la navegación (global · modulo · complemento; vacío: todos)")
    parser.add_argument("--pestana", type=int, default=0, help="pestaña de detalles (0 Resumen · 1 Paleta · 2 Diferencias · 3 Registro · 4 Operación)")
    parser.add_argument("--verificar", action="store_true", help="corre «Verificar lo generado» antes de capturar (unos segundos)")
    parser.add_argument("--sin-correr", action="store_true", help="no corre nada antes de capturar")
    parser.add_argument("--paleta", default=None, help="abre la paleta de órdenes con este texto")
    parser.add_argument("--ancho", type=int, default=1280)
    parser.add_argument("--alto", type=int, default=800)
    args = parser.parse_args()

    if "LLIPHI_STUDIO_CAPTURA" not in os.environ:      # primera pasada: la copia, el entorno temporal (y esquema), y relanzar
        from lliphi_app import hay_gui_comun
        if not hay_gui_comun():
            print("capturar.py: falta gui_comun (pip, o GUI_COMUN_DIR)", file=sys.stderr)
            return 2
        from gui_comun.galeria.esquema import entorno_con_esquema
        import muestra
        carpeta = Path(tempfile.mkdtemp(prefix="lliphi-studio-captura-", dir="/tmp"))   # fuera de la carpeta de inicio
        m = muestra.crear(carpeta / "muestra")
        config_usuario = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        for nombre in ("kdeglobals", "kcminputrc", "Kvantum", "fontconfig"):
            origen = config_usuario / nombre
            if origen.is_dir():
                shutil.copytree(origen, m.casa / ".config" / nombre, dirs_exist_ok=True)
            elif origen.is_file():
                shutil.copy2(origen, m.casa / ".config" / nombre)
        env = entorno_con_esquema(Path(args.esquema).expanduser().resolve(), m.casa / ".config") if args.esquema else dict(os.environ, XDG_CONFIG_HOME=str(m.casa / ".config"))
        env.update(m.entorno)
        # los iconos y tipografías del usuario se ven por XDG_DATA_DIRS; XDG_DATA_HOME sigue en la casa falsa (ninguna ruta de la máquina en los destinos)
        env["XDG_DATA_DIRS"] = str(Path.home() / ".local" / "share") + ":" + (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share")
        env.update({"LLIPHI_STUDIO_CAPTURA": str(carpeta), "QT_QPA_PLATFORM": "offscreen", "LLIPHI_STUDIO_MUESTRA": str(m.raiz)})
        env.setdefault("QT_QPA_PLATFORMTHEME", "kde")
        if "GUI_COMUN_DIR" not in env:
            import gui_comun
            env["GUI_COMUN_DIR"] = str(Path(gui_comun.__file__).resolve().parents[1])
        orden = [sys.executable, str(AQUI / "capturar.py")] + [a for a in sys.argv[1:] if not a.startswith("--esquema") and a != args.esquema]
        codigo = subprocess.run(orden, env=env).returncode
        shutil.rmtree(carpeta, ignore_errors=True)
        return codigo

    from lliphi_app import aplicacion
    from gui_comun.nucleo import Aplicacion
    from gui_comun.qt import QTimer

    app = Aplicacion(aplicacion.APP_ID, aplicacion.NOMBRE, version=aplicacion.APP_VERSION, organizacion=aplicacion.ORG_NAME, nombre_ajustes=aplicacion.APP_NAME)
    piezas = aplicacion.construir(app, leer_instalacion=False)
    espacio, destinos, operaciones, interfaz, tareas = (piezas[k] for k in ("espacio", "destinos", "operaciones", "interfaz", "tareas"))
    destinos.leer_instalacion_ahora()
    if not app.cargar(aplicacion.QML_DIR / "Main.qml"):
        return 1
    raiz = app.motor.rootObjects()[0]
    raiz.setProperty("width", args.ancho)
    raiz.setProperty("height", args.alto)
    pendientes: list[str] = []

    def correr_siguiente():
        if tareas.activa:
            QTimer.singleShot(150, correr_siguiente)
            return
        if pendientes:
            operaciones.fijar(pendientes.pop(0))
            operaciones.simular()
            QTimer.singleShot(150, correr_siguiente)
            return
        QTimer.singleShot(300, listo)

    def empezar():
        espacio.fijarRol(args.rol)
        if args.destino:
            destinos.irA(args.destino)
        if not args.sin_correr:
            if args.verificar:
                pendientes.append("verificar")
            if args.destino:
                pendientes.append("generar")
        correr_siguiente()

    def listo():
        if args.destino:
            operaciones.fijar("generar")
        raiz.setProperty("mostrarDetalles", True)
        raiz.setProperty("mostrarInferior", True)
        inferior = raiz.property("inferior")
        if inferior is not None:
            inferior.setProperty("pestanaActual", 0)
        QTimer.singleShot(500, lambda: interfaz.pedir.emit("pestana", {"indice": args.pestana}))
        if args.paleta is not None:
            QTimer.singleShot(900, lambda: interfaz.pedir.emit("paleta", {"texto": args.paleta}))
        app.capturar(args.salida, espera_ms=2400)

    QTimer.singleShot(600, empezar)
    codigo = app.app.exec()
    app.cerrar()
    print("CAPTURA", args.salida)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
