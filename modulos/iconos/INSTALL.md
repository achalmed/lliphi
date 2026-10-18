La imagen de arriba es un render de los SVG (Inkscape) a 16, 22, 32, 48 y 64 px, no una captura del escritorio.

## Instalar a mano

1. Copia `lliphi/` y `lliphi-oscuro/` a `~/.local/share/icons/`.
2. Preferencias del sistema → Apariencia y estilo → Iconos → elige **Lliphi** (con la variante clara) o **Lliphi Oscuro**
   (con la oscura). También: `kcmshell6 kcm_icons`.

Las dos variantes solo se diferencian en lo que heredan (`breeze` o `breeze-dark`), que es lo que ven las aplicaciones
GTK; en las aplicaciones KDE las carpetas toman el color de acento del esquema activo (`FollowsColorScheme`). Todo lo
que no es una carpeta sigue siendo Breeze.

## Actualizar

Sustituye las dos carpetas. Si Plasma no refresca los iconos, cierra la sesión y vuelve a entrar.

## Desinstalar

Elige otro tema de iconos en Preferencias del sistema y borra `~/.local/share/icons/lliphi` y
`~/.local/share/icons/lliphi-oscuro`. El instalador (`desinstalar`) hace lo segundo.
