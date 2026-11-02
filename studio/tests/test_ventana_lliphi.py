"""studio/tests/test_ventana_lliphi.py — Lliphi Studio (QML + Kirigami sobre gui-comun 2.7) abre su ventana sin pantalla
con el Python del sistema sobre una COPIA del proyecto: la ventana entera (acciones, menús, barra, resumen, el destino
elegido, una simulación de generar), cada componente QML, `--smoke`, y las reglas de la familia (sin colores propios
en la interfaz —los de la Paleta son datos—, sin marca dentro, sin QtWidgets, gui_comun sin subir carpetas). Ninguna
prueba instala nada en la sesión real ni abre una sesión anidada: esta prueba lo vigila sobre las demás."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from conftest import HAY_VENV, PYTHON_SISTEMA, REPO, STUDIO, correr_python, entorno_gui, requiere_sistema

QML = STUDIO / "lliphi_app" / "qml"
PRUEBAS = STUDIO / "tests"

ABRIR = """
import sys, json, os, time; sys.path.insert(0, sys.argv[1])
from lliphi_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("lliphi-studio", "Lliphi Studio", version="prueba", organizacion="lliphi-pruebas", nombre_ajustes="Lliphi Studio pruebas")
piezas = aplicacion.construir(app, leer_instalacion=False)
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
ok = app.cargar(aplicacion.QML_DIR / "Main.qml")
raiz = app.motor.rootObjects()[0] if ok else None
a, d, o, e, i = piezas["acciones"], piezas["destinos"], piezas["operaciones"], piezas["espacio"], piezas["interfaz"]
sin = (a.accion("op.simular").habilitada, a.accion("op.aplicar").visible, a.accion("op.aplicar").habilitada, a.accion("archivo.generado").habilitada)
d.irA("esquema"); app.app.processEvents()
con = (a.accion("op.simular").habilitada, a.accion("op.aplicar").habilitada, a.accion("op.simular").textoPlano, o.actual, a.accion("archivo.generado").habilitada)
corrio = o.simular() if os.environ.get("LLIPHI_CON_VENV") == "1" else None
inicio = time.monotonic()
while piezas["tareas"].activa and time.monotonic() - inicio < 120:
    app.app.processEvents(); time.sleep(0.05)
app.app.processEvents()
for n in range(5):
    i.pedir.emit("pestana", {"indice": n}); app.app.processEvents()
for q in ("respaldos", "sesion", "venv", "aplicar"):
    i.pedir.emit(q, {}); app.app.processEvents()
a.accion("app.ajustes").disparar(); app.app.processEvents()
titulo = raiz.property("title") if raiz else ""
contexto, registro = e.contexto, d.registro
a.accion("ver.rol.complemento").disparar(); app.app.processEvents()
QTimer.singleShot(800, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "titulo": titulo, "errores": errores, "acciones": a.nombres(), "menus": [x["titulo"] for x in a.menus], "barra": a.barra, "sin": sin,
                  "con": con, "corrio": corrio, "registro": registro[:300], "resumen": e.resumen, "contexto": contexto, "total": d.total, "rol": e.rol,
                  "marcada": a.accion("ver.rol.complemento").marcada, "nav": e.nombreNavegacion}))
