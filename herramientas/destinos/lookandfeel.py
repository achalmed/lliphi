"""Temas globales (paquetes `Plasma/LookAndFeel`), uno por variante.

Estructura (Calibre 10525; `/usr/share/plasma/look-and-feel/org.kde.breezedark.desktop`): `metadata.json` con
`KPackageStructure` y `KPlugin`, `contents/defaults` con la sintaxis `[archivo][grupo]`, `contents/layouts/
org.kde.plasma.desktop-layout.js` y `contents/previews/`. Hereda splash, bloqueo y cierre de sesión de Breeze
con `X-KDE-fallbackPackage`; no trae ninguno propio en el primer lote."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import RAIZ, VERSION, autores, escribir

LAYOUT = """// GENERADO por herramientas/generar.py desde tokens/; no editar.
// Disposición de {nombre}: barra superior fina (lanzador, reloj, bandeja) y dock inferior flotante que se
// oculta bajo las ventanas. Se aplica solo si el usuario marca «Disposición del escritorio» al aplicar el tema.

var superior = new Panel;
superior.location = "top";
superior.height = Math.round(gridUnit * 2);           // ≈ 36 px con gridUnit 18
superior.hiding = "none";
superior.floating = false;
superior.addWidget("org.kde.plasma.kickoff");
superior.addWidget("org.kde.plasma.panelspacer");
superior.addWidget("org.kde.plasma.digitalclock");
superior.addWidget("org.kde.plasma.panelspacer");
superior.addWidget("org.kde.plasma.systemtray");

var dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(gridUnit * 3);              // ≈ 56 px
dock.hiding = "windowscover";
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
var tareas = dock.addWidget("org.kde.plasma.icontasks");
tareas.currentConfigGroup = ["General"];
tareas.writeConfig("launchers", "applications:org.kde.dolphin.desktop,applications:org.kde.konsole.desktop,applications:systemsettings.desktop");

var escritorios = desktopsForActivity(currentActivity());
for (var i = 0; i < escritorios.length; i++) {{
    escritorios[i].wallpaperPlugin = "org.kde.image";
    escritorios[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    escritorios[i].writeConfig("Image", "{fondo}");
}}
"""


def defaults(marca: dict, variante: str) -> str:
    return "\n".join([
        "# GENERADO por herramientas/generar.py desde tokens/; no editar", "",
        "[kdeglobals][KDE]", "widgetStyle=Breeze", "",
        "[kdeglobals][General]", f"ColorScheme={marca['id_esquema'][variante]}", "",
        "[kdeglobals][Icons]", f"Theme={'breeze' if variante == 'claro' else 'breeze-dark'}", "",
        "[plasmarc][Theme]", f"name={marca['id']}", "",
        "[Wallpaper]", f"Image={marca['id_fondo']}", "",
        "[kcminputrc][Mouse]", "cursorTheme=breeze_cursors", "",
        "[kwinrc][org.kde.kdecoration2]", "library=org.kde.breeze", "theme=Breeze", "ButtonsOnLeft=M", "ButtonsOnRight=IAX", "",
        "[kwinrc][WindowSwitcher]", "LayoutName=org.kde.breeze.desktop", "",
        "[kwinrc][DesktopSwitcher]", "LayoutName=org.kde.breeze.desktop", "",
        "[KSplash]", "Theme=org.kde.breeze", "",
    ])


def metadata(marca: dict, variante: str) -> str:
    return json.dumps({
        "KPackageStructure": "Plasma/LookAndFeel",
        "KPlugin": {
            "Authors": autores(marca),
            "Category": "",
            "Description": f"{marca['nombre_esquema'][variante]}: {marca['descripcion']}",
            "Id": marca["id_global"][variante],
            "License": marca["licencia_activos"],
            "Name": marca["nombre_esquema"][variante],
            "Version": VERSION,
            "Website": marca["sitio"],
        },
        "X-KDE-fallbackPackage": "org.kde.breeze.desktop",
    }, ensure_ascii=False, indent=4) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        base = destino / "look-and-feel" / marca["id_global"][variante]
        escribir(base / "metadata.json", metadata(marca, variante), hechos)
        escribir(base / "contents" / "defaults", defaults(marca, variante), hechos)
        escribir(base / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js",
                 LAYOUT.format(nombre=marca["nombre"], fondo=marca["id_fondo"]), hechos)
        # Vistas previas: hasta la fase 7 son el boceto (rotulado como tal); después, capturas reales.
        for origen, nombre in ((RAIZ / "muestras" / f"boceto-{variante}.png", "fullscreenpreview.jpg"),
                               (RAIZ / "muestras" / f"boceto-{variante}.png", "preview.png")):
            if origen.exists():
                dest = base / "contents" / "previews" / nombre
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origen, dest)
                hechos.append(dest)
    return hechos
