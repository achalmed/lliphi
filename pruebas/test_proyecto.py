"""Pruebas del proyecto: tokens válidos, contraste, deriva de lo generado, estructura de los paquetes,
instalación reversible en un HOME temporal y licencias (REUSE). Se corren con `.venv/bin/pytest`."""
from __future__ import annotations

import configparser
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PY = sys.executable
TOKENS = json.loads((RAIZ / "tokens" / "tokens.json").read_text(encoding="utf-8"))
MARCA = json.loads((RAIZ / "tokens" / "marca.json").read_text(encoding="utf-8"))
GEN = RAIZ / "generado"


def correr(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], cwd=RAIZ, capture_output=True, text=True, env=env)


# ---------------------------------------------------------------- tokens

def _tokens_planos(grupo: dict, prefijo: str = "") -> dict:
    out = {}
    for k, v in grupo.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and "$value" in v:
            out[prefijo + k] = v
        elif isinstance(v, dict):
            out.update(_tokens_planos(v, prefijo + k + "."))
    return out


def test_tokens_dtcg_validos():
    planos = _tokens_planos(TOKENS)
    assert planos, "tokens.json sin tokens"
    for nombre, t in planos.items():
        assert not re.search(r"[${}.]", nombre.split(".")[-1]), nombre
        tipo = t.get("$type") or "heredado"
        if "colorSpace" in t.get("$value", {}) if isinstance(t["$value"], dict) else False:
            v = t["$value"]
            assert v["colorSpace"] == "oklch" and len(v["components"]) == 3, nombre
            assert re.fullmatch(r"#[0-9a-f]{6}", v["hex"]), nombre
    for variante in ("claro", "oscuro"):
        sem = _tokens_planos(TOKENS["semanticos"][variante])
        for clave in ("fondo.ventana", "fondo.vista", "texto.normal", "seleccion.fondo", "seleccion.texto", "foco", "hover", "enlace"):
            assert clave in sem, (variante, clave)


def test_marca_ids_ascii():
    for v in (MARCA["id"], *MARCA["id_esquema"].values(), *MARCA["id_global"].values(), MARCA["id_fondo"]):
        assert re.fullmatch(r"[A-Za-z0-9.-]+", v), v


# ---------------------------------------------------------------- contraste y deriva

def test_contraste_todos_los_pares():
    r = correr("herramientas/paleta.py")
    assert r.returncode == 0, r.stdout[-2000:]
    assert "FALLA" not in r.stdout


def test_generado_sin_deriva():
    r = correr("herramientas/generar.py", "verificar")
    assert r.returncode == 0, r.stdout[-2000:]


