"""studio/tests/test_ventana_lliphi.py — Lliphi Studio (QML + Kirigami sobre gui-comun 3.0) abre su ventana sin pantalla
con el Python del sistema sobre una COPIA del proyecto: la ventana entera (acciones con su estado de operación, menús,
barra, cada área, el plan de instalar en seis pasos, la sesión de prueba con su confirmación), cada componente QML,
`--smoke`, y las reglas de la familia (sin colores propios en la interfaz —los de la paleta y las maquetas son
datos—, sin marca dentro, sin QtWidgets, gui_comun sin subir carpetas). Ninguna prueba instala nada en la sesión real
ni abre una sesión anidada: esta prueba lo vigila sobre las demás."""
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
a, c, e, i, w = piezas["acciones"], piezas["centro"], piezas["espacio"], piezas["interfaz"], piezas["escritura"]
paginas = []
for area in [x["id"] for x in c.areas]:
    a.accion("ver.area." + area).disparar(); app.app.processEvents()
    paginas.append([area, len(c.tarjetas), raiz.property("title") if raiz else ""])
c.irADestino("konsole"); app.app.processEvents()
pares = [p["estado"] for p in c.pares]
a.accion("escr.instalar").disparar(); app.app.processEvents()
plan = w.plan
pedida = []
a.confirmacionPedida.connect(lambda p: pedida.append(p))
a.accion("sesion.arrancar").disparar(); app.app.processEvents()          # pide confirmación: no arranca nada
for q in ("respaldos", "sesion", "venv"):
    i.pedir.emit(q, {}); app.app.processEvents()
