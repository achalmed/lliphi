"""Tema de iconos de carpetas: hereda todo de Breeze y entrega solo las carpetas, dibujadas aquí, en el rojo de acento.

Dos temas freedesktop (Calibre 10531): `<id>` (hereda `breeze,hicolor`) y `<id>-oscuro` (hereda `breeze-dark,breeze,
hicolor`); se diferencian en la herencia y en los colores de respaldo del stylesheet. Cada SVG lleva
`<style id="current-color-scheme">` con `.ColorScheme-Highlight` (el acento: la carpeta), `.ColorScheme-HighlightedText`
(el texto sobre el acento: la solapa frontal y el distintivo) y `.ColorScheme-Text`, y rellena con `currentColor`;
`FollowsColorScheme=true` en `index.theme` hace que KIconLoader sustituya esos colores por los del esquema activo,
de modo que las carpetas siguen al acento del usuario. Fuera de KDE (GTK) se ven los colores de respaldo.

Tamaños 16, 22, 32, 48 (`Type=Fixed`) y 64 (`Type=Scalable` hasta 512, para las vistas grandes de Dolphin). Nombres:
`folder` y sus sinónimos, `folder-open`, y los lugares de uso común (`user-home`, `folder-documents`, descargas,
imágenes, música, vídeos, escritorio, plantillas, público, raíz, remoto) con un distintivo geométrico a partir de 22 px.
Toda la geometría se calcula del tamaño; ningún color se escribe aquí."""
from __future__ import annotations

from pathlib import Path

from . import escribir, semanticos

# nombre → (dibujo, distintivo); los sinónimos comparten dibujo y distintivo con su base
LUGARES: dict[str, tuple[str, str | None]] = {
    "folder": ("cerrada", None), "inode-directory": ("cerrada", None), "stock_folder": ("cerrada", None),
    "folder-open": ("abierta", None), "folder_open": ("abierta", None),
    "user-home": ("cerrada", "casa"),
    "folder-documents": ("cerrada", "documento"),
    "folder-download": ("cerrada", "flecha-abajo"), "folder-downloads": ("cerrada", "flecha-abajo"),
    "folder-pictures": ("cerrada", "imagen"), "folder-images": ("cerrada", "imagen"), "folder-image": ("cerrada", "imagen"), "folder-picture": ("cerrada", "imagen"),
    "folder-music": ("cerrada", "nota"), "folder-sound": ("cerrada", "nota"),
    "folder-videos": ("cerrada", "reproducir"), "folder-video": ("cerrada", "reproducir"),
    "folder-desktop": ("cerrada", "monitor"), "user-desktop": ("cerrada", "monitor"),
    "folder-templates": ("cerrada", "plantilla"),
    "folder-publicshare": ("cerrada", "compartir"), "folder-public": ("cerrada", "compartir"),
    "folder-root": ("cerrada", "raiz"),
    "folder-remote": ("cerrada", "red"), "folder-network": ("cerrada", "red"),
}
TAMANOS = (16, 22, 32, 48, 64)
ESCALABLE_HASTA = 512


def _f(x: float) -> str:
    """Número corto para el atributo d: entero si lo es, si no con un decimal."""
    return str(int(x)) if float(x).is_integer() else f"{x:.1f}"


def geometria(S: int) -> dict[str, float]:
    """Medidas de la carpeta para un tamaño S, alineadas al píxel en los tamaños pequeños."""
    m = {16: 1, 22: 1, 32: 2, 48: 3, 64: 4}[S]
    r = {16: 1, 22: 1.5, 32: 2, 48: 3, 64: 4}[S]
    yt = round(S * 0.19)           # borde superior de la pestaña
    th = round(S * 0.12)           # alto de la pestaña
    yb = yt + th                   # borde superior del cuerpo
    yf = round(S * 0.45)           # borde superior de la solapa frontal
    y1 = S - m - round(S * 0.06)   # borde inferior
    tw = round(S * 0.40)           # ancho de la pestaña
    return {"S": S, "m": m, "r": r, "yt": yt, "th": th, "yb": yb, "yf": yf, "y1": y1, "tw": tw, "x1": S - m}


def cuerpo(g: dict[str, float]) -> str:
    """Trayectoria del cuerpo con la pestaña (esquinas exteriores redondeadas, borde derecho de la pestaña en diagonal)."""
    m, r, yt, th, yb, y1, tw, x1 = g["m"], g["r"], g["yt"], g["th"], g["yb"], g["y1"], g["tw"], g["x1"]
    f = _f
    return (f"M{f(m)},{f(yt + r)} Q{f(m)},{f(yt)} {f(m + r)},{f(yt)} H{f(m + tw - r)} Q{f(m + tw)},{f(yt)} {f(m + tw + r * 0.6)},{f(yt + r * 0.6)} "
            f"L{f(m + tw + th)},{f(yb)} H{f(x1 - r)} Q{f(x1)},{f(yb)} {f(x1)},{f(yb + r)} V{f(y1 - r)} Q{f(x1)},{f(y1)} {f(x1 - r)},{f(y1)} "
            f"H{f(m + r)} Q{f(m)},{f(y1)} {f(m)},{f(y1 - r)} Z")


