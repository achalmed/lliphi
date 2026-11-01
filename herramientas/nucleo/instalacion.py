"""Instalación, aplicación, desinstalación y comprobación en el usuario actual, con simulación, respaldo y reversión.

Qué se copia y adónde lo dice la lista `instalacion` del `modulo.json` de cada módulo (origen relativo a
`generado/<id>/`, destino relativo a su base). Bases: `data` ($XDG_DATA_HOME), `config` ($XDG_CONFIG_HOME), `vscode`
(~/.vscode/extensions o $VSCODE_EXTENSIONS) y las condicionales `positron` y `vscodium`, que solo se usan si existe la
carpeta del editor (nunca se crea). Nunca se escribe en `/usr` (el inicio de sesión SDDM tiene su propia orden con
pkexec: `instalar.py sddm`).

Antes de tocar nada se respaldan, con su SHA-256 verificada, los archivos que declaran los `respaldos()` de los
`aplicar.py` de los módulos (la configuración que Plasma reescribe al aplicar un tema, el perfil de Konsole, las notas
de Plasma) en `$XDG_STATE_HOME/<id>/respaldos/<fecha>/`, con un `UNDO.sh` que restaura y desinstala. Lo instalado
queda en `$XDG_STATE_HOME/<id>/instalado.json`. Con `--aplicar-tema` se llama al `aplicar()` del tema global y después
al de cada módulo, en el orden del registro. Solo biblioteca estándar; Python ≥ 3.10."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from . import RAIZ, VERSION, cargar, registro

_, MARCA = cargar()
ID = MARCA["id"]

HOME = Path.home()
DATA = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local" / "share")
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or HOME / ".config")
STATE = Path(os.environ.get("XDG_STATE_HOME") or HOME / ".local" / "state") / ID
VSCODE = Path(os.environ.get("VSCODE_EXTENSIONS") or HOME / ".vscode" / "extensions")
POSITRON = Path(os.environ.get("POSITRON_EXTENSIONS") or HOME / ".positron" / "extensions")
VSCODIUM = Path(os.environ.get("VSCODIUM_EXTENSIONS") or HOME / ".vscode-oss" / "extensions")
MANIFIESTO = STATE / "instalado.json"

BASES = {"data": DATA, "config": CONFIG, "vscode": VSCODE, "positron": POSITRON, "vscodium": VSCODIUM}
# base condicional → (carpeta que debe existir, nombre del editor); el instalador nunca crea esa carpeta
CONDICIONALES = {"positron": (POSITRON.parent, "Positron"), "vscodium": (VSCODIUM.parent, "VSCodium")}
# formato → tipo con que `kpackagetool6 --type <tipo> --show <id>` encuentra un paquete de usuario (comprobar). `--list`
# no sirve: omite los paquetes sin `KPackageStructure`, como los estilos de Plasma (también Breeze). Los fondos
# (`Wallpaper/Images`) no se resuelven así ni siquiera los del sistema (`Next`): se comprueban solo por sus archivos.
KPACKAGE = {"Plasma/LookAndFeel": "Plasma/LookAndFeel", "Plasma/Theme": "Plasma/Theme", "KWin/Aurorae": "KWin/Aurorae"}


@dataclass
class Contexto:
    """Lo que recibe el `aplicar()` y el `respaldos()` de cada módulo."""
    variante: str
    modulos: list[str]
    marca: dict = field(default_factory=lambda: MARCA)
    tokens: dict = field(default_factory=lambda: cargar()[0])
    DATA: Path = DATA
    CONFIG: Path = CONFIG

    @staticmethod
    def hay(herramienta: str) -> bool:
        return shutil.which(herramienta) is not None

    @staticmethod
    def decir(texto: str) -> None:
        print(f"  {texto}")

    @staticmethod
    def codigo(id_: str, archivo: str = "construir"):
        return registro.codigo(id_, archivo)

    def ejecutar(self, orden: list[str], mostrar: bool = False) -> subprocess.CompletedProcess:
        if mostrar:
            self.decir(f"ejecutando: {' '.join(orden)}")
        return subprocess.run(orden, capture_output=True, text=True)

    def kwrite(self, archivo: str, grupos: list[str], clave: str, valor: str) -> bool:
        """`kwriteconfig6 --file <archivo> --group … --key <clave> <valor>`; False si no está kwriteconfig6."""
        if not self.hay("kwriteconfig6"):
            return False
        orden = ["kwriteconfig6", "--file", archivo]
        for g in grupos:
            orden += ["--group", g]
        self.ejecutar(orden + ["--key", clave, valor])
        return True


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha_dir(p: Path) -> str:
    h = hashlib.sha256()
    if p.is_file():
        return sha(p)
    for f in sorted(x for x in p.rglob("*") if x.is_file()):
        h.update(str(f.relative_to(p)).encode()); h.update(f.read_bytes())
    return h.hexdigest()


def _norm(ruta: str | Path) -> str:
    """Ruta sin `..` ni `.`: el manifiesto de 0.3.0 guardaba Kvantum como `…/.local/share/../../.config/Kvantum/…`."""
    return os.path.normpath(str(ruta))


def instalables(seleccion: list[str]) -> list[str]:
    """De lo pedido, los módulos que instalan archivos propios."""
    return [i for i in seleccion if registro.modulo(i).datos.get("instalacion")]


def pares_de(seleccion: list[str]) -> tuple[list[tuple[Path, Path]], list[str]]:
    """(origen absoluto en generado/, destino absoluto) de cada archivo o carpeta de los módulos pedidos, y los avisos
    de los pares omitidos porque su base condicional no existe (no se instala Positron donde no hay Positron)."""
    pares, omitidos = [], []
    for i in seleccion:
        m = registro.modulo(i)
        for par in m.datos.get("instalacion", []):
            origen, destino, b = par["origen"].format(**MARCA), par["destino"].format(**MARCA), par.get("base", "data")
            if b in CONDICIONALES and not CONDICIONALES[b][0].is_dir():
                omitidos.append(f"omitido {i}/{origen} → {BASES[b] / destino}: no existe {CONDICIONALES[b][0]} ({CONDICIONALES[b][1]} no está instalado)")
                continue
            pares.append((m.generado / origen, BASES[b] / destino))
    return pares, omitidos


def plasma_version() -> str | None:
    try:
        out = subprocess.run(["plasmashell", "--version"], capture_output=True, text=True, timeout=10).stdout
        return out.strip().split()[-1]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return None


def comprobar_dependencias(seleccion: list[str]) -> list[str]:
    faltan = []
    v = plasma_version()
    if v is None:
        faltan.append("plasmashell (Plasma 6) no se encuentra en el PATH")
    elif int(v.split(".")[0]) < 6:
        faltan.append(f"Plasma {v}: se necesita Plasma 6")
    for i in instalables(seleccion):
        for herramienta in registro.modulo(i).dependencias("herramientas"):
            if shutil.which(herramienta) is None:
                faltan.append(f"{herramienta} (módulo {i})")
    return faltan


def ajeno(origen: Path, destino: Path) -> bool:
    """True si en el destino hay algo que no instaló este proyecto: no consta en el manifiesto y su contenido
    no es idéntico a lo que se instalaría (una reinstalación idéntica nunca es conflicto)."""
    if not destino.exists():
        return False
    if MANIFIESTO.exists():
        previo = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        if _norm(destino) in {_norm(r) for r in previo.get("rutas", {})}:
            return False
    return sha_dir(destino) != sha_dir(origen)


def _respaldables(ctx: Contexto) -> list[tuple[Path, str, str, Path]]:
    """(ruta, modo, rótulo, ruta dentro del respaldo) de lo que declaran los `respaldos()` de todos los módulos.
    Modos: `reponer` (archivo que UNDO.sh devuelve tal cual) y `completar` (carpeta cuyos archivos que falten repone)."""
    salida = []
    for m in registro.con("aplicar"):
        mod = registro.codigo(m.id, "aplicar")
        for ruta, modo, rotulo in (mod.respaldos(ctx) if hasattr(mod, "respaldos") else []):
            base, sub = (("config", ruta.relative_to(CONFIG)) if ruta.is_relative_to(CONFIG) else ("data", ruta.relative_to(DATA)))
            salida.append((ruta, modo, rotulo, Path(base) / sub))
    return salida


def respaldar(ctx: Contexto, aplicar: bool) -> tuple[Path, list[tuple[Path, str, str, Path]]]:
    """Copia lo que existe de lo respaldable y devuelve todo lo respaldable (para el UNDO.sh)."""
    carpeta = STATE / "respaldos" / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    sumas, todos = {}, _respaldables(ctx)
    for ruta, modo, rotulo, rel in todos:
        if not ruta.exists() or (modo == "completar" and not any(ruta.iterdir())):
            continue
        destino = carpeta / rel
        if aplicar:
            destino.parent.mkdir(parents=True, exist_ok=True)
            if modo == "completar":
                shutil.copytree(ruta, destino, dirs_exist_ok=True)
            else:
                shutil.copy2(ruta.resolve(), destino)
                if sha(ruta) != sha(destino):
                    raise SystemExit(f"respaldo no verificado: {rotulo}")
        if modo == "reponer":
            sumas[str(rel.relative_to(rel.parts[0]))] = sha(ruta)
        print(f"  {'respaldado' if aplicar else 'SIM respaldar'} {rotulo}")
    if aplicar:
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "sumas.json").write_text(json.dumps(sumas, indent=2) + "\n", encoding="utf-8")
    return carpeta, todos


def escribir_undo(carpeta: Path, respaldados: list[tuple[Path, str, str, Path]], rutas: list[Path]) -> None:
    lineas = ["#!/usr/bin/env bash", f"# UNDO de {MARCA['nombre']} {VERSION}: restaura la configuración respaldada en {carpeta.name} y desinstala.",
              "set -euo pipefail", f'CONFIG="{CONFIG}"', f'DATA="{DATA}"', f'RESPALDO="{carpeta}"', ""]
    for ruta, modo, rotulo, rel in respaldados:
        base = "$CONFIG" if rel.parts[0] == "config" else "$DATA"
        sub = rel.relative_to(rel.parts[0]).as_posix()
        if modo == "completar":
            lineas.append(f'[ -d "$RESPALDO/{rel.as_posix()}" ] && mkdir -p "{base}/{sub}" && cp -rn "$RESPALDO/{rel.as_posix()}/." "{base}/{sub}/" && echo "restauradas las {rotulo.split(" (")[0]} que faltaban"')
        else:
            lineas.append(f'[ -f "$RESPALDO/{rel.as_posix()}" ] && mkdir -p "$(dirname "{base}/{sub}")" && cp -p "$RESPALDO/{rel.as_posix()}" "{base}/{sub}" && echo "restaurado {rotulo}"')
    for r in rutas:
        lineas.append(f'rm -rf "{r}" && echo "retirado {r}"')
    lineas += [f'rm -f "{MANIFIESTO}"', 'echo "Listo. Cierra la sesión y vuelve a entrar para que Plasma relea la configuración."']
    undo = carpeta / "UNDO.sh"
    undo.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    undo.chmod(0o755)


def a_aplicar(seleccion: list[str]) -> list[str]:
    """Los módulos cuyo `aplicar()` corre con `--aplicar-tema`: el tema global siempre (aplicar el tema es aplicar el
    global), lo pedido, y los componentes y externos que el tema global integra o nombra, que no tienen archivos
    propios y solo existen a través de él."""
    g = registro.modulo("global")
    sin_archivos = [i for i in g.dependencias("integra") + g.dependencias("referencia") if registro.modulo(i).clase != "paquete"]
    quiero = {"global", *seleccion, *sin_archivos}
    # un aplicar.py puede declarar solo respaldos() (disposicion): entonces no hay nada que aplicar en la sesión
    return [m.id for m in registro.con("aplicar") if m.id in quiero and hasattr(registro.codigo(m.id, "aplicar"), "aplicar")]


def instalar(seleccion: list[str], aplicar: bool, aplicar_tema: str | None) -> int:
    faltan = comprobar_dependencias(seleccion)
    if faltan:
        print("faltan dependencias:\n  " + "\n  ".join(faltan)); return 2
    print(f"{'Instalando' if aplicar else 'SIMULACIÓN de'} {MARCA['nombre']} {VERSION} en {DATA}")
    pares, omitidos = pares_de(seleccion)
    for aviso in omitidos:
        print(f"  {aviso}")
    conflictos = [d for o, d in pares if ajeno(o, d)]
    if conflictos:
        print("en el destino hay archivos que no instaló este proyecto; no se tocan:\n  " + "\n  ".join(map(str, conflictos)))
        print("retíralos tú o instala en otro usuario."); return 3
    ctx = Contexto(variante=aplicar_tema or "oscuro", modulos=seleccion)
    carpeta, respaldados = respaldar(ctx, aplicar)
    for origen, destino in pares:
        if not origen.exists():
            print(f"  falta en generado/: {origen.relative_to(RAIZ)} (ejecuta herramientas/generar.py --aplicar)"); return 1
        print(f"  {'copiado' if aplicar else 'SIM copiar'} {origen.relative_to(RAIZ / 'generado')} → {destino}")
        if aplicar:
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                shutil.rmtree(destino) if destino.is_dir() else destino.unlink()
            shutil.copytree(origen, destino) if origen.is_dir() else shutil.copy2(origen, destino)
    if aplicar:
        STATE.mkdir(parents=True, exist_ok=True)
        # el manifiesto acumula: instalar solo algunos módulos no olvida los ya instalados
        previo = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.exists() else {}
        rutas = {_norm(k): v for k, v in previo.get("rutas", {}).items() if Path(k).exists()}
        rutas.update({_norm(d): sha_dir(d) for _, d in pares})
        MANIFIESTO.write_text(json.dumps({"version": VERSION, "fecha": datetime.now().isoformat(timespec="seconds"),
                                          "modulos": sorted(set(previo.get("modulos", [])) | set(instalables(seleccion))), "rutas": rutas,
                                          "respaldo": str(carpeta)}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        escribir_undo(carpeta, respaldados, [d for _, d in pares])
        print(f"  manifiesto: {MANIFIESTO}\n  reversión: {carpeta / 'UNDO.sh'}")
    if aplicar_tema:
        orden = a_aplicar(seleccion)
        if not aplicar:
            print(f"  SIM ejecutar: plasma-apply-lookandfeel -a {MARCA['id_global'][aplicar_tema]}")
            print(f"  SIM aplicar en la sesión: {', '.join(orden)}")
        else:
            for id_ in orden:
                if registro.codigo(id_, "aplicar").aplicar(ctx):
                    print(f"  falló la aplicación de {id_}; lo demás no se aplica"); return 1
    print("hecho." if aplicar else "nada escrito; añade --aplicar para instalar.")
    return 0


def desinstalar(aplicar: bool) -> int:
    if not MANIFIESTO.exists():
        print("no hay nada instalado por este proyecto (sin manifiesto)."); return 0
    m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    print(f"{'Desinstalando' if aplicar else 'SIMULACIÓN de desinstalar'} {MARCA['nombre']} {m['version']}")
    for ruta in m["rutas"]:
        p = Path(ruta)
        print(f"  {'retirado' if aplicar else 'SIM retirar'} {p}")
        if aplicar and p.exists():
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    respaldo = Path(m["respaldo"])
    print(f"  la configuración previa está en {respaldo} (UNDO.sh la restaura entera)")
    print("  las dependencias de terceros (Colloid y su superpuesto -Lliphi, Papirus, Papirus-Dark-Lliphi, cursores, tipografías) no se retiran")
    if aplicar:
        MANIFIESTO.unlink()
        print("hecho. Si el tema estaba aplicado, elige otro en Preferencias del sistema → Apariencia o ejecuta UNDO.sh.")
    return 0


def estado(como_json: bool = False) -> int:
    if como_json:   # forma de máquina (Lliphi Studio): qué está instalado y si cada ruta sigue como se instaló
        datos: dict = {"instalado": MANIFIESTO.exists(), "version_proyecto": VERSION, "manifiesto": str(MANIFIESTO)}
        if MANIFIESTO.exists():
            m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
            datos.update({k: m.get(k) for k in ("version", "fecha", "modulos", "respaldo")})
            datos["rutas"] = [{"ruta": r, "ok": Path(r).exists() and sha_dir(Path(r)) == suma} for r, suma in m["rutas"].items()]
        print(json.dumps(datos, ensure_ascii=False))
        return 0
    if MANIFIESTO.exists():
        m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        print(f"{MARCA['nombre']} {m['version']} instalado el {m['fecha']}: módulos {', '.join(m['modulos'])}")
        for ruta, suma in m["rutas"].items():
            p = Path(ruta)
            print(f"  {'ok ' if p.exists() and sha_dir(p) == suma else 'MOD'} {ruta}")
    else:
        print("no instalado.")
    return 0


def _tema_freedesktop(nombre: str) -> bool:
    return any((d / nombre / "index.theme").exists() for d in (DATA / "icons", HOME / ".icons", Path("/usr/share/icons")))


def comprobar() -> int:
    """Que lo instalado esté completo y sea lo de esta versión, que KDE lo reconozca y que lo que el tema global nombra
    exista en el sistema. Sale 0 si todo está, 4 si falta o difiere algo."""
    fallos = 0

    def linea(ok: bool, texto: str, aviso: bool = False) -> None:
        nonlocal fallos
        print(f"  {'ok   ' if ok else ('aviso' if aviso else 'FALTA')} {texto}")
        fallos += 0 if ok or aviso else 1

    if not MANIFIESTO.exists():
        print("no instalado (sin manifiesto)."); return 4
    m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    print(f"Comprobando {MARCA['nombre']} {m['version']} (esta copia del proyecto: {VERSION})")
    linea(m["version"] == VERSION, f"versión instalada {m['version']} = versión del proyecto {VERSION}", aviso=True)
    instaladas = {_norm(r) for r in m["rutas"]}
    for i in [x for x in m["modulos"] if x in registro.ids()]:
        pares, _ = pares_de([i])
        for origen, destino in pares:
            linea(_norm(destino) in instaladas and destino.exists() and sha_dir(destino) == sha_dir(origen),
                  f"{i}: {destino} {'igual a generado/' if destino.exists() else 'no está'}")
        tipo = KPACKAGE.get(registro.modulo(i).datos["formato"])
        if tipo and shutil.which("kpackagetool6"):
            env = {**os.environ, "XDG_DATA_HOME": str(DATA)}
            for origen, _ in pares:
                r = subprocess.run(["kpackagetool6", "--type", tipo, "--show", origen.name], capture_output=True, text=True, env=env)
                linea(r.returncode == 0, f"{i}: KDE reconoce {origen.name} como {tipo} (kpackagetool6 --show)")
    # lo que el tema global declara y no instala este proyecto
    iconos = registro.codigo("iconos-cursores")
    for v in ("claro", "oscuro"):
        tema, base = iconos.tema(v), iconos.ICONOS[v]
        reserva = iconos.RESERVA.get(v) or ("breeze-dark" if v == "oscuro" else "breeze")
        linea(_tema_freedesktop(tema) or _tema_freedesktop(base) or _tema_freedesktop(reserva),
              f"iconos {tema} ({v}), {base} o su reserva {reserva}", aviso=not _tema_freedesktop(tema))
    linea(any((d / iconos.CURSORES / "cursors").is_dir() for d in (DATA / "icons", HOME / ".icons", Path("/usr/share/icons"))),
          f"cursores {iconos.CURSORES} (instalar.py dependencias --aplicar)", aviso=True)
    familias = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
    for familia in ("Inter", "JetBrainsMono Nerd Font"):
        linea(familia in familias, f"tipografía {familia}", aviso=True)
    print(f"[comprobar] {'todo en su sitio' if not fallos else f'{fallos} falta(s) o diferencia(s)'}")
    return 0 if not fallos else 4


def dependencias(aplicar: bool, opcionales: bool) -> int:
    """Instala lo de terceros que el tema nombra (los `externas.py` de los módulos) en el usuario, sin root."""
    print(f"{'Instalando' if aplicar else 'SIMULACIÓN de'} dependencias en {DATA}")
    for m in registro.con("externas"):
        registro.codigo(m.id, "externas").instalar(aplicar, opcionales)
    return 0
