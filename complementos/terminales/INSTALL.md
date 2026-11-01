## Instalar a mano

El instalador (`python3 herramientas/instalar.py --modulos terminales --aplicar`) copia los archivos a
`~/.config/alacritty/themes/` y `~/.config/kitty/themes/`; ninguna terminal los carga sola: hay que importarlos.

### Alacritty (≥ 0.13, configuración en TOML)

1. Copia `alacritty/lliphi-claro.toml` y `alacritty/lliphi-oscuro.toml` a `~/.config/alacritty/themes/`.
2. En `~/.config/alacritty/alacritty.toml` añade (o amplía) la importación:

```toml
[general]
import = ["~/.config/alacritty/themes/lliphi-oscuro.toml"]
```

Alacritty recarga la configuración al guardar. Para cambiar de variante basta cambiar el nombre importado.

### Kitty

1. Copia `kitty/lliphi-claro.conf` y `kitty/lliphi-oscuro.conf` a `~/.config/kitty/themes/`.
2. En `~/.config/kitty/kitty.conf` añade `include themes/lliphi-oscuro.conf`, o elige el tema con
   `kitten themes --config-file-name kitty.conf Lliphi Oscuro` (la cabecera `## name:` lo registra en el selector).
3. Recarga con `ctrl+shift+F5` o abre una ventana nueva.

## Actualizar

Sustituye los archivos; la importación sigue valiendo. Alacritty y Kitty los releen al recargar.

## Desinstalar

Quita la línea `import` o `include` y borra los archivos de `themes/`. El instalador (`desinstalar`) retira los archivos
pero no toca `alacritty.toml` ni `kitty.conf`, que son tuyos.
