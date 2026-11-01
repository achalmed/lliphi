#!/usr/bin/env python3
"""Atajo de compatibilidad (documentado en la versión 0.3.0): equivale a `python3 herramientas/instalar.py sddm`. El
inicio de sesión SDDM es el complemento `complementos/sddm/` (su instalador: `complementos/sddm/instalar_sddm.py`).

Uso:  python3 herramientas/instalar_sddm.py [--aplicar]
Vista previa sin root:  sddm-greeter-qt6 --test-mode --theme generado/sddm/lliphi"""
import subprocess
import sys
from pathlib import Path

sys.exit(subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "instalar.py"), "sddm", *sys.argv[1:]]).returncode)
