"""studio/tests/test_servicios_lliphi.py — los servicios de Lliphi Studio sin Qt sobre una COPIA del proyecto: el
proyecto (módulos, tokens, marca, órdenes con el .venv), los destinos (la fila con su estado generado e instalado, la
verificación guardada, el resumen en Markdown, la paleta como datos) y el catálogo de operaciones (cada una con su modo
de solo lectura o su plan, lo que toca, la orden exacta). Nada se instala ni se escribe fuera de la copia."""
from __future__ import annotations

import json
import subprocess
import time

import pytest

from conftest import HAY_VENV

from lliphi_app.servicios import destinos as svc
from lliphi_app.servicios import operaciones as ops
from lliphi_app.servicios import proyecto


def test_proyecto_sobre_la_copia(entorno_muestra):
    m = entorno_muestra
    assert proyecto.raiz() == m.lliphi
    modulos = proyecto.modulos()
    ids = [x.id for x in modulos]
    assert len(modulos) >= 20 and ids[0] == "global" and "esquema" in ids and "konsole" in ids
    esquema = proyecto.modulo("esquema")
    assert esquema.rol == "modulo" and esquema.clase == "paquete" and esquema.generado == m.lliphi / "generado" / "esquema"
    assert proyecto.marca()["id"] == "lliphi" and proyecto.version()
    assert set(proyecto.tokens()["primitivas"]) == {"claro", "oscuro"}
    orden = proyecto.orden("generar", "--modulos", "esquema")
    assert orden[1] == str(m.lliphi / "herramientas" / "generar.py") and orden[-2:] == ["--modulos", "esquema"]
    assert proyecto.orden("paleta")[1].endswith("modulos/esquema/paleta.py")


def test_fila_y_resumen(entorno_muestra, tmp_path):
    m = proyecto.modulo("esquema")
    v = svc.Verificacion(tmp_path / "v.json")
    sin = {"instalado": False, "modulos": [], "rutas": []}
    f = svc.fila(m, v, sin)
    assert f["destino"] == m.nombre and f["rol"] == "Módulo" and int(f["archivos"]) >= 2
    assert f["clave_generado"] == "sin_comprobar" and f["clave_instalacion"] == "sin_instalar" and f["n_destinos"] >= 2
    assert f["icono"]["destino"] and f["construccion"] != "—"
    md = svc.resumen_markdown(m, f, sin)
    assert md.startswith(f"# {m.nombre}") and "## Entrega" in md and "## Instalación" in md and "LliphiOscuro.colors" in md
    externo = next(x for x in proyecto.modulos() if x.clase == "externo")
    fe = svc.fila(externo, v, sin)
    assert fe["clave_instalacion"] == "no_instalable" and fe["archivos"] == "—"


def test_verificacion_guardada(entorno_muestra, tmp_path):
    v = svc.Verificacion(tmp_path / "v.json")
    assert v.fecha == 0 and not v.vigente
    v.registrar(["esquema/difiere: LliphiOscuro.colors", "konsole/falta en lo versionado: Lliphi.colorscheme"])
    assert v.vigente and v.diferencias == {"esquema": ["difiere: LliphiOscuro.colors"], "konsole": ["falta en lo versionado: Lliphi.colorscheme"]}
    assert v.estado(proyecto.modulo("esquema"), 4) == "desfasado" and v.estado(proyecto.modulo("global"), 10) == "al_dia"
    v2 = svc.Verificacion(tmp_path / "v.json")                              # se relee del disco
    assert v2.diferencias == v.diferencias and v2.vigente
    (entorno_muestra.lliphi / "tokens" / "tokens.json").touch()             # las fuentes cambiaron después: caduca
    time.sleep(0.01)
    assert not svc.Verificacion(tmp_path / "v.json").vigente


