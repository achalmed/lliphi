---
tipo: doc
estado: activo
titulo: 'Arquitectura de Lliphi: tema global integrador, seis módulos, complementos y núcleo de construcción e instalación'
---
# Arquitectura

Desde la reingeniería del 2026-10-31 (expediente: [`migracion-modular.md`](migracion-modular.md)); la arquitectura de
la fase 5, hasta la versión 0.3.0, está en [`historial/arquitectura-0.3.md`](historial/arquitectura-0.3.md). Las
decisiones de diseño visual y su porqué siguen en [`decisiones.md`](decisiones.md).

## 1. Principios

1. **Una fuente, todo generado.** Los colores salen de `tokens/tokens.json` (lo escribe la paleta del módulo
   `esquema`); lo que no sale de los tokens viene de bases de terceros con licencia (`fuentes/base/`). Lo que se
   instala está en `generado/`, versionado para instalar sin herramientas, y nunca se edita a mano.
2. **Cada módulo se describe a sí mismo.** Un `modulo.json` dice qué es, qué formato de KDE entrega, de quién depende
   y qué se instala dónde; el núcleo lo descubre. No hay tablas de módulos que mantener a la par.
3. **El tema global integra; no duplica.** Declara los componentes por su identificador y solo lleva dentro lo que KDE
   exige que esté dentro (pantallas de carga y salida, disposición).
4. **Cada pieza en el mecanismo de KDE que le corresponde.** Un esquema de color no es un KPackage; un estilo de Plasma
   no lleva `KPackageStructure`; el bloqueo de pantalla no es del tema global (§3).
5. **Desarrollo e instalación separados.** Todo el desarrollo vive en el repositorio; `~/.local/share`, `~/.config` y
   `/usr/share` son solo destinos. Simular por omisión, respaldar con sumas, `UNDO.sh` siempre.

## 2. Mapa

```
                         tokens/ (paleta, marca) ◄── modulos/esquema/paleta.py
                                  │
        ┌─────────────────────────┼──────────────────────────────────────────┐
        ▼                         ▼                                          ▼
  modulos/ (los seis)       global/ (integrador)                   complementos/ (fuera del tema global)
  esquema ─────────── id ───►┐                                      fondos ── id ──►┐  (imagen ► carga-bloqueo, sddm)
  estilo ──────────── id ───►│ contents/defaults                    kvantum ── id ─►│
  decoracion ──────── id ───►│   (valores() de cada módulo)         konsole · terminales · editores
  iconos-cursores ─── id ───►│                                      libreoffice · sddm · obsidian
                             │                                      navegadores
  carga-bloqueo ── archivos ►│ contents/splash, contents/logout
  disposicion ──── archivos ►│ contents/layouts
                             ▼
        herramientas/nucleo/: registro · construccion · validacion · instalacion · sitio
                │                                   │
   generar.py: construir, verificar,      instalar.py: instalar, aplicar, comprobar,
   validar, lista, empaquetar             estado, desinstalar, dependencias, sddm
                │                                   │
                ▼                                   ▼
   generado/<id>/  ·  sitio/generado/  ·  dist/     ~/.local/share/{color-schemes,plasma/…,aurorae/themes,wallpapers,…}
                                                    ~/.config/{Kvantum,alacritty,kitty,zed}  ·  /usr/share/sddm (pkexec)
```

## 3. Componentes

### 3.1 El tema global (`global/`)

Dos paquetes `Plasma/LookAndFeel` (`org.lliphi.claro`, `org.lliphi.oscuro`) que se aplican con Preferencias del sistema
→ Tema global o `plasma-apply-lookandfeel`. Responsabilidades: metadatos, la tipografía, la composición de
`contents/defaults` con lo que aporta cada módulo (`valores()`), la integración de los componentes (`integrar()`), las
vistas previas, la aplicación en la sesión (`aplicar.py`) y la lista de configuración que se respalda. Hereda de Breeze
(`X-KDE-fallbackPackage`) lo que no trae. Detalle: [`global/README.md`](../global/README.md).

