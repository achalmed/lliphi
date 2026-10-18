"""Paquete de fondo de pantalla de Plasma: composición original generada desde los tokens.

Estructura (Calibre 10529; `/usr/share/wallpapers/Next`): `metadata.json` (`KPlugin` con `Id`, `Name`,
`License`, `Authors`; `X-KDE-PlasmaImageWallpaper-AccentColor` con `{Light, Dark}`), `contents/images/
<AnchoxAlto>.png` (variante clara) e `contents/images_dark/` (oscura, Plasma ≥ 6.6), `contents/screenshot.png`.

La imagen es un degradado suave de dos neutros de la variante con una franja diagonal del acento a baja
opacidad: sobria, sin texto ni logotipo. Requiere Pillow; sin él, el destino se omite con aviso."""
from __future__ import annotations

import json
from pathlib import Path

from . import VERSION, autores, semanticos

TAMANOS = ((1920, 1080), (2560, 1440), (3840, 2160))


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def imagen(t: dict[str, str], ancho: int, alto: int, variante: str):
    from PIL import Image, ImageDraw, ImageFilter
    a, b = _hex(t["fondo.vista"]), _hex(t["fondo.ventana-alterno"])
    if variante == "claro":
        a, b = _hex(t["fondo.ventana"]), _hex(t["fondo.vista"])
    # degradado diagonal base (dibujado pequeño y escalado: rápido y determinista)
    w, h = 192, 108
    base = Image.new("RGB", (w, h))
    px = base.load()
    for y in range(h):
        for x in range(w):
            k = (x / w * 0.6 + y / h * 0.4)
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))
    base = base.resize((ancho, alto), Image.BICUBIC)
    # franja diagonal del acento, muy tenue, desenfocada
    capa = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ac = _hex(t["acento.base"])
    alfa = 34 if variante == "oscuro" else 26
    d.polygon([(ancho * 0.58, 0), (ancho * 0.78, 0), (ancho * 0.30, alto), (ancho * 0.10, alto)], fill=(*ac, alfa))
    d.polygon([(ancho * 0.84, 0), (ancho * 0.90, 0), (ancho * 0.42, alto), (ancho * 0.36, alto)], fill=(*ac, alfa // 2))
    capa = capa.filter(ImageFilter.GaussianBlur(ancho // 48))
    base = Image.alpha_composite(base.convert("RGBA"), capa).convert("RGB")
    return base


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("  aviso: sin Pillow no se generan los fondos (pip install pillow)")
        return []
    hechos: list[Path] = []
    base = destino / "wallpapers" / marca["id_fondo"]
    claro, oscuro = semanticos(tokens, "claro"), semanticos(tokens, "oscuro")
    meta = {"KPlugin": {"Authors": autores(marca), "Id": marca["id_fondo"], "License": marca["licencia_activos"],
                        "Name": marca["nombre_fondo"], "Version": VERSION},
            "X-KDE-PlasmaImageWallpaper-AccentColor": {"Light": claro["acento.base"], "Dark": oscuro["acento.base"]}}
    base.mkdir(parents=True, exist_ok=True)
    (base / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    hechos.append(base / "metadata.json")
    for carpeta, t, variante in (("images", claro, "claro"), ("images_dark", oscuro, "oscuro")):
        for ancho, alto in TAMANOS:
            ruta = base / "contents" / carpeta / f"{ancho}x{alto}.png"
            ruta.parent.mkdir(parents=True, exist_ok=True)
            imagen(t, ancho, alto, variante).save(ruta, optimize=True)
            hechos.append(ruta)
    captura = base / "contents" / "screenshot.png"
    imagen(oscuro, 480, 270, "oscuro").save(captura, optimize=True)
    hechos.append(captura)
    return hechos