def test_estado_instalacion_por_manifiesto(entorno_muestra):
    m = proyecto.modulo("esquema")
    pares, omitidos = svc.pares_instalacion("esquema")
    assert len(pares) >= 2 and all(o.startswith(str(entorno_muestra.lliphi)) for o, _d in pares)
    assert svc.estado_instalacion(m, {"instalado": False}, pares) == "sin_instalar"
    rutas = [{"ruta": d, "ok": True} for _o, d in pares]
    assert svc.estado_instalacion(m, {"instalado": True, "modulos": ["esquema"], "rutas": rutas}, pares) == "instalado"
    rutas[0]["ok"] = False
    assert svc.estado_instalacion(m, {"instalado": True, "modulos": ["esquema"], "rutas": rutas}, pares) == "modificado"
    assert svc.leer_estado_instalacion()["instalado"] is False                # el HOME falso no tiene nada instalado


def test_paleta_como_datos(entorno_muestra):
    grupos = svc.paleta(proyecto.tokens())
    assert [(g["grupo"], g["variante"]) for g in grupos][:2] == [("primitivas", "claro"), ("primitivas", "oscuro")]
    assert len(grupos) == 6
    c = grupos[0]["colores"][0]
    assert c["nombre"] == "neutro-0" and c["hex"].startswith("#") and len(c["hex"]) == 7 and c["oklch"].startswith("oklch(")


def test_catalogo_de_operaciones(entorno_muestra):
    ids = [o.id for o in ops.OPERACIONES]
    assert len(ids) == len(set(ids)) and {"generar", "instalar", "verificar", "validar", "paleta", "estado", "comprobar", "desinstalar", "sesion_arrancar", "revertir"} <= set(ids)
    c = ops.Contexto(proyecto.raiz(), "esquema", "claro", "")
    for o in ops.OPERACIONES:
        assert o.simular is not None or o.plan is not None or o.aplicar is not None, o.id
        assert o.titulo and o.descripcion and o.grupo in dict(ops.GRUPOS)
        if o.escribe:
            assert o.toca != "solo lee" and o.aplicar is not None, o.id
        if o.instala:
            assert o.escribe
        if o.simular is not None:
            assert o.simular(c).texto()
    assert ops.operacion("generar").simular(c).texto() == "python herramientas/generar.py --modulos esquema"
    assert ops.operacion("instalar").aplicar(c).texto().endswith("instalar.py --modulos esquema --aplicar")
    assert ops.operacion("sesion_arrancar").simular(c).texto().endswith("sesion.py arrancar --variante claro")
    assert "sesion.py cerrar" in ops.operacion("sesion_arrancar").toca
    assert "Elige un respaldo" in ops.operacion("revertir").plan(c)
    assert "dist/" in ops.operacion("empaquetar").plan(c) and "quarto render" in ops.operacion("sitio").plan(c)
    assert ops.de_grupo("destino")[0].id == "generar" and all(o.sobre_destino for o in ops.de_grupo("destino"))


@pytest.mark.skipif(not HAY_VENV, reason="sin el .venv del proyecto (coloraide): requirements.txt")
def test_generar_en_simulacion_no_escribe(entorno_muestra):
    """La orden de F5 sobre la copia: código 0 y generado/ intacto."""
    m = entorno_muestra
    antes = {p: p.stat().st_mtime for p in (m.lliphi / "generado" / "esquema").rglob("*") if p.is_file()}
    r = subprocess.run(proyecto.orden("generar", "--modulos", "esquema"), cwd=m.lliphi, capture_output=True, text=True, timeout=120, env=dict(**m.entorno, PATH=__import__("os").environ["PATH"]))
    assert r.returncode == 0, r.stderr[-2000:]
    assert "simulación" in r.stdout
    assert {p: p.stat().st_mtime for p in (m.lliphi / "generado" / "esquema").rglob("*") if p.is_file()} == antes
    estado = json.loads(subprocess.run(proyecto.orden("instalar", "estado", "--json"), cwd=m.lliphi, capture_output=True, text=True, timeout=60,
                                       env=dict(**m.entorno, PATH=__import__("os").environ["PATH"])).stdout)
    assert estado["instalado"] is False
