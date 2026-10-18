#!/usr/bin/env python3
"""Boceto del escritorio: composición prevista (panel, dock, ventana, menú, notificación) con los tokens.

NO es una captura: es un dibujo en HTML con los colores, radios y espacios de `tokens/tokens.json`, para
juzgar la dirección artística antes de implementar el estilo de Plasma. Las capturas reales llegan en la
fase 7 y se guardan aparte, con su nombre de variante y caso.

Uso:  .venv/bin/python herramientas/boceto.py            # escribe muestras/boceto-claro.png y boceto-oscuro.png
Requiere Google Chrome o Chromium para imprimir el HTML a PNG.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOKENS = RAIZ / "tokens" / "tokens.json"
MARCA = RAIZ / "tokens" / "marca.json"
SALIDA = RAIZ / "muestras"

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{nombre} · boceto {variante}</title>
<style>
:root {{ {vars} }}
* {{ box-sizing: border-box; }}
body {{ margin:0; width:1600px; height:900px; overflow:hidden; font-family: Inter, "Noto Sans", sans-serif; font-size:14px;
       color: var(--texto-normal); background: {fondo}; position:relative; }}
.panel {{ position:absolute; top:0; left:0; right:0; height:36px; background: var(--fondo-ventana); border-bottom:1px solid var(--borde-sutil);
         display:flex; align-items:center; padding:0 12px; gap:16px; }}
.panel .app {{ font-weight:600; }}
.panel .reloj {{ margin-left:auto; font-variant-numeric: tabular-nums; }}
.panel .bandeja {{ display:flex; gap:12px; color: var(--texto-secundario); }}
.dock {{ position:absolute; bottom:12px; left:50%; transform:translateX(-50%); height:56px; padding:0 10px; border-radius:var(--radio-panel);
        background: var(--fondo-ventana); border:1px solid var(--borde-sutil); box-shadow: var(--sombra); display:flex; align-items:center; gap:10px; }}
.dock .icono {{ width:40px; height:40px; border-radius:10px; background: var(--fondo-boton); position:relative; }}
.dock .icono.activo::after {{ content:""; position:absolute; bottom:-7px; left:14px; width:12px; height:3px; border-radius:2px; background: var(--acento-base); }}
.ventana {{ position:absolute; top:84px; left:120px; width:980px; height:620px; border-radius:var(--radio-ventana); overflow:hidden;
           background: var(--fondo-ventana); border:1px solid var(--borde-sutil); box-shadow: var(--sombra); display:flex; flex-direction:column; }}
.titulo {{ height:38px; background: var(--fondo-encabezado); display:flex; align-items:center; padding:0 12px; gap:8px; border-bottom:1px solid var(--borde-sutil); }}
.titulo .nombre {{ flex:1; text-align:center; font-weight:500; }}
.titulo .btn {{ width:12px; height:12px; border-radius:50%; border:1.5px solid var(--texto-inactivo); }}
.titulo .btn.cerrar {{ border-color: var(--acento-base); }}
.herramientas {{ height:44px; display:flex; align-items:center; gap:8px; padding:0 12px; }}
.herramientas .b {{ padding:6px 12px; border-radius:var(--radio-control); background: var(--fondo-boton); border:1px solid var(--borde-sutil); }}
.herramientas .b.primario {{ background: var(--acento-base); color: var(--texto-sobre-acento); border-color: transparent; }}
.herramientas .campo {{ margin-left:auto; width:260px; padding:6px 10px; border-radius:var(--radio-control); background: var(--fondo-vista); border:2px solid var(--foco); }}
.cuerpo {{ flex:1; display:flex; }}
.lateral {{ width:200px; padding:8px; display:flex; flex-direction:column; gap:2px; border-right:1px solid var(--borde-sutil); }}
.lateral .item {{ padding:6px 10px; border-radius:var(--radio-control); }}
.lateral .item.sel {{ background: var(--seleccion-fondo); color: var(--seleccion-texto); }}
.vista {{ flex:1; background: var(--fondo-vista); padding:12px; display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; align-content:start; }}
.archivo {{ border-radius:var(--radio-control); padding:10px; display:flex; flex-direction:column; align-items:center; gap:6px; }}
.archivo .ic {{ width:56px; height:44px; border-radius:6px; background: var(--fondo-boton); }}
.archivo.sel {{ background: var(--seleccion-fondo); color: var(--seleccion-texto); }}
.archivo.sel .ic {{ background: var(--acento-suave); }}
.estado {{ height:28px; border-top:1px solid var(--borde-sutil); padding:0 12px; display:flex; align-items:center; color: var(--texto-secundario); font-size:13px; }}
.menu {{ position:absolute; top:44px; left:12px; width:300px; border-radius:var(--radio-menu); background: var(--fondo-ventana); border:1px solid var(--borde-sutil); box-shadow: var(--sombra); padding:8px; }}
.menu .cab {{ padding:6px 10px; color: var(--texto-secundario); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
.menu .it {{ padding:8px 10px; border-radius:var(--radio-control); display:flex; gap:10px; align-items:center; }}
.menu .it .ic {{ width:20px; height:20px; border-radius:5px; background: var(--fondo-boton); }}
.menu .it.hover {{ background: color-mix(in srgb, var(--hover) 14%, transparent); outline:1px solid var(--hover); }}
.menu .busca {{ margin:4px 2px 8px; padding:7px 10px; border-radius:var(--radio-control); background: var(--fondo-vista); border:1px solid var(--borde-separador); color: var(--texto-inactivo); }}
.noti {{ position:absolute; right:16px; bottom:84px; width:340px; border-radius:var(--radio-menu); background: var(--fondo-ventana); border:1px solid var(--borde-sutil); box-shadow: var(--sombra); padding:12px 14px; }}
.noti .t {{ font-weight:600; margin-bottom:4px; }}
.noti .s {{ color: var(--texto-secundario); font-size:13px; }}
.noti .barra {{ margin-top:10px; height:4px; border-radius:2px; background: var(--fondo-boton); }}
.noti .barra i {{ display:block; width:62%; height:100%; border-radius:2px; background: var(--acento-base); }}
.tooltip {{ position:absolute; left:680px; top:730px; padding:6px 10px; border-radius:var(--radio-menu); background: var(--fondo-tooltip); color: var(--texto-tooltip); font-size:13px; }}
.rotulo {{ position:absolute; right:16px; top:44px; font-size:12px; color: var(--texto-inactivo); }}
.estados {{ position:absolute; right:16px; top:100px; width:360px; display:flex; flex-direction:column; gap:6px; font-size:13px; }}
.estados div {{ padding:6px 10px; border-radius:var(--radio-control); background: var(--fondo-ventana); border:1px solid var(--borde-sutil); }}
.estados .err {{ color: var(--estado-error); }} .estados .adv {{ color: var(--estado-advertencia); }} .estados .ok {{ color: var(--estado-exito); }} .estados .inf {{ color: var(--estado-info); }}
</style></head><body>
<div class="panel"><span class="app">{nombre}</span><span>Archivo</span><span>Editar</span><span>Ver</span>
  <span class="reloj">sáb 18 oct · 13:40</span><span class="bandeja"><span>◐</span><span>▮▮▮</span><span>♪</span></span></div>
<div class="menu"><div class="busca">Buscar…</div><div class="cab">Favoritos</div>
  <div class="it"><span class="ic"></span>Dolphin</div><div class="it hover"><span class="ic"></span>Konsole</div>
  <div class="it"><span class="ic"></span>Kate</div><div class="it"><span class="ic"></span>Preferencias del sistema</div></div>
<div class="ventana"><div class="titulo"><span class="nombre">Documentos — Dolphin</span><span class="btn"></span><span class="btn"></span><span class="btn cerrar"></span></div>
  <div class="herramientas"><span class="b">Atrás</span><span class="b">Adelante</span><span class="b primario">Nueva carpeta</span><span class="campo">Texto con foco</span></div>
  <div class="cuerpo"><div class="lateral"><div class="item">Inicio</div><div class="item sel">Documentos</div><div class="item">Imágenes</div><div class="item">Descargas</div><div class="item">Papelera</div></div>
    <div class="vista">{archivos}</div></div>
  <div class="estado">6 carpetas, 2 archivos (1,4 MB) · 1 seleccionado</div></div>
<div class="estados"><div class="err">Error: no se pudo guardar el archivo</div><div class="adv">Advertencia: batería al 15 %</div><div class="ok">Copia terminada</div><div class="inf">Actualizaciones disponibles</div></div>
<div class="noti"><div class="t">Copiando archivos</div><div class="s">tesis.pdf → Documentos · 62 %</div><div class="barra"><i></i></div></div>
<div class="tooltip">Tooltip: Nueva carpeta (Ctrl+Mayús+N)</div>
<div class="dock"><span class="icono activo"></span><span class="icono"></span><span class="icono activo"></span><span class="icono"></span><span class="icono"></span></div>
<div class="rotulo">boceto · no es una captura · {nombre} {variante}</div>
</body></html>"""


