"""Pruebas del proyecto: tokens válidos, contraste, deriva de lo generado, estructura de los paquetes, arquitectura
modular (registro, validación, integración en el tema global), instalación reversible en un HOME temporal y licencias
(REUSE). Se corren con `.venv/bin/pytest`."""
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
sys.path.insert(0, str(RAIZ / "herramientas"))
from nucleo import registro  # noqa: E402


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
    r = correr("modulos/esquema/paleta.py")
    assert r.returncode == 0, r.stdout[-2000:]
    assert "FALLA" not in r.stdout


def test_ajustes_paleta(tmp_path: Path):
    """Los valores de la paleta viven en ajustes.json (canónico); un borrador se informa en JSON sin escribir nada."""
    sys.path.insert(0, str(RAIZ / "modulos" / "esquema"))
    import paleta
    ruta = RAIZ / "modulos" / "esquema" / "ajustes.json"
    texto = ruta.read_text(encoding="utf-8")
    assert paleta.volcar_ajustes(json.loads(texto)) == texto
    r = correr("modulos/esquema/paleta.py", "--json")
    datos = json.loads(r.stdout)
    assert r.returncode == 0 and datos["ok"]
    assert datos["variantes"]["oscuro"]["semanticos"]["acento.base"]["hex"] == "#c93436"
    borrador = json.loads(texto)
    borrador["acento"]["oscuro"] = "azul"
    borrador["neutros"]["oscuro"]["neutro-5"] = [0.30, 0.006]      # texto inactivo casi negro: debe fallar
    (tmp_path / "b.json").write_text(json.dumps(borrador), encoding="utf-8")
    antes = (RAIZ / "tokens" / "tokens.json").read_bytes()
    r = correr("modulos/esquema/paleta.py", "--ajustes", str(tmp_path / "b.json"), "--json")
    datos = json.loads(r.stdout)
    assert r.returncode == 1 and not datos["ok"] and datos["acento"]["oscuro"] == "azul"
    assert correr("modulos/esquema/paleta.py", "--ajustes", str(tmp_path / "b.json"), "--aplicar").returncode != 0
    assert (RAIZ / "tokens" / "tokens.json").read_bytes() == antes


def test_ajustes_de_los_modulos(tmp_path: Path):
    """Decoración e iconos leen sus valores de ajustes.json; las órdenes dan su informe en JSON para Lliphi Studio."""
    dec = registro.codigo("decoracion")
    assert dec.ajustes()["rc"]["TitleHeight"] == "18"
    assert dec.valores(MARCA, "oscuro")["kwinrc][org.kde.kdecoration2"]["ButtonsOnLeft"] == dec.ajustes()["botones"]["izquierda"]
    with pytest.raises(ValueError):
        dec._poner("[Layout]\nTitleHeight=12\n", "NoExiste", "1")
    assert registro.codigo("iconos-cursores").ICONOS["oscuro"] == "Papirus-Dark-Lliphi"
    r = correr("herramientas/generar.py", "validar", "--json")
    assert r.returncode == 0 and json.loads(r.stdout)["valido"]
    datos = json.loads(correr("herramientas/generar.py", "verificar", "--json").stdout)
    assert {"archivos", "al_dia", "diferencias"} <= set(datos)
    env = {**os.environ, "XDG_STATE_HOME": str(tmp_path / "state")}
    assert json.loads(correr("herramientas/instalar.py", "estado", "--json", env=env).stdout)["instalado"] is False


