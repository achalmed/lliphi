"""Paquete de fondo de pantalla de Plasma: composición original generada desde los tokens.

Estructura (Calibre 10529; `/usr/share/wallpapers/Next`): `metadata.json` (`KPlugin` con `Id`, `Name`,
`License`, `Authors`; `X-KDE-PlasmaImageWallpaper-AccentColor` con `{Light, Dark}`), `contents/images/
<AnchoxAlto>.png` (variante clara) e `contents/images_dark/` (oscura, Plasma ≥ 6.6), `contents/screenshot.png`.

Dos paquetes: «Lliphi Horizonte» (`<dominio>.horizonte`, el del tema global), un degradado suave de dos neutros con
una franja diagonal del acento a baja opacidad; y «Lliphi Forma» (`<dominio>.forma`, decisiones 4.23), una composición
de formas sobre neutro liso: dos cuadrados de vidrio esmerilado, un semicírculo en el rojo de Lliphi y una píldora que
se deshace hacia abajo, con una matriz de puntos tenue (el guiño a la tipografía de puntos de Nothing) y grano fino;
claro y oscuro. Sin texto ni logotipo. Requiere Pillow; sin él, el destino se omite con aviso."""
from __future__ import annotations

import json
from pathlib import Path

from nucleo import VERSION, autores, semanticos

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


