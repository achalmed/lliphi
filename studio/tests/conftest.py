"""studio/tests/conftest.py — una COPIA del proyecto y un HOME falso para cada prueba: nunca se escribe en el repo real
ni en la configuración del escritorio.

El temporal va al disco (XDG_CACHE_HOME), no a /tmp (tmpfs: es RAM). La copia lleva lo que leen las órdenes (tokens,
módulos, herramientas, generado, fuentes) y enlaza `.venv`; no copia el sitio ni las muestras.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[1]
REPO = STUDIO.parent
BASETEMP = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "pytest" / "lliphi-studio" / "basetemp"
sys.path.insert(0, str(STUDIO))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if config.option.basetemp:
        return
    args = [Path(a.split("::")[0]).resolve() for a in (config.args or [])]
    if args and all(REPO in a.parents or a == REPO for a in args):
        BASETEMP.parent.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(BASETEMP)


@pytest.fixture(scope="session")
def copia_base(tmp_path_factory) -> Path:
    destino = tmp_path_factory.mktemp("lliphi") / "lliphi"
    ignorar = shutil.ignore_patterns("__pycache__", ".pytest_cache", "_site", ".quarto")
    destino.mkdir()
    for nombre in ("VERSION", "REUSE.toml", "pyproject.toml", "README.md"):
        shutil.copy2(REPO / nombre, destino / nombre)
    for carpeta in ("tokens", "global", "modulos", "complementos", "herramientas", "generado", "fuentes", "docs"):
        shutil.copytree(REPO / carpeta, destino / carpeta, ignore=ignorar, symlinks=True)
    (destino / "sitio").mkdir()
    (destino / "muestras").symlink_to(REPO / "muestras")   # solo se leen (capturas que exige validar)
    if (REPO / ".venv").exists():
        (destino / ".venv").symlink_to(REPO / ".venv")
    return destino


@pytest.fixture
def lliphi(copia_base, tmp_path, monkeypatch) -> Path:
    """Una copia del proyecto para esta prueba (los ajustes se restauran) y un HOME y XDG falsos."""
    casa = tmp_path / "casa"
    for sub in (".local/share", ".local/state", ".config", ".cache"):
        (casa / sub).mkdir(parents=True)
    copias = {p: p.read_bytes() for p in copia_base.glob("modulos/*/ajustes.json")}
    monkeypatch.setenv("LLIPHI_DIR", str(copia_base))
    monkeypatch.setenv("HOME", str(casa))
    monkeypatch.setenv("XDG_DATA_HOME", str(casa / ".local" / "share"))
    monkeypatch.setenv("XDG_STATE_HOME", str(casa / ".local" / "state"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(casa / ".config"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(casa / ".cache"))
    yield copia_base
    for p, contenido in copias.items():
        p.write_bytes(contenido)


@pytest.fixture(scope="session")
def app():
    from PySide6.QtWidgets import QApplication
    QApplication.setOrganizationName("PruebasLliphiStudio")
    QApplication.setApplicationName("LliphiStudioPruebas")
    return QApplication.instance() or QApplication([])
