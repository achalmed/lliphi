---
tipo: doc
estado: activo
titulo: 'Decisiones del proyecto y su porqué'
---
# Decisiones

Una entrada por decisión, con fecha, lo decidido y el motivo. Lo pendiente va a `../estado.md` §Por hacer.

## 1. Alcance y gobierno

- **1.1 (2026-10-18) Repositorio público y autónomo, exento del contrato de suites del ecosistema.** Quien lo clone no
  tiene `~/Documents/core`; las herramientas cargan solo la biblioteca estándar de Python (más `coloraide` para la
  paleta) y no leen `core/env.sh`. La selección del tema en la máquina del autor vive en `~/.dotfiles/kde`, no aquí.
- **1.2 (2026-10-18) El autor decide cuatro cosas:** nombre, paleta, alta en `meta/workspace.yml` y cualquier cambio en
  `web` o en `~/.dotfiles`. El resto lo decide el director y lo registra aquí.
- **1.3 (2026-10-18) Una versión para todo el proyecto** (SemVer en `CHANGELOG.md`); cada módulo declara desde qué
  versión existe. Varias versiones por módulo multiplicarían fichas y confusión.

## 2. Diseño

- **2.1 (2026-10-18) Fuente de verdad en OKLCH**, con `hex` de respaldo, en formato Design Tokens 2025.10. Motivo:
  luminosidad perceptual para derivar superficies y estados; Plasma tiñe en OKLab; el formato es intercambiable.
- **2.2 (2026-10-18) Un solo acento, el rojo de Nothing (matiz 25), que sigue al sistema.** El autor rechazó el verde
  azulado de la primera propuesta: el tema es la fusión de Nothing y WhiteSur. Nothing fija el rojo 258 veces en los SVG y
  WhiteSur el azul; aquí el acento es un token (y `azul` y `verde-azul` son variantes generadas) y los SVG propios usan `currentColor` con las clases
  `ColorScheme-*`, de modo que el acento del usuario o del fondo lo sustituye.
- **2.3 (2026-10-18) Texto claro sobre el acento en las dos variantes;** el acento del oscuro baja de luminosidad
  hasta cumplir 4.5:1. Alternativa descartada: texto oscuro sobre un acento brillante en la variante oscura (rompe
  la equivalencia de estados entre variantes).
- **2.4 (2026-10-18) Foco con el acento de mayor contraste de cada variante** (base en el claro, suave en el oscuro),
  porque el acento base no llega a 3:1 sobre el botón oscuro.
- **2.5 (2026-10-18) Sin translucidez en el primer lote.** WhiteSur cae a 3.27:1 sobre fondos claros; una variante
  translúcida vendrá como módulo con su contraste medido sobre fondos de prueba.
- **2.6 (2026-10-18) Sin imponer fuentes** desde `defaults`; Inter e IBM Plex Mono se recomiendan y el instalador las
  ofrece con `--fuentes`.
- **2.7 (2026-10-18) Neutros casi negros (Nothing) y grises suaves (WhiteSur claro)** con un matiz frío común (270)
  y croma ≤ 0.006; sustituye al «papel cálido / pizarra fría» de la primera propuesta, que el autor no reconoció
  como la fusión pedida. Las dos variantes comparten lógica y geometría y cambian solo las primitivas.

## 3. Técnica

- **3.1 (2026-10-18) Decoración Breeze coloreada por el esquema, no Aurorae.** Aurorae se reescribió en Plasma 6.6
  (motor SVG V2, QML aislado y con futuro incierto): es un artefacto de baja estabilidad. `[WM]` y `Colors:Header`
  bastan para la barra de título.
- **3.2 (2026-10-18) Sin Kvantum ni estilos compilados en C++** (Lightly archivado; Klassy con ramas por versión).
  Breeze lee el esquema; un tema que exige Kvantum se rompe con cada Qt.
- **3.3 (2026-10-18) GTK por el mecanismo de Plasma.** `kde-gtk-config` y `breeze-gtk` generan el CSS desde el
  esquema (`~/.config/gtk-4.0/colors.css` en esta máquina lo demuestra); un tema GTK propio competiría con eso.
