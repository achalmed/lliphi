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
    assert datos["variantes"]["oscuro"]["semanticos"]["acento.base"]["hex"] == "#e22529"   # el rojo de Nothing (decisiones 4.25)
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
    assert registro.codigo("iconos-cursores").ICONOS == {"claro": "Colloid-Grey-Light", "oscuro": "Colloid-Grey-Dark"}
    assert registro.codigo("iconos-cursores").RESERVA["oscuro"] == "Papirus-Dark-Lliphi"
    r = correr("herramientas/generar.py", "validar", "--json")
    assert r.returncode == 0 and json.loads(r.stdout)["valido"]
    datos = json.loads(correr("herramientas/generar.py", "verificar", "--json").stdout)
    assert {"archivos", "al_dia", "diferencias"} <= set(datos)
    env = {**os.environ, "XDG_STATE_HOME": str(tmp_path / "state")}
    assert json.loads(correr("herramientas/instalar.py", "estado", "--json", env=env).stdout)["instalado"] is False


def test_cabecera_en_una_sola_banda():
    """Mejora 12: en el oscuro, la barra de herramientas de Kvantum opaca en el color de la ventana (el del título de la
    decoración) y la ventana translúcida (la vista y la terminal integrada conservan su transparencia); el claro, como
    estaba (barra de WhiteSur)."""
    oscuro = GEN / "kvantum" / MARCA["nombre"]
    kv = (oscuro / f"{MARCA['nombre']}Dark.kvconfig").read_text(encoding="utf-8")
    assert re.search(r"^translucent_windows=true$", kv, re.M) and re.search(r"^transparent_dolphin_view=true$", kv, re.M)
    svg = (oscuro / f"{MARCA['nombre']}Dark.svg").read_text(encoding="utf-8")
    ventana = TOKENS["semanticos"]["oscuro"]["fondo"]["ventana"]["$value"]["hex"]
    piezas = re.findall(r'<[^<>]*\bid="(toolbar-normal(?:-inactive)?(?:-(?:top|left|right|topleft|topright))?)"[^<>]*?fill:(#[0-9a-fA-F]{6})', svg)
    assert piezas and all(color.lower() == ventana for _id, color in piezas), piezas
    acento = TOKENS["semanticos"]["oscuro"]["acento"]["base"]["$value"]["hex"]
    menu = re.findall(r'<[^<>]*\bid="menubaritem-(?:pressed|toggled)[^"]*"[^<>]*?fill:(#[0-9a-fA-F]{6})', svg)
    assert menu and {c.lower() for c in menu} == {acento}          # decisiones 4.20: como el elegido dentro del menú
    assert re.search(rf"^highlight\.color={acento}$", kv, re.M)
    claro = (GEN / "kvantum" / MARCA["nombre"] / f"{MARCA['nombre']}.kvconfig").read_text(encoding="utf-8")
    assert re.search(r"^translucent_windows=true$", claro, re.M)
    # decisiones 4.21: la barra del claro también en su fondo.ventana; y ningún azul de WhiteSur fuera de los tokens
    svg_claro = (GEN / "kvantum" / MARCA["nombre"] / f"{MARCA['nombre']}.svg").read_text(encoding="utf-8")
    ventana_c = TOKENS["semanticos"]["claro"]["fondo"]["ventana"]["$value"]["hex"]
    piezas_c = re.findall(r'<[^<>]*\bid="(toolbar-normal(?:-inactive)?(?:-(?:top|left|right|topleft|topright))?)"[^<>]*?fill:(#[0-9a-fA-F]{6})', svg_claro)
    assert piezas_c and all(c.lower() == ventana_c for _i, c in piezas_c), piezas_c
    import colorsys
    for v, texto in (("oscuro", svg), ("claro", svg_claro)):
        propios = {x["$value"]["hex"].lower() for x in _tokens_planos(TOKENS["semanticos"][v]).values()}
        for h in {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", texto)} - propios:
            tono, luz, sat = colorsys.rgb_to_hls(*(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)))
            assert not (sat >= 0.3 and 0.5 < tono < 0.75 and luz <= 0.9), (v, h)


def test_dock_de_lliphi():
    """Mejora 11: fondo de paneles del oscuro opaco en el gris de la ventana; mosaicos de tareas y paginador de Lliphi
    con las clases de color de Plasma (siguen el acento); el dock lleva el paginador de números."""
    est = registro.codigo("estilo").ajustes()
    for v in ("claro", "oscuro"):
        carpeta = GEN / "estilo" / f"{MARCA['id']}-{v}" / "widgets"
        tareas = (carpeta / "tasks.svg").read_text(encoding="utf-8")
        ET.fromstring(tareas)
        for estado in est["tareas"]["estados"]:
            for pieza in ("top", "center", "bottom"):
                assert tareas.count(f'id="{estado}-{pieza}"') == 1, (v, estado, pieza)
        assert 'id="group-expander-top"' in tareas and "ColorScheme-Highlight" in tareas
        paginador = (carpeta / "pager.svg").read_text(encoding="utf-8")
        ET.fromstring(paginador)
        assert all(f'id="{e}-{p}"' in paginador for e in ("normal", "hover", "active") for p in ("topleft", "center", "bottomright"))
    panel = (GEN / "estilo" / f"{MARCA['id']}-oscuro" / "widgets" / "panel-background.svg").read_text(encoding="utf-8")
    fondo = TOKENS["semanticos"]["oscuro"]["fondo"]["ventana"]["$value"]["hex"]
    assert "opacity:0.45;fill:#000000" not in panel and f"opacity:{est['panel']['oscuro']['opacidad']};fill:{fondo}" in panel
    ET.fromstring(panel)
    assert 'id="shadow-' not in panel and 'id="mask-topleft"' in panel and 'id="topleft"' in panel   # sin sombra, con máscara
    claro = (GEN / "estilo" / f"{MARCA['id']}-claro" / "widgets" / "panel-background.svg").read_text(encoding="utf-8")
    # el claro, igual (decisiones 4.21), con su panel claro (4.32, base WhiteSur-alt): el gris de su propia ventana
    fondo_claro = TOKENS["semanticos"]["claro"]["fondo"]["ventana"]["$value"]["hex"]
    assert f"opacity:{est['panel']['claro']['opacidad']};fill:{fondo_claro}" in claro and 'id="shadow-' not in claro
    assert "opacity:0.45;fill:#ffffff" not in claro
    dock = registro.codigo("disposicion").paneles()[1]
    pager = [w for w in dock["widgets"] if w["tipo"] == "org.kde.plasma.pager"]
    assert pager and pager[0]["config"]["General"]["displayedText"] == "0"


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
    # la paleta de terminal de Konsole (base Nothing, 4.29 y 4.30), que llevan también las terminales y los editores
    hexes_konsole = {h for v in ("claro", "oscuro") for h in registro.codigo("konsole").ansi(TOKENS, v).values()}
    for f in GEN.rglob("*"):
        # línea base (decisiones 4.4 y 4.5): LliphiOscuro/LliphiClaro.colors son WhiteSur-kde con solo el acento de los tokens
        # (lo verifica test_esquema_linea_base_solo_acento) y el `colors` del estilo de Plasma es copia de WhiteSur-kde;
        # solo las variantes `-tokens` y lo demás salen por entero del maestro; Konsole, de su base Nothing
        copia_whitesur = f.suffix == ".colors" and not f.stem.endswith("-tokens") or (f.name == "colors" and "estilo" in f.parts)
        copia_whitesur = copia_whitesur or f.suffix == ".colorscheme"     # Konsole: base Nothing (4.29), test_konsole_sobre_nothing
        if f.suffix in (".colors", ".colorscheme", "") and f.is_file() and f.name != "defaults" and "decoracion" not in f.parts and not copia_whitesur:
            for m in re.findall(r"=(\d{1,3},\d{1,3},\d{1,3})\b", f.read_text(encoding="utf-8")):
                assert m in permitidos_rgb, (f.name, m)
        if f.suffix == ".svg" and "estilo" not in f.parts and "kvantum" not in f.parts and "decoracion" not in f.parts and "global" not in f.parts:
            for h in re.findall(r"#[0-9a-fA-F]{6}\b", f.read_text(encoding="utf-8")):
                assert h.lower() in hexes | {"#000000"}, (f.name, h)
        if f.suffix in (".toml", ".conf", ".json"):
            # los editores admiten #rrggbbaa: el color base debe ser del maestro; el alfa es libre
            for h in re.findall(r"#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?\b", f.read_text(encoding="utf-8")):
                assert "#" + h.lower() in hexes | hexes_konsole, (f.name, h)


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


def test_fondos_firmados():
    """Decisiones 4.25: Forma y Relámpago con su versión firmada, que difiere de la sin firma solo donde va la firma, y
    la tira de Relámpago ordenada por luz."""
    fondos = registro.codigo("fondos")
    PIL = pytest.importorskip("PIL.Image")
    for id_ in (fondos.id_forma(MARCA), fondos.id_relampago(MARCA)):
        meta = json.loads((GEN / "fondos" / f"{id_}.firmado" / "metadata.json").read_text(encoding="utf-8"))
        assert meta["KPlugin"]["Name"].endswith(MARCA["firma"])
        sin = PIL.open(GEN / "fondos" / id_ / "contents" / "images_dark" / "1920x1080.jpg").convert("L")
        con = PIL.open(GEN / "fondos" / f"{id_}.firmado" / "contents" / "images_dark" / "1920x1080.jpg").convert("L")
        import PIL.ImageChops as ch
        caja = ch.difference(sin, con).point(lambda v: 255 if v > 24 else 0).getbbox()
        assert caja is not None and (caja[3] - caja[1]) < 1080 * 0.06, (id_, caja)   # una franja baja y estrecha
    pa = fondos.relampago_paleta(TOKENS, "oscuro")
    acentos = sorted([pa["fuerte"], pa["acento"], pa["suave"]], key=sum)
    assert acentos[0] == pa["acento"] and acentos[-1] == pa["fuerte"]
    assert TOKENS["semanticos"]["oscuro"]["acento"]["base"]["$value"]["hex"] == "#e22529"   # el rojo de Nothing (decisiones 4.25)
    assert TOKENS["semanticos"]["claro"]["acento"]["base"]["$value"]["hex"] == "#315bef"
    oscuro = (GEN / "estilo" / f"{MARCA['id']}-oscuro" / "colors").read_text(encoding="utf-8")
    assert "49,91,239" not in oscuro and "226,37,41" in oscuro
    assert "49,91,239" in (GEN / "estilo" / f"{MARCA['id']}-claro" / "colors").read_text(encoding="utf-8")
    # cerrar: rojo de Nothing en el oscuro; en el claro, el acento azul (decisiones 4.33; hasta entonces seguía rojo, 4.12)
    cerrar_claro = (GEN / "decoracion" / f"{MARCA['id']}-claro" / "close.svg").read_text(encoding="utf-8").lower()
    assert "#eb3131" not in cerrar_claro and "#315bef" in cerrar_claro
    assert "#eb3131" in (GEN / "decoracion" / MARCA["id"] / "close.svg").read_text(encoding="utf-8").lower()


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
        assert f"[kdeglobals][Icons]\nTheme={'Colloid-Grey-Light' if v == 'claro' else 'Colloid-Grey-Dark'}-Lliphi" in d   # 4.22 y 4.35
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
    """Un solo tema de Kvantum con las dos variantes (decisiones 4.19): Kvantum busca <tema>Dark con kvantum-dark, y el
    tema global declara kvantum-dark en el oscuro y kvantum en el claro."""
    d = GEN / "kvantum" / MARCA["nombre"]
    estilos = {v: registro.codigo("kvantum").valores(MARCA, v)["kdeglobals][KDE"]["widgetStyle"] for v in ("claro", "oscuro")}
    assert estilos == {"claro": "kvantum", "oscuro": "kvantum-dark"}
    for v, archivo in (("claro", MARCA["nombre"]), ("oscuro", f"{MARCA['nombre']}Dark")):
        kv = (d / f"{archivo}.kvconfig").read_text(encoding="utf-8")
        hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}
        for clave in ("window.color", "highlight.color", "text.color"):
            m = re.search(rf"^{re.escape(clave)}=(#[0-9a-f]{{6}})", kv, re.M)
            assert m and m.group(1).lower() in hexes, (v, clave)
        ET.parse(d / f"{archivo}.svg")

