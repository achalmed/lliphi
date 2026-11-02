"""studio/tests/test_proyecto.py — la capa sin Qt de Lliphi Studio (2026-11-01): módulos, ajustes, borradores,
respaldos y las órdenes con --json. Todo sobre una copia del proyecto y un HOME falso (conftest.py)."""
from __future__ import annotations

import json

from lliphi_studio import proyecto


def test_los_diecisiete_modulos_y_los_seis(lliphi):
    mods = proyecto.modulos()
    assert len(mods) == 17 and mods[0].id == "global"
    assert [m.id for m in mods if m.rol == "modulo"] == ["esquema", "estilo", "decoracion", "iconos-cursores",
                                                          "carga-bloqueo", "disposicion"]
    assert ("global", "disposicion", "integra") in proyecto.aristas()
    assert set(proyecto.SECCION) == {m.id for m in mods if m.rol == "modulo"}


def test_ajustes_canonicos_y_guardar(lliphi):
    for id_ in proyecto.EDITABLES:
        texto = proyecto.modulo(id_).ajustes.read_text(encoding="utf-8")
        assert proyecto.volcar(id_, json.loads(texto)) == texto, id_
        assert proyecto.diff_ajustes(id_, proyecto.leer_ajustes(id_)) == ""
    d = proyecto.leer_ajustes("decoracion")
    d["rc"]["TitleHeight"] = "22"
    assert '+    "TitleHeight": "22"' in proyecto.diff_ajustes("decoracion", d)
    ruta = proyecto.guardar_ajustes("decoracion", d)
    assert ruta.is_relative_to(lliphi) and proyecto.leer_ajustes("decoracion")["rc"]["TitleHeight"] == "22"


def test_borrador_fuera_del_proyecto(lliphi):
    b = proyecto.leer_borrador("esquema")
    b["acento"]["oscuro"] = "azul"
    ruta = proyecto.guardar_borrador("esquema", b)
    assert not ruta.is_relative_to(lliphi) and "lliphi-studio" in str(ruta)
    assert proyecto.leer_borrador("esquema")["acento"]["oscuro"] == "azul"
    assert proyecto.leer_ajustes("esquema")["acento"]["oscuro"] == "rojo"
    proyecto.descartar_borrador("esquema")
    assert proyecto.leer_borrador("esquema")["acento"]["oscuro"] == "rojo"


def test_respaldos_del_instalador(lliphi, tmp_path):
    assert proyecto.respaldos() == []
    r = proyecto.state_lliphi() / "respaldos" / "2026-11-01_120000"
    r.mkdir(parents=True)
    (r / "UNDO.sh").write_text("#!/bin/bash\n", encoding="utf-8")
    assert [x.carpeta.name for x in proyecto.respaldos()] == ["2026-11-01_120000"]


def test_ordenes_en_json(lliphi):
    v = proyecto.correr_json("generar", "validar")
    assert v and v["valido"], v
    e = proyecto.correr_json("instalar", "estado")
    assert e["instalado"] is False
    assert proyecto.orden("paleta")[1].endswith("modulos/esquema/paleta.py")
