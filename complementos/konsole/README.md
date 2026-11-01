# Konsole (`konsole`)

Los esquemas de color de Konsole (`Lliphi Claro.colorscheme`, `Lliphi Oscuro.colorscheme`) sobre el esquema
«Nothing» del tema Nothing de jomada (`fuentes/base/Nothing-konsole/`, GPL-3.0-or-later; decisiones 4.29). El oscuro
es Nothing tal cual: su rojo en carpetas, claves de fastfetch y logotipos, fondo translúcido con desenfoque. El claro es
su espejo en azul: el acento azul en el `Color4`, el azul de Nothing en el `Color1`, su rojo en el `Color0`, y cada
color con la luz más alta que da ≥ 4,5:1 sobre el fondo claro. Al cambiar de variante, el esquema del perfil y de las
ventanas abiertas lo cambia `fondo-variante` (decisiones 4.28).

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

Pruebas: `test_konsole_16_colores`, `test_konsole_sobre_nothing`, `test_perfil_konsole_toma_el_esquema`.
