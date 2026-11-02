# Xournal++ (`xournalpp`)

Xournal++ con Lliphi (decisiones 5.20; comprobado en 1.3.3).

- **Interfaz y modo oscuro**: Xournal++ es una aplicación GTK 3, así que los da el complemento `gtk` (Breeze con los
  colores de los tokens), y con «Tema: usar el del sistema» (`themeVariant=useSystem`) pasa al oscuro con el
  escritorio. La caja de herramientas flotante, que su `xournalpp.css` pinta en blanco, también la colorea `gtk`.
- **Paleta de bolígrafos** (`palettes/Lliphi.gpl`, formato «GIMP Palette»): trece colores en el orden de los botones de
  color de la barra (`COLOR(0)`…`COLOR(10)`; los dos últimos, en el selector). Las páginas son blancas en las dos
  variantes, así que los de escribir (negro, azul, rojo, verde, morado, cian, ámbar, gris, blanco) son los legibles
  sobre papel —el texto y el acento del claro, el rojo de Nothing, los ANSI del claro—, y los de resaltar (amarillo,
  verde, azul, rosa), los claros del oscuro.
- **Colores de `settings.xml`**: alrededor de las páginas, un gris oscuro (el separador del oscuro), que enmarca la hoja
  blanca en las dos variantes; la selección en el azul del claro, que se ve sobre el papel, y la activa en el rojo; y
  el **recoloreado** del modo oscuro (Preferencias → Ver → Recolorear, desactivado por omisión): papel en el fondo del
  oscuro y tinta en su texto. Son un solo valor para las dos variantes, porque Xournal++ no los cambia con el modo.
- **Fondo de página y rejilla**: se dejan como los elige el usuario en cada documento (página blanca, rejilla y renglones
  de Xournal++): son parte del documento y se imprimen.

Los colores se declaran en `ajustes.json` como `[variante, token]` y salen de los tokens; `settings-lliphi.xml` es el
fragmento para copiar a mano.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos xournalpp --aplicar
python3 herramientas/instalar.py --modulos xournalpp       # simula
```

`aplicar.py` escribe la paleta y los colores en `settings.xml` solo con Xournal++ cerrado (lo reescribe al salir); si
`settings.xml` es un enlace a los dotfiles, el cambio queda en los dotfiles. Pruebas: `test_xournalpp`.
