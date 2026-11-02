"""studio/lliphi_app/servicios/destinos.py — cada destino del tema (el tema global, los módulos y los complementos)
como fila de la ventana, sin Qt: qué entrega (`modulo.json`), cuántos archivos tiene en `generado/` y de cuándo, si
está al día con los tokens (`generar.py verificar --json`, guardado en la caché del studio con su fecha), si está
instalado y sigue como se instaló (el manifiesto e `instalar.py estado --json`, con los pares origen → destino del
núcleo), el Resumen en Markdown y la paleta de los tokens como datos (`docs/rediseno.md` S1–S3)."""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

from lliphi_app.servicios import proyecto

ROLES = (("global", "Tema global"), ("modulo", "Módulo"), ("complemento", "Complemento"))
TEXTO_ROL = dict(ROLES)
ESTADOS_GENERADO = (("al_dia", "Al día"), ("desfasado", "Desfasado"), ("sin_comprobar", "Sin comprobar"), ("sin_generar", "Sin generar"))
ESTADOS_INSTALACION = (("instalado", "Instalado"), ("modificado", "Modificado"), ("sin_instalar", "Sin instalar"), ("no_instalable", "No se instala"))
TEXTO_GENERADO = dict(ESTADOS_GENERADO)
TEXTO_INSTALACION = dict(ESTADOS_INSTALACION)
NIVEL_GENERADO = {"al_dia": "positivo", "desfasado": "negativo", "sin_comprobar": "neutro", "sin_generar": "inactivo"}
NIVEL_INSTALACION = {"instalado": "positivo", "modificado": "negativo", "sin_instalar": "neutro", "no_instalable": "inactivo"}
ICONO_ROL = {"global": "preferences-desktop-theme-global", "modulo": "package-x-generic", "complemento": "preferences-plugin"}
PRIVILEGIADOS = ("sddm", "gtk")           # piden pkexec: se instalan desde la terminal


def nucleo():
    """El núcleo de Lliphi (`herramientas/nucleo`, solo biblioteca estándar) cargado por ruta desde la raíz del proyecto."""
    ruta = proyecto.raiz() / "herramientas" / "nucleo" / "__init__.py"
    nombre = "lliphi_nucleo_studio"
    if nombre in sys.modules and getattr(sys.modules[nombre], "__file__", "") == str(ruta):
        return sys.modules[nombre]
    for viejo in [k for k in sys.modules if k == nombre or k.startswith(nombre + ".")]:   # otra raíz (las pruebas): sin submódulos viejos
        del sys.modules[viejo]
    spec = importlib.util.spec_from_file_location(nombre, ruta, submodule_search_locations=[str(ruta.parent)])
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def pares_instalacion(id_: str) -> tuple[list[tuple[str, str]], list[str]]:
    """[(origen, destino)] absolutos de lo que instala el módulo y los avisos de lo omitido (bases que no están)."""
    try:
        n = nucleo()
        instalacion = importlib.import_module(f"{n.__name__}.instalacion")
        pares, omitidos = instalacion.pares_de([id_])
        return [(str(o), str(d)) for o, d in pares], list(omitidos)
    except Exception as e:      # noqa: BLE001  un manifiesto roto no tumba la tabla
        return [], [f"no se pudieron leer los destinos de instalación: {e}"]


def generado_de(m: proyecto.Modulo) -> tuple[int, float | None]:
    """(archivos, fecha del más reciente) de `generado/<id>/`."""
    carpeta = m.generado
    if not carpeta.is_dir():
        return 0, None
    tiempos = [p.stat().st_mtime for p in carpeta.rglob("*") if p.is_file()]
    return len(tiempos), (max(tiempos) if tiempos else None)


def fuentes_mas_nuevas_que(fecha: float) -> bool:
    """¿Cambió algo de lo que entra en la construcción (tokens, manifiestos, construir.py, fuentes) después de `fecha`?"""
    r = proyecto.raiz()
    for carpeta in (r / "tokens", r / "global", r / "modulos", r / "complementos", r / "fuentes", r / "herramientas"):
        if not carpeta.is_dir():
            continue
        for p in carpeta.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts and p.stat().st_mtime > fecha:
                return True
    return False


