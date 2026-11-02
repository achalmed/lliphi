# Calibre: biblioteca y visor (`calibre`)

Calibre (comprobado en 9.17) con Lliphi en las dos variantes (decisiones 5.22).

## Qué hace hoy Calibre con el escritorio

- **No usa Kvantum.** En Linux pinta con su propio estilo (el de Calibre, sobre Fusion) salvo con
  `CALIBRE_USE_SYSTEM_THEME=1`, así que el tema de Kvantum de Lliphi no le llega.
- **Sí sigue al claro y al oscuro.** Con «Paleta de colores: del sistema» (`color_palette = system`, lo que trae por
  omisión) cambia entre su paleta clara y la oscura con el esquema del escritorio, en vivo.
- **Desde la 7, cada modo admite una paleta con nombre**, en `gui.json` (`light_palettes`, `dark_palettes`): rol de
  `QPalette` → color.

## Qué hace Lliphi

- Dos paletas, **Lliphi Claro** y **Lliphi Oscuro**, con la lógica de Kvantum y del esquema (ventana, vista, botón,
  selección y acento, enlaces, etiquetas, inactivos), como las de cada modo, y `color_palette` en «system».
- **El visor de libros** tiene esquemas propios (`viewer-webengine.json`). Su esquema «Sistema» toma el fondo, el texto
  y, en el oscuro, los enlaces de la paleta de Calibre, así que ya sigue a Lliphi y a la variante (en el claro Calibre
  no pasa el color de los enlaces y quedan en el azul del libro). Se añaden dos esquemas fijos, «Lliphi Claro» y
  «Lliphi Oscuro», con los enlaces de Lliphi, para leer en una variante distinta de la del escritorio; los del usuario
  se conservan.
- **Nada más.** Solo esas claves de esos dos archivos de preferencias de la interfaz, con respaldo y con Calibre
  cerrado. La biblioteca (`metadata.db` y los libros, en la carpeta de la biblioteca) no se abre ni se toca.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos calibre --aplicar
```

`gui-lliphi.json` y `visor-lliphi.json` son los fragmentos; `aplicar.py` los funde (`fundir_gui`, `fundir_visor`).
Pruebas: `test_calibre`.
