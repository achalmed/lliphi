# Editores: VS Code, Positron, VSCodium y Zed (`editores`)

Una extensión de tema mínima de VS Code (que leen también Positron y VSCodium) y un tema de Zed, con la interfaz del
esquema, la sintaxis derivada de los ANSI con una tabla única (`sintaxis()`, que reutiliza `libreoffice`) y la
terminal integrada de Konsole.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- La extensión va a `~/.vscode/extensions/lliphi.lliphi` y, solo si existe su carpeta, a Positron y VSCodium
  (bases condicionales: el instalador nunca las crea); Zed, a `$XDG_CONFIG_HOME/zed/themes/`.
- Lo generado: `generado/editores/{vscode,zed}/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos editores --aplicar
python3 herramientas/instalar.py --modulos editores            # simula la instalación
```

Pruebas: `test_vscode_extension`, `test_zed_tema`.
