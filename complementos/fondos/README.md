# Fondos de pantalla (`fondos`)

Dos paquetes de fondo, cada uno con imagen clara (`images/`) y oscura (`images_dark/`, Plasma ≥ 6.6), en 1080p,
1440p y 4K y con el acento declarado (`X-KDE-PlasmaImageWallpaper-AccentColor`):

- «Lliphi Horizonte» (`org.lliphi.horizonte`), el que nombra el tema global: un degradado de dos neutros con una franja
  diagonal del acento (PNG).
- «Lliphi Forma» (`org.lliphi.forma`, decisiones 4.23): dos cuadrados de vidrio esmerilado, un semicírculo en el rojo de
  Lliphi y una píldora que se deshace hacia abajo con una matriz de puntos tenue, sobre neutro liso con grano fino
  (JPEG de calidad 90 sin submuestreo: el grano no comprime en PNG). Se dibuja a 4K y se reduce; reproducible
  (semillas fijas).

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: paquete `Wallpaper/Images` en `~/.local/share/wallpapers/<id>/` (`metadata.json` con `KPlugin.Id`, sin
  `KPackageStructure`, como `Next` del sistema). `kpackagetool6` no resuelve estos paquetes ni los del sistema; se
  comprueban por sus archivos.
- `construir.py`: `imagen()` (la usan también `carga-bloqueo` y `sddm`), `generar()` y `valores()` (`[Wallpaper] Image`).
- `aplicar.py`: el fondo por ruta con `plasma-apply-wallpaperimage` (en el claro, la imagen clara fija; decisiones 4.16).
- Construcción: Pillow. Lo generado: `generado/fondos/org.lliphi.horizonte/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos fondos --aplicar
python3 herramientas/instalar.py --modulos fondos            # simula la instalación
```

Pruebas: `test_fondo_paquete`.
