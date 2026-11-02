---
tipo: doc
estado: hecho
forma: explicacion
titulo: "Rediseño de Lliphi Studio como espacio de trabajo: auditoría de la GUI de Widgets, arquitectura de información, distribución de la ventana, componentes y decisiones"
creado: 2026-11-02
---
# Rediseño de Lliphi Studio: los destinos del tema, lo generado y lo instalado en una ventana de trabajo

Fase 5 de la modernización de la familia de studios (`gui-comun/docs/arquitectura-qml-kirigami.md` §8): Lliphi
Studio es el noveno y último que sigue al piloto Git Studio, cuyo lenguaje visual y arquitectura de información
(`git-studio/docs/rediseno.md` §2, §4, §6, §8) el autor aprobó el 2026-11-01 «para todos los programas de la
familia». Biblioteca, Quarto, Simuladores y Raphi mostraron cómo se aplica a un studio que orquesta herramientas con
datos propios: la tabla de lo que se maneja, una operación actual, F5 lee o simula y Ctrl+Intro escribe tras
confirmar. Este documento aplica ese diseño al studio del tema: la auditoría de lo que hay (§1), las ocho preguntas
de producto (§2), la arquitectura de información (§3), la ventana (§4), lo construido (§5), los componentes (§6), lo
que el marco necesitó (§7) y las decisiones (§8). **Está construido** (rama `wip/2026-11-02-qml`, en un árbol de
trabajo aparte porque otras sesiones trabajaban en el checkout, 2026-11-02): las capturas de §5 son reales; pasa a
`hecho` cuando el autor lo valide en la sesión real (`../estado.md`).

Tres reglas condicionan todo lo demás. **El repo es público y autónomo** (`../README.md`): `gui_comun` llega como
paquete de pip o por `GUI_COMUN_DIR`, nunca subiendo carpetas; la ventana es opcional y lo de terminal no gana
ninguna dependencia. **Lo generado no se edita y lo instalado es reversible**: `generar.py verificar` detecta la
deriva y el instalador deja un `UNDO.sh` por cada instalación; la ventana corre esas mismas órdenes, no las
reemplaza. **Los colores de Lliphi son datos del tema, no colores de la interfaz**: la ventana sigue con
`Kirigami.Theme` (el esquema del usuario) y enseña la paleta como muestras de datos.

## 1. Auditoría de la GUI actual (Widgets, `gui-comun` 1.4)

Nueve secciones en una barra lateral con la marca «Lliphi Studio · El centro de control de Lliphi» (retirada en esta
fase) al estilo de Qt Design Studio: Dashboard (cifras y grafo), Color (editor OKLCH con interfaz de muestra y
contraste), Plasma (explorador de SVG de nueve piezas), Ventanas (Aurorae), Iconos y cursores (temas freedesktop y
Xcursor), Pantallas (`QQuickWidget` con la carga), Disposición (paneles y widgets), Vista en vivo (la sesión de
prueba) y Construir y desplegar (las órdenes). Lo que esta fase conserva como servicios: `proyecto.py` (módulos,
ajustes, borradores, órdenes, git, versiones, respaldos; sin Qt) y `color.py` (OKLCH → sRGB y contraste; sin Qt).

| sección | qué hace hoy | entidades y operaciones | mezclado en la ventana |
|---|---|---|---|
| Dashboard | cifras y grafo de los módulos; validación, deriva e instalación por `--json` | módulo, deriva, instalación | las cifras pintadas a mano; nada lista destino por destino qué está al día o instalado |
| Color · Plasma · Ventanas · Iconos · Pantallas · Disposición | editores visuales de los `ajustes.json` de cuatro módulos y exploradores de SVG, iconos y pantallas | ajustes, borrador, diff | 3 285 líneas de QtWidgets y `QPainter` por sección; cada editor es una pantalla a mano |
| Vista en vivo | arrancar, recargar, capturar y cerrar la sesión anidada | sesión de prueba | la sesión arranca sin decir que consume RAM y disco |
| Construir y desplegar | botones por orden (simular, aplicar, comprobar, desinstalar, dependencias, SDDM, revertir) | orden, respaldo | las confirmaciones sin la orden ni lo que toca |

Lo que falta hoy: una **vista por destino** (qué entrega cada módulo y complemento, si lo generado está al día con los
tokens, si está instalado y sigue como se instaló); la salida de una orden se pierde al cambiar de sección; la
reversibilidad (el `UNDO.sh` del respaldo) no está a la vista al instalar; el lanzador instalado apunta a un Python
con PySide6 por pip, que no carga Kirigami.