- **3.4 (2026-10-18) Estilo de Plasma mínimo que hereda de Breeze** (`metadata.json` + `colors` + `plasmarc` + los SVG
  propios imprescindibles), como hace `breeze-dark`. Nothing copia 60 SVG idénticos de Breeze sin necesidad.
- **3.5 (2026-10-18) `generado/` se versiona** para que un usuario instale sin Python ni herramientas; una prueba de
  deriva (`generar.py verificar`) impide editarlo a mano, como `just check` en Catppuccin.
- **3.6 (2026-10-18) Instalador en Python con biblioteca estándar**, simulación por defecto, solo rutas de usuario,
  respaldo con SHA-256 y `UNDO.sh` en `~/.local/state/lliphi/`. Motivo: reversible, auditable, sin root.
- **3.7 (2026-10-18) SDDM y Plymouth fuera del instalador de usuario**: root y riesgo de bloquear el arranque; módulo
  posterior con confirmación explícita.
- **3.8 (2026-10-18) Ningún SVG ni recurso de terceros.** Los temas de partida son GPL y derivarlos obligaría a GPL y
  mancharía la originalidad; todo lo gráfico se dibuja aquí. Licencia: MIT para código y CC BY-SA 4.0 para activos,
  declarada por archivo con REUSE 3.3.
- **3.9 (2026-10-18) Sitio con Quarto**, el motor del hub del autor, como sitio satélite en Netlify que publica el
  `_site/` empujado (patrón de los 11 blogs) y enlazado desde el hub. Se confirma en la fase 8 tras inspeccionar
  el hub; alternativa: sección del hub.
- **3.10 (2026-10-18) Lámina de muestras con PyQt6 del sistema y Breeze sin pantalla.** Fuera de Plasma no hay plugin
  de plataforma: la QPalette se construye desde el esquema. Límite conocido: el foco del deslizador y la barra de
  progreso sale en azul Breeze en la lámina; la validación real es la fase 7.
- **3.11 (2026-10-18) Terminales y editores desde los mismos tokens, sin colores nuevos.** Lo que Konsole no define
  (selección, cursor, enlaces, bordes, pestañas) sale de los semánticos de la misma variante; la sintaxis de los
  editores deriva de los ANSI con una sola tabla (`editores.sintaxis`: palabras clave rojo, cadenas verde, números y
  constantes amarillo, funciones azul, tipos cian, atributos magenta, comentarios en el texto inactivo). Los resaltes
  que se superponen al texto llevan alfa (`#rrggbbaa`) sobre un color del maestro; la prueba de hexes lo admite
  recortando el alfa. Alternativa descartada: una paleta de sintaxis propia (más colores que medir y mantener).
- **3.12 (2026-10-18) La extensión de VS Code se instala fuera de XDG.** VS Code solo lee `~/.vscode/extensions/`
  (o `$VSCODE_EXTENSIONS`); el instalador añade esa base para ese único módulo, sin versión en el nombre de la carpeta
  (`lliphi.lliphi`) para que actualizar no deje carpetas viejas. Alternativa descartada: publicar en el Marketplace o
  empaquetar un `.vsix`, que exigen `vsce` y una cuenta; queda para cuando el autor publique. Ampliación (2026-10-18):
  Positron y VSCodium, derivados de VS Code, leen la misma extensión desde `~/.positron/extensions/` y
  `~/.vscode-oss/extensions/`; el instalador añade esas dos bases como **condicionales**: solo copia si ya existe la
  carpeta del editor y nunca la crea, porque crear `~/.positron` en una máquina sin Positron sería basura.
- **3.13 (2026-10-18) Iconos: solo carpetas, dos temas por herencia, 64 px escalable.** Un tema propio completo
  compite con Breeze y envejece con cada KDE; aquí se dibujan únicamente `folder`, `folder-open`, sus sinónimos y los
  lugares de uso común, con un distintivo geométrico desde 22 px (a 16 px no cabe). Hay dos temas porque la herencia
  (`breeze` o `breeze-dark`) es lo único que ven las aplicaciones GTK; en KDE, `FollowsColorScheme=true` y las clases
  `ColorScheme-Highlight` / `ColorScheme-HighlightedText` hacen que la carpeta siga el acento y su texto de contraste.
  El directorio de 64 px es `Scalable` hasta 512 para que las vistas grandes de Dolphin no caigan en la carpeta de
  Breeze. Alternativa descartada: directorios `@2x`/`@3x` (los SVG ya escalan; se añadirán si la validación real
  muestra desalineación en 150 %).
