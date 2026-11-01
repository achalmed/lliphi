"""Aplicación del bloqueo de pantalla (mejora 10, decisiones 4.16): el bloqueo de Plasma escribe siempre en blanco; con
el fondo claro el reloj no se lee. En las dos variantes el bloqueo usa la imagen oscura de Lliphi (como el inicio de
sesión SDDM), escrita en `kscreenlockerrc` (respaldado por el tema global). La pantalla de carga no se aplica aquí: la
elige `[KSplash] Theme` del tema global."""
from __future__ import annotations


def aplicar(ctx) -> int:
    oscura = ctx.DATA / "wallpapers" / ctx.marca["id_fondo"] / "contents" / "images_dark" / "3840x2160.png"
    if "fondos" in ctx.modulos and oscura.exists() and ctx.hay("kwriteconfig6"):
        for clave in ("Image", "PreviewImage"):
            ctx.kwrite("kscreenlockerrc", ["Greeter", "Wallpaper", "org.kde.image", "General"], clave, oscura.as_uri())
        ctx.decir("bloqueo de pantalla: fondo oscuro de Lliphi")
    return 0
