"""Aplicación de los iconos (mejora 3 y decisiones 4.15): carpetas en el acento de la variante; el oscuro usa el
superpuesto rojo Papirus-Dark-Lliphi (`externas.py`) y el claro Papirus tal cual (azul); si faltan, Papirus-Dark y
después Breeze. Los cursores los aplica el tema global por `[kcminputrc][Mouse]`."""
from __future__ import annotations


def aplicar(ctx) -> int:
    iconos = ctx.codigo("iconos-cursores").ICONOS[ctx.variante]
    if iconos == "Papirus-Dark-Lliphi" and not (ctx.DATA / "icons" / iconos).exists():
        iconos = "Papirus-Dark"
    if not (ctx.DATA / "icons" / iconos).exists():
        ctx.decir(f"{iconos} no está en {ctx.DATA / 'icons'} (ejecuta herramientas/instalar.py dependencias --aplicar); se usa Breeze")
        iconos = "breeze-dark" if ctx.variante == "oscuro" else "breeze"
    if (ctx.DATA / "icons" / iconos).exists():
        if ctx.hay("plasma-changeicons"):
            ctx.ejecutar(["plasma-changeicons", iconos])
        elif ctx.kwrite("kdeglobals", ["Icons"], "Theme", iconos):
            ctx.ejecutar(["dbus-send", "--session", "--type=signal", "/KIconLoader", "org.kde.KIconLoader.iconChanged", "int32:0"])
        ctx.decir(f"iconos aplicados: {iconos}")
    return 0
