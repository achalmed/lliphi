# Disposición del escritorio (`disposicion`)

**Desktop Layout** del encargo: los paneles, los widgets y el fondo de cada escritorio (barra superior fina con
lanzador, reloj y bandeja; dock inferior flotante que se oculta bajo las ventanas, con Dolphin, Konsole y
Preferencias), y los selectores de ventanas y de escritorios de KWin. Es un **componente** del tema global.

## Por qué es un componente

Plasma ejecuta el script de disposición desde el paquete `Plasma/LookAndFeel`
(`contents/layouts/org.kde.plasma.desktop-layout.js`) y solo si el usuario marca «Disposición del escritorio» al
aplicar el tema (o con `plasma-apply-lookandfeel --resetLayout`). El tema global llama a `integrar()` y el script queda
dentro de su paquete. Plasma admite también paquetes `Plasma/LayoutTemplate` sueltos; Lliphi no los usa (no formaba
parte de lo existente).

## Responsabilidad

- `ajustes.json`: los paneles y sus widgets, declarativos (ubicación, alto en `gridUnit`, ocultar, flotante, longitud,
  alineación; cada widget con su id y su configuración). Lo edita Lliphi Studio; `construir.py` rechaza un valor que el
  scripting de Plasma 6.6 no entiende (`windowscover` ya no existe).
- `escritorio.js`: la plantilla, JavaScript de la API de scripting de escritorio de Plasma (`Panel`, `addWidget`,
  `writeConfig`, `desktopsForActivity`, `userDataPath`) que recorre los paneles. Tres marcas se sustituyen al construir:
  `@NOMBRE@` (nombre del tema), `@PANELES@` (los paneles de `ajustes.json`) y `@FONDO@` (id del paquete de fondo de
  `complementos/fondos`). El fondo se pone por ruta porque Plasma 6.6 no
  resolvía el nombre de un paquete de usuario (docs/validacion.md §3).
- `construir.py`: escribe el script con la cabecera de generado; aporta `[kwinrc][WindowSwitcher]` y
  `[kwinrc][DesktopSwitcher]` (`LayoutName=org.kde.breeze.desktop`).
- `aplicar.py`: declara qué hay que respaldar antes de instalar: las notas del widget de notas
  (`~/.local/share/plasma_notes`), que Plasma borra si un cambio de disposición quita el widget (incidente del
  2026-10-18). `UNDO.sh` repone las que falten sin pisar las existentes. La configuración de los paneles
  (`plasma-org.kde.plasma.desktop-appletsrc`) la respalda el tema global.

## Estructura

```
modulos/disposicion/
├── modulo.json    componente · integracion.en = global · referencia a fondos
├── ajustes.json   los paneles y sus widgets (fuente; lo edita Lliphi Studio)
├── escritorio.js  la plantilla de la disposición (JavaScript de Plasma)
├── construir.py   valores() e integrar()
├── aplicar.py     respaldos()
├── INSTALL.md · README.md
```

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos disposicion --aplicar   # reconstruye el tema global
python3 herramientas/instalar.py --modulos global --aplicar
plasma-apply-lookandfeel -a org.lliphi.oscuro --resetLayout                # SUSTITUYE la disposición actual
```

Pruébala antes en una sesión anidada o con otro usuario (docs/validacion.md §5): aplicar una disposición borra la
actual. Pruebas: `test_tema_global_estructura`, `test_componentes_dentro_del_tema_global`.
