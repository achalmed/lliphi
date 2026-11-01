"""El proyecto Lliphi visto desde el studio, sin Qt: rutas, módulos, ajustes, versiones, git y las órdenes.

La ventana es un cliente: lee los `modulo.json`, `tokens/`, `generado/` y el manifiesto de instalación; escribe solo
los `ajustes.json` de los módulos (fuente, nunca `generado/`); todo lo demás lo hacen las órdenes de Lliphi. La raíz
del proyecto es la carpeta que contiene `studio/`, o la de `LLIPHI_DIR` (las pruebas la apuntan a una copia).
"""
from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RAICES = (("global", "global"), ("modulo", "modulos"), ("complemento", "complementos"))
# los seis módulos del encargo, con la sección del studio que los trabaja
SECCION = {"esquema": "color", "estilo": "plasma", "decoracion": "ventanas", "iconos-cursores": "iconos",
           "carga-bloqueo": "pantallas", "disposicion": "disposicion"}
EDITABLES = ("esquema", "decoracion", "disposicion", "iconos-cursores")   # los que tienen ajustes.json


def raiz() -> Path:
    return Path(os.environ.get("LLIPHI_DIR") or Path(__file__).resolve().parents[2])


def home() -> Path:
    return Path(os.environ.get("HOME") or Path.home())


def estado_studio() -> Path:
    """Borradores y preferencias del studio: `$XDG_STATE_HOME/lliphi-studio/`."""
    return Path(os.environ.get("XDG_STATE_HOME") or home() / ".local" / "state") / "lliphi-studio"


def python() -> str:
    """El Python de `.venv` (coloraide y Pillow, que piden la paleta y la construcción) o, si no hay, este."""
    venv = raiz() / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def orden(herramienta: str, *args: str) -> list[str]:
    """La línea de una orden de Lliphi: `generar`, `instalar`, `sesion` (herramientas/) o `paleta` (el esquema)."""
    ruta = {"paleta": raiz() / "modulos" / "esquema" / "paleta.py"}.get(herramienta, raiz() / "herramientas" / f"{herramienta}.py")
    return [python(), str(ruta), *args]


def correr_json(herramienta: str, *args: str, timeout: int = 120) -> dict | None:
    """Corre una orden con `--json` y devuelve lo que imprime (None si no se pudo)."""
    try:
        r = subprocess.run(orden(herramienta, *args, "--json"), cwd=raiz(), capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else None
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError, IndexError):
        return None


# ------------------------------------------------------------------ módulos

@dataclass
class Modulo:
    id: str
    rol: str
    carpeta: Path
    datos: dict = field(repr=False)

    @property
    def nombre(self) -> str:
        return self.datos.get("nombre", self.id)

    @property
    def clase(self) -> str:
        return self.datos.get("clase", "")

    @property
    def formato(self) -> str:
        return self.datos.get("formato", "")

    @property
    def orden(self) -> int:
        return int(self.datos.get("orden", 100))

    def dependencias(self, tipo: str) -> list[str]:
        return list(self.datos.get("dependencias", {}).get(tipo, []))

    @property
    def generado(self) -> Path:
        return raiz() / "generado" / self.id

    @property
    def ajustes(self) -> Path:
        return self.carpeta / "ajustes.json"

    def herramientas(self) -> dict[str, bool]:
        """Las órdenes del sistema que pide (obligatorias y opcionales) y si están."""
        return {h: shutil.which(h) is not None for h in self.dependencias("herramientas") + self.dependencias("herramientas_opcionales")}

    def ultima_construccion(self) -> float | None:
        """La fecha del archivo más reciente de lo generado de este módulo (o del tema global, si es componente)."""
        carpeta = raiz() / "generado" / (self.datos.get("integracion", {}).get("en") or self.id)
        tiempos = [p.stat().st_mtime for p in carpeta.rglob("*") if p.is_file()] if carpeta.exists() else []
        return max(tiempos) if tiempos else None


