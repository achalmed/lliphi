"""Aplicación en GIMP (decisiones 5.21): `gimprc` toma `(theme "<nombre>")` y `(theme-color-scheme system)`, para que
GIMP use el tema de Lliphi y cambie entre su variante clara y la oscura con el escritorio. Nada más de `gimprc` se
toca, y solo con GIMP cerrado: GIMP reescribe `gimprc` al salir y perdería el cambio. `gimprc` se respalda antes."""
from __future__ import annotations

import re
from pathlib import Path

VERSION_GIMP = "3.2"


def gimprc(config: Path) -> Path:
    return config / "GIMP" / VERSION_GIMP / "gimprc"


def fijar(texto: str, clave: str, valor: str) -> str:
    """Pone `(clave valor)` en el texto de un gimprc: sustituye la línea de esa clave o la añade al final."""
    linea = f"({clave} {valor})"
    patron = re.compile(rf"^\({re.escape(clave)} [^\n]*\)$", re.M)
    if patron.search(texto):
        return patron.sub(lambda _m: linea, texto, count=1)
    return texto.rstrip("\n") + "\n" + linea + "\n"


def respaldos(ctx) -> list:
    rc = gimprc(ctx.CONFIG)
    return [(rc, "reponer", f"gimprc de GIMP {VERSION_GIMP}")] if rc.exists() else []


def aplicar(ctx) -> int:
    if "gimp" not in ctx.modulos:
        return 0
    rc = gimprc(ctx.CONFIG)
    if not (rc.parent / "themes" / ctx.marca["nombre"]).is_dir():
        ctx.decir(f"GIMP: el tema no está en {rc.parent / 'themes'}; instala el módulo gimp")
        return 0
    if ctx.hay("pgrep") and ctx.ejecutar(["pgrep", "-x", f"gimp-{VERSION_GIMP}"]).returncode == 0:
        ctx.decir(f"GIMP está abierto: elige el tema «{ctx.marca['nombre']}» en Preferencias → Interfaz → Tema (o ciérralo y vuelve a aplicar)")
        return 0
    real = rc.resolve() if rc.exists() else rc
    antes = real.read_text(encoding="utf-8") if real.exists() else ""
    despues = fijar(fijar(antes, "theme", f'"{ctx.marca["nombre"]}"'), "theme-color-scheme", "system")
    if despues != antes:
        real.parent.mkdir(parents=True, exist_ok=True)
        real.write_text(despues, encoding="utf-8")
    ctx.decir(f"GIMP: tema «{ctx.marca['nombre']}» que sigue al escritorio (claro u oscuro) desde el próximo arranque")
    return 0