def test_ningun_hex_fuera_del_maestro():
    """Los archivos de texto generados solo contienen colores que existen en tokens.json."""
    hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values()
             if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    rgbs = {",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5)) for h in hexes}
    permitidos_rgb = rgbs | {"56,56,56", "112,111,110"}          # efectos de KColorScheme, de Breeze
    for f in GEN.rglob("*"):
        if f.suffix in (".colors", ".colorscheme", "") and f.is_file() and f.name != "defaults" and "aurorae" not in f.parts:
            for m in re.findall(r"=(\d{1,3},\d{1,3},\d{1,3})\b", f.read_text(encoding="utf-8")):
                assert m in permitidos_rgb, (f.name, m)
        if f.suffix == ".svg" and "desktoptheme" not in f.parts and "kvantum" not in f.parts and "aurorae" not in f.parts and "icons" not in f.parts:
            for h in re.findall(r"#[0-9a-fA-F]{6}\b", f.read_text(encoding="utf-8")):
                assert h.lower() in hexes | {"#000000"}, (f.name, h)
        if f.suffix in (".toml", ".conf", ".json"):
            # los editores admiten #rrggbbaa: el color base debe ser del maestro; el alfa es libre
            for h in re.findall(r"#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?\b", f.read_text(encoding="utf-8")):
                assert "#" + h.lower() in hexes, (f.name, h)


# ---------------------------------------------------------------- estructura de los paquetes

def test_esquemas_completos():
    for v in ("claro", "oscuro"):
        cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
        cp.read(GEN / "color-schemes" / f"{MARCA['id_esquema'][v]}.colors", encoding="utf-8")
        for g in ("Colors:View", "Colors:Window", "Colors:Button", "Colors:Selection", "Colors:Tooltip", "Colors:Complementary", "Colors:Header", "Colors:Header][Inactive"):
            assert g in cp, g
            for k in ("BackgroundNormal", "BackgroundAlternate", "ForegroundNormal", "ForegroundInactive", "ForegroundActive",
                      "ForegroundLink", "ForegroundVisited", "ForegroundNegative", "ForegroundNeutral", "ForegroundPositive", "DecorationFocus", "DecorationHover"):
                assert k in cp[g], (g, k)
        assert cp["General"]["ColorScheme"] == MARCA["id_esquema"][v]
        assert "WM" in cp and "KDE" in cp


def test_tema_global_estructura():
    for v in ("claro", "oscuro"):
        base = GEN / "look-and-feel" / MARCA["id_global"][v]
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPackageStructure"] == "Plasma/LookAndFeel"
        assert meta["KPlugin"]["Id"] == MARCA["id_global"][v] == base.name
        assert meta["X-KDE-fallbackPackage"] == "org.kde.breeze.desktop"
        d = (base / "contents" / "defaults").read_text(encoding="utf-8")
        assert f"ColorScheme={MARCA['id_esquema'][v]}" in d and f"name={MARCA['id']}" in d
        assert "kvantum" in d.lower() and "ButtonsOnLeft=XIA" in d
        deco = MARCA["id"] if v == "oscuro" else MARCA["id"] + "-claro"
        assert "library=org.kde.kwin.aurorae.v2" in d and f"theme=__aurorae__svg__{deco}" in d
        assert (base / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js").exists()
        assert (base / "contents" / "previews" / "preview.png").exists()


def test_estilo_plasma_derivado():
    """El estilo de Plasma deriva de WhiteSur-kde: dos variantes, sin `colors` (sigue el esquema), GPL declarada, SVG válidos."""
    for v in ("claro", "oscuro"):
        base = GEN / "desktoptheme" / f"{MARCA['id']}-{v}"
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPlugin"]["Id"] == base.name and meta["KPlugin"]["License"] == "GPL-3.0-or-later"
        assert not (base / "colors").exists(), "el estilo sigue el esquema del sistema: sin colors"
        for req in ("widgets/panel-background.svg", "dialogs/background.svg", "widgets/tasks.svg", "widgets/button.svg", "plasmarc"):
            assert (base / req).exists(), (v, req)
        for svg in base.rglob("*.svg"):
            ET.parse(svg)
        assert "BlurBehindEffect" in (base / "plasmarc").read_text(encoding="utf-8")
    assert (RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "LICENSE").exists()


def test_kvantum_derivado():
    for v in ("claro", "oscuro"):
        d = GEN / "kvantum" / MARCA["id_esquema"][v]
        kv = (d / f"{MARCA['id_esquema'][v]}.kvconfig").read_text(encoding="utf-8")
        hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}
        for clave in ("window.color", "highlight.color", "text.color"):
            m = re.search(rf"^{re.escape(clave)}=(#[0-9a-f]{{6}})", kv, re.M)
            assert m and m.group(1).lower() in hexes, (v, clave)
        ET.parse(d / f"{MARCA['id_esquema'][v]}.svg")

def test_konsole_16_colores():
    for v in ("claro", "oscuro"):
        cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
        cp.read(GEN / "konsole" / f"{MARCA['nombre_esquema'][v]}.colorscheme", encoding="utf-8")
        for i in range(8):
            assert f"Color{i}" in cp and f"Color{i}Intense" in cp and f"Color{i}Faint" in cp
        assert cp["General"]["Description"] == MARCA["nombre_esquema"][v]


def _terminal(variante: str) -> dict[str, str]:
    return {k: v["$value"]["hex"] for k, v in TOKENS["terminal"][variante].items()}


def test_terminales_alacritty_kitty():
    import tomllib
    ansi = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    for v in ("claro", "oscuro"):
        t = _terminal(v)
        sem = {k: x["$value"]["hex"] for k, x in _tokens_planos(TOKENS["semanticos"][v]).items()}
        a = tomllib.loads((GEN / "terminales" / "alacritty" / f"{MARCA['id']}-{v}.toml").read_text(encoding="utf-8"))["colors"]
        assert a["primary"] == {"background": t["fondo"], "foreground": t["texto"], "dim_foreground": t["texto-tenue"], "bright_foreground": t["texto-intenso"]}
        assert a["selection"] == {"text": sem["seleccion.texto"], "background": sem["seleccion.fondo"]}
        assert a["cursor"]["cursor"] == sem["acento.base"]
        for i, n in enumerate(ansi):
            assert a["normal"][n] == t[f"color{i}"] and a["bright"][n] == t[f"color{i + 8}"], (v, n)
        k = {}
        for linea in (GEN / "terminales" / "kitty" / f"{MARCA['id']}-{v}.conf").read_text(encoding="utf-8").splitlines():
            if linea and not linea.startswith("#"):
                clave, valor = linea.split(maxsplit=1); k[clave] = valor
        assert k["foreground"] == t["texto"] and k["background"] == t["fondo"]
        assert k["selection_background"] == sem["seleccion.fondo"] and k["selection_foreground"] == sem["seleccion.texto"]
        assert k["cursor"] == sem["acento.base"] and k["url_color"] == sem["enlace"]
        for i in range(16):
            assert k[f"color{i}"] == t[f"color{i}"], (v, i)
        assert f"## name: {MARCA['nombre_esquema'][v]}" in (GEN / "terminales" / "kitty" / f"{MARCA['id']}-{v}.conf").read_text(encoding="utf-8")


def _sintaxis_esperada(v: str) -> dict[str, str]:
    t = _terminal(v)
    sem = {k: x["$value"]["hex"] for k, x in _tokens_planos(TOKENS["semanticos"][v]).items()}
    return {"palabra-clave": t["color1"], "cadena": t["color2"], "numero": t["color3"], "funcion": t["color4"],
            "comentario": sem["texto.inactivo"], "fondo": sem["fondo.vista"], "texto": sem["texto.normal"], "rojo": t["color1"]}


def test_vscode_extension():
    ext = GEN / "editores" / "vscode" / MARCA["id"]
    pkg = json.loads((ext / "package.json").read_text(encoding="utf-8"))
    assert pkg["name"] == MARCA["id"] and pkg["categories"] == ["Themes"] and pkg["engines"]["vscode"]
    temas = pkg["contributes"]["themes"]
    assert {x["uiTheme"] for x in temas} == {"vs", "vs-dark"} and len(temas) == 2
    por_ambito = {"keyword": "palabra-clave", "string": "cadena", "constant.numeric": "numero", "entity.name.function": "funcion", "comment": "comentario"}
    for entrada in temas:
        v = "claro" if entrada["uiTheme"] == "vs" else "oscuro"
        tema = json.loads((ext / entrada["path"]).read_text(encoding="utf-8"))
        assert tema["name"] == entrada["label"] == MARCA["nombre_esquema"][v]
        assert tema["type"] == ("light" if v == "claro" else "dark")
        e = _sintaxis_esperada(v)
        assert tema["colors"]["editor.background"] == e["fondo"] and tema["colors"]["editor.foreground"] == e["texto"]
        assert tema["colors"]["terminal.ansiRed"] == e["rojo"] and tema["colors"]["terminal.background"] == _terminal(v)["fondo"]
        colores_por_ambito = {a: tc["settings"]["foreground"] for tc in tema["tokenColors"] for a in tc["scope"]}
        for ambito, papel in por_ambito.items():
            assert colores_por_ambito[ambito] == e[papel], (v, ambito)
        assert tema["semanticTokenColors"]["function"] == e["funcion"]
    assert (ext / "README.md").exists()


def test_zed_tema():
    z = json.loads((GEN / "editores" / "zed" / f"{MARCA['id']}.json").read_text(encoding="utf-8"))
    assert z["name"] == MARCA["nombre"] and {t["appearance"] for t in z["themes"]} == {"light", "dark"}
    for tema in z["themes"]:
        v = "claro" if tema["appearance"] == "light" else "oscuro"
        assert tema["name"] == MARCA["nombre_esquema"][v]
        e = _sintaxis_esperada(v)
        st = tema["style"]
        assert st["editor.background"] == e["fondo"] and st["text"] == e["texto"] and st["terminal.ansi.red"] == e["rojo"]
        for papel, clave in (("palabra-clave", "keyword"), ("cadena", "string"), ("numero", "number"), ("funcion", "function"), ("comentario", "comment")):
            assert st["syntax"][clave]["color"] == e[papel], (v, clave)
        assert st["players"] and {"cursor", "background", "selection"} <= set(st["players"][0])


def test_decoracion_aurorae():
    """La decoración deriva de Nothing: dos variantes con marco, botones, rc y metadatos; GPL declarada."""
    for v, id_ in (("oscuro", MARCA["id"]), ("claro", f"{MARCA['id']}-claro")):
        base = GEN / "aurorae" / id_
        for req in ("decoration.svg", "close.svg", "maximize.svg", "minimize.svg", "restore.svg", f"{id_}rc", "metadata.json", "metadata.desktop"):
            assert (base / req).exists(), (v, req)
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPlugin"]["Id"] == id_ and meta["KPlugin"]["License"] == "GPL-3.0-or-later"
        rc = (base / f"{id_}rc").read_text(encoding="utf-8")
        assert re.search(r"^ActiveTextColor=\d+,\d+,\d+$", rc, re.M)
        for svg in base.glob("*.svg"):
            ET.parse(svg)
    assert (RAIZ / "fuentes" / "base" / "Nothing-aurorae" / "ORIGEN.md").exists()

def test_libreoffice_esquemas():
    """Fragmentos .xcu y extensión .oxt: estructura, 91 entradas por esquema, cada Color decimal es un hex de los tokens."""
    import zipfile
    sys.path.insert(0, str(RAIZ / "herramientas"))
    from destinos.libreoffice import VISIBLES, entradas  # noqa: E402
    hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    enteros = {int(h[1:], 16) for h in hexes}
    base = GEN / "libreoffice"
    raiz = "/org.openoffice.Office.UI/ColorScheme/ColorSchemes"
    for archivo, variantes in ((f"{MARCA['id']}.xcu", ("claro", "oscuro")), (f"{MARCA['id']}-claro.xcu", ("claro",)), (f"{MARCA['id']}-oscuro.xcu", ("oscuro",))):
        doc = ET.parse(base / archivo).getroot()
        assert doc.tag == "{http://openoffice.org/2001/registry}items"
        items = doc.findall("item")
        nodos = {i.find("node").get("{http://openoffice.org/2001/registry}name") for i in items if i.get("{http://openoffice.org/2001/registry}path") == raiz}
        assert nodos == {MARCA["nombre_esquema"][v] for v in variantes}
        for v in variantes:
            e = entradas(TOKENS, v)
            assert len(e) == 91 and e["DocColor"] == _sintaxis_esperada(v)["fondo"] and e["BASICKeyword"] == _sintaxis_esperada(v)["palabra-clave"]
            assert e["BASICString"] == _terminal(v)["color2"] and e["SQLNumber"] == _terminal(v)["color3"] and e["SQLComment"] == _sintaxis_esperada(v)["comentario"]
            prefijo = f"{raiz}/org.openoffice.Office.UI:ColorScheme['{MARCA['nombre_esquema'][v]}']/"
            colores = {i.get("{http://openoffice.org/2001/registry}path")[len(prefijo):]: int(i.find("prop/value").text)
                       for i in items if i.get("{http://openoffice.org/2001/registry}path", "").startswith(prefijo) and i.find("prop").get("{http://openoffice.org/2001/registry}name") == "Color"}
            assert set(colores) == set(e)
            for entrada, n in colores.items():
                assert n in enteros and n == int(e[entrada][1:], 16), (v, entrada, n)
            visibles = {i.get("{http://openoffice.org/2001/registry}path")[len(prefijo):]: i.find("prop/value").text
                        for i in items if i.get("{http://openoffice.org/2001/registry}path", "").startswith(prefijo) and i.find("prop").get("{http://openoffice.org/2001/registry}name") == "IsVisible"}
            assert visibles == {k: str(b).lower() for k, b in VISIBLES.items()}
        assert all(prop.get("{http://openoffice.org/2001/registry}op") == "fuse" for prop in doc.iter("prop")), archivo
    # la extensión: zip reproducible con manifest, description y el component-data con los dos esquemas
    with zipfile.ZipFile(base / f"{MARCA['id']}.oxt") as z:
        assert set(z.namelist()) == {"META-INF/manifest.xml", "description.xml", "descripcion.txt", f"{MARCA['id']}.xcu"}
        assert all(zi.date_time == (1980, 1, 1, 0, 0, 0) for zi in z.infolist()), "zip no reproducible"
        manifest = ET.fromstring(z.read("META-INF/manifest.xml"))
        entrada = manifest.find("{http://openoffice.org/2001/manifest}file-entry")
        assert entrada.get("{http://openoffice.org/2001/manifest}media-type") == "application/vnd.sun.star.configuration-data"
        assert entrada.get("{http://openoffice.org/2001/manifest}full-path") == f"{MARCA['id']}.xcu"
        desc = ET.fromstring(z.read("description.xml"))
        assert desc.find("{http://openoffice.org/extensions/description/2006}identifier").get("value") == f"{MARCA['dominio_inverso']}.libreoffice"
        assert desc.find("{http://openoffice.org/extensions/description/2006}version").get("value") == (RAIZ / "VERSION").read_text().strip()
        datos = ET.fromstring(z.read(f"{MARCA['id']}.xcu"))
        assert datos.get("{http://openoffice.org/2001/registry}name") == "UI" and datos.get("{http://openoffice.org/2001/registry}package") == "org.openoffice.Office"
        esquemas = datos.findall("node/node/node")
        assert {n.get("{http://openoffice.org/2001/registry}name") for n in esquemas} == set(MARCA["nombre_esquema"].values())
        for esquema in esquemas:
            assert esquema.get("{http://openoffice.org/2001/registry}op") == "replace"
            v = "claro" if esquema.get("{http://openoffice.org/2001/registry}name") == MARCA["nombre_esquema"]["claro"] else "oscuro"
            e = entradas(TOKENS, v)
            assert [n.get("{http://openoffice.org/2001/registry}name") for n in esquema.findall("node")] == list(e)
            for n in esquema.findall("node"):
                valor = int(n.find("prop[@{http://openoffice.org/2001/registry}name='Color']/value").text)
                assert valor in enteros and valor == int(e[n.get("{http://openoffice.org/2001/registry}name")][1:], 16)
        assert (base / "oxt" / f"{MARCA['id']}.xcu").read_bytes() == z.read(f"{MARCA['id']}.xcu")


def test_fondo_paquete():
    base = GEN / "wallpapers" / MARCA["id_fondo"]
    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    assert meta["KPlugin"]["Id"] == MARCA["id_fondo"]
    assert set(meta["X-KDE-PlasmaImageWallpaper-AccentColor"]) == {"Light", "Dark"}
    sys.path.insert(0, str(RAIZ / "herramientas"))
    from destinos.fondo import TAMANOS  # noqa: E402
    PIL = pytest.importorskip("PIL.Image")
    for carpeta in ("images", "images_dark"):
        for ancho, alto in TAMANOS:
            ruta = base / "contents" / carpeta / f"{ancho}x{alto}.png"
            assert ruta.exists(), ruta
            im = PIL.open(ruta)
            assert im.size == (ancho, alto) and im.mode == "RGB"
    assert PIL.open(base / "contents" / "screenshot.png").size == (480, 270)
    # el oscuro es casi negro y el claro casi blanco en la esquina (fuera del relámpago y del campo de puntos)
    oscuro = PIL.open(base / "contents" / "images_dark" / "1920x1080.png").getpixel((4, 4))
    claro = PIL.open(base / "contents" / "images" / "1920x1080.png").getpixel((4, 4))
    assert max(oscuro) < 40 and min(claro) > 215


# ---------------------------------------------------------------- instalación reversible

def _entorno(tmp: Path) -> dict:
    env = dict(os.environ)
    env.update(HOME=str(tmp), XDG_DATA_HOME=str(tmp / ".local/share"), XDG_CONFIG_HOME=str(tmp / ".config"),
               XDG_STATE_HOME=str(tmp / ".local/state"))
    return env


@pytest.mark.skipif(shutil.which("plasmashell") is None, reason="sin Plasma")
def test_instalar_y_desinstalar_restaura(tmp_path: Path):
    env = _entorno(tmp_path)
    (tmp_path / ".config").mkdir()
    (tmp_path / ".config" / "kdeglobals").write_text("[General]\nColorScheme=BreezeDark\n", encoding="utf-8")
    (tmp_path / ".positron").mkdir()          # Positron instalado; VSCodium (~/.vscode-oss) no: se omite sin crearlo
    antes = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    sim = correr("herramientas/instalar.py", env=env)
    assert sim.returncode == 0 and "SIM" in sim.stdout and not (tmp_path / ".local/share").exists(), sim.stdout
    assert "omitido" in sim.stdout and "VSCodium" in sim.stdout and "Positron no está" not in sim.stdout, sim.stdout
    ap = correr("herramientas/instalar.py", "--aplicar", env=env)
    assert ap.returncode == 0, ap.stdout + ap.stderr
    assert (tmp_path / ".local/share/plasma/look-and-feel" / MARCA["id_global"]["oscuro"] / "metadata.json").exists()
    assert (tmp_path / ".local/share/color-schemes" / f"{MARCA['id_esquema']['claro']}.colors").exists()
    assert (tmp_path / ".config/alacritty/themes" / f"{MARCA['id']}-oscuro.toml").exists()
    assert (tmp_path / ".config/kitty/themes" / f"{MARCA['id']}-claro.conf").exists()
    assert (tmp_path / ".config/zed/themes" / f"{MARCA['id']}.json").exists()
    assert (tmp_path / ".vscode/extensions" / f"{MARCA['id']}.{MARCA['id']}" / "package.json").exists()
    assert (tmp_path / ".positron/extensions" / f"{MARCA['id']}.{MARCA['id']}" / "package.json").exists()
    assert not (tmp_path / ".vscode-oss").exists()
    assert (tmp_path / ".local/share/aurorae/themes" / MARCA["id"] / "decoration.svg").exists()
    assert (tmp_path / ".local/share/aurorae/themes" / f"{MARCA['id']}-claro" / f"{MARCA['id']}-clarorc").exists()
    manifiesto = tmp_path / ".local/state" / MARCA["id"] / "instalado.json"
    assert manifiesto.exists()
    respaldo = Path(json.loads(manifiesto.read_text())["respaldo"])
    assert (respaldo / "config" / "kdeglobals").exists() and (respaldo / "UNDO.sh").exists()
    est = correr("herramientas/instalar.py", "estado", env=env)
    assert "MOD" not in est.stdout
    # otro proyecto en el mismo destino → conflicto, no se pisa
    ajeno = tmp_path / ".local/share/plasma/desktoptheme" / f"{MARCA['id']}-oscuro" / "ajeno.txt"
    ajeno.write_text("x")
    manifiesto.unlink()
    conf = correr("herramientas/instalar.py", "--aplicar", env=env)
    assert conf.returncode == 3 and ajeno.exists()
    ajeno.unlink(); ap2 = correr("herramientas/instalar.py", "--aplicar", env=env); assert ap2.returncode == 0
    # UNDO restaura la configuración y retira lo instalado
    (tmp_path / ".config" / "kdeglobals").write_text("[General]\nColorScheme=Otro\n", encoding="utf-8")
    manifiesto2 = json.loads(manifiesto.read_text())
    undo = subprocess.run(["bash", str(Path(manifiesto2["respaldo"]) / "UNDO.sh")], capture_output=True, text=True, env=env)
    assert undo.returncode == 0, undo.stderr
    assert (tmp_path / ".config" / "kdeglobals").read_bytes() == antes[Path(".config/kdeglobals")]
    assert not (tmp_path / ".local/share/plasma/look-and-feel" / MARCA["id_global"]["oscuro"]).exists()
    assert not (tmp_path / ".config/kitty/themes" / f"{MARCA['id']}-claro.conf").exists()
    assert not (tmp_path / ".vscode/extensions" / f"{MARCA['id']}.{MARCA['id']}").exists()
    assert not (tmp_path / ".positron/extensions" / f"{MARCA['id']}.{MARCA['id']}").exists() and (tmp_path / ".positron").is_dir()
    assert not manifiesto.exists()


# ---------------------------------------------------------------- licencias

@pytest.mark.skipif(shutil.which("reuse") is None and not (RAIZ / ".venv/bin/reuse").exists(), reason="sin reuse")
def test_reuse_lint():
    reuse = shutil.which("reuse") or str(RAIZ / ".venv/bin/reuse")
    r = subprocess.run([reuse, "lint"], cwd=RAIZ, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:]
