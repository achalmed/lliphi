## Instalar

```bash
python3 herramientas/instalar.py --modulos kate --aplicar
```

O a mano: copia `generado/kate/lliphi-claro.theme` y `lliphi-oscuro.theme` a
`~/.local/share/org.kde.syntax-highlighting/themes/`.

Después, en Kate: Configuración → Configurar Kate → Apariencia → Temas de color. Hay dos maneras de usarlo:

- **Que siga a la variante (recomendado)**: marca «Seleccionar automáticamente el tema de color» (en `katerc`,
  `[KTextEditor Renderer] Auto Color Theme Selection=true`, el valor por omisión). Con Lliphi Claro o Lliphi Oscuro
  aplicados y el estilo Kvantum (el que pone el tema global), Kate elige el tema de Lliphi de la variante y lo cambia
  al cambiar de variante. Con el estilo Breeze la paleta es otra y Kate cae en Breeze: usa la segunda manera.
- **Uno fijo**: desmarca esa casilla y elige «Lliphi Oscuro» o «Lliphi Claro» en la lista.

Kate lee los temas al arrancar: ciérralo y ábrelo después de instalar.

**Si Kate no cambia con la variante** (iconos claros sobre una barra clara, el editor en Breeze Dark): Kate tiene su
propio esquema de ventana elegido en Configuración → Esquema de color de la ventana, guardado en `katerc` como
`[UiSettings] ColorScheme=…`, que se impone al de Plasma. Elige ahí «Predeterminado» (o borra esa línea con Kate
cerrado) y Kate seguirá al tema global. Lo mismo vale para cualquier aplicación de KDE con ese menú (Kdenlive, Haruna…).

## Actualizar

Vuelve a instalar; Kate toma el tema de `revision` mayor al arrancar.

## Desinstalar

`python3 herramientas/instalar.py desinstalar --aplicar` (retira lo de todos los módulos) o borra los dos `.theme`; Kate
vuelve a Breeze.
