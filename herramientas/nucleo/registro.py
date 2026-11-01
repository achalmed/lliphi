"""Registro de módulos: descubre los manifiestos (`modulo.json`), los ordena y carga su código.

Hay tres raíces: `global/` (el tema global, integrador), `modulos/<id>/` (los seis módulos) y `complementos/<id>/`
(piezas fuera del tema global). Cada carpeta con `modulo.json` es un módulo cuyo `id` es el nombre de la carpeta.
El código de un módulo (`construir.py`, `aplicar.py`, `externas.py`) se carga por ruta, porque los ids llevan guion
y no son nombres de paquete de Python; un módulo usa el de otro con `registro.codigo("<id>")`, y solo si lo declara
en `dependencias.construccion` (lo comprueba `validacion.py`). Solo biblioteca estándar."""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from . import RAIZ

RAICES = (("global", RAIZ / "global"), ("modulo", RAIZ / "modulos"), ("complemento", RAIZ / "complementos"))
CLASES = ("paquete", "componente", "externo")
ROLES = ("global", "modulo", "complemento")
GENERADO = RAIZ / "generado"


@dataclass
class Modulo:
    id: str
    rol: str                      # global · modulo · complemento (por la raíz en la que está)
    carpeta: Path
    datos: dict = field(repr=False)

    @property
    def clase(self) -> str:       # paquete (entrega archivos propios) · componente (los escribe dentro del tema global) · externo (terceros)
        return self.datos["clase"]

    @property
    def orden(self) -> int:
        return int(self.datos.get("orden", 100))

    def dependencias(self, tipo: str) -> list[str]:
        return list(self.datos.get("dependencias", {}).get(tipo, []))

    @property
    def generado(self) -> Path:
        return GENERADO / self.id

    def archivo(self, nombre: str) -> Path:
        return self.carpeta / nombre

    def tiene(self, nombre: str) -> bool:
        return (self.carpeta / nombre).is_file()


def _leer(rol: str, carpeta: Path) -> Modulo:
    datos = json.loads((carpeta / "modulo.json").read_text(encoding="utf-8"))
    return Modulo(id=carpeta.name, rol=rol, carpeta=carpeta, datos=datos)


_CACHE: dict[str, Modulo] | None = None


def todos() -> list[Modulo]:
    """Todos los módulos, en el orden canónico: global primero, después los seis módulos y los complementos por `orden`."""
    global _CACHE
    if _CACHE is None:
        hallados: list[Modulo] = []
        for rol, raiz in RAICES:
            if rol == "global":
                if (raiz / "modulo.json").exists():
                    hallados.append(_leer(rol, raiz))
                continue
            for carpeta in sorted(raiz.iterdir()) if raiz.is_dir() else []:
                if (carpeta / "modulo.json").exists():
                    hallados.append(_leer(rol, carpeta))
        hallados.sort(key=lambda m: (ROLES.index(m.rol), m.orden, m.id))
        _CACHE = {m.id: m for m in hallados}
    return list(_CACHE.values())


def modulo(id_: str) -> Modulo:
    todos()
    assert _CACHE is not None
    if id_ not in _CACHE:
        raise KeyError(f"módulo desconocido: {id_}")
    return _CACHE[id_]


def ids(clase: str | None = None) -> list[str]:
    return [m.id for m in todos() if clase is None or m.clase == clase]


def orden_de_construccion(seleccion: list[str]) -> list[str]:
    """Los ids pedidos más lo que necesitan para construirse (`construccion` e `integra`), en orden topológico."""
    visto: dict[str, int] = {}          # 1 = en curso, 2 = hecho
    salida: list[str] = []

    def visitar(i: str, camino: tuple[str, ...]) -> None:
        if visto.get(i) == 2:
            return
        if visto.get(i) == 1:
            raise ValueError("ciclo de dependencias: " + " → ".join((*camino, i)))
        visto[i] = 1
        m = modulo(i)
        for d in m.dependencias("construccion") + m.dependencias("integra"):
            visitar(d, (*camino, i))
        visto[i] = 2
        salida.append(i)

    for i in seleccion:
        visitar(i, ())
    return salida


_CODIGO: dict[tuple[str, str], ModuleType] = {}


def codigo(id_: str, archivo: str = "construir") -> ModuleType:
    """Carga `<carpeta del módulo>/<archivo>.py` (una sola vez) y lo devuelve."""
    clave = (id_, archivo)
    if clave not in _CODIGO:
        ruta = modulo(id_).archivo(f"{archivo}.py")
        if not ruta.exists():
            raise FileNotFoundError(f"el módulo {id_} no tiene {archivo}.py")
        herramientas = str(RAIZ / "herramientas")
        if herramientas not in sys.path:
            sys.path.insert(0, herramientas)
        nombre = f"lliphi_{id_.replace('-', '_')}_{archivo}"
        spec = importlib.util.spec_from_file_location(nombre, ruta)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nombre] = mod
        spec.loader.exec_module(mod)
        _CODIGO[clave] = mod
    return _CODIGO[clave]


def con(archivo: str) -> list[Modulo]:
    """Los módulos que tienen `<archivo>.py` (aplicar, externas), en el orden canónico."""
    return [m for m in todos() if m.tiene(f"{archivo}.py")]