def solapa_cerrada(g: dict[str, float]) -> str:
    m, r, yf, y1, x1 = g["m"], g["r"], g["yf"], g["y1"], g["x1"]
    f = _f
    return (f"M{f(m)},{f(yf)} H{f(x1)} V{f(y1 - r)} Q{f(x1)},{f(y1)} {f(x1 - r)},{f(y1)} H{f(m + r)} Q{f(m)},{f(y1)} {f(m)},{f(y1 - r)} Z")


def solapa_abierta(g: dict[str, float]) -> str:
    """Solapa inclinada: el borde superior empieza más a la derecha y el inferior llega hasta el borde izquierdo."""
    m, r, yf, y1, x1, S = g["m"], g["r"], g["yf"], g["y1"], g["x1"], g["S"]
    sk = round(S * 0.14)
    f = _f
    return (f"M{f(m + sk)},{f(yf)} H{f(x1)} V{f(y1 - r)} Q{f(x1)},{f(y1)} {f(x1 - r)},{f(y1)} H{f(m + r)} Q{f(m)},{f(y1)} {f(m)},{f(y1 - r)} Z")


def distintivo(nombre: str, g: dict[str, float]) -> str:
    """Glifo geométrico centrado en la solapa; `fill`/`stroke` con currentColor (clase HighlightedText en el grupo).
    Devuelve elementos SVG; vacío si el tamaño es demasiado pequeño."""
    S, yf, y1 = g["S"], g["yf"], g["y1"]
    if S < 22:
        return ""
    alto = y1 - yf
    a = round(alto * 0.62)          # lado del cuadro del glifo
    cx, cy = S / 2, yf + alto / 2 + (0.5 if S == 22 else 0)
    x0, y0 = cx - a / 2, cy - a / 2
    w = max(1, round(S / 22))       # grosor de trazo
    f = _f
    sw = f'fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'
    if nombre == "casa":
        return (f'<path d="M{f(cx)},{f(y0)} L{f(x0)},{f(y0 + a * 0.45)} V{f(y0 + a)} H{f(x0 + a)} V{f(y0 + a * 0.45)} Z" fill="currentColor"/>')
    if nombre == "documento":
        d = a * 0.28
        return (f'<path d="M{f(x0 + a * 0.15)},{f(y0)} H{f(x0 + a * 0.85 - d)} L{f(x0 + a * 0.85)},{f(y0 + d)} V{f(y0 + a)} H{f(x0 + a * 0.15)} Z" fill="currentColor"/>')
    if nombre == "flecha-abajo":
        return (f'<path d="M{f(cx - a * 0.18)},{f(y0)} H{f(cx + a * 0.18)} V{f(y0 + a * 0.5)} H{f(x0 + a)} L{f(cx)},{f(y0 + a)} L{f(x0)},{f(y0 + a * 0.5)} H{f(cx - a * 0.18)} Z" fill="currentColor"/>')
    if nombre == "imagen":
        return (f'<path d="M{f(x0)},{f(y0 + a)} L{f(x0 + a * 0.38)},{f(y0 + a * 0.4)} L{f(x0 + a * 0.62)},{f(y0 + a * 0.75)} L{f(x0 + a * 0.76)},{f(y0 + a * 0.58)} L{f(x0 + a)},{f(y0 + a)} Z" fill="currentColor"/>'
                f'<circle cx="{f(x0 + a * 0.78)}" cy="{f(y0 + a * 0.22)}" r="{f(max(a * 0.14, 1))}" fill="currentColor"/>')
    if nombre == "nota":
        rr = a * 0.24
        return (f'<circle cx="{f(x0 + rr)}" cy="{f(y0 + a - rr)}" r="{f(rr)}" fill="currentColor"/>'
                f'<path d="M{f(x0 + 2 * rr - w / 2)},{f(y0 + a - rr)} V{f(y0)} H{f(x0 + a)} V{f(y0 + a * 0.3)} H{f(x0 + 2 * rr + w / 2)}" fill="currentColor"/>')
    if nombre == "reproducir":
        return (f'<path d="M{f(x0 + a * 0.2)},{f(y0)} L{f(x0 + a)},{f(cy)} L{f(x0 + a * 0.2)},{f(y0 + a)} Z" fill="currentColor"/>')
    if nombre == "monitor":
        return (f'<path d="M{f(x0)},{f(y0)} H{f(x0 + a)} V{f(y0 + a * 0.68)} H{f(x0)} Z M{f(cx - a * 0.3)},{f(y0 + a - w)} H{f(cx + a * 0.3)} V{f(y0 + a)} H{f(cx - a * 0.3)} Z" fill="currentColor"/>')
    if nombre == "plantilla":
        return (f'<rect x="{f(x0 + w / 2)}" y="{f(y0 + w / 2)}" width="{f(a - w)}" height="{f(a - w)}" {sw} stroke-dasharray="{f(max(w * 1.5, 1.5))} {f(max(w * 1.2, 1.2))}"/>')
    if nombre == "compartir":
        rr = max(a * 0.16, 1)
        return (f'<circle cx="{f(x0 + rr)}" cy="{f(cy)}" r="{f(rr)}" fill="currentColor"/>'
                f'<circle cx="{f(x0 + a - rr)}" cy="{f(y0 + rr)}" r="{f(rr)}" fill="currentColor"/>'
                f'<circle cx="{f(x0 + a - rr)}" cy="{f(y0 + a - rr)}" r="{f(rr)}" fill="currentColor"/>'
                f'<path d="M{f(x0 + rr)},{f(cy)} L{f(x0 + a - rr)},{f(y0 + rr)} M{f(x0 + rr)},{f(cy)} L{f(x0 + a - rr)},{f(y0 + a - rr)}" {sw}/>')
    if nombre == "raiz":
        return (f'<path d="M{f(cx)},{f(y0)} L{f(x0 + a)},{f(y0 + a * 0.25)} V{f(y0 + a * 0.75)} L{f(cx)},{f(y0 + a)} L{f(x0)},{f(y0 + a * 0.75)} V{f(y0 + a * 0.25)} Z" fill="currentColor"/>')
    if nombre == "red":
        rr = a / 2 - w / 2
        return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rr)}" {sw}/>'
                f'<path d="M{f(cx - rr)},{f(cy)} H{f(cx + rr)} M{f(cx)},{f(cy - rr)} V{f(cy + rr)}" {sw}/>'
                f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rr * 0.45)}" ry="{f(rr)}" {sw}/>')
    raise ValueError(nombre)


