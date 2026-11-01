# Fondos de pantalla (`fondos`)

El paquete de fondo «Lliphi Horizonte» (`org.lliphi.horizonte`): un degradado de dos neutros con una franja diagonal
del acento, en 1080p, 1440p y 4K, con imagen clara (`images/`) y oscura (`images_dark/`, Plasma ≥ 6.6) y el acento
declarado (`X-KDE-PlasmaImageWallpaper-AccentColor`).

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
