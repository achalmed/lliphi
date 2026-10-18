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
- **2.2 (2026-10-18) Un solo acento (matiz 195) que sigue al sistema.** Nothing fija el rojo 258 veces en los SVG y
  WhiteSur el azul; aquí el acento es un token y los SVG propios usan `currentColor` con las clases
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
- **2.7 (2026-10-18) Papel cálido de día, pizarra fría de noche** (matices 80 y 255) con croma ≤ 0.014: las dos
  variantes comparten lógica y geometría y cambian solo las primitivas.

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
  respaldo con SHA-256 y `UNDO.sh` en `~/.local/state/llampu/`. Motivo: reversible, auditable, sin root.
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
