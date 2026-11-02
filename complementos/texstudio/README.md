# TeXstudio (`texstudio`)

El resaltado del editor de TeXstudio 4.x para **Lliphi Claro** y **Lliphi Oscuro**. La interfaz de TeXstudio ya sigue
el esquema de color de Plasma (y su fondo del editor es el `Base` de la paleta, con Kvantum `fondo.vista`); esto es lo
que faltaba, los formatos de resaltado.

- **TeXstudio sigue solo a la variante.** Guarda sus formatos en dos secciones de `texstudio.ini`, `[formats]` y
  `[formatsDark]`, y usa una u otra según su «modo oscuro», que deduce de la paleta del sistema y vuelve a deducir
  cuando la paleta cambia. Lliphi llena las dos: el claro en `[formats]`, el oscuro en `[formatsDark]` (decisiones 5.6;
  comprobado en la sesión de prueba con TeXstudio abierto, capturas 55).
- **La sintaxis** es la tabla única de los editores, leída como en VS Code con LaTeX Workshop: las órdenes en el azul
  de las funciones, `\begin` y `\end` en el rojo de las palabras clave, los entornos en cian, lo matemático en
  amarillo y cian, los títulos de sección en rojo y negrita, los comentarios en cursiva, las referencias, citas y
  paquetes presentes en magenta y los que faltan en el color de error y subrayados con onda.
- **Los resaltes** (línea actual, selección, búsqueda, diferencias, errores de compilación) son colores del maestro con
  el alfa ya compuesto sobre el fondo del editor, porque TeXstudio guarda los colores sin alfa.

Es un **complemento** (fuera del tema global). Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Lo generado: `generado/texstudio/lliphi.txsprofile`, un perfil de TeXstudio (INI de QSettings) con solo esas dos
  secciones: cada formato es `data\<formato>\<campo>` (`foreground`, `background`, `linescolor`, estilos y
  `priority`), los 88 de `defaultFormats.qxf` de TeXstudio 4.9 salvo los marcadores.
- `aplicar.py`: con `--aplicar-tema`, sustituye en `texstudio.ini` solo `[formats]` y `[formatsDark]`; lo demás queda
  byte a byte. El archivo se respalda antes (`respaldos()`) y, si es un enlace de dotfiles, se escribe el archivo real.
  Con TeXstudio abierto no se toca (lo reescribiría al cerrarse).

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos texstudio --aplicar
```

Pruebas: `test_texstudio_formatos`, `test_texstudio_fundir_respeta_lo_demas`.
