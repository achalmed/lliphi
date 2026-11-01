"""studio/tests/test_paginas.py — las secciones de Lliphi Studio sobre una copia del proyecto (conftest.py): los
editores trabajan en un borrador fuera del proyecto y solo escriben el ajustes.json de su módulo."""
from __future__ import annotations

import time

import pytest

from lliphi_studio import color, proyecto


def esperar(cond, app, segundos: float = 60) -> bool:
    fin = time.monotonic() + segundos
    while not cond() and time.monotonic() < fin:
        app.processEvents()
        time.sleep(0.03)
    return cond()


def cerrar(v, app) -> None:
    esperar(lambda: not any(w.isRunning() for w in v._workers), app, 120)
    v.ui.close()


@pytest.fixture
def ventana(lliphi, app):
    from lliphi_studio.ventana import Ventana
    hechas = []

    def crear(*solo):
        v = Ventana(solo=solo)
        hechas.append(v)
        return v
    yield crear
    for v in hechas:
        cerrar(v, app)


def test_color_oklch_coincide_con_la_paleta(lliphi):
    aj = proyecto.leer_ajustes("esquema")
    informe = proyecto.correr_json("paleta")
    for v in ("claro", "oscuro"):
        for k, (l, c) in aj["neutros"][v].items():
            assert color.oklch_a_hex(l, c, aj["matiz_neutro"]) == informe["variantes"][v]["primitivas"][k]["hex"]
    assert round(color.contraste("#ffffff", "#000000"), 1) == 21.0
    assert color.simular("#c93436", None) == "#c93436" and color.simular("#c93436", "deuteranopía") != "#c93436"
    assert "esquema" in color.usos(lliphi / "generado", informe["variantes"]["oscuro"]["semanticos"]["acento.base"]["hex"])


def test_color_edita_un_borrador_y_mide_el_contraste(ventana, app, lliphi):
    v = ventana("color")
    pag = v.paginas["color"]
    assert esperar(lambda: pag.informe is not None, app), "sin informe de paleta.py"
    assert pag.informe["ok"] and pag.ruta == ("acentos", "rojo", "oscuro", "base")
    antes = proyecto.modulo("esquema").ajustes.read_bytes()
    assert pag.seleccionar(("neutros", "oscuro", "neutro-5"))   # texto inactivo del oscuro, casi negro: debe fallar
    pag.informe = None
    pag.d_l.poner(0.30)
    pag._cambio()
    assert esperar(lambda: pag.informe is not None and not pag.informe["ok"], app)
    assert proyecto.leer_borrador("esquema")["neutros"]["oscuro"]["neutro-5"][0] == 0.3
    assert "Contraste (" in pag.editor.pestanas.tabText(2) and pag.editor.diff.toPlainText().startswith("---")
    pag._guardar()                                    # no se guarda con pares que fallan
    assert proyecto.modulo("esquema").ajustes.read_bytes() == antes
    pag.datos = proyecto.leer_ajustes("esquema")
    proyecto.descartar_borrador("esquema")


def test_svg_de_plasma_marcos_y_esquema(lliphi):
    from lliphi_studio import svgplasma
    estilo = lliphi / "generado" / "estilo" / "lliphi-oscuro"
    assert "widgets" in svgplasma.archivos(estilo)
    texto = svgplasma.leer(estilo / "widgets" / "panel-background.svg")
    ids = svgplasma.elementos(texto)
    assert "" in svgplasma.marcos(ids) and "shadow" in svgplasma.marcos(ids)
    colores = svgplasma.esquema(lliphi / "generado" / "esquema" / "LliphiOscuro.colors")
    assert colores["Highlight"] == proyecto.tokens()["semanticos"]["oscuro"]["acento"]["base"]["$value"]["hex"]
    assert colores["Highlight"] in svgplasma.con_esquema(texto, colores)
    deco = svgplasma.leer(lliphi / "generado" / "decoracion" / "lliphi" / "decoration.svg")
    assert {"decoration", "decoration-inactive"} <= set(svgplasma.marcos(svgplasma.elementos(deco)))


