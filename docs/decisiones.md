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
- **4.12 (2026-10-19) Un acento por variante, cada uno de su tema de partida** (decisión del autor: «el rojo para el
  tema oscuro y el azul para el tema claro, y así aprovechamos los dos colores de Nothing y WhiteSur»). `paleta.py` tiene
  `ACENTO = {"claro": "azul-whitesur", "oscuro": "rojo"}`: el oscuro conserva el rojo de Nothing (#c93436) y el claro toma el
  azul exacto de WhiteSur (#315bef, 5,4:1 con blanco), con un azul suave (#4777f0) apenas más oscuro que el #4f7fef de WhiteSur
  para que el hover cumpla 3:1 sobre los botones. Todo lo que sale de los tokens (esquemas, Kvantum, Konsole, editores,
  terminales, pantalla de carga) sigue la regla. Excepción: el botón de cerrar de Nothing sigue rojo en la decoración clara,
  porque su rojo significa «cerrar», no acento (excepción revertida en 4.33: cerrar va en azul en el claro). `--acento X` sigue poniendo el mismo acento en las dos variantes para probar.
- **4.13 (2026-10-19) Mejora 8: el acento llega al estilo de Plasma.** El `colors` del estilo (copiado de WhiteSur en la línea
  base) seguía con el azul de WhiteSur en 28 claves, así que interruptores, deslizadores y resaltados del panel, la bandeja y los
  plasmoides salían azules mientras las aplicaciones ya iban en rojo. Ahora pasa por la misma sustitución de solo acento que el
  esquema (`esquema.con_acento`): rojo en el oscuro y el azul de WhiteSur en el claro. Comparación en
  `muestras/comparacion-linea-base-acento-plasma.png`, tomada con `plasmawindowed` para fotografiar solo el plasmoide. Aprobada por el autor el 2026-10-19.
- **4.14 (2026-10-19) Mejora 9: una sola monoespaciada, JetBrains Mono (Nerd Font).** El autor trajo una recomendación
  tipográfica (Inter, IBM Plex Sans, JetBrains Mono, Red Hat Text, Atkinson Hyperlegible) y delegó la decisión. Se decide:
  (1) **Inter se queda** para la interfaz, con Inter Medium en los títulos (aprobado en la mejora 4); (2) **JetBrains Mono**
  sustituye a Hack como monoespaciada del sistema y a FiraCode en Konsole, en su versión Nerd Font para conservar los iconos del
  prompt y de `lsd`: una sola monoespaciada en todo el escritorio en vez de dos; (3) **IBM Plex Sans no entra**: es tipografía de
  documentos, no de escritorio, y la interfaz ya tiene a Inter; Red Hat Text y Atkinson tampoco, por la misma razón; (4) el
  suavizado ya era el recomendado (antialias, `hintslight`, subpíxel RGB) y no se toca. La fuente se descarga de la versión
  publicada de ryanoasis/nerd-fonts (OFL-1.1) con `dependencias.py`, en el usuario y sin root; el instalador solo la pone en
  Konsole si está instalada. Comparación en `muestras/comparacion-linea-base-monoespaciada.png`. Aprobada por el autor el 2026-10-19.
- **4.15 (2026-10-19) Carpetas en el acento de cada variante sin tocar Papirus.** La mejora 3 coloreaba de rojo las carpetas
  modificando los enlaces dentro de Papirus; con la regla 4.12 el claro las necesita azules, y no se puede: Papirus-Dark comparte
  con Papirus los tamaños grandes por enlaces simbólicos. Ahora `dependencias.py` deja Papirus como en su versión publicada
  (carpetas azules, para el claro) y crea `Papirus-Dark-Lliphi`, un tema superpuesto que hereda de Papirus-Dark y solo declara
  enlaces a las variantes rojas de todo icono que acaba en una carpeta azul (lugares, `inode-directory`, `user-home`…). El
  oscuro usa ese superpuesto. Efecto secundario bueno: Home y Escritorio, que antes quedaban azules en el oscuro, ahora son rojos.
- **4.37 (2026-11-01) GTK con los neutros de los tokens, sobre Breeze y sin tema propio.** El autor pidió los temas de
  Lliphi para las aplicaciones GTK. Medido en su escritorio: GTK 3 y GTK 4 usan Breeze (el portal de KDE da
  `gtk-theme` Breeze; GSettings dice Adwaita, pero GTK en Plasma lo lee del portal) con los colores que `kde-gtk-config`
  escribe en `~/.config/gtk-{3,4}.0/colors.css` desde el esquema; la preferencia oscura llega por el portal
  (`org.freedesktop.appearance color-scheme` = 1 en el oscuro) y el acento no (el portal de KDE no lo da y el libadwaita
  de Ubuntu pone el naranja de Yaru). El fallo de fondo: el esquema es la línea base de WhiteSur (4.4, ventana #363636) y
  Qt se ve con los neutros de los tokens que pone Kvantum (#1b1c1e), así que GTK y Qt no casaban. Se decide (complemento
  `gtk`): **(1) mejorar lo que genera KDE, no un tema derivado de WhiteSur-gtk**: libadwaita ignora los temas GTK y solo
  lee `gtk.css` del usuario, `kde-gtk-config` ya reescribe los colores en cada cambio de esquema y conserva lo demás de
  `gtk.css`, y un tema propio pedía `sassc`, recursos rasterizados y cambiar `gtk-theme-name` en cada variante; el precio
  es la forma de Breeze en los controles. **(2)** Una hoja por variante para GTK 3 (`lliphi-claro.css`,
  `lliphi-oscuro.css`, los 84 colores `*_breeze`) y una sola para GTK 4 con `@media (prefers-color-scheme: dark)`: los
  colores con nombre de libadwaita 1.9 (que los define igual, dentro de la misma consulta) y sus variables
  (`--accent-bg-color`, que Yaru fija con un valor directo), más los `*_breeze` de Breeze para GTK 4; se importan desde
  `gtk.css` detrás de `colors.css`. **(3)** Los derivados se escriben como `mix()` de GTK sobre dos tokens; la selección
  sin foco del claro es el azul entero (a media luz, el texto blanco no se leía en pantalla). **(4) Claro y oscuro**: GTK 4
  y libadwaita cambian solos; la línea de GTK 3 la cambia la vigilancia de `fondo-variante`, solo si ya importa una hoja
  de Lliphi, y también `color-scheme` de GSettings para lo que no lea el portal (no entra en `UNDO.sh`: `gsettings
  reset`). Comprobado en un KWin virtual aparte (`muestras/capturas/*-38-gtk*.png`): antes y después en el oscuro,
  libadwaita en las dos variantes con el acento de cada una.
- **4.36 (2026-11-01) Ningún azul fijo en el estilo de Plasma.** El autor vio, en Lliphi Oscuro, la barra del volumen
  en azul. WhiteSur-dark dibuja esa barra (`widgets/bar_meter_*`) con la clase `ColorScheme-Highlight` pero con
  `fill:#4285f4` escrito, así que la clase no servía; lo mismo en el botón pulsado (`#0860f2`), el calendario, el
  indicador de actividad, las casillas y otros 30 sitios del oscuro y algunos del claro. Se decide, en las dos variantes
  (`azules_al_acento` del estilo): en un elemento con clase de color, el azul del relleno o del trazo (en el estilo o
  como atributo) pasa a `currentColor`, y manda la clase, que sigue el acento del sistema; sin clase, pasa al acento
  de la variante por su luz, como en Kvantum (4.21). La hoja de estilo, los degradados con clase de Breeze y las
  marcas de referencia (`#0000ff` y lilas) no se tocan. `test_estilo_sin_azules_fijos` lo vigila. En la misma revisión
  se corrigió el superpuesto de la bandeja (4.35): si ya existe como enlace (la sesión de prueba enlaza los temas del
  usuario) se quita el enlace sin seguirlo, y si no se puede construir, aplicar el tema avisa y sigue. Probado en la
  sesión de prueba: el volumen en rojo en el oscuro y el brillo en azul en el claro
  (`muestras/capturas/oscuro-33-volumen-acento.png`).
- **4.35 (2026-11-01) Los iconos de la bandeja, del mismo tamaño.** El autor vio en la bandeja iconos de tamaños
  distintos (el «!» de apport, el de Remmina, más grandes que la campana o el volumen) y pidió uniformidad. Medido en la
  sesión de prueba: el claro y el oscuro no cambian el tamaño (mismos píxeles); la causa es Colloid, que dibuja sus
  iconos simbólicos llenando un lienzo de 16 y sus iconos de 22 con 3 px de margen, y la bandeja (22 px) escala el
  simbólico a 22. Se decide un superpuesto por tema de iconos, `<tema>-Lliphi` (`bandeja` en
  `modulos/iconos-cursores/ajustes.json`), que es el que nombra el tema global: hereda del Colloid de la variante y
  solo trae sus simbólicos de estado, aplicaciones y dispositivos (1180) en 22 px con el dibujo en 16 centrado
  (`con_margen`, sin redibujar nada), en carpetas de tamaño fijo 22. KIconLoader prueba primero la coincidencia exacta
  en toda la cadena de temas, así que el superpuesto solo se usa al pedir 22 px; en menús y botones (16 px) siguen los
  de Colloid. Se construye en la máquina desde el Colloid instalado (`instalar.py dependencias` y al aplicar), como el
  superpuesto rojo de Papirus (4.15). Medido en la sesión de prueba: sin él, Remmina y apport a 22 × 22 y lo demás a
  16; con él, todos a 16 (`muestras/capturas/claro-37-bandeja-a-medida.png`).
- **4.34 (2026-11-01) Las etiquetas emergentes del claro, legibles en Kvantum.** Tras 4.33 el autor seguía viendo la
  etiqueta «Minimize» del botón de la ventana sin leerse. No la dibuja el estilo de Plasma: KWin la muestra como una
  etiqueta de Qt, con el estilo de widgets (Kvantum), igual que toda etiqueta de las aplicaciones. El tema claro de
  Kvantum dibuja la etiqueta clara (`tooltip-normal` en `fondo.ventana`), pero `CLAVES` le ponía el texto
  `texto.tooltip` del esquema, casi blanco porque el esquema claro (como WhiteSur) declara etiquetas oscuras. Un ajuste
  por variante, `etiquetas`, pone en el claro `tooltip.base.color=fondo.ventana` y `tooltip.text.color=texto.normal`.
  Comprobado en la sesión de prueba con una etiqueta de Qt: antes `#fbfcfd` sobre `#ecedef`, ahora `#1d1f24`
  (`muestras/capturas/claro-36-etiqueta-kvantum.png`). KWin carga Kvantum al empezar la sesión: las etiquetas de los
  botones de la ventana cambian al volver a entrar.
- **4.33 (2026-11-01) Decoración clara visible y en azul, botón de menú propio y etiquetas claras legibles.** El autor
  señaló en la decoración clara tres fallos y un deseo: (1) cerrar seguía rojo, y en el claro debía ser azul; se
  revierte la excepción de 4.12 y los rojos de `close.svg` (`#eb3131`, `#a82323`, `#d46969`) pasan al acento
  (`acento.base`, `acento.texto`, `acento.suave`); (2) minimizar y maximizar tenían el centro casi blanco de Nothing
  sobre el título claro y no se veían; el centro (`#f4f0ed`) pasa a `texto.inactivo`; (3) la etiqueta «Minimize» no se
  leía: WhiteSur-alt (4.32) dibuja la etiqueta clara pero su `colors` la declara oscura (fondo 54,54,54, texto
  222,222,222); con `etiquetas_como_ventana` el estilo claro le da los colores de la ventana; y (4) en la vista previa
  de las decoraciones, el segundo botón de la izquierda repetía el icono de la aplicación, porque Nothing no trae
  `appmenu.svg` y Aurorae dibuja entonces el icono de la ventana. Lliphi lo dibuja en las dos variantes: tres líneas
  redondeadas de largo decreciente (un icono propio, distinto de las tres líneas iguales de Breeze) en el color del
  título, con un círculo tenue al pasar y al pulsar. El oscuro conserva cerrar en rojo y los círculos blancos de Nothing.
  Probado en la sesión de prueba (`muestras/capturas/claro-35-decoracion.png`).
- **4.32 (2026-11-01) Lliphi Claro con panel claro.** El autor vio en Preferencias del sistema → Estilo de Plasma que
  «Lliphi Claro» se veía oscuro y preguntó por qué, si su nombre dice claro. El estilo del claro partía de «WhiteSur»,
  que pinta panel, dock, menús emergentes y widgets en gris oscuro (`54,54,54`, texto blanco); se había conservado a
  propósito en la mejora 2 y en 4.16. El autor decide ahora que el claro sea claro: la base pasa a «WhiteSur-alt», la
  variante de WhiteSur con los mismos dibujos y el panel claro (blanco, texto gris oscuro). El fondo de paneles y dock
  toma el `fondo.ventana` del propio claro (antes, el del oscuro: 4.21) al 88 % y sin sombra; `panel()` sustituye el
  blanco al 45 % de WhiteSur-alt como sustituía el negro al 45 % de WhiteSur-dark. El generador retira los archivos que
  WhiteSur-alt no trae y añade los suyos. En la misma revisión se vio en la máquina del autor un estilo «Lliphi» que sigue
  al esquema de color: es el de la primera versión (instalado el 2026-10-18), que el instalador ya no genera; se retira
  a los respaldos. Probado en la sesión de prueba: panel, dock y lanzador claros, y la vista previa clara
  (`muestras/capturas/claro-33-panel-claro.png`, `claro-34-estilo-plasma.png`).
- **4.31 (2026-11-01) El deslizador y la barra de progreso inactivos, con el rojo entero.** El autor comparó en
  Preferencias del sistema → Estilo de las aplicaciones las vistas previas de `kvantum` y `kvantum-dark`: en la clara
  el deslizador y la barra de progreso salían en el azul entero; en la oscura, en un rojo apagado. La vista previa se
  dibuja como ventana inactiva, y WhiteSur oscuro pinta `slider-toggled-inactive*` y
  `progress-pattern-normal-inactive*` con `opacity:0.5`, mientras el claro los deja enteros. Un ajuste,
  `inactivo_pleno` (solo en el oscuro), quita esa opacidad de esas piezas; lo deshabilitado
  (`progress-pattern-disabled*`) sigue a media opacidad. Afecta también a toda ventana inactiva del oscuro, que ahora
  conserva el rojo en deslizadores y barras de progreso, como el claro conserva el azul. Probado en la sesión de prueba.
  En la misma revisión se descartó cambiar el marco de los botones de Kvantum para la vista previa de los esquemas de
  color: su banda opaca da el borde blanco a un botón de un esquema oscuro dibujado con el tema claro, pero sin ella los
  botones claros perdían las esquinas.
- **4.30 (2026-11-01) Las demás terminales, con la paleta de Konsole.** A pedido del autor, tras 4.29: Alacritty,
  Kitty y la terminal integrada de VS Code, Positron, VSCodium y Zed llevaban la paleta ANSI genérica de los tokens y
  se veían como la ventana que el autor descartó. `complementos/konsole/construir.py` expone `ansi(tokens, variante)`
  (el normal en `color0..7`, el intenso de Konsole en `color8..15`, el fondo y los textos) y las usan `terminales`
  (todo) y `editores` (los dieciséis ANSI; el fondo y el texto de la terminal integrada siguen siendo los del
  editor). La sintaxis de los editores, los colores con nombre de LibreOffice y los de Obsidian siguen en los tokens:
  allí el azul ha de ser azul. `test_ningun_hex_fuera_del_maestro` admite la paleta de Konsole.
- **4.29 (2026-11-01) Konsole sobre el esquema de Nothing.** El autor comparó una ventana con el esquema «Nothing»
  (el de su paquete de dotfiles, del tema Nothing de jomada, GPL-3.0-or-later) con otra en Lliphi Oscuro: la de Nothing
  combinaba con el tema y la nuestra no. La paleta ANSI genérica de los tokens (4.28 añadía solo el acento en el
  magenta) daba carpetas y claves de fastfetch azules, rojo salmón y lila sobre el rojo del tema. Nothing pinta de rojo
  el rojo (`Color1`) y también el azul (`Color4`), y lleva su azul en el negro (`Color0`). Se toma como base, como
  WhiteSur lo es del esquema de Plasma (4.4): `fuentes/base/Nothing-konsole/`. El oscuro es Nothing tal cual (su
  `#eb3131` es el rojo de que sale el acento, 4.25, y como texto se lee mejor que `#e22529`); solo cambian el nombre,
  la opacidad (0,8, la de Nothing, en `efectos.opacidad-konsole`) y `ColorRandomization`, que se apaga para que todas
  las pestañas tengan el mismo fondo. El claro es su espejo: fondo `neutro-1` y texto `neutro-7`; el acento azul en
  el `Color4`, el azul de Nothing en el `Color1` y su rojo en el `Color0`, de modo que lo que en el oscuro es rojo en
  el claro es azul; los demás conservan el matiz y el croma de Nothing con la luz más alta que da ≥ 4,5:1 sobre el
  fondo (en OKLCH, con la biblioteca estándar), el tenue 0,06 más claro y el intenso 0,06 más oscuro. Coste aceptado:
  en el claro, lo que un programa pinte de «rojo» (un error, una línea borrada) sale azul, como en el oscuro de
  Nothing sale rojo lo «azul». Los esquemas de Konsole pasan a GPL-3.0-or-later. Probado en la sesión de prueba con
  `lsd` y `fastfetch` en las dos variantes.
- **4.28 (2026-11-01) Konsole sigue a la variante y lleva su acento** (el acento en el magenta, superado por 4.29;
  lo de seguir a la variante sigue en pie). El autor vio Konsole con colores que no
  combinaban con el tema: debía ir en rojo con Lliphi Oscuro y en azul con Lliphi Claro. Dos causas. Konsole no tiene un
  esquema «del sistema»: el perfil queda con el esquema que se instaló, así que con el tema claro seguía en Lliphi
  Oscuro. Y los dieciséis ANSI no llevan el acento: el prompt pinta con azul y magenta genéricos. Se resuelve así: en el
  esquema de Konsole, el magenta (`Color5`) toma el acento de la variante, el primero que da ≥ 4,5:1 sobre el fondo
  (`acento` en el claro, `#315bef`; `acento-suave` en el oscuro, `#f36259`; `acento` del oscuro da 4,1:1), con
  `acento-texto` como intenso. El magenta de los tokens no cambia, porque LibreOffice, Obsidian y los editores lo usan
  con su nombre. Y la vigilancia de `fondo-variante` cambia también Konsole: si el perfil por defecto usa un esquema de
  Lliphi, le pone el de la variante y lo cambia en las sesiones abiertas escribiendo en su terminal `ESC ] 50 ;
  ColorScheme=… BEL`, la secuencia de `konsoleprofile`. Un perfil con otro esquema no se toca. Al instalar, la vigilancia
  se reinicia para que corra el programa nuevo. Probado en la sesión de prueba: Konsole abierto en oscuro, el tema
  global al claro y el esquema de vuelta al oscuro; la ventana abierta cambia sola.
- **4.27 (2026-11-01) El fondo del escritorio por omisión: «Lliphi Relámpago · @achalmaedison».** Decisión del
  autor: los fondos predeterminados son los de Relámpago firmados, azul en el claro y rojo en el oscuro. La marca gana
  `fondo_escritorio` (`org.lliphi.relampago.firmado`), que usan el instalador, la disposición del tema global y el
  `plasmarc` del estilo de Plasma (`defaultFileSuffix=.jpg`); `id_fondo` (Horizonte) queda como la imagen del bloqueo
  y del inicio de sesión, donde el reloj blanco pide la oscura. La disposición escribe ahora la imagen de su variante
  y no el paquete: en la sesión de prueba, con «usar la disposición del tema», el guion se ejecutaba después del
  instalador, ponía el paquete y Plasma mostraba en el claro la imagen oscura (4.16). Probado en la sesión de prueba:
  claro con disposición, al oscuro y de vuelta al claro.
- **4.26 (2026-11-01) El fondo sigue a la variante.** El autor cambió el tema global entre Lliphi Claro y Lliphi
  Oscuro desde Preferencias del sistema y el fondo no cambió. Dos causas, comprobadas en la sesión de prueba:
  `plasma-apply-lookandfeel` no toca el fondo, y con un paquete de imagen clara y oscura Plasma elige por los colores
  del estilo de Plasma, que en el claro declaran el panel oscuro (4.16), así que mostraría la oscura. Se resuelve con
  un complemento, `fondo-variante`: un programa de biblioteca estándar que escucha el aviso de KDE de cambio de colores
  (`org.kde.KGlobalSettings.notifyChange`, con `dbus-monitor`), lee el esquema (`[General] ColorScheme`) y, si es de
  Lliphi y el fondo de un escritorio también (`org.lliphi.*`), pone la imagen de la variante del **mismo** fondo
  (`images/` o `images_dark/`, el mismo tamaño si lo hay, si no el mayor), por el scripting de Plasma. Arranca con la
  sesión (`autostart`) y con `instalar.py --aplicar-tema`. Lo que no es de Lliphi no se toca: quien elige otro fondo o
  otro esquema lo conserva. Se descartó cambiar el fondo dentro del tema global (`Plasma/LookAndFeel` no sabe del
  fondo que el usuario eligió y lo pisaría siempre con Horizonte) y un servicio de systemd (la sesión de prueba
  arranca sin systemd de usuario, 8.3). Probado en la sesión de prueba con Forma firmada: tema global al claro,
  esquema solo al oscuro y tema global al oscuro, y el fondo siguió las tres veces.
- **4.25 (2026-11-01) El rojo de Nothing, la tira de la paleta por luz y la firma en los fondos.** (1) El autor vio
  más bonito el rojo de Nothing (`#eb3131`, el mismo del botón de cerrar de la decoración) que el de Lliphi (`#c93436`).
  Con texto blanco encima, `#eb3131` da 4,08:1 y la selección exige 4,5:1; se toma su matiz y su croma (OKLCH 26,76° y
  0,221) con la luz justa para cumplir: `#e22529` (L 0,588; 4,53:1; ΔE2000 2,8 frente al de Nothing, frente a 7,3 el
  anterior). El suave y el de texto del oscuro pasan al mismo matiz (`#f36259`, `#ff968b`); todos los pares cumplen y
  el acento destaca más sobre la ventana (3,70:1 frente a 3,27). (2) En «Lliphi Relámpago» la tira de los tres
  acentos iba por su papel (texto, base, suave) y en el oscuro, donde el acento de texto es el más claro, se veía
  desordenada; ahora va por su luz en las dos variantes. La paleta no estaba desordenada: el acento de texto es el más
  claro en el oscuro y el más oscuro en el claro porque tiene que leerse sobre su fondo. (3) A pedido del autor, los
  fondos Forma y Relámpago tienen además una versión con su usuario, `@achalmaedison` (`marca.json`, `firma`), pequeño
  y tenue, en la misma matriz de puntos: en Forma bajo la píldora, alineado a su final, como la firma de un cuadro; en
  Relámpago bajo la tira de la paleta, alineado con el nombre. Las versiones sin firma se conservan.
- **4.24 (2026-11-01) Un tercer fondo: «Lliphi Relámpago», con el acento de cada variante.** El autor pidió fondos con
  elementos que representen al proyecto, cada variante con su color («para claro no es rojo»), sin quitar los que hay.
  Se añade un tercer paquete (`org.lliphi.relampago`): el relámpago (*lliphi*, en quechua; `nombre.md`) en semitono de
  puntos, más grandes hacia el eje de cada trazo, con un halo; el nombre en una matriz de puntos de 5 × 7 con el punto
  de la marca («Lliphi.», como en la pantalla de carga); y la rampa de neutros y acentos de la variante, que son los
  tokens de los que sale todo. El claro usa el azul de WhiteSur y el oscuro el rojo de Nothing (4.12). Las letras se
  dibujan como puntos en el código para no depender de una tipografía instalada (la CI construye lo mismo). Horizonte y
  Forma no cambian.
- **4.23 (2026-11-01) Un segundo fondo: «Lliphi Forma».** El autor pidió dos fondos, claro y oscuro, como «Nothing2» y
  «Nothing3» de jomada (formas sobre gris claro y sobre negro) o mejores. No se copian: `complementos/fondos` genera una
  composición propia desde los tokens, en un segundo paquete (`org.lliphi.forma`): dos cuadrados de vidrio esmerilado
  (una rejilla de grises al azar, ampliada y desenfocada, con grano), un semicírculo en el rojo de Lliphi (el acento del
  oscuro, en las dos variantes, como el botón de cerrar), una píldora con degradado vertical que se deshace hacia abajo
  y, como aporte propio, una matriz de puntos tenue en su mitad de arriba (el guiño a la tipografía de puntos), con
  sombras suaves y grano fino. Se guarda en JPEG (6 MB el paquete; en PNG el grano daba 14 MB). «Lliphi Horizonte»
  sigue siendo el fondo del tema global, del bloqueo y de SDDM.
- **4.22 (2026-11-01) Iconos: Colloid Grey.** Decisión del autor: los iconos de Lliphi pasan a ser Colloid Grey
  (vinceliuice/Colloid-icon-theme, GPL-3.0), `Colloid-Grey-Light` en el claro (simbólicos oscuros, `#363636`) y
  `Colloid-Grey-Dark` en el oscuro (simbólicos claros, `#dedede`). Papirus y su superpuesto de carpetas rojas (4.7,
  4.15) quedan como reserva, que `aplicar.py` usa si Colloid no está instalado. Colloid no publica temas construidos:
  se instala con el guion de su autor (`install.sh -t grey`); `instalar.py dependencias` lo comprueba y dice cómo, pero
  no ejecuta código descargado. Colloid dibuja todos los `start-here` como el logotipo de Apple, y Lliphi quita lo que
  imita a Apple (3.11): el lanzador de la barra superior lleva en la disposición su propio icono, `plasma-symbolic` (el
  logotipo de Plasma del mismo Colloid, en el gris del tema).
- **4.21 (2026-11-01) Ningún azul de WhiteSur en el oscuro, y las mejoras también en el claro.** Con Lliphi Oscuro,
  al pulsar un botón de Preferencias del sistema salía azul: los botones de Kvantum (`button-pressed`, `-default`,
  `-toggled`) y otras piezas (pestañas, grupos, un icono) conservaban catorce azules de WhiteSur que el mapa de colores
  no traducía. Se decide (`azules_al_acento` en `complementos/kvantum/ajustes.json`) que todo azul de la base que no sea
  ya un color de Lliphi pase al acento de la variante por su luz (`acento.base` los oscuros, `acento.suave` los claros),
  en las dos variantes. Y, a pedido del autor («todas las mejoras también en el tema claro»): la barra de herramientas
  del claro en su `fondo.ventana`, como el título (antes `#fbfcfd` contra `#ecedef`), y el fondo del dock del claro sin
  sombra y al 88 %, con el gris de ventana del oscuro porque el claro conserva el panel oscuro de 4.16. Los mosaicos de
  tareas, el paginador, la disposición y el tema único de Kvantum ya eran de las dos variantes. Comprobado en sesión
  de prueba (`muestras/capturas/claro-23-dock-cabecera.png`).
- **4.20 (2026-11-01) El menú abierto de la barra de menús, en el acento.** El autor vio que en el claro el elemento
  abierto de la barra de menús («Settings» desplegado) y el elegido dentro del menú son del mismo azul, y en el oscuro
  no: el elegido es el acento (`#c93436`, la selección de la paleta) y el de la barra salía en el rojo claro de pasar el
  ratón (`#ef6661`), porque WhiteSur oscuro pinta `menubaritem-pressed`/`-toggled` con su tono claro (`#5294e2`). Se
  decide, en `complementos/kvantum/ajustes.json` (`menu_abierto`), pintar esas piezas en el oscuro con `acento.base`.
- **4.19 (2026-11-01) Un solo tema de Kvantum con sus dos variantes.** El autor aplicó Lliphi Claro desde Preferencias
  del sistema y las ventanas quedaron mezcladas: esquema claro (texto oscuro) sobre el Kvantum oscuro. El tema global
  solo puede declarar el estilo de las aplicaciones (`kvantum` o `kvantum-dark`); qué tema de Kvantum se usa lo dice
  `~/.config/Kvantum/kvantum.kvconfig`, que solo escribía el instalador de Lliphi. Kvantum resuelve esto por sí mismo:
  con `kvantum-dark` busca la variante `<tema>Dark` del tema elegido (así lo hace WhiteSur). Se decide que el
  complemento entregue un solo tema, `Lliphi`, con `Lliphi.*` (claro) y `LliphiDark.*` (oscuro) en la misma carpeta, y
  que el instalador fije `theme=Lliphi` una vez: desde entonces cambiar de variante con el tema global cambia también
  Kvantum. El contenido de cada variante no cambia (los archivos son idénticos a los de `LliphiClaro` y `LliphiOscuro`).
- **4.18 (2026-11-01) Mejora 12: título y barra de herramientas en una sola banda.** El autor comparó una ventana de
  Dolphin con otra que le gusta más, donde el título de la decoración y la barra de herramientas son del mismo color, y
  pidió lo mismo o mejor. En la de Lliphi el título es el `#1b1b1d` de Nothing y la barra salía `#363636`: Kvantum la
  pinta con su propio elemento (`toolbar-normal`) en el gris fijo de WhiteSur, que no se recoloreaba, y además la ventana
  era translúcida (WhiteSur, 75 % con desenfoque), así que todo lo que no es la decoración salía más claro y teñido por
  el fondo. Se decide, en `complementos/kvantum/ajustes.json`, solo para el oscuro: la barra de herramientas, activa e
  inactiva, en `fondo.ventana` (el mismo tono que el título, a una unidad) y opaca; con `merge_menubar_with_toolbar`
  arrastra la de menús. La ventana sigue translúcida: el autor pidió conservar la transparencia de la vista de Dolphin
  y de la terminal integrada (una primera versión con ventanas sólidas la perdía). La línea oscura bajo la barra se
  queda como divisoria con el contenido. El claro no cambia.
  Comparación en `muestras/comparacion-linea-base-cabecera.png` (sesión de prueba).
- **4.17 (2026-11-01) Mejora 11: el dock de Lliphi.** El autor comparó el dock con otro que le gusta más (oscuro y
  sólido, sin recuadros bajo cada aplicación, y un paginador de números con una línea encima) y pidió que el de Lliphi se
  vea así o mejor. Causas en el de 0.3.0: el fondo de paneles de WhiteSur es negro al 45 %, que con el desenfoque se ve
  gris lavado; los mosaicos de tareas de WhiteSur pintan un recuadro gris bajo cada aplicación abierta con un punto; y el
  paginador traía el azul fijo de WhiteSur. Se decide, en `modulos/estilo/ajustes.json`: (1) el fondo de paneles del
  oscuro al 88 % y en el gris de la ventana (`fondo.ventana`), sin la sombra de WhiteSur, que en las puntas del dock
  flotante se veía como dos manchas oscuras; el claro, como estaba (su panel oscuro, aprobado en 4.16); (2)
  `widgets/tasks.svg` lo dibuja Lliphi: un fondito claro tras cada aplicación abierta (el autor pidió conservarlo), más
  marcado al pasar, la activa con un mosaico teñido del acento al 30 % y una barra en el rojo claro de foco, y avisos y
  progreso en sus colores; (3) `widgets/pager.svg` también: un trazo corto sobre cada número, separado de él, en el
  acento el escritorio activo. Todo
  con las clases `ColorScheme-*` de Plasma, así que sigue el acento del sistema. En la disposición, el dock gana el
  paginador (números, sin siluetas) tras un separador. Límites: el separador de Plasma 6 solo dibuja su línea en modo
  edición (fuera de él da el espacio), y el paginador se oculta con un solo escritorio, y se configura con «solo la pantalla actual»: si no, toma la proporción de todo el escritorio y con dos monitores cada escritorio sale muy ancho. Comparación en
  `muestras/comparacion-linea-base-dock.png` (sesión de prueba, cuatro escritorios).
- **4.16 (2026-10-19) Mejora 10: el claro, validado en pantalla y corregido** (el panel oscuro, superado por 4.32). En una sesión de Plasma virtual aparte se
  encontraron y corrigieron dos fallos más: (1) el fondo salía oscuro en el claro, porque Plasma elige la imagen clara u oscura
  del paquete por los colores del estilo de Plasma, y el de WhiteSur claro tiene el panel oscuro; el instalador fija ahora la
  imagen clara por ruta; (2) el bloqueo de pantalla escribe siempre en blanco y sobre el fondo claro el reloj no se leía; el
  instalador pone en las dos variantes la imagen oscura de Lliphi en el bloqueo, como el inicio de sesión. Se conserva a
  propósito el panel oscuro de WhiteSur claro, aprobado en la mejora 2. Comparación en
  `muestras/comparacion-linea-base-claro-validado.png`; método y trampas en `docs/validacion.md` §8. Aprobada por el autor el 2026-10-19.

## 5. Más allá del escritorio

- **5.1 (2026-11-01) Tema de Obsidian: un complemento de Lliphi que se publica en su repositorio propio.** El autor
  pidió un tema de Obsidian desde los tokens de Lliphi que reemplace a Minimal en su vault y cierre su familia de
  complementos de Obsidian (cada uno en su repositorio público). Se decide: (1) **Lliphi genera, otro repositorio
  publica**: `complementos/obsidian/` escribe `generado/obsidian/theme.css` con las pruebas de siempre (colores del
  maestro, sin deriva), y `achalmed/obsidian-lliphi` lo trae con `traer.sh` (de la rama main o de una copia local),
  lleva el `manifest.json` y su versión, que no es la de Lliphi, y no depende de este repositorio para instalarse; el
  instalador de Lliphi no toca Obsidian porque un vault no es una carpeta XDG. (2) **Solo variables de Obsidian 1.x**
  (las de su `app.css` 1.14), ni selectores de la interfaz ni las de Minimal o Style Settings: así el tema sobrevive a
  las versiones de la aplicación y a los complementos que leen la paleta. (3) **Traducción**: la escala
  `--color-base-*` sigue la lógica de Plasma (la nota sobre `fondo.vista`, las barras laterales sobre `fondo.ventana`,
  bordes, y los tres textos); el acento es el de cada variante, con los enlaces en `enlace`; los ocho colores con nombre
  salen de los ANSI de la terminal (rosa = magenta brillante) y el naranja, que Lliphi no tiene, es `estado.advertencia`;
  en el claro el amarillo y el naranja quedan cerca, el precio de no inventar colores fuera del maestro. El fondo de los
  botones de peligro del oscuro es el acento (el rojo de Nothing), porque el `estado.error` del oscuro es un rojo claro
  para texto y no admite texto blanco. (4) **Lo que el autor tenía en Minimal y se conserva**: encabezados de color
  (h1 rojo … h6 morado), enlaces sin subrayado; el ancho de línea legible queda en 40rem, como lo tenía. (5) **Fragmentos
  del vault**: `callouts.css` (colores de las anotaciones de Zotero en las notas de lectura) pasa al tema y se amplía a
  los ocho colores de Zotero en cualquier nota, porque es color y el tema es quien decide el color; además en Obsidian 1.14
  `--callout-color` es un color y el fragmento, que lo daba como terna RGB, dejaba las llamadas sin color.
  `hidecitations.css` (ocultar las citas de Pandoc en la lectura) **no** es de tema sino de una función concreta y se
  queda como fragmento. `my font`, activo sin archivo, se retira de la lista. Comprobado en el vault del autor con
  Obsidian 1.14.5 (`docs/compatibilidad.md`).
- **5.2 (2026-11-01) LibreOffice: paletas como las de Dracula, dentro de la misma extensión.** El autor pidió que Lliphi
  tenga temas para otros programas al estilo de [dracula/dracula-theme](https://github.com/dracula/dracula-theme), y
  empezar por LibreOffice con un tema claro y uno oscuro. El de Dracula para LibreOffice son dos piezas: los colores de la
  aplicación (un `.xcu` que se pega en `registrymodifications.xcu`) y una paleta `.soc` que se copia a la carpeta del
  usuario. Lliphi ya tenía la primera, mejor empaquetada (extensión `.oxt` y fragmentos); se decide: (1) añadir la
  **paleta**, una por variante (`lliphi-claro.soc`, `lliphi-oscuro.soc`), con los neutros, el acento, los cuatro estados y
  los dieciséis ANSI, sin repetir colores (32 en el oscuro); los nombres en castellano, porque LibreOffice los muestra al
  pasar el ratón. (2) **meterlas en la extensión**, en `palette/`, con un `paletas.xcu` que añade `%origin%/palette` a
  `Paths/Palette/InternalPaths`: así una sola instalación trae esquemas y paletas, y desinstalarla las quita; sueltas
  siguen sirviendo para copiarlas a `~/.config/libreoffice/4/user/config/`. (3) el sombreado de campos e índices pasa a
  `borde.separador` en las dos variantes: en el oscuro el anterior no se veía (comprobado en pantalla), y en el claro da
  el gris que LibreOffice trae por omisión. La interfaz sigue al escritorio; el «tema de LibreOffice» (UI propia) queda
  sin activar, como estaba. Validado con un perfil desechable en una sesión de KWin virtual (`validacion.md` §10).
- **5.12 (2026-11-01) Sitios web: estilos de usuario que solo redefinen las variables de cada sitio.** El autor, que
  navega sobre todo en Zen y también en Chrome, pidió Lliphi en DuckDuckGo y en GitHub. Se decide: (1) **Estilos de
  usuario en UserCSS**, uno por sitio (`complementos/sitios-web/`, `generado/sitios-web/<sitio>.user.css`): la cabecera
  `==UserStyle==` la entiende Stylus en Zen y en Chrome, y el cuerpo va en `@-moz-document domain(...)`, que Zen también
  lee sin extensión desde `userContent.css`; no se hace una extensión propia ni se toca el perfil del autor (Stylus no
  estaba instalado en ninguno de los dos navegadores: el `INSTALL.md` lo explica). El estilo no lleva la URL del
  repositorio ni el usuario del autor. (2) **Solo variables del sitio, con `!important`**: así gana a las del sitio sin
  depender de la especificidad de sus selectores y resiste sus cambios de maquetación. GitHub las tiene todas en Primer
  (`--bgColor-*`, `--fgColor-*`, `--borderColor-*`, `--button-*`, `--control-*`, `--diffBlob-*`,
  `--prettylights-syntax-*`, `--codeMirror-syntax-*`, `--ansi-*`, `--contribution-*`, `--fontStack-*`); se redefinen
  solo las funcionales, porque las demás son `var(...)` de estas, y se dejan las etiquetas que cada repositorio colorea.
  DuckDuckGo tiene tres generaciones de su sistema de diseño a la vez (`--theme-col-*`, `--sds-color-*`, `--ds-*`, las
  dos últimas escritas en línea en `<html>` por su JavaScript; un `!important` de una hoja gana a una declaración en
  línea sin él), y su tema oscuro pinta el fondo de la página y el de la cabecera con un gris fijo: dos reglas sin color
  propio los devuelven a sus variables; es la única concesión a los selectores. (3) **La variante según el modo**:
  DuckDuckGo por `prefers-color-scheme` (como su tema «Predeterminado»); GitHub por su propio `data-color-mode`
  (`light`, `dark`, o `auto` más `prefers-color-scheme`), para que gane lo que el usuario eligió en GitHub; comprobado
  cambiando el atributo con el sistema en claro. (4) **Identidad**: los neutros de los semánticos; el acento solo en
  enlaces, foco, selección, la pestaña elegida y el botón principal (el verde de GitHub, el amarillo de la marca de
  DuckDuckGo); los fondos tenues del «acento» de Primer (avisos informativos, cabecera de cada trozo de un diff) en el
  azul de `estado.info`, porque en el oscuro el acento es rojo y se leía como un borrado (se vio en la primera captura);
  los rellenos con texto blanco (insignias, «Open», «Closed», «Merged», contadores) con un fondo que lo admite: en el
  oscuro los estados de los semánticos son claros, así que toman los del claro y el peligro es el rojo de Nothing, como
  en Obsidian (5.1); el código con `sintaxis()` de `editores`, los registros de Actions con los ANSI, los diffs y el
  gráfico de contribuciones con los estados (éxito y error, con alfa), nunca un verde o un rojo ajeno; Inter y JetBrains
  Mono. Ningún color se escribe a mano: todo sale de los tokens, a lo sumo con alfa (`#rrggbbaa`). (5) **DuckDuckGo sin
  extensión**: sus ajustes de apariencia (`kae`, `k7`, `kj`, `k8`, `k9`, `kaa`, `kx`, `k21`, `kt`, `ka`, colores en hex
  sin `#`) se generan por variante, porque fijan colores y no siguen al sistema: la página de inicio, la de ajustes ya
  rellena (la de `/settings?…` sin `#appearance`, que DuckDuckGo pegaba al último parámetro) para guardarlos, la
  plantilla de buscador y unos marcadores importables. (6) **Un sitio, un archivo**: `duckduckgo.py` y `github.py`
  comparten la interfaz que describe `construir.py` (`AMBITOS`, `variables`, `CONTRASTE`…), y las pruebas recorren
  `SITIOS`: añadir un sitio no pide una prueba nueva para lo común (CSS bien anidado, colores del maestro, cada par de
  `CONTRASTE` ≥ 4,5:1 con los fondos translúcidos mezclados sobre el de la página). Comprobado en el navegador
  integrado con el CSS inyectado, en las dos variantes (`muestras/capturas/*-3[89]-sitios-*.png`, `*-40-sitios-*.png`).
  Queda fuera lo que no va por variables: la cabecera de GitHub sin sesión (Primer Brand, negra) y el enlace «Search
  Assist» de DuckDuckGo en el claro, que conserva su azul.
- **5.3 (2026-11-01) Navegadores: Zen con un `userChrome.css` que sigue al sistema y Chrome con dos temas.** El autor
  pidió Lliphi en Zen Browser, el que usa, y en Chrome. Complemento `navegadores` con las dos piezas, generadas de los
  semánticos de cada variante. **Zen** (1.24b, Flatpak `app.zen_browser.zen`, Firefox 159): pinta la interfaz con
  variables `--zen-*` que en parte calcula del degradado del espacio de trabajo y escribe en línea en `:root`,
  `#zen-browser-background` y `#zen-toolbar-background`, y otras que redefinen elementos como `zen-workspace` (la pestaña
  activa). Se descartan (1) un tema WebExtension con `theme` y `dark_theme`: Zen ignora casi todos sus colores al pintar
  con el degradado; y (2) un «Zen Mod»: Zen regenera `zen-themes.css` desde su tienda y uno local no sobrevive. Se elige
  un **`userChrome.css`**: es una hoja de usuario y sus `!important` ganan a los de Zen y a los estilos en línea; define
  `--lliphi-*` por variante (`@media (prefers-color-scheme: dark)` elige la oscura y fija `color-scheme`, para que lo que
  Zen pinta con `light-dark()` vaya con ella) y pone sobre ellas unas cincuenta variables de Zen y de Firefox en la raíz
  y en los elementos que las redefinen (buscados en las hojas de Zen 1.24 y Firefox 159). El degradado del espacio de
  trabajo queda en el gris de la ventana: la identidad sobria manda. Las ventanas privadas conservan el aspecto de Zen
  para que se distingan. La pestaña activa del oscuro es `fondo.boton`, no la vista, que es más oscura que la barra
  lateral y la hundiría. Lo acompaña un **`user.js`**: `toolkit.legacyUserProfileCustomizations.stylesheets` (Zen no
  carga `userChrome.css` sin ella) y `zen.view.window.scheme = 2`: el perfil del autor tenía el oscuro fijo (0), y sin
  esto Zen no cambiaría con el sistema. Desinstalar retira ambos archivos, pero el valor queda en `prefs.js`
  (`INSTALL.md` dice cómo volver). Comprobado en la sesión de prueba: con `plasma-apply-colorscheme` Zen pasa de una
  variante a otra en vivo, y los colores medidos en pantalla son los de los tokens (barra lateral, pestaña activa y
  barra de direcciones, en las dos). **Chrome** (156): un tema es un `manifest.json` con `theme.colors` y no tiene
  variante oscura; con un tema puesto, Chrome deja de seguir al sistema. Se descarta un tema neutro (los colores de un
  tema son fijos: o es claro o es oscuro) y el color de Chrome por semilla (un solo color por los dos modos, y lo
  transforma Material 3); se hacen **dos temas sin empaquetar**, Lliphi Claro y Lliphi Oscuro: franja y pestañas de
  fondo en `fondo.ventana`, barra y pestaña activa en `fondo.vista` (la pestaña se funde con la página), textos de los
  semánticos y enlaces de la página nueva en `enlace`. Chrome reinterpreta un poco el oscuro (franja `#212223` en vez de
  `#1b1c1e`) y su anillo de foco toma su propio acento: el formato no deja fijarlo. Chrome tampoco deja instalar un tema
  desde fuera (desde la 137 ya no acepta `--load-extension`): el instalador deja los temas en
  `$XDG_DATA_HOME/lliphi/chrome/` y se cargan con «Cargar descomprimida»; en la sesión de prueba se cargaron por el
  protocolo de DevTools (`Extensions.loadUnpacked`). Nueva base de instalación condicional `zen` (el perfil de
  `installs.ini`, el que abre Zen, también el del Flatpak; o `$ZEN_PERFIL`); un `userChrome.css` o `user.js` ajeno es
  conflicto y no se pisa. Pruebas `test_navegadores_zen`, `test_navegadores_chrome` y `test_instalar_navegadores`.
- **5.4 (2026-11-01) Positron entero en Lliphi, en la misma extensión.** El autor pidió los temas de Positron, Kate,
  TeXstudio y Vim/Neovim. Positron ya leía la extensión de VS Code (`complementos/editores`), pero registra 150 claves
  de color propias (`positron*`) y 37 de ellas tienen por omisión un color fijo suyo: los azules de la selección de la
  cuadrícula de datos, los grises de los separadores y de los campos de las barras de acciones y de los diálogos, los
  iconos de estado del intérprete, la bienvenida, los gráficos del resumen de columnas y el fondo de las trazas de la
  consola. Inventario sacado de los `registerColor("positron…")` de `workbench.desktop.main.js` de Positron 2026.06.
  Se decide: (1) **todas ellas desde los tokens**, en `colores_positron()`, dentro de la misma extensión (Positron la
  instala de `~/.positron/extensions/`; VS Code ignora las claves que no conoce): selección y cursor de la cuadrícula
  en el acento, estados en los colores de estado, la distribución de las columnas en el azul de `charts.blue` y los
  nulos en su rojo; (2) **la consola de Positron es la terminal integrada**: su fondo y sus dieciséis ANSI son los de
  la terminal (Konsole, 4.30), no el fondo del panel, porque es salida de terminal y así los colores 1–7 dan ≥ 4,5:1;
  (3) se definen además las claves estándar de las que Positron deriva otras y que el tema dejaba vacías
  (`tree.tableColumnsBorder`, los fondos del desplazamiento fijo). Las demás claves de Positron derivan de claves
  estándar que el tema ya define. `test_positron_entero` comprueba que no falte ninguna de las 37.
- **5.5 (2026-11-01) Kate: un tema de KSyntaxHighlighting con el fondo de la paleta que ven las aplicaciones.** La
  interfaz de Kate ya seguía el esquema de color; faltaba el editor. Kate, con «Seleccionar automáticamente el tema de
  color» (activo por omisión, y activo en la configuración del autor), elige el tema cuyo `BackgroundColor` es el
  `Base` de la paleta de la aplicación y, entre ellos, el de `TextSelection` igual a su `Highlight`
  (`Repository::themeForPalette` de KSyntaxHighlighting 6.24, leído en su código); si ninguno coincide, Breeze. Se
  decide: (1) **complemento `kate`** con `lliphi-claro.theme` y `lliphi-oscuro.theme` en
  `$XDG_DATA_HOME/org.kde.syntax-highlighting/themes/`, con la tabla de sintaxis de los editores; (2) **el fondo y la
  selección son los de la paleta de Kvantum** (`kvantum.paleta_qt`: `base.color` = `fondo.vista`, `highlight.color` =
  `seleccion.fondo`), que es la que ven las aplicaciones con el estilo Kvantum del tema global, y no la del esquema
  `.colors` (`#242424` en el oscuro, línea base de WhiteSur): se probó en la sesión de prueba, con un tema anclado al
  esquema Kate cayó en Breeze Dark y con el anclado a Kvantum eligió Lliphi Oscuro; al pasar a Lliphi Claro con Kate
  abierto, cambió solo a Lliphi Claro, sin escribir en `katerc`. Con el estilo Breeze en lugar de Kvantum la paleta es
  la del esquema y Kate cae en Breeze: se elige el tema a mano (`INSTALL.md`); (3) como la selección es el acento opaco,
  el texto seleccionado es `seleccion.texto` (4,5:1 en el oscuro, el mismo par de toda la selección de Plasma); (4) los
  resaltes (línea actual, búsqueda, plegado, plantillas) son colores del maestro con el alfa de los editores compuesto
  sobre el fondo (`editores.sobre`), porque el formato no mezcla alfa. Sin `aplicar.py`: no hace falta tocar la
  configuración del usuario.
- **5.6 (2026-11-01) TeXstudio: las dos secciones de formatos, en un perfil y, si se pide, en `texstudio.ini`.**
  TeXstudio 4.9 guarda los formatos de resaltado en `[formats]` y en `[formatsDark]` de `texstudio.ini` y usa una u
  otra según su modo oscuro, que deduce de la paleta (texto casi blanco) y vuelve a deducir cuando la paleta cambia
  (`Texstudio::paletteChanged`); el fondo del editor es el `Base` de la paleta (con Kvantum, `fondo.vista`). Se decide: (1) **complemento
  `texstudio`** que llena las dos secciones (el claro en `[formats]`, el oscuro en `[formatsDark]`): TeXstudio sigue
  solo a la variante; (2) se escriben **los 88 formatos** de `defaultFormats.qxf` salvo los marcadores, con sus campos
  completos y la prioridad de los que la declaran, porque un formato leído sustituye entero al de omisión; (3) la
  sintaxis se lee como LaTeX Workshop en VS Code: órdenes en azul (`funcion`), `\begin`/`\end` en rojo (`palabra-clave`),
  entornos en cian, lo matemático en amarillo y cian, títulos en rojo y negrita; referencias, citas y paquetes
  presentes en magenta y los que faltan en el color de error con onda; las llaves por nivel en el orden de
  `editorBracketHighlight` de VS Code; los resaltes, compuestos sobre el `base.color` de Kvantum (TeXstudio guarda los
  colores sin alfa); (4) **dos maneras de aplicarlo, sin perder lo demás**: el perfil `lliphi.txsprofile` (Opciones →
  Cargar perfil…, que solo fusiona sus claves) y el `aplicar.py` del instalador, que sustituye solo esas dos secciones
  de `texstudio.ini`, respalda el archivo, escribe el real si es un enlace de dotfiles y no hace nada con TeXstudio
  abierto (lo reescribiría al cerrarse). En la sesión de prueba, TeXstudio abierto pasó de `[formatsDark]` a
  `[formats]` al cambiar a Lliphi Claro, sin reiniciarse.
- **5.7 (2026-11-01) Vim y Neovim: un solo `colors/lliphi.vim` con las dos variantes.** Vim 9.1 y Neovim 0.11 están
  instalados; el autor no tiene configuración de Neovim y su `~/.vimrc` solo fija el ratón. Se decide: (1)
  **complemento `vim`** con un esquema en Vim script que leen los dos (no uno en Lua y otro en Vim script, que se
  desincronizarían): Lliphi Claro con `background=light` y Lliphi Oscuro con `dark`; los grupos de Tree-sitter, de los
  tokens semánticos del LSP (el reparto de `semanticTokenColors` de VS Code) y de diagnósticos, bajo `has('nvim')`,
  porque Vim no admite `@` en un nombre de grupo; (2) **el fondo y el texto son los de Konsole**, no `fondo.vista`:
  Vim corre dentro de la terminal y así se funde con ella (la tabla de sintaxis da ≥ 5:1 sobre ese fondo); la
  terminal integrada lleva los dieciséis ANSI de Konsole; `g:lliphi_transparente` deja el fondo a la terminal; (3) sin
  colores verdaderos, cada grupo toma el más cercano de los dieciséis colores de Konsole; (4) se instala en
  `$XDG_DATA_HOME/nvim/site/colors/`, que Neovim lee solo; Vim, con `~/.vimrc`, no lee carpetas XDG, así que
  `INSTALL.md` pide un enlace en `~/.vim/colors/` (el instalador no escribe fuera de las carpetas XDG). La configuración
  del autor (`~/.vimrc`) no se toca: se le propone `set termguicolors` y `colorscheme lliphi`.
- **5.8 (2026-11-01) Seguir a la variante: no hace falta ampliar `fondo-variante` para estos editores.** Se evaluó
  añadirlos a la vigilancia de 4.26/4.28 y no compensa: **Kate** cambia solo (5.5), **TeXstudio** cambia solo (5.6),
  **Vim y Neovim** toman `background` de la terminal al arrancar (Konsole responde a OSC 11) y un cambio de
  `background` recarga el esquema; en una sesión que ya estaba abierta basta `:set background=…`, y forzarla desde
  fuera exigiría un servidor de Neovim o una orden en la configuración del usuario. **Positron** (Electron) sigue al
  sistema con sus propios ajustes, `window.autoDetectColorScheme`, `workbench.preferredLightColorTheme` y
  `workbench.preferredDarkColorTheme`, que están en el `settings.json` del usuario (en dotfiles): se documenta en
  `complementos/editores/INSTALL.md` y se le propone al autor, sin escribirlo. Todo comprobado en la sesión de prueba
  (capturas 53–56): con los cuatro abiertos en Lliphi Oscuro, el paso a Lliphi Claro cambió en vivo Kate, TeXstudio y
  Positron; `fondo-variante` pasó el perfil de Konsole a Lliphi Claro y un Neovim nuevo abrió con `background=light`.
- **5.9 (2026-11-01) La extensión de los editores se instala con la orden del editor, no copiando la carpeta.** En el
  escritorio del autor los temas de Lliphi no aparecían en Positron 2026.06 aunque la carpeta estaba en
  `~/.positron/extensions/lliphi.lliphi`: Positron, como VS Code desde hace varias versiones, solo carga las extensiones
  de su registro (`extensions.json`), anotó la carpeta copiada en `.obsolete` como desinstalada y la ignoró; y como
  «Lliphi Claro» no existía para él, borró de `settings.json` el tema claro preferido que lo nombraba (lo que parecía
  una línea que desaparecía sola). En la sesión de prueba no se vio porque el HOME era nuevo: la carpeta ya estaba antes
  del primer arranque y entró en el registro. Se decide: (1) `editores` genera además `vscode/lliphi.vsix` (un zip OPC
  con `extension.vsixmanifest`, reproducible: orden, fecha y permisos fijos, para que `verificar` no vea deriva); (2) el
  instalador deja de copiar la carpeta a VS Code, Positron y VSCodium y la instala con `<editor> --install-extension
  <vsix> --force` de cada uno que esté en el PATH (con `--extensions-dir` si el usuario fijó su carpeta), que la
  registra; `UNDO.sh` y `desinstalar` la retiran con `--uninstall-extension`; (3) para eso el núcleo de instalación gana
  dos ganchos genéricos de los `aplicar.py`, `tras_instalar(ctx, aplicar)` (después de copiar, también al simular;
  devuelve las líneas de `UNDO.sh` que lo deshacen) y `al_desinstalar(ctx, aplicar)`. Probado con órdenes falsas en
  `test_instalar_y_desinstalar_restaura` y, en el escritorio del autor, con el Positron real.
- **5.30 (2026-11-01) Telegram Desktop: dos temas desde los tokens, con las claves de la versión instalada.** El autor
  pidió el tema de Lliphi para Telegram. Instalado: Telegram Desktop 7.3.3 (Snap). Se decide: (1) **plantilla de
  claves**: la paleta por omisión de esa versión, `ui/colors.palette` de lib_ui en la confirmación que usa tdesktop
  `v7.3.3`, copiada en `fuentes/base/telegram-palette/` (GPL-3.0-or-later, como la base de Konsole; lo generado hereda
  la licencia). De ella salen el nombre, el orden y las referencias de las 586 claves; de sus colores, ninguno: una
  clave con color propio que no esté traducida hace fallar la generación. El `day-blue.tdesktop-theme` de los
  recursos de tdesktop es de 2019 y le faltan unas cien claves. (2) **todo resuelto**: Telegram copia una referencia
  con el valor que tenga la otra clave en ese momento, así que el tema se escribe con `#rrggbb[aa]` en cada clave y
  no depende del orden. (3) **traducción**: la ventana, la lista y los cuadros siguen la lógica de Plasma (vistas en
  `fondo.vista`, pasar el ratón en `fondo.ventana`); el acento en la selección (el chat activo), el foco, los botones
  principales, los contadores y los mensajes propios; los enlaces y las marcas de leído en `acento.texto`; «en línea»,
  aceptado y llamadas recibidas en `estado.exito` (Telegram los pinta con el acento); errores y borradores en
  `estado.error`; los ocho colores de participantes, de los ANSI, con el naranja en `estado.advertencia`, como en
  Obsidian. Lo que Telegram pinta siempre oscuro (visor de medios, llamadas, billetera) toma los tokens del oscuro en
  las dos variantes; los botones de color con icono blanco (contestar, Premium), los del claro. Los fondos con texto
  blanco del oscuro (peligro, insignias silenciadas) usan el acento o `borde.separador`, porque el error y el
  inactivo del oscuro son claros. (4) **la burbuja propia es el acento con alfa** (`26` en el claro, `33` en el oscuro)
  sobre el fondo del chat: un tinte azul o rojo oscuro, sobrio, sin un color fuera del maestro; la entrante es
  `fondo.vista` sobre `fondo.ventana` (claro) o `fondo.ventana-alterno` sobre el negro de Nothing (oscuro). El blanco
  sobre el rojo, con 4,5:1 justos, queda para lo breve (el chat activo, los botones), como en Plasma. Las flechas de
  descarga van en blanco: por omisión toman el fondo de la burbuja, que con alfa las dejaría translúcidas. (5) **fondo
  del chat liso** (`tiled.png` de un color): con un fondo de imagen, el tinte de las burbujas y su contraste dependerían
  de la imagen; los fondos de Lliphi quedan para el escritorio. (6) **seguir al sistema sin `fondo-variante`**:
  Telegram guarda un tema diurno y uno nocturno (`_themeKeyDay` y `_themeKeyNight` en `localstorage.cpp`; aplicar un
  tema lo guarda en el del modo actual) y, con «Modo nocturno automático» en «Sistema», cambia entre ellos cuando
  cambia la preferencia de color del sistema. Basta con aplicar cada tema en su modo una vez (`INSTALL.md`); ampliar la
  vigilancia exigiría escribir en el `tdata/` cifrado de Telegram. (7) **comprobación**: las pruebas leen el zip como
  Telegram (claves, sintaxis, fondo) y miden el contraste del texto sobre las burbujas con el alfa compuesto (≥ 4,5:1;
  el mínimo, 4,52, es el blanco sobre el rojo). En pantalla solo se vio que Telegram arranca con un HOME y un
  `-workdir` aislados en una sesión de KWin virtual (binario del Snap con sus bibliotecas). Antes de iniciar sesión,
  Telegram toma un archivo de la línea de órdenes como algo que enviar a un chat y no lo aplica, así que el aspecto
  queda por mirar en la cuenta del autor (con «Mantener cambios» o «Cancelar» en la vista previa de Telegram).
- **5.20 (2026-11-01) Xournal++: lo de GTK lo da `gtk`; la paleta y los colores propios, desde los tokens.** El autor
  pidió Xournal++ (1.3.3, GTK 3). Su interfaz y su modo oscuro (`themeVariant=useSystem`) siguen al complemento `gtk`,
  que además colorea la caja de herramientas flotante (su `xournalpp.css` la pinta en blanco). El complemento
  `xournalpp` trae lo que es de Xournal++: **(1)** una paleta de bolígrafos `Lliphi.gpl` en la carpeta de paletas del
  usuario, sobria: trece colores en el orden de los botones de la barra; como las páginas son blancas en las dos
  variantes, los de escribir son los legibles sobre papel (≥ 4,5:1: texto y acento del claro, el rojo de Nothing, los
  ANSI del claro) y los de resaltar, los claros del oscuro. **(2)** En `settings.xml`, con Xournal++ cerrado: gris oscuro
  alrededor de las páginas, la selección en el azul del claro (se ve sobre el papel) y la activa en el rojo, y los colores
  del recoloreado del modo oscuro (papel y tinta del oscuro, sin activarlo); son un valor para las dos variantes porque
  Xournal++ no los cambia con el modo. El fondo de página y la rejilla se dejan: son del documento y se imprimen. El
  `settings.xml` del autor es un enlace a sus dotfiles: aplicar escribe allí, con respaldo. Comprobado en el KWin
  virtual con un documento de muestra (`muestras/capturas/*-39-xournalpp.png`).
- **5.21 (2026-11-01) GIMP: un tema «Lliphi» con dos variantes, derivado del Default de GIMP 3.2.** GIMP es la 3.2.2.
  Su tema Default ya es paramétrico (diecisiete colores con nombre en `gimp-{light,gray,dark}.css` y el resto en
  `common*.css`), así que el de Lliphi copia los comunes (GPL-3.0-or-later, `fuentes/base/GIMP-Default/`) y escribe los
  colores desde los tokens: el claro con Lliphi Claro, el oscuro y el gris con Lliphi Oscuro. Un tema con sus dos
  variantes, como hace GIMP 3 y como Kvantum (4.19), en vez de dos temas: con `(theme-color-scheme system)` GIMP sigue al
  escritorio en vivo y `fondo-variante` no tiene que hacer nada. Encima, una capa con lo elegido (filas de listas y
  vistas, menú bajo el ratón, casillas, interruptores, progreso) en el acento; el lienzo y las barras de valor de las
  opciones de herramienta quedan neutros: en rojo entero gritaban (visto en pantalla) y GIMP los quiere grises para no
  sesgar el color. `common.css` importaba `../System/gimp.css`, que fuera del sistema no existe: pasa a `system.css`
  copiado. Y dos paletas `.gpl` con los colores de las de LibreOffice. Aplicar escribe solo `theme` y
  `theme-color-scheme` en `gimprc`, con GIMP cerrado. Comprobado en el KWin virtual en las dos variantes
  (`muestras/capturas/*-40-gimp.png`).
- **5.22 (2026-11-01) Calibre: sus paletas con nombre, no Kvantum; el visor sigue solo.** Calibre 9.17 no usa Kvantum
  (pinta con su estilo, sobre Fusion, salvo con `CALIBRE_USE_SYSTEM_THEME`) y ya cambia entre claro y oscuro con el
  escritorio (`color_palette` «system», en vivo). Desde la 7 cada modo admite una paleta con nombre en `gui.json`
  (`light_palettes`, `dark_palettes`, rol de `QPalette` → color; leído del código de 9.17). Se decide: **(1)** dos paletas
  «Lliphi Claro» y «Lliphi Oscuro» con la lógica de Kvantum, y `color_palette` en «system»; se conserva el estilo de
  Calibre, que es el mantenido. **(2)** El visor tiene esquemas propios, pero su «Sistema» toma fondo, texto y enlaces de
  la paleta de Calibre (`system_colors()`), así que con (1) ya sigue a Lliphi y a la variante; se añaden dos esquemas
  fijos de Lliphi para leer en la otra variante. **(3)** Solo esas claves de `gui.json` y `viewer-webengine.json`, con
  respaldo y con Calibre cerrado; la biblioteca del autor (`~/Documents/biblioteca`, `metadata.db`) no se abre. Comprobado
  en el KWin virtual con un perfil y una biblioteca de prueba (`muestras/capturas/*-41-calibre*.png`).
- **5.40 (2026-11-01) RStudio: temas `.rstheme` que también pintan la consola y la terminal.** El autor pidió RStudio,
  Octave y Spyder, los programas con que enseña e investiga. RStudio (2026.05.1 en su máquina) tiene un formato propio de
  temas, `.rstheme`: CSS sobre el editor Ace con dos comentarios de cabecera, `rs-theme-name` y `rs-theme-is-dark`, que
  registra desde `~/.config/rstudio/themes/` o con `rstudioapi::addTheme`. Se decide: (1) **un `.rstheme` por variante**
  con las reglas de los 34 temas que trae RStudio (editor, bloques de R Markdown, depuración, búsqueda, autocompletado,
  paréntesis y guías de sangría de colores), la sintaxis con la tabla de los editores y `isDark` verdadero solo en el
  oscuro, porque con él RStudio deriva del fondo del editor toda la interfaz (paneles, pestañas, barras y menús). (2) **la
  consola de R y la terminal integrada con los dieciséis colores de Konsole** (`.xtermColor0..15`, `.terminal`), como las
  demás terminales (4.30); los colores 16 a 255 de xterm no son de Lliphi y se calculan con la fórmula estándar (cubo
  6×6×6 y rampa de grises), como en los temas de RStudio, para que cli y tibble se vean como en una terminal; la prueba
  de colores los excluye por nombre. (3) **el instalador copia los temas y, con `--aplicar-tema`, pone `editor_theme`**
  en `rstudio-prefs.json` (respaldado; lo demás no se toca), como hace con el perfil de Konsole. RStudio no sigue al modo
  claro u oscuro del sistema, y comprobado en la sesión de prueba **no relee `rstudio-prefs.json` mientras está
  abierto** (a los 26 s seguía el tema anterior; al reabrirlo, el nuevo; al cerrarlo no reescribió el archivo): el cambio
  de variante se ve al abrir RStudio de nuevo (5.43). Validado en la sesión de prueba con las dos variantes (editor,
  consola con colores ANSI, interfaz).
- **5.41 (2026-11-01) GNU Octave: Lliphi Claro y Lliphi Oscuro en los dos «modos de color» de Octave.** Octave 11.1.0
  (Qt 6, QScintilla 2.14.1) no tiene temas: guarda sus colores en `~/.config/octave/octave-gui.ini` (ya no
  `qt-settings`) junto con todo lo demás (ventanas, atajos, archivos recientes). Leído en el código de la rama `stable`
  (`gui-preferences-*.cc`, `gui-settings.cc`), cada color tiene dos claves, la del primer modo y la del segundo con
  `_2` («Second color mode (light/dark)»), y los lexers del editor van en `[Scintilla]` y `[Scintilla_2]`. Se decide:
  (1) **el claro en el primer modo y el oscuro en el segundo**, de modo que cambiar de variante es cambiar los cuatro
  interruptores `*/color_mode` (editor, ventana de órdenes, editor de variables, espacio de trabajo). (2) **fusionar, no
  copiar**: un programa (`octave-lliphi.py`, instalado en `variante.d/`) escribe solo esas claves y conserva las
  fuentes que el usuario ya hubiera elegido; con `--aplicar-tema` lo ejecuta el instalador tras respaldar el ini. (3)
  **colores en el formato de Qt**: `@Variant(…)` con el `QColor` serializado, escapado como `iniEscapedString` de Qt, y
  comprobado contra Qt real (PySide6 lee once colores de prueba idénticos, y el primero coincide byte a byte con el que
  escribe Qt); los lexers, con entero 0xRRGGBB, y **todos** sus estilos válidos (Octave y Matlab 0–8, Bash 0–13, Diff
  0–11): uno que falte vuelve al blanco de QScintilla. Los lexers de C++, Java, Perl y Batch los deja Octave con su
  inversión automática en el segundo modo. (4) la ventana de órdenes solo admite texto, fondo, selección y cursor: van
  el fondo y el texto de Konsole; los dieciséis ANSI no tienen dónde ir. La interfaz no se toca: Octave sigue el esquema
  de Plasma. (5) si Octave nunca se abrió no se crea el ini: su asistente sale mientras `global_skip_welcome_wizard` no
  sea verdadero. Validado en la sesión de prueba: editor y ventana de órdenes en las dos variantes.
- **5.42 (2026-11-01) Spyder: esquemas de sintaxis, interfaz automática y los ANSI en la consola IPython.** Spyder 6.1.0
  (Anaconda, entorno base) guarda los esquemas en `[appearance]` de `~/.config/spyder-py3/config/spyder.ini`: 17 claves
  por esquema, la lista `names` y el elegido en `selected`; con `ui_theme = automatic` la interfaz es oscura si el texto
  normal del esquema es claro (`is_dark_font_color`). Se decide: (1) **dos esquemas, `lliphi/claro` y `lliphi/oscuro`, en
  `names`** como los de Spyder, no en `custom_names`, que exige nombres `custom-<n>` (crear un esquema nuevo falla con
  otro); con la tabla de los editores (definiciones en negrita, comentarios y `self` en cursiva). (2) **interfaz en
  automático**: así el esquema elegido decide claro u oscuro; esa interfaz es la paleta propia de Spyder (QDarkStyle), no
  la de Plasma. (3) **los dieciséis ANSI de Konsole en la consola IPython**: qtconsole los tiene fijos
  (`darkbg_color_map`) pero atiende OSC 4 de xterm; `consola.py`, que Spyder ejecuta al arrancar cada consola
  (`startup/run_file`; las `startup/run_lines` se ejecutan ocultas y qtconsole descarta su salida), los cambia por los de
  la variante del esquema elegido, y los escribe con la función que guarda el envoltorio de spyder-kernels para no
  provocar su aviso «Output from spyder call 'safe_exec'»; solo se configura si la consola no ejecutaba ya otro archivo.
  (4) Spyder reescribe `spyder.ini` entero mientras está abierto: el programa (`spyder-lliphi.py`) no escribe con Spyder
  abierto (su cerrojo `spyder.lock` apunta a un proceso vivo) y lo dice. Validado en la sesión de prueba en las dos
  variantes (editor, interfaz y consola con los colores de la terminal).
- **5.43 (2026-11-01) RStudio, Octave y Spyder siguen a la variante con la vigilancia de `fondo-variante`.** Ninguno de
  los tres cambia solo entre claro y oscuro. En lugar de enseñar a `seguir.py` los formatos de cada programa, se le añade
  un solo gancho: en cada cambio de variante ejecuta los programas de `variante.d/` (junto a él, en
  `~/.local/share/lliphi/`) con la variante y `--aplicar` (sin él al simular); cada complemento instala el suyo y decide
  si le toca: RStudio cambia `editor_theme` solo si era un tema de Lliphi; Octave, los interruptores solo si sus colores
  son los de Lliphi (lo reconoce por el fondo de la ventana de órdenes de los dos modos); Spyder, `selected` solo si el
  esquema era de Lliphi y Spyder está cerrado. Así el cambio que toca `seguir.py` es pequeño (otras sesiones también lo
  amplían) y un programa nuevo no lo vuelve a tocar. Los tres aplican el cambio al abrirse de nuevo (RStudio no relee su
  archivo abierto; Octave lee los colores al arrancar; Spyder, cerrado). Comprobado de punta a punta en la sesión de
  prueba: `plasma-apply-lookandfeel` al claro cambió los tres; de vuelta al oscuro con Spyder abierto, RStudio y Octave
  cambiaron y Spyder no se tocó.
- **5.44 (2026-11-02) RStudio: el `.rstheme` pinta también la ventana (barras, pestañas, divisores).** El autor vio que
  Lliphi solo aparecía en «Editor theme» y no en «RStudio theme» (Global Options → Appearance). Ese menú es fijo: solo
  ofrece los dos estilos de la interfaz que trae RStudio, «Modern» y «Sky», y no admite temas propios; con un tema claro,
  la ventana quedaba con los grises y el azul de esos estilos, y con uno oscuro, con el gris azulado propio de RStudio
  (`#303941`), no con los de Lliphi (5.40 suponía que RStudio derivaba la interfaz del fondo del editor: lo hace solo con
  los paneles de contenido). Pero RStudio carga el `.rstheme` en toda la página, no solo en el editor, así que el tema
  puede pintar la ventana. Leído el DOM de RStudio 2026.05.1 en vivo (depuración remota de Chromium en la sesión de
  prueba), se decide: (1) **solo clases estables**: las que RStudio deja para los temas (`rstheme_toolbarWrapper`,
  `rstheme_secondaryToolbar`, `rstheme_tabLayoutCenter`, `rstheme_minimizedWindowObject`) y las de GWT
  (`gwt-TabLayoutPanelTab(-selected)`, `gwt-TabLayoutPanelTabs`, `gwt-SplitLayoutPanel-*Dragger`, `dataGridHeader`),
  nunca las ofuscadas (`GBQS1KEB…`), que cambian en cada versión; la prueba lo comprueba. (2) **con `!important`**,
  porque RStudio pinta esas clases con más especificidad según su estilo y la variante; valen con «Modern» y con «Sky»
  (los dos son `rstudio-themes-flat`). (3) **la composición de Plasma**: barra de pestañas y divisores en
  `fondo.ventana-alterno`, barras de herramientas, cabeceras y pestaña elegida en `fondo.ventana`, la pestaña elegida
  con una raya de 2 px del acento arriba, como las pestañas de Breeze, y su texto en `texto.normal` (las demás en
  `texto.secundario`, ≥ 4,5:1). Comprobado en la sesión de prueba con las dos variantes, pixel a pixel contra los tokens.
- **5.45 (2026-11-02) GTK sigue de verdad a la variante: iconos, claro u oscuro y el nombre del tema.** El autor vio en
  gretl (GTK 3) los iconos mal en Lliphi Claro. Causa: al pasar a Claro (22:50 del 2026-11-01), kde-gtk-config (el
  módulo `gtkconfig` de kded) escribió en `gtk-3.0/settings.ini`, `gtk-4.0/settings.ini`, xsettingsd y GSettings los
  iconos `Colloid-Grey-Dark-Lliphi` y `prefer-dark-theme` del tema anterior, una décima de segundo después de que
  Plasma escribiera los nuevos: una carrera de KDE, no reproducida en la sesión de prueba (en el escritorio del autor
  `kdeglobals` es un enlace a sus dotfiles). Y en Oscuro gretl tampoco se veía bien: decide su modo oscuro buscando
  «dark» en `gtk-theme` de GSettings (sus iconos `fx` y `β̂` en versión `_dk`, la ruta en `#4a90d9`), y kde-gtk-config
  da `Breeze-Dark` solo a las aplicaciones X11 (xsettingsd) y deja `Breeze` en GSettings. Se decide, en la vigilancia
  de `fondo-variante` (sin tocar los formatos de GTK, que siguen siendo de KDE): (1) **si GTK no tiene los iconos o el
  claro u oscuro de KDE, se recarga `gtkconfig`**, que al cargarse lo vuelve a escribir todo desde la configuración de
  KDE (comprobado: con la configuración estropeada a mano, la recarga la deja como KDE); antes se espera hasta 3 s por
  si aún está escribiendo, y no se hace nada si el módulo no está cargado. (2) **`gtk-theme` de GSettings pasa a
  `Breeze-Dark` en Oscuro y a `Breeze` en Claro**, lo mismo que KDE da por xsettingsd, solo si es uno de los dos y el
  oscuro está instalado (otro tema no se toca) y después de la recarga, que vuelve a escribir `Breeze`. Comprobado en la
  sesión de prueba (Claro → Oscuro → Claro con la vigilancia en marcha, y gretl en cada una) y en la prueba
  `test_gtk_sigue_a_kde`. Si algo de KDE vuelve a escribir `Breeze` sin cambio de variante (otra preferencia de GTK),
  gretl vuelve a sus iconos claros hasta el siguiente cambio.
  (3) **el instalador arranca la vigilancia en una unidad propia del systemd de usuario** (`lliphi-fondo-variante`,
  con `systemd-run --collect`): arrancada como hijo del instalador, quedaba en el grupo de procesos de quien lo
  ejecutó (una terminal, el asistente) y se paraba al cerrarlo. Solo si ese systemd es el de la misma sesión (mismo
  `HOME` y misma pantalla): en la sesión de prueba anidada no lo es y la vigilancia correría en el escritorio real;
  allí sigue arrancando como antes.
- **5.46 (2026-11-02) La tipografía en el formato de Qt 6, y la del usuario se respeta.** Al reinstalar con
  `--aplicar-tema` (5.45), el autor vio toda la interfaz «fea y en negrita». Lliphi escribía las fuentes de
  `kdeglobals` en el formato de Qt 5, de 10 campos (`Inter,10,-1,5,400,0,0,0,0,0`), y Qt 6 lee el peso de ese formato
  en la escala vieja (0–99, 50 normal): 400 pasa a 900, Black (comprobado con Qt 6.10: `QFont::fromString` da 900; con
  los 16 campos de Qt 6, 400). Hasta entonces no se notaba porque el autor había vuelto a guardar sus fuentes desde
  Preferencias del sistema, que las escribe en el formato de Qt 6 (con los títulos en `SemiBold`). Se decide: (1) **las
  fuentes en el formato de Qt 6** (`fuente()` de `global/construir.py`, 16 campos, el que escribe el propio
  `QFont::toString`), en `contents/defaults`, en el instalador y en el `Font=` de SDDM, cuya pantalla también es Qt 6;
  (2) **el instalador respeta la fuente del usuario** si ya es de la misma familia (Inter, JetBrains Mono) y está en el
  formato de Qt 6: su tamaño y su peso son elección suya; la del formato de Qt 5 o la de otra familia se reescribe. A
  su escritorio se le repusieron sus valores del respaldo. Prueba: `test_tipografia_en_formato_qt6`.
- **5.47 (2026-11-02) GTK como root y los botones de ventana de GTK.** El autor vio «BleachBit as Administrator» sin
  Lliphi y el botón de cerrar de Claude Desktop de otro color. (1) **Como root** (pkexec o sudo), una aplicación GTK
  tiene el `HOME` de root y no lee `~/.config/gtk-3.0/` del usuario. pkexec le quita Wayland, así que va por X11 y toma
  el tema y los iconos de xsettingsd, que es de la sesión del usuario: le falta solo `gtk.css` y lo que importa
  (comprobado en la sesión de prueba con un `HOME` vacío y X11: Breeze o Adwaita sin Lliphi; con los enlaces, Lliphi
  Claro y, al pasar a Oscuro, Lliphi Oscuro, aun con el «Dark mode» propio de BleachBit, que viene activado). Se decide
  **`instalar.py gtk-root`**: con pkexec, enlaza en `~root/.config/gtk-3.0/` y `gtk-4.0/` la hoja, los colores, las
  hojas de Lliphi y los botones del usuario. Enlaces y no copias, para que sigan a la variante; sin `settings.ini`
  (llega por xsettingsd); no sobrescribe un archivo propio de root (sale 3 sin tocar nada); `UNDO.sh` los quita. Es,
  con `sddm`, lo único de Lliphi que pide contraseña, y lo ejecuta el usuario: desde una terminal con `sudo`, sin ella
  con `pkexec` (en la terminal de la app de Claude pkexec falló: polkit responde «No session for cookie» fuera de la
  sesión de escritorio). (2) **Los botones de ventana** de las
  aplicaciones con barra propia (Electron, barras de cabecera de GTK) son imágenes que kde-gtk-config hace de la
  decoración de KWin (`gtk-3.0/assets/`), y la carrera de 5.45 también puede dejar las de la otra variante (las de
  Claude Desktop eran las del oscuro, de las 22:50). La vigilancia lo comprueba: con la decoración de Lliphi, el botón
  de cerrar del claro lleva su acento y el del oscuro no; si no cuadra con la variante, recarga `gtkconfig`. Una
  aplicación ya abierta guarda las imágenes que cargó al arrancar: toma las nuevas al abrirse de nuevo.