def modulos() -> list[Modulo]:
    salida = []
    for rol, carpeta in RAICES:
        base = raiz() / carpeta
        if (base / "modulo.json").exists():
            salida.append(Modulo("global", rol, base, json.loads((base / "modulo.json").read_text(encoding="utf-8"))))
            continue
        for d in sorted(base.iterdir()) if base.is_dir() else []:
            if (d / "modulo.json").exists():
                salida.append(Modulo(d.name, rol, d, json.loads((d / "modulo.json").read_text(encoding="utf-8"))))
    return sorted(salida, key=lambda m: (["global", "modulo", "complemento"].index(m.rol), m.orden, m.id))


def modulo(id_: str) -> Modulo:
    return next(m for m in modulos() if m.id == id_)


def aristas() -> list[tuple[str, str, str]]:
    """(de, a, tipo) para el grafo de dependencias: construcción, integra y referencia."""
    return [(m.id, d, t) for m in modulos() for t in ("construccion", "integra", "referencia") for d in m.dependencias(t)]


# ------------------------------------------------------------------ tokens, marca y ajustes

def marca() -> dict:
    return json.loads((raiz() / "tokens" / "marca.json").read_text(encoding="utf-8"))


def tokens() -> dict:
    return json.loads((raiz() / "tokens" / "tokens.json").read_text(encoding="utf-8"))


def version() -> str:
    v = raiz() / "VERSION"
    return v.read_text(encoding="utf-8").strip() if v.exists() else "?"


def leer_ajustes(id_: str) -> dict:
    return json.loads(modulo(id_).ajustes.read_text(encoding="utf-8"))


def volcar(id_: str, datos: dict) -> str:
    """El texto canónico de un ajustes.json: sangría de dos espacios; las ternas OKLCH de la paleta, en una línea
    (lo mismo que `paleta.volcar_ajustes()`); cada widget de la disposición, en una línea."""
    lineas: dict[str, str] = {}
    if id_ == "disposicion":
        datos = json.loads(json.dumps(datos))
        for p in datos.get("paneles", []):
            for i, w in enumerate(p.get("widgets", [])):
                marca_ = f"@@widget{len(lineas)}@@"
                lineas[f'"{marca_}"'] = json.dumps(w, ensure_ascii=False)
                p["widgets"][i] = marca_
    texto = json.dumps(datos, ensure_ascii=False, indent=2)
    for k, v in lineas.items():
        texto = texto.replace(k, v)
    if id_ == "esquema":
        texto = re.sub(r"\[\s*(-?[\d.]+(?:,\s*-?[\d.]+)*)\s*\]",
                       lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",")) + "]", texto)
    return texto + "\n"


def diff_ajustes(id_: str, datos: dict) -> str:
    """El diff entre el ajustes.json del proyecto y un borrador (vacío si son iguales)."""
    actual = modulo(id_).ajustes.read_text(encoding="utf-8")
    nuevo = volcar(id_, datos)
    return "".join(difflib.unified_diff(actual.splitlines(True), nuevo.splitlines(True),
                                        f"a/{modulo(id_).ajustes.relative_to(raiz())}", f"b/{modulo(id_).ajustes.relative_to(raiz())}"))


def guardar_ajustes(id_: str, datos: dict) -> Path:
    """Escribe el ajustes.json del módulo (la única escritura del studio en el proyecto), de forma atómica."""
    ruta = modulo(id_).ajustes
    tmp = ruta.with_suffix(".json.tmp")
    tmp.write_text(volcar(id_, datos), encoding="utf-8")
    tmp.replace(ruta)
    return ruta


def borrador(id_: str) -> Path:
    return estado_studio() / "borradores" / f"{id_}.json"