def test_plasma_compone_las_tres_columnas(ventana, app):
    v = ventana("plasma")
    pag = v.paginas["plasma"]
    assert pag.ruta_rel == "widgets/panel-background.svg"
    assert [c[0] for c in pag.lienzo.columnas] == ["Lliphi Oscuro", "Lliphi Claro", "WhiteSur-dark (base)"]
    assert pag.lienzo.prefijo == "" and pag.lista_marcos.count() >= 3
    diff = pag.editor.diff.toPlainText()                                # el recoloreo frente a WhiteSur (o nada)
    assert diff.startswith("---") or diff.startswith("Idéntico")
    imagen = pag.lienzo.grab().toImage()
    assert imagen.width() > 100 and imagen.pixelColor(imagen.width() // 2, imagen.height() // 2).isValid()


def test_ventanas_edita_el_rc_en_un_borrador(ventana, app, lliphi):
    from lliphi_studio.paginas import ventanas
    v = ventana("ventanas")
    pag = v.paginas["ventanas"]
    assert ventanas.rc_efectivo(pag.datos, "oscuro")["TitleHeight"] == "18"
    real = (lliphi / "generado" / "decoracion" / "lliphi" / "lliphirc").read_text(encoding="utf-8")
    for k, valor in ventanas.rc_efectivo(pag.datos, "oscuro").items():   # lo mismo que construye construir.py
        assert any(l.split("=", 1)[0] == k and l.split("=", 1)[1].strip() == valor for l in real.splitlines()), k
    pag.campos["TitleHeight"].setValue(24)
    pag.campos["TitleHeight"].setValue(15)                               # 15 es el de la base: sale de los ajustes
    assert "TitleHeight" not in pag.datos["rc"]
    pag.campos["ButtonSpacing"].setValue(10)
    pag._botones("izquierda", "xai?")
    borrador = proyecto.leer_borrador("decoracion")
    assert borrador["rc"]["ButtonSpacing"] == "10" and borrador["botones"]["izquierda"] == "XAI"
    assert "ButtonSpacing=10" in pag.rc_salida.toPlainText()
    pag.lienzo.resize(900, 520)
    pag.lienzo.grab()
    assert {letra for _r, letra in pag.lienzo._zonas} >= {"X", "A", "I"}
    pag._descartar()
    assert proyecto.diff_ajustes("decoracion", pag.datos) == ""


def _xcursor(ruta, tamanos=(24, 32), cuadros=2):
    """Un archivo Xcursor de verdad, pequeño: un cuadrado por tamaño y cuadro."""
    import struct
    imagenes = []
    for t in tamanos:
        for c in range(cuadros):
            pix = struct.pack("<I", 0xFF000000 | (0x30 * (c + 1))) * (t * t)
            imagenes.append(struct.pack("<9I", 36, 0xFFFD0002, t, 1, t, t, 1, 2, 50) + pix)
    toc_fin = 16 + 12 * len(imagenes)
    toc, pos = b"", toc_fin
    for (t, im) in zip([t for t in tamanos for _ in range(cuadros)], imagenes):
        toc += struct.pack("<III", 0xFFFD0002, t, pos)
        pos += len(im)
    ruta.write_bytes(b"Xcur" + struct.pack("<III", 16, 0x10000, len(imagenes)) + toc + b"".join(imagenes))


@pytest.fixture
def temas_falsos(lliphi):
    """Un tema de iconos que hereda de otro, con un icono, y un tema de cursores (en el XDG_DATA_HOME falso)."""
    icons = proyecto.data_home() / "icons"
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48"><rect width="48" height="48" fill="#c93436"/></svg>'
    for tema, hereda, iconos_ in (("Falso", "Base", ["folder-red"]), ("Base", "", ["folder", "folder-blue"])):
        (icons / tema / "48x48" / "places").mkdir(parents=True)
        (icons / tema / "index.theme").write_text(
            f"[Icon Theme]\nName={tema}\nInherits={hereda}\nDirectories=48x48/places\n\n[48x48/places]\nSize=48\nContext=Places\nType=Fixed\n",
            encoding="utf-8")
        for n in iconos_:
            (icons / tema / "48x48" / "places" / f"{n}.svg").write_text(svg, encoding="utf-8")
    (icons / "Cursores" / "cursors").mkdir(parents=True)
    _xcursor(icons / "Cursores" / "cursors" / "left_ptr")
    return icons


def test_iconos_y_xcursor(temas_falsos):
    from lliphi_studio import iconos
    t = iconos.temas()
    assert {"Falso", "Base", "Cursores"} <= set(t)
    assert iconos.cadena("Falso", t)[:2] == ["Falso", "Base"]
    ruta, de = iconos.buscar("Falso", "folder", 48, t)
    assert de == "Base" and ruta.name == "folder.svg"                    # heredado
    assert iconos.nombres(t["Falso"], "Places") == ["folder-red"]
    im = iconos.leer_xcursor(temas_falsos / "Cursores" / "cursors" / "left_ptr")
    assert iconos.tamanos(im) == [24, 32] and len(im) == 4 and im[0].retardo == 50 and len(im[0].pixeles) == 24 * 24 * 4
    assert iconos.cursores(t["Cursores"]) == ["left_ptr"]


def test_pagina_de_iconos_organiza_en_un_borrador(ventana, app, temas_falsos):
    v = ventana("iconos")
    pag = v.paginas["iconos"]
    pag.c_oscuro.setCurrentText("Falso")
    assert proyecto.leer_borrador("iconos-cursores")["iconos"]["oscuro"] == "Falso"
    assert '"oscuro": "Falso"' in pag.editor.diff.toPlainText()
    for i in range(pag.arbol.topLevelItemCount()):
        g = pag.arbol.topLevelItem(i)
        for j in range(g.childCount()):
            if g.child(j).data(0, 0x0100) == ("Cursores", "Cursores"):
                pag.arbol.setCurrentItem(g.child(j))
    assert pag.pila.currentWidget() is pag.cursores and list(pag.cursores.cuadros) == ["left_ptr"]
    pag.cursores.grab()
    pag._descartar()
    assert proyecto.diff_ajustes("iconos-cursores", pag.datos) == ""


def test_pantallas_carga_de_verdad_y_maquetas(ventana, app):
    v = ventana("pantallas")
    pag = v.paginas["pantallas"]
    assert pag.caso == "carga" and pag.qml is not None and not pag.qml.errors()
    assert pag.qml.rootObject().property("stage") == 1
    for fila in range(1, pag.lista.count()):
        pag.lista.setCurrentRow(fila)
        if pag.caso != "carga":
            assert pag.pila.currentWidget() is pag.maqueta
            pag.maqueta.grab()
    assert "Splash.qml" in [pag.archivos.item(i).text() for i in range(pag.archivos.count())] or pag.caso != "carga"
