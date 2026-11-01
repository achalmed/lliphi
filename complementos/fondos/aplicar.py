"""Aplicación del fondo por ruta (Plasma 6.6 no resuelve el nombre del paquete de usuario; docs/validacion.md §3)."""
from __future__ import annotations


def aplicar(ctx) -> int:
    fondo = ctx.DATA / "wallpapers" / ctx.marca["id_fondo"]
    if ctx.variante == "claro":
        # mejora 10 (decisiones 4.16): con el paquete, Plasma elige la imagen clara u oscura por los colores del
        # estilo de Plasma, y el de WhiteSur claro tiene el panel oscuro: saldría el fondo oscuro. Se fija la clara.
        fondo = fondo / "contents" / "images" / "3840x2160.png"
    if "fondos" in ctx.modulos and fondo.exists() and ctx.hay("plasma-apply-wallpaperimage"):
        ctx.ejecutar(["plasma-apply-wallpaperimage", str(fondo)])
        ctx.decir(f"fondo aplicado: {fondo}")
    return 0