- **3.14 (2026-10-18) LibreOffice: extensión `.oxt` de configuración y fragmento `.xcu`; el instalador no toca
  LibreOffice.** LibreOffice no tiene carpeta de temas: los esquemas de «Colores de la aplicación» viven en el set
  `org.openoffice.Office.UI/ColorScheme/ColorSchemes` de su configuración, cuyas capas son los `.xcd` del programa (root),
  las extensiones (`unopkg`, `~/.config/libreoffice/4/user/uno_packages/`) y `registrymodifications.xcu`, que LibreOffice
  reescribe entero al cerrar. Por eso se generan (a) un `.oxt` solo de configuración (`oor:component-data`, sin código),
  reproducible byte a byte para la prueba de deriva, que se instala con `unopkg add` o el Gestor de extensiones, y (b)
  fragmentos `<oor:items>` con el formato exacto que LibreOffice escribe (`org.openoffice.Office.UI:ColorScheme['…']`,
  `oor:op="fuse"`) para quien prefiera pegarlos. El instalador no tiene módulo `libreoffice`: copiar a
  `~/.config/libreoffice/4/user/` un archivo que LibreOffice no lee sería engañoso, sobrescribir
  `registrymodifications.xcu` rompería la configuración del usuario, y ejecutar `unopkg` desde el instalador falla con
  LibreOffice abierto y crea un perfil donde no lo hay. La lista de 91 entradas sale del esquema real de 26.2 (`main.xcd`)
  y no de la de 24.8 del encargo (`ObjectBoundaries` y `WriterScriptIndicator` ya no existen); las versiones anteriores
  ignoran lo que no conocen. Los colores de interfaz (`WindowColor`…) se incluyen con la lógica del esquema de Plasma,
  pero solo actúan si el usuario activa el tema de LibreOffice (`Appearance/LibreOfficeTheme`): por omisión la interfaz
  la sigue dando Plasma y Lliphi solo pinta el documento.


## 4. Cambio de enfoque de 0.2.0 (decisión del autor, 2026-10-18)

- **4.1 Derivar de lo que existe, no dibujar desde cero.** El autor rechazó 0.1.0 («Breeze con detalles en rojo») y los
  iconos y la decoración dibujados a mano («todo feo»). Desde ahora Lliphi se construye a partir de los dos temas que
  eligió y de lo mejor que hay publicado: el estilo de Plasma, el tema Kvantum y la decoración Aurorae de
  **WhiteSur-kde** (GPL-3.0) recoloreados con los tokens y sin lo que imita a Apple; los botones de **Nothing** (GPL-3.0);
  iconos **Papirus** con carpetas rojas; cursores **Bibata**; tipografía **IBM Plex**. Deroga 3.1, 3.2, 3.4 y 3.8 en lo que
  contradigan. Consecuencia: lo derivado es GPL-3.0-or-later (REUSE.toml, `fuentes/base/ORIGEN.md`); lo propio sigue en MIT.
- **4.2 Kvantum sí.** Es lo que da a WhiteSur su aspecto en las aplicaciones (menús y ventanas translúcidos con desenfoque).
  El instalador lo configura si está instalado (`qt6-style-kvantum`) y, si no, deja Breeze con menús translúcidos.
- **4.3 Dependencias descargadas, no redistribuidas.** `herramientas/dependencias.py` trae Papirus y Bibata de sus
  versiones publicadas al `~/.local/share/icons` del usuario; el repositorio solo las cita.
- **3.15 (2026-10-18) Decoración Aurorae derivada, no dibujada.** El autor rechazó una primera decoración propia
  (anillos, sombra por degradados) por parecer «Breeze con detalles rojos» y fijó el criterio: partir del código que
  existe. La decoración deriva de dos temas GPL-3.0-or-later copiados sin cambios a `fuentes/aurorae/base/`: el marco,
  los radios, la sombra y la disposición de WhiteSur-dark (vinceliuice) y los botones circulares de Nothing (jomada).
  `herramientas/destinos/aurorae.py` reescribe solo los colores (hex de los tokens; cerrar en el acento, los demás en
  gris: sin semáforo) y los valores del rc que cambian (barra de 30 px, botones a la derecha, título sin sombra).
  Consecuencia: `fuentes/aurorae/**` y `generado/aurorae/**` son GPL-3.0-or-later (excepción a la decisión 3.8,
  declarada en `REUSE.toml`), y la decoración se publica como módulo aparte con esa licencia. Lo aprendido del motor
  V2 con la versión dibujada (recarga, estados, `metadata.desktop`) queda en `validacion.md` §6.
