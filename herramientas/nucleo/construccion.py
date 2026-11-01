"""Construcción: genera `generado/<id>/` de cada módulo de clase `paquete` (el tema global integra dentro del suyo a
los componentes) y `sitio/generado/`, compara con lo versionado (deriva) y empaqueta `dist/`.

Siempre se construye en una carpeta temporal y se compara antes de copiar: `generado/` solo cambia con `--aplicar`, y
`verificar` falla si lo versionado difiere de una construcción nueva (alguien editó a mano un archivo generado) o si
en `generado/` sobra una carpeta que no es de ningún módulo. Solo biblioteca estándar (los fondos piden Pillow)."""
from __future__ import annotations

import filecmp
import hashlib
import shutil
import tarfile
from pathlib import Path

from . import RAIZ, VERSION, cargar, registro, sitio

GENERADO = RAIZ / "generado"
SITIO = RAIZ / "sitio" / "generado"   # Quarto solo renderiza lo que cuelga de su proyecto
DIST = RAIZ / "dist"


def objetivos(pedidos: list[str] | None) -> list[str]:
    """Qué hay que construir para lo pedido: un componente se construye construyendo el tema global que lo integra;
    un módulo externo no tiene nada que construir. `sitio` es el destino de los datos del sitio. Sin pedido, todo."""
    if not pedidos:
        return registro.ids("paquete") + ["sitio"]
    salida: list[str] = []
    for p in pedidos:
        if p == "sitio":
            objetivo = "sitio"
        else:
            m = registro.modulo(p)
            objetivo = m.datos["integracion"]["en"] if m.clase == "componente" else (m.id if m.clase == "paquete" else None)
        if objetivo and objetivo not in salida:
            salida.append(objetivo)
    return salida


def construir_en(carpeta: Path, nombres: list[str]) -> list[Path]:
    """Construye en `carpeta/<id>/` (y `carpeta/sitio/`) lo pedido, en orden de dependencias."""
    tokens, marca = cargar()
    hechos: list[Path] = []
    paquetes = [n for n in nombres if n != "sitio"]
    for id_ in registro.orden_de_construccion(paquetes):
        if id_ in paquetes:
            hechos += registro.codigo(id_).generar(tokens, marca, carpeta / id_)
    if "sitio" in nombres:
        hechos += sitio.generar(tokens, marca, carpeta / "sitio")
    return hechos


def destino_de(nombre: str) -> Path:
    return SITIO if nombre == "sitio" else GENERADO / nombre


def diferencias(nuevo: Path, viejo: Path) -> list[str]:
    out: list[str] = []
    for ruta in sorted(p for p in nuevo.rglob("*") if p.is_file()):
        rel = ruta.relative_to(nuevo)
        otro = viejo / rel
        if not otro.exists():
            out.append(f"falta en lo versionado: {rel}")
        elif not filecmp.cmp(ruta, otro, shallow=False):
            out.append(f"difiere: {rel}")
    if viejo.exists():
        for ruta in sorted(p for p in viejo.rglob("*") if p.is_file()):
            rel = ruta.relative_to(viejo)
            if not (nuevo / rel).exists():
                out.append(f"sobra en lo versionado: {rel}")
    return out


def huerfanas() -> list[str]:
    """Carpetas de `generado/` que no son de ningún módulo de clase `paquete` (p. ej., restos de la disposición anterior)."""
    validas = set(registro.ids("paquete"))
    return [f"sobra en generado/: {p.name} (no es de ningún módulo)" for p in sorted(GENERADO.iterdir()) if p.name not in validas]


def comparar(carpeta: Path, nombres: list[str]) -> list[str]:
    d: list[str] = []
    for n in nombres:
        d += [f"{n}/{x}" for x in diferencias(carpeta / n, destino_de(n))]
    return d


def copiar(carpeta: Path, nombres: list[str]) -> None:
    for n in nombres:
        origen, destino = carpeta / n, destino_de(n)
        if destino.exists():
            shutil.rmtree(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if origen.exists():
            shutil.copytree(origen, destino)


def empaquetar() -> int:
    """dist/: un .tar.gz por módulo de clase `paquete` (lo que hay en `generado/<id>/`), SHA256SUMS, notas de versión y
    ficha de la tienda."""
    tokens, marca = cargar()
    DIST.mkdir(exist_ok=True)
    sumas = []
    for id_ in registro.ids("paquete"):
        origen = GENERADO / id_
        if not origen.is_dir():
            print(f"  falta generado/{id_}: ejecuta herramientas/generar.py --aplicar"); return 1
        ruta = DIST / f"{marca['id']}-{id_}-{VERSION}.tar.gz"
        with tarfile.open(ruta, "w:gz") as tar:
            for sub in sorted(origen.iterdir()):
                tar.add(sub, arcname=sub.name)
        sumas.append(f"{hashlib.sha256(ruta.read_bytes()).hexdigest()}  {ruta.name}")
        print(f"  {ruta.relative_to(RAIZ)}")
    (DIST / "SHA256SUMS").write_text("\n".join(sorted(sumas, key=lambda s: s.split()[1])) + "\n", encoding="utf-8")
    cambios = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    ini = cambios.find(f"## [{VERSION}]")
    fin = cambios.find("\n## [", ini + 1) if ini >= 0 else -1
    notas = cambios[ini:fin if fin > 0 else None] if ini >= 0 else f"## [{VERSION}]\n"
    (DIST / f"NOTAS-{VERSION}.md").write_text(notas + f"\nComprobar: `sha256sum -c SHA256SUMS`. Sitio: {marca['sitio_tema']}\n", encoding="utf-8")
    (DIST / "FICHA-KDE-STORE.md").write_text(f"""# {marca['nombre']} {VERSION}

{marca['descripcion']}

Dos variantes, **{marca['nombre_esquema']['oscuro']}** (rojo de Nothing) y **{marca['nombre_esquema']['claro']}** (azul
de WhiteSur). Parte de WhiteSur-kde (estilo de Plasma, Kvantum, pantallas de carga, salida e inicio de sesión) y de la
decoración Aurorae de Nothing, con el acento de cada variante, Inter en la interfaz y JetBrains Mono Nerd Font como
monoespaciada; iconos Papirus con las carpetas en el acento.

- Sitio y guías: {marca['sitio_tema']}
- Código (Source): {marca['repositorio']}
- Licencia: código MIT, activos CC BY-SA 4.0, lo derivado de WhiteSur y Nothing GPL-3.0-or-later (REUSE 3.3)
- Requiere Plasma 6 (probado en 6.6); dependencias: WhiteSur-cursors, Papirus, Inter, JetBrains Mono Nerd Font
""", encoding="utf-8")
    print(f"  dist/SHA256SUMS · dist/NOTAS-{VERSION}.md · dist/FICHA-KDE-STORE.md")
    return 0
