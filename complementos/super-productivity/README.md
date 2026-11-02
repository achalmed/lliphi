# Super Productivity (`super-productivity`)

Un tema de [Super Productivity](https://super-productivity.com) con **Lliphi Claro** y **Lliphi Oscuro** en un solo
archivo, `lliphi.css`. Con «Modo oscuro: Sistema» (lo predeterminado) la aplicación pasa sola, y en vivo, de una
variante a otra con el escritorio.

Es un **complemento**: vive fuera del tema global de Plasma. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); decisión: [`docs/decisiones.md`](../../docs/decisiones.md) §5.48.

## Responsabilidad y formato

- Super Productivity (≥ 18) acepta CSS propio por dos vías y el mismo archivo vale para las dos:
  - **`styles.css`** en su carpeta de datos (`~/.config/superProductivity/`; la del Flatpak o la del Snap si es el
    caso): al cargar la ventana lo inyecta con `webContents.insertCSS`. Es la que usa el instalador: un archivo que se
    copia y se retira, sin abrir la aplicación ni tocar sus datos.
  - **Un tema de usuario**, desde Ajustes → General → «Instalar tema…»: la aplicación lo valida (sin `url()`, `src()`
    ni `@import`), lo guarda en su IndexedDB y aparece como «Lliphi» en «Tema (experimental)».
- Solo redefine **variables de la aplicación**, en las capas de su «contrato de temas»
  (`src/styles/_css-variables.scss`): la escala de superficies (`--surface-0…4`) y de texto (`--ink*`), los bordes, la
  categoría B (tareas, subtareas, notas, paneles, barras de desplazamiento), los grises fijos del oscuro
  (`--dark0…24`), la paleta de Material (primario y acento con el acento de Lliphi, advertencia con el error) y los
  contenedores y textos de Material que la aplicación deja fijos (diálogos, menús, listas, campos, calendarios,
  avisos). Además, JetBrains Mono para el código y los radios de Lliphi.
- Las hojas de `insertCSS` van **antes** que las de la aplicación en la cascada, así que cada selector lleva un punto
  más de especificidad que el suyo: `html body:not(.isDarkTheme)` para el claro, `html body.isDarkTheme` para el
  oscuro y `html:root` para lo común. El claro no puede ir en `body` a secas: ganaría a los alias de la aplicación
  (que tienen especificidad cero) también en el oscuro.
- La paleta de Material la pone la aplicación **en línea** en `<html>` con el color del proyecto o la etiqueta en uso;
  por eso va en `:root` con `!important`, y la del oscuro en `:root:has(> body.isDarkTheme)`. Consecuencia: los
  colores de proyecto dejan de teñir la interfaz.
- La letra de la interfaz es la de la aplicación: Angular Material la escribe literal en sus reglas de tipografía, no en
  variables, y cambiarla en parte mezclaría dos letras. Su lista empieza por las del sistema (Roboto si está
  instalada; si no, Inter).
- Seguir a la variante: con «Modo oscuro: Sistema», la aplicación usa `prefers-color-scheme`, que en Plasma da el portal
  según el esquema de color en uso; no hace falta programa en `variante.d/`.
- Lo generado: `generado/super-productivity/lliphi.css`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos super-productivity --aplicar
python3 herramientas/sesion.py arrancar --virtual --aplicar     # y en la sesión, Super Productivity una vez
```

Pruebas: `test_super_productivity_tema` (estructura, especificidad, colores del maestro, contraste ≥ 4,5:1 y las
reglas del validador de la aplicación) y `test_super_productivity_instalacion` (la base condicional). Comprobado con
Super Productivity 18.10.0 (deb, Electron 41) en la sesión de prueba, en las dos variantes y por las dos vías.