def test_konsole_16_colores():
    for v in ("claro", "oscuro"):
        cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
        cp.read(GEN / "konsole" / f"{MARCA['nombre_esquema'][v]}.colorscheme", encoding="utf-8")
        for i in range(8):
            assert f"Color{i}" in cp and f"Color{i}Intense" in cp and f"Color{i}Faint" in cp
        assert cp["General"]["Description"] == MARCA["nombre_esquema"][v]



def test_konsole_sobre_nothing():
    """Decisiones 4.29: el oscuro es el esquema «Nothing» tal cual (solo cambian nombre, opacidad y la aleatoriedad);
    el claro es su espejo: el acento azul en el `Color4`, el azul de Nothing en el `Color1`, su rojo en el `Color0`,
    y cada color normal ≥ 4,5:1 sobre el fondo claro."""
    konsole = registro.codigo("konsole")

    def leer(ruta):
        cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
        cp.read(ruta, encoding="utf-8")
        return cp
    base = leer(RAIZ / "fuentes" / "base" / "Nothing-konsole" / "Nothing.colorscheme")
    oscuro = leer(GEN / "konsole" / f"{MARCA['nombre_esquema']['oscuro']}.colorscheme")
    for g in base.sections():
        if g != "General":
            assert oscuro[g]["Color"] == base[g]["Color"], g
    assert oscuro["General"]["Opacity"] == str(TOKENS["efectos"]["opacidad-konsole"]["$value"])
    claro = leer(GEN / "konsole" / f"{MARCA['nombre_esquema']['claro']}.colorscheme")
    tupla = lambda texto: tuple(int(x) for x in texto.split(","))
    prim = {k: ",".join(str(int(x["$value"]["hex"][i:i + 2], 16)) for i in (1, 3, 5)) for k, x in TOKENS["primitivas"]["claro"].items()}
    assert claro["Background"]["Color"] == prim["neutro-1"] and claro["Foreground"]["Color"] == prim["neutro-7"]
    assert [claro[f"Color4{s}"]["Color"] for s in ("", "Faint", "Intense")] == [prim["acento"], prim["acento-suave"], prim["acento-texto"]]
    fondo = tupla(claro["Background"]["Color"])
    for i in range(8):
        assert konsole.contraste(tupla(claro[f"Color{i}"]["Color"]), fondo) >= 4.5, i
    for i, j in ((0, 4), (1, 0), (5, 5)):                                    # el espejo conserva el matiz de Nothing
        h_claro, h_base = konsole.a_oklch(tupla(claro[f"Color{i}"]["Color"]))[2], konsole.a_oklch(tupla(base[f"Color{j}"]["Color"]))[2]
        assert abs((h_claro - h_base + 180) % 360 - 180) < 6, (i, h_claro, h_base)


def _terminal(variante: str) -> dict[str, str]:
    return {k: v["$value"]["hex"] for k, v in TOKENS["terminal"][variante].items()}


def test_terminales_alacritty_kitty():
    """Decisiones 4.30: Alacritty y Kitty llevan la paleta de Konsole (fondo, textos y los dieciséis ANSI)."""
    import tomllib
    ansi = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    for v in ("claro", "oscuro"):
        t = registro.codigo("konsole").ansi(TOKENS, v)
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
        k = registro.codigo("konsole").ansi(TOKENS, v)                       # la terminal integrada, la de Konsole (4.30)
        assert tema["colors"]["terminal.ansiRed"] == k["color1"] and tema["colors"]["terminal.ansiBrightBlue"] == k["color12"]
        assert tema["colors"]["terminal.background"] == _terminal(v)["fondo"]
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
        assert st["editor.background"] == e["fondo"] and st["text"] == e["texto"]
        assert st["terminal.ansi.red"] == registro.codigo("konsole").ansi(TOKENS, v)["color1"]
        for papel, clave in (("palabra-clave", "keyword"), ("cadena", "string"), ("numero", "number"), ("funcion", "function"), ("comentario", "comment")):
            assert st["syntax"][clave]["color"] == e[papel], (v, clave)
        assert st["players"] and {"cursor", "background", "selection"} <= set(st["players"][0])