- **4.4 (2026-10-18, 18:10) La línea base es la configuración activa del autor** (`docs/linea-base.md`): WhiteSur-dark tal
  cual (tema global, estilo, esquema azul), decoración Nothing, Kvantum LliphiOscuro, breeze-dark, cursores WhiteSur, y la
  única novedad pedida: Inter (interfaz) y Hack (mono). Las mejoras entran una a una con su visto bueno. Deroga lo de 4.1 que
  recoloreaba el estilo de Plasma y usaba Papirus/Bibata/Hack como predeterminados: quedan como opcionales.
- **4.5 (2026-10-18, 18:30) Mejora 1: el acento rojo entra en el esquema, nada más** (`docs/linea-base.md` §2.1).
  `herramientas/destinos/esquema.py` copia WhiteSurDark/WhiteSur y sustituye solo los valores que WhiteSur usa como
  acento (sus azules: 49,91,239 y derivados) por el token de la misma función: `DecorationFocus`→`foco`,
  `DecorationHover`→`hover`, `ForegroundLink`→`enlace`, `ForegroundActive`→`acento.texto`, `ForegroundVisited`→
  `acento.suave`, y en `Colors:Selection` el fondo→`seleccion.fondo`, el alterno→`acento.suave` y los textos→
  `seleccion.texto`. Se conserva el alfa (`,150`) de los valores atenuados. Los grises, los estados (negativo, neutral,
  positivo), `[WM]` y `[ColorEffects:*]` quedan como en WhiteSur. Se aplicó solo con `plasma-apply-colorscheme` en la
  sesión del autor (tema global, estilo, Kvantum y decoración intactos); reversión: `plasma-apply-colorscheme WhiteSurDark`.
  Aprobada por el autor a las 18:35 sobre `muestras/comparacion-linea-base-acento.png`.
- **4.6 (2026-10-18, 18:50) Mejora 2: la variante clara se comprueba en sesión anidada, no en la del autor**
  (`docs/linea-base.md` §2.2, `docs/validacion.md` §7). `org.lliphi.claro` ya era la equivalente (WhiteSur claro tal cual,
  `LliphiClaro` con el acento de la mejora 1, `lliphi-claro`, Kvantum `LliphiClaro`, `breeze`); lo único que desentonaba
  era el foco azul de Kvantum: `WhiteSur.svg` usa `#0860f2` como acento (47 usos) y `herramientas/destinos/kvantum.py`
  solo mapeaba `#315bef` (el acento del oscuro). Se mapean `#0860f2`→`acento.base`, `#0e4bb4`/`#0852ce`/`#1352c4`→
  `acento.texto`, `#77aff1`→`acento.suave`. No se aplica nada en la sesión del autor: la variante clara se le propone con
  la captura y la prueba en su sesión queda a su mano (instrucciones en `estado.md`). Observado y dejado como está: las
  carpetas de `breeze` (claro) son azules fijas, a diferencia de `breeze-dark` que sigue el acento: es la mejora 3 (iconos).
  Aprobada por el autor a las 18:58.
- **4.7 (2026-10-18, 19:05) Mejora 3: Papirus con carpetas rojas, tal cual, como iconos de la línea base**
  (`docs/linea-base.md` §2.3). Papirus (GPL-3.0) ya estaba descargado por `herramientas/dependencias.py` con los
  `folder-red-*` enlazados sobre `folder-*` (lo que hace `papirus-folders`); se usa su rojo propio (`#e25252` /
  `#bf4b4b`), no el de los tokens (`#c93436`): derivar de lo que existe sin redibujar; si el autor quiere el rojo exacto,
  el paso siguiente sería sustituir esos dos hex en los `folder-red-*` descargados. `Papirus-Dark` (oscuro) y `Papirus`
  (claro) pasan a `defaults` del tema global, al instalador (`plasma-changeicons`, con Breeze de reserva) y a las
  dependencias por defecto; Bibata sigue opcional. Aplicado en la sesión del autor solo con
  `plasma-changeicons Papirus-Dark` (reversión: `plasma-changeicons breeze-dark`). Pendiente de su visto bueno sobre
  `muestras/comparacion-linea-base-iconos.png`. Aprobada por el autor a las 19:12: con ella se cierra la línea base.
