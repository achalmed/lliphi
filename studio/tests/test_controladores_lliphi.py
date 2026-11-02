"""studio/tests/test_controladores_lliphi.py — los controladores de la ventana en proceso (sin QML) sobre una COPIA del
proyecto: espacio (filtros por rol y estado), destinos (la tabla, los contadores, el actual con su Resumen, la paleta, las
diferencias y el registro), operaciones (F5 simula o enseña el plan, Ctrl+Intro aplica sobre la copia, los motivos de
no poder, el registro y el plan en la caché) y ajustes. Con el .venv del proyecto corre generar.py de verdad sobre la
copia; nada instala en la sesión real ni abre una sesión anidada."""
from __future__ import annotations

import time

import pytest

from conftest import HAY_VENV, requiere_binding


def _esperar(app, tareas, segundos=120):
    inicio = time.monotonic()
    while tareas.activa and time.monotonic() - inicio < segundos:
        app.processEvents()
        time.sleep(0.05)
    app.processEvents()


@pytest.fixture
def piezas(app, entorno_muestra, ajustes_temporales):
    from gui_comun.consola import Consola
    from gui_comun.tareas import Tareas
    from lliphi_app.controladores.ajustes import Ajustes
    from lliphi_app.controladores.destinos import Destinos
    from lliphi_app.controladores.espacio import Espacio
    from lliphi_app.controladores.operaciones import Operaciones
    cache = ajustes_temporales / "cache" / "studio"
    consola = Consola()
    tareas = Tareas(consola)
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes)
    destinos = Destinos(espacio, consola, tareas, cache=cache)
    operaciones = Operaciones(espacio, destinos, ajustes, consola, tareas, cache=cache)
    yield dict(consola=consola, tareas=tareas, espacio=espacio, destinos=destinos, operaciones=operaciones, ajustes=ajustes, muestra=entorno_muestra, cache=cache)
    _esperar(app, tareas, 10)


@requiere_binding
def test_espacio_y_tabla(app, piezas):
    e, d = piezas["espacio"], piezas["destinos"]
    assert e.rol == "" and e.estado == "" and e.nombreNavegacion == "rol" and e.textoFiltro == "todos los destinos"
    assert d.total >= 20 and d.modelo.rowCount() == d.total
    c = d.contadores
    assert c["global"] == 1 and c["modulo"] >= 5 and c["complemento"] >= 10 and c["sin_comprobar"] == d.total and c["sin_instalar"] + c["no_instalable"] == d.total
    e.fijarRol("complemento")
    assert e.nombreNavegacion == "rol.complemento" and d.modelo.rowCount() == c["complemento"]
    e.fijarEstado("desfasado")
    assert e.nombreNavegacion == "estado.desfasado" and d.modelo.rowCount() == 0
    e.fijarEstado("")
    e.fijarRol("")
    assert d.modelo.rowCount() == d.total
    assert [f["nombre"] for f in d.filasRoles] == ["rol", "rol.global", "rol.modulo", "rol.complemento"] and d.filasRoles[0]["contador"] == d.total
    assert [f["nombre"] for f in d.filasEstados][:3] == ["estado.al_dia", "estado.desfasado", "estado.sin_comprobar"]
    assert d.resumen.startswith(f"{d.total} destinos · 0 al día · 0 desfasados · {d.total} sin comprobar")
    assert d.fechaVerificacion == "nunca en este studio" and not d.hayInstalacion and "no está instalado" in d.textoInstalacion


@requiere_binding
def test_destino_actual(app, piezas):
    e, d = piezas["espacio"], piezas["destinos"]
    assert not d.hayActual and d.resumenMarkdown == "" and d.diferencias == ""
    e.fijarRol("complemento")
    assert d.filaDe("esquema") < 0
    assert d.irA("esquema")                                                   # fuera del filtro: lo quita y lo elige
    assert e.rol == "" and d.hayActual and d.id == "esquema" and d.textoRol == "Módulo" and d.filaDe("esquema") >= 0
    assert d.resumenMarkdown.startswith("# Esquemas de color") and d.instalable and d.generable
    assert d.carpetaGenerado == str(piezas["muestra"].lliphi / "generado" / "esquema") and d.archivoAjustes.endswith("modulos/esquema/ajustes.json")
    assert d.archivoManifiesto.endswith("modulos/esquema/modulo.json")
    assert d.textoGenerado == "Sin comprobar" and d.textoEstadoInstalacion == "Sin instalar" and d.nDiferencias == 0
    assert len(d.paleta) == 6 and d.paleta[1]["variante"] == "oscuro"
    d.registrar_verificacion(["esquema/difiere: LliphiOscuro.colors"])
    assert d.textoGenerado == "Desfasado" and d.nivelGenerado == "negativo" and d.nDiferencias == 1 and "difiere: LliphiOscuro.colors" in d.diferencias
    assert d.contadores["desfasado"] == 1 and d.contadores["al_dia"] == d.total - 1 and d.fechaVerificacion != "nunca en este studio"
    d.fijarFila(0)
    assert d.id == "global" and d.textoGenerado == "Al día" and d.textoRol == "Tema global"
    assert not d.irA("no-existe") and d.id == "global"
    d.anotar("global", "salida de prueba")
    assert d.registro == "salida de prueba"
    assert d.respaldos == [] and d.sesiones == []                                     # el HOME falso está vacío
    nombres = [x["nombre"] for x in d.entradas_paleta("")]
    assert "destino.esquema" in nombres and "destino.konsole" in nombres


