---
tipo: estado
estado: activo
actualizado: 2026-10-18
---
# estado.md — tema-plasma (nombre provisional de la carpeta y del proyecto)

Lo primero que se lee y lo último que se escribe en cada sesión. El encargo es
`prompts/07 produccion/temas_de_escritorio/prompt_01_ecosistema_de_temas_kde.md` (fases 1 a 9).
Hasta que el autor elija el nombre (fase 3), la carpeta se llama `tema-plasma` y no está en `meta/workspace.yml`.

## Hecho

| fecha | qué | dónde se ve |
|---|---|---|
| 2026-10-18 | lote 2, iconos: `herramientas/destinos/iconos.py` → `generado/icons/{lliphi,lliphi-oscuro}/` (solo carpetas y lugares, 25 nombres × 5 tamaños, `FollowsColorScheme`, 64 px escalable); render de muestra `muestras/capturas/iconos-carpetas-render.png`; módulo, instalador, prueba, compatibilidad, changelog, decisión 3.13 | `modulos/iconos/`, `sitio/generado/catalogo/iconos.qmd` |
| 2026-10-18 | lote 2, editores: `herramientas/destinos/editores.py` → `generado/editores/vscode/lliphi/` (extensión con `package.json` y dos temas) y `generado/editores/zed/lliphi.json`; tabla única de sintaxis desde los ANSI; el instalador añade la base `vscode` (`~/.vscode/extensions/`, decisión 3.12); pruebas, compatibilidad, changelog | `modulos/editores/`, `sitio/generado/catalogo/editores.qmd` |
| 2026-10-18 | lote 2, terminales: generador `herramientas/destinos/terminales.py` → `generado/terminales/{alacritty,kitty}/` (claro y oscuro, desde el grupo `terminal` más selección, cursor y enlace de los semánticos); módulo `terminales`; el instalador admite destinos en `$XDG_CONFIG_HOME`; prueba, compatibilidad y changelog | `modulos/terminales/`, `sitio/generado/catalogo/terminales.qmd` |
| 2026-10-18 | fase 3 cerrada: el autor eligió **Lliphi**; fase 4 corregida: la primera paleta (verde azulado) no era la fusión pedida; segunda paleta con el rojo de Nothing sobre neutros casi negros y grises suaves (25 pares en verde), variantes de acento `azul` y `verde-azul` en el script, boceto del escritorio (`herramientas/boceto.py` → `muestras/boceto-*.png`) | `docs/direccion-artistica.md` |
| 2026-10-18 | fase 5 (borrador): arquitectura (fuente → generadores → `generado/` versionado con prueba de deriva; instalador reversible; módulos y lotes), decisiones 1.1–3.10 y matriz de compatibilidad | `docs/arquitectura.md`, `docs/decisiones.md`, `docs/compatibilidad.md` |
| 2026-10-18 | fase 4: paleta OKLCH en `herramientas/paleta.py` → `tokens/tokens.json` (DTCG 2025.10), 25 pares de contraste medidos y en verde en las dos variantes, primer generador (`herramientas/generar_esquema.py` → `generado/color-schemes/*.colors`) y lámina de widgets Breeze (`herramientas/lamina.py` → `muestras/*.png`); `.venv` con coloraide; dirección artística documentada, pendiente de aprobación | `docs/direccion-artistica.md` |
| 2026-10-18 | fase 2 cerrada: análisis de los temas de partida, matriz de referencias, mecánica de cada categoría en Plasma 6.6 y estándares del repositorio; Aurorae reescrito en 6.6 (motor SVG V2): el primer lote usa Breeze coloreada por el esquema | `docs/analisis-temas-de-partida.md`, `docs/investigacion.md` |
| 2026-10-18 | fase 3: estudio de nombres (Lliphi recomendado; Sosiego segunda opción) | `docs/nombre.md` |
| 2026-10-18 | usuario de prueba `prueba-tema` (uid 1001) creado por el autor para la validación de la fase 7 | `id prueba-tema` |
| 2026-10-18 | fase 2, fuentes: 15 páginas (KDE Developer sobre estilos de Plasma, Aurorae y fondos; freedesktop Icon Theme y XDG Base Directory; Design Tokens Format Module 2025.10; REUSE 3.3; SPDX) impresas a PDF e ingeridas en Calibre (ids 10520-10534, serie «Ecosistema de temas - Fundamentación técnica»); RIS para Zotero en `scripts-biblioteca/ingesta/salida_ris/ingesta_20261018_130400.ris` | Calibre; el prompt 1.0.1 las cita |
| 2026-10-18 | fase 1, inspección: versiones (Plasma 6.6.6, Qt 6.10.2, KF 6.24.0, Wayland), herramientas, rutas XDG, tema en uso (WhiteSur-dark), los dos temas de partida identificados en disco y por la API OCS, acceso a las referencias, riesgos | `docs/entorno.md` |

## En curso

- nada: el primer lote (0.1.0) está completo y probado; la publicación es del autor (`docs/publicacion.md`).

## Por hacer

- 2026-10-18 · dueño: autor · **el disco interno `/dev/nvme0n1` (INTEL HBRPEKNX0101AH) aparece como «likely to fail soon» en Plasma** (aviso de Device Health visto en la sesión de prueba): respaldar y comprobar con `sudo smartctl -a /dev/nvme0n1`.
- 2026-10-18 · dueño: autor · **publicar 0.1.0**: crear el remoto `achalmed/lliphi`, empujar, etiquetar `v0.1.0`, `gh release create` con `dist/`, sitio en Netlify (`lliphi`), parche del hub y fichas en KDE Store; comandos en `docs/publicacion.md`.
- 2026-10-18 · dueño: autor · **validar visualmente el lote 2**: abrir Alacritty, Kitty, VS Code y Zed con los temas (`instalar.py --modulos terminales,editores --aplicar` y los pasos de cada `INSTALL.md`), elegir los iconos `lliphi` en el KCM y mirar Dolphin a 100 % y 150 % (si los distintivos se desalinean, añadir directorios `@2x`); capturas a `muestras/capturas/` y estado de los módulos a «probado».
- 2026-10-18 · dueño: asistente · navegador (Zen/Firefox) desde los mismos tokens; cursores; `[Icons][Theme]` en los temas globales cuando el autor apruebe los iconos; subir `VERSION` a 0.2.0 al publicar el lote 2 (los módulos ya declaran `desde: 0.2.0`).
- 2026-10-18 · dueño: autor · validar con inicio de sesión real como `prueba-tema` (SDDM, splash, bloqueo, escala 150 %, una aplicación GTK): `python3 /tmp/lliphi-dist/herramientas/instalar.py --aplicar --aplicar-tema oscuro`.
- 2026-10-18 · dueño: director · renombrar la carpeta `tema-plasma` → `lliphi` con `core/renombrar.py` y darla de alta en `meta/workspace.yml`.
- 2026-10-18 · dueño: autor · importar en Zotero `scripts-biblioteca/ingesta/salida_ris/ingesta_20261018_130400.ris` (15 ítems de esta serie) y pegar las claves en `#zotero_key`.