def svg_carpeta(S: int, dibujo: str, badge: str | None, colores: dict[str, str]) -> str:
    g = geometria(S)
    solapa = solapa_abierta(g) if dibujo == "abierta" else solapa_cerrada(g)
    glifo = distintivo(badge, g) if badge else ""
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<!-- GENERADO por herramientas/generar.py desde tokens/; no editar -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">\n'
            f'  <defs>\n    <style id="current-color-scheme" type="text/css">\n'
            f'      .ColorScheme-Text {{ color:{colores["texto"]}; }}\n'
            f'      .ColorScheme-Highlight {{ color:{colores["acento"]}; }}\n'
            f'      .ColorScheme-HighlightedText {{ color:{colores["sobre-acento"]}; }}\n'
            f'    </style>\n  </defs>\n'
            f'  <path id="cuerpo" class="ColorScheme-Highlight" fill="currentColor" d="{cuerpo(g)}"/>\n'
            f'  <path id="solapa" class="ColorScheme-HighlightedText" fill="currentColor" fill-opacity="0.22" d="{solapa}"/>\n'
            + (f'  <g id="distintivo" class="ColorScheme-HighlightedText" fill="currentColor" fill-opacity="0.95">{glifo}</g>\n' if glifo else "")
            + "</svg>\n")


def index_theme(marca: dict, variante: str) -> str:
    nombre = marca["nombre"] if variante == "claro" else marca["nombre_esquema"]["oscuro"]
    hereda = "breeze,hicolor" if variante == "claro" else "breeze-dark,breeze,hicolor"
    lineas = ["# GENERADO por herramientas/generar.py desde tokens/; no editar", "[Icon Theme]", f"Name={nombre}",
              f"Comment=Carpetas de {marca['nombre']} en el color de acento; todo lo demás, de Breeze", f"Inherits={hereda}",
              "Example=folder", "FollowsColorScheme=true", "DisplayDepth=32",
              "Directories=" + ",".join(f"places/{S}" for S in TAMANOS), ""]
    for S in TAMANOS:
        lineas += [f"[places/{S}]", f"Size={S}", "Context=Places"]
        if S == TAMANOS[-1]:
            lineas += ["Type=Scalable", f"MinSize={S}", f"MaxSize={ESCALABLE_HASTA}"]
        else:
            lineas += ["Type=Fixed"]
        lineas.append("")
    return "\n".join(lineas)


def id_tema(marca: dict, variante: str) -> str:
    return marca["id"] if variante == "claro" else f"{marca['id']}-oscuro"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        s = semanticos(tokens, variante)
        colores = {"texto": s["texto.normal"], "acento": s["acento.base"], "sobre-acento": s["texto.sobre-acento"]}
        base = destino / "icons" / id_tema(marca, variante)
        escribir(base / "index.theme", index_theme(marca, variante), hechos)
        for S in TAMANOS:
            for nombre, (dibujo, badge) in LUGARES.items():
                escribir(base / "places" / str(S) / f"{nombre}.svg", svg_carpeta(S, dibujo, badge, colores), hechos)
    return hechos
