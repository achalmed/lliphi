# Estilo de Plasma (`estilo`)

**Plasma Style** del encargo: `lliphi-claro` y `lliphi-oscuro`, los SVG del panel, los diálogos, los tooltips, los
widgets y los fondos translúcidos de Plasma, derivados del estilo de WhiteSur-kde (GPL-3.0; decisión 3.11).

## Responsabilidad

- Copiar los 38 SVG de WhiteSur (descomprimidos para que el diff se lea) y recolorear sus hex fijos con `MAPA`
  (vacío en la línea base del autor: WhiteSur tal cual).
- El `colors` del estilo: el de WhiteSur con solo el acento de la variante (mejora 8, decisiones 4.13), con la misma
  función `con_acento()` del módulo `esquema`.
- `metadata.json` y `plasmarc` propios: desenfoque y contraste (de los tokens `efectos`), transparencia adaptable y
  fondo por omisión.
- Aporta al tema global `[plasmarc][Theme] name`.

## Formato KDE

Paquete `Plasma/Theme` en `~/.local/share/plasma/desktoptheme/<id>/`: `metadata.json` con `KPlugin` y `X-Plasma-API`
(**sin** `KPackageStructure`, igual que Breeze en `/usr/share/plasma/desktoptheme/default`), `plasmarc`, `colors`,
`widgets/*.svg`, `dialogs/*.svg` y `solid/` (las versiones opacas sin efectos). `kpackagetool6 --type Plasma/Theme
--show <id>` lo encuentra; `--list` no, por la falta de `KPackageStructure`.

## Estructura

```
modulos/estilo/
├── modulo.json   paquete · Plasma/Theme · depende de esquema para construirse
├── construir.py  copia y recolorea fuentes/base/WhiteSur-kde/plasma/desktoptheme/{WhiteSur,WhiteSur-dark}; valores()
├── INSTALL.md · README.md
```

Lo generado: `generado/estilo/lliphi-{claro,oscuro}/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos estilo --aplicar
python3 herramientas/instalar.py --modulos estilo --aplicar && plasma-apply-desktoptheme lliphi-oscuro
```

Para recolorear un SVG, añade su hex a `MAPA[variante]` → token semántico (nunca un hex nuevo: lo vigila
`test_ningun_hex_fuera_del_maestro` para lo que sale de los tokens). La translucidez solo se ve en una sesión real,
no en la anidada (docs/validacion.md §6). Pruebas: `test_estilo_plasma_derivado`, `test_acento_por_variante`.
