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
  porque su rojo significa «cerrar», no acento. `--acento X` sigue poniendo el mismo acento en las dos variantes para probar.
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
- **4.28 (2026-11-01) Konsole sigue a la variante y lleva su acento.** El autor vio Konsole con colores que no
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
- **4.16 (2026-10-19) Mejora 10: el claro, validado en pantalla y corregido.** En una sesión de Plasma virtual aparte se
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
