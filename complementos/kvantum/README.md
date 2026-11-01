# Kvantum (`kvantum`)

El estilo de las aplicaciones Qt (`LliphiClaro`, `LliphiOscuro`), derivado del Kvantum de WhiteSur (GPL-3.0): menús y
tooltips translúcidos, controles redondeados, con las claves de color del `.kvconfig` y los hex del `.svg` tomados de
los tokens.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: carpeta `<id>/` con `<id>.kvconfig` y `<id>.svg` en `$XDG_CONFIG_HOME/Kvantum/` (base `config`; en 0.3.0
  se calculaba desde `$XDG_DATA_HOME/../..` y fallaba con rutas XDG no estándar).
- `construir.py`: `generar()` y `valores()` (`[kdeglobals][KDE] widgetStyle=kvantum|kvantum-dark`).
- `ajustes.json`: por variante, si las ventanas son translúcidas (como WhiteSur) o sólidas, y el token de la barra de
  herramientas. En el oscuro, translúcidas y la barra opaca en `fondo.ventana`: título, menús y herramientas en una sola banda y
  la vista y la terminal integrada con transparencia (decisiones 4.18).
- `aplicar.py`: `Kvantum/kvantum.kvconfig` con el tema de la variante y el estilo de widgets en `kdeglobals`.
- Requiere Kvantum para Qt 6 (`qt6-style-kvantum`). Lo generado: `generado/kvantum/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos kvantum --aplicar
python3 herramientas/instalar.py --modulos kvantum            # simula la instalación
```

Pruebas: `test_kvantum_derivado`, `test_kvantum_en_xdg_config_home`.
