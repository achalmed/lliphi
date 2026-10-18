#!/usr/bin/env python3
"""Genera `generado/` desde `tokens/` y comprueba que lo versionado no se ha editado a mano.

Uso:  python3 herramientas/generar.py                 # simula: qué escribiría y qué cambiaría
      python3 herramientas/generar.py --aplicar       # escribe generado/
      python3 herramientas/generar.py verificar       # 0 si generado/ coincide con una generación nueva; 1 si no
      python3 herramientas/generar.py --destinos esquema,konsole [--aplicar]
Solo biblioteca estándar (los fondos piden Pillow). `tokens/tokens.json` lo escribe antes `herramientas/paleta.py`.
"""
from __future__ import annotations

import filecmp
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from destinos import RAIZ, cargar  # noqa: E402
from destinos import desktoptheme, esquema, fondo, konsole, lookandfeel  # noqa: E402

GENERADO = RAIZ / "generado"
DESTINOS = {"esquema": esquema, "global": lookandfeel, "estilo": desktoptheme, "konsole": konsole, "fondos": fondo}


def generar_en(carpeta: Path, nombres: list[str]) -> list[Path]:
    tokens, marca = cargar()
    hechos: list[Path] = []
    for n in nombres:
        hechos += DESTINOS[n].generar(tokens, marca, carpeta)
    return hechos


def diferencias(nuevo: Path, viejo: Path) -> list[str]:
    out: list[str] = []
    for ruta in sorted(p for p in nuevo.rglob("*") if p.is_file()):
        rel = ruta.relative_to(nuevo)
        otro = viejo / rel
        if not otro.exists():
            out.append(f"falta en generado/: {rel}")
        elif not filecmp.cmp(ruta, otro, shallow=False):
            out.append(f"difiere: {rel}")
    for ruta in sorted(p for p in viejo.rglob("*") if p.is_file()):
        rel = ruta.relative_to(viejo)
        if not (nuevo / rel).exists():
            out.append(f"sobra en generado/: {rel}")
    return out


def main() -> int:
    args = sys.argv[1:]
    nombres = list(DESTINOS)
    if "--destinos" in args:
        nombres = args[args.index("--destinos") + 1].split(",")
    with tempfile.TemporaryDirectory(prefix="llampu-gen-") as tmp:
        carpeta = Path(tmp)
        hechos = generar_en(carpeta, nombres)
        if "verificar" in args:
            d = diferencias(carpeta, GENERADO) if "--destinos" not in args else [
                x for x in diferencias(carpeta, GENERADO) if not x.startswith("sobra")]
            for x in d:
                print(" ", x)
            print(f"[verificar] {len(hechos)} archivos generados · {len(d)} diferencia(s) · {'al día' if not d else 'DERIVA'}")
            return 0 if not d else 1
        d = diferencias(carpeta, GENERADO)
        if "--aplicar" in args:
            for n in nombres:
                pass
            # reemplazo completo de las carpetas de los destinos pedidos
            for sub in {h.relative_to(carpeta).parts[0] for h in hechos}:
                if (GENERADO / sub).exists():
                    shutil.rmtree(GENERADO / sub)
                shutil.copytree(carpeta / sub, GENERADO / sub)
            print(f"[generar] {len(hechos)} archivos escritos en generado/ ({len(d)} cambiaron)")
        else:
            for x in d:
                print(" ", x)
            print(f"[generar] simulación: {len(hechos)} archivos; {len(d)} cambiarían (--aplicar escribe)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