### 3.2 Los seis módulos (`modulos/`)

| encargo | id | clase | entrega | formato y destino |
|---|---|---|---|---|
| Color Scheme | `esquema` | paquete | `LliphiClaro.colors`, `LliphiOscuro.colors`; la paleta (`tokens/tokens.json`) | KColorScheme, `color-schemes/` |
| Plasma Style | `estilo` | paquete | `lliphi-claro`, `lliphi-oscuro` | `Plasma/Theme`, `plasma/desktoptheme/` |
| Window Decoration | `decoracion` | paquete | `lliphi`, `lliphi-claro` | `KWin/Aurorae` (SVG V2), `aurorae/themes/` |
| Icons & Cursors | `iconos-cursores` | externo | Papirus y `Papirus-Dark-Lliphi`; WhiteSur-cursors (Bibata opcional) | freedesktop, `icons/` |
| Splash & Lockscreen | `carga-bloqueo` | componente | `contents/splash/`, `contents/logout/`; fondo del bloqueo | dentro del `Plasma/LookAndFeel`; `kscreenlockerrc` |
| Desktop Layout | `disposicion` | componente | `contents/layouts/org.kde.plasma.desktop-layout.js`; selectores de KWin | dentro del `Plasma/LookAndFeel` |

**Clases.** Un *paquete* entrega archivos propios en `generado/<id>/` y los instala en su sitio de KDE. Un
*componente* no tiene paquete propio porque KDE solo lo lee de dentro del tema global: lo desarrolla su módulo y el tema
global lo integra al construirse. Un módulo *externo* gestiona recursos de terceros que no se redistribuyen: los
instala a petición (`externas.py`) y aporta sus identificadores.

**Bloqueo de pantalla y SDDM.** En Plasma 6.6 la interfaz del bloqueo la carga `kscreenlocker_greet` del paquete de
shell (`plasma/shells/org.kde.plasma.desktop/contents/lockscreen/`), no del tema global: lo que un tema controla es el
fondo del bloqueo (`kscreenlockerrc`) y sus colores. El inicio de sesión es SDDM, otro programa y otro formato, fuera de
la sesión del usuario y con root: es el complemento `sddm`, no parte de `carga-bloqueo`.

### 3.3 Complementos (`complementos/`)

Lo que existía y no es parte de un `Plasma/LookAndFeel`: `fondos` (`Wallpaper/Images`; el tema global lo nombra y su
imagen la usan `carga-bloqueo` y `sddm`), `kvantum` (estilo de aplicaciones; el tema global nombra `widgetStyle`),
`konsole`, `terminales`, `editores`, `libreoffice` y `sddm`; y uno nacido después, fuera del escritorio: `obsidian`, el
tema de Obsidian que se publica en su repositorio propio (`achalmed/obsidian-lliphi`, decisión 5.1), y `navegadores`, los
temas de Zen Browser y de Chrome (decisión 5.3). Después, los de otras aplicaciones: `gtk` (GTK 3, GTK 4 y
libadwaita sobre Breeze, decisión 4.37), `xournalpp`, `gimp` y `calibre` (decisiones 5.20–5.22). `fondo-variante` (decisiones 4.26
y 4.28) no es un paquete de Plasma: es el programa que, al cambiar de variante, pone la imagen clara u oscura del mismo
fondo de Lliphi y el esquema de la variante en Konsole, con su archivo de inicio automático.
`telegram` (decisión 5.30) entrega los dos `.tdesktop-theme` de Telegram Desktop; Telegram los guarda en su `tdata/`
y sigue la variante solo, con su modo nocturno automático.

### 3.4 Lo compartido

`tokens/` (contrato de color y marca), `fuentes/base/` (WhiteSur-kde y Nothing con su licencia y `ORIGEN.md`),
`muestras/` (capturas reales, láminas y bocetos; de ahí salen las vistas previas), `sitio/` (Quarto; el catálogo se
genera desde los manifiestos) y `herramientas/{lamina,boceto,comparar,contacto}.py` (muestras).

