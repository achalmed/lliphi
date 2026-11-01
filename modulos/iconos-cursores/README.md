# Iconos y cursores (`iconos-cursores`)

**Icons & Cursors** del encargo. Dos recursos diferenciados, ambos de terceros, que Lliphi no redistribuye: los
instala en el usuario a petición y el tema global los nombra. Es un módulo **externo**: no tiene carpeta en `generado/`.

## Responsabilidad

| recurso | qué | mecanismo de instalación | quién lo aplica |
|---|---|---|---|
| iconos (decisiones 4.22) | `Colloid-Grey-Light` en el claro y `Colloid-Grey-Dark` en el oscuro (Colloid, GPL-3.0) | el guion de su autor (`install.sh -t grey`); `externas.colloid()` solo comprueba y dice cómo, no ejecuta código descargado | `[kdeglobals][Icons]` del tema global y `aplicar.py`; si falta, la reserva de abajo |
| reserva, claro | Papirus tal como se publica (carpetas azules) | `externas.papirus()`: tarball de la última versión de PapirusDevelopmentTeam → `~/.local/share/icons/{Papirus,Papirus-Dark,Papirus-Light}` | `[kdeglobals][Icons]` del tema global y `aplicar.py` (`plasma-changeicons`) |
| reserva, oscuro | `Papirus-Dark-Lliphi`: tema superpuesto que hereda de Papirus-Dark y solo redefine las carpetas, con enlaces simbólicos a las `folder-red-*` de Papirus | `externas.carpetas_en_color()` (construido en la máquina, sobre el Papirus instalado) | ídem; si falta, Papirus-Dark y después Breeze |
| cursores | WhiteSur-cursors | `externas.whitesur_cursores()`: `dist/` del tarball de la rama principal → `~/.local/share/icons/WhiteSur-cursors` | `[kcminputrc][Mouse] cursorTheme` del tema global |
| cursores (opcional) | Bibata Modern Classic e Ice | `externas.bibata()` con `--opcionales` | a mano |

Por qué un superpuesto y no recolorear Papirus: Papirus-Dark comparte con Papirus los tamaños grandes por enlaces, así
que no se pueden colorear distinto modificando sus archivos (decisiones 4.15).

## Formato

Temas freedesktop (Icon Theme Specification): `index.theme` con `Inherits` y `Directories`; los cursores, con
`cursors/`. Viven en `~/.local/share/icons/` (o `~/.icons`, `/usr/share/icons`).

## Estructura

```
modulos/iconos-cursores/
├── modulo.json   externo · freedesktop · sin instalación propia
├── construir.py  ICONOS por variante y CURSORES; valores() para el tema global
├── externas.py   descarga e instalación de Papirus, el superpuesto, WhiteSur-cursors y Bibata
├── aplicar.py    aplica el tema de iconos de la variante, con reservas
├── INSTALL.md · README.md
```

## Desarrollar

```bash
python3 herramientas/instalar.py dependencias            # simula
python3 herramientas/instalar.py dependencias --aplicar  # instala lo que falte
python3 herramientas/instalar.py comprobar               # ¿están los temas que nombra el tema global?
```

Para cambiar el tema de iconos o de cursores de una variante, `ICONOS` o `CURSORES` en `construir.py` (el tema global y
`aplicar.py` lo toman de ahí; `generar.py validar` comprueba que coincidan). `desinstalar` no retira lo de terceros.
Pruebas: `test_tema_global_estructura`, `test_variante_clara_validada`.
