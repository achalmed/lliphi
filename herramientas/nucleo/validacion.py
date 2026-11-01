"""Validación: que cada módulo esté bien declarado, que sus dependencias existan y no formen ciclos, que lo generado
tenga la estructura real del formato de KDE que dice ser y que el tema global solo nombre componentes que existen.

Los formatos se comprobaron contra Plasma 6.6.6 (docs/migracion-modular.md §1.1): `Plasma/LookAndFeel` y `KWin/Aurorae`
llevan `KPackageStructure`; `Plasma/Theme` lleva `X-Plasma-API` y no lo lleva; `Wallpaper/Images` es un `metadata.json`
con `KPlugin.Id` y `contents/images*/`; KColorScheme es un `.colors` suelto. Solo biblioteca estándar."""
from __future__ import annotations

import configparser
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from . import RAIZ, VERSION, cargar, registro

CLAVES = ("nombre", "resumen", "clase", "formato", "tecnologia", "estado", "desde", "archivos", "dependencias", "instalacion")
DEPENDENCIAS = ("construccion", "integra", "referencia", "herramientas", "herramientas_opcionales", "python", "terceros", "bases")
BASES = ("data", "config", "vscode", "positron", "vscodium")
ESTADOS = ("probado", "experimental", "implementado", "pendiente")
GRUPOS_COLORES = ("Colors:View", "Colors:Window", "Colors:Button", "Colors:Selection", "Colors:Tooltip",
                  "Colors:Complementary", "Colors:Header")


class Informe:
    def __init__(self) -> None:
        self.errores: list[str] = []
        self.avisos: list[str] = []

    def error(self, id_: str, texto: str) -> None:
        self.errores.append(f"{id_}: {texto}")

    def aviso(self, id_: str, texto: str) -> None:
        self.avisos.append(f"{id_}: {texto}")

    def exigir(self, cond: bool, id_: str, texto: str) -> bool:
        if not cond:
            self.error(id_, texto)
        return cond


def _rel(ruta: Path) -> str:
    """La ruta relativa al proyecto para los mensajes (o entera, si está fuera: p. ej., una copia en las pruebas)."""
    return str(ruta.relative_to(RAIZ)) if ruta.is_relative_to(RAIZ) else str(ruta)


def _ini(ruta: Path) -> configparser.ConfigParser:
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    cp.optionxform = str  # type: ignore[assignment]
    cp.read(ruta, encoding="utf-8")
    return cp


