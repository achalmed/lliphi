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
| 2026-10-18 | fase 5 (borrador): arquitectura (fuente → generadores → `generado/` versionado con prueba de deriva; instalador reversible; módulos y lotes), decisiones 1.1–3.10 y matriz de compatibilidad | `docs/arquitectura.md`, `docs/decisiones.md`, `docs/compatibilidad.md` |
| 2026-10-18 | fase 4: paleta OKLCH en `herramientas/paleta.py` → `tokens/tokens.json` (DTCG 2025.10), 25 pares de contraste medidos y en verde en las dos variantes, primer generador (`herramientas/generar_esquema.py` → `generado/color-schemes/*.colors`) y lámina de widgets Breeze (`herramientas/lamina.py` → `muestras/*.png`); `.venv` con coloraide; dirección artística documentada, pendiente de aprobación | `docs/direccion-artistica.md` |
| 2026-10-18 | fase 2 cerrada: análisis de los temas de partida, matriz de referencias, mecánica de cada categoría en Plasma 6.6 y estándares del repositorio; Aurorae reescrito en 6.6 (motor SVG V2): el primer lote usa Breeze coloreada por el esquema | `docs/analisis-temas-de-partida.md`, `docs/investigacion.md` |
| 2026-10-18 | fase 3: estudio de nombres (Llampu recomendado; Sosiego segunda opción) | `docs/nombre.md` |
| 2026-10-18 | usuario de prueba `prueba-tema` (uid 1001) creado por el autor para la validación de la fase 7 | `id prueba-tema` |
| 2026-10-18 | fase 2, fuentes: 15 páginas (KDE Developer sobre estilos de Plasma, Aurorae y fondos; freedesktop Icon Theme y XDG Base Directory; Design Tokens Format Module 2025.10; REUSE 3.3; SPDX) impresas a PDF e ingeridas en Calibre (ids 10520-10534, serie «Ecosistema de temas - Fundamentación técnica»); RIS para Zotero en `scripts-biblioteca/ingesta/salida_ris/ingesta_20261018_130400.ris` | Calibre; el prompt 1.0.1 las cita |
| 2026-10-18 | fase 1, inspección: versiones (Plasma 6.6.6, Qt 6.10.2, KF 6.24.0, Wayland), herramientas, rutas XDG, tema en uso (WhiteSur-dark), los dos temas de partida identificados en disco y por la API OCS, acceso a las referencias, riesgos | `docs/entorno.md` |

## En curso

- fase 3 y 4: el autor elige el nombre (Llampu o Sosiego) y aprueba la paleta; mientras tanto se redacta la arquitectura (fase 5) con el nombre provisional (dueño: asistente).

## Por hacer

- 2026-10-18 · dueño: autor · elegir el nombre (fase 3) y después dar de alta la carpeta en `meta/workspace.yml` (director).
- 2026-10-18 · dueño: autor · importar en Zotero `scripts-biblioteca/ingesta/salida_ris/ingesta_20261018_130400.ris` (15 ítems de esta serie) y pegar las claves en `#zotero_key`.
