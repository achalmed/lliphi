---
tipo: doc
estado: activo
titulo: 'Reingeniería modular (2026-10-31): auditoría, diseño, plan de migración, inventario y verificación'
---
# Reingeniería modular

Encargo del autor del 2026-10-31: pasar de una arquitectura monolítica a un tema global integrador con seis módulos
y un sistema central de construcción e instalación, **sin cambiar la identidad ni lo que se instala**. Este documento
es el expediente del cambio (auditoría → diseño → plan → respaldo → ejecución → verificación); la arquitectura
resultante, como referencia viva, está en [`arquitectura.md`](arquitectura.md).

## 1. Auditoría del estado anterior (etiqueta `antes-arquitectura-modular-2026-10-31`)

Lo que había y funcionaba (línea base medida antes de tocar nada): `generar.py verificar` sin deriva (271 archivos,
204 en `generado/` y 67 en `sitio/generado/`), 24 pruebas en verde, una instalación de prueba en un `HOME` aparte con
183 archivos.

| pieza | dónde vivía | qué hacía |
|---|---|---|
| tokens | `tokens/tokens.json` (lo escribe `herramientas/paleta.py`), `tokens/marca.json` | fuente única de color, tipografía, efectos e identificadores |
| generadores | `herramientas/destinos/*.py` (12) | un generador por tipo de archivo, registrados a mano en `DESTINOS` de `generar.py` |
| bases de terceros | `fuentes/base/WhiteSur-kde`, `fuentes/base/Nothing-aurorae` | copias de partida con su licencia y `ORIGEN.md` |
| derivados | `generado/<tipo de KDE>/` (`color-schemes`, `desktoptheme`, `aurorae`, `look-and-feel`, `wallpapers`, …) | lo que se instala; versionado; no se edita |
| instalador | `herramientas/instalar.py` (416 líneas) | tabla `MODULOS` escrita a mano y una sola función que copia, respalda y además aplica todo (fondo, bloqueo, Kvantum, tipografía, iconos, decoración, Konsole) |
| dependencias de terceros | `herramientas/dependencias.py` | Papirus y el superpuesto `Papirus-Dark-Lliphi`, WhiteSur-cursors, Bibata (opcional), JetBrains Mono Nerd Font, comprobación de Inter |
| SDDM | `herramientas/instalar_sddm.py` | única pieza con root (pkexec) |
| catálogo del sitio | `modulos/<id>/{modulo.json,INSTALL.md}` (9) | solo para el sitio; no lo leían ni el generador ni el instalador |
| empaquetado | `generar.py empaquetar` | tercera tabla escrita a mano (`paquetes`) |

**Rasgos monolíticos** (lo que esta reingeniería corrige):

1. **Tres tablas de módulos que había que mantener a la par**: `DESTINOS` (generar), `paquetes` (empaquetar) y
   `MODULOS` (instalar), más el catálogo del sitio. Añadir un módulo exigía tocar cuatro sitios.
2. **El generador del tema global hacía de todo**: `lookandfeel.py` escribía los metadatos, los `defaults` (con los
   identificadores de esquema, estilo, decoración, iconos, cursores, fondo, Kvantum, tipografía y pantalla de carga
   escritos en línea), la disposición del escritorio (un script JavaScript dentro de una cadena de Python) y las
   pantallas de carga y de salida.
3. **El instalador aplicaba todos los componentes en una sola función** de 120 líneas: no se podía cambiar la
   aplicación de un componente sin tocar las de los demás.
4. **Lo que se instala no se distinguía por módulo**: `generado/` estaba ordenado por tipo de archivo de KDE, no por
   responsabilidad, y los iconos, los cursores, las pantallas y la disposición no tenían lugar propio.
5. **Una ruta relativa frágil**: Kvantum se instalaba en `$XDG_DATA_HOME/../../.config/Kvantum`, que solo acierta si
   `XDG_DATA_HOME` y `XDG_CONFIG_HOME` tienen sus valores por omisión.
6. **Sin validación de estructura ni de referencias**: nada comprobaba que los identificadores que declara el tema
   global existieran en los paquetes que se generan, ni que KDE reconociera lo instalado.

**Defectos previos que no son de arquitectura** (se anotan, no se corrigen aquí, regla 12 del encargo):
`herramientas/contacto.py` importa `destinos.iconos`, retirado antes de esta reingeniería, y no funciona; `REUSE.toml`
cita `fuentes/aurorae/**`, que no existe (la base de Nothing está en `fuentes/base/Nothing-aurorae`) y declara
CC BY-SA para el estilo de Plasma derivado de WhiteSur, cuyos metadatos dicen GPL-3.0-or-later.

