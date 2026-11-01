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
