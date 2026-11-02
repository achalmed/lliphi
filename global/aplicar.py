"""Aplicación del tema global en la sesión (`instalar.py --aplicar --aplicar-tema claro|oscuro`) y lo que hay que
respaldar antes de instalar. Lo llama `herramientas/nucleo/instalacion.py` antes que a los demás módulos: si
`plasma-apply-lookandfeel` falla, no se aplica nada más."""
from __future__ import annotations

# archivos de configuración que Plasma reescribe al aplicar un tema global: se respaldan siempre
CONFIGS = ["kdeglobals", "plasmarc", "kwinrc", "kcminputrc", "ksplashrc", "kscreenlockerrc",
           "plasma-org.kde.plasma.desktop-appletsrc", "gtk-3.0/settings.ini", "gtk-4.0/settings.ini",
           "konsolerc", "breezerc"]


def respaldos(ctx) -> list:
    return [(ctx.CONFIG / rel, "reponer", rel) for rel in CONFIGS]


def aplicar(ctx) -> int:
    id_global = ctx.marca["id_global"][ctx.variante]
    r = ctx.ejecutar(["plasma-apply-lookandfeel", "-a", id_global], mostrar=True)
    ctx.decir((r.stdout + r.stderr).strip()[-300:])
    if r.returncode:
        return 1
    # menús translúcidos con desenfoque en las aplicaciones Qt (función de serie de Breeze): el vidrio llega a las apps
    opacidad_menus = ctx.tokens.get("efectos", {}).get("opacidad-menus-qt", {}).get("$value", 80)
    if ctx.kwrite("breezerc", ["Style"], "MenuOpacity", str(opacidad_menus)):
        ctx.decir(f"menús de Breeze al {opacidad_menus} % (breezerc, respaldado)")
    tipografia(ctx)
    return 0


def tipografia(ctx) -> None:
    """Inter y JetBrains Mono (Nerd Font) en toda la sesión: lo que fija `defaults` solo lo lee el KCM al aplicar el
    tema. Con la misma familia ya puesta (en formato de Qt 6), el tamaño y el peso son del usuario (decisiones 5.46)."""
    if not ctx.hay("kwriteconfig6"):
        return
    fuentes = ctx.codigo("global").valores(ctx.marca, ctx.variante)
    respetadas = 0
    for grupo, claves in fuentes.items():
        for clave, valor in claves.items():
            actual = ctx.ejecutar(["kreadconfig6", "--file", "kdeglobals", "--group", grupo.split("][")[1],
                                   "--key", clave]).stdout.strip()
            # con la misma familia ya puesta, el tamaño y el peso son elección del usuario: no se tocan; salvo en el
            # formato de Qt 5 (menos de 16 campos), que Qt 6 lee en negrita, el que escribía Lliphi hasta 5.46
            if actual.split(",")[0] == valor.split(",")[0] and len(actual.split(",")) >= 16:
                respetadas += 1
                continue
            ctx.kwrite("kdeglobals", [grupo.split("][")[1]], clave, valor)
    # sin esta señal KWin y las aplicaciones abiertas siguen con la fuente anterior hasta reiniciar la sesión:
    # es la que emite el módulo de Tipografías (plasma-integration la escucha); notifyChange 1 = FontChanged
    ctx.ejecutar(["dbus-send", "--session", "--type=signal", "/KDEPlatformTheme", "org.kde.KDEPlatformTheme.refreshFonts"])
    ctx.ejecutar(["dbus-send", "--session", "--type=signal", "/KGlobalSettings", "org.kde.KGlobalSettings.notifyChange", "int32:1", "int32:0"])
    ctx.decir("tipografía: Inter 10 (interfaz), Inter Medium 10 (títulos) y JetBrainsMono Nerd Font 10 (monoespaciada), recargada en vivo"
              + (f"; {respetadas} con la familia ya puesta, sin tocar su tamaño ni su peso" if respetadas else ""))
