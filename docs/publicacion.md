---
tipo: doc
estado: activo
titulo: 'Publicación (fase 9): lo que queda preparado y los comandos exactos que ejecuta el autor'
---
# Publicación

Estado el 2026-10-18: el autor pidió al asistente ejecutar la publicación. **Hecho**: remoto `achalmed/lliphi`,
etiqueta `v0.1.0` (en el commit del primer lote), release con `dist/`, sitio en GitHub Pages (`achalmed.github.io/lliphi`,
workflow `.github/workflows/sitio.yml`), enlace en el hub. **Pendiente del autor**: KDE Store (cuenta) y, si lo quiere,
Netlify. Lo que sigue describe el procedimiento para las versiones siguientes.

## 1. Lo que ya está en el repositorio

- `VERSION` = `0.1.0`; `CHANGELOG.md` con la sección `[0.1.0]`; `LICENSES/`, `REUSE.toml`; `README.md`,
  `CONTRIBUTING.md`; `.github/workflows/ci.yml` (contraste, deriva, pruebas, REUSE, render del sitio).
- `herramientas/generar.py empaquetar` escribe en `dist/` (no versionado) un `.tar.gz` por módulo y
  `SHA256SUMS`; el nombre lleva la versión.
- `sitio/_site/` renderizado y versionado (Netlify lo sirve sin build, como en el hub).

## 2. Comandos para el autor

### Repositorio y primera versión

```bash
cd ~/Documents/lliphi            # o ~/Documents/lliphi tras el renombrado
gh repo create achalmed/lliphi --public --source=. --remote=origin --description "Temas para KDE Plasma: casi negro y gris suave con acento rojo; claro y oscuro desde una sola fuente de tokens" --push
git tag -a v0.1.0 -m "Lliphi 0.1.0: primer lote (esquemas, temas globales, estilo de Plasma, Konsole, fondos)"
git push origin v0.1.0
.venv/bin/python herramientas/generar.py empaquetar
gh release create v0.1.0 dist/*.tar.gz dist/SHA256SUMS --title "Lliphi 0.1.0" --notes-file dist/NOTAS-0.1.0.md
```

### Sitio: GitHub Pages (hecho) o Netlify (opcional)

GitHub Pages publica `sitio/_site` en cada push que lo cambie (`gh api -X POST repos/achalmed/lliphi/pages -f build_type=workflow`
ya ejecutado). Si se prefiere Netlify:

En app.netlify.com: *Add new site → Import an existing project* → repositorio `achalmed/lliphi`, **base directory**
`sitio`, **publish directory** `sitio/_site`, *build command* vacío; nombre del sitio `lliphi`
(`lliphi.netlify.app`, libre el 2026-10-18). Después, el parche del hub (`integracion-hub.md`).

### KDE Store

Una ficha por módulo publicable, en pling.com (misma cuenta que opendesktop):

| ficha | categoría | archivo de `dist/` |
|---|---|---|
| Lliphi Oscuro (y Claro) | Global Themes (Plasma 6) | `lliphi-global-<versión>.tar.gz` (contiene `org.lliphi.oscuro/` y `org.lliphi.claro/`) |
| Lliphi (esquemas) | KDE Color Scheme KDE4 | `lliphi-esquema-<versión>.tar.gz` |
| Lliphi (estilo de Plasma) | Plasma Theme | `lliphi-estilo-<versión>.tar.gz` |
| Lliphi Horizonte | KDE Wallpaper | `lliphi-fondos-<versión>.tar.gz` |

Texto de la ficha: `dist/FICHA-KDE-STORE.md` (lo escribe `empaquetar`). Campo *Source*: el repositorio; licencia:
CC BY-SA 4.0 (activos) y MIT (código). El procedimiento de alta en la tienda no se ha verificado desde el proyecto
(`investigacion.md` §6): la primera subida la hace el autor y se documenta aquí lo que encuentre.

## 3. Después de publicar

- `estado.md`: fila en «Hecho» con la fecha y los enlaces; `docs/compatibilidad.md` se actualiza con los informes de
  usuarios.
- Alta del repositorio en `meta/workspace.yml` y renombrado de la carpeta (`core/renombrar.py`): cambio estructural
  del director con etiqueta, simulación y respaldo.
- Versiones siguientes: `VERSION`, `CHANGELOG.md`, `git tag -a`, `empaquetar`, `gh release create`.
