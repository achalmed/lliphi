# LibreOffice: colores de la aplicación (`libreoffice`)

Dos esquemas de «Colores de la aplicación» (91 entradas de LibreOffice 26.2) como extensión `.oxt` reproducible y como
fragmentos `.xcu`; BASIC y SQL con la tabla de sintaxis de los editores.

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

Pruebas: `test_libreoffice_esquemas`.