class Verificacion:
    """La última `generar.py verificar --json` guardada en la caché del studio: por módulo, sus diferencias."""

    def __init__(self, archivo: Path):
        self.archivo = Path(archivo)
        self.fecha = 0.0
        self.diferencias: dict[str, list[str]] = {}
        self.todas: list[str] = []
        try:
            d = json.loads(self.archivo.read_text(encoding="utf-8"))
            self.fecha, self.todas = float(d.get("fecha", 0)), list(d.get("diferencias", []))
            self.diferencias = self._por_modulo(self.todas)
        except (OSError, ValueError, TypeError):
            pass

    @staticmethod
    def _por_modulo(diferencias: list[str]) -> dict[str, list[str]]:
        por: dict[str, list[str]] = {}
        for x in diferencias:
            id_, _, resto = x.partition("/")
            por.setdefault(id_, []).append(resto or x)
        return por

    def registrar(self, diferencias: list[str]) -> None:
        self.fecha, self.todas = time.time(), list(diferencias)
        self.diferencias = self._por_modulo(self.todas)
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            self.archivo.write_text(json.dumps({"fecha": self.fecha, "diferencias": self.todas}, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    @property
    def vigente(self) -> bool:
        return self.fecha > 0 and not fuentes_mas_nuevas_que(self.fecha)

    def estado(self, m: proyecto.Modulo, archivos: int) -> str:
        if m.clase == "externo":
            return "al_dia" if self.vigente else "sin_comprobar"
        if archivos == 0 and m.clase == "paquete":
            return "sin_generar"
        if not self.vigente:
            return "sin_comprobar"
        return "desfasado" if self.diferencias.get(m.id) else "al_dia"


def leer_estado_instalacion() -> dict:
    """`instalar.py estado --json`, o lo que diga el manifiesto si la orden no responde."""
    datos = proyecto.correr_json("instalar", "estado", timeout=60)
    if datos:
        return datos
    manifiesto = proyecto.state_lliphi() / "instalado.json"
    try:
        m = json.loads(manifiesto.read_text(encoding="utf-8"))
        return {"instalado": True, "version": m.get("version"), "fecha": m.get("fecha"), "modulos": m.get("modulos", []), "respaldo": m.get("respaldo"),
                "rutas": [{"ruta": r, "ok": Path(r).exists()} for r in m.get("rutas", {})]}
    except (OSError, ValueError):
        return {"instalado": False, "modulos": [], "rutas": []}


def estado_instalacion(m: proyecto.Modulo, instalacion: dict, pares: list[tuple[str, str]]) -> str:
    if m.clase != "paquete" or not m.datos.get("instalacion"):
        return "no_instalable"
    if not instalacion.get("instalado") or m.id not in (instalacion.get("modulos") or []):
        return "sin_instalar"
    rutas = {r["ruta"]: r.get("ok", False) for r in instalacion.get("rutas", [])}
    destinos = [d for _o, d in pares]
    if destinos and any(not rutas.get(d, True) for d in destinos):
        return "modificado"
    return "instalado"


def fila(m: proyecto.Modulo, verificacion: Verificacion, instalacion: dict) -> dict:
    archivos, fecha = generado_de(m)
    pares, _omitidos = pares_instalacion(m.id) if m.clase == "paquete" else ([], [])
    gen = verificacion.estado(m, archivos)
    ins = estado_instalacion(m, instalacion, pares)
    return {"destino": m.nombre, "id": m.id, "rol": TEXTO_ROL.get(m.rol, m.rol), "clase": m.clase, "formato": m.formato,
            "archivos": str(archivos) if archivos else ("—" if m.clase != "paquete" else "0"), "generado": TEXTO_GENERADO[gen],
            "instalacion": TEXTO_INSTALACION[ins], "construccion": time.strftime("%Y-%m-%d %H:%M", time.localtime(fecha)) if fecha else "—",
            "nivel": NIVEL_GENERADO[gen] if gen in ("desfasado", "sin_generar") else NIVEL_INSTALACION[ins] if ins == "modificado" else NIVEL_GENERADO[gen],
            "icono": {"destino": ICONO_ROL.get(m.rol, "package-x-generic")}, "habilitado": True, "rol_id": m.rol, "clave_generado": gen, "clave_instalacion": ins,
            "nivel_generado": NIVEL_GENERADO[gen], "nivel_instalacion": NIVEL_INSTALACION[ins], "n_destinos": len(pares),
            "crudo": {"archivos": archivos, "construccion": fecha or 0, "rol": ["global", "modulo", "complemento"].index(m.rol) if m.rol in ("global", "modulo", "complemento") else 9,
                      "generado": list(TEXTO_GENERADO).index(gen), "instalacion": list(TEXTO_INSTALACION).index(ins)}}


def resumen_markdown(m: proyecto.Modulo, f: dict, instalacion: dict) -> str:
    d = m.datos
    partes = [f"# {m.nombre}", d.get("resumen", "")]
    datos = [f"**Rol**: {TEXTO_ROL.get(m.rol, m.rol)} · **clase** {m.clase} · **formato** {m.formato}"]
    if d.get("tecnologia"):
        datos.append(f"**Tecnología**: {d['tecnologia']}")
    if d.get("estado") or d.get("desde"):
        datos.append(f"**Estado**: {d.get('estado', '')}" + (f" · desde {d['desde']}" if d.get("desde") else ""))
    datos.append(f"**Generado**: {f['archivos']} archivo(s) en `generado/{m.id}/` · {f['generado'].lower()} · última construcción {f['construccion']}")
    datos.append(f"**Instalación**: {f['instalacion'].lower()}" + (f" · {f['n_destinos']} destino(s)" if f["n_destinos"] else ""))
    if m.id in PRIVILEGIADOS:
        datos.append("**Privilegios**: este destino (o parte de él) se instala con pkexec desde la terminal (`instalar.py sddm` · `instalar.py gtk-root`).")
    partes.append("  \n".join(datos))
    if d.get("archivos"):
        partes.append("## Entrega\n\n" + "\n".join(f"- `{a}`" for a in d["archivos"]))
    deps = d.get("dependencias", {})
    lineas = []
    for tipo, titulo in (("construccion", "construcción"), ("integra", "integra"), ("referencia", "referencia"), ("bases", "bases"), ("python", "Python"), ("terceros", "terceros")):
        if deps.get(tipo):
            lineas.append(f"- **{titulo}**: " + ", ".join(deps[tipo]))
    herramientas = m.herramientas()
    if herramientas:
        lineas.append("- **herramientas**: " + ", ".join(f"{h} {'✓' if ok else '✗ (no está)'}" for h, ok in herramientas.items()))
    if lineas:
        partes.append("## Dependencias\n\n" + "\n".join(lineas))
    pares, omitidos = pares_instalacion(m.id) if m.clase == "paquete" else ([], [])
    if pares:
        rutas = {r["ruta"]: r.get("ok", False) for r in instalacion.get("rutas", [])}
        instalado = m.id in (instalacion.get("modulos") or [])
        lineas = []
        for origen, destino in pares:
            marca = "" if not instalado else (" · ✓ intacto" if rutas.get(destino, False) else (" · ✗ modificado o ausente" if destino in rutas else " · no instalado"))
            lineas.append(f"- `{proyecto.Path(origen).name}` → `{destino}`{marca}")
        partes.append("## Instalación\n\n" + "\n".join(lineas) + ("\n\n" + "\n".join(f"- {o}" for o in omitidos) if omitidos else ""))
    if instalacion.get("instalado") and instalacion.get("respaldo"):
        partes.append(f"*Último respaldo del instalador*: `{instalacion['respaldo']}` (su `UNDO.sh` vuelve exactamente a lo de antes).")
    return "\n\n".join(p for p in partes if p) + "\n"


def paleta(tokens: dict) -> list[dict]:
    """[{grupo, variante, colores: [{nombre, hex, oklch}]}] de los tokens de color, como datos del tema."""
    salida = []
    for grupo in ("primitivas", "semanticos", "terminal"):
        for variante in ("claro", "oscuro"):
            arbol = (tokens.get(grupo) or {}).get(variante) or {}
            colores = []

            def recorrer(nodo: dict, prefijo: str = "") -> None:
                for k, v in nodo.items():
                    if k.startswith("$"):
                        continue
                    if isinstance(v, dict) and "$value" in v:
                        valor = v["$value"]
                        hexa = valor.get("hex", "") if isinstance(valor, dict) else str(valor)
                        comp = valor.get("components") if isinstance(valor, dict) else None
                        oklch = f"oklch({comp[0]:.3f} {comp[1]:.3f} {comp[2]:.0f})" if isinstance(comp, list) and len(comp) == 3 else ""
                        if hexa.startswith("#"):
                            colores.append({"nombre": prefijo + k, "hex": hexa, "oklch": oklch})
                    elif isinstance(v, dict):
                        recorrer(v, prefijo + k + ".")

            recorrer(arbol)
            if colores:
                salida.append({"grupo": grupo, "variante": variante, "titulo": f"{grupo.capitalize()} · {variante}", "colores": colores})
    return salida