## 2. Las ocho preguntas de producto

1. **Tarea principal**: tras tocar los tokens o un módulo, saber qué destinos quedaron desfasados, regenerarlos
   (simular, aplicar), validar, y llevar al escritorio lo que se quiera con el instalador reversible (simular,
   confirmar, aplicar; comprobar; desinstalar o volver atrás con el `UNDO.sh`). El destino es el sujeto; generar e
   instalar, los verbos.
2. **Información constante**: cuántos destinos hay y cuántos están al día, desfasados, instalados y sin instalar; el
   destino elegido y su estado; si hay una orden en marcha (barra de estado).
3. **Flujo de trabajo**: elegir el destino (o el filtro por estado) → Resumen → F5 (generar en simulación, o
   verificar) → Diferencias → Ctrl+Intro (generar de verdad) → F5 instalar en simulación → Ctrl+Intro instalar (con el
   respaldo y su `UNDO.sh` a la vista) → Registro.
4. **Qué se edita y qué se lee**: se leen los `modulo.json`, los tokens, `generado/`, el manifiesto de instalación y
   los respaldos; la ventana escribe `generado/` y el escritorio del usuario solo con las órdenes de Lliphi tras
   confirmar. Los `ajustes.json` se abren en el editor (§8, S6).
5. **Lo irreversible**: nada de lo que hace el instalador lo es (respaldo con sumas y `UNDO.sh`); regenerar
   `generado/` es reversible por git; la sesión anidada consume RAM y gigas de disco en la caché; `sddm` y
   `gtk-root` piden privilegios (pkexec) y quedan fuera de la ventana (terminal).
6. **Qué comparte con la familia**: menú, barra, navegación, tabla, detalles, panel inferior, barra de estado,
   paleta, ajustes, mensajes, `VistaTexto` (`gui-comun` 2.7). No pidió nada nuevo al marco (§7).
7. **Dependencias**: la ventana, el PySide6 y el Kirigami del sistema (`/usr/bin/python3`); las órdenes, la
   biblioteca estándar, Pillow (fondos; está en el sistema) y `coloraide` (`paleta.py`): un `.venv` del repo sobre el
   Python del sistema con `requirements.txt` (S9).
8. **Qué queda fuera**: los editores visuales de 1.x (Color, Plasma, Ventanas, Iconos, Pantallas, Disposición), que
   eran pantallas a mano por módulo (S6); `sddm` y `gtk-root` (pkexec); la publicación en la KDE Store.

## 3. Arquitectura de información

### 3.1 Una tabla, un destino actual, una operación actual, una ventana

- **Navegación** (`PanelNavegacion`): *Destinos* (Todos, Tema global, Módulos, Complementos, con contador) y
  *Estado* (Generado al día, Desfasado, Sin comprobar, Instalado, Modificado, Sin instalar, con contador).
- **Centro** (`TablaDatos`): un destino por fila: Destino, Rol, Clase, Formato, Generado (archivos), Al día
  (al día · desfasado · sin comprobar), Instalación (instalado · modificado · sin instalar · no se instala), Última
  construcción. Filtro Ctrl+F. Orden por cabecera.
- **Detalles** (`PanelDetalles` del destino actual): Resumen · Paleta · Diferencias · Registro · Operación.
- **Panel inferior** (`PanelInferior`): la salida del generador, del instalador y de la sesión de prueba; el
  progreso de la tarea.
- **Barra de estado**: «29 destinos · n al día · n desfasados · n sin comprobar · n instalados» y, a la derecha, el
  destino actual con sus estados y la operación elegida.

### 3.2 Entidades y dónde vive cada dato

