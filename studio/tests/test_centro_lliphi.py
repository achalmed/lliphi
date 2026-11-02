"""studio/tests/test_centro_lliphi.py — el centro de configuración de la reingeniería (2026-11-02) sobre una COPIA del
proyecto y su HOME falso (`studio/muestra.py`): el sistema de diseño (muestras, escalas, contrastes WCAG con veredicto,
la maqueta), las áreas (cada destino en una sola), lo instalado frente a lo generado por archivo (falta · igual ·
distinto · ajeno), los planes de los seis pasos y, de verdad, instalar y desinstalar `konsole` **en el HOME de la copia**
con su verificación y su informe. Nada se instala en la sesión real ni se abre una sesión anidada: antes de ejecutar,
la prueba comprueba que HOME y XDG_DATA_HOME son los de la copia."""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

import pytest

from conftest import requiere_binding


# ------------------------------------------------------------------------------------------------ servicios (sin Qt)

def test_sistema_de_diseno_con_su_color_real(entorno_sesion):
    from lliphi_app.servicios import diseno
    s = diseno.sistema()
    assert [v["variante"] for v in s["variantes"]] == ["claro", "oscuro"]
    for v in s["variantes"]:
        ls = [m["l"] for m in v["neutros"]]
        assert ls == sorted(ls) and len(ls) >= 8                     # la escala de neutros, de oscuro a claro
        assert all(m["hex"].startswith("#") and m["oklch"].startswith("oklch(") for m in v["neutros"] + v["acentos"])
        assert len(v["ansi"]) == 16 and v["terminal"]["fondo"].startswith("#")
        pares = {c["que"]: c for c in v["contrastes"]}
        texto = pares["Texto sobre la ventana"]
        assert texto["razon"] >= 7 and texto["veredicto"] == "AAA" and texto["nivel"] == "positivo"
        assert pares["Separador"]["tipo"] == "decorativo" and pares["Separador"]["nivel"] == ""
        assert v["fallan"] == sum(c["nivel"] == "negativo" for c in v["contrastes"])
        assert {"fondo_ventana", "texto_normal", "acento_base", "seleccion_fondo"} <= set(v["maqueta"])
    assert s["tipografia"]["familias"]["interfaz"][0] == "Inter"
    assert diseno.veredicto(4.6, "texto") == ("AA", "positivo") and diseno.veredicto(3.2, "texto") == ("AA grande", "neutro")
    assert diseno.veredicto(2.9, "grafico")[1] == "negativo" and diseno.veredicto(8, "texto")[0] == "AAA"


def test_areas_reparten_los_destinos(entorno_sesion):
    from lliphi_app.servicios import areas, proyecto
    lista = areas.areas()
    ids = [d for a in lista for d in a["destinos"]]
    assert len(ids) == len(set(ids))                                 # cada destino en una sola área
    assert set(ids) == {m.id for m in proyecto.modulos()}            # y todos tienen la suya
    assert areas.area_de("konsole") == "konsole" and areas.area_de("obsidian") == "otros" and areas.area_de("esquema") == "esquemas"