### 1.1 Comprobado en Plasma 6.6.6 (no supuesto)

- **Formatos de paquete distintos** (`kpackagetool6 --list-types` y los paquetes de `/usr/share`): el tema global es
  un KPackage `Plasma/LookAndFeel` (`metadata.json` con `KPackageStructure`); el estilo de Plasma es `Plasma/Theme`
  (`metadata.json` con `X-Plasma-API`, sin `KPackageStructure`, en `plasma/desktoptheme/`); la decoración es
  `KWin/Aurorae` (`aurorae/themes/`); el fondo es `Wallpaper/Images` (`wallpapers/`); el esquema de color es un
  archivo `.colors` suelto (KColorScheme, no es KPackage); iconos y cursores son temas freedesktop (`index.theme`);
  SDDM usa `metadata.desktop` con `[SddmGreeterTheme]` y vive en `/usr/share/sddm/themes/`.
- **La pantalla de bloqueo no está en el tema global**: el saludador (`kscreenlocker_greet`) carga `lockscreen` del
  *paquete de shell* (`/usr/share/plasma/shells/org.kde.plasma.desktop/contents/lockscreen/LockScreen.qml`, cadenas
  `ShellPackage` y `lockscreenmainscript` del binario), y `org.kde.breeze.desktop` no trae `contents/lockscreen/`. Un
  `LockScreen.qml` dentro de un look-and-feel se ignoraría. Lo que un tema controla del bloqueo es su fondo
  (`kscreenlockerrc`, grupo `[Greeter][Wallpaper][org.kde.image][General]`) y sus colores (esquema y estilo).
- **La pantalla de carga sí es del tema global**: `[KSplash] Theme=<id>` carga `contents/splash/Splash.qml` del
  look-and-feel con ese `Id`; lo mismo el diálogo de salida (`contents/logout/`) y la disposición
  (`contents/layouts/org.kde.plasma.desktop-layout.js`).
- `kpackagetool6 --type <tipo> --list` con `XDG_DATA_HOME` apuntando a un `HOME` de prueba enumera los paquetes de
  usuario: sirve para comprobar que KDE reconoce lo instalado sin tocar la sesión.

## 2. Diseño

Un tema global que integra, seis módulos con responsabilidad propia, siete complementos que existían y se conservan
fuera del tema global, y un núcleo común que descubre todo por sus manifiestos. Detalle en
[`arquitectura.md`](arquitectura.md).

| módulo (encargo) | id | clase | qué entrega | formato KDE |
|---|---|---|---|---|
| Global Theme | `global` | paquete integrador | `org.lliphi.claro`, `org.lliphi.oscuro` | `Plasma/LookAndFeel` |
| Color Scheme | `esquema` | paquete | `LliphiClaro.colors`, `LliphiOscuro.colors` (+ `-tokens`); dueño de la paleta | KColorScheme |
| Plasma Style | `estilo` | paquete | `lliphi-claro`, `lliphi-oscuro` | `Plasma/Theme` |
| Window Decoration | `decoracion` | paquete | `lliphi`, `lliphi-claro` | `KWin/Aurorae` (motor SVG V2) |
| Icons & Cursors | `iconos-cursores` | externo | Papirus y `Papirus-Dark-Lliphi`; WhiteSur-cursors (Bibata opcional) | tema freedesktop |
| Splash & Lockscreen | `carga-bloqueo` | componente | `contents/splash/`, `contents/logout/` del tema global; fondo del bloqueo | parte del `Plasma/LookAndFeel` + `kscreenlockerrc` |
| Desktop Layout | `disposicion` | componente | `contents/layouts/org.kde.plasma.desktop-layout.js`; selectores de KWin | parte del `Plasma/LookAndFeel` |

Complementos (fuera del tema global, se conservan): `fondos` (`Wallpaper/Images`), `kvantum`, `konsole`,
`terminales`, `editores`, `libreoffice`, `sddm`.

Decisiones de diseño:

- **Los identificadores existentes no cambian** (`esquema`, `estilo`, `decoracion`, `global`, `fondos`, …): las
  órdenes documentadas (`instalar.py --modulos esquema,konsole`), el manifiesto de instalación del autor
  (`~/.local/state/lliphi/instalado.json`) y las páginas publicadas del catálogo siguen valiendo. Los tres módulos
  nuevos llevan id en español, como el resto del proyecto (N 1.13).
