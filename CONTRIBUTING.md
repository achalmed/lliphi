# Contribuir a Lliphi

La guía completa está en el sitio: [lliphi.netlify.app/contribuir](https://achalmed.github.io/lliphi/contribuir.html)
(fuente: `sitio/contribuir.qmd`). Resumen:

1. Incidencia primero (problema o propuesta), con versión de Plasma, variante y captura.
2. Lo generado no se edita: cambia los tokens o la fuente del módulo (`modulos/<id>/`, `complementos/<id>/`, `global/`)
   y corre `generar.py --aplicar`. Cada módulo explica en su `README.md` cómo se desarrolla.
3. Contraste en verde (`modulos/esquema/paleta.py`), módulos válidos (`generar.py validar`), pruebas en verde (`pytest`),
   licencias en verde (`reuse lint`).
4. Un módulo nuevo es una carpeta con `modulo.json`, `README.md`, `INSTALL.md` y `construir.py` (contrato en
   `docs/arquitectura.md` §4); el núcleo, el instalador y el sitio lo descubren solos.
5. Nada de terceros; todo archivo con licencia declarada.
6. Commits en español con Conventional Commits.
