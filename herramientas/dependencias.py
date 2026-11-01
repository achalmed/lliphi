#!/usr/bin/env python3
"""Atajo de compatibilidad (documentado en la versión 0.3.0): equivale a `python3 herramientas/instalar.py dependencias`.
Las dependencias de terceros ahora las declara cada módulo en su `externas.py` (`global/`, `modulos/iconos-cursores/`).

Uso:  python3 herramientas/dependencias.py [--aplicar] [--opcionales]"""
import subprocess
import sys
from pathlib import Path

sys.exit(subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "instalar.py"), "dependencias", *sys.argv[1:]]).returncode)
