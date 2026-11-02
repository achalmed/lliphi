# RStudio (`rstudio`)

Dos temas para RStudio, **Lliphi Claro** y **Lliphi Oscuro**, en el formato propio de RStudio (`.rstheme`, CSS sobre el
editor Ace): el editor de código y de R Markdown con la misma tabla de sintaxis que los demás editores de Lliphi, la
consola de R y la terminal integrada con los dieciséis colores de Konsole, los paréntesis y las guías de sangría de
colores, y la interfaz entera (paneles, pestañas, barras, menús) clara u oscura según la variante (`rs-theme-is-dark`).

Es un **complemento**: vive fuera del tema global de Plasma. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); decisión: [`docs/decisiones.md`](../../docs/decisiones.md) §5.40.

## Responsabilidad y formato

- Lo instala el instalador: los dos `.rstheme` en `~/.config/rstudio/themes/` y `variante-rstudio.py` en
  `~/.local/share/lliphi/variante.d/rstudio.py`. Con `--aplicar-tema` además pone el tema de la variante en
  `editor_theme` de `~/.config/rstudio/rstudio-prefs.json` (respaldado antes; lo demás del archivo no se toca).
- RStudio no sigue solo al modo claro u oscuro del escritorio: lo hace la vigilancia de
  [`fondo-variante`](../fondo-variante/README.md), que en cada cambio de variante llama a `variante-rstudio.py`; solo
  cambia `editor_theme` si ya era un tema de Lliphi. RStudio lee ese archivo al arrancar (abierto, no lo relee), así que
  el cambio se ve al abrirlo de nuevo.
- Construcción: `sintaxis()` de `editores` y `ansi()` de `konsole` (dependencias declaradas). Los colores 16 a 255 de
  xterm se calculan con la fórmula estándar, como en los temas que trae RStudio.
- Lo generado: `generado/rstudio/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos rstudio --aplicar
.venv/bin/python herramientas/instalar.py --modulos rstudio            # simula
```

Pruebas: `test_rstudio_temas` y `test_ide_ciencia_siguen_a_la_variante` (`pruebas/test_proyecto.py`). Comprobado con
RStudio 2026.05.1.
