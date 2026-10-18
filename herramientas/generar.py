#!/usr/bin/env python3
"""Genera `generado/` desde `tokens/` y comprueba que lo versionado no se ha editado a mano.

Uso:  python3 herramientas/generar.py                 # simula: qué escribiría y qué cambiaría
      python3 herramientas/generar.py --aplicar       # escribe generado/
      python3 herramientas/generar.py verificar       # 0 si generado/ coincide con una generación nueva; 1 si no
      python3 herramientas/generar.py --destinos esquema,konsole [--aplicar]
      python3 herramientas/generar.py empaquetar       # dist/: tarballs por módulo, SHA256SUMS, notas y ficha de la tienda
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
from destinos import desktoptheme, editores, esquema, fondo, konsole, lookandfeel, sitio, terminales  # noqa: E402

GENERADO = RAIZ / "generado"
DESTINOS = {"esquema": esquema, "global": lookandfeel, "estilo": desktoptheme, "konsole": konsole, "fondos": fondo,
            "terminales": terminales, "editores": editores, "sitio": sitio}
# el sitio se genera dentro de sitio/generado/ (Quarto solo renderiza lo que cuelga de su proyecto)
BASES = {"sitio": RAIZ / "sitio" / "generado"}


def base_de(nombre: str) -> Path:
    return BASES.get(nombre, GENERADO)


def generar_en(carpeta: Path, nombres: list[str]) -> list[Path]:
    tokens, marca = cargar()
    hechos: list[Path] = []
    for n in nombres:
        hechos += DESTINOS[n].generar(tokens, marca, carpeta / n)
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


def empaquetar() -> int:
    """dist/: un .tar.gz por módulo publicable (desde generado/), SHA256SUMS, notas de versión y ficha de la tienda."""
    import hashlib
    import tarfile
    version = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
    tokens, marca = cargar()
    dist = RAIZ / "dist"
    dist.mkdir(exist_ok=True)
    paquetes = {"esquema": ["color-schemes"], "global": ["look-and-feel"], "estilo": ["desktoptheme"],
                "konsole": ["konsole"], "fondos": ["wallpapers"], "terminales": ["terminales"],
                "editores": ["editores"]}
    sumas = []
    for modulo, carpetas in paquetes.items():
        ruta = dist / f"{marca['id']}-{modulo}-{version}.tar.gz"
        with tarfile.open(ruta, "w:gz") as tar:
            for c in carpetas:
                for sub in sorted((GENERADO / c).iterdir()):
                    tar.add(sub, arcname=sub.name)
        sumas.append(f"{hashlib.sha256(ruta.read_bytes()).hexdigest()}  {ruta.name}")
        print(f"  {ruta.relative_to(RAIZ)}")
    (dist / "SHA256SUMS").write_text("\n".join(sumas) + "\n", encoding="utf-8")
    cambios = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    ini = cambios.find(f"## [{version}]")
    fin = cambios.find("\n## [", ini + 1) if ini >= 0 else -1
    notas = cambios[ini:fin if fin > 0 else None] if ini >= 0 else f"## [{version}]\n"
    (dist / f"NOTAS-{version}.md").write_text(notas + f"\nComprobar: `sha256sum -c SHA256SUMS`. Sitio: {marca['sitio_tema']}\n", encoding="utf-8")
    (dist / "FICHA-KDE-STORE.md").write_text(f"""# {marca['nombre']} {version}

{marca['descripcion']}

Dos variantes, **{marca['nombre_esquema']['claro']}** y **{marca['nombre_esquema']['oscuro']}**, generadas desde una
sola fuente de tokens con contraste medido (WCAG 2.2). El estilo de Plasma sigue el esquema y el acento del sistema;
decoración Breeze coloreada; sin Kvantum; instalación reversible con el instalador del repositorio.

- Sitio y guías: {marca['sitio_tema']}
- Código (Source): {marca['repositorio']}
- Licencia: activos CC BY-SA 4.0, código MIT (REUSE 3.3)
- Requiere Plasma 6 (probado en 6.6)
""", encoding="utf-8")
    print(f"  dist/SHA256SUMS · dist/NOTAS-{version}.md · dist/FICHA-KDE-STORE.md")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "empaquetar" in args:
        return empaquetar()
    nombres = list(DESTINOS)
    if "--destinos" in args:
        nombres = args[args.index("--destinos") + 1].split(",")
    with tempfile.TemporaryDirectory(prefix="lliphi-gen-") as tmp:
        carpeta = Path(tmp)
        hechos = generar_en(carpeta, nombres)
        # cada destino escribe en carpeta/<destino>/<subcarpetas>; se compara y se copia subcarpeta a subcarpeta
        d: list[str] = []
        copias: list[tuple[Path, Path]] = []
        for n in nombres:
            origen_n = carpeta / n
            if not origen_n.exists():
                continue
            for sub in sorted(x for x in origen_n.iterdir()):
                destino_sub = base_de(n) / sub.name
                d += [f"{n}/{x}" for x in (diferencias(sub, destino_sub) if destino_sub.exists() else [f"falta en destino: {sub.name}"])]
                copias.append((sub, destino_sub))
        if "verificar" in args:
            for x in d:
                print(" ", x)
            print(f"[verificar] {len(hechos)} archivos generados · {len(d)} diferencia(s) · {'al día' if not d else 'DERIVA'}")
            return 0 if not d else 1
        if "--aplicar" in args:
            for origen_sub, destino_sub in copias:
                if destino_sub.exists():
                    shutil.rmtree(destino_sub) if destino_sub.is_dir() else destino_sub.unlink()
                destino_sub.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(origen_sub, destino_sub) if origen_sub.is_dir() else shutil.copy2(origen_sub, destino_sub)
            print(f"[generar] {len(hechos)} archivos escritos ({len(d)} cambiaron)")
        else:
            for x in d:
                print(" ", x)
            print(f"[generar] simulación: {len(hechos)} archivos; {len(d)} cambiarían (--aplicar escribe)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
