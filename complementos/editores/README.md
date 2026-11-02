# Editores: VS Code, Positron, VSCodium y Zed (`editores`)

Una extensión de tema mínima de VS Code (que leen también Positron y VSCodium) y un tema de Zed, con la interfaz del
esquema, la sintaxis derivada de los ANSI de los tokens con una tabla única (`sintaxis()`, que reutilizan `libreoffice`,
`obsidian`, `kate`, `texstudio` y `vim`) y la terminal integrada con los dieciséis ANSI de Konsole (`konsole.ansi`, sobre
el esquema de Nothing; decisiones 4.30). En Positron cubre también sus claves propias (`colores_positron()`: consola,
barras de acciones, diálogos, explorador de datos, estado del intérprete; decisiones 5.4). `sobre()` compone un color
con alfa sobre un fondo, para los editores que no admiten `#rrggbbaa`.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- La extensión se empaqueta como `vscode/lliphi.vsix` (reproducible) y `aplicar.py` la instala con
  `--install-extension` de cada editor de la familia que esté en el PATH (`tras_instalar()`, y la retira
  `al_desinstalar()`): copiada a mano, el editor no la registra y no la carga (decisiones 5.9). Zed, a
  `$XDG_CONFIG_HOME/zed/themes/`.
- Lo generado: `generado/editores/{vscode,zed}/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos editores --aplicar
python3 herramientas/instalar.py --modulos editores            # simula la instalación
```

Pruebas: `test_vscode_extension`, `test_positron_entero`, `test_zed_tema`.