## 4. Contrato de un módulo

```
<raíz>/<id>/            raíz: global/ (solo el tema global), modulos/ o complementos/
├── modulo.json         obligatorio
├── README.md           obligatorio: responsabilidad, formato, estructura, dependencias, cómo desarrollarlo
├── INSTALL.md          obligatorio: instalar, actualizar y desinstalar a mano (lo publica el sitio)
├── construir.py        paquete: generar(); componente: integrar(); opcional: valores()
├── aplicar.py          opcional: aplicar(ctx), respaldos(ctx), tras_instalar(ctx, aplicar), al_desinstalar(ctx, aplicar)
├── externas.py         externo (y quien tenga terceros): instalar(aplicar, opcionales)
├── ajustes.json        opcional: los valores editables del módulo, declarativos (los edita Lliphi Studio, `studio/`)
└── …                   fuentes propias (p. ej. escritorio.js de disposicion)
```

`modulo.json`:

| clave | qué |
|---|---|
| `nombre`, `resumen`, `tecnologia`, `estado`, `desde`, `licencia`, `archivos`, `capturas` | ficha del catálogo del sitio; `archivos` se valida contra lo generado |
| `clase` | `paquete` · `componente` · `externo` |
| `orden` | posición dentro de su raíz (orden de aplicación y del catálogo) |
| `formato` | `Plasma/LookAndFeel`, `KColorScheme`, `Plasma/Theme`, `KWin/Aurorae`, `Wallpaper/Images`, `Kvantum`, `Konsole`, `SDDM`, `freedesktop` o `varios`: decide qué comprueba `validar` |
| `dependencias.construccion` | módulos cuyo código usa al construirse (`registro.codigo("<id>")`); la validación rechaza los no declarados |
| `dependencias.integra` | solo el tema global: los componentes que lleva dentro |
| `dependencias.referencia` | módulos cuyos identificadores declara (lo que el tema global nombra) |
| `dependencias.herramientas` / `herramientas_opcionales` | órdenes del sistema obligatorias para instalar / que mejoran la aplicación |
| `dependencias.python`, `terceros`, `bases` | Pillow, coloraide; paquetes de terceros; bases de `fuentes/base/` |
| `integracion` | componente: `{"en": "global", "rutas": [...]}` que deben quedar dentro del paquete |
| `instalacion` | paquete: `[{"origen", "destino", "base"}]`; `origen` relativo a `generado/<id>/`, `destino` a la base (`data`, `config`, `vscode`, `positron`, `vscodium`); admiten `{id}`, `{id_esquema[claro]}`… de `tokens/marca.json` |

`ajustes.json` (opcional) separa los valores de cómo se usan: hoy lo tienen `esquema` (los OKLCH de la paleta),
`decoracion` (claves del `rc`, colores del título, botones, recoloreo), `disposicion` (paneles y widgets) e
`iconos-cursores` (temas y color de las carpetas). Se escribe con sangría de dos espacios; la paleta deja cada terna
OKLCH en una línea (`paleta.volcar_ajustes()`). Tras cambiarlo, `paleta.py --aplicar` si es la paleta y `generar.py`.

Funciones:

- `generar(tokens, marca, destino) -> list[Path]`: escribe la salida del paquete bajo `destino` (= `generado/<id>/`).
- `integrar(tokens, marca, variante, paquete, hechos)`: escribe dentro del paquete del tema global de la variante.
- `valores(marca, variante) -> {"archivo][grupo": {clave: valor}}`: lo que aporta a `contents/defaults`; cada clave
  tiene un solo dueño.
- `aplicar(ctx) -> int`: lo que hace en la sesión con `--aplicar-tema`; `ctx` da `variante`, `modulos`, `marca`,
  `tokens`, `DATA`, `CONFIG`, `kwrite()`, `ejecutar()`, `hay()`, `decir()` y `codigo()`. Distinto de 0 detiene la aplicación.
