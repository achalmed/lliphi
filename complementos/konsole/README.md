# Konsole (`konsole`)

Los esquemas de color de Konsole (`Lliphi Claro.colorscheme`, `Lliphi Oscuro.colorscheme`) con los dieciséis ANSI
del grupo `terminal` de los tokens, fondo con desenfoque y opacidad de `efectos`. El magenta (`Color5`) lleva el acento de
la variante, rojo en el oscuro y azul en el claro (decisiones 4.28): lo que el prompt pinte en magenta combina con el
tema. Al cambiar de variante, el esquema del perfil y de las ventanas abiertas lo cambia `fondo-variante`.

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