- **Cada módulo se describe a sí mismo** (`modulo.json`: clase, formato, dependencias de construcción, referencias e
  instalación) y el núcleo lo descubre: desaparecen las tres tablas.
- **El tema global compone, no duplica**: cada módulo aporta sus claves de `contents/defaults` (`valores()`) y los
  componentes escriben sus carpetas dentro del paquete (`integrar()`); el tema global solo fija el orden y añade lo
  suyo (metadatos, tipografía, vistas previas). Ningún archivo de otro módulo se copia dentro del tema global salvo los
  que KDE exige que estén ahí (carga, salida, disposición).
- **`generado/<id>/` es exactamente lo que entrega un módulo** (y lo que va en su tarball); los componentes no tienen
  carpeta propia porque su salida vive, por exigencia de KDE, dentro de `generado/global/<Id>/contents/`.
- **Lo que se instala no cambia**: mismo árbol, mismos bytes; se demuestra comparando sumas (§5).
- **Las órdenes no cambian**: `generar.py` construye, valida, verifica y empaqueta; `instalar.py` instala, aplica,
  desinstala, comprueba e instala dependencias. Ambas son fachadas de `herramientas/nucleo/`.
  `dependencias.py` e `instalar_sddm.py` quedan como atajos de compatibilidad (documentados en la versión 0.3.0 publicada).

## 3. Plan de migración (ejecutado en este orden)

1. Línea base de equivalencia: sumas de `generado/`, `sitio/generado/` y de una instalación en un `HOME` de prueba.
2. Respaldo (N 3.13, 3.16, 3.17): etiqueta `antes-arquitectura-modular-2026-10-31`; `git bundle --all` verificado,
   copia `rsync` contrastada con `sumas.sha256` y `UNDO.sh` (`git reset --keep`) en
   `$RESPALDOS_DIR/renombres/2026-10-31-lliphi-arquitectura-modular/`; trabajo en la rama
   `wip/2026-10-31-arquitectura-modular`.
3. Traslados con `git mv` (conservan la historia), según el inventario del §4.
4. Núcleo (`herramientas/nucleo/`): registro, construcción, validación, instalación y sitio.
5. Partir `lookandfeel.py` y `instalar.py` en los módulos; tema global como integrador.
6. Regenerar `generado/` en su nueva disposición y comparar con la línea base.
7. Pruebas, `generar.py validar`, `reuse lint`, render del sitio, instalación en `HOME` de prueba,
   `kpackagetool6`, y aplicación en una sesión de Plasma anidada.
8. Documentación: `arquitectura.md`, un `README.md` por módulo, README, CONTRIBUTING, sitio, CHANGELOG y `estado.md`.

## 4. Inventario: qué se conserva y adónde va

