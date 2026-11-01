# Obsidian: tema Lliphi (`obsidian`)

Un tema de Obsidian 1.x, `theme.css`, con Lliphi Claro y Lliphi Oscuro en un solo archivo: solo redefine las variables
de la aplicación (neutros, acento por variante, los ocho colores con nombre, estados, tipografía, radios, sintaxis del
código y las llamadas de Zotero), sin selectores de la interfaz.

Es un **complemento**: no es parte de un `Plasma/LookAndFeel`. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md); por qué y cómo se tradujeron los tokens: decisión 5.1 de
[`docs/decisiones.md`](../../docs/decisiones.md).

## Responsabilidad y formato

- Entrega `generado/obsidian/theme.css`. Obsidian lo lee de `<vault>/.obsidian/themes/Lliphi/` junto con un
  `manifest.json`, que no es de aquí: el tema se publica en su repositorio propio,
  [achalmed/obsidian-lliphi](https://github.com/achalmed/obsidian-lliphi), que trae este archivo con `traer.sh`, lleva
  su versión y lo instala en un vault.
- No lo instala el instalador de Lliphi: un vault no es una carpeta XDG (`INSTALL.md`).
- Construcción: usa `sintaxis()` de `editores` (dependencia de construcción declarada), así que el código se ve igual
  que en VS Code, Zed y LibreOffice.

| variable de Obsidian | sale de |
|---|---|
| `--color-base-00…100` | `fondo.vista` (la nota), `fondo.ventana` (barras laterales), bordes y los tres textos de los semánticos |
| `--accent-h/s/l`, `--color-accent*`, `--interactive-accent*` | `acento.base`, `acento.suave`, `acento.texto`, `hover` |
| `--text-accent` (enlaces, etiquetas) | `enlace` |
| `--color-red…pink` y `-rgb` | ANSI de `terminal` (rojo 1, amarillo 3, verde 2, cian 6, azul 4, morado 5, rosa 13); naranja = `estado.advertencia` |
| `--text-error/warning/success`, `--background-modifier-*` | `estado.*`; el fondo de los botones de peligro del oscuro es `acento.base` |
| `--code-*` | la tabla `sintaxis()` de `editores` |
| `--font-*-theme`, `--radius-*` | `tipografia`, `radio` |
| `--h1…h6-color` | rojo, naranja, amarillo, verde, azul, morado |
| `--callout-color` de `[!tipo\|#ffd400]` | el color con nombre de cada color de anotación de Zotero |

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos obsidian            # simula
.venv/bin/python herramientas/generar.py --modulos obsidian --aplicar
.venv/bin/pytest -k obsidian
```

Para verlo, en el repositorio del tema: `./traer.sh <esta-copia-de-lliphi> --aplicar` y `./instalar.sh <vault> --aplicar`;
Obsidian recarga el tema al cambiar el archivo.

Pruebas: `test_obsidian_tema` (variables requeridas en las dos variantes, valores contra los tokens, ternas `-rgb`
coherentes, ningún color fuera del maestro, nada de Minimal, las ocho llamadas de Zotero).