def _json(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def defaults(ruta: Path) -> dict[str, dict[str, str]]:
    """`contents/defaults` → {'kdeglobals][General': {...}, 'KSplash': {...}} (la sintaxis `[archivo][grupo]`)."""
    grupos: dict[str, dict[str, str]] = {}
    actual = None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("#") or not linea.strip():
            continue
        if linea.startswith("[") and linea.endswith("]"):
            actual = grupos.setdefault(linea[1:-1], {})
        elif actual is not None and "=" in linea:
            k, v = linea.split("=", 1)
            actual[k] = v
    return grupos


# ---------------------------------------------------------------- manifiestos y dependencias

def manifiestos(inf: Informe, marca: dict) -> None:
    ids = set(registro.ids())
    for m in registro.todos():
        d = m.datos
        for clave in CLAVES:
            inf.exigir(clave in d, m.id, f"falta «{clave}» en modulo.json")
        inf.exigir(re.fullmatch(r"[a-z][a-z0-9-]*", m.id) is not None, m.id, "el id (nombre de la carpeta) debe ser minúsculas ASCII con guiones")
        inf.exigir(d.get("clase") in registro.CLASES, m.id, f"clase desconocida: {d.get('clase')}")
        inf.exigir(d.get("estado") in ESTADOS, m.id, f"estado desconocido: {d.get('estado')}")
        for nombre in ("README.md", "INSTALL.md"):
            inf.exigir((m.carpeta / nombre).is_file(), m.id, f"falta {nombre}")
        deps = d.get("dependencias", {})
        for tipo in deps:
            inf.exigir(tipo in DEPENDENCIAS, m.id, f"tipo de dependencia desconocido: {tipo}")
        for tipo in ("construccion", "integra", "referencia"):
            for otro in deps.get(tipo, []):
                inf.exigir(otro in ids, m.id, f"{tipo}: no existe el módulo «{otro}»")
                inf.exigir(otro != m.id, m.id, f"{tipo}: un módulo no depende de sí mismo")
        for base in deps.get("bases", []):
            inf.exigir((RAIZ / base).is_dir(), m.id, f"no existe la base de terceros {base}")
        for c in d.get("capturas", []):
            nombre = Path(c).name
            inf.exigir((RAIZ / "muestras" / "capturas" / nombre).exists() or (RAIZ / "muestras" / nombre).exists(), m.id, f"no existe la captura {nombre}")
        # código de cada clase
        if m.clase == "paquete":
            inf.exigir(m.tiene("construir.py") and hasattr(registro.codigo(m.id), "generar"), m.id, "un paquete necesita construir.py con generar()")
        if m.clase == "componente":
            inf.exigir(m.tiene("construir.py") and hasattr(registro.codigo(m.id), "integrar"), m.id, "un componente necesita construir.py con integrar()")
            en = d.get("integracion", {}).get("en")
            if inf.exigir(en in ids, m.id, "un componente declara en «integracion.en» el paquete que lo integra"):
                inf.exigir(m.id in registro.modulo(en).dependencias("integra"), m.id, f"{en} no lo declara en «integra»: no se construiría")
        if m.clase == "externo":
            inf.exigir(m.tiene("externas.py"), m.id, "un módulo externo necesita externas.py (cómo se instalan sus terceros)")
        for otro in deps.get("integra", []):
            if otro in ids:
                inf.exigir(registro.modulo(otro).clase == "componente", m.id, f"integra «{otro}», que no es un componente")
        # el código solo usa otros módulos que declara
        for archivo in ("construir.py", "aplicar.py", "externas.py"):
            if m.tiene(archivo):
                usados = set(re.findall(r'registro\.codigo\("([a-z-]+)"', m.archivo(archivo).read_text(encoding="utf-8")))
                declarados = set(deps.get("construccion", [])) | set(deps.get("integra", [])) | {m.id}
                for u in sorted(usados - declarados):
                    inf.error(m.id, f"{archivo} usa el código de «{u}» sin declararlo en dependencias.construccion")
        # instalación
        for par in d.get("instalacion", []):
            inf.exigir(par.get("base", "data") in BASES, m.id, f"base de instalación desconocida: {par.get('base')}")
            origen = m.generado / par["origen"].format(**marca)
            inf.exigir(origen.exists(), m.id, f"se instala {_rel(origen)}, que no existe (¿falta generar.py --aplicar?)")
        if m.clase != "paquete":
            inf.exigir(not d.get("instalacion"), m.id, "solo un paquete instala archivos propios")
    try:
        registro.orden_de_construccion(registro.ids())
    except ValueError as e:
        inf.error("registro", str(e))


# ---------------------------------------------------------------- estructura real de lo generado

def _metadata(inf: Informe, id_: str, carpeta: Path, estructura: str | None) -> dict:
    ruta = carpeta / "metadata.json"
    if not inf.exigir(ruta.exists(), id_, f"{carpeta.name}: falta metadata.json"):
        return {}
    meta = _json(ruta)
    plugin = meta.get("KPlugin", {})
    inf.exigir(plugin.get("Id") == carpeta.name, id_, f"{carpeta.name}: KPlugin.Id ({plugin.get('Id')}) ≠ nombre de la carpeta")
    if estructura:
        inf.exigir(meta.get("KPackageStructure") == estructura, id_, f"{carpeta.name}: KPackageStructure ≠ {estructura}")
    if "Version" in plugin:
        inf.exigir(plugin["Version"] == VERSION, id_, f"{carpeta.name}: Version {plugin['Version']} ≠ VERSION {VERSION}")
    return meta


def _svgs(inf: Informe, id_: str, carpeta: Path) -> None:
    for svg in carpeta.rglob("*.svg"):
        try:
            ET.parse(svg)
        except ET.ParseError as e:
            inf.error(id_, f"SVG mal formado {_rel(svg)}: {e}")


def estructura(inf: Informe, m: registro.Modulo, marca: dict) -> None:
    if m.clase != "paquete":
        return
    g = m.generado
    if not inf.exigir(g.is_dir(), m.id, f"falta {_rel(g)} (generar.py --aplicar)"):
        return
    for a in m.datos.get("archivos", []):
        inf.exigir((g / a.rstrip("/")).exists(), m.id, f"el manifiesto anuncia «{a}», que no está en generado/{m.id}")
    formato = m.datos["formato"]
    hijos = sorted(p for p in g.iterdir())
    if formato == "Plasma/LookAndFeel":
        for p in hijos:
            _metadata(inf, m.id, p, "Plasma/LookAndFeel")
            inf.exigir((p / "contents" / "defaults").is_file(), m.id, f"{p.name}: falta contents/defaults")
            inf.exigir((p / "contents" / "previews" / "preview.png").is_file(), m.id, f"{p.name}: falta la vista previa")
    elif formato == "KColorScheme":
        for p in hijos:
            cp = _ini(p)
            for grupo in GRUPOS_COLORES:
                inf.exigir(grupo in cp, m.id, f"{p.name}: falta [{grupo}]")
            inf.exigir(cp.get("General", "ColorScheme", fallback=None) == p.stem, m.id, f"{p.name}: [General] ColorScheme ≠ nombre del archivo")
    elif formato == "Plasma/Theme":
        for p in hijos:
            meta = _metadata(inf, m.id, p, None)
            inf.exigir("X-Plasma-API" in meta, m.id, f"{p.name}: un estilo de Plasma declara X-Plasma-API")
            inf.exigir((p / "plasmarc").is_file(), m.id, f"{p.name}: falta plasmarc")
            for req in ("widgets/panel-background.svg", "dialogs/background.svg"):
                inf.exigir((p / req).is_file(), m.id, f"{p.name}: falta {req}")
            _svgs(inf, m.id, p)
    elif formato == "KWin/Aurorae":
        for p in hijos:
            _metadata(inf, m.id, p, "KWin/Aurorae")
            for req in ("decoration.svg", f"{p.name}rc", "close.svg"):
                inf.exigir((p / req).is_file(), m.id, f"{p.name}: falta {req}")
            _svgs(inf, m.id, p)
    elif formato == "Wallpaper/Images":
        for p in hijos:
            _metadata(inf, m.id, p, None)
            for sub in ("images", "images_dark"):
                inf.exigir(any((p / "contents" / sub).glob("*.png")), m.id, f"{p.name}: contents/{sub}/ sin imágenes")
    elif formato == "Kvantum":
        for p in hijos:   # el tema y su variante oscura (<tema>Dark), que Kvantum elige con el estilo kvantum-dark
            for nombre in (p.name, f"{p.name}Dark"):
                for ext in ("kvconfig", "svg"):
                    inf.exigir((p / f"{nombre}.{ext}").is_file(), m.id, f"{p.name}: falta {nombre}.{ext}")
            _svgs(inf, m.id, p)
    elif formato == "Konsole":
        for p in hijos:
            inf.exigir(_ini(p).get("General", "Description", fallback=None) is not None, m.id, f"{p.name}: falta [General] Description")
    elif formato == "SDDM":
        for p in hijos:
            meta = _ini(p / "metadata.desktop")
            if inf.exigir("SddmGreeterTheme" in meta, m.id, f"{p.name}: metadata.desktop sin [SddmGreeterTheme]"):
                s = meta["SddmGreeterTheme"]
                inf.exigir((p / s.get("MainScript", "")).is_file(), m.id, f"{p.name}: falta MainScript")
                inf.exigir(s.get("Theme-Id") == p.name, m.id, f"{p.name}: Theme-Id ≠ nombre de la carpeta")
    else:   # varios: al menos que JSON y TOML se lean
        import tomllib   # Python ≥ 3.11; el resto del núcleo funciona con 3.10
        for p in g.rglob("*.json"):
            try:
                _json(p)
            except ValueError as e:
                inf.error(m.id, f"JSON ilegible {_rel(p)}: {e}")
        for p in g.rglob("*.toml"):
            try:
                tomllib.loads(p.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as e:
                inf.error(m.id, f"TOML ilegible {_rel(p)}: {e}")


# ---------------------------------------------------------------- integración en el tema global

def integracion(inf: Informe, marca: dict) -> None:
    """Cada identificador que declara el tema global existe en el módulo que lo entrega, y cada componente integrado
    dejó sus archivos dentro del paquete. Es la comprobación de «componentes faltantes o incompatibles»."""
    global_ = registro.modulo("global")
    iconos = registro.codigo("iconos-cursores")
    for v in ("claro", "oscuro"):
        paquete = global_.generado / marca["id_global"][v]
        ruta = paquete / "contents" / "defaults"
        if not ruta.exists():
            continue
        d = defaults(ruta)
        def valor(grupo: str, clave: str) -> str | None:
            return d.get(grupo, {}).get(clave)
        cs = valor("kdeglobals][General", "ColorScheme")
        inf.exigir(cs is not None and (registro.modulo("esquema").generado / f"{cs}.colors").exists(), "global", f"{v}: ColorScheme={cs} no lo entrega el módulo esquema")
        estilo = valor("plasmarc][Theme", "name")
        inf.exigir(estilo is not None and (registro.modulo("estilo").generado / estilo / "metadata.json").exists(), "global", f"{v}: [plasmarc][Theme] name={estilo} no lo entrega el módulo estilo")
        deco = valor("kwinrc][org.kde.kdecoration2", "theme") or ""
        inf.exigir(deco.startswith("__aurorae__svg__") and (registro.modulo("decoracion").generado / deco.removeprefix("__aurorae__svg__") / "decoration.svg").exists(),
                   "global", f"{v}: decoración {deco} no la entrega el módulo decoracion")
        inf.exigir(valor("kwinrc][org.kde.kdecoration2", "library") == "org.kde.kwin.aurorae.v2", "global", f"{v}: la decoración SVG pide library=org.kde.kwin.aurorae.v2 en Plasma 6.6")
        fondo = valor("Wallpaper", "Image")
        inf.exigir(fondo is not None and (registro.modulo("fondos").generado / fondo / "metadata.json").exists(), "global", f"{v}: fondo {fondo} no lo entrega el complemento fondos")
        estilo_apps = valor("kdeglobals][KDE", "widgetStyle") or ""
        if estilo_apps.startswith("kvantum"):
            tema_kv = registro.codigo("kvantum").tema_de(marca) + ("Dark" if estilo_apps == "kvantum-dark" else "")
            inf.exigir((registro.modulo("kvantum").generado / registro.codigo("kvantum").tema_de(marca) / f"{tema_kv}.kvconfig").is_file(),
                       "global", f"{v}: widgetStyle={estilo_apps} sin el tema de Kvantum {tema_kv}")
        inf.exigir(valor("kdeglobals][Icons", "Theme") == iconos.ICONOS[v], "global", f"{v}: el tema de iconos no es el del módulo iconos-cursores")
        inf.exigir(valor("kcminputrc][Mouse", "cursorTheme") == iconos.CURSORES, "global", f"{v}: el tema de cursores no es el del módulo iconos-cursores")
        splash = valor("KSplash", "Theme")
        if splash == marca["id_global"][v]:
            inf.exigir((paquete / "contents" / "splash" / "Splash.qml").is_file(), "global", f"{v}: [KSplash] Theme apunta al propio paquete y no trae contents/splash/Splash.qml")
        for id_ in global_.dependencias("integra"):
            for rel in registro.modulo(id_).datos.get("integracion", {}).get("rutas", []):
                inf.exigir((paquete / rel).is_file(), id_, f"{v}: no está integrado {rel} en {_rel(paquete)}")
        lockscreen = paquete / "contents" / "lockscreen"
        if lockscreen.exists():
            inf.aviso("global", f"{v}: contents/lockscreen/ se ignora en Plasma 6.6 (el bloqueo es del paquete de shell)")


def validar() -> Informe:
    inf = Informe()
    _, marca = cargar()
    manifiestos(inf, marca)
    for m in registro.todos():
        estructura(inf, m, marca)
    integracion(inf, marca)
    return inf


def informe(como_json: bool = False) -> int:
    inf = validar()
    if como_json:   # forma de máquina (Lliphi Studio): cada error y aviso con su módulo
        def partir(x: str) -> dict:
            id_, _, texto = x.partition(": ")
            return {"modulo": id_, "texto": texto}
        print(json.dumps({"modulos": len(registro.todos()), "valido": not inf.errores,
                          "errores": [partir(x) for x in inf.errores], "avisos": [partir(x) for x in inf.avisos]},
                         ensure_ascii=False))
        return 0 if not inf.errores else 1
    for x in inf.avisos:
        print(f"  aviso  {x}")
    for x in inf.errores:
        print(f"  ERROR  {x}")
    n = len(registro.todos())
    print(f"[validar] {n} módulos · {len(inf.errores)} error(es) · {len(inf.avisos)} aviso(s) · {'válido' if not inf.errores else 'NO VÁLIDO'}")
    return 0 if not inf.errores else 1
