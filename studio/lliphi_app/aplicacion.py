"""studio/lliphi_app/aplicacion.py — arma Lliphi Studio: la aplicación (gui_comun.nucleo), los controladores, el registro
de acciones (menú, barra, paleta, atajos) y carga `qml/Main.qml`.

Reingeniería del 2026-11-02 (`docs/reingenieria.md`): un centro de configuración del escritorio por áreas. Toda
operación existe una sola vez, aquí, en `Acciones`, con su estado de operación de `gui-comun` 3.0. Generar, instalar y
desinstalar van en seis pasos (`controladores/escritura.py`): preparar el plan es lectura; ejecutarlo (Ctrl+Intro) pide
confirmación con las consecuencias del plan y es escritura, instalación o eliminación. La sesión de prueba es una
acción propia con confirmación. Las demás órdenes del catálogo (`servicios/operaciones.py`) se corren desde los menús
Proyecto y Herramientas: las de lectura, directamente; las que escriben, tras confirmar. Python no construye interfaz;
la ventana no escribe en el proyecto ni en el escritorio por su cuenta: toda escritura es una orden de Lliphi.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from lliphi_app import APP_NAME, APP_VERSION, INSTALAR, ORG_NAME, faltan, hay_gui_comun

if not hay_gui_comun():
    raise ImportError("falta gui_comun: " + INSTALAR)

from gui_comun.acciones import Acciones, StandardKey  # noqa: E402
from gui_comun.consola import Consola  # noqa: E402
from gui_comun.nucleo import Aplicacion  # noqa: E402
from gui_comun.qt import QObject, Signal, Slot  # noqa: E402
from gui_comun.tareas import Tareas  # noqa: E402

from lliphi_app.controladores.ajustes import Ajustes  # noqa: E402
from lliphi_app.controladores.centro import Centro  # noqa: E402
from lliphi_app.controladores.destinos import Destinos  # noqa: E402
from lliphi_app.controladores.escritura import Escritura  # noqa: E402
from lliphi_app.controladores.espacio import Espacio  # noqa: E402
from lliphi_app.controladores.operaciones import Operaciones  # noqa: E402
from lliphi_app.servicios import areas as svc_areas  # noqa: E402
from lliphi_app.servicios import operaciones as ops  # noqa: E402
from lliphi_app.servicios import pasos as svc_pasos  # noqa: E402
from lliphi_app.servicios import proyecto  # noqa: E402

APP_DIR = Path(__file__).resolve().parent
QML_DIR = APP_DIR / "qml"
RECURSOS_DIR = APP_DIR / "recursos"
APP_ID = "lliphi-studio"
NOMBRE = APP_NAME
DESCRIPCION = ("El centro de configuración del tema Lliphi: por áreas (sistema de diseño, esquemas de color, Plasma, Kvantum, Konsole, "
               "editores, fondos, tipografía, iconos y otros destinos), cada una con su página; la paleta OKLCH con su color real, los "
               "contrastes WCAG con su veredicto y claro y oscuro lado a lado; de cada destino, lo instalado frente a lo generado archivo "
               "por archivo, la compatibilidad y la fecha. Generar, instalar y desinstalar en seis pasos visibles (plan, afectados, "
               "conflictos, ejecutar, verificar, informe), con el respaldo y su UNDO.sh. Las órdenes son las de Lliphi (generar.py, "
               "instalar.py, paleta.py, sesion.py); la ventana no reemplaza ninguna.")
ACENTO = "carmesi"


def datos_lanzador() -> dict:
    return dict(app_id=APP_ID, nombre=NOMBRE, comentario="El tema Lliphi: destinos, lo generado, lo instalado y la sesión de prueba",
                orden=["/usr/bin/python3", str(APP_DIR.parent / "main.py")], logo_svg=(RECURSOS_DIR / "marca.svg").read_text(encoding="utf-8"),
                acento=ACENTO, categorias="Settings;DesktopSettings;", palabras="lliphi;tema;plasma;kde;color;paleta;aurorae;iconos;cursores;")


class Interfaz(QObject):
    pedir = Signal(str, "QVariantMap")

    @Slot(str)
    def abrir(self, nombre: str) -> None:
        self.pedir.emit(nombre, {})


def construir(app: Aplicacion, cache: Path | None = None, leer_instalacion: bool = True) -> dict:
    """Crea controladores y acciones, y los expone al QML. Devuelve lo creado (para las pruebas y las capturas)."""
    consola = Consola()
    tareas = Tareas(consola)
    interfaz = Interfaz()
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes, getattr(app, "escritorio", None))
    destinos = Destinos(espacio, consola, tareas, cache=cache)
    operaciones = Operaciones(espacio, destinos, ajustes, consola, tareas, cache=cache)
    centro = Centro(destinos)
    escritura = Escritura(destinos, consola, tareas, cache=destinos._cache)
    acciones = Acciones()
    acciones.estandar(NOMBRE, paneles=False, atajos={"ventana.pantalla_completa": "F11"})
    pedir = lambda que, **datos: (lambda *_: interfaz.pedir.emit(que, datos))
    actual = lambda: centro.destino

    # --- Archivo
    acciones.registrar("archivo.ajustes", "Abrir los &ajustes del destino", "document-edit", None, "Archivo", habilitada=False, operacion="lectura",
                       al_disparar=lambda *_: espacio.abrir(centro.archivoAjustes()), descripcion="Su ajustes.json con el editor del sistema; después, Generar (Ctrl+B)")
    acciones.registrar("archivo.generado", "Mostrar lo &generado en Dolphin", "system-file-manager", "Ctrl+Shift+O", "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrirDolphin(centro.carpetaGenerado(actual())), descripcion="generado/<destino>/ señalado en Dolphin")
    acciones.registrar("archivo.terminal", "Abrir &terminal en el proyecto", "utilities-terminal", "Shift+F4", "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrirTerminal(str(proyecto.raiz())))
    acciones.registrar("archivo.tokens", "Abrir &tokens.json", "color-management", None, "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrir(str(proyecto.raiz() / "tokens" / "tokens.json")),
                       descripcion="La fuente de verdad del color (la escribe paleta.py; se edita modulos/esquema/ajustes.json)")
    acciones.registrar("archivo.esquema", "Abrir los ajustes de la &paleta", "preferences-desktop-color", None, "Archivo", operacion="lectura",
                       al_disparar=lambda *_: espacio.abrir(str(proyecto.raiz() / "modulos" / "esquema" / "ajustes.json")),
                       descripcion="modulos/esquema/ajustes.json: las ternas OKLCH de las que paleta.py escribe los tokens")
    # --- Ver: las áreas
    for i, a in enumerate(svc_areas.areas(), start=1):
        acciones.registrar(f"ver.area.{a['id']}", f"{a['titulo']}", a["icono"], f"Ctrl+{i % 10}", "Ver", marcable=True,
                           al_disparar=lambda *_, n=a["id"]: centro.fijarArea(n), descripcion=a["que"])
    acciones.registrar("ver.salida", "&Salida y registro", "utilities-terminal", "F4", "Ver", marcable=True, al_disparar=pedir("salida"),
                       descripcion="La salida íntegra de las órdenes de Lliphi y el registro")
    acciones.registrar("ver.releer", "&Releer el proyecto", "view-refresh", "F6", "Ver", operacion="lectura",
                       al_disparar=lambda *_: (destinos.recargar(), destinos.leer_instalacion()),
                       descripcion="Vuelve a leer los manifiestos, lo generado, la verificación guardada y la instalación")
    # --- Destino: los seis pasos
    def preparar(tipo: str, ids: list[str]):
        escritura.planificar(tipo, ids)
        interfaz.pedir.emit("pasos", {})
    acciones.registrar("escr.generar", "&Generar el destino…", "run-build", "Ctrl+B", "Destino", operacion="lectura",
                       al_disparar=lambda *_: preparar("generar", [actual()]), descripcion="Prepara el plan de generar.py --modulos <destino> (pasos 1–3); no escribe")
    acciones.registrar("escr.instalar", "&Instalar el destino…", "install", "Ctrl+I", "Destino", operacion="lectura",
                       al_disparar=lambda *_: preparar("instalar", [actual()]), descripcion="Prepara el plan de instalar.py --modulos <destino>: cada archivo, lo que cambia y lo ajeno")
    acciones.registrar("escr.generar_todo", "Generar &todo…", "run-build", "Ctrl+Shift+B", "Destino", operacion="lectura",
                       al_disparar=lambda *_: preparar("generar", []), descripcion="Prepara el plan de generar.py para todos los destinos")
    acciones.registrar("escr.instalar_todo", "Instalar t&odo…", "install", None, "Destino", operacion="lectura",
                       al_disparar=lambda *_: preparar("instalar", []), descripcion="Prepara el plan de instalar.py para todos los destinos instalables")
    acciones.registrar("escr.desinstalar", "&Desinstalar…", "edit-delete", None, "Destino", operacion="lectura",
                       al_disparar=lambda *_: preparar("desinstalar", []), descripcion="Prepara el plan de instalar.py desinstalar: lo que retirará y lo que queda")
    for tipo, op_ in (("generar", "escritura"), ("instalar", "instalacion"), ("desinstalar", "eliminacion")):
        acciones.registrar(f"escr.ejecutar.{tipo}", f"Ejecutar: {svc_pasos.TIPOS[tipo].lower()}…", "dialog-ok-apply", None, "Destino", operacion=op_, confirmar=True,
                           visible=False, consecuencias=escritura.consecuencias, al_disparar=lambda *_: escritura.ejecutar())
    acciones.registrar("escr.ejecutar", "&Ejecutar el plan…", "dialog-ok-apply", "Ctrl+Return", "Destino", habilitada=False,
                       al_disparar=lambda *_: escritura.hayPlan and acciones.accion(f"escr.ejecutar.{escritura.plan['tipo']}").disparar(),
                       descripcion="Paso 4: pide confirmación con lo que cambia y corre la orden; luego verifica e informa")
    acciones.registrar("escr.cancelar", "&Cancelar la orden", "process-stop", None, "Destino", habilitada=False, al_disparar=tareas.cancelar)
    # --- Proyecto · Herramientas: el catálogo de órdenes (las de leer, directas; las que escriben, tras confirmar)
    for o in ops.OPERACIONES:
        if o.id in ("generar", "instalar", "generar_todo", "instalar_todo", "desinstalar", "sesion_arrancar"):
            continue                                    # van en seis pasos o con su acción propia
        acciones.registrar(f"op.{o.id}", o.titulo, o.icono, None, dict(ops.GRUPOS)[o.grupo], operacion="simulacion" if o.escribe else "lectura",
                           al_disparar=lambda *_, i=o.id: (operaciones.fijar(i), operaciones.simular()), descripcion=o.descripcion)
    acciones.registrar("op.aplicar", "&Aplicar la orden elegida…", "dialog-ok-apply", None, "Proyecto", habilitada=False, operacion="escritura", confirmar=True,
                       consecuencias=lambda: operaciones.textoConfirmacion, al_disparar=lambda *_: operaciones.aplicar(),
                       descripcion="La orden elegida de Proyecto o Herramientas, de verdad: escribe tras confirmar")
    acciones.registrar("proyecto.verificar", "&Verificar lo generado", "view-refresh", "Ctrl+T", "Proyecto", operacion="lectura",
                       al_disparar=lambda *_: (operaciones.fijar("verificar"), operaciones.simular()), descripcion="Construye en un temporal y compara: actualiza «Al día»")
    acciones.registrar("proyecto.comprobar", "&Comprobar la instalación", "checkmark", "Ctrl+Shift+T", "Proyecto", operacion="lectura",
                       al_disparar=lambda *_: (operaciones.fijar("comprobar"), operaciones.simular()))
    # --- Herramientas: la sesión de prueba, con su acción y su confirmación
    def consecuencias_sesion() -> str:
        peso = svc_areas.peso_sesiones()
        return ("Arranca un kwin_wayland y un plasmashell anidados (un Plasma entero en RAM) y deja una casa nueva en "
                f"$XDG_CACHE_HOME/lliphi/sesiones/ (cientos de MB; ya hay {peso}). Tu sesión real no se toca; «Cerrar la sesión de prueba» la "
                f"termina y la carpeta queda.\n\nOrden: {ops.operacion('sesion_arrancar').aplicar(operaciones.contexto()).texto()}")
    acciones.registrar("sesion.arrancar", "&Arrancar la sesión de prueba…", "window-new", None, "Herramientas", operacion="escritura", confirmar=True,
                       consecuencias=consecuencias_sesion, al_disparar=lambda *_: (operaciones.fijar("sesion_arrancar"), operaciones.aplicar()),
                       descripcion="Un Plasma anidado con su propio HOME, para ver el tema sin tocar tu sesión")
    acciones.registrar("herr.respaldos", "&Respaldos y volver atrás…", "edit-undo", None, "Herramientas", al_disparar=pedir("respaldos"),
                       descripcion="Cada respaldo del instalador con su UNDO.sh: verlo, elegirlo y volver atrás tras confirmar")
    acciones.registrar("herr.sesion", "La &sesión de prueba…", "window-new", None, "Herramientas", al_disparar=pedir("sesion"),
                       descripcion="Estado, arrancar (tras confirmar), recargar, capturar, cerrar; las sesiones que quedaron en la caché")
    acciones.registrar("herr.sitio", "Abrir el &sitio de Lliphi", "internet-web-browser", None, "Herramientas", al_disparar=lambda *_: espacio.abrirEnlace(proyecto.marca().get("sitio_tema", "")))
    acciones.registrar("herr.lanzador", "Instalar el acceso &directo", "application-x-executable", None, "Herramientas", al_disparar=lambda *_: instalar_lanzador())
    acciones.registrar("herr.venv", "El &entorno de las órdenes…", "python", None, "Herramientas", al_disparar=pedir("venv"),
                       descripcion="Con qué intérprete corren generar.py, instalar.py y paleta.py, y cómo crear el .venv (coloraide)")
    # --- Ayuda
    acciones.registrar("ayuda.manual", "&Manual de Lliphi Studio", "help-contents", StandardKey.HelpContents, "Ayuda",
                       al_disparar=lambda *_: espacio.abrir(str(APP_DIR.parent / "README.md")))
    acciones.registrar("ayuda.arquitectura", "&Arquitectura de Lliphi", "help-hint", None, "Ayuda",
                       al_disparar=lambda *_: espacio.abrir(str(proyecto.raiz() / "docs" / "arquitectura.md")))

    acciones.definir_menus([
        ("&Archivo", ["archivo.ajustes", "archivo.generado", "archivo.terminal", "|", "archivo.tokens", "archivo.esquema", "|", "app.salir"]),
        ("&Ver", [f"ver.area.{a['id']}" for a in svc_areas.areas()] + ["|", "ver.releer", "ver.salida", "ventana.pantalla_completa"]),
        ("&Destino", ["escr.generar", "escr.instalar", "|", "escr.generar_todo", "escr.instalar_todo", "escr.desinstalar", "|", "escr.ejecutar", "escr.cancelar"]),
        ("&Proyecto", ["proyecto.verificar", "proyecto.comprobar", "|"] + [f"op.{o.id}" for o in ops.de_grupo("proyecto") if acciones.existe(f"op.{o.id}")] + ["|", "op.aplicar"]),
        ("&Herramientas", ["sesion.arrancar", "herr.sesion", "herr.respaldos", "|"] + [f"op.{o.id}" for o in ops.de_grupo("herramientas") if acciones.existe(f"op.{o.id}")]
         + ["|", "herr.sitio", "herr.lanzador", "herr.venv", "|", "ventana.paleta"]),
        ("A&justes", ["app.ajustes"]),
        ("Ay&uda", ["ayuda.manual", "ayuda.arquitectura", "app.acerca"]),
    ])
    acciones.definir_barra(["ver.releer", "proyecto.verificar", "|", "escr.generar", "escr.instalar", "|", "escr.ejecutar"])
    acciones.anadir_fuente(espacio.entradas_paleta)
    acciones.anadir_fuente(lambda _t: [{"nombre": f"destino.{m.id}", "texto": f"Destino: {m.nombre}", "grupo": "Destinos", "icono": "preferences-desktop-theme-global",
                                        "ejecutar": lambda i=m.id: centro.irADestino(i)} for m in destinos._modulos.values()])

    def instalar_lanzador() -> None:
        if not tareas.activa:
            tareas.proceso("Instalando el acceso directo", ["/usr/bin/python3", str(APP_DIR.parent / "main.py"), "--instalar-lanzador"],
                           cwd=str(proyecto.raiz()), operacion="instalacion")

    def disponibilidad():
        activa = tareas.activa
        m = destinos._modulos.get(centro.destino)
        acciones.habilitar("archivo.ajustes", bool(centro.archivoAjustes()))
        acciones.habilitar("archivo.generado", m is not None)
        acciones.habilitar("escr.generar", m is not None and not activa)
        acciones.habilitar("escr.instalar", m is not None and m.clase == "paquete" and bool(m.datos.get("instalacion")) and m.id not in ("sddm", "gtk") and not activa)
        for n in ("escr.generar_todo", "escr.instalar_todo", "escr.desinstalar", "proyecto.verificar", "proyecto.comprobar", "ver.releer", "herr.lanzador", "sesion.arrancar"):
            acciones.habilitar(n, not activa)
        acciones.habilitar("escr.ejecutar", escritura.puedeEjecutar)
        for tipo in ("generar", "instalar", "desinstalar"):
            acciones.habilitar(f"escr.ejecutar.{tipo}", escritura.puedeEjecutar)
        acciones.habilitar("escr.cancelar", activa)
        acciones.habilitar("op.aplicar", operaciones.puedeAplicar and operaciones.actual not in ("generar", "instalar", "instalar_todo", "desinstalar", "generar_todo"))
        for a in svc_areas.areas():
            acciones.marcar(f"ver.area.{a['id']}", a["id"] == centro.area)

    def barra_estado():
        espacio.fijarResumen(destinos.resumen)
        a = svc_areas.area(centro.area)
        partes = [a["titulo"]]
        m = destinos._modulos.get(centro.destino)
        if m is not None:
            f = destinos._filas.get(m.id, {})
            partes.append(f"{m.nombre} · {f.get('generado', '').lower()} · {f.get('instalacion', '').lower()}")
        espacio.fijarContexto(" · ".join(partes))

    centro.areaCambiada.connect(lambda: (disponibilidad(), barra_estado()))
    centro.destinoCambiado.connect(lambda: (disponibilidad(), barra_estado()))
    destinos.cambiado.connect(lambda: (disponibilidad(), barra_estado()))
    operaciones.cambiado.connect(disponibilidad)
    escritura.cambiado.connect(disponibilidad)
    tareas.cambiada.connect(disponibilidad)
    disponibilidad()
    barra_estado()

    piezas = dict(consola=consola, tareas=tareas, interfaz=interfaz, ajustes=ajustes, espacio=espacio, destinos=destinos, operaciones=operaciones,
                  centro=centro, escritura=escritura, acciones=acciones)
    for nombre, objeto in piezas.items():
        app.exponer(nombre, objeto)
        if nombre in ("acciones", "tareas", "consola"):        # los diálogos heredados los nombran así
            app.exponer(nombre + "Studio", objeto)
    app.exponer("descripcionStudio", DESCRIPCION)
    app._piezas = piezas
    if leer_instalacion:
        destinos.leer_instalacion()
    return piezas


def main(argv: list[str]) -> int:
    if faltan():
        print(f"{NOMBRE} necesita {', '.join(faltan())}. Instálalo con:\n  {INSTALAR}", file=sys.stderr)
        return 3
    if not proyecto.hay_venv():
        print(f"{NOMBRE}: sin el .venv del proyecto, paleta.py (coloraide) no corre; lo demás sí. Créalo con:\n  {proyecto.orden_crear_venv()}", file=sys.stderr)
    from gui_comun import lanzador
    atendido = lanzador.desde_main(argv, **datos_lanzador())
    if atendido is not None:
        return atendido
    app = Aplicacion(APP_ID, NOMBRE, version=APP_VERSION, organizacion=ORG_NAME, nombre_ajustes=APP_NAME)
    piezas = construir(app)
    if "--destino" in argv:
        piezas["centro"].irADestino(argv[argv.index("--destino") + 1])
    elif "--area" in argv:
        piezas["centro"].fijarArea(argv[argv.index("--area") + 1])
    return app.ejecutar(QML_DIR / "Main.qml", humo="--smoke" in argv)
