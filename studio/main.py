#!/usr/bin/python3
"""
main.py — Punto de entrada de Lliphi Studio (opcional: Lliphi funciona sin ella, con herramientas/*.py). Sin lógica: la
aplicación se arma en lliphi_app/aplicacion.py.

Corre con el Python del sistema (/usr/bin/python3), cuyo Qt es el que trae Kirigami; las órdenes de Lliphi corren con el
`.venv` del proyecto si existe (`/usr/bin/python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r
requirements.txt`: coloraide, para paleta.py) o, si no, con este mismo Python. `gui_comun` llega como paquete de pip o por
`GUI_COMUN_DIR` (la carpeta del repo gui-comun); nunca se busca en otra carpeta: el repo es autónomo.

Uso:
    /usr/bin/python3 studio/main.py                       # desde la raíz de lliphi
    /usr/bin/python3 studio/main.py --destino esquema     # abre con un destino elegido
    /usr/bin/python3 studio/main.py --smoke               # construye la interfaz y sale (prueba de humo)
    /usr/bin/python3 studio/main.py --instalar-lanzador   # el acceso directo del menú (-n simula)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))      # el paquete del studio

from lliphi_app.aplicacion import main                          # noqa: E402  (lliphi_app localiza gui_comun al importarse)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
