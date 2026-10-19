"""Temas globales (paquetes `Plasma/LookAndFeel`), uno por variante.

Estructura (Calibre 10525; `/usr/share/plasma/look-and-feel/org.kde.breezedark.desktop`): `metadata.json` con
`KPackageStructure` y `KPlugin`, `contents/defaults` con la sintaxis `[archivo][grupo]`, `contents/layouts/
org.kde.plasma.desktop-layout.js` y `contents/previews/`. El bloqueo lo hereda de Breeze con `X-KDE-fallbackPackage`.

Mejora 6 (decisiones 4.10): la pantalla de carga (`contents/splash/`) y el diálogo de salida (`contents/logout/`) derivan
de los de WhiteSur-dark (GPL-3.0; `fuentes/base/WhiteSur-kde/plasma/look-and-feel/`): fondo de Lliphi (el mismo que da
`fondo.py`, copiado dentro del paquete para no depender de rutas relativas) y, en lugar del logotipo de Apple, el nombre
del tema escrito en Inter con el punto en el color del acento. El indicador giratorio es el de WhiteSur; en la variante
clara se oscurece con el token de texto. Lo derivado es GPL-3.0-or-later (REUSE.toml)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import RAIZ, VERSION, autores, escribir, fondo, semanticos

WHITESUR = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "plasma" / "look-and-feel" / "com.github.vinceliuice.WhiteSur-dark" / "contents"

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
        # mejora 3 y decisiones 4.15: carpetas en el acento (herramientas/dependencias.py): Papirus tal cual (azul) en el
        # claro y el superpuesto Papirus-Dark-Lliphi (rojo) en el oscuro; ambos heredan de breeze
        "[kdeglobals][Icons]", f"Theme={'Papirus' if variante == 'claro' else 'Papirus-Dark-Lliphi'}", "",
        "[kdeglobals][General]", f"ColorScheme={marca['id_esquema'][variante]}", "font=Inter,10,-1,5,400,0,0,0,0,0", "fixed=JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0",
        "menuFont=Inter,10,-1,5,400,0,0,0,0,0", "toolBarFont=Inter,10,-1,5,400,0,0,0,0,0",
        "smallestReadableFont=Inter,8,-1,5,400,0,0,0,0,0", "",
        "[kdeglobals][WM]", "activeFont=Inter,10,-1,5,500,0,0,0,0,0", "",
        "[plasmarc][Theme]", f"name={marca['id']}-{variante}", "",
        "[Wallpaper]", f"Image={marca['id_fondo']}", "",   # por nombre; el instalador lo aplica además por ruta (docs/validacion.md §3)
        "[kcminputrc][Mouse]", "cursorTheme=WhiteSur-cursors", "",
        # decoración propia (Aurorae, motor SVG V2 de Plasma 6.6: el KCM escribe `org.kde.kwin.aurorae.v2`); sin menú a la izquierda
        "[kwinrc][org.kde.kdecoration2]", "library=org.kde.kwin.aurorae.v2",
        f"theme=__aurorae__svg__{marca['id'] if variante == 'oscuro' else marca['id'] + '-claro'}", "ButtonsOnLeft=XIA", "ButtonsOnRight=", "",
        "[kwinrc][WindowSwitcher]", "LayoutName=org.kde.breeze.desktop", "",
        "[kwinrc][DesktopSwitcher]", "LayoutName=org.kde.breeze.desktop", "",
        "[KSplash]", f"Theme={marca['id_global'][variante]}", "",   # mejora 6: la pantalla de carga propia
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
        "X-KPackage-Dependencies": ["kns://xcursor.knsrc/api.kde-look.org/1411743"],
    }, ensure_ascii=False, indent=4) + "\n"


LOGO_WHITESUR = """        Image {
            id: logo
            //match SDDM/lockscreen avatar positioning
            property real size: units.gridUnit * 8

            anchors.centerIn: parent

            source: "images/logo.svg"

//            sourceSize.width: 503
//            sourceSize.height: 99
        }"""

LOGO_LLIPHI = """        Text {{
            id: logo
            // Lliphi: el nombre en Inter en lugar del logotipo de Apple de WhiteSur
            anchors.centerIn: parent
            textFormat: Text.StyledText
            text: "{nombre}<font color='{acento}'>.</font>"
            color: "{texto}"
            font.family: "Inter"
            font.weight: Font.Light
            font.pixelSize: units.gridUnit * 4
            font.letterSpacing: units.gridUnit * 0.15
        }}"""

FONDO_WHITESUR = 'source: "../../../../../wallpapers/WhiteSur-dark/contents/images/3840x2160.jpg"'


def pantallas(tokens: dict, marca: dict, variante: str, base: Path, hechos: list[Path]) -> None:
    """Mejora 6: pantalla de carga y diálogo de salida derivados de WhiteSur-dark."""
    t = semanticos(tokens, variante)
    cabecera = f"// GENERADO por herramientas/generar.py desde fuentes/base/WhiteSur-kde (GPL-3.0) y tokens/; no editar\n"
    # pantalla de carga
    for f in sorted((WHITESUR / "splash").rglob("*")):
        if not f.is_file() or f.name in ("logo.svg", "Splash.qml", "background.png"):
            continue
        rel = f.relative_to(WHITESUR)
        if f.suffix == ".svg":   # indicador blanco de WhiteSur; en la clara, el gris del texto
            svg = f.read_text(encoding="utf-8")
            escribir(base / "contents" / rel, svg if variante == "oscuro" else svg.replace("#ffffff", t["texto.normal"]), hechos)
    qml = (WHITESUR / "splash" / "Splash.qml").read_text(encoding="utf-8")
    assert LOGO_WHITESUR in qml, "cambió el Splash.qml de WhiteSur: revisar la sustitución del logotipo"
    qml = qml.replace(LOGO_WHITESUR, LOGO_LLIPHI.format(nombre=marca["nombre"], acento=t["acento.base"], texto=t["texto.normal"]))
    escribir(base / "contents" / "splash" / "Splash.qml", cabecera + qml, hechos)
    imagen = fondo.imagen(t, 2560, 1440, variante)
    for ruta in (base / "contents" / "splash" / "images" / "background.png", base / "contents" / "logout" / "background.png"):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        imagen.save(ruta, optimize=True)
        hechos.append(ruta)
    # diálogo de salida: el de WhiteSur con el fondo de Lliphi dentro del paquete
    for nombre in ("LogoutButton.qml", "timer.js"):
        escribir(base / "contents" / "logout" / nombre, (WHITESUR / "logout" / nombre).read_text(encoding="utf-8"), hechos)
    qml = (WHITESUR / "logout" / "Logout.qml").read_text(encoding="utf-8")
    assert FONDO_WHITESUR in qml, "cambió el Logout.qml de WhiteSur: revisar la ruta del fondo"
    escribir(base / "contents" / "logout" / "Logout.qml", cabecera + qml.replace(FONDO_WHITESUR, 'source: "background.png"'), hechos)


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for variante in ("claro", "oscuro"):
        base = destino / "look-and-feel" / marca["id_global"][variante]
        escribir(base / "metadata.json", metadata(marca, variante), hechos)
        escribir(base / "contents" / "defaults", defaults(marca, variante), hechos)
        escribir(base / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js",
                 LAYOUT.format(nombre=marca["nombre"], fondo=marca["id_fondo"]), hechos)
        pantallas(tokens, marca, variante, base, hechos)
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
