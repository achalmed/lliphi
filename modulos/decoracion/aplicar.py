"""Aplicación de la decoración: `plasma-apply-lookandfeel` no siempre escribe el grupo [org.kde.kdecoration2] de los
defaults (comprobado en sesión anidada, docs/validacion.md §6); se escribe aquí y se avisa a KWin."""
from __future__ import annotations


def aplicar(ctx) -> int:
    if "decoracion" not in ctx.modulos:
        return 0
    construir = ctx.codigo("decoracion")
    deco = construir.id_tema(ctx.marca, ctx.variante)
    if (ctx.DATA / "aurorae" / "themes" / deco).exists() and ctx.hay("kwriteconfig6"):
        for grupo, claves in construir.valores(ctx.marca, ctx.variante).items():
            for clave, valor in claves.items():
                ctx.kwrite("kwinrc", [grupo.split("][")[1]], clave, valor)
        if ctx.hay("qdbus6"):
            ctx.ejecutar(["qdbus6", "org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"])
        ctx.decir(f"decoración aplicada: __aurorae__svg__{deco}")
    return 0
