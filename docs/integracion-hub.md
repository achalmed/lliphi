---
tipo: doc
estado: activo
titulo: 'Integración con el hub achalmaedison.netlify.app: decisión, parche propuesto (sin aplicar) y reversión'
---
# Integración con el hub

## Decisión (fase 8)

El hub (`web`, Quarto, Netlify) ya organiza sus 11 blogs como **sitios satélite**: repositorio propio, `_quarto.yml`
propio, dominio `<nombre>.netlify.app`, `_site/` empujado y servido sin build, y un enlace desde el menú «More» del
hub (`web/docs/pubs-submodulos.md`, `web/_pubs/pubs.yml`). Lliphi sigue el mismo patrón, con dos diferencias
deliberadas:

1. **No es submódulo de `web`** ni entra en `_pubs/pubs.yml`: no es un blog, no comparte el tema «Quiet Laboratory»
   (su tema sale de los tokens del escritorio) y `scripts/sync-theme-pubs.sh` no debe propagarle el SCSS del hub.
2. El sitio vive dentro del repositorio del tema (`sitio/`), no en un repositorio aparte: una sola fuente de tokens
   alimenta escritorio y web, y el catálogo se genera de `modulos/`.

Alternativas descartadas: una sección del hub (`achalmaedison.netlify.app/lliphi/`) obligaría a renderizar el sitio
con el tema del hub y a versionar las capturas en `web`; un subdominio propio (`lliphi.achalmaedison.dev`) exige un
dominio que hoy no existe.

## Parche propuesto para `web/_quarto.yml` (no aplicado)

Una entrada en el menú «More», después de los blogs y antes de «Book an appointment»:

```diff
           - text: "Seguridad informática"
             href: https://chaska-x.netlify.app/
+          - text: "Lliphi · temas para KDE Plasma"
+            href: https://lliphi.netlify.app/
           - text: "Book an appointment"
             href: appointment/index.qmd
```

Cómo aplicarlo con respaldo y reversión (lo ejecuta el autor, en `~/Documents/web`):

```bash
cp _quarto.yml "$RESPALDOS_DIR/web-_quarto.yml.antes-lliphi-$(date +%F)"      # respaldo fuera del repo
# editar _quarto.yml con el diff de arriba
quarto render index.qmd                                                       # verifica que el hub renderiza (N 5.16)
git add _quarto.yml _site && git commit -m "nav: enlace a Lliphi (temas para KDE Plasma) en More" && git push
```

Reversión: `git revert <commit>` o restaurar la copia del respaldo y volver a renderizar.

El menú «More» de los 11 blogs es una copia del del hub: si el autor quiere el enlace también allí, se añade la misma
línea en cada `_pubs/*/_quarto.yml` (los `_quarto.yml` de los pubs no se propagan con `sync-theme-pubs.sh`).

## Enlace de vuelta

El sitio de Lliphi enlaza al hub en la barra («Edison Achalma») y en el pie («Hub académico»), y usa el mismo pie
de licencia que el hub (código y contenido por separado).