def aplanar(grupo: dict, prefijo: str = "") -> dict[str, str]:
    plano = {}
    for k, v in grupo.items():
        if isinstance(v, dict) and "$value" in v and isinstance(v["$value"], dict) and "hex" in v["$value"]:
            plano[prefijo + k] = v["$value"]["hex"]
        elif isinstance(v, dict) and "$value" not in v:
            plano.update(aplanar(v, prefijo + k + "-"))
    return plano


def main() -> int:
    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    marca = json.loads(MARCA.read_text(encoding="utf-8"))
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        print("falta Chrome/Chromium"); return 1
    SALIDA.mkdir(exist_ok=True)
    archivos = "".join(f'<div class="archivo{" sel" if i == 2 else ""}"><span class="ic"></span>{n}</div>'
                       for i, n in enumerate(("Clases", "Tesis", "Radio", "Fotos", "informe.pdf", "datos.csv", "Proyectos", "Lecturas")))
    for variante in ("claro", "oscuro"):
        plano = aplanar(tokens["semanticos"][variante])
        vars_ = " ".join(f"--{k}: {v};" for k, v in plano.items())
        r = tokens["radio"]
        vars_ += f' --radio-control: {r["control"]["$value"]["value"]}px; --radio-menu: {r["menu"]["$value"]["value"]}px;'
        vars_ += f' --radio-ventana: {r["ventana"]["$value"]["value"]}px; --radio-panel: {r["panel-flotante"]["$value"]["value"]}px;'
        vars_ += " --sombra: 0 8px 24px rgba(0,0,0,.18);" if variante == "claro" else " --sombra: 0 8px 24px rgba(0,0,0,.45);"
        fondo = ("linear-gradient(160deg, #cfd3d8 0%, #e8e6e3 60%, #f3efe9 100%)" if variante == "claro"
                 else "linear-gradient(160deg, #0d0f12 0%, #1a1c20 55%, #2a2522 100%)")
        html = PLANTILLA.format(nombre=marca["nombre"], variante=variante, vars=vars_, fondo=fondo, archivos=archivos)
        h = SALIDA / f"boceto-{variante}.html"; h.write_text(html, encoding="utf-8")
        png = SALIDA / f"boceto-{variante}.png"
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1600,900",
                        f"--screenshot={png}", f"file://{h}"], check=True, capture_output=True)
        h.unlink()
        print(f"escrito {png.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
