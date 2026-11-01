# Esquema de color (`esquema`)

**Color Scheme** del encargo. Dueño de la paleta de Lliphi y de los esquemas de color de Plasma: `LliphiClaro.colors`
y `LliphiOscuro.colors` (KColorScheme), que colorean todas las aplicaciones Qt y KDE y, a través de Plasma, las GTK.

## Responsabilidad

- **La paleta** (`paleta.py`): define cada color en OKLCH, deriva los tokens semánticos de las dos variantes, mide el
  contraste WCAG 2.2 de 25 pares (texto ≥ 4.5:1; foco y controles ≥ 3:1) y escribe `tokens/tokens.json` (DTCG
  2025.10). Ese archivo es la salida pública del módulo y el contrato que leen todos los demás: ningún otro módulo
  define colores.
- **Los esquemas** (`construir.py`): la línea base del autor (decisiones 4.4) más la mejora 1 (4.5): los esquemas de
  WhiteSur renombrados y con solo el acento (foco, hover, enlace, selección) tomado de los tokens; todo lo demás, byte a
  byte. El esquema generado por entero desde los tokens se conserva como `Lliphi*-tokens.colors` (no se instala).
- **La correspondencia cromática** que reutilizan otros: `con_acento()` (la usa `estilo` para su `colors`).
- Aporta al tema global `[kdeglobals][General] ColorScheme`.

## Formato KDE

Archivo `.colors` suelto (no es KPackage) en `~/.local/share/color-schemes/`: grupos `[Colors:View|Window|Button|
Selection|Tooltip|Complementary|Header]` y `[Colors:Header][Inactive]` con doce claves `R,G,B`, más
`[ColorEffects:*]`, `[General]` (`ColorScheme` = nombre del archivo), `[KDE]` y `[WM]`.

## Estructura

```
modulos/esquema/
├── modulo.json   paquete · KColorScheme · instala los dos .colors en color-schemes/
├── paleta.py     paleta OKLCH → tokens/tokens.json y contraste (pide coloraide: .venv)
├── construir.py  esquemas desde fuentes/base/WhiteSur-kde/color-schemes + acento de los tokens; valores(); con_acento()
├── INSTALL.md · README.md
```

Lo generado: `generado/esquema/{LliphiClaro,LliphiOscuro}{,-tokens}.colors`.

## Dependencias

Base `fuentes/base/WhiteSur-kde` (GPL-3.0); `plasma-apply-colorscheme` para aplicar; `coloraide` solo para `paleta.py`.
Lo usan: `estilo` (código), `global` (identificador) y, por los tokens, todos.

## Desarrollar

```bash
.venv/bin/python modulos/esquema/paleta.py                      # informe de contraste; sale 1 si un par falla
.venv/bin/python modulos/esquema/paleta.py --acento azul --aplicar   # reescribe tokens/tokens.json
.venv/bin/python herramientas/generar.py --aplicar               # un cambio de tokens afecta a todos los módulos
python3 herramientas/instalar.py --modulos esquema --aplicar && plasma-apply-colorscheme LliphiOscuro
```

Un azul de WhiteSur que no esté en `AZULES_WHITESUR` no se sustituye: si WhiteSur cambia, ampliar la lista y mirar
`test_esquema_linea_base_solo_acento`, que exige que solo cambie el acento. Pruebas: `test_tokens_dtcg_validos`,
`test_contraste_todos_los_pares`, `test_esquemas_completos`, `test_esquema_linea_base_solo_acento`, `test_acento_por_variante`.