def _contraste(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


# las claves de Positron 2026.06 cuyo valor por omisión es un color fijo suyo (decisiones 5.4): todas deben estar
POSITRON_FIJAS = (
    "positronSplitterExpandCollapseButton.foreground", "positronToolTip.background", "positronToolTip.border",
    "positronActionBar.separator", "positronActionBar.textInputBackground", "positronActionBar.textInputBorder",
    "positronActionBar.textInputSelectionForeground", "positronActionBar.textInputSelectionBackground",
    "positronModalDialog.separator", "positronModalDialog.textInputBackground", "positronModalDialog.textInputBorder",
    "positronModalDialog.textInputSelectionForeground", "positronModalDialog.textInputSelectionBackground",
    "positronModalDialog.checkboxBackground", "positronModalDialog.checkboxForeground", "positronModalDialog.checkboxBorder",
    "positronConsole.traceBackground", "positronRuntime.stateIconActive", "positronRuntime.stateIconDisconnected",
    "positronRuntime.stateIconIdle", "positronDataGrid.cursorBorder", "positronDataGrid.selectionBorder",
    "positronDataGrid.selectionInnerBorder", "positronDataGrid.selectionBackground",
    "positronDataExplorer.invalidFilterBackground", "positronDataExplorer.statusIndicatorComputing",
    "positronDataExplorer.statusIndicatorDisconnected", "positronDataExplorer.columnNullPercentGraphBackgroundFill",
    "positronDataExplorer.columnNullPercentGraphBackgroundStroke", "positronDataExplorer.columnNullPercentGraphIndicatorFill",
    "positronDataExplorer.sparklineAxis", "positronDataExplorer.sparklineFill", "positronDataExplorer.sparklineHover",
    "positronDataExplorer.sparklineStroke", "positronWelcome.foreground", "positronWelcome.secondaryForeground",
    "positronNotebook.cellFooterForeground", "tree.tableColumnsBorder")


def test_positron_entero():
    """Decisiones 5.4: Positron no pinta nada con sus colores propios; la consola lleva el fondo de la terminal integrada
    y los ANSI de Konsole, legibles (≥ 4,5:1 los colores 1–7) sobre ese fondo."""
    for v in ("claro", "oscuro"):
        c = json.loads((GEN / "editores" / "vscode" / MARCA["id"] / "themes" / f"{MARCA['id']}-{v}-color-theme.json").read_text(encoding="utf-8"))["colors"]
        faltan = [k for k in POSITRON_FIJAS if k not in c]
        assert not faltan, (v, faltan)
        k = registro.codigo("konsole").ansi(TOKENS, v)
        assert c["positronConsole.background"] == c["terminal.background"] and c["positronConsole.ansiRed"] == k["color1"]
        assert c["positronConsole.ansiBrightWhite"] == k["color15"]
        for i, n in enumerate(("Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"), start=1):
            assert _contraste(c[f"positronConsole.ansi{n}"], c["positronConsole.background"]) >= 4.5, (v, n)
        assert _contraste(c["positronWelcome.foreground"], c["editor.background"]) >= 4.5, v


ALFAS = ("1a", "1f", "26", "33", "40", "55", "66")


def _permitidos(v: str, fondo: str) -> set[str]:
    """Los colores que puede llevar un tema de editor de la variante `v` con fondo `fondo`: los del maestro, los de
    Konsole y cualquiera de ellos con un alfa de los editores compuesto sobre el fondo (`editores.sobre`)."""
    base = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    base |= set(registro.codigo("konsole").ansi(TOKENS, v).values())
    sobre = registro.codigo("editores").sobre
    return base | {sobre(c, fondo, a) for c in base for a in ALFAS}


def test_kate_temas():
    """Decisiones 5.5: dos temas de KSyntaxHighlighting con la sintaxis de los editores; su fondo y su selección son los
    de la paleta que Kvantum da a las aplicaciones, para que Kate (themeForPalette) elija solo el de la variante; texto
    legible."""
    for v in ("claro", "oscuro"):
        tema = json.loads((GEN / "kate" / f"{MARCA['id']}-{v}.theme").read_text(encoding="utf-8"))
        qt = registro.codigo("kvantum").paleta_qt(TOKENS, v)
        c, e = tema["editor-colors"], _sintaxis_esperada(v)
        assert tema["metadata"]["name"] == MARCA["nombre_esquema"][v] and isinstance(tema["metadata"]["revision"], int)
        assert c["BackgroundColor"] == qt["base.color"] == e["fondo"] and c["TextSelection"] == qt["highlight.color"]
        ts = tema["text-styles"]
        assert ts["Keyword"]["text-color"] == e["palabra-clave"] and ts["String"]["text-color"] == e["cadena"]
        assert ts["Function"]["text-color"] == e["funcion"] and ts["Comment"]["text-color"] == e["comentario"] and ts["Comment"]["italic"]
        assert ts["DecVal"]["text-color"] == e["numero"] and ts["Normal"]["text-color"] == e["texto"]
        faltan = {"Normal", "Keyword", "Function", "Variable", "ControlFlow", "Operator", "BuiltIn", "Extension", "Preprocessor",
                  "Attribute", "Char", "SpecialChar", "String", "VerbatimString", "SpecialString", "Import", "DataType", "DecVal",
                  "BaseN", "Float", "Constant", "Comment", "Documentation", "Annotation", "CommentVar", "RegionMarker",
                  "Information", "Warning", "Alert", "Error", "Others"} - set(ts)
        assert not faltan, (v, faltan)
        permitidos = _permitidos(v, c["BackgroundColor"])
        for nombre, estilo in ts.items():
            assert _contraste(estilo["text-color"], c["BackgroundColor"]) >= 4.5, (v, nombre)
            assert {estilo["text-color"], estilo["selected-text-color"], estilo.get("background-color", estilo["text-color"])} <= permitidos, (v, nombre)
        assert set(c.values()) <= permitidos, (v, set(c.values()) - permitidos)
        assert _contraste(ts["Normal"]["selected-text-color"], c["TextSelection"]) >= 4.5, v


def _formatos_texstudio(seccion: str) -> dict[str, dict[str, str]]:
    cp = configparser.RawConfigParser(comment_prefixes=("#", ";"))
    cp.optionxform = str
    cp.read_string((GEN / "texstudio" / f"{MARCA['id']}.txsprofile").read_text(encoding="utf-8"))
    formatos: dict[str, dict[str, str]] = {}
    for clave, valor in cp[seccion].items():
        if clave.startswith("data\\"):
            _, id_, campo = clave.split("\\")
            formatos.setdefault(id_.replace("%3A", ":"), {})[campo] = valor
    assert cp[seccion]["version"] == "1.0"
    return formatos


def test_texstudio_formatos():
    """Decisiones 5.6: [formats] (claro) y [formatsDark] (oscuro), con todos los formatos de TeXstudio 4.9 y la tabla de
    sintaxis; texto legible sobre el `base.color` de Kvantum (el `Base` con que pinta TeXstudio)."""
    ids = {"comment", "magicComment", "commentTodo", "keyword", "extra-keyword", "math-keyword", "math-delimiter", "math-text",
           "environment", "structure", "verbatim", "link", "numbers", "escapeseq", "text", "current", "selection", "search",
           "braceMatch", "braceMismatch", "spellingMistake", "line:error", "line:warning", "line:badbox", "background",
           "referencePresent", "referenceMissing", "citationPresent", "citationMissing", "diffAdd", "diffDelete",
           *(f"braceLevel{i}" for i in range(8))}
    for v, seccion in (("claro", "formats"), ("oscuro", "formatsDark")):
        f, e = _formatos_texstudio(seccion), _sintaxis_esperada(v)
        assert ids <= set(f), (v, ids - set(f))
        assert len(f) >= 88
        fondo = registro.codigo("kvantum").paleta_qt(TOKENS, v)["base.color"]
        assert f["keyword"]["foreground"] == e["funcion"] and f["extra-keyword"]["foreground"] == e["palabra-clave"]
        assert f["comment"]["foreground"] == e["comentario"] and f["comment"]["italic"] == "true"
        assert f["math-keyword"]["foreground"] == e["numero"] and f["align-ampersand"]["priority"] == "5"
        assert f["spellingMistake"]["waveUnderline"] == "true"
        permitidos = _permitidos(v, fondo)
        for id_, campos in f.items():
            colores = {campos[k] for k in ("foreground", "background", "linescolor") if k in campos}
            assert colores <= permitidos, (v, id_, colores - permitidos)
            if "foreground" in campos:
                assert _contraste(campos["foreground"], campos.get("background", fondo)) >= 4.5, (v, id_)


def test_texstudio_fundir_respeta_lo_demas(tmp_path):
    """El aplicar de TeXstudio solo sustituye [formats] y [formatsDark]; lo demás del texstudio.ini queda igual, y un
    enlace de dotfiles sigue siendo enlace. Con TeXstudio abierto no escribe."""
    aplicar = registro.codigo("texstudio", "aplicar")
    original = ("[General]\nIniMode=true\n\n[formats]\nversion=1.0\n\n[formatsDark]\nversion=1.0\n\n"
                "[texmaker]\nEditor\\Font%20Family=JetBrains Mono\nGUI\\Style=0\n\n[version]\nwritten_by_TXS_version=4.9.9\n")
    real = tmp_path / "dotfiles" / "texstudio.ini"
    real.parent.mkdir(parents=True)
    real.write_text(original, encoding="utf-8")
    ini = tmp_path / "config" / "texstudio" / "texstudio.ini"
    ini.parent.mkdir(parents=True)
    ini.symlink_to(real)

    class Ctx:
        CONFIG, modulos, marca, tokens = tmp_path / "config", ["texstudio"], MARCA, TOKENS
        abierto = False
        dicho: list[str] = []
        def ejecutar(self, orden):
            return subprocess.CompletedProcess(orden, 0 if self.abierto else 1)
        def decir(self, texto):
            self.dicho.append(texto)
        @staticmethod
        def codigo(id_, archivo="construir"):
            return registro.codigo(id_, archivo)

    ctx = Ctx()
    ctx.abierto = True
    assert aplicar.aplicar(ctx) == 0 and real.read_text(encoding="utf-8") == original and "abierto" in ctx.dicho[-1]
    ctx.abierto = False
    assert aplicar.respaldos(ctx)[0][0] == ini
    assert aplicar.aplicar(ctx) == 0
    nuevo = real.read_text(encoding="utf-8")
    assert ini.is_symlink()
    cp = configparser.RawConfigParser(comment_prefixes=("#", ";"))
    cp.optionxform = str
    cp.read_string(nuevo)
    viejo = configparser.RawConfigParser()
    viejo.optionxform = str
    viejo.read_string(original)
    for s in ("General", "texmaker", "version"):
        assert dict(cp[s]) == dict(viejo[s]), s
    assert nuevo.index("[General]") < nuevo.index("[formats]") < nuevo.index("[formatsDark]") < nuevo.index("[texmaker]")
    assert len([k for k in cp["formatsDark"] if k.startswith("data\\")]) > 500
    # idempotente, y sin las secciones las añade tras [General]
    assert aplicar.fundir(nuevo, {"formats": ["[formats]", "a=1", ""]}).count("[formats]") == 1
    sin = aplicar.fundir("[General]\nx=1\n\n[texmaker]\ny=2\n", {"formats": ["[formats]", "a=1", ""]})
    assert sin.index("[General]") < sin.index("[formats]") < sin.index("[texmaker]") and "y=2" in sin


def test_vim_esquema():
    """Decisiones 5.7: un colors/lliphi.vim con las dos variantes según background, la sintaxis de los editores, el fondo
    y los ANSI de Konsole, y los grupos de Neovim bajo has('nvim'); si Vim o Neovim están, lo cargan sin errores."""
    texto = (GEN / "vim" / "colors" / f"{MARCA['id']}.vim").read_text(encoding="utf-8")
    assert f"let g:colors_name = '{MARCA['id']}'" in texto and "if &background ==# 'light'" in texto
    claro, oscuro = texto.split("if &background ==# 'light'")[1].split("\nelse\n")
    for v, bloque in (("claro", claro), ("oscuro", oscuro.split("\nendif\n")[0])):
        k, e = registro.codigo("konsole").ansi(TOKENS, v), _sintaxis_esperada(v)
        hi = {m.group(1): dict(re.findall(r"(\w+)=(\S+)", m.group(2))) for m in re.finditer(r"^\s*hi (\S+) (.*)$", bloque, re.M)}
        assert hi["Normal"]["guibg"] == k["fondo"] and hi["Keyword"]["guifg"] == e["palabra-clave"]
        assert hi["String"]["guifg"] == e["cadena"] and hi["Function"]["guifg"] == e["funcion"] and hi["Comment"]["gui"] == "italic"
        assert hi["@keyword"]["guifg"] == e["palabra-clave"] and hi["@lsp.type.function"]["guifg"] == e["funcion"]
        assert "DiagnosticError" in hi and bloque.index("if has('nvim')") < bloque.index("hi @keyword")
        assert f"'{k['color1']}'" in bloque.split("g:terminal_ansi_colors")[1].split("\n")[0]
        assert f"let g:terminal_color_15 = '{k['color15']}'" in bloque
        permitidos = _permitidos(v, k["fondo"])
        for grupo, d in hi.items():
            assert {d[c] for c in ("guifg", "guibg", "guisp") if c in d} - {"NONE"} <= permitidos, (v, grupo)
            if d.get("guifg", "NONE") != "NONE" and d.get("guibg", "NONE") == "NONE" and grupo in ("Comment", "Keyword", "String", "Number", "Function", "Type", "LineNr"):
                assert _contraste(d["guifg"], k["fondo"]) >= 4.5, (v, grupo)
    casa = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / MARCA["id"] / "pruebas-vim"
    shutil.rmtree(casa, ignore_errors=True)
    (casa / "colors").mkdir(parents=True)
    shutil.copy(GEN / "vim" / "colors" / f"{MARCA['id']}.vim", casa / "colors")
    for bg in ("light", "dark"):
        guion = casa / f"p-{bg}.vim"
        guion.write_text(f"set nocompatible termguicolors background={bg}\nlet &rtp = '{casa},' . &rtp\nlet v:errmsg = ''\n"
                         f"colorscheme {MARCA['id']}\ncall writefile([v:errmsg, g:colors_name, &background], '{casa}/salida-{bg}')\nqa!\n", encoding="utf-8")
        for programa, orden in (("vim", ["vim", "-Nu", "NONE", "-es", "-S", str(guion)]),
                                ("nvim", ["nvim", "--clean", "--headless", "-S", str(guion)])):
            if shutil.which(programa) is None:
                continue
            (casa / f"salida-{bg}").unlink(missing_ok=True)
            subprocess.run(orden, capture_output=True, timeout=30, env={**os.environ, "HOME": str(casa)})
            assert (casa / f"salida-{bg}").read_text(encoding="utf-8").splitlines() == ["", MARCA["id"], bg], (programa, bg)
    shutil.rmtree(casa, ignore_errors=True)


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



def _hex_tupla(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def test_navegadores_zen():
    """userChrome.css de Zen: las dos variantes con prefers-color-scheme, cada color del maestro, las variables de Zen
    sobre las de Lliphi, las ventanas privadas aparte, Inter, contraste ≥ 4,5:1; y el user.js que lo carga y sigue al
    sistema (decisiones 5.3)."""
    nav, konsole = registro.codigo("navegadores"), registro.codigo("konsole")
    texto = (GEN / "navegadores" / "zen" / "userChrome.css").read_text(encoding="utf-8")
    assert "GENERADO por herramientas/generar.py (complementos/navegadores" in texto
    sin_comentarios = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
    assert sin_comentarios.count("{") == sin_comentarios.count("}")
    claro_css, oscuro_css = sin_comentarios.split("@media (prefers-color-scheme: dark)")
    variantes = {}
    for v, parte in (("claro", claro_css), ("oscuro", oscuro_css)):
        bloque = re.search(r":root\s*\{([^{}]*)\}", parte).group(1)
        variantes[v] = dict(re.findall(r"(--lliphi-[\w-]+)\s*:\s*(#[0-9a-f]{6}) !important;", bloque))
        esquema = "light" if v == "claro" else "dark"
        assert f"color-scheme: {esquema} !important;" in parte, v
    for v, x in variantes.items():
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        assert x == nav.zen_variables(TOKENS, v), v
        assert x["--lliphi-ventana"] == sem["fondo.ventana"] and x["--lliphi-vista"] == sem["fondo.vista"]
        assert x["--lliphi-acento"] == sem["acento.base"] and x["--lliphi-seleccion-fondo"] == sem["seleccion.fondo"]
        assert set(x.values()) <= set(sem.values()), v          # ningún color fuera de los semánticos de la variante
        for texto_, fondo in (("texto", "ventana"), ("texto", "vista"), ("texto", "pestana"), ("texto", "ventana-alterno"),
                              ("texto", "boton"), ("texto-secundario", "ventana"), ("texto-inactivo", "ventana"),
                              ("sobre-acento", "acento"), ("seleccion-texto", "seleccion-fondo"), ("enlace", "vista"),
                              ("tooltip-texto", "tooltip-fondo")):
            c = konsole.contraste(_hex_tupla(x[f"--lliphi-{texto_}"]), _hex_tupla(x[f"--lliphi-{fondo}"]))
            assert c >= 4.5, (v, texto_, fondo, round(c, 2))
    # las variables de Zen y Firefox: todas sobre una variable de Lliphi definida, en la raíz (no privada) y sus interiores
    comun = re.search(r"(:root:not\(\[zen-private-window='true'\]\)[^{]*)\{([^{}]*)\}", sin_comentarios)
    assert "zen-workspace" in comun.group(1) and "#zen-browser-background" in comun.group(1)
    mapa = dict(re.findall(r"(--[\w-]+)\s*:\s*var\((--lliphi-[\w-]+)\) !important;", comun.group(2)))
    assert set(mapa) == set(nav.ZEN) and set(mapa.values()) <= set(variantes["claro"])
    for clave in ("--zen-primary-color", "--zen-main-browser-background", "--toolbox-textcolor", "--tab-background-color-selected"):
        assert clave in mapa, clave
    assert re.search(r':root \{\s*font-family: "Inter", "Noto Sans", sans-serif !important;', texto)
    js = (GEN / "navegadores" / "zen" / "user.js").read_text(encoding="utf-8")
    assert 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);' in js
    assert 'user_pref("zen.view.window.scheme", 2);' in js
    assert all(l.startswith(("//", "user_pref(")) for l in js.splitlines())


def test_navegadores_chrome():
    """Dos temas de Chrome sin empaquetar (Manifest V3, `theme.colors` en ternas), con colores del maestro y el texto
    legible sobre su fondo (≥ 4,5:1)."""
    nav, konsole = registro.codigo("navegadores"), registro.codigo("konsole")
    for v in ("claro", "oscuro"):
        m = json.loads((GEN / "navegadores" / "chrome" / f"{MARCA['id']}-{v}" / "manifest.json").read_text(encoding="utf-8"))
        assert m["manifest_version"] == 3 and m["name"] == MARCA["nombre_esquema"][v]
        assert re.fullmatch(r"\d+(\.\d+){0,3}", m["version"]) and m["version"] == (RAIZ / "VERSION").read_text().strip()
        assert set(m) == {"manifest_version", "name", "version", "description", "homepage_url", "theme"}
        colores = m["theme"]["colors"]
        assert set(colores) == set(nav.CHROME)
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        for clave, terna in colores.items():
            assert len(terna) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in terna), (v, clave)
            assert "#%02x%02x%02x" % tuple(terna) == sem[nav.CHROME[clave]], (v, clave)
        assert colores["toolbar"] == list(_hex_tupla(sem["fondo.vista"])) and colores["frame"] == list(_hex_tupla(sem["fondo.ventana"]))
        for texto_, fondo in nav.CHROME_PARES.items():
            c = konsole.contraste(tuple(colores[texto_]), tuple(colores[fondo]))
            assert c >= 4.5, (v, texto_, fondo, round(c, 2))


