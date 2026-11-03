"""studio/lliphi_app/servicios/areas.py — las áreas del centro de configuración y lo que cada página dice de sus destinos,
sin Qt (reingeniería 2026-11-02, `docs/reingenieria.md` §3.1).

Un área agrupa destinos (el tema global, módulos y complementos de `modulo.json`) bajo lo que el usuario reconoce en las
Preferencias del sistema: esquemas de color, Plasma, Kvantum, Konsole… Para cada destino la página enseña:

- su tarjeta (`tarjeta`): lo generado (al día, desfasado, sin comprobar) y su fecha, la instalación, la compatibilidad
  (el `estado` del `modulo.json`, «desde», las herramientas que faltan, las bases que no están);
- lo instalado frente a lo generado, archivo por archivo (`comparar`): cada par origen → destino del núcleo
  (`pares_de`) como **igual**, **distinto** (instalado por Lliphi y cambiado después), **ajeno** (ocupa la ruta y Lliphi
  no lo instaló: el instalador no lo toca), **falta** (no está en el escritorio) o **sin generar**;
- la diferencia de un par de texto (`diferencia`), en filas lado a lado.

Todo se lee del núcleo de Lliphi (`herramientas/nucleo/instalacion.py`), cargado por ruta: no hay una segunda copia.
"""
from __future__ import annotations

import difflib
import importlib
import json
import shutil
import subprocess
from pathlib import Path

from gui_comun import diferencias

from lliphi_app.servicios import destinos, proyecto

# id, título, icono, destinos (los complementos no nombrados van a «otros»), qué es
AREAS = (
    ("diseno", "Sistema de diseño", "color-management", (), "Los tokens, la única fuente: paleta OKLCH, contrastes y la vista previa"),
    ("esquemas", "Esquemas de color", "preferences-desktop-color", ("esquema",), "Lliphi Claro y Lliphi Oscuro para KDE (.colors)"),
    ("plasma", "Plasma", "preferences-desktop-plasma", ("global", "estilo", "decoracion", "disposicion", "carga-bloqueo", "sddm"),
     "El tema global, el estilo de Plasma, la decoración, la disposición, la pantalla de carga y el inicio de sesión"),
    ("kvantum", "Kvantum", "preferences-desktop-theme-applications", ("kvantum",), "El estilo de las aplicaciones Qt"),
    ("konsole", "Konsole y terminales", "utilities-terminal", ("konsole", "terminales"), "Konsole, Alacritty, Kitty y los 16 colores ANSI"),
    ("editores", "Editores", "accessories-text-editor", ("editores", "kate", "texstudio", "vim", "rstudio", "octave", "spyder"),
     "VS Code, Positron, Zed, Kate, TeXstudio, Vim, RStudio, Octave y Spyder"),
    ("fondos", "Fondos", "preferences-desktop-wallpaper", ("fondos", "fondo-variante"), "Los fondos del escritorio, claro y oscuro"),
    ("tipografia", "Tipografía", "preferences-desktop-font", (), "Las familias y el tamaño de los tokens, y si están instaladas"),
    ("iconos", "Iconos y cursores", "preferences-desktop-icons", ("iconos-cursores",), "Papirus y los cursores (de terceros) y las carpetas de Lliphi"),
    ("otros", "Otros destinos", "preferences-plugin", None, "Navegadores, LibreOffice, GTK, Obsidian, Telegram y los demás"),
)
TEXTO_PAR = {"igual": "igual a lo generado", "distinto": "cambiado después de instalar", "ajeno": "ajeno: Lliphi no lo instaló",
             "falta": "no está en el escritorio", "sin_generar": "falta en generado/"}
NIVEL_PAR = {"igual": "positivo", "distinto": "neutro", "ajeno": "negativo", "falta": "", "sin_generar": "negativo"}
NIVEL_COMPAT = {"probado": "positivo", "implementado": "positivo", "experimental": "neutro", "esperado": "neutro"}


def areas() -> list[dict]:
    ids = {m.id for m in proyecto.modulos()}
    nombrados = {d for a in AREAS if a[3] for d in a[3]}
    salida = []
    for id_, titulo, icono, lista, que in AREAS:
        miembros = sorted(ids - nombrados - {"global"}) if lista is None else [d for d in lista if d in ids]
        salida.append({"id": id_, "titulo": titulo, "icono": icono, "destinos": miembros, "que": que})
    return salida


