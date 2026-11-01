"""Utilidades para traer de GitHub lo de terceros que Lliphi usa tal cual (los `externas.py` de los módulos): la API
de versiones, la descarga y las familias tipográficas instaladas. Solo biblioteca estándar (urllib)."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path

HOME = Path.home()
DATA = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local" / "share")
ICONOS = DATA / "icons"
FUENTES = DATA / "fonts"


def api(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lliphi", "Accept": "application/vnd.github+json"}), timeout=60) as r:
        return json.load(r)


def descargar(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lliphi"}), timeout=600) as r:
        return r.read()


def familias() -> set[str]:
    r = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout.splitlines()
    return {f.strip() for linea in r for f in linea.split(",")}