def _mezcla(a, b, k: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def forma_paleta(tokens: dict, variante: str) -> dict:
    """Los colores de «Lliphi Forma» desde las primitivas: el fondo, la luz media y la variación de cada cuadrado, los
    dos extremos de la píldora, los puntos y el rojo (el acento del oscuro en las dos variantes, como el botón de
    cerrar de la decoración)."""
    pc = {k: _hex(v["$value"]["hex"]) for k, v in tokens["primitivas"]["claro"].items()}
    po = {k: _hex(v["$value"]["hex"]) for k, v in tokens["primitivas"]["oscuro"].items()}
    rojo = po["acento"]
    if variante == "claro":
        return {"fondo": _mezcla(pc["neutro-4"], pc["neutro-5"], 0.18), "a": (0.80, 0.15), "b": (0.50, 0.14),
                "pildora": (po["neutro-3b"], pc["neutro-4"]), "puntos": pc["neutro-0"], "rojo": rojo,
                "sombra": 0.45, "puntos_alfa": 70, "luz": 0.06}
    return {"fondo": po["neutro-0"], "a": (0.40, 0.12), "b": (0.26, 0.10), "pildora": (po["neutro-5"], po["neutro-2"]),
            "puntos": po["neutro-7"], "rojo": rojo, "sombra": 0.6, "puntos_alfa": 55, "luz": 0.035}


def _mosaico(lado: int, media: float, var: float, semilla: int):
    """Un cuadrado de vidrio esmerilado: una rejilla de 6 × 6 grises al azar (semilla fija: reproducible), ampliada,
    desenfocada y con grano."""
    import random
    from PIL import Image, ImageChops, ImageFilter
    rnd = random.Random(semilla)
    peq = Image.new("L", (6, 6))
    peq.putdata([max(0, min(255, round(255 * (media + rnd.uniform(-var, var))))) for _ in range(36)])
    m = peq.resize((lado, lado), Image.NEAREST).filter(ImageFilter.GaussianBlur(lado * 0.035))
    grano = _ruido(lado, lado, 18, semilla + 100).filter(ImageFilter.GaussianBlur(0.6))
    return ImageChops.add(m, grano, scale=1.0, offset=-128)


def _ruido(ancho: int, alto: int, sigma: float, semilla: int):
    """Ruido gaussiano en gris centrado en 128, reproducible (Image.effect_noise no admite semilla)."""
    import random
    from PIL import Image
    rnd = random.Random(semilla)
    teja = Image.new("L", (256, 256))
    teja.putdata([max(0, min(255, round(rnd.gauss(128, sigma)))) for _ in range(256 * 256)])
    salida = Image.new("L", (ancho, alto))
    for y in range(0, alto, 256):
        for x in range(0, ancho, 256):
            salida.paste(teja.rotate(90 * ((x // 256 + y // 256) % 4)), (x, y))
    return salida


def forma(tokens: dict, variante: str, ancho: int = 3840, alto: int = 2160, firma: str | None = None):
    """«Lliphi Forma» de una variante, al tamaño pedido."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    p = forma_paleta(tokens, variante)
    lienzo = Image.new("RGB", (ancho, alto), p["fondo"])
    vin = Image.new("L", (ancho // 8, alto // 8), 0)       # el centro, apenas más claro
    ImageDraw.Draw(vin).ellipse((-ancho // 32, -alto // 16, ancho // 8 + ancho // 32, alto // 8 + alto // 16), fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(ancho // 64)).resize((ancho, alto), Image.BICUBIC)
    lienzo = Image.composite(Image.new("RGB", (ancho, alto), _mezcla(p["fondo"], (255, 255, 255), p["luz"])), lienzo, vin)
    s = round(alto * 0.25)                                 # lado de los cuadrados
    r = s // 2
    pw, ph = round(s * 1.62), round(s * 0.74)
    x0 = ancho // 2 - (2 * s + r + pw - round(s * 0.02)) // 2
    y0 = alto // 2 - s // 2
    xs = x0 + 2 * s + r                                    # el canto plano del semicírculo
    px, py = xs - round(s * 0.02), y0 + (s - ph) // 2
    radio_c, pluma = round(s * 0.05), max(2, round(s * 0.012))
    # 1: las sombras de todo, desenfocadas
    sombra = Image.new("L", (ancho, alto), 0)
    ds = ImageDraw.Draw(sombra)
    for i in range(2):
        ds.rounded_rectangle((x0 + i * s, y0 + s * 0.06, x0 + (i + 1) * s, y0 + s * 1.06), radio_c, fill=110)
    ds.pieslice((xs - r, y0 + s * 0.06, xs + r, y0 + s * 1.06), 90, 270, fill=120)
    ds.rounded_rectangle((px, py + ph * 0.10, px + pw, py + ph * 0.75), round(ph * 0.48), fill=100)
    sombra = sombra.filter(ImageFilter.GaussianBlur(s * 0.10)).point(lambda v: round(v * p["sombra"]))
    lienzo = Image.composite(Image.new("RGB", (ancho, alto), (0, 0, 0)), lienzo, sombra)
    # 2: los cuadrados esmerilados
    mascara_c = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mascara_c).rounded_rectangle((pluma, pluma, s - pluma, s - pluma), radio_c, fill=255)
    mascara_c = mascara_c.filter(ImageFilter.GaussianBlur(pluma * 0.6))
    for i, (media, var) in enumerate((p["a"], p["b"])):
        m = _mosaico(s, media, var, 7 + i)
        lienzo.paste(Image.merge("RGB", (m, m, m)), (x0 + i * s, y0), mascara_c)
    # 3: el semicírculo, con una luz leve arriba a la izquierda
    sc = Image.new("RGB", (2 * r, 2 * r), p["rojo"])
    d = ImageDraw.Draw(sc)
    for k in range(r, 0, -1):
        t = k / r
        dx = r * 0.12 * (1 - t)
        d.ellipse((r - k - dx, r - k - dx, r + k - dx, r + k - dx), fill=_mezcla(p["rojo"], _mezcla(p["rojo"], (255, 255, 255), 0.18), (1 - t) * 0.6))
    medio = Image.new("L", (2 * r, 2 * r), 0)
    ImageDraw.Draw(medio).pieslice((0, 0, 2 * r - 1, 2 * r - 1), 90, 270, fill=255)
    lienzo.paste(sc, (xs - r, y0), medio.filter(ImageFilter.GaussianBlur(1.2)))
    # 4: la píldora: degradado vertical, matriz de puntos arriba, se deshace abajo
    arriba, abajo = p["pildora"]
    grad = Image.new("RGB", (1, ph))
    for y in range(ph):
        grad.putpixel((0, y), _mezcla(arriba, abajo, (y / ph) ** 1.6))
    grad = grad.resize((pw, ph), Image.BICUBIC)
    grano = _ruido(pw, ph, 10, 31)
    grad = Image.merge("RGB", [ImageChops.add(c, grano, scale=1.0, offset=-128) for c in grad.split()])
    puntos = Image.new("L", (pw, ph), 0)
    dp = ImageDraw.Draw(puntos)
    paso = max(6, round(ph / 11))
    rp = max(1, round(paso * 0.14))
    for yy in range(paso, ph // 2, paso):
        for xx in range(round(ph / 2), pw - round(ph / 2), paso):
            dp.ellipse((xx - rp, yy - rp, xx + rp, yy + rp), fill=p["puntos_alfa"])
    grad = Image.composite(Image.new("RGB", (pw, ph), p["puntos"]), grad, puntos)
    mascara = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, pw - 1, ph - 1), round(ph * 0.48), fill=255)
    desvanece = Image.new("L", (1, ph))
    for y in range(ph):
        desvanece.putpixel((0, y), 255 if y < ph * 0.55 else round(255 * max(0.0, 1 - (y - ph * 0.55) / (ph * 0.45)) ** 0.8))
    mascara = ImageChops.multiply(mascara, desvanece.resize((pw, ph))).filter(ImageFilter.GaussianBlur(1.0))
    lienzo.paste(grad, (px, py), mascara)
    if firma:   # como la firma de un cuadro: bajo la composición, alineada al final de la píldora
        tinta = p["pildora"][0] if variante == "claro" else p["puntos"]
        lienzo = _firma(lienzo, firma, px + pw, y0 + s + round(s * 0.22), alto / 300, tinta, 0.40 if variante == "claro" else 0.32,
                        a_la_derecha=True)
    # 5: grano fino en todo el lienzo
    g = _ruido(ancho, alto, 6, 53)
    return Image.merge("RGB", [ImageChops.add(c, g, scale=1.0, offset=-128) for c in lienzo.split()])


# «Lliphi Relámpago»: las letras del nombre en una matriz de puntos de 5 × 7 (X = punto); sin tipografías, para que
# la imagen salga igual en cualquier máquina
LETRAS = {
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    # la firma (minúsculas y @), en la misma rejilla
    "@": [".XXX.", "X...X", "X.XXX", "X.X.X", "X.XXX", "X....", ".XXX."],
    "a": [".....", ".....", ".XXX.", "....X", ".XXXX", "X...X", ".XXXX"],
    "c": [".....", ".....", ".XXX.", "X....", "X....", "X....", ".XXX."],
    "d": ["....X", "....X", ".XXXX", "X...X", "X...X", "X...X", ".XXXX"],
    "e": [".....", ".....", ".XXX.", "X...X", "XXXXX", "X....", ".XXX."],
    "h": ["X....", "X....", "XXXX.", "X...X", "X...X", "X...X", "X...X"],
    "i": ["..X..", ".....", ".XX..", "..X..", "..X..", "..X..", ".XXX."],
    "l": [".XX..", "..X..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "m": [".....", ".....", "XX.X.", "X.X.X", "X.X.X", "X.X.X", "X.X.X"],
    "n": [".....", ".....", "XXXX.", "X...X", "X...X", "X...X", "X...X"],
    "o": [".....", ".....", ".XXX.", "X...X", "X...X", "X...X", ".XXX."],
    "s": [".....", ".....", ".XXXX", "X....", ".XXX.", "....X", "XXXX."],
}


def _firma(lienzo, texto: str, x: float, y: float, paso: float, color, alfa: float, a_la_derecha: bool = False):
    """Escribe `texto` en la matriz de puntos, pequeño y tenue: `paso` es la distancia entre puntos y `alfa` la
    opacidad. Con `a_la_derecha`, `x` es donde termina."""
    from PIL import Image, ImageDraw
    ancho = (len(texto) * 6 - 1) * paso
    if a_la_derecha:
        x -= ancho
    capa = Image.new("L", lienzo.size, 0)
    d = ImageDraw.Draw(capa)
    r = paso * 0.38
    for n, letra in enumerate(texto):
        for j, fila in enumerate(LETRAS.get(letra, LETRAS["o"])):
            for i, c in enumerate(fila):
                if c == "X":
                    px, py = x + (n * 6 + i) * paso, y + j * paso
                    d.ellipse((px - r, py - r, px + r, py + r), fill=round(255 * alfa))
    return Image.composite(Image.new("RGB", lienzo.size, color), lienzo, capa)


def relampago_paleta(tokens: dict, v: str) -> dict:
    """Los colores de «Lliphi Relámpago» de una variante: su fondo, su texto, la rampa de neutros y SU acento (azul en
    el claro, rojo en el oscuro)."""
    p = {k: _hex(x["$value"]["hex"]) for k, x in tokens["primitivas"][v].items()}
    if v == "claro":
        return {"fondo": p["neutro-2"], "rejilla": p["neutro-4"], "texto": p["neutro-7"], "acento": p["acento"],
                "suave": p["acento-suave"], "fuerte": p["acento-texto"],
                "rampa": [p[k] for k in ("neutro-0", "neutro-1", "neutro-2", "neutro-3", "neutro-4", "neutro-5", "neutro-6", "neutro-7")],
                "halo": 0.30}
    return {"fondo": p["neutro-0"], "rejilla": p["neutro-3b"], "texto": p["neutro-7"], "acento": p["acento"],
            "suave": p["acento-suave"], "fuerte": p["acento-texto"],
            "rampa": [p[k] for k in ("neutro-0", "neutro-1", "neutro-2", "neutro-3", "neutro-3b", "neutro-4", "neutro-5", "neutro-7")],
            "halo": 0.45}


def relampago(tokens: dict, v: str, W: int = 3840, H: int = 2160, firma: str | None = None):
    """«Lliphi Relámpago» de una variante: el relámpago (lliphi, en quechua) en semitono de puntos con su halo, el nombre
    en matriz de puntos con el punto de la marca en el acento y la rampa de los tokens de la variante."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    pa = relampago_paleta(tokens, v)
    img = Image.new("RGB", (W, H), pa["fondo"])
    d = ImageDraw.Draw(img)
    # rejilla de puntos tenue en todo el fondo
    paso = round(H / 54)
    rp = max(1, round(paso * 0.07))
    for y in range(paso // 2, H, paso):
        for x in range(paso // 2, W, paso):
            d.ellipse((x - rp, y - rp, x + rp, y + rp), fill=_mezcla(pa["fondo"], pa["rejilla"], 0.55))
    # el relámpago: un zigzag; dentro, puntos más grandes cerca de su eje
    cx, cy = round(W * 0.31), round(H * 0.5)
    e = H * 0.36
    poli = [(-0.10, -1.00), (0.42, -1.00), (0.10, -0.18), (0.48, -0.18), (-0.30, 1.00), (-0.04, 0.12), (-0.40, 0.12)]
    pts = [(cx + x * e, cy + y * e) for x, y in poli]
    mascara = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mascara).polygon(pts, fill=255)
    # halo
    halo = mascara.filter(ImageFilter.GaussianBlur(H * 0.05)).point(lambda a: round(a * pa["halo"]))
    img = Image.composite(Image.new("RGB", (W, H), pa["acento"]), img, halo)
    d = ImageDraw.Draw(img)
    interior = mascara.filter(ImageFilter.GaussianBlur(H * 0.012))   # más denso en el centro de cada trazo
    paso_r = round(H / 54)
    mpx = interior.load()
    for y in range(paso_r // 2, H, paso_r):
        for x in range(paso_r // 2, W, paso_r):
            a = mpx[x, y]
            if a > 20:
                r = paso_r * (0.16 + 0.30 * (a / 255))
                col = _mezcla(pa["suave"], pa["acento"], a / 255)
                d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    # el nombre en matriz de puntos, con el punto final en el acento
    texto = "LLIPHI"
    dp = round(H / 70)              # paso de los puntos del nombre
    rr = dp * 0.36
    x0 = round(W * 0.49)
    y0 = round(H * 0.5 - 3.5 * dp)
    x = x0
    for letra in texto:
        filas = LETRAS[letra]
        for j, fila in enumerate(filas):
            for i, c in enumerate(fila):
                if c == "X":
                    px, py = x + i * dp, y0 + j * dp
                    d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=pa["texto"])
        x += 6 * dp
    pr = dp * 0.62                   # el punto de la marca («Lliphi.»)
    d.ellipse((x - pr + dp * 0.2, y0 + 6 * dp - pr, x + pr + dp * 0.2, y0 + 6 * dp + pr), fill=pa["acento"])
    # la rampa de la paleta: los tokens de la variante
    lado = round(dp * 1.6)
    yr = y0 + 9 * dp + round(dp * 0.6)
    # los tres acentos, ordenados por su luz (en el oscuro el acento de texto es el más claro; en el claro, el más
    # oscuro): así la tira sube de oscuro a claro en las dos variantes
    acentos = sorted([pa["fuerte"], pa["acento"], pa["suave"]], key=lambda c: sum(c))
    for k, col in enumerate(pa["rampa"] + acentos):
        xr = x0 - round(dp * 0.4) + k * (lado + round(dp * 0.45))
        d.rounded_rectangle((xr, yr, xr + lado, yr + lado), round(lado * 0.25), fill=col,
                            outline=_mezcla(pa["fondo"], pa["texto"], 0.15), width=max(1, round(H / 1080)))
    if firma:   # bajo la rampa, alineada con el nombre: pequeña y tenue
        img = _firma(img, firma, x0, yr + lado + round(dp * 1.6), H / 300, pa["texto"], 0.42 if v == "claro" else 0.36)
    g = _ruido(W, H, 5, 53)
    return Image.merge("RGB", [ImageChops.add(c, g, scale=1.0, offset=-128) for c in img.split()])


def id_forma(marca: dict) -> str:
    return f"{marca['dominio_inverso']}.forma"


def id_relampago(marca: dict) -> str:
    return f"{marca['dominio_inverso']}.relampago"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("  aviso: sin Pillow no se generan los fondos (pip install pillow)")
        return []
    hechos: list[Path] = []
    base = destino / marca["id_fondo"]
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
    from PIL import Image
    paquetes = [(id_forma(marca), "Forma", forma, (oscuro["acento.base"], oscuro["acento.base"])),
                (id_relampago(marca), "Relámpago", relampago, (claro["acento.base"], oscuro["acento.base"]))]
    for id_, nombre, dibujo, acentos in paquetes:
        hechos += _paquete_jpeg(destino, marca, id_, f"{marca['nombre']} {nombre}", dibujo, acentos, tokens)
        if marca.get("firma"):   # la misma imagen con la firma del autor, pequeña y tenue (decisiones 4.25)
            hechos += _paquete_jpeg(destino, marca, f"{id_}.firmado", f"{marca['nombre']} {nombre} · {marca['firma']}",
                                    lambda t, v, w, h, d=dibujo: d(t, v, w, h, firma=marca["firma"]), acentos, tokens)
    return hechos


def _paquete_jpeg(destino: Path, marca: dict, id_: str, nombre: str, dibujo, acentos: tuple[str, str], tokens: dict) -> list[Path]:
    """Un paquete de fondo dibujado una vez a 4K por variante y reducido a los otros tamaños (el mismo dibujo en
    todos), en JPEG de calidad 90 sin submuestreo del color: el grano no comprime en PNG."""
    from PIL import Image
    hechos: list[Path] = []
    base = destino / id_
    meta = {"KPlugin": {"Authors": autores(marca), "Id": id_, "License": marca["licencia_activos"], "Name": nombre,
                        "Version": VERSION},
            "X-KDE-PlasmaImageWallpaper-AccentColor": {"Light": acentos[0], "Dark": acentos[1]}}
    base.mkdir(parents=True, exist_ok=True)
    (base / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    hechos.append(base / "metadata.json")
    for carpeta, variante in (("images", "claro"), ("images_dark", "oscuro")):
        grande = dibujo(tokens, variante, *TAMANOS[-1])
        for ancho, alto in TAMANOS:
            ruta = base / "contents" / carpeta / f"{ancho}x{alto}.jpg"
            ruta.parent.mkdir(parents=True, exist_ok=True)
            (grande if (ancho, alto) == TAMANOS[-1] else grande.resize((ancho, alto), Image.LANCZOS)).save(
                ruta, quality=90, subsampling=0, optimize=True)
            hechos.append(ruta)
        if variante == "oscuro":
            grande.resize((480, 270), Image.LANCZOS).save(base / "contents" / "screenshot.jpg", quality=90, optimize=True)
            hechos.append(base / "contents" / "screenshot.jpg")
    return hechos


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: el fondo por nombre (el instalador lo aplica además por
    ruta, porque Plasma 6.6 no resuelve el nombre de un paquete de usuario; docs/validacion.md §3)."""
    return {"Wallpaper": {"Image": marca["id_fondo"]}}