| antes | después | módulo |
|---|---|---|
| `herramientas/destinos/__init__.py` | `herramientas/nucleo/__init__.py` | núcleo |
| `herramientas/destinos/sitio.py` | `herramientas/nucleo/sitio.py` | núcleo |
| `generar.py` (tablas `DESTINOS`, `paquetes`) | `generar.py` + `nucleo/construccion.py`, `nucleo/registro.py`, `nucleo/validacion.py` | núcleo |
| `instalar.py` (tabla `MODULOS`, copia, respaldo, UNDO, estado) | `instalar.py` + `nucleo/instalacion.py` | núcleo |
| `herramientas/destinos/lookandfeel.py`: metadatos, `defaults`, vistas previas | `global/construir.py` | global |
| `instalar.py`: `plasma-apply-lookandfeel`, menús de Breeze, tipografía en vivo | `global/aplicar.py` | global |
| `dependencias.py`: JetBrains Mono Nerd Font, comprobación de Inter | `global/externas.py` | global |
| `modulos/global/{modulo.json,INSTALL.md}` | `global/` | global |
| `herramientas/paleta.py` | `modulos/esquema/paleta.py` (sigue escribiendo `tokens/tokens.json`) | esquema |
| `herramientas/destinos/esquema.py` | `modulos/esquema/construir.py` | esquema |
| `herramientas/destinos/desktoptheme.py` | `modulos/estilo/construir.py` | estilo |
| `herramientas/destinos/aurorae.py` | `modulos/decoracion/construir.py` | decoración |
| `instalar.py`: `kwinrc` de la decoración y `reconfigure` de KWin | `modulos/decoracion/aplicar.py` | decoración |
| `dependencias.py`: Papirus, superpuesto, WhiteSur-cursors, Bibata | `modulos/iconos-cursores/externas.py` | iconos y cursores |
| `instalar.py`: tema de iconos (con reservas Papirus-Dark y Breeze) | `modulos/iconos-cursores/aplicar.py` | iconos y cursores |
| `lookandfeel.py`: `pantallas()` (carga y salida desde WhiteSur-dark) | `modulos/carga-bloqueo/construir.py` | carga y bloqueo |
| `instalar.py`: fondo oscuro del bloqueo en `kscreenlockerrc` | `modulos/carga-bloqueo/aplicar.py` | carga y bloqueo |
| `lookandfeel.py`: cadena `LAYOUT` | `modulos/disposicion/escritorio.js` + `construir.py` | disposición |
| `herramientas/destinos/fondo.py` + aplicación del fondo | `complementos/fondos/{construir,aplicar}.py` | fondos |
| `herramientas/destinos/kvantum.py` + activación de Kvantum | `complementos/kvantum/{construir,aplicar}.py` | Kvantum |
| `herramientas/destinos/konsole.py` + perfil de Konsole | `complementos/konsole/{construir,aplicar}.py` | Konsole |
| `herramientas/destinos/{terminales,editores,libreoffice}.py` | `complementos/<id>/construir.py` | complementos |
| `herramientas/destinos/sddm.py`, `herramientas/instalar_sddm.py` | `complementos/sddm/{construir,instalar_sddm}.py` | SDDM |
| `modulos/{fondos,konsole,terminales,editores,libreoffice}/` | `complementos/<id>/` | complementos |
| `generado/color-schemes/` | `generado/esquema/` | |
| `generado/desktoptheme/` | `generado/estilo/` | |
| `generado/aurorae/` | `generado/decoracion/` | |
| `generado/look-and-feel/` | `generado/global/` | |
| `generado/wallpapers/` | `generado/fondos/` | |
| `generado/{kvantum,konsole,terminales,editores,libreoffice,sddm}/` | igual | |
| `fuentes/base/`, `tokens/`, `muestras/`, `docs/`, `sitio/` | igual | compartidos |
| `herramientas/{lamina,boceto,comparar,contacto}.py` | igual | herramientas de muestras |
| `docs/arquitectura.md` (fase 5) | `docs/historial/arquitectura-0.3.md` | historia |

## 5. Verificación

| comprobación | resultado |
|---|---|
| `generar.py verificar --modulos <los 11 paquetes>` antes de tocar el sitio | 204 archivos, **0 diferencias** con lo de 0.3.0 trasladado |
| `generar.py verificar` (todo) | 278 archivos al día; el sitio cambia solo en el catálogo (módulos nuevos y enlaces) y en las dos capturas nuevas |
| `modulos/esquema/paleta.py --aplicar` | `tokens.json` idéntico salvo la ruta que cita su `$description` |
| instalación en `HOME` de prueba con el instalador nuevo frente al de 0.3.0 | **181 archivos idénticos** (sumas); `UNDO.sh` con las mismas restauraciones; difieren el orden de los `rm` y la ruta de Kvantum, ahora normalizada |
| `generar.py validar` | 14 módulos, 0 errores, 0 avisos |
| `pytest` | 33 en verde (24 anteriores adaptadas, 9 nuevas) |
| `reuse lint` | 1012/1012 archivos con licencia |
| sesión de Plasma 6.6 anidada | instalación, aplicación de las dos variantes, `comprobar`; defectos en `validacion.md` §9 |

Encontrado y corregido durante la verificación: `disposicion/aplicar.py` solo declara `respaldos()` y el núcleo
intentaba llamar a su `aplicar()` (lo destapó la aplicación real; prueba `test_orden_de_aplicacion`); `comprobar` usaba
`kpackagetool6 --list`, que omite los paquetes sin `KPackageStructure` (ahora `--show`).

## 6. Vuelta atrás

Mientras `main` no reciba otro commit: `bash "$RESPALDOS_DIR/renombres/2026-10-31-lliphi-arquitectura-modular/UNDO.sh"`
(`git reset --keep` a la etiqueta). El trabajo está en la rama `wip/2026-10-31-arquitectura-modular`, sin fusionar ni
publicar; después de fusionar, `git revert`. El respaldo completo (bundle verificado, copia y sumas) está en la misma
carpeta.

