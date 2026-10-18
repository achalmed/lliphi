## Instalar a mano

El instalador (`python3 herramientas/instalar.py --modulos editores --aplicar`) copia la extensión a
`~/.vscode/extensions/lliphi.lliphi/` (o a `$VSCODE_EXTENSIONS` si está definida) y el tema de Zed a
`~/.config/zed/themes/lliphi.json`. Ninguno de los dos editores lo activa solo.

### VS Code

1. Copia la carpeta `vscode/lliphi/` a `~/.vscode/extensions/lliphi.lliphi/` (VSCodium: `~/.vscode-oss/extensions/`).
2. Reinicia VS Code y elige el tema: `Ctrl+K Ctrl+T` → «Lliphi Oscuro» o «Lliphi Claro»; o en `settings.json`:

```json
"workbench.colorTheme": "Lliphi Oscuro"
```

Para que siga al sistema: `"window.autoDetectColorScheme": true`, `"workbench.preferredDarkColorTheme": "Lliphi Oscuro"`,
`"workbench.preferredLightColorTheme": "Lliphi Claro"`.

### Zed

1. Copia `zed/lliphi.json` a `~/.config/zed/themes/`.
2. En Zed: paleta de órdenes → `theme selector: toggle` → «Lliphi Oscuro» o «Lliphi Claro»; o en `settings.json`:

```json
"theme": { "mode": "system", "dark": "Lliphi Oscuro", "light": "Lliphi Claro" }
```

Zed relee la carpeta de temas al vuelo.

## Actualizar

Sustituye la carpeta de la extensión y el archivo de Zed; los nombres de los temas no cambian.

## Desinstalar

Elige otro tema en cada editor y borra `~/.vscode/extensions/lliphi.lliphi/` y `~/.config/zed/themes/lliphi.json`.
El instalador (`desinstalar`) hace lo segundo y no toca los `settings.json`, que son tuyos.
