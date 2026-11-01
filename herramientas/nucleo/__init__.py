"""Núcleo común de Lliphi: lo que comparten los módulos y las dos órdenes (`generar.py`, `instalar.py`).

Aquí viven las utilidades de lectura de los tokens (`cargar`, `aplanar`, `semanticos`, `rgb`…) que usan los
`construir.py` de cada módulo; el resto del núcleo está en `registro.py` (qué módulos hay y en qué orden),
`construccion.py`, `validacion.py`, `instalacion.py` y `sitio.py`. Solo biblioteca estándar.

Cada módulo de clase `paquete` expone `generar(tokens, marca, destino: Path) -> list[Path]` y escribe bajo `destino`
(`generado/<id>/`); la interfaz completa está en `docs/arquitectura.md` §4."""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
TOKENS = RAIZ / "tokens" / "tokens.json"
MARCA = RAIZ / "tokens" / "marca.json"
VERSION = (RAIZ / "VERSION").read_text(encoding="utf-8").strip() if (RAIZ / "VERSION").exists() else "0.1.0"
CABECERA_INI = "# GENERADO por herramientas/generar.py desde tokens/; no editar\n"


def cargar() -> tuple[dict, dict]:
    return (json.loads(TOKENS.read_text(encoding="utf-8")), json.loads(MARCA.read_text(encoding="utf-8")))


def aplanar(grupo: dict, prefijo: str = "") -> dict[str, dict]:
    """{'fondo.ventana': token, …} desde el árbol de grupos DTCG."""
    plano = {}
    for k, v in grupo.items():
        if isinstance(v, dict) and "$value" in v:
            plano[prefijo + k] = v
        elif isinstance(v, dict):
            plano.update(aplanar(v, prefijo + k + "."))
    return plano


def hexa(token: dict) -> str:
    return token["$value"]["hex"]


def rgb(token: dict) -> str:
    h = hexa(token).lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def semanticos(tokens: dict, variante: str) -> dict[str, str]:
    """token semántico → hex, para una variante."""
    return {k: hexa(v) for k, v in aplanar(tokens["semanticos"][variante]).items()}


def escribir(ruta: Path, texto: str, hechos: list[Path]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")
    hechos.append(ruta)


def autores(marca: dict) -> list[dict]:
    return [{"Name": marca["autor"], "Email": marca.get("correo", "")}]
