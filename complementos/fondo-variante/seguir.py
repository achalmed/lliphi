#!/usr/bin/env python3
"""@NOMBRE@: el fondo y Konsole siguen a la variante. GENERADO por herramientas/generar.py desde complementos/fondo-variante; no editar.

Al cambiar el tema global (o el esquema de color) entre @NOMBRE@ Claro y @NOMBRE@ Oscuro, Plasma no cambia el fondo;
y si el fondo es un paquete con imagen clara y oscura, elige por los colores del estilo de Plasma, que no siempre son
los de la variante. Este programa mira el esquema de color (`[General] ColorScheme` de kdeglobals) y pone en
cada escritorio, del mismo paquete de fondo de @NOMBRE@ que ya tenga (`@DOMINIO@.*`), la imagen de la variante:
`contents/images/` en el claro y `contents/images_dark/` en el oscuro. Si el esquema o el fondo no son de @NOMBRE@,
no toca nada.

Konsole tampoco sigue a la variante: si el perfil por defecto (`konsolerc` → DefaultProfile) usa un esquema de
@NOMBRE@, se le pone el de la variante (ventanas nuevas) y se cambia en las sesiones abiertas con ese esquema, con la
secuencia de Konsole `ESC ] 50 ; ColorScheme=… BEL` escrita en su terminal (la de `konsoleprofile`); un perfil con
otro esquema no se toca.

GTK 3 no tiene consultas de medios: si `~/.config/gtk-3.0/gtk.css` importa la hoja de una variante de @NOMBRE@
(`@ID@-claro.css` o `@ID@-oscuro.css`, complemento gtk), se cambia esa línea por la de la otra (aplicaciones nuevas;
kde-gtk-config ya reescribió `colors.css`), y la preferencia `color-scheme` de GSettings pasa a `prefer-light` o
`prefer-dark`. Sin esa línea, GTK no se toca. GTK 4 y libadwaita cambian solos (`prefers-color-scheme`). Y si
kde-gtk-config dejó en GTK el tema de iconos o el claro u oscuro del tema anterior, se recarga su módulo de kded; y
`gtk-theme` de GSettings pasa a `Breeze-Dark` o `Breeze` (gretl elige por ese nombre sus iconos del modo oscuro).

Los programas que no cambian solos de variante (RStudio, Octave, Spyder) instalan cada uno el suyo en
`variante.d/`, junto a este: en cada cambio se ejecuta `variante.d/<programa>.py <variante> --aplicar` (sin
`--aplicar` al simular), y cada uno decide si le toca (decisiones 5.43).

Uso:  seguir-variante.py              # simula: dice qué cambiaría
      seguir-variante.py --aplicar    # lo cambia una vez
      seguir-variante.py --vigilar    # lo cambia ahora y cada vez que KDE avisa de un cambio de colores (sesión)
Solo biblioteca estándar; usa kreadconfig6, qdbus6 y dbus-monitor.
"""
from __future__ import annotations

import os
import re
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

DOMINIO = "@DOMINIO@"
VARIANTES = {"@ESQUEMA_CLARO@": "claro", "@ESQUEMA_OSCURO@": "oscuro"}
CARPETA = {"claro": "images", "oscuro": "images_dark"}
KONSOLE = {"claro": "@KONSOLE_CLARO@", "oscuro": "@KONSOLE_OSCURO@"}
HOJA_GTK3 = re.compile(r"^(\s*@import\s+(?:url\()?['\"])@ID@-(claro|oscuro)(\.css['\"]\)?;\s*)$", re.M)
ESQUEMA_GTK = {"claro": "prefer-light", "oscuro": "prefer-dark"}
DATA = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
LEER = """var d = desktops(); var r = [];
for (var i = 0; i < d.length; i++) { d[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
  r.push(i + "\\t" + d[i].wallpaperPlugin + "\\t" + d[i].readConfig("Image")); }
print(r.join("\\n"));"""


def herramienta(nombre: str) -> str | None:
    return shutil.which(nombre, path="/usr/bin:/usr/local/bin:/bin") or shutil.which(nombre)


def variante() -> str | None:
    r = subprocess.run([herramienta("kreadconfig6") or "kreadconfig6", "--file", "kdeglobals", "--group", "General",
                        "--key", "ColorScheme"], capture_output=True, text=True)
    return VARIANTES.get(r.stdout.strip())


