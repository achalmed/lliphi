## Instalar

Requiere Obsidian 1.14 o posterior (probado en 1.14.5). El instalador de Lliphi **no toca Obsidian**: los temas viven
dentro de cada vault (`<vault>/.obsidian/themes/`), no en una carpeta XDG.

### Desde el repositorio del tema (recomendado)

El tema se publica con su `manifest.json` en [achalmed/obsidian-lliphi](https://github.com/achalmed/obsidian-lliphi):

1. Descarga `theme.css` y `manifest.json` de la última versión y cópialos a `<vault>/.obsidian/themes/Lliphi/`
   (o, con un clon del repositorio, `./instalar.sh <vault> --aplicar`; o con BRAT, «Add a beta theme»,
   `achalmed/obsidian-lliphi`).
2. Obsidian → Ajustes → Apariencia → Temas → **Lliphi**. La variante sigue al modo claro u oscuro de Obsidian
   (Ajustes → Apariencia → Modo).

### Desde esta copia de Lliphi

```bash
mkdir -p "<vault>/.obsidian/themes/Lliphi"
cp generado/obsidian/theme.css "<vault>/.obsidian/themes/Lliphi/"
printf '{\n  "name": "Lliphi",\n  "version": "0.0.0",\n  "minAppVersion": "1.14.0",\n  "author": "achalmed"\n}\n' > "<vault>/.obsidian/themes/Lliphi/manifest.json"
```

## Actualizar

Copia el `theme.css` nuevo encima (o `./traer.sh --aplicar` y `./instalar.sh <vault> --aplicar` en el repositorio del
tema); Obsidian lo recarga solo.

## Desinstalar

Elige otro tema en Ajustes → Apariencia → Temas y borra `<vault>/.obsidian/themes/Lliphi/`.
