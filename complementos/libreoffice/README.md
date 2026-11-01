# LibreOffice: colores de la aplicación (`libreoffice`)

Dos temas para LibreOffice, Lliphi Claro y Lliphi Oscuro, con las dos piezas que trae el de Dracula: los esquemas de
«Colores de la aplicación» (91 entradas de LibreOffice 26.2; BASIC y SQL con la tabla de sintaxis de los editores) y una
**paleta** `.soc` por variante para los selectores de color de los documentos. Todo va en una extensión `.oxt`
reproducible (los esquemas y una carpeta `palette/` que registra en las rutas de paletas), y suelto como fragmentos
`.xcu` y paletas `.soc` para quien no quiera extensiones.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- No lo instala el instalador: se añade a mano con `unopkg add` (`INSTALL.md`).
- Construcción: usa `sintaxis()` de `editores` (dependencia de construcción declarada).
- Lo generado: `generado/libreoffice/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos libreoffice --aplicar
unopkg add generado/libreoffice/lliphi.oxt          # con LibreOffice cerrado
```

Pruebas: `test_libreoffice_esquemas` (esquemas y extensión) y `test_libreoffice_paletas`. Validado en LibreOffice
26.2.6 con un perfil desechable en una sesión de KWin virtual (`docs/validacion.md` §10).
