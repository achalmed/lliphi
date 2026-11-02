# Sitios web: DuckDuckGo y GitHub (`sitios-web`)

Lliphi Claro y Lliphi Oscuro en sitios web, como **estilos de usuario**: un `<sitio>.user.css` por sitio, en formato
UserCSS (lo instala Stylus en Zen y en Chrome; Zen también lo lee sin extensión desde `userContent.css`). Cada estilo
solo redefine las **variables CSS del sitio**, con `!important`, y elige la variante por el modo claro u oscuro; no
lleva selectores frágiles de la página, así que resiste los cambios del sitio. Para DuckDuckGo hay además sus
**ajustes de apariencia** con los colores de Lliphi, para usarlo sin extensión.

Es un **complemento**: no es parte de un `Plasma/LookAndFeel`. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); por qué y cómo: decisión 5.12 de
[`docs/decisiones.md`](../../docs/decisiones.md). Instalación: [`INSTALL.md`](INSTALL.md).

## Responsabilidad y formato

| archivo de `generado/sitios-web/` | qué es |
|---|---|
| `duckduckgo.user.css` | DuckDuckGo: las variables de sus tres sistemas de diseño (`--theme-col-*`, `--sds-color-*`, `--ds-*`), Inter, y el fondo de la página y de la cabecera (que su tema oscuro pinta con un gris fijo) sobre esas variables; la variante sigue a `prefers-color-scheme` |
| `github.user.css` | GitHub: las variables funcionales de Primer (`--bgColor-*`, `--fgColor-*`, `--borderColor-*`, `--button-*`, `--control-*`, `--diffBlob-*`, `--prettylights-syntax-*`, `--codeMirror-syntax-*`, `--ansi-*`, `--contribution-*`, `--fontStack-*`); la variante sigue a `data-color-mode` de GitHub y, en «Sincronizar con el sistema», a `prefers-color-scheme` |
| `duckduckgo/ajustes.json` | los parámetros de apariencia de DuckDuckGo de cada variante (`kae`, `k7`, `kj`, `k8`, `k9`, `kaa`, `kx`, `k21`, `kt`, `ka`), la URL de inicio y la plantilla de buscador (`?q=%s&…`) |
| `duckduckgo/marcadores.html` | las dos URL de inicio como marcadores (formato de Netscape, que importan Zen y Chrome) |

Identidad, la misma que el resto de Lliphi:

- neutros de los semánticos (`fondo.vista` para la página, `fondo.ventana` para cabeceras, tarjetas y controles);
- el acento solo en los enlaces (`enlace`), el foco, la selección, la pestaña elegida y el botón principal (en GitHub,
  el verde; en DuckDuckGo, el amarillo de la marca);
- los rellenos que llevan texto blanco (insignias, contadores, estados «Open», «Closed», «Merged») con un fondo que
  lo admite: en el oscuro, los estados de los semánticos son claros, así que los rellenos toman los del claro y el
  peligro, el rojo de Nothing (`Paleta.relleno` de `construir.py`);
- el código de GitHub con `sintaxis()` de `editores` (la misma tabla que VS Code, Zed, LibreOffice y Obsidian), los
  registros de Actions con los ANSI de la terminal, los diffs y el gráfico de contribuciones con los estados;
- Inter en la interfaz y JetBrains Mono en el código.

## Añadir un sitio

Un archivo `<sitio>.py` en esta carpeta con la interfaz de los sitios (la describe `construir.py`): `NOMBRE`,
`DOMINIOS`, `DESCRIPCION`, `AMBITOS` (dónde vale cada variante), `variables(p)`, `reglas(p)`, `comunes(fuentes)`,
`CONTRASTE` y `FONDO`, y `extras(tokens, marca)` si el sitio necesita otros archivos. Después, su id en `SITIOS`, su
archivo en `modulo.json` y su fila arriba. Las pruebas recorren `SITIOS`: no hace falta una prueba nueva para lo común.

Para encontrar las variables de un sitio: abrir la página, y en la consola listar las propiedades `--*` de las reglas
de `:root` o de `html` (las de su tema) con sus valores; usar solo las semánticas (fondo, texto, borde, acento,
estado), nunca las de la paleta cruda del sitio.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos sitios-web            # simula
.venv/bin/python herramientas/generar.py --modulos sitios-web --aplicar
.venv/bin/pytest -k sitios_web
```

Pruebas: `test_sitios_web_estilos` (UserCSS válido y anidado correcto, solo los dominios del sitio, cada variante igual
a los tokens en cada ámbito, cada color del maestro con alfa a lo sumo, contraste ≥ 4,5:1 en cada par de `CONTRASTE`
con los fondos translúcidos mezclados sobre el de la página, nada personal), `test_sitios_web_github_primer` (el acento
solo donde va, sintaxis, diffs, fuentes) y `test_sitios_web_duckduckgo_ajustes`.

Para verlo sin instalar nada: abrir el sitio en un navegador cualquiera e inyectar el contenido del estilo (sin la
envoltura `@-moz-document`) como hoja de estilos desde la consola; así se tomaron las capturas
`muestras/capturas/*-sitios-*.png`.