def leer_borrador(id_: str) -> dict:
    """El borrador del módulo, o sus ajustes si no hay (o si el borrador está roto)."""
    b = borrador(id_)
    if b.exists():
        try:
            return json.loads(b.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return leer_ajustes(id_)


def guardar_borrador(id_: str, datos: dict) -> Path:
    b = borrador(id_)
    b.parent.mkdir(parents=True, exist_ok=True)
    b.write_text(volcar(id_, datos), encoding="utf-8")
    return b


def descartar_borrador(id_: str) -> None:
    borrador(id_).unlink(missing_ok=True)


# ------------------------------------------------------------------ git, versiones y entorno

@dataclass
class Git:
    rama: str = "?"
    cambios: list[str] = field(default_factory=list)
    adelante: int = 0
    atras: int = 0
    etiqueta: str = ""


def git() -> Git:
    def g(*args: str) -> str:
        r = subprocess.run(["git", "-C", str(raiz()), *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    estado = g("status", "--porcelain=v1", "--branch")
    if not estado:
        return Git()
    lineas = estado.splitlines()
    cabeza = lineas[0][3:]
    rama = cabeza.split("...")[0]
    adelante = int(m.group(1)) if (m := re.search(r"ahead (\d+)", cabeza)) else 0
    atras = int(m.group(1)) if (m := re.search(r"behind (\d+)", cabeza)) else 0
    return Git(rama, [l[3:] for l in lineas[1:]], adelante, atras, g("describe", "--tags", "--abbrev=0", "--match", "v*"))


def version_de(programa: str, *args: str) -> str:
    if not shutil.which(programa):
        return "no está"
    try:
        r = subprocess.run([programa, *(args or ("--version",))], capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return "?"
    texto = (r.stdout or r.stderr).strip().splitlines()
    return re.sub(rf"^{re.escape(programa)}\s*", "", texto[0], flags=re.I) if texto else "?"


def versiones() -> dict[str, str]:
    """Lliphi, Plasma, KDE Frameworks y Qt del sistema (por la versión de sus bibliotecas), Papirus e Inkscape."""
    salida = {"Lliphi": version(), "Plasma": version_de("plasmashell")}
    for nombre, patron in (("KDE Frameworks", "libKF6CoreAddons.so.6.*"), ("Qt del sistema", "libQt6Core.so.6.*")):
        libs = sorted(p for d in (Path("/usr/lib/x86_64-linux-gnu"), Path("/usr/lib64"), Path("/usr/lib")) if d.is_dir()
                      for p in d.glob(patron))
        salida[nombre] = libs[-1].name.split(".so.")[1] if libs else "?"
    salida["Papirus"] = "instalado" if (data_home() / "icons" / "Papirus" / "index.theme").exists() else "no está"
    salida["Inkscape"] = version_de("inkscape").split(" (")[0]
    return salida


def data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or home() / ".local" / "share")


def state_lliphi() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or home() / ".local" / "state") / marca()["id"]


@dataclass
class Respaldo:
    carpeta: Path
    undo: Path
    archivos: int


def respaldos() -> list[Respaldo]:
    """Los respaldos del instalador (más reciente primero), cada uno con su UNDO.sh."""
    base = state_lliphi() / "respaldos"
    salida = []
    for d in sorted(base.iterdir(), reverse=True) if base.is_dir() else []:
        if (d / "UNDO.sh").exists():
            salida.append(Respaldo(d, d / "UNDO.sh", sum(1 for p in d.rglob("*") if p.is_file())))
    return salida


def docs() -> list[tuple[str, Path]]:
    """Los documentos que la ventana sabe mostrar (título, ruta)."""
    r = raiz()
    pares = [("README", r / "README.md"), ("Estado", r / "estado.md"), ("Arquitectura", r / "docs" / "arquitectura.md"),
             ("Validación", r / "docs" / "validacion.md"), ("Decisiones", r / "docs" / "decisiones.md"),
             ("Compatibilidad", r / "docs" / "compatibilidad.md"), ("Studio", r / "studio" / "README.md")]
    return [(t, p) for t, p in pares if p.exists()]