- `respaldos(ctx) -> [(ruta, "reponer"|"completar", rótulo)]`: qué copiar antes de instalar y cómo devolverlo en `UNDO.sh`.
- `tras_instalar(ctx, aplicar) -> [línea]`: lo que instala un módulo sin copiar archivos (la extensión de los editores,
  con `--install-extension`; decisiones 5.9), después de copiar y también al simular; devuelve las líneas de `UNDO.sh`
  que lo deshacen. `al_desinstalar(ctx, aplicar)`: lo retira con `instalar.py desinstalar`.

## 5. Construcción (`herramientas/generar.py`)

```bash
.venv/bin/python herramientas/generar.py                       # simula: construye en temporal y dice qué cambiaría
.venv/bin/python herramientas/generar.py --aplicar             # escribe generado/ y sitio/generado/
.venv/bin/python herramientas/generar.py --modulos estilo,global [--aplicar]
.venv/bin/python herramientas/generar.py verificar             # 1 si lo versionado difiere de una construcción nueva
.venv/bin/python herramientas/generar.py validar               # §7
.venv/bin/python herramientas/generar.py lista                 # módulos, clase, formato, dependencias
.venv/bin/python herramientas/generar.py verificar|validar --json   # en JSON, para Lliphi Studio (también instalar.py estado --json)
.venv/bin/python herramientas/generar.py empaquetar            # dist/: un tarball por paquete, SHA256SUMS, notas, ficha
```

El registro ordena la construcción por dependencias (`construccion` e `integra`; un ciclo es error). Pedir un
componente construye el tema global que lo integra; un externo no construye nada. `verificar` también señala carpetas de
`generado/` que no son de ningún módulo. Requisitos: Python ≥ 3.10 (3.11 para `validar`), Pillow para fondos, pantallas
y SDDM, coloraide para la paleta (`pip install -e ".[dev]"`).

## 6. Instalación, aplicación y desinstalación (`herramientas/instalar.py`)

```bash
python3 herramientas/instalar.py                                   # simula
python3 herramientas/instalar.py --aplicar [--modulos esquema,konsole]
python3 herramientas/instalar.py --aplicar --aplicar-tema oscuro   # además aplica en la sesión
python3 herramientas/instalar.py dependencias [--aplicar] [--opcionales]
python3 herramientas/instalar.py comprobar | estado | desinstalar [--aplicar] | sddm [--aplicar]
bash ~/.local/state/lliphi/respaldos/<fecha>/UNDO.sh                # vuelve exactamente a lo de antes
```

1. Comprueba Plasma ≥ 6 y las `herramientas` de lo que va a instalar (sale 2 si falta algo).
2. Calcula los pares origen → destino de los manifiestos; omite y avisa las bases condicionales sin su editor.
3. Se detiene (sale 3) si un destino tiene algo que no instaló Lliphi y no es idéntico.
4. Respalda lo que declaran los `respaldos()` de todos los módulos con su SHA-256 verificada.
5. Copia, corre los `tras_instalar()` de los módulos pedidos, anota `instalado.json` (rutas normalizadas, sumas,
   módulos, respaldo) y escribe `UNDO.sh` con lo que estos devuelven.
6. Con `--aplicar-tema`: `aplicar()` del tema global (si `plasma-apply-lookandfeel` falla, no sigue) y después el de
   cada módulo en el orden del registro; los componentes y externos del tema global se aplican siempre con él.

`comprobar` (sale 4 si falta algo): cada ruta del manifiesto existe y es igual a `generado/`; KDE reconoce cada
paquete (`kpackagetool6 --type <tipo> --show <id>` para tema global, estilo y decoración; los fondos no se resuelven
así ni los del sistema); los temas de iconos y cursores y las tipografías que nombra el tema global existen (aviso).
`desinstalar` retira lo del manifiesto y corre los `al_desinstalar()`, no lo de terceros. Nada de esto usa rutas absolutas del repositorio: todo
cuelga de la raíz del proyecto y de las variables XDG.

## 7. Validación y pruebas