| entidad | de dónde sale | qué muestra la ventana |
|---|---|---|
| tokens | `tokens/tokens.json` (OKLCH, DTCG; lo escribe `paleta.py`) y `tokens/marca.json` | la pestaña Paleta: primitivas, semánticos y terminal de cada variante como muestras de datos, con su hex y su OKLCH |
| destino | cada `modulo.json` (`global/`, `modulos/<id>/`, `complementos/<id>/`): nombre, resumen, clase, formato, tecnología, estado, dependencias, herramientas, archivos, instalación | la fila; Resumen |
| generado | `generado/<id>/` (archivos y fecha); `generar.py verificar --json` dice qué difiere de una construcción nueva | la columna Generado y Al día; Diferencias |
| instalación | el manifiesto `$XDG_STATE_HOME/lliphi/instalado.json` (módulos, rutas con su suma) e `instalar.py estado --json` (cada ruta sigue como se instaló); los pares origen → destino del núcleo | la columna Instalación; Resumen (cada ruta y si sigue intacta) |
| respaldo | `$XDG_STATE_HOME/lliphi/respaldos/<fecha>/` con su `UNDO.sh` | Herramientas › Respaldos y volver atrás…; la confirmación de instalar lo nombra |
| sesión de prueba | `sesion.py estado --json` (`$XDG_CACHE_HOME/lliphi/sesiones/<fecha>/casa`) | Herramientas › Sesión de prueba…; su estado en la barra |
| sitio | `sitio/` (Quarto) y `sitio/generado/` (lo escribe `generar.py`) | la operación Sitio (render tras confirmar) |

### 3.3 Dónde vive cada operación

Cada operación existe una sola vez en `Acciones` (`studio/lliphi_app/aplicacion.py`) y su catálogo es
`studio/lliphi_app/servicios/operaciones.py`: lo que F5 lee o simula y lo que Ctrl+Intro escribe tras confirmar.

| grupo | F5 lee o simula | Ctrl+Intro escribe tras confirmar |
|---|---|---|
| Destino | **Generar** (`generar.py --modulos <id>`: qué escribiría) · **Instalar** (`instalar.py --modulos <id>`: qué respaldaría y copiaría) | **Generar** (`--aplicar`: escribe `generado/<id>/` y `sitio/generado/`) · **Instalar** (`--aplicar`: respaldo con sumas y `UNDO.sh`, copia, KDE lo reconoce) |
| Proyecto | **Verificar lo generado** (`generar.py verificar`: deriva contra los tokens; actualiza Al día de todos) · **Validar** (`generar.py validar`) · **Estado de la instalación** (`instalar.py estado`) · **Comprobar** (`instalar.py comprobar`) · Paleta (`paleta.py`: qué cambiaría en los tokens) · Pruebas (`pytest`) · Licencias (`reuse lint`) · Empaquetar (plan) · Sitio (plan) | **Generar todo** (`generar.py --aplicar`) · **Paleta** (`paleta.py --aplicar`) · **Desinstalar** (`instalar.py desinstalar --aplicar`) · Dependencias (`instalar.py dependencias --aplicar`: Papirus, cursores, tipografías; sin root) · **Empaquetar** (`generar.py empaquetar`: `dist/`) · **Sitio** (`quarto render sitio`) |
| Herramientas | Respaldos y volver atrás… (cada `UNDO.sh`; verlo) · Sesión de prueba… (estado, capturar, cerrar) | Volver atrás (`bash UNDO.sh`, tras confirmar) · Arrancar la sesión de prueba (tras confirmar que consume RAM y disco en la caché) · Recargar la sesión |

## 4. Distribución de la ventana (1280 × 800)

Menú (Archivo · Editar · Ver · Destino · Proyecto · Herramientas · Ajustes · Ayuda), barra corta (Simular F5 · Aplicar
Ctrl+Intro · | · Verificar lo generado · Comprobar la instalación · el selector de operación · el filtro), navegación
compacta a la izquierda, la tabla de destinos en el centro, los detalles del destino a la derecha (Resumen, Paleta,
Diferencias, Registro, Operación), el panel inferior con la salida de las órdenes y la barra de estado con los
contadores. Ningún nombre ni logotipo dentro de la ventana; ningún color ni fuente propios en la interfaz.

## 5. Lo construido

| captura | qué muestra |
|---|---|
| `figuras/lliphi-studio-oscuro.png` | Lliphi Oscuro: los destinos con su estado, el esquema de color elegido y la pestaña Paleta con los tokens como datos |
| `figuras/lliphi-studio-claro.png` | Lliphi Claro: el Resumen de un destino con sus dependencias, herramientas y rutas de instalación |
| `figuras/lliphi-studio-paleta.png` | la paleta de órdenes (Ctrl+K) buscando un destino |

Las capturas se toman sobre el proyecto de muestra (`studio/muestra.py`: una copia ligera del proyecto en una carpeta
temporal), con HOME, configuración y caché temporales (ninguna ruta de la máquina en pantalla), con `studio/capturar.py`.

## 6. Componentes

