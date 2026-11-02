"""studio/lliphi_app/aplicacion.py — arma Lliphi Studio: la aplicación (gui_comun.nucleo), los controladores, el registro
de acciones (menú, barra, menú contextual, paleta, atajos) y carga `qml/Main.qml`.

Toda operación existe una sola vez, aquí, en `Acciones`. Las operaciones del catálogo son acciones `op.<id>` que
eligen la operación actual; correrla es siempre F5 (la orden de Lliphi en simulación o de solo lectura, o el plan de la
ventana) o Ctrl+Intro (Aplicar, tras confirmar en QML con la orden exacta, lo que toca y el respaldo con su UNDO.sh).
Lo que necesita un diálogo lo pide a QML por `Interfaz.pedir`. Python no construye interfaz; la ventana no escribe en
el proyecto ni en el escritorio por su cuenta: toda escritura es una orden de Lliphi.
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
from lliphi_app.controladores.destinos import Destinos  # noqa: E402
from lliphi_app.controladores.espacio import ESTADOS, Espacio  # noqa: E402
from lliphi_app.controladores.operaciones import Operaciones  # noqa: E402
from lliphi_app.servicios import operaciones as ops  # noqa: E402
from lliphi_app.servicios import proyecto  # noqa: E402

APP_DIR = Path(__file__).resolve().parent
QML_DIR = APP_DIR / "qml"
RECURSOS_DIR = APP_DIR / "recursos"
APP_ID = "lliphi-studio"
NOMBRE = APP_NAME
DESCRIPCION = ("El tema Lliphi en una ventana de trabajo: cada destino (el tema global, los módulos y los complementos) con lo que entrega, si lo "
               "generado está al día con los tokens y si está instalado en tu sesión y sigue intacto; la paleta de los tokens como datos; las "
               "diferencias de una verificación y el registro de cada orden. F5 simula o lee (generar, verificar, validar, instalar en simulación, "
               "comprobar) y Ctrl+Intro escribe o instala tras confirmar, siempre con el respaldo y su UNDO.sh a la vista. Las órdenes son las de "
               "Lliphi (generar.py, instalar.py, paleta.py, sesion.py); la ventana no reemplaza ninguna.")
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
    espacio = Espacio(consola, ajustes)
    destinos = Destinos(espacio, consola, tareas, cache=cache)
    operaciones = Operaciones(espacio, destinos, ajustes, consola, tareas, cache=cache)
    acciones = Acciones()
    acciones.estandar(NOMBRE)
    pedir = lambda que, **datos: (lambda *_: interfaz.pedir.emit(que, datos))

    # --- Archivo
    acciones.registrar("archivo.ajustes", "Abrir los &ajustes del destino", "document-edit", None, "Archivo", habilitada=False,
                       al_disparar=lambda *_: espacio.abrir(destinos.archivoAjustes), descripcion="Su ajustes.json con el editor del sistema (los módulos que lo tienen); después, Generar")
    acciones.registrar("archivo.manifiesto", "Abrir su &modulo.json", "application-json", None, "Archivo", habilitada=False, al_disparar=lambda *_: espacio.abrir(destinos.archivoManifiesto))
    acciones.registrar("archivo.generado", "Abrir lo &generado en Dolphin", "system-file-manager", "Ctrl+Shift+O", "Archivo", habilitada=False,
                       al_disparar=lambda *_: espacio.abrirDolphin(destinos.carpetaGenerado), descripcion="generado/<destino>/ en Dolphin")
    acciones.registrar("archivo.terminal", "Abrir &terminal en el proyecto", "utilities-terminal", "Shift+F4", "Archivo", al_disparar=lambda *_: espacio.abrirTerminal(str(proyecto.raiz())))
    acciones.registrar("archivo.copiar", "Copiar el &id del destino", "edit-copy", "Ctrl+Shift+C", "Archivo", habilitada=False, al_disparar=lambda *_: espacio.copiar(destinos.id))
    acciones.registrar("archivo.tokens", "Abrir &tokens.json", "color-management", None, "Archivo", al_disparar=lambda *_: espacio.abrir(str(proyecto.raiz() / "tokens" / "tokens.json")),
                       descripcion="La fuente de verdad del color (GENERADO por paleta.py; se edita modulos/esquema/ajustes.json)")
    # --- Editar
    acciones.registrar("editar.filtrar", "&Filtrar", "edit-find", StandardKey.Find, "Editar", al_disparar=pedir("filtrar"))
    acciones.registrar("editar.todo", "Seleccionar &todo", "edit-select-all", StandardKey.SelectAll, "Editar", al_disparar=pedir("seleccionar_todo"))
    # --- Ver
    acciones.registrar("ver.rol", "&Todos los destinos", "view-list-tree", "Ctrl+0", "Ver › Destinos", marcable=True, al_disparar=lambda *_: (espacio.fijarEstado(""), espacio.fijarRol("")))
    for i, (r, t) in enumerate((("global", "&Tema global"), ("modulo", "&Módulos"), ("complemento", "&Complementos")), start=1):
        acciones.registrar(f"ver.rol.{r}", f"{t}", "", f"Ctrl+{i}", "Ver › Destinos", marcable=True, al_disparar=lambda *_, n=r: (espacio.fijarEstado(""), espacio.fijarRol(n)))
    acciones.registrar("ver.estado", "Todos los &estados", "", None, "Ver › Estado", marcable=True, al_disparar=lambda *_: espacio.fijarEstado(""))
    for e, t in ESTADOS:
        acciones.registrar(f"ver.estado.{e}", t, "", None, "Ver › Estado", marcable=True, al_disparar=lambda *_, n=e: espacio.fijarEstado(n))
    acciones.registrar("ver.releer", "&Releer el proyecto", "view-refresh", "F6", "Ver", al_disparar=lambda *_: (destinos.recargar(), destinos.leer_instalacion()),
                       descripcion="Vuelve a leer los manifiestos, lo generado, la verificación guardada y la instalación")
    # --- Destino · Proyecto · Herramientas: elegir cada operación
    for o in ops.OPERACIONES:
        acciones.registrar(f"op.{o.id}", o.titulo, o.icono, None, dict(ops.GRUPOS)[o.grupo], al_disparar=lambda *_, i=o.id: operaciones.fijar(i), descripcion=o.descripcion)
    acciones.registrar("op.simular", "&Simular", "system-run", StandardKey.Refresh, "Destino", al_disparar=operaciones.simular,
                       descripcion="Corre la operación elegida en simulación o de solo lectura (o muestra su plan); la salida queda en el panel inferior")
    acciones.registrar("op.aplicar", "&Aplicar…", "dialog-ok-apply", "Ctrl+Return", "Destino", habilitada=False, al_disparar=pedir("aplicar"),
                       descripcion="Muestra la orden exacta, lo que toca y el respaldo; si confirmas, escribe o instala de verdad")
    acciones.registrar("op.cancelar", "&Cancelar la orden", "process-stop", None, "Destino", habilitada=False, al_disparar=operaciones.cancelar)
    acciones.registrar("proyecto.verificar", "&Verificar lo generado ahora", "view-refresh", "Ctrl+T", "Proyecto",
                       al_disparar=lambda *_: (operaciones.fijar("verificar"), operaciones.simular()), descripcion="Elige «Verificar lo generado» y la corre: actualiza «Al día» de cada destino")
    acciones.registrar("proyecto.comprobar", "&Comprobar la instalación ahora", "checkmark", "Ctrl+Shift+T", "Proyecto",
                       al_disparar=lambda *_: (operaciones.fijar("comprobar"), operaciones.simular()), descripcion="Elige «Comprobar la instalación» y la corre")
    for i, (nombre, texto) in enumerate((("resumen", "Ver el &resumen"), ("paleta", "Ver la &paleta"), ("diferencias", "Ver las &diferencias"), ("registro", "Ver el re&gistro"))):
        acciones.registrar(f"destino.{nombre}", texto, "", None, "Destino", al_disparar=pedir("pestana", indice=i))
    # --- Herramientas
    acciones.registrar("herr.respaldos", "&Respaldos y volver atrás…", "edit-undo", None, "Herramientas", al_disparar=pedir("respaldos"),
                       descripcion="Cada respaldo del instalador con su UNDO.sh: verlo, elegirlo y volver atrás tras confirmar")
    acciones.registrar("herr.sesion", "&Sesión de prueba…", "window-new", None, "Herramientas", al_disparar=pedir("sesion"),
                       descripcion="El Plasma anidado: estado, arrancar (tras confirmar), recargar, capturar, cerrar; las sesiones que quedaron en la caché")
    acciones.registrar("herr.sitio", "Abrir el &sitio de Lliphi", "internet-web-browser", None, "Herramientas", al_disparar=lambda *_: espacio.abrirEnlace(proyecto.marca().get("sitio_tema", "")))
    acciones.registrar("herr.lanzador", "Instalar el acceso &directo", "application-x-executable", None, "Herramientas", al_disparar=lambda *_: instalar_lanzador())
    acciones.registrar("herr.venv", "El &entorno de las órdenes…", "python", None, "Herramientas", al_disparar=pedir("venv"),
                       descripcion="Con qué intérprete corren generar.py, instalar.py y paleta.py, y cómo crear el .venv (coloraide)")
    # --- Ayuda
    acciones.registrar("ayuda.manual", "&Manual de Lliphi Studio", "help-contents", StandardKey.HelpContents, "Ayuda",
                       al_disparar=lambda *_: subprocess.Popen(["xdg-open", str(APP_DIR.parent / "README.md")]))
    acciones.registrar("ayuda.arquitectura", "&Arquitectura de Lliphi", "help-hint", None, "Ayuda",
                       al_disparar=lambda *_: subprocess.Popen(["xdg-open", str(proyecto.raiz() / "docs" / "arquitectura.md")]))
    acciones.registrar("ayuda.destino", "README del &destino", "help-about", None, "Ayuda", habilitada=False,
                       al_disparar=lambda *_: espacio.abrir(str(Path(destinos.carpeta) / "README.md")))

    acciones.definir_menus([
        ("&Archivo", ["archivo.ajustes", "archivo.manifiesto", "archivo.generado", "archivo.terminal", "archivo.copiar", "|", "archivo.tokens", "|", "app.salir"]),
        ("&Editar", ["editar.filtrar", "editar.todo"]),
        ("&Ver", ["ventana.navegacion", "ventana.detalles", "ventana.inferior", "|", ("&Destinos", ["ver.rol", "ver.rol.global", "ver.rol.modulo", "ver.rol.complemento"]),
                  ("&Estado", ["ver.estado"] + [f"ver.estado.{e}" for e, _t in ESTADOS]), "|", "ver.releer", "|", "ventana.pantalla_completa"]),
        ("&Destino", ["op.simular", "op.aplicar", "op.cancelar", "|"] + [f"op.{o.id}" for o in ops.de_grupo("destino")] + ["|", "destino.resumen", "destino.paleta", "destino.diferencias", "destino.registro"]),
        ("&Proyecto", ["proyecto.verificar", "proyecto.comprobar", "|"] + [f"op.{o.id}" for o in ops.de_grupo("proyecto")]),
        ("&Herramientas", ["herr.respaldos", "herr.sesion", "|"] + [f"op.{o.id}" for o in ops.de_grupo("herramientas")] + ["|", "herr.sitio", "herr.lanzador", "herr.venv", "|", "ventana.paleta"]),
        ("A&justes", ["app.ajustes"]),
        ("Ay&uda", ["ayuda.manual", "ayuda.arquitectura", "ayuda.destino", "app.acerca"]),
    ])
    acciones.definir_barra(["op.simular", "op.aplicar", "|", "proyecto.verificar", "proyecto.comprobar"])
    acciones.anadir_fuente(espacio.entradas_paleta)
    acciones.anadir_fuente(operaciones.entradas_paleta)
    acciones.anadir_fuente(destinos.entradas_paleta)

    def instalar_lanzador() -> None:
        if not tareas.activa:
            tareas.proceso("Instalando el acceso directo", ["/usr/bin/python3", str(APP_DIR.parent / "main.py"), "--instalar-lanzador"], cwd=str(proyecto.raiz()))

    def filtro_cambiado():
        acciones.marcar("ver.rol", espacio.rol == "")
        for r in ("global", "modulo", "complemento"):
            acciones.marcar(f"ver.rol.{r}", espacio.rol == r)
        acciones.marcar("ver.estado", espacio.estado == "")
        for e, _t in ESTADOS:
            acciones.marcar(f"ver.estado.{e}", espacio.estado == e)
        disponibilidad()

    def disponibilidad():
        activa = tareas.activa
        hay = destinos.hayActual
        acciones.habilitar("archivo.ajustes", hay and bool(destinos.archivoAjustes))
        for nombre in ("archivo.manifiesto", "archivo.generado", "archivo.copiar", "ayuda.destino"):
            acciones.habilitar(nombre, hay)
        a = acciones.accion("op.simular")
        a.texto = f"&{operaciones.verbo}"
        acciones.habilitar("op.simular", operaciones.puedeSimular)
        b = acciones.accion("op.aplicar")
        b.visible = operaciones.escribe
        acciones.habilitar("op.aplicar", operaciones.puedeAplicar)
        acciones.habilitar("op.cancelar", operaciones.enCurso)
        acciones.habilitar("proyecto.verificar", not activa)
        acciones.habilitar("proyecto.comprobar", not activa)
        acciones.habilitar("ver.releer", not activa)
        acciones.habilitar("herr.lanzador", not activa)

    def barra_estado():
        espacio.fijarResumen(destinos.resumen)
        partes = []
        if destinos.hayActual:
            partes.append(f"{destinos.nombre} · {destinos.textoGenerado.lower()} · {destinos.textoEstadoInstalacion.lower()}")
        if operaciones.titulo:
            partes.append(operaciones.titulo)
        espacio.fijarContexto(" · ".join(partes))

    espacio.filtroCambiado.connect(filtro_cambiado)
    destinos.cambiado.connect(lambda: (disponibilidad(), barra_estado()))
    destinos.actualCambiado.connect(lambda: (disponibilidad(), barra_estado()))
    operaciones.cambiado.connect(lambda: (disponibilidad(), barra_estado()))
    tareas.cambiada.connect(disponibilidad)
    filtro_cambiado()
    barra_estado()

    piezas = dict(consola=consola, tareas=tareas, interfaz=interfaz, ajustes=ajustes, espacio=espacio, destinos=destinos, operaciones=operaciones, acciones=acciones)
    for nombre, objeto in piezas.items():        # acciones, tareas y consola son propiedades de VentanaStudio: en QML van con sufijo
        app.exponer(nombre + "Studio" if nombre in ("acciones", "tareas", "consola") else nombre, objeto)
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
        piezas["destinos"].irA(argv[argv.index("--destino") + 1])
    return app.ejecutar(QML_DIR / "Main.qml", humo="--smoke" in argv)
