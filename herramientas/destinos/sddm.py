"""Tema de inicio de sesión (SDDM) de Lliphi, DERIVADO del de WhiteSur-dark (Vince Liuice, sobre el de Breeze de David
Edmundson; `fuentes/base/WhiteSur-kde/sddm/WhiteSur-dark`), por la mejora 7 (decisiones 4.11).

Qué cambia sobre la base:
- fondo: el de Lliphi (el mismo que da `fondo.py`, variante oscura), dentro del tema;
- acento rojo fijado en el propio `Main.qml` (`Kirigami.Theme`), porque el saludador de SDDM no lee la configuración del
  autor; la tipografía Inter no se puede fijar ahí (`Kirigami.Theme.defaultFont` es de solo lectura) y va en `[Theme] Font`
  de `/etc/sddm.conf.d/99-lliphi.conf`, que escribe el instalador;
- `metadata.desktop` y `theme.conf` propios; sin logotipo.
Se instala en `/usr/share/sddm/themes/lliphi` con `herramientas/instalar_sddm.py` (pide la contraseña con pkexec).
Lo derivado es GPL-3.0-or-later; los QML conservan su cabecera LGPL-2.0-or-later de KDE (REUSE.toml)."""
from __future__ import annotations

import shutil
from pathlib import Path

from . import RAIZ, VERSION, escribir, fondo, semanticos

BASE = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "sddm" / "WhiteSur-dark"
ANCLA = "    Kirigami.Theme.colorSet: Kirigami.Theme.Complementary\n    Kirigami.Theme.inherit: false\n"
# campo de texto de WhiteSur: un solo rectángulo translúcido; Lliphi añade un borde en el acento cuando tiene el foco
FONDO_CAMPO = """    background: Rectangle {
        color: parent.focus ? "#ffffff" : "#dddddd"
        radius: 100
        opacity: 0.45
    }"""
FONDO_CAMPO_LLIPHI = """    background: Item {{
        Rectangle {{
            anchors.fill: parent
            color: campo.focus ? "#ffffff" : "#dddddd"
            radius: 100
            opacity: 0.45
        }}
        Rectangle {{   // Lliphi (mejora 7): el acento al enfocar
            anchors.fill: parent
            color: "transparent"
            radius: 100
            border.width: 2
            border.color: "{acento}"
            visible: campo.activeFocus
        }}
    }}"""

PLUS = """    // Lliphi (mejora 7): acento rojo dentro del tema (la fuente Inter la fija la configuración de SDDM)
    Kirigami.Theme.highlightColor: "{acento}"
    Kirigami.Theme.focusColor: "{acento}"
    Kirigami.Theme.hoverColor: "{suave}"
"""


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    t = semanticos(tokens, "oscuro")
    base = destino / "sddm" / marca["id"]
    for f in sorted(BASE.rglob("*")):
        if not f.is_file() or f.name in ("Main.qml", "Input.qml", "metadata.desktop", "theme.conf", "theme.conf.user"):
            continue
        rel = f.relative_to(BASE)
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, base / rel); hechos.append(base / rel)
    qml = (BASE / "Main.qml").read_text(encoding="utf-8")
    assert ANCLA in qml, "cambió el Main.qml de WhiteSur: revisar dónde se fija el tema de Kirigami"
    qml = qml.replace(ANCLA, ANCLA + PLUS.format(acento=t["acento.base"], suave=t["acento.suave"]), 1)
    escribir(base / "Main.qml", qml, hechos)
    campo = (BASE / "Input.qml").read_text(encoding="utf-8")
    assert FONDO_CAMPO in campo and "TextField {\n" in campo, "cambió el Input.qml de WhiteSur: revisar el fondo del campo"
    campo = campo.replace("TextField {\n", "TextField {\n    id: campo\n", 1).replace(FONDO_CAMPO, FONDO_CAMPO_LLIPHI.format(acento=t["acento.base"]))
    escribir(base / "Input.qml", campo, hechos)
    escribir(base / "theme.conf", "\n".join([
        "# GENERADO por herramientas/generar.py desde tokens/ y fuentes/base/WhiteSur-kde; no editar",
        "[General]", "showlogo=hidden", "type=image",
        f"color={t['texto.normal']}",   # en WhiteSur es también el color del texto de los campos
        "font=Inter", "fontSize=10",
        "background=background.png", "needsFullUserModel=false", ""]), hechos)
    escribir(base / "metadata.desktop", "\n".join([
        "[SddmGreeterTheme]", f"Name={marca['nombre']}", f"Description=Inicio de sesión de {marca['nombre']}, derivado de WhiteSur-dark",
        f"Author={marca['autor']}", "Copyright=(c) 2014 David Edmundson; WhiteSur-dark de Vince Liuice", "License=GPL-3.0-or-later",
        "Type=sddm-theme", f"Version={VERSION}", f"Website={marca['sitio']}", "Screenshot=preview.png", "MainScript=Main.qml",
        "ConfigFile=theme.conf", "TranslationsDirectory=translations", f"Theme-Id={marca['id']}", "Theme-API=2.0", "QtVersion=6", ""]), hechos)
    imagen = fondo.imagen(t, 2560, 1440, "oscuro")
    imagen.save(base / "background.png", optimize=True); hechos.append(base / "background.png")
    captura = RAIZ / "muestras" / "capturas" / "oscuro-18-inicio-de-sesion.png"
    (shutil.copyfile(captura, base / "preview.png") if captura.exists() else fondo.imagen(t, 640, 360, "oscuro").save(base / "preview.png", optimize=True))
    hechos.append(base / "preview.png")
    return hechos
