#!/usr/bin/env python3
"""
main.py — Punto de entrada de Lliphi Studio (opcional: Lliphi funciona sin ella, con herramientas/*.py).

Uso:
    python3 studio/main.py                           # desde la raíz de lliphi
    python3 studio/main.py --smoke                   # construye la interfaz y sale (prueba de humo)
    python3 studio/main.py --pagina color            # abre en una sección (dashboard, color, plasma, ventanas, iconos,
                                                     # pantallas, disposicion, vivo, despliegue)
    python3 studio/main.py --captura <carpeta>       # una captura PNG de cada sección y sale
    python3 studio/main.py --instalar-lanzador [-n]  # acceso directo en el menú de aplicaciones (--quitar-lanzador)
"""

import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))

from lliphi_studio import INSTALAR, faltan  # noqa: E402

APP_ID = "lliphi-studio"


def datos_lanzador() -> dict:
    from lliphi_studio.ventana import ACENTO, LOGO
    return dict(app_id=APP_ID, nombre="Lliphi Studio", comentario="El centro de control de Lliphi: paleta, estilo de "
                "Plasma, decoración, iconos, pantallas, disposición, sesión de prueba y despliegue",
                orden=[sys.executable, str(_AQUI / "main.py")], logo_svg=LOGO, acento=ACENTO, categorias="Settings;DesktopSettings;",
                palabras="lliphi;tema;plasma;kde;color;paleta;aurorae;iconos;cursores;")


def _capturas(app, ventana, carpeta: Path) -> None:
    from PySide6.QtCore import QTimer
    carpeta.mkdir(parents=True, exist_ok=True)
    ids = list(ventana._page_order)

    def siguiente(i: int = 0) -> None:
        if i >= len(ids):
            app.quit()
            return
        ventana.navigate(ids[i])
        QTimer.singleShot(1800 if i == 0 else 900, lambda: (ventana.ui.grab().save(str(carpeta / f"{i + 1:02d}-{ids[i]}.png")),
                                                            siguiente(i + 1)))
    QTimer.singleShot(2500, siguiente)


def main() -> int:
    if faltan():
        print(f"Lliphi Studio necesita {', '.join(faltan())}. Instálalo con:\n  {INSTALAR}", file=sys.stderr)
        return 3
    from gui_comun import lanzador
    atendido = lanzador.desde_main(sys.argv[1:], **datos_lanzador())   # --instalar-lanzador / --quitar-lanzador
    if atendido is not None:
        return atendido
    from gui_comun.diseno import preparar_plataforma
    preparar_plataforma()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    QApplication.setOrganizationName("EdisonAchalma")
    QApplication.setApplicationName("LliphiStudio")
    QApplication.setDesktopFileName(APP_ID)
    app = QApplication([sys.argv[0]])
    from lliphi_studio.ventana import Ventana
    ventana = Ventana()
    ventana.show()
    if "--pagina" in sys.argv:
        ventana.navigate(sys.argv[sys.argv.index("--pagina") + 1])
    if "--smoke" in sys.argv:
        QTimer.singleShot(0, app.quit)
    if "--captura" in sys.argv:
        _capturas(app, ventana, Path(sys.argv[sys.argv.index("--captura") + 1]))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