- **4.8 (2026-10-19) Mejora 4: decoración Nothing con dos plus** (sin tocar formas ni tamaños): el anillo cian del botón de
  minimizar (`#9cdde4`) pasa al gris del anillo de maximizar (`#bdbab8`), y el título usa los grises de los tokens
  (`texto.normal`, `texto.inactivo`) sin sombra en vez del lavanda de Nothing. Además se corrige un fallo del instalador: escribía
  Inter Medium en `[WM] activeFont` pero emitía la señal de paleta (`notifyChange 0`) y no la de fuentes, así que KWin seguía
  dibujando los títulos en Hack hasta reiniciar la sesión; ahora emite `org.kde.KDEPlatformTheme.refreshFonts`, la misma del
  módulo de Tipografías. Comparación en `muestras/comparacion-linea-base-decoracion.png`. Aprobada por el autor el 2026-10-19.
- **4.9 (2026-10-19) Mejora 5: Konsole con el esquema Lliphi Oscuro.** El perfil por defecto del autor usaba Breeze; ahora
  toma `Lliphi Oscuro` (fondo casi negro, ANSI de los tokens, opacidad 0,86 con desenfoque) y conserva FiraCode Nerd Font,
  que el prompt y `lsd` necesitan para sus iconos. El instalador, con `--aplicar-tema`, respalda el perfil por defecto
  (`konsolerc` → `DefaultProfile`), cambia solo `ColorScheme` en `[Appearance]` y edita el archivo real para no romper el
  enlace de dotfiles; `UNDO.sh` lo restaura. Comparación en `muestras/comparacion-linea-base-konsole.png`. Aprobada por el autor el 2026-10-19.
- **4.10 (2026-10-19) Mejora 6: pantallas de carga y de salida derivadas de WhiteSur-dark.** El tema global declaraba su
  propia pantalla de carga sin traerla, y Plasma caía en la de Breeze sobre negro; el diálogo de salida también era el de
  Breeze. Ahora ambos paquetes incluyen `contents/splash/` y `contents/logout/` de WhiteSur-dark con el fondo de Lliphi
  dentro del paquete y, en lugar del logotipo de Apple, «Lliphi» en Inter Light con el punto en el rojo del acento. Se
  previsualizan sin cerrar la sesión con `ksplashqml org.lliphi.oscuro --test --window` y
  `ksmserver-logout-greeter --windowed --lookandfeel org.lliphi.oscuro` (este con `timeout -s KILL 8`: tiene una cuenta atrás
  de 30 s que ejecuta la acción). Comparación en `muestras/comparacion-linea-base-pantallas.png`, con la foto del autor pixelada. Aprobada por el autor el 2026-10-19.
- **4.11 (2026-10-19) Mejora 7: inicio de sesión (SDDM) derivado de WhiteSur-dark.** Sustituye al de Kubuntu: fondo de
  Lliphi, Inter y un borde en el rojo del acento cuando el campo tiene el foco; sin logotipo. El saludador de SDDM no lee la
  configuración del autor, así que el rojo va en el propio tema (`Kirigami.Theme.highlightColor` y el borde del campo) y la
  fuente en `[Theme] Font` de `/etc/sddm.conf.d/99-lliphi.conf` y en `font=` de `theme.conf`. `Kirigami.Theme.defaultFont` es
  de solo lectura: asignarlo hace que SDDM muestre su pantalla de error. Es la única pieza con root:
  `herramientas/instalar_sddm.py --aplicar` usa pkexec (la contraseña la escribe el autor) y deja `UNDO.sh`. Las caras de los
  usuarios son las de AccountsService, no del tema. Comparación en `muestras/comparacion-linea-base-inicio-de-sesion.png`. Aprobada por el autor el 2026-10-19.