`VentanaStudio`, `PanelNavegacion`, `TablaDatos`, `PanelDetalles`, `PanelInferior`, `VistaTexto` (el Resumen en
Markdown, las diferencias, el registro, un `UNDO.sh`), `MenuAcciones`, `BotonAccion`, `DialogoAjustes`,
`PaletaOrdenes`, `Mensajes`; `Kirigami.PromptDialog` para confirmar; la Paleta es un `Flow` de muestras
(`Rectangle` con el hex del token como dato) con su nombre.

## 7. Lo que el marco necesitó (`gui-comun` 2.7)

Nada: la Paleta se resuelve con QtQuick y los datos del token; la tabla, los detalles y las órdenes son los de 2.x.
`gui-comun` queda en 2.7.0.

## 8. Decisiones

- **S1 · La tabla sale de los `modulo.json` y de `generado/`; los estados, de las órdenes de Lliphi.** Leer los
  manifiestos y contar archivos es instantáneo; «al día» lo dice `generar.py verificar --json` (unos veinte segundos:
  construye todo en un temporal), así que la columna empieza en «sin comprobar» y se rellena con F5 «Verificar lo
  generado», en segundo plano; «instalado» lo dice el manifiesto y `instalar.py estado --json` (instantáneo).
- **S2 · La navegación es por rol del destino y por estado**: el tema global, los seis módulos y los veintidós
  complementos, y lo que pide atención (desfasado, modificado, sin instalar).
- **S3 · Los colores del tema se muestran como datos, nunca como colores de la interfaz**: la pestaña Paleta pinta
  cada token en un `Rectangle` con su hex (lo que el tema produce), sobre la ventana con `Kirigami.Theme`; la prueba de
  «sin colores propios» excluye solo el valor del token que viene del modelo.
- **S4 · F5 lee o simula; Ctrl+Intro escribe tras confirmar.** Generar e instalar simulan con la propia orden (sin
  `--aplicar`); la confirmación nombra la orden exacta, lo que toca y, al instalar, que queda un respaldo con `UNDO.sh`
  en el estado del usuario; desinstalar y volver atrás también confirman.
- **S5 · Nada del studio arranca una sesión de prueba sin confirmar**, ni las pruebas ni las capturas: consume RAM y
  deja gigas en `$XDG_CACHE_HOME/lliphi/sesiones`; la confirmación lo dice y Herramientas › Sesión de prueba… enseña
  qué sesiones hay y cuánto pesan.
- **S6 · Los editores visuales de 1.x se retiran y los `ajustes.json` se editan en el editor.** Eran pantallas escritas a
  mano por módulo (QtWidgets y `QPainter`): no se portan; «Abrir los ajustes del destino» abre su `ajustes.json`, y
  F5/Ctrl+Intro regeneran. Si el autor los quiere de vuelta, serán componentes QML propios sobre `proyecto.py` y
  `color.py`, que se conservan como servicios.
- **S7 · `sddm` y `gtk-root` quedan en la terminal**: piden pkexec; la ventana lo dice en el Resumen de esos destinos.
- **S8 · Lo de 1.x que sigue**: el proyecto y el color sin Qt (`servicios/proyecto.py`, `servicios/color.py`); las
  órdenes son las mismas; el acceso directo lo escribe `gui_comun.lanzador` y corre `/usr/bin/python3`.
- **S9 · Un `.venv` del repo sobre el Python del sistema** (`/usr/bin/python3 -m venv --system-site-packages .venv` y
  `pip install -r requirements.txt`: `coloraide`; Pillow y pytest ya están en el sistema): las órdenes corren con él
  si existe y, si no, con el Python de la ventana (todo menos `paleta.py` funciona igual). PySide6 nunca va en el
  `.venv`. El `.venv` de Anaconda que había (`pyproject` `[dev]`) sigue valiendo para desarrollar.
- **S10 · El proyecto de muestra** (`studio/muestra.py`): una copia ligera del proyecto (tokens, manifiestos,
  herramientas, fuentes, `generado/`) en una carpeta temporal, con HOME y XDG temporales (el instalador escribe en una
  casa falsa, nunca en la sesión real). Las pruebas generan de verdad un destino ligero (`esquema`: solo biblioteca
  estándar) e instalan en la casa falsa; nunca arrancan una sesión anidada.
- **S11 · El árbol de trabajo aparte**: el checkout del autor tenía cambios de otras sesiones; esta rama vive en
  `$XDG_CACHE_HOME/lliphi-wip` (`git worktree`), con su propio `.venv`, y el director la fusiona.
