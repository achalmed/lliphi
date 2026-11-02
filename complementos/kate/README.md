# Kate (`kate`)

El tema del editor de Kate, que comparten KWrite, KDevelop y todo programa con KTextEditor: **Lliphi Claro** y
**Lliphi Oscuro** como temas de KSyntaxHighlighting. La interfaz de Kate ya sigue el esquema de color de Plasma; esto
es lo que faltaba, el área de texto.

- **La sintaxis** es la tabla única de los editores (`complementos/editores`, `sintaxis()`): palabras clave en rojo,
  cadenas en verde, números en amarillo, funciones en azul, tipos en cian, atributos en magenta y comentarios en el
  texto inactivo, como en VS Code, Positron, Zed, Obsidian y LibreOffice.
- **El fondo y la selección** son los de la paleta que Kvantum da a las aplicaciones (`kvantum.paleta_qt`: `fondo.vista`
  y `seleccion.fondo`): Kate, con «Seleccionar automáticamente el tema de color» activo (su valor por omisión), elige el
  tema cuyo fondo es el `Base` de la paleta y cuya selección es su `Highlight`. Así **Kate sigue solo a la variante**:
  al pasar de Lliphi Claro a Lliphi Oscuro cambia de tema también en las ventanas abiertas, sin tocar `katerc`
  (decisiones 5.4; comprobado en la sesión de prueba, capturas 54).
- Los resaltes (línea actual, búsqueda, plegado, plantillas) son colores del maestro con el alfa ya compuesto sobre el
  fondo, porque el formato no mezcla el alfa.

Es un **complemento** (fuera del tema global). Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: JSON de KSyntaxHighlighting 6 (`metadata`, `text-styles`, `editor-colors`) en
  `$XDG_DATA_HOME/org.kde.syntax-highlighting/themes/`; la `revision` sube con la versión de Lliphi.
- Sin `aplicar.py`: no hace falta escribir nada en la configuración de Kate.
- Lo generado: `generado/kate/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos kate --aplicar
python3 herramientas/instalar.py --modulos kate               # simula la instalación
```

Prueba: `test_kate_temas`.
