#!/usr/bin/env python3
"""Construye `generado/` desde `tokens/` y los módulos, lo valida y comprueba que lo versionado no se ha editado a mano.

Uso:  python3 herramientas/generar.py                      # simula: qué escribiría y qué cambiaría
      python3 herramientas/generar.py --aplicar            # escribe generado/ y sitio/generado/
      python3 herramientas/generar.py --modulos esquema,global [--aplicar]
      python3 herramientas/generar.py verificar            # 0 si generado/ coincide con una construcción nueva; 1 si no
      python3 herramientas/generar.py validar              # manifiestos, dependencias, estructura KDE e integración
      python3 herramientas/generar.py verificar|validar --json   # lo mismo en JSON (lo lee Lliphi Studio)
      python3 herramientas/generar.py lista                # módulos, clase, dependencias e instalación
      python3 herramientas/generar.py empaquetar           # dist/: tarballs por módulo, SHA256SUMS, notas y ficha de la tienda
Cada módulo se describe en su `modulo.json` (`global/`, `modulos/<id>/`, `complementos/<id>/`) y se construye con su
`construir.py`; el núcleo está en `herramientas/nucleo/` (docs/arquitectura.md). Solo biblioteca estándar (los fondos
piden Pillow). `tokens/tokens.json` lo escribe antes `modulos/esquema/paleta.py`.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nucleo import construccion, registro, validacion  # noqa: E402


def lista() -> int:
    for m in registro.todos():
        deps = {k: v for k, v in m.datos.get("dependencias", {}).items() if k in ("construccion", "integra", "referencia")}
        texto = " · ".join(f"{k}: {', '.join(v)}" for k, v in deps.items() if v)
        print(f"{m.rol:<11} {m.id:<16} {m.clase:<10} {m.datos['formato']:<20} {len(m.datos.get('instalacion', []))} destinos  {texto}")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__); return 0
    if "empaquetar" in args:
        return construccion.empaquetar()
    if "validar" in args:
        return validacion.informe("--json" in args)
    if "lista" in args:
        return lista()
    pedidos = args[args.index("--modulos") + 1].split(",") if "--modulos" in args else None
    try:
        nombres = construccion.objetivos(pedidos)
    except KeyError as e:
        print(e.args[0]); return 1
    with tempfile.TemporaryDirectory(prefix="lliphi-gen-") as tmp:
        carpeta = Path(tmp)
        hechos = construccion.construir_en(carpeta, nombres)
        d = construccion.comparar(carpeta, nombres) + (construccion.huerfanas() if pedidos is None else [])
        if "verificar" in args and "--json" in args:
            print(json.dumps({"archivos": len(hechos), "al_dia": not d, "diferencias": d}, ensure_ascii=False))
            return 0 if not d else 1
        if "verificar" in args:
            for x in d:
                print(" ", x)
            print(f"[verificar] {len(hechos)} archivos generados · {len(d)} diferencia(s) · {'al día' if not d else 'DERIVA'}")
            return 0 if not d else 1
        if "--aplicar" in args:
            construccion.copiar(carpeta, nombres)
            for x in construccion.huerfanas() if pedidos is None else []:
                print(f"  {x}: retírala con git rm -r")
            print(f"[generar] {len(hechos)} archivos escritos ({len(d)} cambiaron) · {', '.join(nombres)}")
        else:
            for x in d:
                print(" ", x)
            print(f"[generar] simulación: {len(hechos)} archivos; {len(d)} cambiarían (--aplicar escribe) · {', '.join(nombres)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
