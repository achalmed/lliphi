#!/usr/bin/python3
"""studio/capturar.py — una captura de Lliphi Studio para la documentación sobre una COPIA del proyecto (`muestra.py`)
en una carpeta temporal fuera de la carpeta de inicio, con HOME, configuración, caché, datos y estado temporales
(ninguna ruta de la máquina en pantalla y nada instalado en la sesión real), el esquema de color que se pida, el área,
el destino y, si se pide, el plan de los seis pasos o la paleta de órdenes.

    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-oscuro.png --esquema generado/esquema/LliphiOscuro.colors --area diseno
    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-claro.png --esquema generado/esquema/LliphiClaro.colors --destino konsole --pasos instalar
    /usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-paleta.png --esquema generado/esquema/LliphiOscuro.colors --paleta "instalar"

Con `--verificar` corre de verdad, sobre la copia, «Verificar lo generado» (unos segundos), para que las tarjetas
enseñen si lo generado está al día. Corre con el Python del sistema; las órdenes, con el `.venv` del proyecto (enlazado
en la copia) si existe. `--pasos` solo PREPARA el plan (pasos 1–3): nunca ejecuta.
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
    parser.add_argument("--area", default="", help="el área de la barra lateral (diseno · esquemas · plasma · kvantum · konsole · editores · fondos · tipografia · iconos · otros)")
    parser.add_argument("--destino", default="", help="el destino elegido (lleva a su área)")
    parser.add_argument("--par", type=int, default=-1, help="el archivo del destino cuya diferencia se muestra")
    parser.add_argument("--pasos", default="", help="prepara el plan de los seis pasos: instalar · generar · desinstalar (no ejecuta)")
    parser.add_argument("--paso", type=int, default=0, help="el paso que se muestra (0 Plan · 1 Afectados · 2 Conflictos)")
    parser.add_argument("--instalar-en-la-copia", default="", help="copia a mano al HOME de la copia lo generado de este destino (para ver «igual» y una diferencia)")
    parser.add_argument("--verificar", action="store_true", help="corre «Verificar lo generado» antes de capturar (unos segundos)")
    parser.add_argument("--paleta", default=None, help="abre la paleta de órdenes con este texto")
    parser.add_argument("--ancho", type=int, default=1360)
    parser.add_argument("--alto", type=int, default=900)
    args = parser.parse_args()

    if "LLIPHI_STUDIO_CAPTURA" not in os.environ:      # primera pasada: la copia, el entorno temporal (y esquema), y relanzar
        from lliphi_app import hay_gui_comun
        if not hay_gui_comun():
            print("capturar.py: falta gui_comun (pip, o GUI_COMUN_DIR)", file=sys.stderr)
            return 2
        from gui_comun.galeria.esquema import entorno_con_esquema
        import muestra
        carpeta = Path(tempfile.mkdtemp(prefix="lliphi-studio-captura-", dir="/tmp"))   # fuera de la carpeta de inicio
        m = muestra.crear(carpeta / "muestra", solo_lectura=True)     # solo ve, prepara y copia al HOME de la copia: generado/ enlazado
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
    destinos, operaciones, interfaz, tareas = (piezas[k] for k in ("destinos", "operaciones", "interfaz", "tareas"))
    destinos.leer_instalacion_ahora()
    if not app.cargar(aplicacion.QML_DIR / "Main.qml"):
        return 1
    raiz = app.motor.rootObjects()[0]
    raiz.setProperty("width", args.ancho)
    raiz.setProperty("height", args.alto)
    centro, escritura = piezas["centro"], piezas["escritura"]

    def preparar_copia():
        """Para ver «igual» y una diferencia: copia lo generado del destino al HOME de la copia y cambia una línea del primero."""
        from lliphi_app.servicios import areas
        for i, par in enumerate(areas.comparar(args.instalar_en_la_copia)):
            o, d = Path(par["origen"]), Path(par["destino"])
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(o, d, dirs_exist_ok=True) if o.is_dir() else shutil.copy2(o, d)
            if i == 0 and d.is_file():
                lineas = d.read_text(encoding="utf-8").splitlines()
                if len(lineas) > 4:
                    lineas[3] = lineas[3] + "  # cambiado a mano"
                d.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    def empezar():
        if args.instalar_en_la_copia:
            preparar_copia()
        if args.verificar:
            operaciones.fijar("verificar")
            operaciones.simular()
        QTimer.singleShot(200, esperar)

    def esperar():
        if tareas.activa:
            QTimer.singleShot(150, esperar)
            return
        if args.area:
            centro.fijarArea(args.area)
        if args.destino:
            centro.irADestino(args.destino)
            if args.par >= 0:
                centro.fijarPar(args.par)
        if args.pasos:
            escritura.planificar(args.pasos, [args.destino] if args.destino and args.pasos != "desinstalar" else [])
            interfaz.pedir.emit("pasos", {})
        QTimer.singleShot(300, listo)

    def listo():
        raiz.setProperty("pasoMostrado", args.paso)
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
