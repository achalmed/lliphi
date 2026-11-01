"""Aplicación del fondo por ruta (Plasma 6.6 no resuelve el nombre del paquete de usuario; docs/validacion.md §3).

El fondo del escritorio es `fondo_escritorio` de la marca («Lliphi Relámpago · @achalmaedison», decisiones 4.27); el
de `id_fondo` (Horizonte) sigue siendo la imagen del bloqueo y del inicio de sesión."""
from __future__ import annotations


def aplicar(ctx) -> int:
    paquete = ctx.DATA / "wallpapers" / ctx.marca.get("fondo_escritorio", ctx.marca["id_fondo"])
    if not paquete.exists():
        paquete = ctx.DATA / "wallpapers" / ctx.marca["id_fondo"]
    # la imagen de la variante por ruta, no el paquete: con el paquete Plasma elige por los colores del estilo de Plasma,
    # que no siempre son los de la variante (hasta 4.32 el claro declaraba el panel oscuro y salía la imagen oscura: 4.16)
    carpeta = paquete / "contents" / ("images" if ctx.variante == "claro" else "images_dark")
    imagenes = sorted(carpeta.glob("*x*.*"), key=lambda p: [int(n) for n in p.stem.split("x")]) if carpeta.is_dir() else []
    fondo = imagenes[-1] if imagenes else paquete
    if "fondos" in ctx.modulos and fondo.exists() and ctx.hay("plasma-apply-wallpaperimage"):
        ctx.ejecutar(["plasma-apply-wallpaperimage", str(fondo)])
        ctx.decir(f"fondo aplicado: {fondo}")
    return 0
