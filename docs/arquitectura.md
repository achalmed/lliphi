---
tipo: doc
estado: activo
titulo: 'Arquitectura del repositorio (fase 5): fuente de verdad, generadores, módulos, instalación, pruebas y publicación'
---
# Arquitectura

Fase 5 del encargo, 2026-10-18 (borrador hasta que el autor apruebe el nombre y la paleta). Las decisiones y su
porqué están en `decisiones.md`; la mecánica de Plasma que las sostiene, en `investigacion.md` §2. El nombre
«lliphi» es provisional (`tokens/marca.json`).

## 1. Principio: una fuente, todo generado

```
tokens/tokens.json  (DTCG 2025.10; lo escribe herramientas/paleta.py)
tokens/marca.json   (nombre, ids, autor)
        │
        ▼  herramientas/generar.py  (un módulo por destino en herramientas/destinos/)
generado/            ← nunca se edita; `herramientas/generar.py verificar` falla si difiere de lo que generaría
  color-schemes/     LliphiClaro.colors, LliphiOscuro.colors
  look-and-feel/     org.lliphi.claro/, org.lliphi.oscuro/   (metadata.json, contents/defaults, layouts, previews)
  desktoptheme/      lliphi-claro/, lliphi-oscuro/           (metadata.json, colors, plasmarc, widgets/*.svg propios)
  konsole/           Lliphi Claro.colorscheme, Lliphi Oscuro.colorscheme
  wallpapers/        org.lliphi.sumaq/ (contents/images, images_dark, metadata.json con acento)
  sitio/             datos del catálogo (JSON) que consume el sitio
```

Lo que no sale de los tokens (los SVG dibujados a mano, los fondos, los QML si algún día los hay) vive en
`fuentes/` y el generador lo copia o lo parametriza. Los tres estratos no se mezclan: **fuentes** (originales,
editables), **generado** (derivados, versionados para que el usuario pueda instalar sin herramientas) y
**artefactos de publicación** (`dist/`: tarballs para KDE Store, no versionados).

## 2. Árbol del repositorio

```
lliphi/
├── README.md · LICENSE · LICENSES/ · REUSE.toml · CHANGELOG.md · CITATION.cff · CONTRIBUTING.md
├── estado.md                 (traspaso entre sesiones, regla 10 del ecosistema; no se publica en el sitio)
├── pyproject.toml            (herramientas y pruebas; sin dependencias de pago)
├── tokens/                   tokens.json (generado por paleta.py) · marca.json
├── herramientas/             paleta.py · generar.py · destinos/{esquema,lookandfeel,desktoptheme,konsole,fondo,sitio}.py
│                             · lamina.py · instalar.py · capturas.py
├── fuentes/                  svg/ (SVG propios del estilo de Plasma) · fondos/ (originales) · marca/ (logotipo)
├── generado/                 (ver §1)
├── modulos/                  un INSTALL.md + manifiesto por pieza publicable (lo lee el sitio)
├── pruebas/                  test_tokens.py · test_contraste.py · test_generado.py · test_instalar.py · test_sitio.py
├── docs/                     entorno · investigacion · analisis-temas-de-partida · nombre · direccion-artistica
│                             · arquitectura · decisiones · compatibilidad · instalar (tutorial) · personalizar (guía)
│                             · referencia (tokens, módulos) · historial/
├── muestras/                 láminas y capturas reales por variante y caso
├── sitio/                    sitio oficial (Quarto, mismo motor que el hub del autor) → _site/
└── dist/                     (no versionado) tarballs por módulo y versión
```

## 3. Módulos

Cada módulo tiene un identificador, una carpeta en `generado/`, un `modulos/<id>/INSTALL.md` (instalación,
actualización y desinstalación a mano), su entrada en la matriz de compatibilidad, su prueba y su estado
(implementado, probado, experimental, pendiente). La versión del proyecto es una (SemVer en `CHANGELOG.md`);
cada módulo declara desde qué versión existe.

| id | qué entrega | tecnología | estado al nacer | lote |
|---|---|---|---|---|
| `esquema` | `LliphiClaro.colors`, `LliphiOscuro.colors` | KColorScheme | implementado (fase 4) | 1 |
| `global` | `org.lliphi.claro`, `org.lliphi.oscuro` (look-and-feel con `X-KDE-fallbackPackage=org.kde.breeze.desktop`) | KPackage Plasma/LookAndFeel | pendiente | 1 |
| `estilo` | `lliphi-claro`, `lliphi-oscuro` (desktoptheme mínimo: `colors`, `plasmarc`, SVG propios solo donde Breeze no basta: panel, diálogos, tooltip) | Plasma SVG | pendiente | 1 |
| `konsole` | dos `.colorscheme` con paleta ANSI derivada y ≥ 4.5:1 | Konsole | pendiente | 1 |
| `fondos` | un paquete con `images/` e `images_dark/` y acento declarado | KPackage Wallpaper | pendiente | 1 |
| `decoracion` | ninguna propia: Breeze coloreada por `[WM]` y `Colors:Header` | KDecoration | implementado por herencia | 1 |
| `gtk` | ninguna propia: `breeze-gtk` genera desde el esquema; documentación de lo que ocurre | kde-gtk-config | implementado por herencia | 1 |
| `iconos` | `lliphi`, `lliphi-oscuro`: solo carpetas (y lugares) en el acento, heredan el resto de Breeze | freedesktop | implementado (lote 2) | 3 |
| `cursores` | herencia de `breeze_cursors`; módulo propio solo si aporta | freedesktop | pendiente | 3 |
| `aurorae` | solo en SVG (V2) y solo si Breeze no basta | Aurorae V2 | pendiente | 3 |
| `terminales` | Alacritty (`[colors]` TOML) y Kitty (`.conf`), claro y oscuro, desde el grupo `terminal` | varias | implementado (lote 2) | 2 |
| `editores` | extensión mínima de VS Code y tema de Zed; sintaxis desde los ANSI con una tabla única | varias | implementado (lote 2) | 2 |
| `kvantum`, `navegadores` (Zen/Firefox), `productividad`, `ciencia` (RStudio, Positron, JupyterLab, matplotlib) | archivos por aplicación generados de los tokens | varias | pendiente | 2–4 |
| `sddm`, `plymouth` | con confirmación explícita y root | SDDM, Plymouth | pendiente | 4 |