def guion(js: str) -> str:
    r = subprocess.run([herramienta("qdbus6") or "qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                        "org.kde.PlasmaShell.evaluateScript", js], capture_output=True, text=True, timeout=20)
    return r.stdout


def imagen_para(url: str, var: str) -> str | None:
    """La imagen de la variante del mismo paquete de fondo de Lliphi, o None si el fondo no es de Lliphi."""
    ruta = Path(unquote(urlparse(url).path)) if url.startswith("file:") else Path(url)
    try:
        rel = ruta.relative_to(DATA / "wallpapers")
    except ValueError:
        return None
    paquete = rel.parts[0] if rel.parts else ""
    if not paquete.startswith(DOMINIO + "."):
        return None
    carpeta = DATA / "wallpapers" / paquete / "contents" / CARPETA[var]
    if not carpeta.is_dir():
        return None
    candidatas = sorted((p for p in carpeta.iterdir() if re.fullmatch(r"\d+x\d+\.(png|jpe?g)", p.name)),
                        key=lambda p: int(p.stem.split("x")[0]) * int(p.stem.split("x")[1]))
    if not candidatas:
        return None
    misma = carpeta / ruta.name
    elegida = misma if misma in candidatas else candidatas[-1]   # el mismo tamaño si lo hay; si no, el mayor
    return elegida.as_uri()


def cambios() -> list[tuple[int, str, str]]:
    var = variante()
    if var is None:
        return []
    salida = []
    for linea in guion(LEER).splitlines():
        partes = linea.split("\t")
        if len(partes) != 3 or partes[1] != "org.kde.image":
            continue
        nueva = imagen_para(partes[2], var)
        if nueva and nueva != partes[2]:
            salida.append((int(partes[0]), partes[2], nueva))
    return salida


def aplicar(lista: list[tuple[int, str, str]]) -> None:
    js = "var d = desktops();\n" + "".join(
        f'd[{i}].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"]; d[{i}].writeConfig("Image", "{nueva}");\n'
        for i, _vieja, nueva in lista)
    guion(js)


def perfil_konsole() -> Path | None:
    """El perfil por defecto de Konsole, si es un archivo del usuario."""
    rc = CONFIG / "konsolerc"
    if not rc.exists():
        return None
    m = re.search(r"^DefaultProfile=(.+)$", rc.read_text(encoding="utf-8", errors="ignore"), re.M)
    perfil = DATA / "konsole" / m.group(1).strip() if m else None
    return perfil if perfil and perfil.exists() else None


def esquema_del_perfil(perfil: Path) -> str | None:
    grupo = None
    for linea in perfil.read_text(encoding="utf-8", errors="ignore").splitlines():
        if linea.startswith("["):
            grupo = linea.strip()
        elif grupo == "[Appearance]" and linea.startswith("ColorScheme="):
            return linea.split("=", 1)[1].strip()
    return None


def fijar_esquema(perfil: Path, esquema: str) -> None:
    """Cambia solo `ColorScheme=` de [Appearance]; en el archivo real, para no romper un enlace de dotfiles."""
    real, grupo, salida = perfil.resolve(), None, []
    for linea in real.read_text(encoding="utf-8").splitlines():
        if linea.startswith("["):
            grupo = linea.strip()
        elif grupo == "[Appearance]" and linea.startswith("ColorScheme="):
            linea = f"ColorScheme={esquema}"
        salida.append(linea)
    real.write_text("\n".join(salida) + "\n", encoding="utf-8")


def terminales_abiertas() -> list[str]:
    """Las terminales (/dev/pts/N) de las sesiones de Konsole abiertas, por su proceso."""
    qdbus = herramienta("qdbus6")
    if not qdbus:
        return []
    salida = []
    servicios = subprocess.run([qdbus], capture_output=True, text=True, timeout=10).stdout.split()
    for servicio in (s for s in servicios if s.startswith("org.kde.konsole-")):
        rutas = subprocess.run([qdbus, servicio], capture_output=True, text=True, timeout=10).stdout.split()
        for ruta in (r for r in rutas if re.fullmatch(r"/Sessions/\d+", r)):
            pid = subprocess.run([qdbus, servicio, ruta, "org.kde.konsole.Session.processId"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
            try:
                tty = os.readlink(f"/proc/{int(pid)}/fd/0")
            except (ValueError, OSError):
                continue
            if tty.startswith("/dev/pts/") and tty not in salida:
                salida.append(tty)
    return salida


def konsole(var: str, escribir: bool) -> None:
    perfil = perfil_konsole()
    actual = esquema_del_perfil(perfil) if perfil else None
    if actual not in KONSOLE.values():
        return                                       # sin perfil propio, o con un esquema que no es de Lliphi
    if actual == KONSOLE[var]:
        return
    print(f"{'' if escribir else 'SIM '}Konsole: {perfil.name} {actual} → {KONSOLE[var]}")
    if not escribir:
        return
    fijar_esquema(perfil, KONSOLE[var])
    for tty in terminales_abiertas():
        try:
            with open(tty, "w", encoding="utf-8") as t:
                t.write(f"\033]50;ColorScheme={KONSOLE[var]}\007")
        except OSError:
            pass


def gtk(var: str, escribir: bool) -> None:
    """GTK 3: la línea `@import '@ID@-<variante>.css';` de gtk.css, si existe; y `color-scheme` de GSettings."""
    css = CONFIG / "gtk-3.0" / "gtk.css"
    texto = css.read_text(encoding="utf-8", errors="ignore") if css.exists() else ""
    m = HOJA_GTK3.search(texto)
    if not m:
        return                                       # GTK de @NOMBRE@ no aplicado: no se toca
    if m.group(2) != var:
        print(f"{'' if escribir else 'SIM '}GTK 3: gtk.css importa @ID@-{m.group(2)}.css → @ID@-{var}.css")
        if escribir:
            css.resolve().write_text(HOJA_GTK3.sub(lambda x: f"{x.group(1)}@ID@-{var}{x.group(3)}", texto, count=1), encoding="utf-8")
    gsettings = herramienta("gsettings")
    if not gsettings:
        return
    actual = subprocess.run([gsettings, "get", "org.gnome.desktop.interface", "color-scheme"],
                            capture_output=True, text=True).stdout.strip().strip("'")
    if actual != ESQUEMA_GTK[var]:
        print(f"{'' if escribir else 'SIM '}GTK: color-scheme {actual} → {ESQUEMA_GTK[var]}")
        if escribir:
            subprocess.run([gsettings, "set", "org.gnome.desktop.interface", "color-scheme", ESQUEMA_GTK[var]], capture_output=True)


def ini_gtk(ruta: Path) -> dict[str, str]:
    texto = ruta.read_text(encoding="utf-8", errors="ignore") if ruta.exists() else ""
    return {k.strip(): v.strip() for k, v in re.findall(r"^\s*([\w-]+)\s*=\s*(.*?)\s*$", texto, re.M)}


def desfase_gtk(var: str) -> list[str]:
    """Lo que GTK (`gtk-3.0/settings.ini`, que escribe kde-gtk-config) tiene distinto de KDE: el tema de iconos y el
    claro u oscuro. Vacío si coinciden o si KDE no gestiona GTK (no hay settings.ini)."""
    ini = CONFIG / "gtk-3.0" / "settings.ini"
    if not ini.exists():
        return []
    gtk = ini_gtk(ini)
    r = subprocess.run([herramienta("kreadconfig6") or "kreadconfig6", "--file", "kdeglobals", "--group", "Icons",
                        "--key", "Theme"], capture_output=True, text=True)
    esperado = {"gtk-application-prefer-dark-theme": "true" if var == "oscuro" else "false"}
    if r.stdout.strip():
        esperado["gtk-icon-theme-name"] = r.stdout.strip()
    return [f"{k} {gtk.get(k, '—')} → {v}" for k, v in esperado.items() if gtk.get(k) != v]


def gtk_kde(var: str, escribir: bool) -> None:
    """kde-gtk-config (el módulo `gtkconfig` de kded) copia a GTK 3/4 y a xsettingsd el tema de iconos y el claro u
    oscuro de KDE. Al cambiar de tema global a veces escribe los del tema anterior (visto el 2026-11-01: con
    @NOMBRE@ Claro, los iconos oscuros y `prefer-dark-theme`, y gretl con iconos claros sobre fondo claro). Si no
    coinciden, se espera por si aún está escribiendo y, si siguen sin coincidir, se recarga el módulo: al cargarse
    vuelve a escribirlo todo desde la configuración de KDE (decisiones 5.45)."""
    desfase = desfase_gtk(var)
    for _ in range(3 if escribir else 0):
        if not desfase:
            return
        time.sleep(1.0)
        desfase = desfase_gtk(var)
    if not desfase:
        return
    qdbus = herramienta("qdbus6")
    cargados = subprocess.run([qdbus or "qdbus6", "org.kde.kded6", "/kded", "org.kde.kded6.loadedModules"],
                              capture_output=True, text=True).stdout.split() if qdbus else []
    if "gtkconfig" not in cargados:
        return                                       # sin kde-gtk-config en marcha: GTK no es cosa de KDE
    print(f"{'' if escribir else 'SIM '}GTK: {'; '.join(desfase)} (se recarga gtkconfig)")
    if escribir:
        for orden in ("unloadModule", "loadModule"):
            subprocess.run([qdbus, "org.kde.kded6", "/kded", f"org.kde.kded6.{orden}", "gtkconfig"], capture_output=True)


TEMA_GTK = {"claro": "Breeze", "oscuro": "Breeze-Dark"}


def tema_gtk(var: str, escribir: bool) -> None:
    """El nombre del tema GTK en GSettings (`gtk-theme`). kde-gtk-config da el oscuro (`Breeze-Dark`) solo a las
    aplicaciones X11, por xsettingsd, y en GSettings deja `Breeze`; las que deciden su modo oscuro por ese nombre
    (gretl busca «dark» en él para sus iconos `_dk` y sus colores) no se enteraban. Se pone el de la variante si es uno
    de los dos de Breeze y el oscuro está instalado; otro tema no se toca (decisiones 5.45)."""
    gsettings = herramienta("gsettings")
    if not gsettings:
        return
    actual = subprocess.run([gsettings, "get", "org.gnome.desktop.interface", "gtk-theme"],
                            capture_output=True, text=True).stdout.strip().strip("'")
    temas = [Path(p) / "themes" for p in (str(DATA), *os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"))]
    if actual not in TEMA_GTK.values() or actual == TEMA_GTK[var] or not any((t / TEMA_GTK[var]).is_dir() for t in temas):
        return
    print(f"{'' if escribir else 'SIM '}GTK: gtk-theme {actual} → {TEMA_GTK[var]}")
    if escribir:
        subprocess.run([gsettings, "set", "org.gnome.desktop.interface", "gtk-theme", TEMA_GTK[var]], capture_output=True)


def una_vez(escribir: bool) -> None:
    lista = cambios()
    for i, vieja, nueva in lista:
        print(f"{'escritorio' if escribir else 'SIM escritorio'} {i}: {Path(urlparse(vieja).path).name} → {nueva}")
    if escribir and lista:
        aplicar(lista)
    if not lista:
        print("nada que cambiar en el fondo (ya es el de la variante, o no es de Lliphi)")
    var = variante()
    if var:
        konsole(var, escribir)
        gtk(var, escribir)
        gtk_kde(var, escribir)
        tema_gtk(var, escribir)                      # después: recargar gtkconfig vuelve a escribir `Breeze`
        programas(var, escribir)


def programas(var: str, escribir: bool) -> None:
    """Los programas de `variante.d/` (decisiones 5.43): cada uno cambia el suyo, si es de @NOMBRE@."""
    carpeta = Path(__file__).resolve().parent / "variante.d"
    for programa in sorted(carpeta.glob("*.py")) if carpeta.is_dir() else []:
        try:
            r = subprocess.run([sys.executable, str(programa), var, *(["--aplicar"] if escribir else [])],
                               capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as e:
            print(f"{programa.name}: {e}", file=sys.stderr)
            continue
        for linea in (r.stdout + r.stderr).splitlines():
            print(linea)


def vigilar() -> int:
    una_vez(True)
    monitor = herramienta("dbus-monitor")
    if not monitor:
        print("falta dbus-monitor", file=sys.stderr)
        return 2
    proc = subprocess.Popen([monitor, "--session", "type='signal',interface='org.kde.KGlobalSettings',member='notifyChange'"],
                            stdout=subprocess.PIPE, text=True)
    pendiente = 0.0
    while proc.poll() is None:
        listo, _, _ = select.select([proc.stdout], [], [], 1.0)
        if listo:
            if "notifyChange" in proc.stdout.readline():
                pendiente = time.monotonic() + 1.5   # el cambio de tema avisa varias veces: se espera a que acabe
        elif pendiente and time.monotonic() >= pendiente:
            pendiente = 0.0
            try:
                una_vez(True)
            except (OSError, subprocess.SubprocessError) as e:
                print(f"no se pudo cambiar el fondo: {e}", file=sys.stderr)
    return proc.returncode or 0


if __name__ == "__main__":
    if "--vigilar" in sys.argv:
        sys.exit(vigilar())
    una_vez("--aplicar" in sys.argv)