def test_instalar_navegadores(tmp_path: Path):
    """El instalador pone userChrome.css y user.js en el perfil de Zen que abre el Flatpak (installs.ini), los temas de
    Chrome en $XDG_DATA_HOME/<id>/chrome/, no pisa un userChrome.css ajeno, omite Zen si no hay perfil y UNDO.sh
    retira lo instalado."""
    env = _entorno(tmp_path)
    sin_zen = correr("herramientas/instalar.py", "--modulos", "navegadores", env=env)
    assert sin_zen.returncode == 0 and "omitido navegadores/zen/userChrome.css" in sin_zen.stdout, sin_zen.stdout
    raiz = tmp_path / ".var/app/app.zen_browser.zen/.zen"
    perfil, otro = raiz / "abc123.Default (release)", raiz / "xyz789.otro"
    perfil.mkdir(parents=True); otro.mkdir()
    (raiz / "profiles.ini").write_text("[General]\nStartWithLastProfile=1\n\n[Profile0]\nName=otro\nIsRelative=1\n"
                                       "Path=xyz789.otro\nDefault=1\n\n[Profile1]\nName=Default (release)\nIsRelative=1\n"
                                       "Path=abc123.Default (release)\n", encoding="utf-8")
    (raiz / "installs.ini").write_text("[2953CB39A2589173]\nDefault=abc123.Default (release)\nLocked=1\n", encoding="utf-8")
    sim = correr("herramientas/instalar.py", "--modulos", "navegadores", env=env)
    assert sim.returncode == 0 and not (perfil / "user.js").exists(), sim.stdout
    assert f"→ {perfil / 'chrome' / 'userChrome.css'}" in sim.stdout        # el de installs.ini, no el Default=1
    ap = correr("herramientas/instalar.py", "--aplicar", "--modulos", "navegadores", env=env)
    assert ap.returncode == 0, ap.stdout + ap.stderr
    assert (perfil / "chrome" / "userChrome.css").read_bytes() == (GEN / "navegadores" / "zen" / "userChrome.css").read_bytes()
    assert (perfil / "user.js").exists() and not (otro / "user.js").exists()
    for v in ("claro", "oscuro"):
        assert (tmp_path / ".local/share" / MARCA["id"] / "chrome" / f"{MARCA['id']}-{v}" / "manifest.json").exists()
    manifiesto = tmp_path / ".local/state" / MARCA["id"] / "instalado.json"
    undo = Path(json.loads(manifiesto.read_text())["respaldo"]) / "UNDO.sh"
    assert subprocess.run(["bash", str(undo)], capture_output=True, text=True, env=env).returncode == 0
    assert not (perfil / "chrome" / "userChrome.css").exists() and not (perfil / "user.js").exists() and perfil.is_dir()
    # un userChrome.css que no es de Lliphi no se toca
    (perfil / "chrome" / "userChrome.css").write_text("/* mío */\n", encoding="utf-8")
    conf = correr("herramientas/instalar.py", "--aplicar", "--modulos", "navegadores", env=env)
    assert conf.returncode == 3 and (perfil / "chrome" / "userChrome.css").read_text() == "/* mío */\n"


def test_estilo_sin_azules_fijos():
    """Decisiones 4.36: ningún relleno ni trazo azul fijo de WhiteSur en los SVG del estilo de Plasma (la barra del
    volumen y del brillo salían azules en el oscuro): con clase de color van en currentColor; sin clase, en el acento de
    la variante. Quedan la hoja de estilo, los degradados de Breeze y las marcas de referencia."""
    estilo = registro.codigo("estilo")
    for v in ("claro", "oscuro"):
        propios = {x["$value"]["hex"].lower() for x in _tokens_planos(TOKENS["semanticos"][v]).values()}
        for f in (GEN / "estilo" / f"{MARCA['id']}-{v}").rglob("*.svg"):
            texto = re.sub(r"<style[^>]*>.*?</style>", "", f.read_text(encoding="utf-8", errors="ignore"), flags=re.S)
            for etiqueta in re.findall(r"<[^<>]+>", texto):
                if etiqueta.startswith("<stop"):
                    continue
                for h in re.findall(r"\b(?:fill|stroke)(?::|=\")(#[0-9a-fA-F]{6})\b", etiqueta):
                    assert not estilo._es_azul(h) or h.lower() in propios, (v, f.name, etiqueta[:120])
    barra = (GEN / "estilo" / f"{MARCA['id']}-oscuro" / "widgets" / "bar_meter_horizontal.svg").read_text(encoding="utf-8")
    activa = re.search(r'<[^<>]*\bid="bar-active-center"[^<>]*>', barra).group(0)
    assert "ColorScheme-Highlight" in activa and "fill:currentColor" in activa


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


def test_decoracion_menu_y_claro_visible():
    """Decisiones 4.33: un botón de menú de aplicación propio (Nothing no lo trae y Aurorae repetía el icono de la
    aplicación), con los cinco estados en el color del título; en el claro, el centro de minimizar y maximizar es gris
    (casi blanco no se veía sobre el título claro); las etiquetas del estilo claro, con los colores de la ventana."""
    for v, id_ in (("oscuro", MARCA["id"]), ("claro", f"{MARCA['id']}-claro")):
        sem = {k: x["$value"]["hex"] for k, x in _tokens_planos(TOKENS["semanticos"][v]).items()}
        menu = (GEN / "decoracion" / id_ / "appmenu.svg").read_text(encoding="utf-8")
        ET.fromstring(menu)
        for estado in ("active-center", "hover-center", "pressed-center", "inactive-center", "deactivated-center"):
            assert f'id="{estado}"' in menu, (v, estado)
        assert f"stroke:{sem['texto.normal']}" in menu and f"stroke:{sem['texto.inactivo']}" in menu
    claro = {k: x["$value"]["hex"] for k, x in _tokens_planos(TOKENS["semanticos"]["claro"]).items()}
    for boton in ("minimize.svg", "maximize.svg"):
        texto = (GEN / "decoracion" / f"{MARCA['id']}-claro" / boton).read_text(encoding="utf-8").lower()
        assert "#f4f0ed" not in texto and claro["texto.inactivo"] in texto, boton
    cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
    cp.read(GEN / "estilo" / f"{MARCA['id']}-claro" / "colors", encoding="utf-8")
    assert dict(cp["Colors:Tooltip"]) == dict(cp["Colors:Window"])

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


