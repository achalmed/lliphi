# Spyder (`spyder`)

Dos esquemas de sintaxis para Spyder, **Lliphi Claro** y **Lliphi Oscuro**, con la misma tabla que los demás editores
de Lliphi. Spyder los usa en el editor, la consola IPython, el historial y la ayuda; con la interfaz en «automático»
(`ui_theme = automatic`) Spyder pone clara u oscura la ventana entera según el esquema. La consola IPython lleva además
los dieciséis colores de la terminal de Lliphi (los de Konsole), para las trazas de error y la salida en color.

Es un **complemento**: vive fuera del tema global de Plasma. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); decisión: [`docs/decisiones.md`](../../docs/decisiones.md) §5.42.

## Responsabilidad y formato

- Spyder guarda los esquemas en `~/.config/spyder-py3/config/spyder.ini` junto con todo lo demás, así que no se copia un
  archivo: el instalador pone `spyder-lliphi.py` en `~/.local/share/lliphi/variante.d/spyder.py` y `consola.py` en
  `~/.local/share/lliphi/spyder/`, y el programa **fusiona** en el ini las claves de los dos esquemas, `names`,
  `selected` y `ui_theme`, sin tocar lo demás. Con `--aplicar-tema` lo ejecuta el instalador, después de respaldar el ini.
- Spyder reescribe `spyder.ini` entero mientras está abierto: con Spyder abierto el programa no escribe nada y lo dice.
- Los colores ANSI de la consola (qtconsole) son fijos, pero atiende la secuencia OSC 4 de xterm: `consola.py`, que Spyder
  ejecuta al arrancar cada consola (`startup/run_file`), los cambia por los de la variante del esquema elegido. Solo se
  configura si la consola no ejecutaba ya otro archivo al arrancar.
- Spyder cambia el esquema de sintaxis al vuelo, pero la interfaz solo al reiniciarse. La vigilancia de
  [`fondo-variante`](../fondo-variante/README.md) cambia el esquema en cada cambio de variante, si es de Lliphi y Spyder
  está cerrado.
- La interfaz (paneles, barras, menús) es la paleta propia de Spyder en su versión clara u oscura (QDarkStyle), no la
  de Plasma: Spyder no deja cambiarla sin tocar su código. Lo de Lliphi son el editor, la consola y su sintaxis.
- Construcción: `sintaxis()` de `editores` y `ansi()` de `konsole`. Lo generado: `generado/spyder/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos spyder --aplicar
XDG_CONFIG_HOME="$XDG_CACHE_HOME/prueba/.config" python3 generado/spyder/spyder-lliphi.py oscuro --esquemas   # simula
```

Pruebas: `test_spyder_esquemas` y `test_ide_ciencia_siguen_a_la_variante`. Comprobado con Spyder 6.1.0 (qtconsole 5.7)
del entorno base de Anaconda.
