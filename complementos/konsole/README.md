# Konsole (`konsole`)

Los esquemas de color de Konsole (`Lliphi Claro.colorscheme`, `Lliphi Oscuro.colorscheme`) con los dieciséis ANSI
del grupo `terminal` de los tokens, fondo con desenfoque y opacidad de `efectos`.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: `.colorscheme` (INI con `[Background]`, `[Foreground*]`, `[Color0..7]` con `Faint` e `Intense`,
  `[General]`) en `~/.local/share/konsole/`.
- `aplicar.py`: con `--aplicar-tema`, el perfil por defecto (`konsolerc` → `DefaultProfile`) toma el esquema y, si está
  instalada, JetBrains Mono Nerd Font (mejoras 5 y 9); un perfil enlazado desde dotfiles sigue enlazado; el perfil se
  respalda antes (`respaldos()`).
- Lo generado: `generado/konsole/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos konsole --aplicar
python3 herramientas/instalar.py --modulos konsole            # simula la instalación
```

Pruebas: `test_konsole_16_colores`, `test_perfil_konsole_toma_el_esquema`.
