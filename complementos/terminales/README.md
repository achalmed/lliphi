# Terminales: Alacritty y Kitty (`terminales`)

Los mismos colores de Konsole (`konsole.ansi`: fondo, textos y los dieciséis ANSI, sobre el esquema de Nothing;
decisiones 4.30) para Alacritty (`[colors]` TOML) y Kitty (`.conf`), claro y oscuro.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Se instalan en `$XDG_CONFIG_HOME/{alacritty,kitty}/themes/`; cada aplicación los importa desde su configuración,
  que el instalador no toca (`INSTALL.md`).
- Lo generado: `generado/terminales/{alacritty,kitty}/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos terminales --aplicar
python3 herramientas/instalar.py --modulos terminales            # simula la instalación
```

Pruebas: `test_terminales_alacritty_kitty`.