def area(id_: str) -> dict:
    return next(a for a in areas() if a["id"] == id_)


def area_de(destino: str) -> str:
    return next((a["id"] for a in areas() if destino in a["destinos"]), "otros")


def instalacion_mod():
    return importlib.import_module(f"{destinos.nucleo().__name__}.instalacion")


def compatibilidad(m: proyecto.Modulo) -> dict:
    """Lo que dice el `modulo.json` (estado, desde, tecnología), las herramientas que faltan y las bases que no están."""
    faltan = [h for h, ok in m.herramientas().items() if not ok and h in m.dependencias("herramientas")]
    opcionales = [h for h, ok in m.herramientas().items() if not ok and h in m.dependencias("herramientas_opcionales")]
    _pares, omitidos = destinos.pares_instalacion(m.id) if m.clase == "paquete" else ([], [])
    estado = m.datos.get("estado", "")
    nivel = "negativo" if faltan else NIVEL_COMPAT.get(estado, "")
    return {"estado": estado, "desde": m.datos.get("desde", ""), "tecnologia": m.datos.get("tecnologia", ""), "faltan": faltan,
            "opcionales": opcionales, "omitidos": len(omitidos), "nivel": nivel,
            "texto": (estado or "—") + (f" · desde {m.datos['desde']}" if m.datos.get("desde") else "")
                     + (f" · falta {', '.join(faltan)}" if faltan else "")}


def tarjeta(m: proyecto.Modulo, verificacion: destinos.Verificacion, instalacion: dict) -> dict:
    f = destinos.fila(m, verificacion, instalacion)
    return {**f, "nombre": m.nombre, "resumenCorto": m.datos.get("resumen", ""), "compatibilidad": compatibilidad(m),
            "instalable": m.clase == "paquete" and bool(m.datos.get("instalacion")) and m.id not in destinos.PRIVILEGIADOS,
            "privilegiado": m.id in destinos.PRIVILEGIADOS, "generable": m.clase in ("paquete", "componente") or m.id == "global"}


def _sha(p: Path) -> str:
    return instalacion_mod().sha_dir(p)


def comparar(id_: str) -> list[dict]:
    """Cada par origen → destino del destino `id_` con su estado (igual · distinto · ajeno · falta · sin_generar)."""
    ins = instalacion_mod()
    pares, _omitidos = ins.pares_de([id_])
    manifiesto = {}
    try:
        manifiesto = json.loads(ins.MANIFIESTO.read_text(encoding="utf-8")).get("rutas", {}) if ins.MANIFIESTO.exists() else {}
    except (OSError, ValueError):
        pass
    nuestras = {ins._norm(r) for r in manifiesto}
    salida = []
    for origen, destino in pares:
        if not origen.exists():
            estado = "sin_generar"
        elif not destino.exists():
            estado = "falta"
        elif _sha(destino) == _sha(origen):
            estado = "igual"
        elif ins._norm(destino) in nuestras:
            estado = "distinto"
        else:
            estado = "ajeno"
        salida.append({"origen": str(origen), "destino": str(destino), "estado": estado, "texto": TEXTO_PAR[estado],
                       "nivel": NIVEL_PAR[estado], "carpeta": origen.is_dir() or destino.is_dir(),
                       "origenCorto": _corta(origen), "destinoCorto": _corta(destino)})
    return salida


def _corta(p: Path) -> str:
    """Una ruta para la pantalla: el proyecto como su nombre de carpeta relativo y HOME como «~»."""
    s = str(p)
    raiz, casa = str(proyecto.raiz()), str(proyecto.home())
    if s.startswith(raiz + "/"):
        return s[len(raiz) + 1:]
    return s.replace(casa, "~", 1) if s.startswith(casa) else s


def _texto(p: Path) -> list[str] | None:
    try:
        datos = p.read_bytes()[:1_000_000]
    except OSError:
        return None
    return None if b"\0" in datos[:8192] else datos.decode("utf-8", "replace").splitlines()


