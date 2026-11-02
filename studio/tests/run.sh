#!/usr/bin/env bash
# studio/tests/run.sh — corre las pruebas de Lliphi Studio (studio/tests) con pytest, con la carpeta temporal en disco y sin caché.
# Uso: studio/tests/run.sh [opciones de pytest]   (p. ej. -k controladores)
# Las del proyecto (pruebas/) se corren aparte: `.venv/bin/python -m pytest -q pruebas` (o el Python del sistema con pytest).
# La carpeta temporal va a ~/.cache (no a /tmp, que es RAM). Nada toca el repo real ni la sesión de KDE: cada prueba parte
# de una COPIA del proyecto (studio/muestra.py) y de un HOME falso; ninguna prueba instala nada en la sesión real ni abre
# una sesión anidada. Las pruebas en proceso usan el binding del Python que corre pytest; las de QML y la de humo abren un
# proceso hijo con el Python del sistema (/usr/bin/python3, el del Qt con Kirigami) sin pantalla. Las órdenes corren, como
# en la ventana, con el .venv del proyecto (enlazado en la copia) si existe.
set -euo pipefail

DIR_STUDIO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR_REPO="$(dirname "$DIR_STUDIO")"
BASE_TMP="${XDG_CACHE_HOME:-$HOME/.cache}/pytest/lliphi-studio"
mkdir -p "$BASE_TMP"

export PYTHONDONTWRITEBYTECODE=1
export QT_QPA_PLATFORM=offscreen
if [[ -z "${GUI_COMUN_DIR:-}" && -d "${DIR_REPO}/../gui-comun/gui_comun" ]]; then
    export GUI_COMUN_DIR="$(cd "${DIR_REPO}/../gui-comun" && pwd)"
fi
exec python3 -m pytest "${DIR_STUDIO}/tests" --basetemp "$BASE_TMP" -p no:cacheprovider -q "$@"
