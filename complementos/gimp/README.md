# GIMP: tema de interfaz y paletas (`gimp`)

Un tema de interfaz para GIMP 3 (comprobado en 3.2.2), **Lliphi**, con sus dos variantes —Lliphi Claro y Lliphi
Oscuro—, y dos paletas de colores (decisiones 5.21).

## El tema

Deriva del tema **Default** de GIMP 3.2 (GPL-3.0-or-later, copiado sin cambios a
[`fuentes/base/GIMP-Default/`](../../fuentes/base/GIMP-Default/ORIGEN.md)). Default ya está hecho para esto: sus tres
archivos de color (`gimp-light.css`, `gimp-gray.css`, `gimp-dark.css`) definen diecisiete colores con nombre e importan
`common-<luz>.css`, donde está todo lo demás. Lliphi escribe esos tres archivos desde los tokens y copia los comunes:

- `gimp-light.css` con Lliphi Claro; `gimp-dark.css` y `gimp-gray.css` con Lliphi Oscuro (Lliphi no tiene gris).
- Una capa propia al final de cada uno: la fila elegida en listas y vistas (capas, canales, pinceles), el elemento del
  menú bajo el ratón, las casillas, los interruptores y el progreso en el acento de la variante, como en Kvantum. El
  lienzo y el resto, neutros, como quiere GIMP para no sesgar la percepción del color.
- `common.css` importa `../System/gimp.css`, que fuera de la carpeta del sistema no existe: pasa a `system.css` (la hoja
  del tema System, copiada). Los separadores (`ui/*.svg`) toman el gris de `texto.inactivo`.

Un tema con dos variantes, como hace GIMP 3 y como Kvantum (decisiones 4.19): con el **esquema de color «Sistema»**
(`(theme-color-scheme system)` en `gimprc`), GIMP elige el claro o el oscuro según el escritorio y lo cambia en vivo,
sin que `fondo-variante` tenga que hacer nada.

## Las paletas

`Lliphi Claro.gpl` y `Lliphi Oscuro.gpl`: los mismos colores que las paletas de LibreOffice (neutros, acento, estados y
los dieciséis ANSI de los tokens, sin repetidos), en filas de dieciséis. El formato «GIMP Palette» lo leen también
Inkscape y Krita.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos gimp --aplicar
python3 herramientas/instalar.py --modulos gimp              # simula
```

`aplicar.py` pone `(theme "Lliphi")` y `(theme-color-scheme system)` en `gimprc`, solo con GIMP cerrado (GIMP lo
reescribe al salir). La carpeta de GIMP depende de su versión: `~/.config/GIMP/3.2/`. Pruebas: `test_gimp_tema`,
`test_gimp_aplicar`.
