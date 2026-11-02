"""Aplicación en Xournal++ (decisiones 5.20): en `settings.xml`, la paleta de bolígrafos de Lliphi y los colores de
alrededor de las páginas, de la selección y del recoloreado; nada más, y solo con Xournal++ cerrado, porque lo
reescribe al salir. Se edita el archivo real: si `settings.xml` es un enlace (dotfiles con stow), el enlace se conserva
y el cambio queda en los dotfiles. `settings.xml` se respalda antes de instalar."""
from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import quoteattr


def settings(config: Path) -> Path:
    return config / "xournalpp" / "settings.xml"


def fijar_propiedades(texto: str, valores: dict[str, str]) -> str:
    """Sustituye el `value` de cada `<property name="…">` o, si falta, la añade antes de `</settings>`."""
    for nombre, valor in valores.items():
        patron = re.compile(rf'(<property name="{re.escape(nombre)}" value=)"[^"]*"(\s*/>)')
        if patron.search(texto):
            texto = patron.sub(lambda m: m.group(1) + quoteattr(valor) + m.group(2), texto, count=1)
        else:
            texto = texto.replace("</settings>", f"  <property name={quoteattr(nombre)} value={quoteattr(valor)}/>\n</settings>", 1)
    return texto


def respaldos(ctx) -> list:
    s = settings(ctx.CONFIG)
    return [(s, "reponer", "settings.xml de Xournal++")] if s.exists() else []


def aplicar(ctx) -> int:
    if "xournalpp" not in ctx.modulos:
        return 0
    s = settings(ctx.CONFIG)
    paleta = ctx.CONFIG / "xournalpp" / "palettes" / f"{ctx.marca['nombre']}.gpl"
    if not paleta.exists():
        ctx.decir("Xournal++: falta la paleta; instala el módulo xournalpp")
        return 0
    if not s.exists():
        ctx.decir("Xournal++: sin settings.xml (ábrelo una vez); la paleta ya está en Preferencias → Paleta")
        return 0
    if ctx.hay("pgrep") and ctx.ejecutar(["pgrep", "-x", "xournalpp"]).returncode == 0:
        ctx.decir("Xournal++ está abierto: elige la paleta en Preferencias (o ciérralo y vuelve a aplicar)")
        return 0
    real = s.resolve()
    antes = real.read_text(encoding="utf-8")
    despues = fijar_propiedades(antes, ctx.codigo("xournalpp").propiedades(ctx.tokens, str(paleta)))
    if despues != antes:
        real.write_text(despues, encoding="utf-8")
    ctx.decir(f"Xournal++: paleta {paleta.name} y colores de {ctx.marca['nombre']} en settings.xml"
              + (" (enlace a los dotfiles: el cambio queda allí)" if s.is_symlink() else ""))
    return 0