def _hex(h: str) -> tuple[int, int, int]:
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def test_fondo_forma():
    """«Lliphi Forma» (decisiones 4.23): claro y oscuro en los tres tamaños, en JPEG; neutro liso en la esquina y el
    semicírculo en el rojo de Lliphi en su sitio."""
    fondos = registro.codigo("fondos")
    base = GEN / "fondos" / fondos.id_forma(MARCA)
    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    assert meta["KPlugin"]["Id"] == fondos.id_forma(MARCA) and meta["KPlugin"]["Name"].endswith("Forma")
    PIL = pytest.importorskip("PIL.Image")
    rojo = _hex(TOKENS["primitivas"]["oscuro"]["acento"]["$value"]["hex"])
    for carpeta in ("images", "images_dark"):
        for ancho, alto in fondos.TAMANOS:
            im = PIL.open(base / "contents" / carpeta / f"{ancho}x{alto}.jpg")
            assert im.size == (ancho, alto) and im.mode == "RGB"
        im = PIL.open(base / "contents" / carpeta / "1920x1080.jpg")
        s = round(1080 * 0.25)
        x0 = 960 - (2 * s + s // 2 + round(s * 1.62) - round(s * 0.02)) // 2
        punto = im.getpixel((x0 + 2 * s + s // 4, 540))          # dentro del semicírculo
        assert all(abs(punto[i] - rojo[i]) < 40 for i in range(3)), (carpeta, punto)
    esquina_o = PIL.open(base / "contents" / "images_dark" / "1920x1080.jpg").getpixel((10, 10))
    esquina_c = PIL.open(base / "contents" / "images" / "1920x1080.jpg").getpixel((10, 10))
    assert max(esquina_o) < 40 and 150 < min(esquina_c) < 230


def test_fondo_relampago():
    """«Lliphi Relámpago» (decisiones 4.24): cada variante con su acento (azul el claro, rojo el oscuro) en el relámpago y
    en el punto de la marca, en los tres tamaños."""
    fondos = registro.codigo("fondos")
    base = GEN / "fondos" / fondos.id_relampago(MARCA)
    meta = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    acentos = {v: TOKENS["semanticos"][v]["acento"]["base"]["$value"]["hex"] for v in ("claro", "oscuro")}
    assert meta["X-KDE-PlasmaImageWallpaper-AccentColor"] == {"Light": acentos["claro"], "Dark": acentos["oscuro"]}
    PIL = pytest.importorskip("PIL.Image")
    for carpeta, v in (("images", "claro"), ("images_dark", "oscuro")):
        for ancho, alto in fondos.TAMANOS:
            assert PIL.open(base / "contents" / carpeta / f"{ancho}x{alto}.jpg").size == (ancho, alto)
        im = PIL.open(base / "contents" / carpeta / "3840x2160.jpg").convert("RGB")
        acento = _hex(TOKENS["primitivas"][v]["acento"]["$value"]["hex"])
        # en el eje del relámpago, a la altura del quiebre, hay puntos del acento de la variante
        fila = [im.getpixel((x, y)) for y in range(1040, 1120, 4) for x in range(round(3840 * 0.22), round(3840 * 0.42), 2)]
        assert any(all(abs(p[i] - acento[i]) < 45 for i in range(3)) for p in fila), v
    assert TOKENS["acento"] == {"claro": "azul-whitesur", "oscuro": "rojo"}


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
    kv = str(tmp_path / ".config/Kvantum" / MARCA["nombre"])
    datos["rutas"] = {(str(tmp_path / ".local/share/../../.config/Kvantum" / MARCA["nombre"]) if k == kv else k): v for k, v in datos["rutas"].items()}
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


def test_iconos_bandeja_a_medida(tmp_path, monkeypatch):
    """Decisiones 4.35: el superpuesto `<tema>-Lliphi` da a los simbólicos (lienzo de 16, dibujo a sangre) una versión de
    22 px con el dibujo en 16 centrado, en carpetas de tamaño fijo 22 que heredan del tema, y conserva lo que Plasma
    necesita para recolorearlos (la hoja current-color-scheme y la clase del raíz)."""
    ext = registro.codigo("iconos-cursores", "externas")
    simbolico = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="ColorScheme-Text" fill="currentColor">'
                 '<style id="current-color-scheme" type="text/css">.ColorScheme-Text { color:#363636; }</style>'
                 '<path d="m8 0a8 8 0 1 0 0 16 8 8 0 0 0 0-16z"/></svg>')
    nuevo = ET.fromstring(ext.con_margen(simbolico))
    assert (nuevo.get("width"), nuevo.get("height"), nuevo.get("viewBox")) == ("22", "22", "0 0 22 22")
    grupo = nuevo.find("{http://www.w3.org/2000/svg}g")
    assert grupo.get("transform").startswith("translate(3 3) scale(1)") and grupo.get("class") == "ColorScheme-Text"
    assert grupo.find(".//{http://www.w3.org/2000/svg}style").get("id") == "current-color-scheme"
    grande = ext.con_margen('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32"/></svg>')
    assert "translate(3 3) scale(0.5)" in grande                               # cualquier lienzo queda en 16 dentro de 22
    # un tema falso con su index.theme y un simbólico
    iconos = tmp_path / "icons"
    base = iconos / ext._AJUSTES["iconos"]["claro"]
    (base / "status" / "symbolic").mkdir(parents=True)
    (base / "status" / "symbolic" / "algo-symbolic.svg").write_text(simbolico, encoding="utf-8")
    (base / "index.theme").write_text("[Icon Theme]\nName=Base\nInherits=hicolor,breeze\nFollowsColorScheme=true\n"
                                      "Directories=status/symbolic\n\n[status/symbolic]\nSize=16\nType=Scalable\n", encoding="utf-8")
    monkeypatch.setattr(ext, "ICONOS", iconos)
    monkeypatch.setattr(ext, "HOME", tmp_path)
    creados = ext.bandeja(True, silencio=True)
    nombre = registro.codigo("iconos-cursores").tema("claro")
    assert nombre in creados and nombre == base.name + "-Lliphi"
    cp = configparser.ConfigParser(interpolation=None, strict=False); cp.optionxform = str
    cp.read(iconos / nombre / "index.theme", encoding="utf-8")
    assert cp["Icon Theme"]["Inherits"].startswith(base.name + ",") and cp["Icon Theme"]["FollowsColorScheme"] == "true"
    assert dict(cp["status/symbolic-22"]) == {"Size": "22", "Context": "Status", "Type": "Fixed"}
    assert 'viewBox="0 0 22 22"' in (iconos / nombre / "status" / "symbolic-22" / "algo-symbolic.svg").read_text(encoding="utf-8")
    # si el superpuesto es un enlace (la sesión de prueba enlaza los temas del usuario), se quita el enlace y no se sigue
    ajeno = tmp_path / "ajeno"
    shutil.copytree(iconos / nombre, ajeno)
    shutil.rmtree(iconos / nombre)
    (iconos / nombre).symlink_to(ajeno)
    ext.bandeja(True, silencio=True)
    assert not (iconos / nombre).is_symlink() and (ajeno / "index.theme").exists()


def test_variante_clara_validada():
    """Mejora 10 (decisiones 4.15–4.16): carpetas por variante sin tocar Papirus, fondo claro fijado y bloqueo oscuro."""
    for v, iconos in (("oscuro", "Colloid-Grey-Dark"), ("claro", "Colloid-Grey-Light")):   # decisiones 4.22
        defaults = (GEN / "global" / MARCA["id_global"][v] / "contents" / "defaults").read_text(encoding="utf-8")
        assert f"Theme={iconos}-Lliphi" in defaults, v                     # el superpuesto de la bandeja (4.35)
    dep = registro.codigo("iconos-cursores", "externas")
    assert dep.SUPERPUESTO["id"] == "Papirus-Dark-Lliphi" and dep.COLOR_ORIGINAL == "blue"
    fondo = registro.modulo("fondos").archivo("aplicar.py").read_text(encoding="utf-8")
    bloqueo = registro.modulo("carga-bloqueo").archivo("aplicar.py").read_text(encoding="utf-8")
    # el escritorio por la ruta de la imagen de la variante, no por el paquete (4.16); el bloqueo, la oscura (4.27: Horizonte)
    assert '("images" if ctx.variante == "claro" else "images_dark")' in fondo
    assert '"images_dark" / "3840x2160.png"' in bloqueo and '"kscreenlockerrc"' in bloqueo


# ---------------------------------------------------------------- arquitectura modular

SEIS = {"esquema": "paquete", "estilo": "paquete", "decoracion": "paquete", "iconos-cursores": "externo",
        "carga-bloqueo": "componente", "disposicion": "componente"}


def test_registro_tema_global_y_seis_modulos():
    """Un tema global integrador, los seis módulos del encargo con su clase y los complementos que ya existían."""
    roles = {m.id: (m.rol, m.clase) for m in registro.todos()}
    assert roles["global"] == ("global", "paquete")
    assert {i: c for i, (r, c) in roles.items() if r == "modulo"} == SEIS
    assert {i for i, (r, _) in roles.items() if r == "complemento"} == {"fondos", "kvantum", "konsole", "terminales", "editores", "libreoffice", "sddm", "obsidian", "fondo-variante",
                                                                              "navegadores", "telegram", "kate", "texstudio", "vim",
                                                                              "gtk", "xournalpp", "gimp", "calibre"}
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
    assert "@NOMBRE@" not in js and "@FONDO@" not in js and f"/{MARCA['fondo_escritorio']}/contents/images_dark/3840x2160.jpg" in js
    claro = (GEN / "global" / MARCA["id_global"]["claro"] / "contents" / "layouts" / "org.kde.plasma.desktop-layout.js").read_text(encoding="utf-8")
    assert f"/{MARCA['fondo_escritorio']}/contents/images/3840x2160.jpg" in claro   # 4.27: la imagen de la variante
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
def test_kvantum_inactivo_pleno():
    """Decisiones 4.31: en el oscuro, el deslizador y la barra de progreso de una ventana inactiva llevan el acento entero
    (WhiteSur los dejaba a media opacidad); lo deshabilitado sigue a media opacidad."""
    svg = (GEN / "kvantum" / MARCA["nombre"] / f"{MARCA['nombre']}Dark.svg").read_text(encoding="utf-8")
    piezas = re.findall(r'<[^<>]*\bid="(?:slider-toggled|progress-pattern-normal)-inactive[^"]*"[^<>]*>', svg)
    assert piezas and not any(re.search(r"(?<![-\w])opacity:0?\.5\b", x) for x in piezas)
    deshabilitado = re.findall(r'<[^<>]*\bid="progress-pattern-disabled[^"]*"[^<>]*>', svg)
    assert any(re.search(r"(?<![-\w])opacity:0?\.5\b", x) for x in deshabilitado)


def test_kvantum_etiquetas_legibles():
    """Decisiones 4.34: en el claro, Kvantum dibuja la etiqueta emergente clara; su texto es el del texto normal (no el
    `texto.tooltip` del esquema, casi blanco) y se lee sobre su fondo (≥ 4,5:1)."""
    konsole = registro.codigo("konsole")
    for v, archivo in (("claro", MARCA["nombre"]), ("oscuro", f"{MARCA['nombre']}Dark")):
        kv = (GEN / "kvantum" / MARCA["nombre"] / f"{archivo}.kvconfig").read_text(encoding="utf-8")
        base = re.search(r"^tooltip\.base\.color=(#[0-9a-f]{6})", kv, re.M).group(1)
        texto = re.search(r"^tooltip\.text\.color=(#[0-9a-f]{6})", kv, re.M).group(1)
        tupla = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        assert konsole.contraste(tupla(base), tupla(texto)) >= 4.5, (v, base, texto)
    svg = (GEN / "kvantum" / MARCA["nombre"] / f"{MARCA['nombre']}.svg").read_text(encoding="utf-8")
    claro = {k: x["$value"]["hex"] for k, x in _tokens_planos(TOKENS["semanticos"]["claro"]).items()}
    etiqueta = re.search(r'<[^<>]*\bid="tooltip-normal"[^<>]*>', svg).group(0)
    assert f"fill:{claro['fondo.ventana']}" in etiqueta, etiqueta                  # el svg la dibuja clara
    kv = (GEN / "kvantum" / MARCA["nombre"] / f"{MARCA['nombre']}.kvconfig").read_text(encoding="utf-8")
    assert f"tooltip.text.color={claro['texto.normal']}" in kv


def test_kvantum_en_xdg_config_home(tmp_path: Path):
    """Kvantum va a $XDG_CONFIG_HOME aunque no sea ~/.config (en 0.3.0 se calculaba desde $XDG_DATA_HOME/../..)."""
    env = _entorno(tmp_path)
    env["XDG_CONFIG_HOME"] = str(tmp_path / "otra-config")
    r = correr("herramientas/instalar.py", "--modulos", "kvantum", env=env)
    assert r.returncode == 0 and f"→ {tmp_path / 'otra-config' / 'Kvantum' / MARCA['nombre']}" in r.stdout, r.stdout


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


def test_fondo_sigue_a_la_variante(tmp_path: Path, monkeypatch):
    """Decisiones 4.26: al cambiar de variante, el programa elige la imagen de la variante del mismo fondo de Lliphi
    (el mismo tamaño si lo hay; si no, el mayor) y no toca un fondo ajeno; el inicio automático no lleva rutas fijas."""
    import importlib.util
    datos = tmp_path / "data"
    monkeypatch.setenv("XDG_DATA_HOME", str(datos))
    spec = importlib.util.spec_from_file_location("seguir_variante", GEN / "fondo-variante" / "seguir-variante.py")
    sv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sv)
    assert sv.VARIANTES == {MARCA["id_esquema"]["claro"]: "claro", MARCA["id_esquema"]["oscuro"]: "oscuro"}
    paquete = datos / "wallpapers" / f"{MARCA['dominio_inverso']}.forma"
    for carpeta, tamanos in (("images", ("1920x1080", "3840x2160")), ("images_dark", ("1920x1080", "2560x1440"))):
        (paquete / "contents" / carpeta).mkdir(parents=True)
        for t in tamanos:
            (paquete / "contents" / carpeta / f"{t}.jpg").write_bytes(b"")
    oscura = (paquete / "contents" / "images_dark" / "1920x1080.jpg").as_uri()
    assert sv.imagen_para(oscura, "claro") == (paquete / "contents" / "images" / "1920x1080.jpg").as_uri()
    assert sv.imagen_para(oscura, "oscuro") == oscura                                 # ya es la de la variante
    grande = (paquete / "contents" / "images_dark" / "2560x1440.jpg").as_uri()
    assert sv.imagen_para(grande, "claro").endswith("images/3840x2160.jpg")           # sin el mismo tamaño, el mayor
    assert sv.imagen_para(paquete.as_uri() + "/", "oscuro").endswith("images_dark/2560x1440.jpg")   # el paquete entero
    ajeno = datos / "wallpapers" / "Next" / "contents" / "images" / "1920x1080.png"
    assert sv.imagen_para(ajeno.as_uri(), "oscuro") is None
    assert sv.imagen_para("file:///usr/share/wallpapers/Next/contents/images/1920x1080.png", "claro") is None
    inicio = (GEN / "fondo-variante" / "lliphi-fondo-variante.desktop").read_text(encoding="utf-8")
    assert "--vigilar" in inicio and "/home/" not in inicio and "$HOME" in inicio
    texto = (GEN / "fondo-variante" / "seguir-variante.py").read_text(encoding="utf-8")
    assert not re.search(r"@[A-Z_]+@", texto)                                     # ninguna marca sin sustituir
    # decisiones 4.28: Konsole sigue a la variante si su perfil usa un esquema de Lliphi; si no, no se toca
    assert sv.KONSOLE == MARCA["nombre_esquema"]
    monkeypatch.setattr(sv, "CONFIG", tmp_path / "config")
    monkeypatch.setattr(sv, "terminales_abiertas", lambda: [])
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "konsolerc").write_text("[Desktop Entry]\nDefaultProfile=yo.profile\n", encoding="utf-8")
    (datos / "konsole").mkdir(parents=True)
    perfil = datos / "konsole" / "yo.profile"
    perfil.write_text(f"[Appearance]\nColorScheme={MARCA['nombre_esquema']['oscuro']}\nFont=Mono,10\n\n[General]\nName=yo\n", encoding="utf-8")
    sv.konsole("claro", escribir=False)
    assert f"ColorScheme={MARCA['nombre_esquema']['oscuro']}" in perfil.read_text(encoding="utf-8")   # simular no escribe
    sv.konsole("claro", escribir=True)
    assert perfil.read_text(encoding="utf-8") == f"[Appearance]\nColorScheme={MARCA['nombre_esquema']['claro']}\nFont=Mono,10\n\n[General]\nName=yo\n"
    perfil.write_text("[Appearance]\nColorScheme=Breeze\n", encoding="utf-8")
    sv.konsole("oscuro", escribir=True)
    assert perfil.read_text(encoding="utf-8") == "[Appearance]\nColorScheme=Breeze\n"                # ajeno: intacto