@requiere_binding
def test_operaciones_disponibilidad_y_plan(app, piezas):
    d, o, a = piezas["destinos"], piezas["operaciones"], piezas["ajustes"]
    assert o.actual == "generar" and o.verbo == "Simular" and o.escribe and o.sobreDestino and not o.instala
    assert not o.puedeSimular and o.motivoNoSimular == "Elige primero un destino en la tabla." and not o.puedeAplicar
    d.irA("esquema")
    assert o.puedeSimular and o.puedeAplicar and o.ordenSimular == "python herramientas/generar.py --modulos esquema" and o.ordenAplicar.endswith("--aplicar")
    assert "Orden: python herramientas/generar.py --modulos esquema --aplicar" in o.textoConfirmacion and "reescribe generado/<destino>/" in o.textoConfirmacion
    o.fijar("instalar")
    assert o.instala and "UNDO.sh" in o.textoConfirmacion and "respalda" in o.textoConfirmacion
    externo = next(x for x in d.ids if d.irA(x) and not d.generable)
    o.fijar("generar")
    assert not o.puedeSimular and "externo" in o.motivoNoSimular, externo
    d.irA("esquema")
    o.fijar("revertir")
    assert not o.puedeSimular and "Elige un respaldo" in o.motivoNoSimular
    o.fijarRespaldo("/no/existe")
    assert o.puedeSimular and o.simular() and "Elige un respaldo" in o.plan            # el plan avisa que no hay UNDO.sh
    o.fijarRespaldo("")
    o.fijar("sesion_recargar")
    assert not o.tieneSimular and not o.puedeSimular and "no tiene modo de solo lectura" in o.motivoNoSimular and o.puedeAplicar
    o.fijar("sesion_arrancar")
    a.variante = "claro"
    assert o.ordenSimular.endswith("sesion.py arrancar --variante claro") and "Consume RAM" in o.textoConfirmacion
    o.fijar("empaquetar")
    assert o.tieneSimular and o.simular()                                               # el plan lo calcula la ventana, sin correr nada
    assert "dist/" in o.plan and "lliphi-esquema-" in o.plan and o.registro == ""
    assert (piezas["cache"] / "operaciones" / "empaquetar.plan.txt").is_file()
    assert [x["id"] for x in o.lista][:2] == ["generar", "instalar"] and o.indiceActual == [x["id"] for x in o.lista].index("empaquetar")
    o.fijarPorIndice(0)
    assert o.actual == "generar"


@requiere_binding
@pytest.mark.skipif(not HAY_VENV, reason="sin el .venv del proyecto (coloraide): requirements.txt")
def test_f5_simula_y_ctrl_intro_aplica_sobre_la_copia(app, piezas):
    d, o, t, m = piezas["destinos"], piezas["operaciones"], piezas["tareas"], piezas["muestra"]
    d.irA("esquema")
    terminadas = []
    o.terminada.connect(lambda i, ap, c: terminadas.append((i, ap, c)))
    assert o.simular() and o.enCurso and not o.puedeSimular
    _esperar(app, t)
    assert terminadas == [("generar", False, 0)] and not o.enCurso
    assert "simulación" in d.registro and "generar.py --modulos esquema" in d.registro and "código de salida 0" in d.registro
    assert d.registro.startswith("# ") and "$ " not in d.registro
    assert o.plan == d.registro and o.registro == ""
    antes = sorted(p.name for p in (m.lliphi / "generado" / "esquema").iterdir())
    assert o.aplicar()
    _esperar(app, t)
    assert terminadas[-1] == ("generar", True, 0)
    assert "aplicado" in o.registro and sorted(p.name for p in (m.lliphi / "generado" / "esquema").iterdir()) == antes
    assert d.id == "esquema" and d.hayActual                                            # la recarga conserva el actual
    assert not (m.casa / ".local" / "share" / "color-schemes").exists()                 # nada llegó al HOME falso: generar no instala
    o.fijar("estado")
    assert o.verbo == "Ejecutar" and o.simular()
    _esperar(app, t)
    assert terminadas[-1][0] == "estado" and not d.hayInstalacion


@requiere_binding
def test_ajustes(app, piezas):
    a = piezas["ajustes"]
    assert a.variante == "oscuro" and a.terminal == "konsole" and a.raiz == str(piezas["muestra"].lliphi) and a.version
    a.variante = "claro"
    a.terminal = "  "
    assert a.variante == "claro" and a.terminal == "konsole"
    a.variante = "otra"
    assert a.variante == "oscuro"
    assert a.hayVenv == HAY_VENV and "venv --system-site-packages" in a.ordenVenv
