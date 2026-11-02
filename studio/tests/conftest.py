"""studio/tests/conftest.py — utilidades de las pruebas de Lliphi Studio (fase 5 QML, 2026-11-02).

El temporal va al disco (XDG_CACHE_HOME), no a /tmp (tmpfs: es RAM). Nada toca el repo real ni la sesión de KDE: cada
prueba parte de una COPIA ligera del proyecto (`studio/muestra.py`) y de un HOME falso (HOME, XDG_* y LLIPHI_DIR a la
copia). Ninguna prueba instala nada en la sesión real ni abre una sesión anidada (`test_ventana_lliphi.py` lo vigila).
Las órdenes corren, como en la ventana, con el `.venv` del proyecto (enlazado en la copia) si existe.

Dos clases de prueba:
- en proceso (servicios, controladores): con el binding del Python que corre pytest; QSettings apunta a un temporal;
- en un proceso hijo (cada QML, la ventana entera, `--smoke`): con el Python del sistema (/usr/bin/python3), el único
  cuyo Qt trae Kirigami. `gui_comun` llega instalado o por `GUI_COMUN_DIR` (run.sh lo pone si el repo gui-comun está al lado).

    studio/tests/run.sh     # = python3 -m pytest studio/tests --basetemp ~/.cache/pytest/lliphi-studio -p no:cacheprovider
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[1]
REPO = STUDIO.parent
BASETEMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pytest" / "lliphi-studio" / "basetemp"

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if str(STUDIO) not in sys.path:
    sys.path.insert(0, str(STUDIO))
if "GUI_COMUN_DIR" not in os.environ and (REPO.parent / "gui-comun" / "gui_comun").is_dir():
    os.environ["GUI_COMUN_DIR"] = str(REPO.parent / "gui-comun")

import muestra as muestra_mod  # noqa: E402
from lliphi_app import hay_gui_comun  # noqa: E402

HAY_GUI_COMUN = hay_gui_comun()
HAY_BINDING = importlib.util.find_spec("PySide6") is not None or importlib.util.find_spec("PyQt6") is not None
HAY_VENV = (REPO / ".venv" / "bin" / "python").is_file()
requiere_binding = pytest.mark.skipif(not (HAY_BINDING and HAY_GUI_COMUN), reason="sin PySide6/PyQt6 o sin gui_comun")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.basetemp:
        return
    args = [Path(a.split("::")[0]).resolve() for a in (config.args or [])]
    if args and all(REPO in a.parents or a == REPO for a in args):
        BASETEMP.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(BASETEMP)


def _python_del_sistema() -> str | None:
    candidato = Path("/usr/bin/python3")
    if not candidato.is_file() or not HAY_GUI_COMUN:
        return None
    r = subprocess.run([str(candidato), "-c", "import PySide6.QtQml"], capture_output=True, text=True)
    return str(candidato) if r.returncode == 0 else None


PYTHON_SISTEMA = _python_del_sistema()
requiere_sistema = pytest.mark.skipif(PYTHON_SISTEMA is None, reason="sin PySide6 con QML en /usr/bin/python3 (Kirigami)")


@pytest.fixture(scope="session")
def muestra_sesion(tmp_path_factory):
    """Una copia del proyecto para toda la sesión (lo que solo lee)."""
    return muestra_mod.crear(tmp_path_factory.mktemp("muestra") / "lliphi")


@pytest.fixture
def muestra(tmp_path):
    """Una copia nueva por prueba (para los procesos hijos y para lo que escribe)."""
    return muestra_mod.crear(tmp_path / "lliphi")


@pytest.fixture
def entorno_muestra(muestra, monkeypatch):
    for k, v in muestra.entorno.items():
        monkeypatch.setenv(k, v)
    return muestra


@pytest.fixture
def ajustes_temporales(tmp_path, monkeypatch):
    from gui_comun.qt import QSettings
    QSettings.setPath(QSettings.Format.NativeFormat, QSettings.Scope.UserScope, str(tmp_path / "config"))
    return tmp_path


def entorno_gui(muestra, **extra: str) -> dict:
    env = dict(os.environ)
    env.update({"QT_QPA_PLATFORM": "offscreen", "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(muestra.entorno)
    env["LLIPHI_STUDIO_MUESTRA"] = str(muestra.raiz)
    env.update(extra)
    return env


def correr_python(guion: str, env: dict, *args: str, plazo: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run([PYTHON_SISTEMA or sys.executable, "-c", guion, str(STUDIO), *args], env=env, capture_output=True, text=True, timeout=plazo)


@pytest.fixture(scope="session")
def app():
    if not (HAY_BINDING and HAY_GUI_COMUN):
        pytest.skip("sin binding o sin gui_comun")
    from gui_comun.qt import QGuiApplication
    QGuiApplication.setOrganizationName("lliphi-studio-pruebas")
    QGuiApplication.setApplicationName("lliphi-studio-pruebas")
    instancia = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
    yield instancia
