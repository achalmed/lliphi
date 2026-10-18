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
    // por ruta del paquete: en Plasma 6.6 el nombre de un paquete de usuario no se resolvía (docs/validacion.md §3)
    escritorios[i].writeConfig("Image", "file://" + userDataPath("wallpapers") + "/{fondo}");
}}
"""


def defaults(marca: dict, variante: str) -> str:
    return "\n".join([
        "# GENERADO por herramientas/generar.py desde tokens/; no editar", "",
        "[kdeglobals][KDE]", f"widgetStyle={'kvantum' if variante == 'claro' else 'kvantum-dark'}", "",
        "[kdeglobals][Icons]", f"Theme={'Papirus-Light' if variante == 'claro' else 'Papirus-Dark'}", "",
        "[kdeglobals][General]", f"ColorScheme={marca['id_esquema'][variante]}", "font=IBM Plex Sans,10,-1,5,400,0,0,0,0,0", "fixed=IBM Plex Mono,10,-1,5,400,0,0,0,0,0",
        "menuFont=IBM Plex Sans,10,-1,5,400,0,0,0,0,0", "toolBarFont=IBM Plex Sans,10,-1,5,400,0,0,0,0,0",
        "smallestReadableFont=IBM Plex Sans,8,-1,5,400,0,0,0,0,0", "",
        "[kdeglobals][WM]", "activeFont=IBM Plex Sans,10,-1,5,500,0,0,0,0,0", "",
        "[plasmarc][Theme]", f"name={marca['id']}-{variante}", "",
        "[Wallpaper]", f"Image={marca['id_fondo']}", "",   # por nombre; el instalador lo aplica además por ruta (docs/validacion.md §3)
        "[kcminputrc][Mouse]", f"cursorTheme={'Bibata-Modern-Ice' if variante == 'claro' else 'Bibata-Modern-Classic'}", "",
        # decoración propia (Aurorae, motor SVG V2 de Plasma 6.6: el KCM escribe `org.kde.kwin.aurorae.v2`); sin menú a la izquierda
        "[kwinrc][org.kde.kdecoration2]", "library=org.kde.kwin.aurorae.v2",
        f"theme=__aurorae__svg__{marca['id'] if variante == 'oscuro' else marca['id'] + '-claro'}", "ButtonsOnLeft=", "ButtonsOnRight=IAX", "",
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
        "X-KPackage-Dependencies": ["kns://icons.knsrc/api.kde-look.org/1166289", "kns://xcursor.knsrc/api.kde-look.org/1914825"],
    }, ensure_ascii=False, indent=4) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        base = destino / "look-and-feel" / marca["id_global"][variante]
        escribir(base / "metadata.json", metadata(marca, variante), hechos)
        escribir(base / "contents" / "defaults", defaults(marca, variante), hechos)
        escribir(base / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js",
                 LAYOUT.format(nombre=marca["nombre"], fondo=marca["id_fondo"]), hechos)
        # Vistas previas: capturas reales de la fase 7 (muestras/capturas); si faltan, el boceto rotulado.
        captura = RAIZ / "muestras" / "capturas" / f"{variante}-02-lanzador.png"
        origen_previa = captura if captura.exists() else RAIZ / "muestras" / f"boceto-{variante}.png"
        for origen, nombre in ((origen_previa, "fullscreenpreview.jpg"), (origen_previa, "preview.png")):
            if origen.exists():
                dest = base / "contents" / "previews" / nombre
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origen, dest)
                hechos.append(dest)
    return hechos
