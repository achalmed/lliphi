"""Esquemas de «Colores de la aplicación» de LibreOffice (Herramientas → Opciones → LibreOffice → Colores de la
aplicación), dos por generación: «<nombre> Claro» y «<nombre> Oscuro», en tres formas:

- `libreoffice/<id>.xcu`: fragmento `<oor:items>` con los dos esquemas, listo para fusionar a mano en
  `registrymodifications.xcu` del perfil (`~/.config/libreoffice/4/user/`), con LibreOffice cerrado; cada entrada es un
  `<item oor:path=".../ColorSchemes/org.openoffice.Office.UI:ColorScheme['<esquema>']/<Entrada>">` con `Color`
  (entero RGB decimal, 0xRRGGBB) y, donde el esquema lo define, `IsVisible`. Hay además un fragmento por variante
  (`<id>-claro.xcu`, `<id>-oscuro.xcu`).
- `libreoffice/<id>.oxt`: extensión (zip con `META-INF/manifest.xml`, `description.xml` y un `.xcu` de
  `oor:component-data`) que se instala con `unopkg add` o desde el Gestor de extensiones y que LibreOffice lee de
  verdad; su fuente queda en `libreoffice/oxt/`. El zip es reproducible (fechas fijas) para la prueba de deriva.

Fuente del formato y de la lista de entradas (comprobada el 2026-10-18): el esquema de configuración
`org.openoffice.Office.UI` → grupo `ColorScheme` (`CurrentColorScheme`, set `ColorSchemes` de tipo `ColorScheme`)
en `/usr/lib/libreoffice/share/registry/main.xcd` de LibreOffice 26.2.6, con 91 entradas, cada una con `Color`
(`xs:int`) y nueve con `IsVisible` (`Links` y `LinksVisited` falso; `Shadow`, `WriterFieldShadings`,
`WriterIdxShadings`, `WriterDirectCursor`, `CalcHiddenColRow`, `CalcTextOverflow` y `DrawGrid` verdadero), y el
`registrymodifications.xcu` real del perfil del autor (solo lectura), que guarda `CurrentColorScheme` con
`oor:op="fuse"`. Respecto a la lista de 24.8 que recibió el encargo: `ObjectBoundaries` y `WriterScriptIndicator` ya no
existen; se añaden `WriterNonPrintChars`, `HTML*`, `CalcCellFocus`, `CalcHiddenColRow`, `CalcTextOverflow`,
`CalcComments`, `Author1..9` y los colores de interfaz `WindowColor … InactiveBorderColor` (los usa el «tema de
LibreOffice» de 24.8+, `org.openoffice.Office.Common/Appearance/LibreOfficeTheme`; si está desactivado, la interfaz
sigue a Plasma y solo cuentan los colores del documento).

Los colores del documento salen de los semánticos de cada variante; BASIC, SQL y HTML, del grupo `terminal` con la misma
tabla que los editores (`editores.sintaxis`: palabras clave rojo color1, cadenas verde color2, números amarillo
color3, comentarios texto inactivo); los nueve autores de control de cambios, de los ANSI. Ningún color se escribe aquí.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from . import VERSION, escribir, hexa, semanticos
from .editores import sintaxis

RUTA_SET = "/org.openoffice.Office.UI/ColorScheme/ColorSchemes"
CABECERA_XML = "<!-- GENERADO por herramientas/generar.py desde tokens/; no editar -->"
# entradas con IsVisible y su valor por omisión en el esquema de LibreOffice
VISIBLES = {"Links": False, "LinksVisited": False, "Shadow": True, "WriterFieldShadings": True, "WriterIdxShadings": True,
            "WriterDirectCursor": True, "CalcHiddenColRow": True, "CalcTextOverflow": True, "DrawGrid": True}
AUTORES = ("color4", "color2", "color5", "color3", "color6", "color1", "color12", "color10", "color13")


def entero(hex6: str) -> int:
    """`#rrggbb` → entero RGB decimal como lo guarda LibreOffice (`Color` es `xs:int`, 0xRRGGBB)."""
    return int(hex6.lstrip("#"), 16)


def entradas(tokens: dict, variante: str) -> dict[str, str]:
    """Entrada de LibreOffice → hex, en el orden del esquema `main.xcd` (91 entradas)."""
    s = semanticos(tokens, variante)
    t = {k: hexa(v) for k, v in tokens["terminal"][variante].items()}
    x = sintaxis(s, t)
    e = {
        # documento
        "DocColor": s["fondo.vista"], "DocBoundaries": s["borde.separador"], "AppBackground": s["fondo.ventana-alterno"],
        "TableBoundaries": s["borde.separador"], "FontColor": s["texto.normal"], "Links": s["enlace"], "LinksVisited": s["visitado"],
        "Spell": s["estado.error"], "Grammar": s["estado.info"], "SmartTags": t["color5"], "Shadow": s["borde.separador"],
        # Writer
        "WriterTextGrid": s["borde.sutil"], "WriterFieldShadings": s["fondo.ventana-alterno"], "WriterIdxShadings": s["fondo.ventana-alterno"],
        "WriterDirectCursor": s["texto.secundario"], "WriterSectionBoundaries": s["borde.separador"], "WriterHeaderFooterMark": s["texto.inactivo"],
        "WriterPageBreaks": s["acento.suave"], "WriterNonPrintChars": s["texto.inactivo"],
        # HTML (código fuente)
        "HTMLSGML": x["funcion"], "HTMLComment": x["comentario"], "HTMLKeyword": x["palabra-clave"], "HTMLUnknown": x["invalido"],
        # Calc
        "CalcGrid": s["borde.sutil"], "CalcCellFocus": s["acento.base"], "CalcPageBreak": s["acento.suave"], "CalcPageBreakManual": s["acento.base"],
        "CalcPageBreakAutomatic": s["texto.inactivo"], "CalcHiddenColRow": s["acento.suave"], "CalcTextOverflow": s["estado.error"],
        "CalcComments": s["estado.advertencia"], "CalcDetective": s["estado.info"], "CalcDetectiveError": s["estado.error"],
        "CalcReference": t["color6"], "CalcNotesBackground": s["fondo.vista-alterno"], "CalcValue": t["color4"], "CalcFormula": t["color2"],
        "CalcText": s["texto.normal"], "CalcProtectedBackground": s["fondo.ventana-alterno"],
        # Draw
        "DrawGrid": s["borde.separador"],
    }
    e.update({f"Author{i + 1}": t[c] for i, c in enumerate(AUTORES)})
    e.update({
        # IDE de BASIC y editor SQL de Base: misma tabla que los editores
        "BASICEditor": s["fondo.vista"], "BASICIdentifier": x["variable"], "BASICComment": x["comentario"], "BASICNumber": x["numero"],
        "BASICString": x["cadena"], "BASICOperator": x["operador"], "BASICKeyword": x["palabra-clave"], "BASICError": x["invalido"],
        "SQLIdentifier": x["variable"], "SQLNumber": x["numero"], "SQLString": x["cadena"], "SQLOperator": x["operador"],
        "SQLKeyword": x["palabra-clave"], "SQLParameter": x["atributo"], "SQLComment": x["comentario"],
        # interfaz (tema de LibreOffice, 24.8+): la misma lógica que el esquema de Plasma
        "WindowColor": s["fondo.ventana"], "WindowTextColor": s["texto.normal"], "BaseColor": s["fondo.vista"], "ButtonColor": s["fondo.boton"],
        "ButtonTextColor": s["texto.normal"], "AccentColor": s["acento.base"], "DisabledColor": s["fondo.ventana-alterno"],
        "DisabledTextColor": s["texto.inactivo"], "ShadowColor": s["borde.separador"], "SeparatorColor": s["borde.separador"],
        "FaceColor": s["fondo.ventana"], "ActiveColor": s["fondo.encabezado"], "ActiveTextColor": s["texto.normal"],
        "ActiveBorderColor": s["borde.separador"], "FieldColor": s["fondo.vista"], "MenuBarColor": s["fondo.encabezado"],
        "MenuBarTextColor": s["texto.normal"], "MenuBarHighlightColor": s["seleccion.fondo"], "MenuBarHighlightTextColor": s["seleccion.texto"],
        "MenuColor": s["fondo.ventana"], "MenuTextColor": s["texto.normal"], "MenuHighlightColor": s["seleccion.fondo"],
        "MenuHighlightTextColor": s["seleccion.texto"], "MenuBorderColor": s["borde.separador"], "InactiveColor": s["fondo.ventana"],
        "InactiveTextColor": s["texto.inactivo"], "InactiveBorderColor": s["borde.sutil"],
    })
    return e


def items_variante(tokens: dict, marca: dict, variante: str) -> list[str]:
    """Los `<item>` de un esquema, en el formato de `registrymodifications.xcu`: primero el nodo del set, luego una
    entrada por color (y `IsVisible` donde existe)."""
    nombre = escape(marca["nombre_esquema"][variante], {'"': "&quot;", "'": "&apos;"})
    ruta = f"{RUTA_SET}/org.openoffice.Office.UI:ColorScheme[&apos;{nombre}&apos;]"
    lineas = [f'<item oor:path="{RUTA_SET}"><node oor:name="{nombre}" oor:op="replace"/></item>']
    for entrada, color in entradas(tokens, variante).items():
        lineas.append(f'<item oor:path="{ruta}/{entrada}"><prop oor:name="Color" oor:op="fuse"><value>{entero(color)}</value></prop></item>')
        if entrada in VISIBLES:
            lineas.append(f'<item oor:path="{ruta}/{entrada}"><prop oor:name="IsVisible" oor:op="fuse"><value>{str(VISIBLES[entrada]).lower()}</value></prop></item>')
    return lineas


def texto_items(tokens: dict, marca: dict, variantes: tuple[str, ...]) -> str:
    nombres = " y ".join(f"«{marca['nombre_esquema'][v]}»" for v in variantes)
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>', CABECERA_XML,
              f"<!-- {nombres} para LibreOffice ≥ 24.8. Con LibreOffice cerrado, copia los <item> dentro de <oor:items> de",
              "     ~/.config/libreoffice/4/user/registrymodifications.xcu; después elige el esquema en Herramientas → Opciones →",
              "     LibreOffice → Colores de la aplicación. La extensión .oxt de esta carpeta hace lo mismo sin tocar ese archivo. -->",
              '<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">']
    for v in variantes:
        lineas += items_variante(tokens, marca, v)
    lineas.append("</oor:items>")
    return "\n".join(lineas) + "\n"


def texto_component_data(tokens: dict, marca: dict) -> str:
    """El `.xcu` de la extensión: `oor:component-data` de `org.openoffice.Office.UI` con los dos esquemas."""
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>', CABECERA_XML,
              '<oor:component-data xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" oor:name="UI" oor:package="org.openoffice.Office">',
              '  <node oor:name="ColorScheme">', '    <node oor:name="ColorSchemes">']
    for v in ("claro", "oscuro"):
        lineas.append(f'      <node oor:name="{escape(marca["nombre_esquema"][v], {chr(34): "&quot;"})}" oor:op="replace">')
        for entrada, color in entradas(tokens, v).items():
            props = f'<prop oor:name="Color" oor:type="xs:int"><value>{entero(color)}</value></prop>'
            if entrada in VISIBLES:
                props += f'<prop oor:name="IsVisible" oor:type="xs:boolean"><value>{str(VISIBLES[entrada]).lower()}</value></prop>'
            lineas.append(f'        <node oor:name="{entrada}">{props}</node>')
        lineas.append("      </node>")
    lineas += ["    </node>", "  </node>", "</oor:component-data>"]
    return "\n".join(lineas) + "\n"


def texto_manifest(marca: dict) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="http://openoffice.org/2001/manifest">
  <manifest:file-entry manifest:media-type="application/vnd.sun.star.configuration-data" manifest:full-path="{marca['id']}.xcu"/>
</manifest:manifest>
"""