def test_fondo_del_escritorio():
    """Decisiones 4.27: el escritorio lleva por omisión «Lliphi Relámpago · @achalmaedison» (la disposición, el estilo
    de Plasma y el instalador); Horizonte sigue en el bloqueo y el inicio de sesión."""
    assert MARCA["fondo_escritorio"] == registro.codigo("fondos").id_relampago(MARCA) + ".firmado"
    for carpeta in ("images", "images_dark"):
        assert (GEN / "fondos" / MARCA["fondo_escritorio"] / "contents" / carpeta / "3840x2160.jpg").is_file()
    for v in ("claro", "oscuro"):
        plasmarc = (GEN / "estilo" / f"{MARCA['id']}-{v}" / "plasmarc").read_text(encoding="utf-8")
        assert f"defaultWallpaperTheme={MARCA['fondo_escritorio']}" in plasmarc and "defaultFileSuffix=.jpg" in plasmarc
    assert MARCA["id_fondo"] in registro.modulo("carga-bloqueo").archivo("aplicar.py").read_text(encoding="utf-8").replace('ctx.marca["id_fondo"]', MARCA["id_fondo"])


# ---------------------------------------------------------------- GTK, Xournal++, GIMP y Calibre (decisiones 4.37, 5.20–5.22)

def _hexes_maestro() -> set[str]:
    return {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values() if isinstance(t["$value"], dict) and "hex" in t["$value"]}


