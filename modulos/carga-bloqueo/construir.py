"""Pantallas de la sesión de Lliphi: la de carga (splash) y el diálogo de salida, derivados de WhiteSur-dark (mejora 6,
decisiones 4.10), más el fondo del bloqueo de pantalla (`aplicar.py`).

Es un **componente** del tema global: KDE solo carga la pantalla de carga y la de salida desde el paquete
`Plasma/LookAndFeel` cuyo `Id` nombra `[KSplash] Theme` (`contents/splash/Splash.qml`, `contents/logout/`), así que
este módulo no tiene paquete propio y escribe sus archivos dentro de `generado/global/<Id>/contents/` cuando el tema
global lo integra (`integrar`). El bloqueo NO se dibuja aquí: en Plasma 6.6 su QML es del paquete de shell
(`plasma/shells/org.kde.plasma.desktop/contents/lockscreen/`), no del tema global (docs/migracion-modular.md §1.1).

Base: `fuentes/base/WhiteSur-kde/plasma/look-and-feel/` (GPL-3.0). Cambios: el fondo de Lliphi (el mismo que da
`complementos/fondos`, copiado dentro del paquete para no depender de rutas relativas) y, en lugar del logotipo de
Apple, el nombre del tema escrito en Inter con el punto en el color del acento. El indicador giratorio es el de
WhiteSur; en la variante clara se oscurece con el token de texto. Lo derivado es GPL-3.0-or-later (REUSE.toml)."""
from __future__ import annotations

from pathlib import Path

from nucleo import RAIZ, escribir, registro, semanticos

fondo = registro.codigo("fondos")   # la imagen del fondo de Lliphi (modulo.json: dependencia de construcción)

WHITESUR = RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "plasma" / "look-and-feel" / "com.github.vinceliuice.WhiteSur-dark" / "contents"

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


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo que aporta a `contents/defaults` del tema global: la pantalla de carga es la de su propio paquete."""
    return {"KSplash": {"Theme": marca["id_global"][variante]}}


def integrar(tokens: dict, marca: dict, variante: str, paquete: Path, hechos: list[Path]) -> None:
    """Escribe `contents/splash/` y `contents/logout/` dentro del paquete del tema global de la variante."""
    t = semanticos(tokens, variante)
    cabecera = f"// GENERADO por herramientas/generar.py desde fuentes/base/WhiteSur-kde (GPL-3.0) y tokens/; no editar\n"
    # pantalla de carga
    for f in sorted((WHITESUR / "splash").rglob("*")):
        if not f.is_file() or f.name in ("logo.svg", "Splash.qml", "background.png"):
            continue
        rel = f.relative_to(WHITESUR)
        if f.suffix == ".svg":   # indicador blanco de WhiteSur; en la clara, el gris del texto
            svg = f.read_text(encoding="utf-8")
            escribir(paquete / "contents" / rel, svg if variante == "oscuro" else svg.replace("#ffffff", t["texto.normal"]), hechos)
    qml = (WHITESUR / "splash" / "Splash.qml").read_text(encoding="utf-8")
    assert LOGO_WHITESUR in qml, "cambió el Splash.qml de WhiteSur: revisar la sustitución del logotipo"
    qml = qml.replace(LOGO_WHITESUR, LOGO_LLIPHI.format(nombre=marca["nombre"], acento=t["acento.base"], texto=t["texto.normal"]))
    escribir(paquete / "contents" / "splash" / "Splash.qml", cabecera + qml, hechos)
    imagen = fondo.imagen(t, 2560, 1440, variante)
    for ruta in (paquete / "contents" / "splash" / "images" / "background.png", paquete / "contents" / "logout" / "background.png"):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        imagen.save(ruta, optimize=True)
        hechos.append(ruta)
    # diálogo de salida: el de WhiteSur con el fondo de Lliphi dentro del paquete
    for nombre in ("LogoutButton.qml", "timer.js"):
        escribir(paquete / "contents" / "logout" / nombre, (WHITESUR / "logout" / nombre).read_text(encoding="utf-8"), hechos)
    qml = (WHITESUR / "logout" / "Logout.qml").read_text(encoding="utf-8")
    assert FONDO_WHITESUR in qml, "cambió el Logout.qml de WhiteSur: revisar la ruta del fondo"
    escribir(paquete / "contents" / "logout" / "Logout.qml", cabecera + qml.replace(FONDO_WHITESUR, 'source: "background.png"'), hechos)
