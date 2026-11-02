"""Tema global de Lliphi (paquetes `Plasma/LookAndFeel`, uno por variante): el **integrador** de los módulos.

Estructura (Calibre 10525; `/usr/share/plasma/look-and-feel/org.kde.breezedark.desktop`): `metadata.json` con
`KPackageStructure` y `KPlugin`, `contents/defaults` con la sintaxis `[archivo][grupo]`, `contents/layouts/
org.kde.plasma.desktop-layout.js`, `contents/splash/`, `contents/logout/` y `contents/previews/`. Lo que no trae lo
hereda de Breeze con `X-KDE-fallbackPackage`.

Qué hace el tema global y qué no:
- **Declara** los componentes por su identificador: `contents/defaults` se compone con lo que aporta cada módulo
  (`valores(marca, variante)` de su `construir.py`) en el orden de `GRUPOS`; el tema global solo pone lo suyo, la
  tipografía. Ningún identificador de otro módulo está escrito aquí.
- **Integra** los componentes que KDE exige dentro del paquete (`dependencias.integra` del manifiesto):
  `carga-bloqueo` escribe `contents/splash/` y `contents/logout/`; `disposicion`, `contents/layouts/`.
- **No copia** los paquetes de los demás módulos (esquema, estilo, decoración, fondo, Kvantum): se instalan por su
  cuenta en su sitio de KDE y el tema global los nombra.
- Pone las vistas previas: capturas reales (`muestras/capturas/`); si faltan, el boceto rotulado."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from nucleo import RAIZ, VERSION, autores, escribir, registro

CABECERA = "# GENERADO por herramientas/generar.py desde tokens/; no editar"

# Orden de los grupos en `contents/defaults` (el de la versión 0.3.0); un grupo que no esté aquí va al final.
GRUPOS = ["kdeglobals][KDE", "kdeglobals][Icons", "kdeglobals][General", "kdeglobals][WM", "plasmarc][Theme",
          "Wallpaper", "kcminputrc][Mouse", "kwinrc][org.kde.kdecoration2", "kwinrc][WindowSwitcher",
          "kwinrc][DesktopSwitcher", "KSplash"]

# Fuentes en el formato de Qt 6 (`QFont::toString`, 16 campos): con los 10 del de Qt 5, Qt 6 lee el peso (quinto campo)
# en la escala vieja, 0–99, y 400 pasa a 900, Black: toda la interfaz en negrita (decisiones 5.46).
def fuente(familia: str, puntos: int, peso: int = 400) -> str:
    """familia, puntos, píxeles (-1), estilo (5), peso, diez atributos (cursiva, subrayado… en 0) y 1, el marcador
    que distingue el formato de Qt 6."""
    return f"{familia},{puntos},-1,5,{peso}" + ",0" * 10 + ",1"


INTERFAZ = fuente("Inter", 10)
MONO = fuente("JetBrainsMono Nerd Font", 10)   # mejora 9 (decisiones 4.14)


def valores(marca: dict, variante: str) -> dict[str, dict[str, str]]:
    """Lo propio del tema global: la tipografía de la interfaz (Inter), de los títulos (Inter Medium) y monoespaciada."""
    return {"kdeglobals][General": {"font": INTERFAZ, "fixed": MONO, "menuFont": INTERFAZ, "toolBarFont": INTERFAZ,
                                     "smallestReadableFont": fuente("Inter", 8)},
            "kdeglobals][WM": {"activeFont": fuente("Inter", 10, 500)}}


def aportes() -> list[str]:
    """Quién aporta a `defaults`, en orden: los referidos y los integrados del manifiesto, con el propio tema global
    detrás del esquema (así `ColorScheme` precede a la tipografía en `[kdeglobals][General]`)."""
    m = registro.modulo("global")
    ids = m.dependencias("referencia") + m.dependencias("integra")
    i = ids.index("esquema") + 1 if "esquema" in ids else 0
    return ids[:i] + ["global"] + ids[i:]


def defaults(marca: dict, variante: str) -> str:
    grupos: dict[str, dict[str, str]] = {}
    for id_ in aportes():
        mod = registro.codigo(id_)
        for grupo, claves in (mod.valores(marca, variante) if hasattr(mod, "valores") else {}).items():
            destino = grupos.setdefault(grupo, {})
            for clave, valor in claves.items():
                assert clave not in destino, f"{id_} repite [{grupo}] {clave}: cada clave de defaults tiene un solo dueño"
                destino[clave] = valor
    orden = [g for g in GRUPOS if g in grupos] + [g for g in grupos if g not in GRUPOS]
    bloques = ["\n".join([f"[{g}]", *[f"{k}={v}" for k, v in grupos[g].items()]]) for g in orden]
    return CABECERA + "\n\n" + "\n\n".join(bloques) + "\n"


def metadata(marca: dict, variante: str) -> str:
    return json.dumps({
        "KPackageStructure": "Plasma/LookAndFeel",
        "KPlugin": {
            "Authors": autores(marca),
            "Category": "",
            "Description": f"{marca['nombre_esquema'][variante]}: {marca['descripcion']}",
            "Id": marca["id_global"][variante],
            "License": marca["licencia_activos"],
            "Name": marca["nombre_esquema"][variante],
            "Version": VERSION,
            "Website": marca["sitio"],
        },
        "X-KDE-fallbackPackage": "org.kde.breeze.desktop",
        "X-KPackage-Dependencies": ["kns://xcursor.knsrc/api.kde-look.org/1411743"],
    }, ensure_ascii=False, indent=4) + "\n"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    integrados = registro.modulo("global").dependencias("integra")
    for variante in ("claro", "oscuro"):
        base = destino / marca["id_global"][variante]
        escribir(base / "metadata.json", metadata(marca, variante), hechos)
        escribir(base / "contents" / "defaults", defaults(marca, variante), hechos)
        for id_ in integrados:
            registro.codigo(id_).integrar(tokens, marca, variante, base, hechos)
        # Vistas previas: capturas reales de la fase 7 (muestras/capturas); si faltan, el boceto rotulado.
        captura = RAIZ / "muestras" / "capturas" / f"{variante}-02-lanzador.png"
        origen_previa = captura if captura.exists() else RAIZ / "muestras" / f"boceto-{variante}.png"
        for origen, nombre in ((origen_previa, "fullscreenpreview.jpg"), (origen_previa, "preview.png")):
            if origen.exists():
                dest = base / "contents" / "previews" / nombre
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(origen, dest)
                hechos.append(dest)
    return hechos