def _contraste(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_hex_de_los_nuevos_complementos_del_maestro():
    """Todo hex de lo generado para GTK, GIMP, Xournal++ y Calibre existe en tokens.json (los derivados van como mix())."""
    hexes = _hexes_maestro()
    for modulo in ("gtk", "gimp", "xournalpp", "calibre"):
        for f in (GEN / modulo).rglob("*"):
            if f.is_file() and f.suffix in (".css", ".svg", ".json", ".xml"):
                for h in re.findall(r"#[0-9a-fA-F]{6}\b", f.read_text(encoding="utf-8")):
                    assert h.lower() in hexes, (f.relative_to(GEN), h)


def test_gtk_hojas():
    """GTK 3: una hoja por variante con todos los colores _breeze que escribe kde-gtk-config; GTK 4: las dos variantes
    con prefers-color-scheme, los colores con nombre de libadwaita y sus variables."""
    gtk = registro.codigo("gtk")
    for v in ("claro", "oscuro"):
        texto = (GEN / "gtk" / "gtk-3.0" / f"{MARCA['id']}-{v}.css").read_text(encoding="utf-8")
        assert "GENERADO" in texto and texto.count("{") == texto.count("}")
        definidos = set(re.findall(r"@define-color (\w+)_breeze ", texto))
        assert definidos == set(gtk.BREEZE) and len(definidos) == 84
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        assert f"@define-color theme_bg_color_breeze {sem['fondo.ventana']};" in texto
        assert f"@define-color theme_selected_bg_color_breeze {sem['seleccion.fondo']};" in texto
        assert "#floatingToolbox" in texto
    texto = (GEN / "gtk" / "gtk-4.0" / f"{MARCA['id']}.css").read_text(encoding="utf-8")
    assert texto.count("{") == texto.count("}") and texto.count("@media (prefers-color-scheme: dark) {") == 2
    claro, oscuro = texto.split("@media (prefers-color-scheme: dark) {", 1)
    for nombre in gtk.ADWAITA:
        assert f"@define-color {nombre} " in claro and f"@define-color {nombre} " in oscuro, nombre
        assert f"--{nombre.replace('_', '-')}: " in claro and f"--{nombre.replace('_', '-')}: " in oscuro, nombre
    assert f"@define-color accent_bg_color {_tokens_planos(TOKENS['semanticos']['claro'])['acento.base']['$value']['hex']};" in claro
    assert f"@define-color accent_bg_color {_tokens_planos(TOKENS['semanticos']['oscuro'])['acento.base']['$value']['hex']};" in oscuro


def test_gtk_contraste():
    gtk = registro.codigo("gtk")
    for v in ("claro", "oscuro"):
        for tabla, pares in ((gtk.BREEZE, gtk.PARES_BREEZE), (gtk.ADWAITA, gtk.PARES_ADWAITA)):
            r = gtk.resueltos(TOKENS, v, tabla)
            for texto, fondo in pares:
                assert _contraste(r[texto], r[fondo]) >= 4.5, (v, texto, fondo, r[texto], r[fondo])
    assert gtk.mezclar("#000000", "#ffffff", 0.5) == "#808080"


def test_gtk_importacion(tmp_path):
    """gtk.css: la línea de Lliphi va detrás de colors.css, no se duplica, cambia de variante y no toca lo demás;
    si colors.css existe y faltaba su línea, se pone delante; un enlace de dotfiles sigue siendo enlace."""
    fijar = registro.codigo("gtk", "aplicar").fijar_importacion
    d = tmp_path / "gtk-3.0"
    d.mkdir()
    (d / "colors.css").write_text("", encoding="utf-8")
    css = d / "gtk.css"
    css.write_text("@import 'colors.css';\nwindow { padding: 1px; }\n", encoding="utf-8")
    assert fijar(css, "lliphi", "lliphi-oscuro.css")
    assert css.read_text(encoding="utf-8") == "@import 'colors.css';\n@import 'lliphi-oscuro.css';\nwindow { padding: 1px; }\n"
    assert not fijar(css, "lliphi", "lliphi-oscuro.css")                     # idempotente
    fijar(css, "lliphi", "lliphi-claro.css")
    assert css.read_text(encoding="utf-8").count("lliphi") == 1 and "lliphi-claro.css" in css.read_text(encoding="utf-8")
    css.write_text("window { padding: 1px; }\n", encoding="utf-8")         # sin la línea de colors.css
    fijar(css, "lliphi", "lliphi-claro.css")
    assert css.read_text(encoding="utf-8").splitlines()[:2] == ["@import 'colors.css';", "@import 'lliphi-claro.css';"]
    real = tmp_path / "dotfiles.css"
    real.write_text("@import 'colors.css';\n", encoding="utf-8")
    enlace = d / "enlace.css"
    enlace.symlink_to(real)
    fijar(enlace, "lliphi", "lliphi-oscuro.css")
    assert enlace.is_symlink() and "lliphi-oscuro.css" in real.read_text(encoding="utf-8")


def test_fondo_variante_cambia_gtk3(tmp_path, monkeypatch):
    """Decisiones 4.37: la vigilancia cambia la hoja de GTK 3 de variante solo si gtk.css ya importa una de Lliphi."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("seguir_variante_gtk", GEN / "fondo-variante" / "seguir-variante.py")
    sv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sv)
    monkeypatch.setattr(sv, "CONFIG", tmp_path)
    monkeypatch.setattr(sv, "herramienta", lambda nombre: None)               # sin gsettings
    css = tmp_path / "gtk-3.0" / "gtk.css"
    css.parent.mkdir()
    css.write_text(f"@import 'colors.css';\n@import '{MARCA['id']}-oscuro.css';\n", encoding="utf-8")
    sv.gtk("claro", escribir=False)
    assert f"{MARCA['id']}-oscuro.css" in css.read_text(encoding="utf-8")       # simular no escribe
    sv.gtk("claro", escribir=True)
    assert css.read_text(encoding="utf-8") == f"@import 'colors.css';\n@import '{MARCA['id']}-claro.css';\n"
    css.write_text("@import 'colors.css';\n", encoding="utf-8")
    sv.gtk("oscuro", escribir=True)
    assert css.read_text(encoding="utf-8") == "@import 'colors.css';\n"           # sin GTK de Lliphi: intacto


def test_gimp_tema():
    """Tema de GIMP: los tres archivos de color definen los diecisiete nombres de Default e importan su común; el común
    importa system.css (no ../System); los separadores, sin colores de Inkscape; contraste del texto y de lo elegido."""
    gimp = registro.codigo("gimp")
    tema = GEN / "gimp" / "themes" / MARCA["nombre"]
    base = RAIZ / "fuentes" / "base" / "GIMP-Default"
    nombres = set(re.findall(r"@define-color ([\w-]+)", (base / "gimp-dark.css").read_text(encoding="utf-8")))
    assert len(nombres) == 17 and nombres == set(gimp.COLORES)
    for archivo, comun in (("light", "common-light.css"), ("gray", "common-dark.css"), ("dark", "common-dark.css")):
        texto = (tema / f"gimp-{archivo}.css").read_text(encoding="utf-8")
        assert set(re.findall(r"@define-color ([\w-]+)", texto)) == nombres and f'@import url("{comun}");' in texto
        assert texto.count("{") == texto.count("}")
    comun = (tema / "common.css").read_text(encoding="utf-8")
    assert '@import url("system.css");' in comun and "../System" not in comun and (tema / "system.css").is_file()
    for svg in (tema / "ui").glob("*.svg"):
        ET.parse(svg)
        assert "pagecolor" not in svg.read_text(encoding="utf-8")
    for v in ("claro", "oscuro"):
        r = gimp.resueltos(TOKENS, v)
        assert _contraste(r["fg-color"], r["bg-color"]) >= 4.5 and _contraste(r["fg-color"], r["extreme-bg-color"]) >= 4.5, v
        sem = {k: t["$value"]["hex"] for k, t in _tokens_planos(TOKENS["semanticos"][v]).items()}
        assert _contraste(sem["seleccion.texto"], sem["seleccion.fondo"]) >= 4.5, v
    for v in ("claro", "oscuro"):
        lineas = (GEN / "gimp" / "palettes" / f"{MARCA['nombre_esquema'][v]}.gpl").read_text(encoding="utf-8").splitlines()
        assert lineas[0] == "GIMP Palette" and lineas[1] == f"Name: {MARCA['nombre_esquema'][v]}"
        colores = [ln for ln in lineas[3:] if not ln.startswith("#")]
        esperados = registro.codigo("libreoffice").paleta(TOKENS, v)
        assert len(colores) == len(esperados)
        for ln, (nombre, h) in zip(colores, esperados):
            r, g, b, resto = ln.split(None, 3)
            assert "#%02x%02x%02x" % (int(r), int(g), int(b)) == h and resto == nombre


def test_gimp_aplicar():
    fijar = registro.codigo("gimp", "aplicar").fijar
    texto = '(prev-language "es")\n(theme "Default")\n(monitor-xresolution 158)\n'
    nuevo = fijar(fijar(texto, "theme", '"Lliphi"'), "theme-color-scheme", "system")
    assert nuevo == '(prev-language "es")\n(theme "Lliphi")\n(monitor-xresolution 158)\n(theme-color-scheme system)\n'
    assert fijar(nuevo, "theme-color-scheme", "system") == nuevo


def test_xournalpp():
    """Paleta de bolígrafos: once colores como mínimo (los botones de la barra), los de escribir legibles sobre papel
    blanco, cada uno del maestro; settings: ARGB opaco de los tokens; y la sustitución de propiedades."""
    x = registro.codigo("xournalpp")
    lineas = (GEN / "xournalpp" / "palettes" / f"{MARCA['nombre']}.gpl").read_text(encoding="utf-8").splitlines()
    assert lineas[0] == "GIMP Palette"
    colores = [ln.split(None, 3) for ln in lineas[1:] if ln[:1].isdigit() or ln[:1] == " "]
    assert len(colores) >= 11
    hexes = _hexes_maestro()
    papel = _tokens_planos(TOKENS["semanticos"]["claro"])["fondo.vista"]["$value"]["hex"]
    for r, g, b, nombre in colores:
        h = "#%02x%02x%02x" % (int(r), int(g), int(b))
        assert h in hexes, nombre
        if "resaltar" not in nombre and nombre != "Blanco":
            assert _contraste(h, papel) >= 4.5, (nombre, h)
    props = x.propiedades(TOKENS, "/ruta/Lliphi.gpl")
    assert props["colorPalette"] == "/ruta/Lliphi.gpl"
    for k, v in props.items():
        if k != "colorPalette":
            assert int(v) >> 24 == 0xFF and "#%06x" % (int(v) & 0xFFFFFF) in hexes, k
    fijar = registro.codigo("xournalpp", "aplicar").fijar_propiedades
    texto = '<settings>\n  <property name="backgroundColor" value="1"/>\n  <property name="iconTheme" value="iconsLucide"/>\n</settings>\n'
    nuevo = fijar(texto, {"backgroundColor": "2", "colorPalette": "/p/L.gpl"})
    assert '<property name="backgroundColor" value="2"/>' in nuevo and '<property name="iconTheme" value="iconsLucide"/>' in nuevo
    assert nuevo.count('name="colorPalette"') == 1 and nuevo.rstrip().endswith("</settings>")
    ET.fromstring(nuevo)


def test_calibre():
    """Paletas de Calibre con roles de QPalette válidos y contraste; el visor con sus dos esquemas; el fundido conserva lo
    del usuario (otras claves, otras paletas, sus esquemas)."""
    c = registro.codigo("calibre")
    roles = {"WindowText", "Text", "ButtonText", "PlaceholderText", "ToolTipText", "BrightText", "HighlightedText", "Window",
             "Base", "Button", "AlternateBase", "ToolTipBase", "Highlight", "Accent", "Link", "LinkVisited"}
    gui = json.loads((GEN / "calibre" / f"gui-{MARCA['id']}.json").read_text(encoding="utf-8"))
    assert gui["color_palette"] == "system"
    for v, clave in (("claro", "light"), ("oscuro", "dark")):
        nombre = MARCA["nombre_esquema"][v]
        assert gui[f"{clave}_palette_name"] == nombre
        p = gui[f"{clave}_palettes"][nombre]
        assert {r.removesuffix("-disabled") for r in p} <= roles and roles <= set(p)
        for texto, fondo in c.PARES:
            assert _contraste(p[texto], p[fondo]) >= 4.5, (v, texto, fondo)
    visor = json.loads((GEN / "calibre" / f"visor-{MARCA['id']}.json").read_text(encoding="utf-8"))["user_color_schemes"]
    assert set(visor) == {f"*{n}" for n in MARCA["nombre_esquema"].values()}
    for e in visor.values():
        assert _contraste(e["foreground"], e["background"]) >= 4.5 and _contraste(e["link"], e["background"]) >= 4.5
    a = registro.codigo("calibre", "aplicar")
    previo = {"emblem_style": "none", "dark_palettes": {"Mía": {"Window": "#000000"}}, "color_palette": "dark"}
    fundido = a.fundir_gui(previo, c.preferencias_gui(TOKENS, MARCA))
    assert fundido["emblem_style"] == "none" and "Mía" in fundido["dark_palettes"] and MARCA["nombre_esquema"]["oscuro"] in fundido["dark_palettes"]
    assert fundido["color_palette"] == "system" and previo["dark_palettes"] == {"Mía": {"Window": "#000000"}}
    visor_previo = {"session_data": {"base_font_size": 18, "user_color_schemes": {"*Mío": {"name": "Mío"}}}, "main_window_state": "x"}
    fv = a.fundir_visor(visor_previo, c.esquemas_visor(TOKENS, MARCA))
    assert fv["main_window_state"] == "x" and fv["session_data"]["base_font_size"] == 18
    assert set(fv["session_data"]["user_color_schemes"]) == {"*Mío", *visor}


def test_aplicar_gtk_xournalpp_gimp_calibre(tmp_path):
    """Los cuatro aplicar() en un HOME temporal, con las herramientas del sistema simuladas (ni gsettings ni pgrep
    reales): cada uno toca solo sus claves, y respaldos() declara los archivos que toca."""
    import shutil as sh
    from nucleo import instalacion
    config, data = tmp_path / "config", tmp_path / "data"
    ordenes = []
    ctx = instalacion.Contexto(variante="claro", modulos=["gtk", "xournalpp", "gimp", "calibre"], CONFIG=config, DATA=data)
    ctx.hay = lambda h: h == "gsettings"                                     # sin pgrep: los programas «cerrados»
    ctx.ejecutar = lambda orden, mostrar=False: ordenes.append(orden)
    ctx.decir = lambda texto: None
    # lo instalado y lo que ya tenía el usuario
    for v in (3, 4):
        (config / f"gtk-{v}.0").mkdir(parents=True)
        (config / f"gtk-{v}.0" / "colors.css").write_text("", encoding="utf-8")
        (config / f"gtk-{v}.0" / "gtk.css").write_text("@import 'colors.css';\n", encoding="utf-8")
    for f in ("lliphi-claro.css", "lliphi-oscuro.css"):
        sh.copy(GEN / "gtk" / "gtk-3.0" / f, config / "gtk-3.0" / f)
    sh.copy(GEN / "gtk" / "gtk-4.0" / "lliphi.css", config / "gtk-4.0" / "lliphi.css")
    (config / "xournalpp" / "palettes").mkdir(parents=True)
    sh.copy(GEN / "xournalpp" / "palettes" / f"{MARCA['nombre']}.gpl", config / "xournalpp" / "palettes")
    (config / "xournalpp" / "settings.xml").write_text('<?xml version="1.0"?>\n<settings>\n  <property name="themeVariant" value="useSystem"/>\n</settings>\n', encoding="utf-8")
    gimp = config / "GIMP" / "3.2"
    sh.copytree(GEN / "gimp" / "themes" / MARCA["nombre"], gimp / "themes" / MARCA["nombre"])
    (gimp / "gimprc").write_text('(config-version "3.2.2")\n', encoding="utf-8")
    (config / "calibre").mkdir()
    (config / "calibre" / "gui.json").write_text('{"emblem_style": "none"}', encoding="utf-8")
    for m in ("gtk", "xournalpp", "gimp", "calibre"):
        assert registro.codigo(m, "aplicar").aplicar(ctx) == 0, m
    assert (config / "gtk-3.0" / "gtk.css").read_text(encoding="utf-8") == "@import 'colors.css';\n@import 'lliphi-claro.css';\n"
    assert (config / "gtk-4.0" / "gtk.css").read_text(encoding="utf-8") == "@import 'colors.css';\n@import 'lliphi.css';\n"
    assert ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-light"] in ordenes
    s = (config / "xournalpp" / "settings.xml").read_text(encoding="utf-8")
    assert 'name="themeVariant" value="useSystem"' in s and f'{MARCA["nombre"]}.gpl' in s
    assert (gimp / "gimprc").read_text(encoding="utf-8") == f'(config-version "3.2.2")\n(theme "{MARCA["nombre"]}")\n(theme-color-scheme system)\n'
    gui = json.loads((config / "calibre" / "gui.json").read_text(encoding="utf-8"))
    assert gui["emblem_style"] == "none" and gui["color_palette"] == "system"
    visor = json.loads((config / "calibre" / "viewer-webengine.json").read_text(encoding="utf-8"))
    assert len(visor["session_data"]["user_color_schemes"]) == 2
    declarados = {r for m in ("gtk", "xournalpp", "gimp", "calibre") for r, _, _ in registro.codigo(m, "aplicar").respaldos(ctx)}
    assert declarados == {config / "gtk-3.0" / "gtk.css", config / "gtk-4.0" / "gtk.css", config / "xournalpp" / "settings.xml",
                          gimp / "gimprc", config / "calibre" / "gui.json", config / "calibre" / "viewer-webengine.json"}


# ---------------------------------------------------------------- Telegram Desktop (decisiones 5.30)

def _rgba(h: str) -> tuple[tuple[int, int, int], float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)), (int(h[6:8], 16) / 255 if len(h) == 8 else 1.0)


def _sobre(frente: str, fondo: str) -> str:
    """El color que se ve al pintar `frente` (con su alfa) sobre `fondo` (opaco)."""
    (f, a), (b, _) = _rgba(frente), _rgba(fondo)
    return "#" + "".join(f"{round(a * x + (1 - a) * y):02x}" for x, y in zip(f, b))


def _contraste(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [v / 255 for v in _rgba(h)[0]]
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    claro, oscuro = sorted((lum(a), lum(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def test_telegram_temas():
    """Los dos .tdesktop-theme abren como zip con colors.tdesktop-theme y tiled.png, tienen todas las claves de la paleta
    de Telegram en su orden, cada color es de los tokens (con alfa libre) y el texto se lee (≥ 4,5:1) sobre las burbujas
    y los fondos, con el alfa compuesto sobre el fondo del chat."""
    import struct
    import zipfile
    import zlib
    tg = registro.codigo("telegram")
    claves = [k for k, _, _ in tg.plantilla()]
    assert len(claves) > 500 and len(set(claves)) == len(claves)
    hexes = {t["$value"]["hex"].lower() for t in _tokens_planos(TOKENS).values()
             if isinstance(t["$value"], dict) and "hex" in t["$value"]}
    linea = re.compile(r"^([A-Za-z]\w*): (#[0-9a-f]{6}(?:[0-9a-f]{2})?);$")
    for v in ("claro", "oscuro"):
        paquete = GEN / "telegram" / f"{MARCA['nombre_esquema'][v]}.tdesktop-theme"
        with zipfile.ZipFile(paquete) as z:
            assert sorted(z.namelist()) == ["colors.tdesktop-theme", "tiled.png"]
            texto = z.read("colors.tdesktop-theme").decode("utf-8")
            png = z.read("tiled.png")
            for nombre in z.namelist():   # lo suelto es lo mismo que lo empaquetado
                assert (GEN / "telegram" / v / nombre).read_bytes() == z.read(nombre)
        filas = [ln for ln in texto.splitlines() if ln and not ln.startswith("//")]
        pares = [linea.fullmatch(ln) for ln in filas]
        assert all(pares), [ln for ln, m in zip(filas, pares) if not m][:5]
        c = {m[1]: m[2] for m in pares}
        assert list(c) == claves                                         # todas las claves, en el orden de la paleta
        for k, h in c.items():
            assert h[:7] in hexes, (v, k, h)                              # ningún color fuera del maestro
        # el fondo liso del chat: un PNG de 16×16 del color de los tokens
        assert png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (16, 16)
        datos = zlib.decompress(png[png.index(b"IDAT") + 4:png.index(b"IEND") - 8])
        chat = tg.fondo_chat(TOKENS, v)
        assert datos[1:4] == bytes(_rgba(chat)[0]) and len(set(datos[1:49])) <= 3
        # burbujas y fondos tal como se ven (alfa compuesto sobre el fondo del chat)
        burbuja = {"entrante": _sobre(c["msgInBg"], chat), "propia": _sobre(c["msgOutBg"], chat),
                   "entrante-sel": _sobre(c["msgInBgSelected"], _sobre(c["msgInBg"], chat)),
                   "entrante-sel-chat": _sobre(c["msgInBgSelected"], chat),
                   "propia-sel": _sobre(c["msgOutBgSelected"], chat),
                   "propia-sel-burbuja": _sobre(c["msgOutBgSelected"], _sobre(c["msgOutBg"], chat)),
                   "servicio": _sobre(c["msgServiceBg"], chat)}
        texto_sobre = [("historyTextInFg", "entrante"), ("historyLinkInFg", "entrante"), ("msgInDateFg", "entrante"),
                       ("msgInServiceFg", "entrante"), ("msgInMonoFg", "entrante"), ("historyTextOutFg", "propia"),
                       ("historyLinkOutFg", "propia"), ("msgOutDateFg", "propia"), ("msgOutServiceFg", "propia"),
                       ("msgOutMonoFg", "propia"), ("historyTextInFgSelected", "entrante-sel"),
                       ("historyTextInFgSelected", "entrante-sel-chat"), ("historyTextOutFgSelected", "propia-sel"),
                       ("historyTextOutFgSelected", "propia-sel-burbuja"), ("msgServiceFg", "servicio")]
        texto_sobre += [(f"historyPeer{i}NameFg", "entrante") for i in range(1, 9)]
        for frente, fondo in texto_sobre:
            assert _contraste(c[frente], burbuja[fondo]) >= 4.5, (v, frente, fondo)
        for frente, fondo in [("windowFg", "windowBg"), ("windowSubTextFg", "windowBg"), ("dialogsNameFg", "dialogsBg"),
                              ("dialogsTextFg", "dialogsBg"), ("dialogsNameFgActive", "dialogsBgActive"),
                              ("dialogsTextFgActive", "dialogsBgActive"), ("activeButtonFg", "activeButtonBg"),
                              ("boxTextFg", "boxBg"), ("tooltipFg", "tooltipBg"), ("historyComposeAreaFg", "historyComposeAreaBg"),
                              ("dialogsUnreadFg", "dialogsUnreadBg"), ("dialogsUnreadFg", "dialogsUnreadBgMuted"),
                              ("sideBarTextFg", "sideBarBg"), ("sideBarTextFgActive", "sideBarBgActive"),
                              ("searchedTextMatchFg", "searchedTextMatchBg"), ("toastFg", "toastBg"), ("callNameFg", "callBgOpaque"),
                              ("historyPeerUserpicFg", "historyPeer1UserpicBg"), ("boxTextFgError", "boxBg"),
                              ("boxTextFgGood", "boxBg"), ("contactsStatusFgOnline", "contactsBg"), ("windowActiveTextFg", "windowBg")]:
            assert _contraste(c[frente], _sobre(c[fondo], c["windowBg"])) >= 4.5, (v, frente, fondo)
    # el acento de cada variante en la selección, los botones y los mensajes propios
    for v in ("claro", "oscuro"):
        acento = TOKENS["semanticos"][v]["acento"]["base"]["$value"]["hex"].lower()
        c = tg.colores(TOKENS, v)
        assert c["dialogsBgActive"] == c["activeButtonBg"] == c["windowBgActive"] == acento
        assert c["msgOutBg"][:7] == acento and len(c["msgOutBg"]) == 9


def test_telegram_tabla_sin_claves_huerfanas():
    """Cada clave de la tabla existe en la paleta de Telegram (una clave retirada en una versión nueva se nota aquí)."""
    tg = registro.codigo("telegram")
    assert set(tg.TABLA) <= {k for k, _, _ in tg.plantilla()}
