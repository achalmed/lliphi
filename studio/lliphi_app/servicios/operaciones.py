"""studio/lliphi_app/servicios/operaciones.py — el catálogo de operaciones de Lliphi Studio (sin Qt): lo que F5 lee o
simula y lo que Ctrl+Intro escribe o instala tras confirmar. Cada operación existe una sola vez aquí; `aplicacion.py` la
registra como acción y `controladores/operaciones.py` la corre con `gui_comun.tareas.proceso` (la orden de Lliphi con el
Python del `.venv`). Las que escriben llevan `toca` (lo que la confirmación dice) y las que instalan recuerdan el
respaldo con su `UNDO.sh` (`docs/rediseno.md` S4)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lliphi_app.servicios import proyecto

GRUPOS = (("destino", "Destino"), ("proyecto", "Proyecto"), ("herramientas", "Herramientas"))


@dataclass
class Contexto:
    raiz: Path
    id: str = ""                          # el destino actual
    variante: str = "oscuro"
    respaldo: str = ""                    # la carpeta del respaldo elegido (volver atrás)


@dataclass
class Orden:
    argv: list
    cwd: Path

    def texto(self) -> str:
        partes = []
        for a in self.argv:
            a = str(a)
            if a == proyecto.python():
                partes.append("python")
            elif a.startswith(str(self.cwd)):
                partes.append(Path(a).relative_to(self.cwd).as_posix())
            else:
                partes.append(a)
        return " ".join(partes)


@dataclass
class Operacion:
    id: str
    titulo: str
    descripcion: str
    grupo: str
    simular: object = None                # f(ctx) -> Orden (F5)
    aplicar: object = None                # f(ctx) -> Orden (Ctrl+Intro)
    plan: object = None                   # f(ctx) -> str: lo que la ventana calcula sin correr nada (F5 sin orden)
    escribe: bool = False
    toca: str = "solo lee"
    sobre_destino: bool = False
    instala: bool = False                 # deja respaldo y UNDO.sh
    larga: bool = False
    icono: str = "system-run"
    verbo_simular: str = ""

    @property
    def verbo(self) -> str:
        if self.verbo_simular:
            return self.verbo_simular
        return "Simular" if self.escribe else "Ejecutar"


def _orden(herramienta: str, *args: str) -> Orden:
    return Orden(proyecto.orden(herramienta, *args), proyecto.raiz())


def _quarto(c: Contexto) -> Orden:
    return Orden(["quarto", "render", "sitio"], c.raiz)


def _plan_empaquetar(c: Contexto) -> str:
    modulos = [m for m in proyecto.modulos() if m.clase == "paquete"]
    v = proyecto.version()
    return ("Escribiría en dist/ (regenerable, fuera de git):\n" + "\n".join(f"  lliphi-{m.id}-{v}.tar.gz" for m in modulos)
            + "\n  SHA256SUMS · NOTAS-" + v + ".md · FICHA-KDE-STORE.md\n\nCtrl+Intro corre generar.py empaquetar.")


def _plan_sitio(c: Contexto) -> str:
    qmd = sorted(p.name for p in (c.raiz / "sitio").glob("*.qmd"))
    return ("quarto render sitio escribiría sitio/_site/ (regenerable, fuera de git) con " + f"{len(qmd)} páginas:\n  " + "\n  ".join(qmd)
            + "\n\nsitio/generado/ lo escribe antes generar.py --aplicar. Ctrl+Intro renderiza.")


OPERACIONES: tuple[Operacion, ...] = (
    # --- el destino actual
    Operacion("generar", "Generar el destino", "generar.py --modulos <destino>: F5 dice qué escribiría en generado/ (y qué cambiaría); Ctrl+Intro lo escribe (--aplicar)",
              "destino", simular=lambda c: _orden("generar", "--modulos", c.id), aplicar=lambda c: _orden("generar", "--modulos", c.id, "--aplicar"), escribe=True,
              toca="reescribe generado/<destino>/ y sitio/generado/ desde los tokens (reversible con git)", sobre_destino=True, icono="run-build"),
    Operacion("instalar", "Instalar el destino", "instalar.py --modulos <destino>: F5 dice qué respaldaría y copiaría a tu escritorio; Ctrl+Intro lo instala con respaldo y UNDO.sh",
              "destino", simular=lambda c: _orden("instalar", "--modulos", c.id), aplicar=lambda c: _orden("instalar", "--modulos", c.id, "--aplicar"), escribe=True, instala=True,
              toca="copia lo generado a ~/.local/share y ~/.config de tu sesión real, tras respaldar lo que cambia con su suma y dejar UNDO.sh", sobre_destino=True, icono="install"),
    # --- el proyecto
    Operacion("verificar", "Verificar lo generado", "generar.py verificar: construye todo en un temporal y compara con generado/; actualiza «Al día» de cada destino (tarda unos segundos)",
              "proyecto", simular=lambda c: _orden("generar", "verificar", "--json"), larga=True, icono="view-refresh", verbo_simular="Verificar"),
    Operacion("validar", "Validar los módulos", "generar.py validar: manifiestos, dependencias, estructura KDE e integración en el tema global",
              "proyecto", simular=lambda c: _orden("generar", "validar"), icono="checkmark", verbo_simular="Validar"),
    Operacion("generar_todo", "Generar todo", "generar.py: F5 dice qué escribiría de todos los destinos; Ctrl+Intro escribe generado/ y sitio/generado/",
              "proyecto", simular=lambda c: _orden("generar"), aplicar=lambda c: _orden("generar", "--aplicar"), escribe=True,
              toca="reescribe generado/ entero y sitio/generado/ (reversible con git)", icono="run-build"),
    Operacion("paleta", "Paleta: los tokens desde los ajustes", "paleta.py: F5 dice qué cambiaría en tokens/tokens.json desde modulos/esquema/ajustes.json y el contraste; Ctrl+Intro lo escribe",
              "proyecto", simular=lambda c: _orden("paleta"), aplicar=lambda c: _orden("paleta", "--aplicar"), escribe=True,
              toca="reescribe tokens/tokens.json (la fuente de verdad del color; reversible con git); después hay que generar", icono="color-management"),
    Operacion("estado", "Estado de la instalación", "instalar.py estado: qué hay instalado en tu sesión, de qué versión, y si cada ruta sigue como se instaló",
              "proyecto", simular=lambda c: _orden("instalar", "estado"), icono="dialog-information"),
    Operacion("comprobar", "Comprobar la instalación", "instalar.py comprobar: todo instalado, de esta versión y reconocido por KDE",
              "proyecto", simular=lambda c: _orden("instalar", "comprobar"), icono="checkmark", verbo_simular="Comprobar"),
    Operacion("instalar_todo", "Instalar todo", "instalar.py: F5 simula la instalación de todos los destinos; Ctrl+Intro instala con respaldo y UNDO.sh",
              "proyecto", simular=lambda c: _orden("instalar"), aplicar=lambda c: _orden("instalar", "--aplicar"), escribe=True, instala=True,
              toca="copia todo lo generado a tu sesión real, tras respaldar lo que cambia con su suma y dejar UNDO.sh", icono="install"),
    Operacion("desinstalar", "Desinstalar", "instalar.py desinstalar: F5 dice qué retiraría; Ctrl+Intro retira lo instalado (el respaldo del instalador queda)",
              "proyecto", simular=lambda c: _orden("instalar", "desinstalar"), aplicar=lambda c: _orden("instalar", "desinstalar", "--aplicar"), escribe=True, instala=True,
              toca="retira de tu sesión lo que instaló Lliphi; el UNDO.sh del último respaldo devuelve lo de antes", icono="edit-delete"),
    Operacion("dependencias", "Dependencias de terceros", "instalar.py dependencias: F5 dice qué bajaría (Papirus, cursores WhiteSur, JetBrains Mono Nerd Font); Ctrl+Intro las instala en tu usuario, sin root",
              "proyecto", simular=lambda c: _orden("instalar", "dependencias"), aplicar=lambda c: _orden("instalar", "dependencias", "--aplicar"), escribe=True, larga=True,
              toca="descarga e instala temas de terceros en ~/.local/share (iconos, cursores, tipografías)", icono="download"),
    Operacion("pruebas", "Pruebas del proyecto", "pytest sobre pruebas/: tokens, contraste, deriva, estructura, instalación reversible en un HOME temporal (tarda)",
              "proyecto", simular=lambda c: Orden([proyecto.python(), "-m", "pytest", "-q", "pruebas"], c.raiz), larga=True, icono="checkmark", verbo_simular="Correr"),
    Operacion("licencias", "Licencias (REUSE)", "reuse lint: cada archivo con su licencia declarada",
              "proyecto", simular=lambda c: Orden([proyecto.python(), "-m", "reuse", "lint"], c.raiz), icono="license", verbo_simular="Comprobar"),
    Operacion("empaquetar", "Empaquetar", "generar.py empaquetar: F5 dice qué tarballs escribiría en dist/; Ctrl+Intro los escribe con SHA256SUMS, notas y la ficha de la tienda",
              "proyecto", plan=_plan_empaquetar, aplicar=lambda c: _orden("generar", "empaquetar"), escribe=True, toca="escribe dist/ (regenerable, fuera de git)", icono="package"),
    Operacion("sitio", "Sitio (Quarto)", "quarto render sitio: F5 dice qué páginas renderizaría; Ctrl+Intro renderiza sitio/_site",
              "proyecto", plan=_plan_sitio, aplicar=_quarto, escribe=True, larga=True, toca="escribe sitio/_site/ (regenerable, fuera de git); publicar es un push", icono="internet-web-browser"),
    # --- herramientas
    Operacion("sesion_estado", "Sesión de prueba: estado", "sesion.py estado: si hay una sesión anidada activa, su variante, su HOME y el LockedHint de la sesión real",
              "herramientas", simular=lambda c: _orden("sesion", "estado"), icono="system-run"),
    Operacion("sesion_arrancar", "Sesión de prueba: arrancar", "sesion.py arrancar: F5 dice qué haría; Ctrl+Intro arranca un Plasma anidado con su propio HOME en la caché (consume RAM y disco)",
              "herramientas", simular=lambda c: _orden("sesion", "arrancar", "--variante", c.variante), aplicar=lambda c: _orden("sesion", "arrancar", "--variante", c.variante, "--aplicar"),
              escribe=True, larga=True, toca="arranca kwin_wayland y plasmashell anidados y deja una casa nueva en $XDG_CACHE_HOME/lliphi/sesiones/ (cientos de MB; sesion.py cerrar la termina, la carpeta queda)",
              icono="window-new"),
    Operacion("sesion_recargar", "Sesión de prueba: recargar", "sesion.py recargar: reinstala y vuelve a aplicar el tema dentro de la sesión anidada",
              "herramientas", aplicar=lambda c: _orden("sesion", "recargar"), escribe=True, toca="instala dentro de la sesión de prueba (no en tu sesión real)", icono="view-refresh"),
    Operacion("sesion_capturar", "Sesión de prueba: capturar", "sesion.py capturar: una captura PNG de la sesión anidada",
              "herramientas", simular=lambda c: _orden("sesion", "capturar"), icono="camera-photo", verbo_simular="Capturar"),
    Operacion("sesion_cerrar", "Sesión de prueba: cerrar", "sesion.py cerrar: termina los procesos de la sesión anidada (solo los de su HOME) y comprueba el LockedHint",
              "herramientas", aplicar=lambda c: _orden("sesion", "cerrar"), escribe=True, toca="cierra la sesión de prueba; nada de tu sesión real", icono="window-close"),
    Operacion("revertir", "Volver atrás con un respaldo", "bash UNDO.sh del respaldo elegido: F5 enseña el guion; Ctrl+Intro lo corre y deja tu sesión como antes de esa instalación",
              "herramientas", plan=lambda c: (Path(c.respaldo) / "UNDO.sh").read_text(encoding="utf-8") if c.respaldo and (Path(c.respaldo) / "UNDO.sh").is_file() else "Elige un respaldo (Herramientas › Respaldos y volver atrás…).",
              aplicar=lambda c: Orden(["bash", str(Path(c.respaldo) / "UNDO.sh")], c.raiz), escribe=True, instala=True,
              toca="restaura byte a byte lo respaldado y desinstala lo que esa instalación puso", icono="edit-undo"),
)


def operacion(id_: str) -> Operacion | None:
    return next((o for o in OPERACIONES if o.id == id_), None)


def de_grupo(grupo: str) -> list[Operacion]:
    return [o for o in OPERACIONES if o.grupo == grupo]