"""

COMPONENTE = """
import sys, json, os; sys.path.insert(0, sys.argv[1])
from lliphi_app import aplicacion
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QTimer
app = Aplicacion("lliphi-studio", "Lliphi Studio", version="prueba", organizacion="lliphi-pruebas", nombre_ajustes="Lliphi Studio pruebas")
aplicacion.construir(app, leer_instalacion=False)
app.motor.addImportPath(str(aplicacion.QML_DIR))
errores = []
app.motor.warnings.connect(lambda avisos: errores.extend(a.toString() for a in avisos))
nombre, carpeta = sys.argv[2], sys.argv[3]
ruta = os.path.join(os.environ["XDG_CACHE_HOME"], "Prueba_" + nombre + ".qml")
os.makedirs(os.path.dirname(ruta), exist_ok=True)
open(ruta, "w").write('import QtQuick\\nimport GuiComun\\nimport "file://%s/%s"\\nVentanaStudio { id: ventana; acciones: accionesStudio; tareas: tareasStudio; consola: consolaStudio; visible: false; %s { id: objeto } }\\n' % (str(aplicacion.QML_DIR), carpeta, nombre))
ok = app.cargar(ruta)
QTimer.singleShot(400, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores}))
"""


def _graves(errores):
    return [e for e in errores if "TypeError" in e or "ReferenceError" in e or "is not a type" in e or "Cannot assign" in e or "Unable to assign" in e]


@requiere_sistema
def test_abre_y_cierra_su_ventana(muestra_sesion):
    r = correr_python(ABRIR, entorno_gui(muestra_sesion, LLIPHI_CON_VENV="1" if HAY_VENV else "0"), plazo=300)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))
    for n in ("archivo.ajustes", "archivo.manifiesto", "archivo.generado", "archivo.terminal", "archivo.copiar", "archivo.tokens", "editar.filtrar", "editar.todo",
              "ver.rol", "ver.rol.global", "ver.rol.modulo", "ver.rol.complemento", "ver.estado", "ver.estado.desfasado", "ver.releer",
              "op.generar", "op.instalar", "op.verificar", "op.validar", "op.generar_todo", "op.paleta", "op.estado", "op.comprobar", "op.instalar_todo", "op.desinstalar",
              "op.dependencias", "op.pruebas", "op.licencias", "op.empaquetar", "op.sitio", "op.sesion_estado", "op.sesion_arrancar", "op.sesion_recargar", "op.sesion_capturar",
              "op.sesion_cerrar", "op.revertir", "op.simular", "op.aplicar", "op.cancelar", "proyecto.verificar", "proyecto.comprobar",
              "destino.resumen", "destino.paleta", "destino.diferencias", "destino.registro", "herr.respaldos", "herr.sesion", "herr.sitio", "herr.lanzador", "herr.venv",
              "ayuda.manual", "ayuda.arquitectura", "ayuda.destino", "ventana.navegacion", "ventana.detalles", "ventana.inferior", "ventana.paleta", "app.ajustes", "app.acerca", "app.salir"):
        assert n in datos["acciones"], n
    assert datos["menus"] == ["&Archivo", "&Editar", "&Ver", "&Destino", "&Proyecto", "&Herramientas", "A&justes", "Ay&uda"]
    assert datos["barra"] == ["op.simular", "op.aplicar", "|", "proyecto.verificar", "proyecto.comprobar"]
    assert datos["sin"] == [False, True, False, False]
    assert datos["con"] == [True, True, "Simular", "generar", True]
    assert datos["total"] >= 20 and datos["resumen"].startswith(f"{datos['total']} destinos · ")
    assert datos["contexto"].startswith("Esquemas de color · sin comprobar · sin instalar · Generar el destino")
    assert datos["titulo"] == "Esquemas de color — Lliphi Studio"
    assert datos["rol"] == "complemento" and datos["marcada"] and datos["nav"] == "rol.complemento"
    if HAY_VENV:
        assert datos["corrio"] and "simulación · Generar el destino · esquema" in datos["registro"] and "código de salida 0" in datos["registro"]


@requiere_sistema
def test_main_smoke(muestra_sesion):
    r = subprocess.run([PYTHON_SISTEMA, str(STUDIO / "main.py"), "--smoke"], env=entorno_gui(muestra_sesion), capture_output=True, text=True, timeout=240, cwd=muestra_sesion.raiz)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    ruido = [l for l in r.stderr.splitlines() if "TypeError" in l or "ReferenceError" in l or "polish() loop" in l]
    assert not ruido, "\n".join(ruido)


COMPONENTES = sorted((p.parent.name, p.stem) for p in QML.glob("*/*.qml"))


@requiere_sistema
@pytest.mark.parametrize("carpeta,nombre", COMPONENTES, ids=[f"{c}/{n}" for c, n in COMPONENTES])
def test_cada_componente_qml(carpeta, nombre, muestra_sesion):
    r = correr_python(COMPONENTE, entorno_gui(muestra_sesion), nombre, carpeta)
    assert r.returncode == 0, r.stderr[-3000:]
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))


def test_sin_colores_propios_en_qml():
    """Ningún color ni tipografía fija en la interfaz: los colores de Lliphi solo aparecen como datos (Paleta: `color: modelData.hex`)."""
    malos = []
    for qml in QML.rglob("*.qml"):
        for n, linea in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            sin_comentario = linea.split("//")[0]
            if re.search(r'"#[0-9a-fA-F]{3,8}"', sin_comentario) or re.search(r'\bfont\.(pointSize|pixelSize|family)\s*:\s*["\d]', sin_comentario):
                malos.append(f"{qml.relative_to(STUDIO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)
    paleta = (QML / "componentes" / "Paleta.qml").read_text(encoding="utf-8")
    assert "color: modelData.hex" in paleta and "Kirigami.Theme" in paleta


def test_sin_marca_dentro_de_la_ventana():
    codigo = "\n".join(l.split("//")[0] for l in (QML / "Main.qml").read_text(encoding="utf-8").splitlines())
    assert "logotipo" not in codigo.lower() and "logo_svg" not in codigo and "marca.svg" not in codigo
    assert 'text: "Lliphi Studio"' not in codigo and "Kirigami.Heading" not in codigo.split("centro:")[0]


def test_sin_qtwidgets_y_sin_subir_carpetas():
    for py in (STUDIO / "lliphi_app").rglob("*.py"):
        texto = py.read_text(encoding="utf-8")
        assert "QtWidgets" not in texto and "gui_comun.widgets" not in texto and "gui_comun.diseno" not in texto, py
    init = (STUDIO / "lliphi_app" / "__init__.py").read_text(encoding="utf-8")
    assert "GUI_COMUN_DIR" in init and ".parent" not in init.split("def hay_gui_comun")[1]       # instalado o por la variable, nunca subiendo carpetas
    main = (STUDIO / "main.py").read_text(encoding="utf-8")
    assert main.startswith("#!/usr/bin/python3") and "import gui_comun" not in main
    assert "ninguna prueba instala nada en la sesión real" in (STUDIO / "tests" / "run.sh").read_text(encoding="utf-8")


def test_ninguna_prueba_instala_ni_abre_sesion():
    """Ninguna prueba del studio pasa --aplicar a instalar.py, ni arranca, recarga o cierra una sesión anidada, ni corre un UNDO.sh."""
    for archivo in PRUEBAS.glob("*.py"):
        if archivo.name == Path(__file__).name:
            continue
        texto = archivo.read_text(encoding="utf-8")
        for linea in texto.splitlines():
            if linea.lstrip().startswith("#") or linea.lstrip().startswith('"""'):
                continue
            assert not re.search(r'"instalar",\s*"--modulos".*"--aplicar"|"instalar",\s*"--aplicar"|"desinstalar",\s*"--aplicar"|"dependencias",\s*"--aplicar"', linea), f"{archivo.name}: {linea.strip()}"
            if "re.search" in linea:
                continue
            assert not re.search(r'"arrancar",.*"--aplicar"|"sesion",\s*"(recargar|cerrar)"|UNDO\.sh"\]', linea), f"{archivo.name}: {linea.strip()}"
        for prohibida in ('fijar("instalar")\n    assert o.aplicar', 'fijar("instalar_todo")', 'fijar("desinstalar")', 'fijar("sesion_arrancar")\n    assert o.aplicar', 'fijar("revertir")\n    assert o.aplicar'):
            assert prohibida not in texto, f"{archivo.name}: {prohibida!r}"
    assert "sesiones" not in (STUDIO / "muestra.py").read_text(encoding="utf-8").replace("sesiones de prueba", "")   # la muestra nunca crea sesiones