def texto_description(marca: dict) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<description xmlns="http://openoffice.org/extensions/description/2006" xmlns:lo="http://libreoffice.org/extensions/description/2011" xmlns:xlink="http://www.w3.org/1999/xlink">
  <identifier value="{marca['dominio_inverso']}.libreoffice"/>
  <version value="{VERSION}"/>
  <display-name><name lang="es">{escape(marca['nombre'])} para LibreOffice</name></display-name>
  <publisher><name xlink:href="{marca['sitio_tema']}" lang="es">{escape(marca['autor'])}</name></publisher>
  <dependencies><lo:LibreOffice-minimal-version value="24.8" lo:name="LibreOffice 24.8"/></dependencies>
  <extension-description><src lang="es" xlink:href="descripcion.txt"/></extension-description>
</description>
"""


def texto_descripcion(marca: dict) -> str:
    return (f"Esquemas de colores de la aplicación «{marca['nombre_esquema']['claro']}» y «{marca['nombre_esquema']['oscuro']}», "
            f"generados desde los tokens de {marca['nombre']}: {marca['descripcion']} Elige el esquema en Herramientas → Opciones → "
            f"LibreOffice → Colores de la aplicación. Licencia {marca['licencia_activos']}. {marca['sitio_tema']}\n")


def empaquetar_oxt(fuente: Path, destino: Path) -> None:
    """Zip reproducible: fechas fijas, permisos fijos, orden alfabético, deflate; así la prueba de deriva compara bytes."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(p for p in fuente.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(str(f.relative_to(fuente)), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, f.read_bytes())


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    base = destino / "libreoffice"
    escribir(base / f"{marca['id']}.xcu", texto_items(tokens, marca, ("claro", "oscuro")), hechos)
    for v in ("claro", "oscuro"):
        escribir(base / f"{marca['id']}-{v}.xcu", texto_items(tokens, marca, (v,)), hechos)
    oxt = base / "oxt"
    escribir(oxt / "META-INF" / "manifest.xml", texto_manifest(marca), hechos)
    escribir(oxt / "description.xml", texto_description(marca), hechos)
    escribir(oxt / "descripcion.txt", texto_descripcion(marca), hechos)
    escribir(oxt / f"{marca['id']}.xcu", texto_component_data(tokens, marca), hechos)
    paquete = base / f"{marca['id']}.oxt"
    empaquetar_oxt(oxt, paquete)
    hechos.append(paquete)
    return hechos
