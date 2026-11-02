"""studio/lliphi_app/servicios/color.py — color sin Qt ni coloraide (heredado de 1.x): OKLCH → sRGB (para pintar las muestras mientras se mueve un deslizador), contraste WCAG,
simulación de daltonismo y dónde aparece un color en lo generado.

Las cifras oficiales (el hex ajustado a la gama y la razón de cada par) las da `paleta.py --ajustes <borrador> --json`
con coloraide; aquí la conversión es la de Björn Ottosson y el ajuste a la gama reduce el croma con L y H fijos (el
método de CSS Color 4), así que puede diferir en una unidad de un canal.
"""
from __future__ import annotations

import math
import re
from pathlib import Path


def _oklab_a_lineal(l: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3,
            -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3,
            -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3)


def _gamma(x: float) -> float:
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def _lineal(x: float) -> float:
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def oklch_lineal(l: float, c: float, h: float) -> tuple[float, float, float]:
    rad = math.radians(h)
    return _oklab_a_lineal(l, c * math.cos(rad), c * math.sin(rad))


def en_gama(l: float, c: float, h: float, eps: float = 1e-4) -> bool:
    return all(-eps <= v <= 1 + eps for v in oklch_lineal(l, c, h))


def ajustar(l: float, c: float, h: float) -> tuple[float, float, float]:
    """El color dentro de sRGB: si se sale, baja el croma (búsqueda binaria) con la misma L y el mismo matiz."""
    if en_gama(l, c, h):
        return l, c, h
    bajo, alto = 0.0, c
    for _ in range(24):
        medio = (bajo + alto) / 2
        bajo, alto = (medio, alto) if en_gama(l, medio, h) else (bajo, medio)
    return l, bajo, h


def oklch_a_rgb(l: float, c: float, h: float) -> tuple[int, int, int]:
    l, c, h = ajustar(max(0.0, min(1.0, l)), max(0.0, c), h)
    return tuple(round(max(0.0, min(1.0, _gamma(max(0.0, min(1.0, v))))) * 255) for v in oklch_lineal(l, c, h))


def hexa(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def oklch_a_hex(l: float, c: float, h: float) -> str:
    return hexa(oklch_a_rgb(l, c, h))


def de_hex(hex_: str) -> tuple[int, int, int]:
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_lineal(v / 255) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(de_hex(a)), luminancia(de_hex(b))), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Machado, Oliveira y Fernandes (2009), severidad 1, en RGB lineal
DALTONISMO = {
    "protanopía": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopía": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopía": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def simular(hex_: str, tipo: str | None) -> str:
    """Cómo ve el color una persona con esa forma de daltonismo (o el mismo, si tipo es None o «normal»)."""
    if not tipo or tipo not in DALTONISMO:
        return hex_
    lin = [_lineal(v / 255) for v in de_hex(hex_)]
    salida = [sum(f[i] * lin[i] for i in range(3)) for f in DALTONISMO[tipo]]
    return hexa(tuple(round(max(0.0, min(1.0, _gamma(max(0.0, min(1.0, v))))) * 255) for v in salida))


def usos(raiz_generado: Path, hex_: str) -> dict[str, list[str]]:
    """Los archivos de texto de `generado/` que contienen el color (como #rrggbb o como r,g,b), por módulo."""
    r, g, b = de_hex(hex_)
    patron = re.compile(rf"{re.escape(hex_.lower())}\b|(?<![\d]){r}, ?{g}, ?{b}(?![\d])", re.I)
    salida: dict[str, list[str]] = {}
    for p in sorted(raiz_generado.rglob("*")):
        if not p.is_file() or p.suffix.lower() in (".png", ".jpg", ".oxt", ".gz", ".soc") or p.stat().st_size > 2_000_000:
            continue
        try:
            texto = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if patron.search(texto):
            rel = p.relative_to(raiz_generado)
            salida.setdefault(rel.parts[0], []).append(str(rel))
    return salida
