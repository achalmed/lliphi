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
