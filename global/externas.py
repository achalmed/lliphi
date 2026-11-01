"""Dependencias de terceros del tema global: la tipografía (mejora 9, decisiones 4.14), instalada en el usuario con
`instalar.py dependencias`. Inter (OFL) viene de la distribución (`fonts-inter`) y aquí solo se comprueba; la
monoespaciada es JetBrains Mono en su versión Nerd Font (OFL; ryanoasis/nerd-fonts), que añade los iconos que usan el
prompt y `lsd`: se descarga de la última versión publicada a `$XDG_DATA_HOME/fonts/JetBrainsMonoNerdFont/`. Antes vivía
en `herramientas/dependencias.py`."""
from __future__ import annotations

import io
import shutil
import subprocess
import tarfile

from nucleo.descargas import FUENTES, api, descargar, familias

FUENTE_MONO = {"repo": "ryanoasis/nerd-fonts", "activo": "JetBrainsMono.tar.xz", "familia": "JetBrainsMono Nerd Font",
               "carpeta": "JetBrainsMonoNerdFont", "licencia": "OFL-1.1"}


def fuente_mono(aplicar: bool) -> None:
    if FUENTE_MONO["familia"] in familias():
        print(f"  {FUENTE_MONO['familia']} ya está instalada"); return
    destino = FUENTES / FUENTE_MONO["carpeta"]
    print(f"  {'descargar' if aplicar else 'SIM descargar'} {FUENTE_MONO['familia']} ({FUENTE_MONO['licencia']}) → {destino}")
    if not aplicar:
        return
    rel = api(f"https://api.github.com/repos/{FUENTE_MONO['repo']}/releases/latest")
    url = next(a["browser_download_url"] for a in rel["assets"] if a["name"] == FUENTE_MONO["activo"])
    destino.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(descargar(url)), mode="r:xz") as tar:
        # solo la familia «Nerd Font» (no las variantes Mono ni Propo) y su licencia
        miembros = [m for m in tar.getmembers() if m.isfile() and (
            (m.name.startswith("JetBrainsMonoNerdFont-") and m.name.endswith(".ttf")) or m.name in ("OFL.txt", "README.md"))]
        tar.extractall(destino, members=miembros, filter="data")
    if shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(destino)], capture_output=True)
    print(f"  {FUENTE_MONO['familia']} {rel['tag_name']} instalada: {len(miembros)} archivos")


def fuentes() -> None:
    hay = "Inter" in familias()
    print(f"  {'ok ' if hay else 'FALTA'} tipografía Inter" + ("" if hay else " (sudo apt install fonts-inter)"))


def instalar(aplicar: bool, opcionales: bool = False) -> None:
    fuente_mono(aplicar)     # mejora 9 (decisiones 4.14): JetBrains Mono Nerd Font
    fuentes()
