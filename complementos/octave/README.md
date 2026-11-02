# GNU Octave (`octave`)

Los colores de la interfaz gráfica de Octave con **Lliphi Claro** y **Lliphi Oscuro**: el editor (los lexers de Octave
y Matlab para los `.m`, Bash y Diff, con la misma tabla de sintaxis que los demás editores de Lliphi), la ventana de
órdenes, el editor de variables y el espacio de trabajo. Octave guarda dos «modos de color» a la vez («Second color
mode (light/dark)» en Preferencias): Lliphi Claro va en el primero y Lliphi Oscuro en el segundo, así que pasar de una
variante a otra es cambiar cuatro interruptores.

Es un **complemento**: vive fuera del tema global de Plasma. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); decisión: [`docs/decisiones.md`](../../docs/decisiones.md) §5.41.

## Responsabilidad y formato

- Octave guarda sus colores en `~/.config/octave/octave-gui.ini` junto con todo lo demás (ventanas, atajos, archivos
  recientes), así que no se copia un archivo: el instalador pone `octave-lliphi.py` en
  `~/.local/share/lliphi/variante.d/octave.py`, y ese programa **fusiona** los colores en el ini, clave por clave, sin
  tocar lo demás (las fuentes que ya hubieras elegido en el editor se conservan). Con `--aplicar-tema` lo ejecuta el
  instalador, después de respaldar el ini.
- La interfaz (menús, paneles, barras) no se toca: Octave 11 es Qt 6 y ya sigue el esquema de color de Plasma.
- La ventana de órdenes solo admite cuatro colores (texto, fondo, selección y cursor); los dieciséis ANSI de la
  terminal de Lliphi no tienen dónde ir.
- Octave lee los colores al arrancar: el cambio de variante se ve al abrirlo de nuevo. La vigilancia de
  [`fondo-variante`](../fondo-variante/README.md) cambia el modo en cada cambio de variante, solo si los colores son de
  Lliphi.
- `lliphi.ini` es el mismo fragmento, legible, para quien quiera mirarlo o fusionarlo a mano.
- Construcción: `sintaxis()` de `editores` y `ansi()` de `konsole`. Lo generado: `generado/octave/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos octave --aplicar
XDG_CONFIG_HOME="$XDG_CACHE_HOME/prueba/.config" python3 generado/octave/octave-lliphi.py oscuro --colores   # simula
```

Pruebas: `test_octave_colores` y `test_ide_ciencia_siguen_a_la_variante`. Comprobado con Octave 11.1.0 (Qt 6,
QScintilla 2.14.1) en un HOME de prueba.
