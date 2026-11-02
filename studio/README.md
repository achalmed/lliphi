---
tipo: readme
estado: activo
---
# studio/ — Lliphi Studio, la ventana opcional de Lliphi (QML + Kirigami sobre gui-comun 2.7)

El tema Lliphi en una ventana de trabajo al estilo Dolphin/Kate: cada **destino** (el tema global, los seis módulos y
los complementos) con lo que entrega, si lo generado está al día con los tokens y si está instalado en tu sesión y
sigue intacto; la **paleta** de los tokens como datos; las **diferencias** de una verificación y el **registro** de cada
orden. **Es opcional**: todo lo de terminal (`herramientas/generar.py`, `instalar.py`, `sesion.py`,
`modulos/esquema/paleta.py`) funciona sin ella, y la ventana no reemplaza ninguna orden: las corre. El diseño está en
[`docs/rediseno.md`](../docs/rediseno.md).

```bash
/usr/bin/python3 -m venv --system-site-packages .venv && .venv/bin/pip install -r requirements.txt   # coloraide (paleta.py); una vez
python3 -m pip install --user "gui-comun @ git+https://github.com/achalmed/gui-comun.git@v2.7.0"      # o GUI_COMUN_DIR=<repo gui-comun>
/usr/bin/python3 studio/main.py                       # desde la raíz de lliphi (el PySide6 del sistema es el que carga Kirigami)
/usr/bin/python3 studio/main.py --destino esquema     # abre con un destino elegido
/usr/bin/python3 studio/main.py --instalar-lanzador   # acceso directo en el menú de aplicaciones (-n simula)
```

## La ventana

Menú · barra corta (Simular, Aplicar, Verificar, Comprobar; el selector de operación y el filtro) · navegación
compacta (**Destinos** por rol: tema global, módulos, complementos · **Estado**: generado al día, desfasado, sin
comprobar, instalado, modificado, sin instalar) · la **tabla de destinos** (Destino, Rol, Clase, Formato, Generado,
Al día, Instalación, Última construcción) · los **detalles** del destino (Resumen, Paleta, Diferencias, Registro,
Operación) · el **panel inferior** con la salida de las órdenes (F4) · la barra de estado · la paleta de órdenes (Ctrl+K).

**F5 lee o simula; Ctrl+Intro escribe o instala tras confirmar.** La confirmación nombra la orden exacta, lo que toca y,
al instalar, que el instalador respalda con SHA-256 y deja `UNDO.sh` en `~/.local/state/lliphi/respaldos/<fecha>/`
(Herramientas › Respaldos y volver atrás…). Esc cancela la orden en curso.

| menú | operaciones (cada una elige la operación actual; F5 y Ctrl+Intro la corren) |
|---|---|
| Destino | Generar el destino · Instalar el destino (`generar.py`/`instalar.py --modulos <id>`, sin y con `--aplicar`) |
| Proyecto | Verificar lo generado (rellena «Al día» de todos los destinos) · Validar · Generar todo · Paleta (tokens desde los ajustes) · Estado y Comprobar la instalación · Instalar todo · Desinstalar · Dependencias de terceros · Pruebas · Licencias (REUSE) · Empaquetar · Sitio (Quarto) |
| Herramientas | Respaldos y volver atrás… (`UNDO.sh`) · Sesión de prueba… (estado, arrancar tras confirmar, recargar, capturar, cerrar; las sesiones de la caché con su peso) · El entorno de las órdenes… · el sitio, el acceso directo |
| Archivo | abrir el `ajustes.json` del destino con el editor (después, F5/Ctrl+Intro regeneran), su `modulo.json`, lo generado en Dolphin, `tokens.json`; terminal en el proyecto; copiar el id |

«Al día» empieza en «sin comprobar»: lo dice `generar.py verificar --json` (unos veinte segundos; construye todo en un
temporal), que se guarda en la caché del studio con su fecha y caduca si cambia alguna fuente. «Instalación» lo dicen el
manifiesto de `~/.local/state/lliphi/` e `instalar.py estado --json` (instantáneo). Los colores de Lliphi aparecen
solo como datos (la pestaña Paleta pinta cada token con su hex); la ventana viste `Kirigami.Theme`. `sddm` y `gtk-root`
piden pkexec: quedan en la terminal (el Resumen lo dice). Los editores visuales de 1.x (color, Plasma, decoración,
iconos, pantallas, disposición) se retiraron (decisión S6): los `ajustes.json` se editan en el editor.

## Estructura

```
studio/
├── main.py                  entrada (sin lógica): --destino, --smoke, --instalar-lanzador
├── muestra.py               una COPIA ligera del proyecto y un HOME falso para pruebas y capturas
├── capturar.py              capturas para la documentación sobre la copia (ninguna ruta de la máquina)
├── lliphi_app/
│   ├── __init__.py          hay_gui_comun(): instalado o por GUI_COMUN_DIR, nunca subiendo carpetas
│   ├── aplicacion.py        arma la aplicación: controladores, Acciones (menú, barra, paleta), carga Main.qml
│   ├── servicios/           sin Qt: proyecto.py (módulos, tokens, órdenes, git, respaldos), color.py (OKLCH),
│   │                        destinos.py (la fila y su estado, el Resumen, la paleta), operaciones.py (el catálogo)
│   ├── controladores/       lo expuesto al QML: espacio, destinos, operaciones, ajustes
│   ├── qml/Main.qml         la ventana sobre GuiComun.VentanaStudio; componentes/ (Resumen, Paleta, Diferencias,
│   │                        Registro, Operación, DialogoRespaldos, DialogoSesion, DialogoAjustesStudio)
│   └── recursos/marca.svg   el icono del acceso directo (nunca dentro de la ventana)
└── tests/                   run.sh · conftest · test_servicios_lliphi · test_controladores_lliphi · test_ventana_lliphi
```

## Pruebas y capturas

```bash
studio/tests/run.sh                                   # sobre una copia del proyecto en ~/.cache/pytest/lliphi-studio; QML con /usr/bin/python3
/usr/bin/python3 studio/capturar.py docs/figuras/lliphi-studio-oscuro.png --esquema generado/esquema/LliphiOscuro.colors --destino esquema --pestana 1 --verificar
```

Ninguna prueba ni captura escribe en el repo real ni en tu sesión: parten de la copia (`muestra.py`) con HOME y XDG
temporales; generan de verdad el destino `esquema` en la copia; **ninguna instala en la sesión real ni abre una sesión
anidada** (`test_ventana_lliphi.py` lo vigila). Los ajustes de la ventana viven en `~/.config/achalma/Lliphi Studio.conf`;
la caché (verificación, planes y registros) en `~/.cache/lliphi-studio/`.
