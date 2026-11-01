"""Aplicación de los iconos (decisiones 4.22 y 4.35): el superpuesto de la bandeja del tema de la variante
(`Colloid-Grey-Light-Lliphi` en el claro, `Colloid-Grey-Dark-Lliphi` en el oscuro), que se construye aquí desde el tema
instalado; si no se puede, el tema tal cual; si no está instalado, su reserva (Papirus en el claro, el superpuesto rojo Papirus-Dark-Lliphi o
Papirus-Dark en el oscuro) y, si tampoco, Breeze. Los cursores los aplica el tema global por `[kcminputrc][Mouse]`."""
from __future__ import annotations

from pathlib import Path


def _hay(ctx, tema: str) -> bool:
    return any((d / tema / "index.theme").exists() for d in (ctx.DATA / "icons", Path.home() / ".icons", Path("/usr/share/icons")))


def aplicar(ctx) -> int:
    mod = ctx.codigo("iconos-cursores")
    try:
        ctx.codigo("iconos-cursores", "externas").bandeja(True, silencio=True)   # el superpuesto de la bandeja (4.35)
    except OSError as e:
        ctx.decir(f"no se pudo construir el superpuesto de la bandeja ({e}); se usa el tema tal cual")
    candidatos = [mod.tema(ctx.variante), mod.ICONOS[ctx.variante], mod.RESERVA.get(ctx.variante)]
    candidatos += ["Papirus-Dark" if ctx.variante == "oscuro" else "Papirus", "breeze-dark" if ctx.variante == "oscuro" else "breeze"]
    iconos = next((t for t in candidatos if t and _hay(ctx, t)), None)
    if iconos is None:
        ctx.decir("no hay ningún tema de iconos de la lista; se deja el actual")
        return 0
    if iconos not in (mod.tema(ctx.variante), mod.ICONOS[ctx.variante]):
        ctx.decir(f"{mod.ICONOS[ctx.variante]} no está instalado (instalar.py dependencias dice cómo); se usa {iconos}")
    if ctx.hay("plasma-changeicons"):
        ctx.ejecutar(["plasma-changeicons", iconos])
    elif ctx.kwrite("kdeglobals", ["Icons"], "Theme", iconos):
        ctx.ejecutar(["dbus-send", "--session", "--type=signal", "/KIconLoader", "org.kde.KIconLoader.iconChanged", "int32:0"])
    ctx.decir(f"iconos aplicados: {iconos}")
    return 0
