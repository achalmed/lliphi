# Lliphi Studio

El centro de control visual de Lliphi: una ventana de escritorio (PySide6) para trabajar los seis módulos del tema sin
salir de las herramientas de Lliphi ni de KDE. **No reemplaza** a Inkscape ni a las herramientas de KDE: las integra.
Es **opcional**: todo lo de terminal (`herramientas/generar.py`, `instalar.py`, `sesion.py`, `modulos/esquema/paleta.py`)
funciona sin ella.

```bash
python3 -m pip install --user PySide6 "git+https://github.com/achalmed/gui-comun@v1.4.0"   # una vez
python3 studio/main.py                           # desde la raíz de lliphi
python3 studio/main.py --pagina color            # abre en una sección
python3 studio/main.py --instalar-lanzador       # acceso directo en el menú de aplicaciones (-n simula)
```

## Secciones

La disposición de los editores es la de Qt Design Studio: biblioteca a la izquierda, lienzo al centro, propiedades a la
derecha y, abajo, el código (el borrador, el diff contra el proyecto y lo que saldría) junto a la consola.

| sección | qué hace | con qué |
|---|---|---|
| Dashboard | estado de los seis módulos (validación, deriva de lo generado, instalación, herramientas, última construcción), grafo de dependencias, tema global y complementos, versiones y repositorio | `generar.py verificar\|validar --json`, `instalar.py estado --json`, `git` |
| Color | editor de la paleta OKLCH: neutros, acentos, estados y terminal; interfaz de muestra clara y oscura lado a lado; contraste WCAG de los 86 pares; simulación de daltonismo; dónde se usa cada color | `modulos/esquema/ajustes.json`, `paleta.py --ajustes <borrador> --json` |
| Plasma | explorador del estilo de Plasma: cada marco de nueve piezas compuesto a cualquier tamaño como lo dibuja Plasma, con el esquema de la variante y sobre el fondo; Lliphi Oscuro, Lliphi Claro y la base de WhiteSur lado a lado; el diff del recoloreo | `QSvgRenderer`, Inkscape (sobre una copia) |
| Ventanas | la decoración Aurorae real (marco con sombra, botones con sus estados al pasar y pulsar, título); editor del `rc`, de los colores del título y de los botones | `modulos/decoracion/ajustes.json`, Inkscape (copia) |
| Iconos y cursores | los temas freedesktop con su cadena `Inherits`; iconos por contexto y tamaño, comparados entre temas; cursores Xcursor animados; el organizador: tema de cada variante, cursores y color de carpetas del superpuesto | `modulos/iconos-cursores/ajustes.json`, `instalar.py dependencias` |
| Pantallas | la carga **de verdad** dentro de la ventana (su QML solo usa QtQuick); salida, bloqueo y SDDM en maqueta con sus imágenes y de verdad con la herramienta de KDE | `QQuickWidget`, `ksplashqml --test --window`, `sddm-greeter-qt6 --test-mode`, `ksmserver-logout-greeter` y `kscreenlocker_greet --testing` solo en la sesión de prueba |
| Disposición | paneles y widgets sobre la pantalla (clic para elegir, arrastrar para ordenar), catálogo de plasmoides; probar el borrador en la sesión de prueba sin guardarlo | `modulos/disposicion/ajustes.json`, `sesion.py guion` |
| Vista en vivo | la sesión de prueba: arrancar, recargar, cambiar de variante, abrir aplicaciones dentro, capturar y cerrar | `herramientas/sesion.py` |
| Construir y desplegar | paleta, construir, verificar, validar, pruebas, licencias, sitio, empaquetar; instalar en tu escritorio, comprobar, dependencias, SDDM, desinstalar; los respaldos con su `UNDO.sh` y «Revertir» | `generar.py`, `instalar.py`, `pytest`, `reuse`, `quarto` |

## Cómo escribe

- **La ventana es cliente del proyecto.** Lee los `modulo.json`, `tokens/`, `generado/` y el manifiesto de instalación;
  escribe solo los `ajustes.json` de `esquema`, `decoracion`, `disposicion` e `iconos-cursores` (fuente, nunca
  `generado/`). Todo lo demás lo hacen las órdenes de Lliphi en la consola, igual que en la terminal.
- **Los editores trabajan en un borrador** (`$XDG_STATE_HOME/lliphi-studio/borradores/<módulo>.json`). «Guardar y
  construir» enseña el diff, escribe el `ajustes.json` y reconstruye; la paleta no se guarda si algún par de contraste
  no cumple.
- **Tu escritorio solo cambia desde «Construir y desplegar»**, con el instalador reversible: simular, confirmar,
  aplicar (respaldo con sumas y `UNDO.sh`). Para ver un cambio sin tocarlo está la **Vista en vivo**: un Plasma anidado
  con su propio HOME en la caché (ver `herramientas/sesion.py`).
- Inkscape abre siempre una **copia** en `$XDG_CACHE_HOME/lliphi-studio/inkscape/`: lo generado se reconstruye y las
  bases de terceros no se tocan.

## Estructura

```
studio/
├── main.py                 entrada: --smoke, --pagina, --captura, --instalar-lanzador
├── lliphi_studio/
│   ├── __init__.py         faltan(): PySide6 y gui-comun
│   ├── proyecto.py         sin Qt: módulos, ajustes y borradores, órdenes, git, versiones, respaldos
│   ├── color.py            sin Qt: OKLCH → sRGB, contraste WCAG, daltonismo, dónde se usa un color
│   ├── svgplasma.py        sin Qt: elementos y marcos de los SVG de Plasma y Aurorae, hoja de colores, rc
│   ├── iconos.py           sin Qt: temas freedesktop, búsqueda con herencia, lector de Xcursor
│   ├── pintor.py           QSvgRenderer: elementos y marcos de nueve piezas; copias para Inkscape
│   ├── comun.py            el editor de cuatro paneles, el lienzo con zoom, el visor de código, las tarjetas de orden
│   ├── ventana.py          la ventana (montar_studio de gui-comun), acento carmesí
│   └── paginas/            una sección por archivo
└── tests/                  sobre una copia del proyecto y un HOME falsos en $XDG_CACHE_HOME
```

## Pruebas

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest -q studio/tests
```

Copian el proyecto (sin el sitio) a `$XDG_CACHE_HOME/pytest/lliphi-studio/` y apuntan `LLIPHI_DIR`, `HOME` y los `XDG_*`
a temporales: nunca escriben en el repositorio ni en tu escritorio. No forman parte de la CI (no instala PySide6).

## Límites

- La conversión OKLCH → sRGB de la ventana (para mover los deslizadores sin esperar) coincide con coloraide en los 33
  colores de la paleta; las cifras que mandan son las de `paleta.py`.
- La maqueta de la salida, el bloqueo y SDDM es aproximada: la de verdad es la de la herramienta de KDE.
- Plasma Studio explora y compara; el estilo de Plasma sale de WhiteSur recoloreado por `modulos/estilo/construir.py` y
  no tiene ajustes editables en esta versión.