`generar.py validar` comprueba, para los quince módulos: el manifiesto completo y coherente con su clase; que existan
`README.md`, `INSTALL.md`, las capturas y las bases; dependencias existentes, sin ciclos y declaradas para todo
`registro.codigo()`; cada origen de `instalacion` en `generado/`; la estructura real de lo generado según `formato`
(§1.1 de `migracion-modular.md`: `KPackageStructure` donde corresponde, `KPlugin.Id` = carpeta, `Version` = `VERSION`,
`[General] ColorScheme` = nombre, `X-Plasma-API`, SVG bien formados, `[SddmGreeterTheme]` con su `MainScript`…); y la
**integración**: cada identificador de `contents/defaults` (esquema, estilo, decoración con `aurorae.v2`, fondo, Kvantum,
iconos, cursores, pantalla de carga) existe en el módulo que lo entrega y cada ruta de cada componente está dentro del
paquete. Avisa si aparece un `contents/lockscreen/` (Plasma 6.6 lo ignoraría).

`pytest` (40 pruebas): tokens y contraste, deriva, estructura de cada formato, la línea base de los esquemas, la
arquitectura (registro, validación en verde y con fallos provocados, composición de `defaults`, componentes, orden de
dependencias), la instalación reversible en un `HOME` temporal con `comprobar`, `UNDO.sh` y el manifiesto heredado de
0.3.0, Kvantum con `XDG_CONFIG_HOME` no estándar, los atajos de compatibilidad y `reuse lint`. La CI corre paleta,
`verificar`, `validar`, `pytest`, `reuse lint` y el render del sitio. La validación visual se hace en una sesión de Plasma
anidada (`validacion.md` §5–§9).

## 8. Sesión de prueba y Lliphi Studio

`herramientas/sesion.py` arranca un Plasma anidado (`kwin_wayland` en ventana o `--virtual`) con su propio `HOME` en
`$XDG_CACHE_HOME/lliphi/sesiones/`, instala y aplica Lliphi dentro y deja abrir aplicaciones, ejecutar un guion de
scripting de Plasma y capturar; es la receta de `validacion.md` §8–§9 hecha orden. Toda orden que corre dentro toma el
entorno del `plasmashell` de prueba y se niega si su `HOME` no es el de prueba; `cerrar` termina por PID solo lo de
prueba y compara el `LockedHint` de la sesión real.

`studio/` es la ventana opcional (QML + Kirigami sobre `gui-comun` 2.7; `docs/rediseno.md`): cliente del proyecto, lee los manifiestos, los tokens, lo
generado y el estado de la instalación, escribe solo los `ajustes.json` y corre las órdenes de arriba
([`studio/README.md`](../studio/README.md)). Ningún módulo sabe que existe.

## 9. Desarrollar o modificar un módulo

1. Lee su `README.md`. Cambia su fuente (su `construir.py`, `escritorio.js`, la paleta…), nunca `generado/`.
2. `generar.py --modulos <id>` para ver qué cambia; `--aplicar` para escribirlo; `validar` y `pytest`.
3. Instálalo solo a él (`instalar.py --modulos <id> --aplicar`) y, si aporta a la sesión, pruébalo en una sesión anidada.
4. Si cambia un identificador, cambia el `valores()` del dueño: el tema global lo recoge solo.
5. Captura real a `muestras/capturas/` y fila en `compatibilidad.md`.

**Un módulo nuevo**: carpeta en `modulos/` o `complementos/` con el contrato del §4; si el tema global lo nombra,
añádelo a su `dependencias.referencia`; si va dentro del paquete, `clase: componente` e `integracion.en: global`, y a
`dependencias.integra`. Sin tocar el núcleo, el instalador ni el sitio: los tres lo descubren.

## 10. Compatibilidad

Comprobado en Plasma 6.6.6 (Kubuntu 26.04, Wayland, KF 6.24, Qt 6.10). Lo que depende de la versión: el motor SVG V2 de
Aurorae (`org.kde.kwin.aurorae.v2`, 6.6), `images_dark/` en los fondos (6.6), el bloqueo en el paquete de shell. Matriz
completa por componente en [`compatibilidad.md`](compatibilidad.md).