a.accion("app.ajustes").disparar(); app.app.processEvents()
operaciones = {n: [a.accion(n).operacion, a.accion(n).requiereConfirmacion] for n in a.nombres() if a.accion(n).operacion}
QTimer.singleShot(800, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores, "acciones": a.nombres(), "menus": [x["titulo"] for x in a.menus], "barra": a.barra, "paginas": paginas,
                  "pares": pares, "plan": {k: plan.get(k) for k in ("titulo", "tipo", "orden", "estadoOperacion")}, "afectados": len(plan.get("afectados", [])),
                  "pedida": [p.get("nombre") for p in pedida], "consecuencias": pedida[0].get("consecuencias", "") if pedida else "",
                  "activa": piezas["tareas"].activa, "operaciones": operaciones, "contexto": e.contexto}))
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
open(ruta, "w").write('import QtQuick\\nimport GuiComun\\nimport "file://%s/%s"\\nVentanaBase { id: ventana; acciones: accionesStudio; tareas: tareasStudio; consola: consolaStudio; visible: false; %s { id: objeto } }\\n' % (str(aplicacion.QML_DIR), carpeta, nombre))
ok = app.cargar(ruta)
QTimer.singleShot(400, app.app.quit); app.app.exec(); app.cerrar()
print(json.dumps({"ok": ok, "errores": errores}))
"""


def _graves(errores):
    return [e for e in errores if "TypeError" in e or "ReferenceError" in e or "is not a type" in e or "Cannot assign" in e or "Unable to assign" in e]


@requiere_sistema
def test_abre_y_cierra_su_ventana(muestra_sesion):
    r = correr_python(ABRIR, entorno_gui(muestra_sesion), plazo=300)
    assert r.returncode == 0, f"código {r.returncode}\n{r.stderr[-3000:]}"
    datos = json.loads(r.stdout.strip().splitlines()[-1])
    assert datos["ok"], r.stderr[-3000:]
    assert not _graves(datos["errores"]), "\n".join(_graves(datos["errores"]))
    for n in ("archivo.ajustes", "archivo.generado", "archivo.terminal", "archivo.tokens", "archivo.esquema", "ver.area.diseno", "ver.area.esquemas",
              "ver.area.plasma", "ver.area.kvantum", "ver.area.konsole", "ver.area.editores", "ver.area.fondos", "ver.area.tipografia", "ver.area.iconos",
              "ver.area.otros", "ver.salida", "ver.releer", "escr.generar", "escr.instalar", "escr.generar_todo", "escr.instalar_todo", "escr.desinstalar",
              "escr.ejecutar", "escr.ejecutar.generar", "escr.ejecutar.instalar", "escr.ejecutar.desinstalar", "escr.cancelar",
              "op.verificar", "op.validar", "op.paleta", "op.estado", "op.comprobar", "op.dependencias", "op.pruebas", "op.licencias", "op.empaquetar", "op.sitio",
              "op.sesion_estado", "op.sesion_recargar", "op.sesion_capturar", "op.sesion_cerrar", "op.revertir", "op.aplicar", "proyecto.verificar", "proyecto.comprobar",
              "sesion.arrancar", "herr.respaldos", "herr.sesion", "herr.sitio", "herr.lanzador", "herr.venv", "ayuda.manual", "ayuda.arquitectura",
              "ventana.paleta", "ventana.pantalla_completa", "app.ajustes", "app.acerca", "app.salir"):
        assert n in datos["acciones"], n
    assert "ventana.navegacion" not in datos["acciones"] and "op.instalar_todo" not in datos["acciones"]   # VentanaBase; instalar va en seis pasos
    assert datos["menus"] == ["&Archivo", "&Ver", "&Destino", "&Proyecto", "&Herramientas", "A&justes", "Ay&uda"]
    assert datos["barra"] == ["ver.releer", "proyecto.verificar", "|", "escr.generar", "escr.instalar", "|", "escr.ejecutar"]
    paginas = {p[0]: p for p in datos["paginas"]}
    assert set(paginas) == {"diseno", "esquemas", "plasma", "kvantum", "konsole", "editores", "fondos", "tipografia", "iconos", "otros"}
    assert paginas["esquemas"][1] == 1 and paginas["plasma"][1] >= 5 and paginas["otros"][1] >= 5 and paginas["diseno"][1] == 0
    assert paginas["konsole"][2] == "Konsole y terminales — Lliphi Studio"
    assert datos["pares"] == ["falta", "falta"]                                  # el HOME de la muestra está vacío
    assert datos["plan"]["tipo"] == "instalar" and datos["plan"]["orden"] == "python herramientas/instalar.py --modulos konsole --aplicar"
    assert datos["plan"]["estadoOperacion"] == "instalacion" and datos["afectados"] == 2
    # la sesión de prueba: su acción pide confirmación con lo que pesa, y no arranca nada
    assert datos["pedida"] == ["sesion.arrancar"] and "RAM" in datos["consecuencias"] and "sesiones" in datos["consecuencias"] and not datos["activa"]
    op = datos["operaciones"]
    assert op["escr.ejecutar.instalar"] == ["instalacion", True] and op["escr.ejecutar.desinstalar"] == ["eliminacion", True]
    assert op["escr.ejecutar.generar"] == ["escritura", True] and op["sesion.arrancar"] == ["escritura", True]
    assert op["escr.instalar"] == ["lectura", False] and op["op.paleta"] == ["simulacion", False] and op["op.aplicar"] == ["escritura", True]
    assert datos["contexto"].startswith("Konsole y terminales · Konsole")


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
    """Ningún color ni tipografía fija en la interfaz: los colores de Lliphi solo aparecen como datos (la paleta: `color: m.hex`;
    las maquetas: `colores`, de servicios/diseno.py)."""
    malos = []
    for qml in QML.rglob("*.qml"):
        for n, linea in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            sin_comentario = linea.split("//")[0]
            if re.search(r'"#[0-9a-fA-F]{3,8}"', sin_comentario) or re.search(r'\bfont\.(pointSize|pixelSize|family)\s*:\s*["\d]', sin_comentario):
                malos.append(f"{qml.relative_to(STUDIO)}:{n}: {linea.strip()}")
    assert not malos, "\n".join(malos)
    paleta = (QML / "componentes" / "PaginaDiseno.qml").read_text(encoding="utf-8")
    assert "color: m.hex" in paleta and "Kirigami.Theme" in paleta
    assert "property var colores" in (QML / "componentes" / "Maqueta.qml").read_text(encoding="utf-8")


def test_sin_marca_dentro_de_la_ventana():
    codigo = "\n".join(l.split("//")[0] for l in (QML / "Main.qml").read_text(encoding="utf-8").splitlines())
    assert "logotipo" not in codigo.lower() and "logo_svg" not in codigo and "marca.svg" not in codigo
    assert 'text: "Lliphi Studio"' not in codigo


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