def test_disposicion_desde_ajustes():
    """La disposición sale de ajustes.json; un valor que Plasma 6.6 no entiende se rechaza al construir."""
    disp = registro.codigo("disposicion")
    js = disp.script(MARCA)
    assert '"ocultar": "dodgewindows"' in js and "@PANELES@" not in js and "@FONDO@" not in js
    malo = {"paneles": [{"variable": "x", "ubicacion": "top", "alto": 2, "ocultar": "windowscover", "flotante": False,
                         "widgets": [{"tipo": "org.kde.plasma.kickoff"}]}]}
    with pytest.raises(ValueError):
        disp.script(MARCA, malo)
    generado = (GEN / "global" / MARCA["id_global"]["oscuro"] / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js")
    assert generado.read_text(encoding="utf-8") == js


def _sesion(monkeypatch, tmp_path: Path):
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import sesion
    monkeypatch.setattr(sesion, "CACHE", tmp_path / "cache" / "sesiones")
    monkeypatch.setattr(sesion, "ESTADO", tmp_path / "state" / "sesion-prueba.json")
    monkeypatch.setattr(sesion, "DATA_REAL", tmp_path / "data")
    return sesion


def test_sesion_de_prueba_prepara_y_aisla(tmp_path: Path, monkeypatch):
    """El HOME de prueba lleva systemd, bloqueo e inactividad apagados y los temas enlazados; el entorno no hereda el
    bus ni el PATH del usuario."""
    sesion = _sesion(monkeypatch, tmp_path)
    (tmp_path / "data" / "icons" / "Papirus").mkdir(parents=True)
    casa = sesion.CACHE / "x" / "casa"
    sesion.preparar_casa(casa)
    sesion.preparar_casa(casa)   # idempotente
    assert "systemdBoot=false" in (casa / ".config" / "startkderc").read_text()
    kscreen = (casa / ".config" / "kscreenlockerrc").read_text()
    assert kscreen.count("[Daemon]") == 1 and "Autolock=false" in kscreen
    assert "[AC][Display]" in (casa / ".config" / "powerdevilrc").read_text()
    assert (casa / ".local" / "share" / "icons" / "Papirus").is_symlink()
    monkeypatch.setenv("DBUS_SESSION_BUS_ADDRESS", "unix:path=/no")
    env = sesion.entorno_inicial(casa, tmp_path / "run", virtual=True)
    assert env["HOME"] == str(casa) and env["PATH"] == sesion.PATH
    assert "DBUS_SESSION_BUS_ADDRESS" not in env and "WAYLAND_DISPLAY" not in env
    assert sesion.entorno_inicial(casa, tmp_path / "run", virtual=False)["WAYLAND_DISPLAY"].startswith("/")


def test_sesion_de_prueba_se_niega(tmp_path: Path, monkeypatch):
    """Ninguna orden corre dentro sin una sesión de prueba viva y con su HOME bajo la caché de sesiones."""
    sesion = _sesion(monkeypatch, tmp_path)
    with pytest.raises(PermissionError):
        sesion.entorno_dentro({"casa": str(Path.home())})
    with pytest.raises(LookupError):
        sesion.entorno_dentro({"casa": str(sesion.CACHE / "x" / "casa")})
    assert sesion.ejecutar(["ejecutar", "--", "true"]) == 3
    assert sesion.cerrar(["cerrar"]) == 0
    env = {**os.environ, "XDG_CACHE_HOME": str(tmp_path / "c"), "XDG_STATE_HOME": str(tmp_path / "s")}
    r = correr("herramientas/sesion.py", "arrancar", "--virtual", env=env)
    assert r.returncode == 0 and "SIMULACIÓN" in r.stdout and not (tmp_path / "c").exists()
    assert json.loads(correr("herramientas/sesion.py", "estado", "--json", env=env).stdout)["activa"] is False


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
        # línea base (decisiones 4.4 y 4.5): LliphiOscuro/LliphiClaro.colors son WhiteSur-kde con solo el acento de los tokens
        # (lo verifica test_esquema_linea_base_solo_acento) y el `colors` del estilo de Plasma es copia de WhiteSur-kde;
        # solo las variantes `-tokens` y lo demás (Konsole, terminales) salen por entero del maestro
        copia_whitesur = f.suffix == ".colors" and not f.stem.endswith("-tokens") or (f.name == "colors" and "estilo" in f.parts)
        if f.suffix in (".colors", ".colorscheme", "") and f.is_file() and f.name != "defaults" and "decoracion" not in f.parts and not copia_whitesur:
            for m in re.findall(r"=(\d{1,3},\d{1,3},\d{1,3})\b", f.read_text(encoding="utf-8")):
                assert m in permitidos_rgb, (f.name, m)
        if f.suffix == ".svg" and "estilo" not in f.parts and "kvantum" not in f.parts and "decoracion" not in f.parts and "global" not in f.parts:
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
        cp.read(GEN / "esquema" / f"{MARCA['id_esquema'][v]}.colors", encoding="utf-8")
        for g in ("Colors:View", "Colors:Window", "Colors:Button", "Colors:Selection", "Colors:Tooltip", "Colors:Complementary", "Colors:Header", "Colors:Header][Inactive"):
            assert g in cp, g
            for k in ("BackgroundNormal", "BackgroundAlternate", "ForegroundNormal", "ForegroundInactive", "ForegroundActive",
                      "ForegroundLink", "ForegroundVisited", "ForegroundNegative", "ForegroundNeutral", "ForegroundPositive", "DecorationFocus", "DecorationHover"):
                assert k in cp[g], (g, k)
        assert cp["General"]["ColorScheme"] == MARCA["id_esquema"][v]
        assert "WM" in cp and "KDE" in cp


def test_esquema_linea_base_solo_acento():
    """Mejora 1 (decisiones 4.5): Lliphi{Oscuro,Claro}.colors es WhiteSur{Dark,}.colors con solo el acento sustituido:
    cada clave cuyo valor en WhiteSur es uno de sus azules (o ForegroundLink en la selección) vale el token de su
    función; todas las demás líneas, incluidos [WM] y [ColorEffects:*], son idénticas a WhiteSur."""
    from nucleo import rgb, aplanar  # noqa: E402
    esquema = registro.codigo("esquema")
    for v, origen in (("oscuro", "WhiteSurDark.colors"), ("claro", "WhiteSur.colors")):
        t = {k: rgb(tok) for k, tok in aplanar(TOKENS["semanticos"][v]).items()}
        base = (RAIZ / "fuentes" / "base" / "WhiteSur-kde" / "color-schemes" / origen).read_text(encoding="utf-8").splitlines()
        base = [l for l in base if not l.startswith("Name[")]
        gen = (GEN / "esquema" / f"{MARCA['id_esquema'][v]}.colors").read_text(encoding="utf-8").splitlines()[1:]
        assert len(base) == len(gen), (v, len(base), len(gen))
        grupo, cambiadas = "", 0
        for b, g in zip(base, gen):
            if b.startswith("["):
                grupo = b[1:-1]
            if b.startswith(("ColorScheme=", "Name=")):
                continue
            m = esquema._LINEA.match(b) if grupo.startswith("Colors:") else None
            nombre = esquema.token_de(grupo, m.group(1), m.group(2)) if m else None
            if nombre is None:
                assert b == g, (v, grupo, b, g)
            else:
                assert g == f"{m.group(1)}={t[nombre]}{m.group(3)}", (v, grupo, b, g)
                cambiadas += 1
        assert 20 < cambiadas < 60, (v, cambiadas)
        if v == "oscuro":   # decisiones 4.12: en el oscuro no queda ningún azul de WhiteSur…
            assert not any(azul in l for l in gen for azul in esquema.AZULES_WHITESUR), v
        else:               # …y en el claro el acento ES el azul de WhiteSur
            assert t["acento.base"] == "49,91,239" and "DecorationFocus=49,91,239" in gen, v


def test_acento_por_variante():
    """Decisiones 4.12: rojo de Nothing en el oscuro, azul de WhiteSur en el claro; el estilo de Plasma los sigue (mejora 8)."""
    assert TOKENS["acento"] == {"claro": "azul-whitesur", "oscuro": "rojo"}
    assert TOKENS["semanticos"]["oscuro"]["acento"]["base"]["$value"]["hex"] == "#c93436"
    assert TOKENS["semanticos"]["claro"]["acento"]["base"]["$value"]["hex"] == "#315bef"
    oscuro = (GEN / "estilo" / f"{MARCA['id']}-oscuro" / "colors").read_text(encoding="utf-8")
    assert "49,91,239" not in oscuro and "201,52,54" in oscuro
    assert "49,91,239" in (GEN / "estilo" / f"{MARCA['id']}-claro" / "colors").read_text(encoding="utf-8")
    assert "#eb3131" in (GEN / "decoracion" / f"{MARCA['id']}-claro" / "close.svg").read_text(encoding="utf-8").lower()


def test_tema_global_estructura():
    for v in ("claro", "oscuro"):
        base = GEN / "global" / MARCA["id_global"][v]
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPackageStructure"] == "Plasma/LookAndFeel"
        assert meta["KPlugin"]["Id"] == MARCA["id_global"][v] == base.name
        assert meta["X-KDE-fallbackPackage"] == "org.kde.breeze.desktop"
        d = (base / "contents" / "defaults").read_text(encoding="utf-8")
        assert f"ColorScheme={MARCA['id_esquema'][v]}" in d and f"name={MARCA['id']}" in d
        assert "kvantum" in d.lower() and "ButtonsOnLeft=XIA" in d
        assert f"[kdeglobals][Icons]\nTheme={'Papirus' if v == 'claro' else 'Papirus-Dark'}" in d   # mejora 3
        deco = MARCA["id"] if v == "oscuro" else MARCA["id"] + "-claro"
        assert "library=org.kde.kwin.aurorae.v2" in d and f"theme=__aurorae__svg__{deco}" in d
        assert (base / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js").exists()
        assert (base / "contents" / "previews" / "preview.png").exists()


def test_estilo_plasma_derivado():
    """El estilo de Plasma deriva de WhiteSur-kde: dos variantes, con su `colors` (línea base, decisiones 4.4), GPL declarada, SVG válidos."""
    for v in ("claro", "oscuro"):
        base = GEN / "estilo" / f"{MARCA['id']}-{v}"
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPlugin"]["Id"] == base.name and meta["KPlugin"]["License"] == "GPL-3.0-or-later"
        assert (base / "colors").exists(), "línea base: el estilo lleva el `colors` de WhiteSur tal cual"
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


def _bloques_css(texto: str) -> dict[str, dict[str, str]]:
    """selector → {variable: valor} de un CSS plano (sin anidar), como el que genera el complemento obsidian."""
    sin_comentarios = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
    assert sin_comentarios.count("{") == sin_comentarios.count("}"), "llaves desparejas"
    return {sel.strip(): dict((k.strip(), v.strip()) for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", cuerpo))
            for sel, cuerpo in re.findall(r"([^{}]+)\{([^{}]*)\}", sin_comentarios)}


def test_obsidian_tema():
    """theme.css: las dos variantes de Obsidian 1.x desde los tokens, sin variables de Minimal, y cada color del maestro."""
    texto = (GEN / "obsidian" / "theme.css").read_text(encoding="utf-8")
    b = _bloques_css(texto)
    assert "GENERADO por herramientas/generar.py (complementos/obsidian" in texto
    assert "minimal" not in texto.lower() and "@settings" not in texto
    comun = b["body"]
    assert comun["--font-interface-theme"].startswith('"Inter"') and comun["--font-monospace-theme"].startswith('"JetBrainsMono Nerd Font"')
    assert comun["--radius-s"] == f"{TOKENS['radio']['control']['$value']['value']}px"
    requeridas = [f"--color-base-{n}" for n in ("00", "05", "10", "20", "25", "30", "35", "40", "50", "60", "70", "100")]
    requeridas += [f"--color-{c}{r}" for c in ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink") for r in ("", "-rgb")]
    requeridas += ["--accent-h", "--accent-s", "--accent-l", "--color-accent", "--interactive-accent", "--text-accent",
                   "--text-on-accent", "--text-error", "--text-warning", "--text-success", "--code-keyword", "--code-string",
                   "--code-function", "--code-comment", "--code-background"]
    hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values()
             if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    for v, selector in (("claro", ".theme-light"), ("oscuro", ".theme-dark")):
        x = b[selector]
        faltan = [k for k in requeridas if k not in x]
        assert not faltan, (v, faltan)
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        t, e = _terminal(v), _sintaxis_esperada(v)
        assert x["--color-base-00"] == sem["fondo.vista"] and x["--color-base-20"] == sem["fondo.ventana"]
        assert x["--color-base-100"] == sem["texto.normal"] and x["--color-base-70"] == sem["texto.secundario"]
        assert x["--color-accent"] == x["--interactive-accent"] == sem["acento.base"] and x["--text-accent"] == sem["enlace"]
        assert x["--color-red"] == t["color1"] and x["--color-blue"] == t["color4"] and x["--color-orange"] == sem["estado.advertencia"]
        assert x["--code-keyword"] == e["palabra-clave"] and x["--code-string"] == e["cadena"] and x["--code-comment"] == e["comentario"]
        for k, valor in x.items():
            if k.endswith("-rgb"):
                hex_ = x[k[:-4]] if k[:-4] in x else None
                if hex_:
                    assert valor == ", ".join(str(int(hex_[i:i + 2], 16)) for i in (1, 3, 5)), (v, k)
            elif valor.startswith("#"):
                assert valor.lower() in hexes, (v, k, valor)
    # los colores de Zotero solo aparecen como selector, nunca como valor
    zotero = {s: d for s, d in b.items() if s.startswith(".callout[data-callout-metadata=")}
    assert len(zotero) == 8 and all(d["--callout-color"].startswith("var(--color-") for d in zotero.values())
    assert '.callout[data-callout-metadata="#ffd400" i]' in zotero and zotero['.callout[data-callout-metadata="#ffd400" i]']["--callout-color"] == "var(--color-yellow)"


def test_decoracion_aurorae():
    """La decoración deriva de Nothing: dos variantes con marco, botones, rc y metadatos; GPL declarada."""
    for v, id_ in (("oscuro", MARCA["id"]), ("claro", f"{MARCA['id']}-claro")):
        base = GEN / "decoracion" / id_
        for req in ("decoration.svg", "close.svg", "maximize.svg", "minimize.svg", "restore.svg", f"{id_}rc", "metadata.json", "metadata.desktop"):
            assert (base / req).exists(), (v, req)
        meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPlugin"]["Id"] == id_ and meta["KPlugin"]["License"] == "GPL-3.0-or-later"
        rc = (base / f"{id_}rc").read_text(encoding="utf-8")
        assert re.search(r"^ActiveTextColor=\d+,\d+,\d+$", rc, re.M)
        assert re.search(r"^UseTextShadow=false$", rc, re.M), (v, "mejora 4: título sin sombra")
        for svg in base.glob("*.svg"):
            ET.parse(svg)
            assert "#9cdde4" not in svg.read_text(encoding="utf-8").lower(), (v, svg.name, "mejora 4: sin el cian de Nothing")
    assert (RAIZ / "fuentes" / "base" / "Nothing-aurorae" / "ORIGEN.md").exists()

def test_libreoffice_esquemas():
    """Fragmentos .xcu y extensión .oxt: estructura, 91 entradas por esquema, cada Color decimal es un hex de los tokens."""
    import zipfile
    VISIBLES, entradas = registro.codigo("libreoffice").VISIBLES, registro.codigo("libreoffice").entradas
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
        assert set(z.namelist()) == {"META-INF/manifest.xml", "description.xml", "descripcion.txt", f"{MARCA['id']}.xcu", "paletas.xcu",
                                     f"palette/{MARCA['id']}-claro.soc", f"palette/{MARCA['id']}-oscuro.soc"}
        assert all(zi.date_time == (1980, 1, 1, 0, 0, 0) for zi in z.infolist()), "zip no reproducible"
        manifest = ET.fromstring(z.read("META-INF/manifest.xml"))
        entradas_manifest = manifest.findall("{http://openoffice.org/2001/manifest}file-entry")
        assert all(x.get("{http://openoffice.org/2001/manifest}media-type") == "application/vnd.sun.star.configuration-data" for x in entradas_manifest)
        assert [x.get("{http://openoffice.org/2001/manifest}full-path") for x in entradas_manifest] == [f"{MARCA['id']}.xcu", "paletas.xcu"]
        rutas = ET.fromstring(z.read("paletas.xcu"))
        assert rutas.get("{http://openoffice.org/2001/registry}name") == "Paths"
        assert "%origin%/palette" in {n.get("{http://openoffice.org/2001/registry}name") for n in rutas.iter("node")}
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
        for v in ("claro", "oscuro"):
            assert z.read(f"palette/{MARCA['id']}-{v}.soc") == (base / f"{MARCA['id']}-{v}.soc").read_bytes()


def test_libreoffice_paletas():
    """Paletas .soc (como la de Dracula): XML válido, colores del maestro sin repetir, acento, estados y los dieciséis ANSI."""
    hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    office, draw = "{http://openoffice.org/2000/office}", "{http://openoffice.org/2000/drawing}"
    for v in ("claro", "oscuro"):
        raiz = ET.parse(GEN / "libreoffice" / f"{MARCA['id']}-{v}.soc").getroot()
        assert raiz.tag == f"{office}color-table"
        colores = [(c.get(f"{draw}name"), c.get(f"{draw}color")) for c in raiz.findall(f"{draw}color")]
        nombres, valores = [n for n, _ in colores], [h for _, h in colores]
        assert len(set(nombres)) == len(nombres) and len(set(valores)) == len(valores), v
        assert all(h in hexes for h in valores), v
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        assert dict(colores)["Acento"] == sem["acento.base"] and dict(colores)["Texto"] == sem["texto.normal"]
        assert set(_terminal(v)[f"color{i}"] for i in range(16)) <= set(valores), v
        assert 28 <= len(colores) <= 36, (v, len(colores))


def test_fondo_paquete():
    base = GEN / "fondos" / MARCA["id_fondo"]
    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    assert meta["KPlugin"]["Id"] == MARCA["id_fondo"]
    assert set(meta["X-KDE-PlasmaImageWallpaper-AccentColor"]) == {"Light", "Dark"}
    TAMANOS = registro.codigo("fondos").TAMANOS
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
    comp = correr("herramientas/instalar.py", "comprobar", env=env)
    assert comp.returncode == 0 and "FALTA" not in comp.stdout, comp.stdout
    # manifiesto de 0.3.0: Kvantum anotado como `…/.local/share/../../.config/Kvantum/…`; reinstalar no es conflicto
    datos = json.loads(manifiesto.read_text())
    kv = str(tmp_path / ".config/Kvantum" / MARCA["id_esquema"]["oscuro"])
    datos["rutas"] = {(str(tmp_path / ".local/share/../../.config/Kvantum" / MARCA["id_esquema"]["oscuro"]) if k == kv else k): v for k, v in datos["rutas"].items()}
    manifiesto.write_text(json.dumps(datos))
    (Path(kv) / "otro.txt").write_text("x")
    assert correr("herramientas/instalar.py", "--aplicar", "--modulos", "kvantum", env=env).returncode == 0
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


def test_perfil_konsole_toma_el_esquema(tmp_path, monkeypatch):
    """Mejora 5: el perfil por defecto de Konsole toma el esquema de Lliphi sin perder la fuente ni el enlace de dotfiles."""
    instalar = registro.codigo("konsole", "aplicar")
    real = tmp_path / "dotfiles" / "yo.profile"
    real.parent.mkdir(parents=True)
    real.write_text("[Appearance]\nColorScheme=Breeze\nFont=FiraCode Nerd Font,10\n\n[General]\nName=yo\n", encoding="utf-8")
    (tmp_path / "data" / "konsole").mkdir(parents=True)
    enlace = tmp_path / "data" / "konsole" / "yo.profile"
    enlace.symlink_to(real)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "konsolerc").write_text("[Desktop Entry]\nDefaultProfile=yo.profile\n", encoding="utf-8")
    perfil = instalar.perfil_konsole(tmp_path / "data", tmp_path / "config")
    assert perfil == enlace
    instalar.fijar_esquema_konsole(perfil, "Lliphi Oscuro")
    texto = real.read_text(encoding="utf-8")
    assert enlace.is_symlink()
    assert "ColorScheme=Lliphi Oscuro" in texto and "ColorScheme=Breeze" not in texto
    assert "Font=FiraCode Nerd Font,10" in texto and "Name=yo" in texto
    # un perfil sin [Appearance] la gana al final
    real.write_text("[General]\nName=yo\n", encoding="utf-8")
    instalar.fijar_esquema_konsole(perfil, "Lliphi Claro")
    assert real.read_text(encoding="utf-8").rstrip().endswith("[Appearance]\nColorScheme=Lliphi Claro")
    # mejora 9: con fuente, cambia Font y conserva lo demás
    real.write_text("[Appearance]\nColorScheme=Breeze\nFont=FiraCode Nerd Font,10\n\n[General]\nName=yo\n", encoding="utf-8")
    instalar.fijar_esquema_konsole(perfil, "Lliphi Oscuro", instalar.FUENTE_KONSOLE)
    texto = real.read_text(encoding="utf-8")
    assert f"Font={instalar.FUENTE_KONSOLE}" in texto and "FiraCode" not in texto and texto.count("ColorScheme=") == 1 and "Name=yo" in texto


def test_pantallas_carga_y_salida():
    """Mejora 6: splash y logout derivados de WhiteSur-dark, sin el logotipo de Apple, con el fondo dentro del paquete."""
    for v in ("claro", "oscuro"):
        base = GEN / "global" / MARCA["id_global"][v] / "contents"
        splash = (base / "splash" / "Splash.qml").read_text(encoding="utf-8")
        assert "logo.svg" not in splash and 'font.family: "Inter"' in splash and MARCA["nombre"] in splash
        assert not (base / "splash" / "images" / "logo.svg").exists()
        assert (base / "splash" / "images" / "background.png").exists() and (base / "splash" / "images" / "loading-00.svg").exists()
        salida = (base / "logout" / "Logout.qml").read_text(encoding="utf-8")
        assert 'source: "background.png"' in salida and "wallpapers/WhiteSur" not in salida
        for f in ("background.png", "LogoutButton.qml", "timer.js"):
            assert (base / "logout" / f).exists(), (v, f)
        assert f"Theme={MARCA['id_global'][v]}" in (base / "defaults").read_text(encoding="utf-8")


def test_inicio_de_sesion_sddm():
    """Mejora 7: tema SDDM derivado de WhiteSur-dark con fondo de Lliphi, Inter, foco en el acento y sin logotipo."""
    base = GEN / "sddm" / MARCA["id"]
    for f in ("Main.qml", "Login.qml", "Input.qml", "Background.qml", "metadata.desktop", "theme.conf", "background.png", "preview.png"):
        assert (base / f).exists(), f
    conf = (base / "theme.conf").read_text(encoding="utf-8")
    assert "font=Inter" in conf and "showlogo=hidden" in conf and "background=background.png" in conf
    meta = (base / "metadata.desktop").read_text(encoding="utf-8")
    assert f"Name={MARCA['nombre']}" in meta and f"Theme-Id={MARCA['id']}" in meta and "QtVersion=6" in meta
    assert "Kirigami.Theme.highlightColor" in (base / "Main.qml").read_text(encoding="utf-8")
    assert "border.color" in (base / "Input.qml").read_text(encoding="utf-8")
    assert "defaultFont" not in (base / "Main.qml").read_text(encoding="utf-8"), "Kirigami.Theme.defaultFont es de solo lectura: rompe el tema"
    for orden in (("herramientas/instalar_sddm.py",), ("herramientas/instalar.py", "sddm")):   # el atajo de 0.3.0 y la orden nueva
        r = correr(*orden)
        assert r.returncode in (0, 3) and "pkexec" not in r.stderr and "Traceback" not in r.stderr, r.stderr


def test_variante_clara_validada():
    """Mejora 10 (decisiones 4.15–4.16): carpetas por variante sin tocar Papirus, fondo claro fijado y bloqueo oscuro."""
    for v, iconos in (("oscuro", "Papirus-Dark-Lliphi"), ("claro", "Papirus")):
        defaults = (GEN / "global" / MARCA["id_global"][v] / "contents" / "defaults").read_text(encoding="utf-8")
        assert f"Theme={iconos}" in defaults, v
    dep = registro.codigo("iconos-cursores", "externas")
    assert dep.SUPERPUESTO["id"] == "Papirus-Dark-Lliphi" and dep.COLOR_ORIGINAL == "blue"
    fondo = registro.modulo("fondos").archivo("aplicar.py").read_text(encoding="utf-8")
    bloqueo = registro.modulo("carga-bloqueo").archivo("aplicar.py").read_text(encoding="utf-8")
    assert '"images" / "3840x2160.png"' in fondo and '"images_dark" / "3840x2160.png"' in bloqueo and '"kscreenlockerrc"' in bloqueo


# ---------------------------------------------------------------- arquitectura modular

SEIS = {"esquema": "paquete", "estilo": "paquete", "decoracion": "paquete", "iconos-cursores": "externo",
        "carga-bloqueo": "componente", "disposicion": "componente"}


def test_registro_tema_global_y_seis_modulos():
    """Un tema global integrador, los seis módulos del encargo con su clase y los complementos que ya existían."""
    roles = {m.id: (m.rol, m.clase) for m in registro.todos()}
    assert roles["global"] == ("global", "paquete")
    assert {i: c for i, (r, c) in roles.items() if r == "modulo"} == SEIS
    assert {i for i, (r, _) in roles.items() if r == "complemento"} == {"fondos", "kvantum", "konsole", "terminales", "editores", "libreoffice", "sddm", "obsidian"}
    g = registro.modulo("global")
    assert set(g.dependencias("integra")) == {"carga-bloqueo", "disposicion"}
    assert set(SEIS) <= set(g.dependencias("integra") + g.dependencias("referencia"))
    for m in registro.todos():
        assert (m.carpeta / "README.md").is_file() and (m.carpeta / "INSTALL.md").is_file(), m.id
    # lo generado está por módulo: solo los paquetes tienen carpeta
    assert {p.name for p in GEN.iterdir()} == set(registro.ids("paquete"))


def test_validar_en_verde():
    r = correr("herramientas/generar.py", "validar")
    assert r.returncode == 0, r.stdout[-3000:]


def test_validacion_detecta_componente_faltante(tmp_path, monkeypatch):
    """Si el tema global nombra un esquema que no se genera, o falta un archivo de un componente, la validación falla."""
    from nucleo import validacion
    copia = tmp_path / "generado"
    shutil.copytree(GEN, copia)
    (copia / "esquema" / f"{MARCA['id_esquema']['oscuro']}.colors").unlink()
    (copia / "global" / MARCA["id_global"]["claro"] / "contents" / "splash" / "Splash.qml").unlink()
    monkeypatch.setattr(registro, "GENERADO", copia)
    inf = validacion.Informe()
    validacion.integracion(inf, MARCA)
    texto = "\n".join(inf.errores)
    assert "ColorScheme=" in texto and "esquema" in texto, texto
    assert "Splash.qml" in texto, texto


def test_defaults_compuestos_por_los_modulos():
    """Cada clave de `contents/defaults` tiene un solo dueño y el tema global no escribe identificadores ajenos."""
    from nucleo import validacion
    glob = registro.codigo("global")
    for v in ("claro", "oscuro"):
        d = validacion.defaults(GEN / "global" / MARCA["id_global"][v] / "contents" / "defaults")
        esperado: dict = {}
        for id_ in glob.aportes():
            for grupo, claves in registro.codigo(id_).valores(MARCA, v).items():
                for k, x in claves.items():
                    assert k not in esperado.setdefault(grupo, {}), (grupo, k)
                    esperado[grupo][k] = x
        assert d == esperado, v
    fuente = registro.modulo("global").archivo("construir.py").read_text(encoding="utf-8")
    for ajeno in ("Papirus", "WhiteSur-cursors", "kvantum", "aurorae.v2", "__aurorae__", "LayoutName", MARCA["id_fondo"]):
        assert ajeno not in fuente, ajeno


def test_componentes_dentro_del_tema_global():
    """La pantalla de carga, la de salida y la disposición viven dentro del paquete del tema global (donde Plasma las
    lee) y en ningún otro sitio de generado/; el bloqueo no lleva QML propio (en Plasma 6.6 es del paquete de shell)."""
    for id_ in ("carga-bloqueo", "disposicion"):
        m = registro.modulo(id_)
        assert m.datos["integracion"]["en"] == "global" and not (GEN / id_).exists()
        for v in ("claro", "oscuro"):
            for rel in m.datos["integracion"]["rutas"]:
                assert (GEN / "global" / MARCA["id_global"][v] / rel).is_file(), (id_, v, rel)
    for v in ("claro", "oscuro"):
        assert not (GEN / "global" / MARCA["id_global"][v] / "contents" / "lockscreen").exists()
    js = (GEN / "global" / MARCA["id_global"]["oscuro"] / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js").read_text(encoding="utf-8")
    assert "@NOMBRE@" not in js and "@FONDO@" not in js and f"/{MARCA['id_fondo']}" in js
    # validacion.md §9: el fondo por la carpeta de fondos (el tipo de userDataPath va primero) y un modo de ocultación que
    # Plasma 6.6 entiende (normal, autohide, dodgewindows, windowsgobelow; «windowscover» ya no existe)
    assert 'userDataPath("data", "wallpapers")' in js and 'userDataPath("wallpapers")' not in js
    assert set(re.findall(r'\.hiding = "(\w+)"', js)) <= {"normal", "none", "autohide", "dodgewindows", "windowsgobelow"}


def test_codigo_solo_usa_lo_declarado():
    """Un módulo solo carga el código de otro si lo declara (la validación lo comprueba; aquí, el orden de construcción)."""
    orden = registro.orden_de_construccion(registro.ids())
    for m in registro.todos():
        for d in m.dependencias("construccion") + m.dependencias("integra"):
            assert orden.index(d) < orden.index(m.id), (d, m.id)


@pytest.mark.skipif(shutil.which("plasmashell") is None, reason="sin Plasma")
def test_kvantum_en_xdg_config_home(tmp_path: Path):
    """Kvantum va a $XDG_CONFIG_HOME aunque no sea ~/.config (en 0.3.0 se calculaba desde $XDG_DATA_HOME/../..)."""
    env = _entorno(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path / "otra-config")
    r = correr("herramientas/instalar.py", "--modulos", "kvantum", env=env)
    assert r.returncode == 0 and f"→ {tmp_path / 'otra-config' / 'Kvantum' / MARCA['id_esquema']['claro']}" in r.stdout, r.stdout


def test_atajos_de_compatibilidad():
    """Las órdenes documentadas en 0.3.0 siguen valiendo."""
    r = correr("herramientas/dependencias.py", "--help")
    assert "Traceback" not in r.stderr
    assert correr("herramientas/instalar.py", "--help").returncode == 0
    assert "módulos desconocidos" in correr("herramientas/instalar.py", "--modulos", "nada").stdout


def test_orden_de_aplicacion():
    """Con --aplicar-tema se aplica primero el tema global y después cada módulo que tenga aplicar(); los componentes y
    externos del tema global entran siempre, aunque no se pidan (no tienen archivos propios)."""
    from nucleo import instalacion
    orden = instalacion.a_aplicar(["esquema"])
    assert orden[0] == "global" and {"iconos-cursores", "carga-bloqueo"} <= set(orden) and "disposicion" not in orden
    assert "konsole" not in orden and "konsole" in instalacion.a_aplicar(registro.ids())
    for id_ in orden:
        assert callable(registro.codigo(id_, "aplicar").aplicar), id_
