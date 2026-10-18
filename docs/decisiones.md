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
  empaquetar un `.vsix`, que exigen `vsce` y una cuenta; queda para cuando el autor publique.
- **3.13 (2026-10-18) Iconos: solo carpetas, dos temas por herencia, 64 px escalable.** Un tema propio completo
  compite con Breeze y envejece con cada KDE; aquí se dibujan únicamente `folder`, `folder-open`, sus sinónimos y los
  lugares de uso común, con un distintivo geométrico desde 22 px (a 16 px no cabe). Hay dos temas porque la herencia
  (`breeze` o `breeze-dark`) es lo único que ven las aplicaciones GTK; en KDE, `FollowsColorScheme=true` y las clases
  `ColorScheme-Highlight` / `ColorScheme-HighlightedText` hacen que la carpeta siga el acento y su texto de contraste.
  El directorio de 64 px es `Scalable` hasta 512 para que las vistas grandes de Dolphin no caigan en la carpeta de
  Breeze. Alternativa descartada: directorios `@2x`/`@3x` (los SVG ya escalan; se añadirán si la validación real
  muestra desalineación en 150 %).