def test_instalado_frente_a_generado(entorno_sesion):
    from lliphi_app.servicios import areas, destinos, proyecto
    casa = Path(os.environ["XDG_DATA_HOME"])
    assert str(casa).startswith(os.environ["HOME"])                  # el HOME de la copia, nunca el real
    pares = areas.comparar("konsole")
    assert [p["estado"] for p in pares] == ["falta", "falta"] and pares[0]["destinoCorto"].startswith("~/")
    origen, destino = Path(pares[0]["origen"]), Path(pares[0]["destino"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(origen, destino)
        assert areas.comparar("konsole")[0]["estado"] == "igual"
        destino.write_text(destino.read_text(encoding="utf-8") + "\n# añadido a mano\n", encoding="utf-8")
        p = areas.comparar("konsole")[0]
        assert p["estado"] == "ajeno"                                # cambiado y sin manifiesto: Lliphi no lo instaló
        d = areas.diferencia(p["origen"], p["destino"])
        assert d["izquierda"].startswith("Instalado") and d["quitadas"] == 2 and not d["binario"]   # la línea en blanco y el comentario
        t = areas.tarjeta(proyecto.modulo("konsole"), destinos.Verificacion(Path(os.environ["XDG_CACHE_HOME"]) / "nada.json"),
                          {"instalado": False, "modulos": [], "rutas": []})
        assert t["compatibilidad"]["estado"] and t["instalable"] and t["instalacion"] == "Sin instalar"
    finally:
        destino.unlink(missing_ok=True)


def test_planes_de_los_seis_pasos(entorno_sesion):
    from lliphi_app.servicios import pasos
    plan = pasos.planificar_instalar(["konsole"])
    d = plan.como_dict()
    assert d["estadoOperacion"] == "instalacion" and d["orden"] == "python herramientas/instalar.py --modulos konsole --aplicar"
    assert [a["accion"] for a in d["afectados"]] == ["crear", "crear"]
    assert not any(c["motivo"].startswith("falta plasmashell") and os.environ.get("QT_QPA_PLATFORM") != "offscreen" for c in d["conflictos"])
    des = pasos.planificar_desinstalar()
    assert des.bloqueado and "sin manifiesto" in des.conflictos[0]["motivo"]
    gen = pasos.planificar_generar(["esquema"])
    assert gen.como_dict()["estadoOperacion"] == "escritura" and gen.afectados[0]["accion"] == "regenerar"
    assert "esquema" in gen.orden.texto() and "--aplicar" in gen.orden.texto()
    md = pasos.informe(plan, 0, (True, "2 ruta(s)"), 1.2)
    assert md.startswith("# Instalar konsole") and "| `~/.local/share/konsole/" in md and "verificación: pasa" in md


# ----------------------------------------------------------------------------------------------------- controladores

def _esperar(app, tareas, segundos=120):
    inicio = time.monotonic()
    while tareas.activa and time.monotonic() - inicio < segundos:
        app.processEvents()
        time.sleep(0.05)
    for _ in range(20):
        app.processEvents()


def _armar(ajustes_temporales):
    from gui_comun.consola import Consola
    from gui_comun.tareas import Tareas
    from lliphi_app.controladores.ajustes import Ajustes
    from lliphi_app.controladores.centro import Centro
    from lliphi_app.controladores.destinos import Destinos
    from lliphi_app.controladores.escritura import Escritura
    from lliphi_app.controladores.espacio import Espacio
    cache = ajustes_temporales / "cache" / "studio"
    consola = Consola()
    tareas = Tareas(consola)
    espacio = Espacio(consola, Ajustes())
    destinos = Destinos(espacio, consola, tareas, cache=cache)
    return dict(consola=consola, tareas=tareas, destinos=destinos, centro=Centro(destinos), escritura=Escritura(destinos, consola, tareas, cache=cache), cache=cache)


@requiere_binding
def test_centro_areas_tarjetas_y_pares(app, entorno_sesion, ajustes_temporales):
    p = _armar(ajustes_temporales)
    c = p["centro"]
    assert c.area == "diseno" and c.tarjetas == [] and len(c.sistema["variantes"]) == 2
    c.fijarArea("konsole")
    assert [t["id"] for t in c.tarjetas] == ["konsole", "terminales"] and c.destino == "konsole"
    assert [x["estado"] for x in c.pares] == ["falta", "falta"] and c.cuentaPares["falta"] == 2 and c.par == 0
    assert c.diferencia["vacia"] and "no está en el escritorio" in c.diferencia["notas"][0].lower()
    c.fijarArea("tipografia")
    assert any(f["familia"] == "Inter" for f in c.fuentes)
    c.fijarArea("fondos")
    assert c.fondos and c.fondos[0]["claro"].startswith("file://")
    c.irADestino("obsidian")
    assert c.area == "otros" and c.destino == "obsidian"


@requiere_binding
def test_instalar_y_desinstalar_en_seis_pasos_en_el_home_de_la_copia(app, entorno_muestra, ajustes_temporales, monkeypatch):
    """De verdad, pero en la copia: instalar konsole (dos .colorscheme) y desinstalarlo, con la verificación y el informe."""
    casa = Path(os.environ["HOME"])
    assert str(entorno_muestra.casa) == str(casa) and os.environ["XDG_DATA_HOME"].startswith(str(casa))   # nunca el HOME real
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)          # plasmashell --version se cae con offscreen (instalar.py lo pide)
    p = _armar(ajustes_temporales)
    w = p["escritura"]
    w.planificar("instalar", ["konsole"])
    assert w.alcanzado == 3 and w.plan["cambian"] == 2
    if w.plan["bloqueado"]:
        pytest.skip("el instalador no corre en este entorno: " + "; ".join(c["motivo"] for c in w.plan["conflictos"]))
    assert w.puedeEjecutar and "Orden: python herramientas/instalar.py --modulos konsole --aplicar" in w.consecuencias()
    terminadas = []
    w.terminada.connect(lambda t, c: terminadas.append((t, c)))
    w.ejecutar()
    _esperar(app, p["tareas"])
    assert terminadas == [("instalar", 0)] and w.alcanzado == 6
    assert w.resultado["verificado"] is True and "con la suma de lo generado" in w.resultado["detalle"]
    assert (casa / ".local" / "share" / "konsole" / "Lliphi Oscuro.colorscheme").is_file()
    assert Path(w.resultado["rutaInforme"]).is_file() and w.resultado["informe"].startswith("# Instalar konsole")
    w.planificar("desinstalar", [])
    assert not w.plan["bloqueado"] and any(a["accion"] == "retirar" for a in w.plan["afectados"])
    w.ejecutar()
    _esperar(app, p["tareas"])
    assert terminadas[-1] == ("desinstalar", 0) and w.resultado["verificado"] is True
    assert not (casa / ".local" / "share" / "konsole" / "Lliphi Oscuro.colorscheme").exists()


@requiere_binding
def test_con_un_ajeno_no_se_ejecuta(app, entorno_muestra, ajustes_temporales, monkeypatch):
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    destino = Path(os.environ["XDG_DATA_HOME"]) / "konsole" / "Lliphi Claro.colorscheme"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("[General]\nDescription=otro tema\n", encoding="utf-8")
    p = _armar(ajustes_temporales)
    w = p["escritura"]
    avisos = []
    w.aviso.connect(lambda t, k: avisos.append(t))
    w.planificar("instalar", ["konsole"])
    assert w.plan["bloqueado"] and any("Lliphi no instaló" in c["motivo"] for c in w.plan["conflictos"]) and not w.puedeEjecutar
    w.ejecutar()
    assert not p["tareas"].activa and avisos and "bloquea" in avisos[-1]
    assert destino.read_text(encoding="utf-8").startswith("[General]\nDescription=otro tema")
