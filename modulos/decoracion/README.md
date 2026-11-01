# Decoración de ventanas (`decoracion`)

**Window Decoration** del encargo: los temas Aurorae `lliphi` (oscuro) y `lliphi-claro`, derivados de la decoración
«Nothing» (jomada, GPL-3.0-or-later): botones circulares con glifo al pasar el ratón, barra de título, bordes y
sombra. Independiente de los demás módulos: KWin lo carga por su cuenta.

## Responsabilidad

- Copiar los SVG de Nothing (`decoration.svg`, `close.svg`, `maximize.svg`, `minimize.svg`, `restore.svg`,
  `alldesktops.svg`, `keepabove.svg`, `keepbelow.svg`) y recolorearlos: el oscuro es Nothing tal cual; el claro se
  recolorea con los tokens porque Nothing no tiene variante clara.
- Los plus de la mejora 4 (decisiones 4.8): el anillo cian de minimizar en gris, el título en los grises de Lliphi y
  sin sombra, barra de 18 px; la tipografía del título (Inter Medium) la fija el tema global.
- `metadata.json` (`KPackageStructure: KWin/Aurorae`), `metadata.desktop` y el `<id>rc`.
- Aporta al tema global `[kwinrc][org.kde.kdecoration2]`: `library=org.kde.kwin.aurorae.v2`,
  `theme=__aurorae__svg__<id>` y los botones (`ButtonsOnLeft=XIA`); `aplicar.py` escribe esas claves otra vez y
  reconfigura KWin, porque `plasma-apply-lookandfeel` no siempre las escribe (docs/validacion.md §6).

## Formato KDE y compatibilidad con KWin

Plasma 6.6 reescribió Aurorae (motor SVG V2, `kwin-style-aurorae`): el KCM escribe `library=org.kde.kwin.aurorae.v2` y
el tema se nombra `__aurorae__svg__<carpeta>`. Se instala en `~/.local/share/aurorae/themes/<id>/`.
`kpackagetool6 --type KWin/Aurorae --show <id>` lo encuentra (avisa de que espera `decoration.svgz`; el motor V2 lee
también `.svg`, comprobado en sesión anidada).

## Estructura

```
modulos/decoracion/
├── modulo.json   paquete · KWin/Aurorae
├── construir.py  SVG y rc desde fuentes/base/Nothing-aurorae; id_tema(); valores()
├── aplicar.py    kwinrc + qdbus6 org.kde.KWin /KWin reconfigure
├── INSTALL.md · README.md
```

Lo generado: `generado/decoracion/{lliphi,lliphi-claro}/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos decoracion --aplicar
python3 herramientas/instalar.py --modulos decoracion --aplicar --aplicar-tema oscuro   # o Preferencias → Decoraciones de ventanas
```

Para recolorear, `MAPA[variante]` (hex de Nothing → token) y `NEUTRO` (hex de Nothing → hex de Nothing). Formas y
tamaños de los botones no se tocan. Pruebas: `test_decoracion_aurorae`, `test_acento_por_variante`.
