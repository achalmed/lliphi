#!/usr/bin/env python3
"""Sesión de prueba: un Plasma anidado, con su propio HOME, donde instalar y aplicar Lliphi sin tocar el escritorio real.

Es la receta de `docs/validacion.md` §8–§9 hecha orden: `kwin_wayland` anidado (en una ventana o, con `--virtual`, sin
mostrarse) bajo `dbus-run-session` con un entorno limpio (`env -i`), `HOME` y `XDG_*` en
`$XDG_CACHE_HOME/lliphi/sesiones/<fecha>/casa`, `XDG_RUNTIME_DIR` corto (`$XDG_RUNTIME_DIR/lliphi-<n>`: el socket de
Wayland no admite rutas de más de 108 bytes), `startkderc` con `systemdBoot=false` (nada arranca en el systemd de
usuario de la sesión real), bloqueo e inactividad desactivados antes de arrancar (§8.3: una sesión de prueba bloqueada
pone `LockedHint=yes` en la real) y los temas de iconos, cursores y tipografías del usuario enlazados (solo lectura).

Toda orden que corre dentro toma el entorno completo del `plasmashell` de prueba y **se niega** si su `HOME` no es el
de la sesión; `cerrar` termina por PID solo los procesos cuyo `HOME` (leído de `/proc/<pid>/environ`) es el de prueba
y compara el `LockedHint` de la sesión real antes y después.

Uso:  python3 herramientas/sesion.py arrancar [--variante oscuro|claro] [--disposicion] [--virtual] [--ancho 1600 --alto 900]
                                                [--escritorios N] [--aplicar]
      python3 herramientas/sesion.py estado [--json]
      python3 herramientas/sesion.py recargar [--modulos esquema,estilo] [--disposicion]   # reinstala y vuelve a aplicar
      python3 herramientas/sesion.py ejecutar -- <orden> [args…]                          # dentro, sin esperar
      python3 herramientas/sesion.py guion <archivo.js>                                   # scripting de Plasma dentro
      python3 herramientas/sesion.py capturar [--salida <png>]
      python3 herramientas/sesion.py cerrar
Sin `--aplicar`, `arrancar` solo dice qué haría (simula). Solo biblioteca estándar. Sale 0 bien, 1 error de uso,
2 falta una herramienta, 3 no hay sesión de prueba (o la orden se negó), 4 la sesión no llegó a arrancar.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = json.loads((RAIZ / "tokens" / "marca.json").read_text(encoding="utf-8"))
ID = MARCA["id"]
HOME = Path.home()
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or HOME / ".cache") / ID / "sesiones"
STATE = Path(os.environ.get("XDG_STATE_HOME") or HOME / ".local" / "state") / ID
ESTADO = STATE / "sesion-prueba.json"
DATA_REAL = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local" / "share")
RUNTIME_REAL = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}")
# solo el PATH del sistema: el Qt de otra distribución (p. ej. Anaconda) no debe mezclarse con el de Plasma
PATH = "/usr/local/bin:/usr/bin:/bin"
HERRAMIENTAS = ("dbus-run-session", "kwin_wayland", "startplasma-wayland", "kwriteconfig6")

# configuración que se escribe en el HOME de prueba antes de arrancar: (archivo, grupos, clave, valor)
CONFIG_PREVIA = [
    ("startkderc", ["General"], "systemdBoot", "false"),
    ("kscreenlockerrc", ["Daemon"], "Autolock", "false"),
    ("kscreenlockerrc", ["Daemon"], "LockOnResume", "false"),
    ("powerdevilrc", ["AC", "Display"], "TurnOffDisplayWhenIdle", "false"),
    ("powerdevilrc", ["AC", "Display"], "DimDisplayWhenIdle", "false"),
    ("powerdevilrc", ["AC", "SuspendAndShutdown"], "AutoSuspendAction", "0"),
    ("ksmserverrc", ["General"], "loginMode", "emptySession"),
    ("plasma-welcomerc", ["General"], "LastSeenVersion", "99.0.0"),
]


# ------------------------------------------------------------------ estado y entorno

def leer_estado() -> dict | None:
    return json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else None


def entorno_de(pid: int) -> dict[str, str]:
    try:
        crudo = Path(f"/proc/{pid}/environ").read_bytes()
    except OSError:
        return {}
    return dict(x.split("=", 1) for x in crudo.decode(errors="replace").split("\0") if "=" in x)


def procesos_de(casa: Path) -> list[int]:
    """Los PID cuyo HOME es el de prueba (los únicos que `cerrar` termina)."""
    pids = []
    for d in Path("/proc").iterdir():
        if d.name.isdigit() and int(d.name) != os.getpid() and entorno_de(int(d.name)).get("HOME") == str(casa):
            pids.append(int(d.name))
    return pids


def plasmashell_de(casa: Path) -> int | None:
    for pid in procesos_de(casa):
        try:
            if Path(f"/proc/{pid}/comm").read_text().strip() == "plasmashell":
                return pid
        except OSError:
            continue
    return None


def entorno_dentro(est: dict) -> dict[str, str]:
    """El entorno del plasmashell de prueba, o error si no hay sesión o su HOME no es el de prueba (nunca el real)."""
    casa = Path(est["casa"])
    if not casa.is_relative_to(CACHE) or casa == HOME:
        raise PermissionError(f"el HOME {casa} no es de una sesión de prueba (deben vivir en {CACHE})")
    pid = plasmashell_de(casa)
    if pid is None:
        raise LookupError("la sesión de prueba no tiene plasmashell (¿terminó o aún arranca?)")
    env = entorno_de(pid)
    if env.get("HOME") != str(casa) or env.get("HOME") == str(HOME):
        raise PermissionError("el plasmashell encontrado no es el de prueba")
    return env


def entorno_inicial(casa: Path, runtime: Path, virtual: bool) -> dict[str, str]:
    """Entorno limpio para arrancar: nada del bus ni de la sesión del usuario; solo el display real si va en ventana."""
    env = {"HOME": str(casa), "USER": os.environ.get("USER", ""), "LOGNAME": os.environ.get("LOGNAME", ""),
           "PATH": PATH, "LANG": os.environ.get("LANG", "C.UTF-8"), "SHELL": "/bin/bash",
           "XDG_RUNTIME_DIR": str(runtime), "XDG_DATA_HOME": str(casa / ".local" / "share"),
           "XDG_CONFIG_HOME": str(casa / ".config"), "XDG_STATE_HOME": str(casa / ".local" / "state"),
           "XDG_CACHE_HOME": str(casa / ".cache"), "XDG_SESSION_TYPE": "wayland",
           "KWIN_SCREENSHOT_NO_PERMISSION_CHECKS": "1"}   # solo en la sesión de prueba: deja capturar con spectacle
    if not virtual:   # el KWin exterior se dibuja como una ventana del escritorio real
        display = os.environ.get("WAYLAND_DISPLAY", "wayland-0")
        env["WAYLAND_DISPLAY"] = display if display.startswith("/") else str(RUNTIME_REAL / display)
    return {k: v for k, v in env.items() if v}


def runtime_libre() -> Path:
    n = 1
    while (RUNTIME_REAL / f"{ID}-{n}").exists():
        n += 1
    return RUNTIME_REAL / f"{ID}-{n}"


def preparar_casa(casa: Path, escritorios: int = 1) -> None:
    """El HOME de prueba: configuración previa (sin systemd, sin bloqueo, sin inactividad) y los temas del usuario
    enlazados (iconos, cursores, tipografías), que el tema global nombra pero Lliphi no instala."""
    for sub in (".config", ".local/share", ".local/state", ".cache"):
        (casa / sub).mkdir(parents=True, exist_ok=True)
    for archivo, grupos, clave, valor in CONFIG_PREVIA:
        escribir_ini(casa / ".config" / archivo, grupos, clave, valor)
    # los escritorios virtuales se fijan antes de arrancar: en la sesión anidada org.kde.KWin del bus es el KWin
    # exterior, así que crearlos después por DBus no llega al KWin que ve el plasmashell de prueba
    escribir_ini(casa / ".config" / "kwinrc", ["Desktops"], "Number", str(escritorios))
    escribir_ini(casa / ".config" / "kwinrc", ["Desktops"], "Rows", "1")
    for carpeta in ("icons", "fonts"):
        origen = DATA_REAL / carpeta
        if not origen.is_dir():
            continue
        (casa / ".local" / "share" / carpeta).mkdir(parents=True, exist_ok=True)
        for tema in origen.iterdir():
            destino = casa / ".local" / "share" / carpeta / tema.name
            if not destino.exists() and tema.name not in ("lliphi", "lliphi-oscuro"):
                destino.symlink_to(tema)


def escribir_ini(ruta: Path, grupos: list[str], clave: str, valor: str) -> None:
    """Escribe una clave en un archivo de configuración de KDE (grupos anidados `[A][B]`) sin kwriteconfig6."""
    cabecera = "".join(f"[{g}]" for g in grupos)
    lineas = ruta.read_text(encoding="utf-8").splitlines() if ruta.exists() else []
    if cabecera not in lineas:
        lineas += ([""] if lineas else []) + [cabecera]
    i = lineas.index(cabecera) + 1
    fin = next((j for j in range(i, len(lineas)) if lineas[j].startswith("[")), len(lineas))
    for j in range(i, fin):
        if lineas[j].split("=", 1)[0] == clave:
            lineas[j] = f"{clave}={valor}"
            break
    else:
        lineas.insert(fin if fin == len(lineas) or lineas[fin - 1] else fin - 1, f"{clave}={valor}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def locked_hint() -> str | None:
    """El LockedHint de la sesión real de logind (yes/no), si se puede leer."""
    sesion = os.environ.get("XDG_SESSION_ID")
    if not sesion or not shutil.which("loginctl"):
        return None
    r = subprocess.run(["loginctl", "show-session", sesion, "-p", "LockedHint", "--value"], capture_output=True, text=True)
    return r.stdout.strip() or None


# ------------------------------------------------------------------ órdenes

def instalar_dentro(env: dict, variante: str, modulos: str | None, disposicion: bool) -> int:
    orden = [sys.executable, str(RAIZ / "herramientas" / "instalar.py"), "--aplicar", "--aplicar-tema", variante]
    if modulos:
        orden += ["--modulos", modulos]
    r = subprocess.run(orden, cwd=RAIZ, env=env).returncode
    if r == 0 and disposicion:
        id_global = MARCA["id_global"][variante]
        r = subprocess.run(["plasma-apply-lookandfeel", "-a", id_global, "--resetLayout"], env=env).returncode
    return r


def arrancar(args: list[str]) -> int:
    variante = valor(args, "--variante", "oscuro")
    if variante not in ("claro", "oscuro"):
        print("--variante claro|oscuro"); return 1
    virtual = "--virtual" in args
    ancho, alto = int(valor(args, "--ancho", "1600")), int(valor(args, "--alto", "900"))
    escritorios = int(valor(args, "--escritorios", "1"))
    if (est := leer_estado()) and procesos_de(Path(est["casa"])):
        print(f"ya hay una sesión de prueba ({est['casa']}): sesion.py estado | cerrar"); return 1
    faltan = [h for h in HERRAMIENTAS if not shutil.which(h, path=PATH)]
    if faltan:
        print("faltan:", ", ".join(faltan)); return 2
    fecha = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    casa = CACHE / fecha / "casa"
    runtime = runtime_libre()
    orden = ["dbus-run-session", "--", "kwin_wayland", "--xwayland", "--width", str(ancho), "--height", str(alto),
             *(["--virtual"] if virtual else []), "--exit-with-session=startplasma-wayland"]
    print(f"{'Arrancando' if '--aplicar' in args else 'SIMULACIÓN:'} sesión de prueba de {MARCA['nombre']} ({variante}, "
          f"{ancho}×{alto}, {'virtual' if virtual else 'en una ventana'})")
    print(f"  HOME     {casa}\n  runtime  {runtime}\n  orden    env -i … {' '.join(orden)}")
    print(f"  antes    {', '.join(f'{a} {c}={v}' for a, _, c, v in CONFIG_PREVIA)}, kwinrc Desktops Number={escritorios}")
    if "--aplicar" not in args:
        print("(simulación: añade --aplicar para arrancarla)"); return 0
    antes = locked_hint()
    preparar_casa(casa, escritorios)
    runtime.mkdir(mode=0o700)
    env = entorno_inicial(casa, runtime, virtual)
    # los archivos de Lliphi, antes de que arranque Plasma (sin aplicar: eso necesita el bus de la sesión)
    subprocess.run([sys.executable, str(RAIZ / "herramientas" / "instalar.py"), "--aplicar"], cwd=RAIZ, env=env,
                   stdout=subprocess.DEVNULL)
    registro = open(casa.parent / "sesion.log", "w", encoding="utf-8")
    proc = subprocess.Popen(orden, env=env, stdout=registro, stderr=subprocess.STDOUT, start_new_session=True)
    est = {"pid": proc.pid, "casa": str(casa), "runtime": str(runtime), "variante": variante, "virtual": virtual,
           "ancho": ancho, "alto": alto, "inicio": datetime.now().isoformat(timespec="seconds"), "locked_hint_antes": antes}
    STATE.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(est, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  esperando a plasmashell…", flush=True)
    for _ in range(90):
        if plasmashell_de(casa):
            break
        if proc.poll() is not None:
            print(f"la sesión terminó al arrancar (registro: {casa.parent / 'sesion.log'})"); return 4
        time.sleep(1)
    else:
        print(f"plasmashell no apareció en 90 s (registro: {casa.parent / 'sesion.log'}); sesion.py cerrar"); return 4
    time.sleep(6)   # que el shell registre sus servicios en el bus antes de aplicar
    r = instalar_dentro(entorno_dentro(est), variante, None, "--disposicion" in args)
    if r != 0:   # p. ej. «respaldo no verificado»: el plasmashell recién arrancado aún reescribía su configuración
        print("  reintento en 8 s (el shell recién arrancado aún escribía su configuración)", flush=True)
        time.sleep(8)
        r = instalar_dentro(entorno_dentro(est), variante, None, "--disposicion" in args)
    print(f"[sesion] en marcha: PID {proc.pid}, HOME {casa}" + ("" if r == 0 else f" (la aplicación salió {r})"))
    return 0 if r == 0 else r


def con_sesion(f):
    def envoltura(args: list[str]) -> int:
        est = leer_estado()
        if not est or not procesos_de(Path(est["casa"])):
            print("no hay sesión de prueba (sesion.py arrancar --aplicar)"); return 3
        try:
            return f(args, est)
        except (PermissionError, LookupError) as e:
            print("se niega:", e); return 3
    return envoltura


@con_sesion
def recargar(args: list[str], est: dict) -> int:
    variante = valor(args, "--variante", est["variante"])
    r = instalar_dentro(entorno_dentro(est), variante, valor(args, "--modulos", None), "--disposicion" in args)
    if r == 0 and variante != est["variante"]:
        est["variante"] = variante
        ESTADO.write_text(json.dumps(est, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return r


@con_sesion
def ejecutar(args: list[str], est: dict) -> int:
    orden = args[args.index("--") + 1:] if "--" in args else args[1:]
    if not orden:
        print("sesion.py ejecutar -- <orden> [args…]"); return 1
    env = entorno_dentro(est)
    subprocess.Popen(orden, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    print(f"[sesion] lanzado dentro: {' '.join(orden)}")
    return 0


@con_sesion
def guion(args: list[str], est: dict) -> int:
    if len(args) < 2 or not Path(args[1]).is_file():
        print("sesion.py guion <archivo.js>"); return 1
    env = entorno_dentro(est)
    qdbus = shutil.which("qdbus6", path=PATH) or shutil.which("qdbus", path=PATH)
    if not qdbus:
        print("falta qdbus6"); return 2
    r = subprocess.run([qdbus, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript",
                        Path(args[1]).read_text(encoding="utf-8")], env=env, capture_output=True, text=True)
    print(r.stdout, end="")
    print(r.stderr, end="", file=sys.stderr)
    return r.returncode


@con_sesion
def capturar(args: list[str], est: dict) -> int:
    # spectacle habla con el KWin exterior (el dueño de org.kde.KWin en el bus de la sesión, en el primer socket del
    # directorio de ejecución de prueba) y captura su ventana activa, que es la pantalla de Plasma anidada, sin marco
    env = {**entorno_dentro(est), "WAYLAND_DISPLAY": "wayland-0"}
    salida = Path(valor(args, "--salida", str(Path(est["casa"]).parent / "capturas" / f"{datetime.now():%H%M%S}.png")))
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.unlink(missing_ok=True)
    r = subprocess.run(["spectacle", "-b", "-n", "-a", "-e", "-o", str(salida)], env=env, capture_output=True, text=True, timeout=60)
    for _ in range(20):
        if salida.exists():
            break
        time.sleep(0.5)
    print(f"[sesion] captura: {salida}" if salida.exists() else f"no se pudo capturar ({r.stderr.strip()[:200]})")
    return 0 if salida.exists() else 4


def cerrar(args: list[str]) -> int:
    est = leer_estado()
    if not est:
        print("no hay sesión de prueba."); return 0
    casa = Path(est["casa"])
    if not casa.is_relative_to(CACHE) or casa == HOME:
        print(f"se niega: {casa} no es un HOME de prueba"); return 3
    pids = procesos_de(casa)
    for sen in (signal.SIGTERM, signal.SIGKILL):
        for pid in pids:
            if entorno_de(pid).get("HOME") == str(casa):   # se comprueba otra vez justo antes de cada señal
                try:
                    os.kill(pid, sen)
                except ProcessLookupError:
                    pass
        for _ in range(20):
            pids = procesos_de(casa)
            if not pids:
                break
            time.sleep(0.25)
        if not pids:
            break
    runtime = Path(est.get("runtime", ""))
    if runtime.name.startswith(f"{ID}-") and runtime.parent == RUNTIME_REAL:
        shutil.rmtree(runtime, ignore_errors=True)
    despues = locked_hint()
    print(f"[sesion] cerrada ({'quedan procesos: ' + ', '.join(map(str, pids)) if pids else 'sin procesos'}); "
          f"LockedHint de la sesión real: antes {est.get('locked_hint_antes')}, ahora {despues}")
    if est.get("locked_hint_antes") == "no" and despues == "yes":
        print("  aviso: la sesión real quedó marcada como bloqueada (docs/validacion.md §8.3); si tu pantalla está "
              "desbloqueada, devuélvelo con: busctl call org.freedesktop.login1 /org/freedesktop/login1/session/auto "
              "org.freedesktop.login1.Session SetLockedHint b false")
    ESTADO.unlink(missing_ok=True)
    print(f"  el HOME de prueba se conserva en {casa.parent} (bórralo cuando no lo necesites)")
    return 0 if not pids else 4


def estado(args: list[str]) -> int:
    est = leer_estado()
    vivo = bool(est and procesos_de(Path(est["casa"])))
    datos = {**(est or {}), "activa": vivo, "plasmashell": plasmashell_de(Path(est["casa"])) if vivo else None,
             "locked_hint": locked_hint(), "sesiones": str(CACHE)}
    if "--json" in args:
        print(json.dumps(datos, ensure_ascii=False)); return 0
    if not est:
        print("no hay sesión de prueba."); return 0
    print(f"sesión de prueba {'ACTIVA' if vivo else 'terminada'}: {est['variante']}, {est['ancho']}×{est['alto']}"
          f"{' (virtual)' if est['virtual'] else ''}, desde {est['inicio']}\n  HOME {est['casa']}\n  plasmashell {datos['plasmashell']}"
          f"\n  LockedHint de la sesión real: {datos['locked_hint']}")
    return 0


def valor(args: list[str], opcion: str, defecto: str | None) -> str | None:
    return args[args.index(opcion) + 1] if opcion in args and args.index(opcion) + 1 < len(args) else defecto


ORDENES = {"arrancar": arrancar, "estado": estado, "recargar": recargar, "ejecutar": ejecutar, "guion": guion,
           "capturar": capturar, "cerrar": cerrar}


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help") or args[0] not in ORDENES:
        print(__doc__); return 0 if args[:1] in (["-h"], ["--help"]) else 1
    return ORDENES[args[0]](args)


if __name__ == "__main__":
    sys.exit(main())
