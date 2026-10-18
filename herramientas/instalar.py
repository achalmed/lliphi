#!/usr/bin/env python3
"""Instala, actualiza y desinstala el tema en el usuario actual, con simulación, respaldo y reversión.

Solo escribe en `$XDG_DATA_HOME` (`~/.local/share`) y `$XDG_CONFIG_HOME` (`~/.config`); nunca en `/usr`.
Los módulos de terminales y editores dejan sus archivos en `$XDG_CONFIG_HOME/<aplicación>/themes/`; cada aplicación los
importa desde su propia configuración, que el instalador no toca (lo dice `modulos/<id>/INSTALL.md`). La única excepción
a XDG es la extensión de VS Code, que solo se lee desde `~/.vscode/extensions/` (o `$VSCODE_EXTENSIONS`; decisión 3.12);
la misma extensión va a Positron (`~/.positron/extensions/` o `$POSITRON_EXTENSIONS`) y a VSCodium
(`~/.vscode-oss/extensions/` o `$VSCODIUM_EXTENSIONS`) solo si existe la carpeta del editor (`~/.positron`,
`~/.vscode-oss`); si no, el par se omite y la simulación lo dice, sin crearla.
Antes de tocar nada respalda los archivos de configuración que cambia Plasma al aplicar un tema, con su
SHA-256 verificada, en `$XDG_STATE_HOME/<id>/respaldos/<fecha>/` y deja allí un `UNDO.sh` que restaura
byte a byte y desinstala. Lo instalado queda anotado en `$XDG_STATE_HOME/<id>/instalado.json`.

Uso:
  python3 herramientas/instalar.py                       simula la instalación (no escribe nada)
  python3 herramientas/instalar.py --aplicar             instala los módulos
  python3 herramientas/instalar.py --dependencias --aplicar   además descarga Papirus y Bibata al usuario (herramientas/dependencias.py)
  python3 herramientas/instalar.py --aplicar --aplicar-tema oscuro|claro   además aplica el tema global
  python3 herramientas/instalar.py --modulos esquema,konsole --aplicar
  python3 herramientas/instalar.py desinstalar [--aplicar]
  python3 herramientas/instalar.py estado
Solo biblioteca estándar; Python ≥ 3.10. Sale 0 bien, 1 error de uso, 2 falta una dependencia, 3 conflicto.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GENERADO = RAIZ / "generado"
MARCA = json.loads((RAIZ / "tokens" / "marca.json").read_text(encoding="utf-8"))
ID = MARCA["id"]
VERSION = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()

HOME = Path.home()
DATA = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local" / "share")
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or HOME / ".config")
STATE = Path(os.environ.get("XDG_STATE_HOME") or HOME / ".local" / "state") / ID
VSCODE = Path(os.environ.get("VSCODE_EXTENSIONS") or HOME / ".vscode" / "extensions")
POSITRON = Path(os.environ.get("POSITRON_EXTENSIONS") or HOME / ".positron" / "extensions")
VSCODIUM = Path(os.environ.get("VSCODIUM_EXTENSIONS") or HOME / ".vscode-oss" / "extensions")
MANIFIESTO = STATE / "instalado.json"

# archivos de configuración que Plasma reescribe al aplicar un tema global: se respaldan siempre
CONFIGS = ["kdeglobals", "plasmarc", "kwinrc", "kcminputrc", "ksplashrc", "kscreenlockerrc",
           "plasma-org.kde.plasma.desktop-appletsrc", "gtk-3.0/settings.ini", "gtk-4.0/settings.ini",
           "konsolerc", "breezerc"]

# módulo → [(origen relativo a generado/, destino relativo a la base, base)]; la base es "data" (XDG_DATA_HOME, por
# omisión si el par tiene dos elementos), "config" (XDG_CONFIG_HOME), "vscode" (~/.vscode/extensions) o una base condicional
# ("positron", "vscodium"): solo se instala si existe la carpeta del editor (CONDICIONALES); si no, se omite y se avisa
MODULOS = {
    "esquema": [(f"color-schemes/{MARCA['id_esquema'][v]}.colors", f"color-schemes/{MARCA['id_esquema'][v]}.colors") for v in ("claro", "oscuro")],
    "estilo": [(f"desktoptheme/{ID}-{v}", f"plasma/desktoptheme/{ID}-{v}") for v in ("claro", "oscuro")],
    "kvantum": [(f"kvantum/{MARCA['id_esquema'][v]}", f"../../.config/Kvantum/{MARCA['id_esquema'][v]}") for v in ("claro", "oscuro")],
    "global": [(f"look-and-feel/{MARCA['id_global'][v]}", f"plasma/look-and-feel/{MARCA['id_global'][v]}") for v in ("claro", "oscuro")],
    "konsole": [(f"konsole/{MARCA['nombre_esquema'][v]}.colorscheme", f"konsole/{MARCA['nombre_esquema'][v]}.colorscheme") for v in ("claro", "oscuro")],
    "fondos": [(f"wallpapers/{MARCA['id_fondo']}", f"wallpapers/{MARCA['id_fondo']}")],
    "terminales": [(f"terminales/alacritty/{ID}-{v}.toml", f"alacritty/themes/{ID}-{v}.toml", "config") for v in ("claro", "oscuro")]
                + [(f"terminales/kitty/{ID}-{v}.conf", f"kitty/themes/{ID}-{v}.conf", "config") for v in ("claro", "oscuro")],
    "editores": [(f"editores/vscode/{ID}", f"{ID}.{ID}", "vscode"), (f"editores/vscode/{ID}", f"{ID}.{ID}", "positron"),
                 (f"editores/vscode/{ID}", f"{ID}.{ID}", "vscodium"), (f"editores/zed/{ID}.json", f"zed/themes/{ID}.json", "config")],
    "decoracion": [(f"aurorae/{ID}", f"aurorae/themes/{ID}"), (f"aurorae/{ID}-claro", f"aurorae/themes/{ID}-claro")],
}
BASES = {"data": DATA, "config": CONFIG, "vscode": VSCODE, "positron": POSITRON, "vscodium": VSCODIUM}
# base condicional → (carpeta que debe existir, nombre del editor); el instalador nunca crea esa carpeta
CONDICIONALES = {"positron": (POSITRON.parent, "Positron"), "vscodium": (VSCODIUM.parent, "VSCodium")}


def pares_de(modulos: list[str]) -> tuple[list[tuple[Path, Path]], list[str]]:
    """(origen absoluto en generado/, destino absoluto) de cada archivo o carpeta de los módulos pedidos, y los avisos
    de los pares omitidos porque su base condicional no existe (no se instala Positron donde no hay Positron)."""
    pares, omitidos = [], []
    for m in modulos:
        for par in MODULOS[m]:
            origen, destino, *base = par
            b = base[0] if base else "data"
            if b in CONDICIONALES and not CONDICIONALES[b][0].is_dir():
                omitidos.append(f"omitido {origen} → {BASES[b] / destino}: no existe {CONDICIONALES[b][0]} ({CONDICIONALES[b][1]} no está instalado)")
                continue
            pares.append((GENERADO / origen, BASES[b] / destino))
    return pares, omitidos
DEPENDENCIAS = {"global": ["plasma-apply-lookandfeel"], "esquema": ["plasma-apply-colorscheme"]}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def plasma_version() -> str | None:
    try:
        out = subprocess.run(["plasmashell", "--version"], capture_output=True, text=True, timeout=10).stdout
        return out.strip().split()[-1]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return None


def comprobar_dependencias(modulos: list[str]) -> list[str]:
    faltan = []
    v = plasma_version()
    if v is None:
        faltan.append("plasmashell (Plasma 6) no se encuentra en el PATH")
    elif int(v.split(".")[0]) < 6:
        faltan.append(f"Plasma {v}: se necesita Plasma 6")
    for m in modulos:
        for herramienta in DEPENDENCIAS.get(m, []):
            if shutil.which(herramienta) is None:
                faltan.append(f"{herramienta} (módulo {m})")
    return faltan


def ajeno(origen: Path, destino: Path) -> bool:
    """True si en el destino hay algo que no instaló este proyecto: no consta en el manifiesto y su contenido
    no es idéntico a lo que se instalaría (una reinstalación idéntica nunca es conflicto)."""
    if not destino.exists():
        return False
    if MANIFIESTO.exists():
        previo = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        if str(destino) in previo.get("rutas", {}):
            return False
    return sha_dir(destino) != sha_dir(origen)


def respaldar(aplicar: bool) -> Path:
    sello = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    carpeta = STATE / "respaldos" / sello
    sumas = {}
    for rel in CONFIGS:
        origen = CONFIG / rel
        if origen.exists():
            destino = carpeta / "config" / rel
            if aplicar:
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origen, destino)
                if sha(origen) != sha(destino):
                    raise SystemExit(f"respaldo no verificado: {rel}")
            sumas[rel] = sha(origen)
            print(f"  {'respaldado' if aplicar else 'SIM respaldar'} {rel}")
    if aplicar:
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "sumas.json").write_text(json.dumps(sumas, indent=2) + "\n", encoding="utf-8")
    return carpeta


def escribir_undo(carpeta: Path, rutas: list[Path]) -> None:
    lineas = ["#!/usr/bin/env bash", f"# UNDO de {MARCA['nombre']} {VERSION}: restaura la configuración respaldada en {carpeta.name} y desinstala.",
              "set -euo pipefail", f'CONFIG="{CONFIG}"', f'RESPALDO="{carpeta}"', ""]
    for rel in CONFIGS:
        lineas.append(f'[ -f "$RESPALDO/config/{rel}" ] && mkdir -p "$(dirname "$CONFIG/{rel}")" && cp -p "$RESPALDO/config/{rel}" "$CONFIG/{rel}" && echo "restaurado {rel}"')
    for r in rutas:
        lineas.append(f'rm -rf "{r}" && echo "retirado {r}"')
    lineas += [f'rm -f "{MANIFIESTO}"', 'echo "Listo. Cierra la sesión y vuelve a entrar para que Plasma relea la configuración."']
    undo = carpeta / "UNDO.sh"
    undo.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    undo.chmod(0o755)


def instalar(modulos: list[str], aplicar: bool, aplicar_tema: str | None) -> int:
    faltan = comprobar_dependencias(modulos)
    if faltan:
        print("faltan dependencias:\n  " + "\n  ".join(faltan)); return 2
    print(f"{'Instalando' if aplicar else 'SIMULACIÓN de'} {MARCA['nombre']} {VERSION} en {DATA}")
    pares, omitidos = pares_de(modulos)
    for aviso in omitidos:
        print(f"  {aviso}")
    conflictos = [d for o, d in pares if ajeno(o, d)]
    if conflictos:
        print("en el destino hay archivos que no instaló este proyecto; no se tocan:\n  " + "\n  ".join(map(str, conflictos)))
        print("retíralos tú o instala en otro usuario."); return 3
    carpeta = respaldar(aplicar)
    for origen, destino in pares:
        if not origen.exists():
            print(f"  falta en generado/: {origen.relative_to(RAIZ)} (ejecuta herramientas/generar.py --aplicar)"); return 1
        print(f"  {'copiado' if aplicar else 'SIM copiar'} {origen.relative_to(GENERADO)} → {destino}")
        if aplicar:
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                shutil.rmtree(destino) if destino.is_dir() else destino.unlink()
            shutil.copytree(origen, destino) if origen.is_dir() else shutil.copy2(origen, destino)
    if aplicar:
        STATE.mkdir(parents=True, exist_ok=True)
        # el manifiesto acumula: instalar solo algunos módulos no olvida los ya instalados
        previo = json.loads(MANIFIESTO.read_text(encoding="utf-8")) if MANIFIESTO.exists() else {}
        rutas = {k: v for k, v in previo.get("rutas", {}).items() if Path(k).exists()}
        rutas.update({str(d): sha_dir(d) for _, d in pares})
        MANIFIESTO.write_text(json.dumps({"version": VERSION, "fecha": datetime.now().isoformat(timespec="seconds"),
                                          "modulos": sorted(set(previo.get("modulos", [])) | set(modulos)), "rutas": rutas,
                                          "respaldo": str(carpeta)}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        escribir_undo(carpeta, [d for _, d in pares])
        print(f"  manifiesto: {MANIFIESTO}\n  reversión: {carpeta / 'UNDO.sh'}")
    if aplicar_tema:
        id_global = MARCA["id_global"][aplicar_tema]
        orden = ["plasma-apply-lookandfeel", "-a", id_global]
        print(f"  {'ejecutando' if aplicar else 'SIM ejecutar'}: {' '.join(orden)}")
        if aplicar:
            r = subprocess.run(orden, capture_output=True, text=True)
            print("  " + (r.stdout + r.stderr).strip()[-300:])
            if r.returncode:
                return 1
            # el fondo por ruta (Plasma 6.6 no resuelve el nombre del paquete de usuario) y los iconos de carpeta
            fondo = DATA / "wallpapers" / MARCA["id_fondo"]
            if "fondos" in modulos and fondo.exists() and shutil.which("plasma-apply-wallpaperimage"):
                subprocess.run(["plasma-apply-wallpaperimage", str(fondo)], capture_output=True, text=True)
                print(f"  fondo aplicado: {fondo}")
            # menús translúcidos con desenfoque en las aplicaciones Qt (función de serie de Breeze): el vidrio llega a las apps
            tokens = json.loads((RAIZ / "tokens" / "tokens.json").read_text(encoding="utf-8"))
            opacidad_menus = tokens.get("efectos", {}).get("opacidad-menus-qt", {}).get("$value", 80)
            if shutil.which("kwriteconfig6"):
                subprocess.run(["kwriteconfig6", "--file", "breezerc", "--group", "Style", "--key", "MenuOpacity", str(opacidad_menus)], capture_output=True, text=True)
                print(f"  menús de Breeze al {opacidad_menus} % (breezerc, respaldado)")
            # Kvantum: tema activo y estilo de widgets
            kvdir = CONFIG / "Kvantum"
            if "kvantum" in modulos and kvdir.exists():
                kvdir.mkdir(parents=True, exist_ok=True)
                tema_kv = MARCA["id_esquema"][aplicar_tema]
                (kvdir / "kvantum.kvconfig").write_text(f"[General]\ntheme={tema_kv}\n", encoding="utf-8")
                if shutil.which("kwriteconfig6"):
                    subprocess.run(["kwriteconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "widgetStyle", "kvantum-dark" if aplicar_tema == "oscuro" else "kvantum"], capture_output=True, text=True)
                print(f"  Kvantum: tema {tema_kv}, estilo kvantum")
            # tipografía IBM Plex en toda la sesión (lo que fija defaults solo lo lee el KCM al aplicar el tema)
            if shutil.which("kwriteconfig6"):
                for clave, valor in (("font", "Hack,10,-1,5,400,0,0,0,0,0"), ("fixed", "Hack,10,-1,5,400,0,0,0,0,0"),
                                     ("menuFont", "Hack,10,-1,5,400,0,0,0,0,0"), ("toolBarFont", "Hack,10,-1,5,400,0,0,0,0,0"),
                                     ("smallestReadableFont", "Hack,8,-1,5,400,0,0,0,0,0")):
                    subprocess.run(["kwriteconfig6", "--file", "kdeglobals", "--group", "General", "--key", clave, valor], capture_output=True, text=True)
                subprocess.run(["kwriteconfig6", "--file", "kdeglobals", "--group", "WM", "--key", "activeFont", "Hack,10,-1,5,700,0,0,0,0,0"], capture_output=True, text=True)
                subprocess.run(["dbus-send", "--session", "--type=signal", "/KGlobalSettings", "org.kde.KGlobalSettings.notifyChange", "int32:0", "int32:0"], capture_output=True, text=True)
                print("  tipografía: Hack 10 (interfaz y terminal)")
            iconos = "Papirus-Dark" if aplicar_tema == "oscuro" else "Papirus-Light"
            if (DATA / "icons" / iconos).exists():
                if shutil.which("plasma-changeicons"):
                    subprocess.run(["plasma-changeicons", iconos], capture_output=True, text=True)
                elif shutil.which("kwriteconfig6"):
                    subprocess.run(["kwriteconfig6", "--file", "kdeglobals", "--group", "Icons", "--key", "Theme", iconos], capture_output=True, text=True)
                    subprocess.run(["dbus-send", "--session", "--type=signal", "/KIconLoader", "org.kde.KIconLoader.iconChanged", "int32:0"], capture_output=True, text=True)
                print(f"  iconos aplicados: {iconos}")
            # decoración Aurorae: `plasma-apply-lookandfeel` no siempre escribe el grupo [org.kde.kdecoration2] de los
            # defaults (comprobado en sesión anidada, docs/validacion.md §6); se escribe aquí y se avisa a KWin
            deco = ID if aplicar_tema == "oscuro" else f"{ID}-claro"
            if "decoracion" in modulos and (DATA / "aurorae" / "themes" / deco).exists() and shutil.which("kwriteconfig6"):
                for clave, valor in (("library", "org.kde.kwin.aurorae.v2"), ("theme", f"__aurorae__svg__{deco}"), ("ButtonsOnLeft", ""), ("ButtonsOnRight", "IAX")):
                    subprocess.run(["kwriteconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", clave, valor], capture_output=True, text=True)
                if shutil.which("qdbus6"):
                    subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "org.kde.KWin.reconfigure"], capture_output=True, text=True)
                print(f"  decoración aplicada: __aurorae__svg__{deco}")
    print("hecho." if aplicar else "nada escrito; añade --aplicar para instalar.")
    return 0


def sha_dir(p: Path) -> str:
    h = hashlib.sha256()
    if p.is_file():
        return sha(p)
    for f in sorted(x for x in p.rglob("*") if x.is_file()):
        h.update(str(f.relative_to(p)).encode()); h.update(f.read_bytes())
    return h.hexdigest()


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
    if aplicar:
        MANIFIESTO.unlink()
        print("hecho. Si el tema estaba aplicado, elige otro en Preferencias del sistema → Apariencia o ejecuta UNDO.sh.")
    return 0


def estado() -> int:
    if MANIFIESTO.exists():
        m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        print(f"{MARCA['nombre']} {m['version']} instalado el {m['fecha']}: módulos {', '.join(m['modulos'])}")
        for ruta, suma in m["rutas"].items():
            p = Path(ruta)
            print(f"  {'ok ' if p.exists() and sha_dir(p) == suma else 'MOD'} {ruta}")
    else:
        print("no instalado.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    aplicar = "--aplicar" in args
    modulos = list(MODULOS)
    if "--modulos" in args:
        modulos = args[args.index("--modulos") + 1].split(",")
        desconocidos = [m for m in modulos if m not in MODULOS]
        if desconocidos:
            print("módulos desconocidos:", ", ".join(desconocidos)); return 1
    aplicar_tema = args[args.index("--aplicar-tema") + 1] if "--aplicar-tema" in args else None
    if aplicar_tema and aplicar_tema not in ("claro", "oscuro"):
        print("--aplicar-tema claro|oscuro"); return 1
    if "--dependencias" in args or "dependencias" in args:
        r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "dependencias.py"), *(["--aplicar"] if aplicar else [])])
        if r.returncode or "dependencias" in args:
            return r.returncode
    if "desinstalar" in args:
        return desinstalar(aplicar)
    if "estado" in args:
        return estado()
    if "-h" in args or "--help" in args:
        print(__doc__); return 0
    return instalar(modulos, aplicar, aplicar_tema)


if __name__ == "__main__":
    sys.exit(main())