## 4. Instalación, actualización, desinstalación

`herramientas/instalar.py` (Python 3.10+, sin dependencias fuera de la biblioteca estándar; también se publica
`instalar.sh` que lo llama):

- **simula por defecto**; `--aplicar` escribe; `--modulos esquema,global,…` elige; `--variante claro|oscuro|ambas`;
- escribe solo en `$XDG_DATA_HOME` (`~/.local/share`) y `$XDG_CONFIG_HOME` (`~/.config`); nunca en `/usr`;
- comprueba dependencias (`kpackagetool6`, `plasma-apply-*`, versión de Plasma ≥ 6.2 por `plasmashell --version`);
- **respalda** antes de tocar: `kdeglobals`, `plasmarc`, `kwinrc`, `kcminputrc`, `ksplashrc`, `gtk-3.0/settings.ini`,
  `gtk-4.0/settings.ini`, `plasma-org.kde.plasma.desktop-appletsrc`, en `~/.local/state/lliphi/respaldos/<fecha>/`,
  con suma SHA-256 verificada, y deja ahí un `UNDO.sh` que restaura byte a byte y desinstala;
- no pisa archivos ajenos: si existe un paquete con el mismo `Id` y no es de Lliphi (manifiesto propio), se detiene;
- `--aplicar-tema` aplica con `plasma-apply-lookandfeel` (sin `--resetLayout` salvo `--disposicion`);
- `desinstalar` elimina lo instalado según el manifiesto `~/.local/state/lliphi/instalado.json` y restaura;
- `actualizar` = desinstalar lo de la versión anterior + instalar la nueva, conservando los respaldos.

## 5. Verificación

| prueba | qué comprueba |
|---|---|
| `test_tokens.py` | `tokens.json` válido (DTCG: `$type`, `$value`, sin alias rotos); los ids de `marca.json` son ASCII |
| `test_contraste.py` | los 25 pares de `paleta.py` en las dos variantes (1.4.3 y 1.4.11) |
| `test_generado.py` | `generar.py verificar`: lo versionado en `generado/` coincide con una generación nueva; ningún hex fuera del maestro; sintaxis de `.colors`, `metadata.json`, `plasmarc`, `.colorscheme`; SVG bien formados y con `hint-*` |
| `test_instalar.py` | instalación en un `HOME` temporal: simula, aplica, verifica rutas, desinstala y compara el `HOME` antes y después |
| `test_licencias.py` | `reuse lint` en verde; ningún archivo de `fuentes/` sin cabecera o `.license` |
| `test_sitio.py` | el sitio renderiza, sin enlaces rotos, catálogo = módulos |
| manual (fase 7) | capturas reales por variante y caso en `muestras/`, con el usuario `prueba-tema` |

## 6. Publicación

- `CHANGELOG.md` (Keep a Changelog), etiquetas anotadas `v0.1.0`, GitHub Releases con los tarballs de `dist/`
  (`herramientas/generar.py empaquetar`), notas de versión generadas del CHANGELOG.
- KDE Store: una ficha por módulo publicable (global claro y oscuro, esquemas, Konsole, fondos), con `Source` al
  repositorio; el autor sube a mano (fase 9).
- Integración continua (GitHub Actions): `pytest`, `reuse lint`, `generar.py verificar`, render del sitio.

## 7. Diagrama C4

Contexto: el **autor** (diseña, aprueba, publica) y el **usuario de Plasma** (instala, aplica, desinstala) usan el
**repositorio Lliphi**; este lee la **documentación de KDE** y escribe en **Plasma 6** (archivos de usuario), en
**GitHub** (código y versiones), en **KDE Store** (fichas) y en **Netlify** (sitio), y se enlaza con el **hub
`achalmaedison.netlify.app`**.

Contenedores del repositorio: *tokens* (JSON) → *generadores* (Python) → *generado* (paquetes de Plasma, esquemas,
Konsole, fondos) → *instalador* (Python/Bash) → *escritorio del usuario*; en paralelo, *pruebas* (pytest, reuse)
y *sitio* (Quarto) que lee *modulos/* y *generado/sitio/*.
