"""Aplicación en GTK (decisiones 4.37): `gtk.css` de GTK 3 importa la hoja de la variante y el de GTK 4 la hoja única,
siempre después de `colors.css` (la de kde-gtk-config), para mandar sobre ella; lo demás de `gtk.css` no se toca. Y la
preferencia `color-scheme` de GSettings, para lo que la lea de ahí y no del portal. Los dos `gtk.css` se respaldan
antes de instalar; `color-scheme` no entra en `UNDO.sh` (se devuelve con `gsettings reset`, ver INSTALL.md)."""
from __future__ import annotations

import re
from pathlib import Path


def importacion(id_: str, version: int, variante: str) -> str:
    return f"{id_}-{variante}.css" if version == 3 else f"{id_}.css"


def fijar_importacion(gtk_css: Path, id_: str, hoja: str) -> bool:
    """Deja en `gtk_css` una sola línea `@import '<hoja>';` de Lliphi, detrás de las demás importaciones (y de la de
    `colors.css` si existe ese archivo y faltaba la línea: kde-gtk-config la añade al final y quedaría detrás de la
    nuestra). Devuelve True si cambió algo. Se escribe el archivo real (un enlace de dotfiles sigue siendo enlace)."""
    real = gtk_css.resolve() if gtk_css.exists() else gtk_css
    antes = real.read_text(encoding="utf-8") if real.exists() else ""
    propia = re.compile(rf"^\s*@import\s+(url\()?['\"]{re.escape(id_)}(-claro|-oscuro)?\.css['\"]\)?;\s*$")
    lineas = [ln for ln in antes.splitlines() if not propia.match(ln)]
    if (gtk_css.parent / "colors.css").exists() and not any("colors.css" in ln and ln.lstrip().startswith("@import") for ln in lineas):
        lineas.insert(0, "@import 'colors.css';")
    ultima = max((i for i, ln in enumerate(lineas) if ln.lstrip().startswith("@import")), default=-1)
    lineas.insert(ultima + 1, f"@import '{hoja}';")
    despues = "\n".join(lineas) + "\n"
    if despues == antes:
        return False
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(despues, encoding="utf-8")
    return True


def respaldos(ctx) -> list:
    return [(ctx.CONFIG / f"gtk-{v}.0" / "gtk.css", "reponer", f"gtk.css de GTK {v}") for v in (3, 4)
            if (ctx.CONFIG / f"gtk-{v}.0" / "gtk.css").exists()]


def aplicar(ctx) -> int:
    if "gtk" not in ctx.modulos:
        return 0
    id_ = ctx.marca["id"]
    for v in (3, 4):
        hoja = importacion(id_, v, ctx.variante)
        if not (ctx.CONFIG / f"gtk-{v}.0" / hoja).exists():
            ctx.decir(f"GTK {v}: falta {hoja} en {ctx.CONFIG / f'gtk-{v}.0'}; instala el módulo gtk")
            continue
        cambio = fijar_importacion(ctx.CONFIG / f"gtk-{v}.0" / "gtk.css", id_, hoja)
        ctx.decir(f"GTK {v}: gtk.css importa {hoja}" + ("" if cambio else " (ya lo hacía)") + " (aplicaciones nuevas)")
    if ctx.hay("gsettings"):
        valor = "prefer-dark" if ctx.variante == "oscuro" else "prefer-light"
        ctx.ejecutar(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", valor])
        ctx.decir(f"GTK: color-scheme = {valor} (GSettings; el portal de KDE ya lo da a GTK 4 y libadwaita)")
    return 0