def diferencia(origen: str, destino: str) -> dict:
    """La diferencia de un par lado a lado: a la izquierda lo instalado (el escritorio), a la derecha lo generado. Una
    carpeta se compara por su lista de archivos y la huella de cada uno."""
    o, d = Path(origen), Path(destino)

    def lineas(p: Path) -> list[str] | None:
        if not p.exists():
            return []
        if p.is_dir():
            return [f"{f.relative_to(p)}  ·  {_sha(f)[:8]}" for f in sorted(p.rglob("*")) if f.is_file()]
        return _texto(p)

    izq, der = lineas(d), lineas(o)
    binario = izq is None or der is None
    texto = "" if binario else "\n".join(difflib.unified_diff(izq, der, _corta(d), _corta(o), n=3, lineterm=""))
    r = diferencias.analizar(texto)
    return {"ruta": _corta(d), "izquierda": "Instalado (" + _corta(d) + ")", "derecha": "Generado (" + _corta(o) + ")",
            "filas": r["filas"], "anadidas": r["anadidas"], "quitadas": r["quitadas"], "trozos": len(r["trozos"]),
            "binario": binario, "recortado": r["recortado"], "vacia": not r["filas"], "notas": []}


# ------------------------------------------------------------------ lo propio de algunas áreas

def fuentes_instaladas(familias: list[str]) -> dict[str, bool]:
    """Si cada familia está en fontconfig (`fc-list : family`); vacío si no hay fc-list."""
    if not shutil.which("fc-list"):
        return {}
    try:
        salida = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    hay = {n.strip().lower() for linea in salida.splitlines() for n in linea.split(",")}
    return {f: f.lower() in hay for f in familias if f not in ("sans-serif", "serif", "monospace")}


def fondos() -> list[dict]:
    """Las imágenes de los fondos generados (la más pequeña de cada variante), para verlas en la página."""
    base = proyecto.raiz() / "generado" / "fondos"
    salida = []
    for d in sorted(base.iterdir()) if base.is_dir() else []:
        if not (d / "contents").is_dir():
            continue
        por_tamano = lambda c: sorted(c.glob("*x*.*"), key=lambda p: [int(n) for n in p.stem.split("x") if n.isdigit()])
        claro = por_tamano(d / "contents" / "images")
        oscuro = por_tamano(d / "contents" / "images_dark") or claro
        meta = d / "metadata.json"
        nombre = d.name
        try:
            nombre = json.loads(meta.read_text(encoding="utf-8")).get("KPlugin", {}).get("Name", d.name)
        except (OSError, ValueError):
            pass
        if claro:
            salida.append({"id": d.name, "nombre": nombre, "claro": claro[0].as_uri(), "oscuro": oscuro[0].as_uri(),
                           "tamanos": [p.stem for p in claro]})
    return salida


def iconos() -> dict:
    """Los temas de iconos y de cursores que nombra `iconos-cursores` (son de terceros: Colloid, Papirus y su superpuesto,
    WhiteSur-cursors) y si están en el usuario o en el sistema."""
    try:
        a = proyecto.leer_ajustes("iconos-cursores")
    except (StopIteration, OSError, ValueError):
        a = {}
    candidatos = [("Iconos del claro", (a.get("iconos") or {}).get("claro")), ("Iconos del oscuro", (a.get("iconos") or {}).get("oscuro")),
                  ("Reserva del claro", (a.get("reserva") or {}).get("claro")), ("Reserva del oscuro", (a.get("reserva") or {}).get("oscuro")),
                  ("Cursores", a.get("cursores")), ("Superpuesto de Lliphi", (a.get("superpuesto") or {}).get("id"))]
    bases = (proyecto.data_home() / "icons", proyecto.home() / ".icons", Path("/usr/share/icons"))
    return {"temas": [{"que": que, "tema": tema, "instalado": any((b / tema).is_dir() for b in bases)} for que, tema in candidatos if tema]}


def peso_sesiones() -> str:
    """Cuánto pesan ya las sesiones de prueba (`du -sh`, con plazo); «nada» si no hay carpeta."""
    import os
    carpeta = Path(os.environ.get("XDG_CACHE_HOME") or proyecto.home() / ".cache") / proyecto.marca()["id"] / "sesiones"
    if not carpeta.is_dir():
        return "nada"
    try:
        r = subprocess.run(["du", "-sh", str(carpeta)], capture_output=True, text=True, timeout=15)
        return (r.stdout.split() or ["?"])[0] + "B" if r.returncode == 0 else "?"
    except (OSError, subprocess.TimeoutExpired):
        return "un tamaño que no se pudo medir a tiempo"
