# Telegram Desktop (`telegram`)

Dos temas de Telegram Desktop, **Lliphi Claro** y **Lliphi Oscuro**, como archivos `.tdesktop-theme`, con las 586
claves de color de la versión instalada (7.3.3) y todos los colores sacados de los tokens.

Es un **complemento**: no es parte de un `Plasma/LookAndFeel`. Arquitectura:
[`docs/arquitectura.md`](../../docs/arquitectura.md). Por qué y cómo se tradujeron los tokens: decisión 5.30 de
[`docs/decisiones.md`](../../docs/decisiones.md).

## Responsabilidad y formato

- Entrega `generado/telegram/Lliphi Claro.tdesktop-theme` y `Lliphi Oscuro.tdesktop-theme`. Cada uno es un zip
  reproducible con `colors.tdesktop-theme` (líneas `clave: #rrggbb[aa];`) y `tiled.png`, el fondo liso del chat. Al
  lado van los mismos archivos sueltos (`claro/`, `oscuro/`) para leerlos y compararlos en el repositorio.
- Las claves, su orden y sus referencias salen de la paleta por omisión de Telegram,
  [`fuentes/base/telegram-palette/colors.palette`](../../fuentes/base/telegram-palette/ORIGEN.md) (lib_ui,
  GPL-3.0-or-later; de ahí la licencia de este módulo y de lo generado). Ningún color de esa paleta llega a lo generado.
- No lo instala el instalador de Lliphi: Telegram aplica un tema al abrir el archivo y lo guarda cifrado en su
  `tdata/`, no en una carpeta XDG (`INSTALL.md`).

| zona de Telegram | sale de |
|---|---|
| ventana, lista de chats, cuadros, menús (`window*`, `dialogs*`, `box*`, `menu*`) | `fondo.vista`, `fondo.ventana` (al pasar el ratón), `fondo.ventana-alterno`, los tres textos, `borde.*` |
| selección, foco, botones principales, contadores (`windowBgActive`, `dialogsBgActive`, `activeButton*`, `activeLineFg`) | `acento.base`, `acento.suave`, `foco`, `seleccion.*`; texto en `texto.sobre-acento` |
| enlaces, servicio, marcas de leído (`windowActiveTextFg`, `msg*ServiceFg`, `historyOutIconFg`) | `acento.texto` |
| burbuja entrante (`msgInBg`) | `fondo.vista` en el claro, `fondo.ventana-alterno` en el oscuro |
| burbuja propia (`msgOutBg`) | `acento.base` con alfa (26 claro, 33 oscuro) sobre el fondo del chat: un tinte del acento |
| fondo del chat (`tiled.png`) | liso: `fondo.ventana` en el claro, `fondo.vista` (el negro de Nothing) en el oscuro |
| errores, borradores, peligro (`attentionButton*`, `boxTextFgError`, `dialogsDraftFg`) | `estado.error`; el fondo de peligro con texto blanco del oscuro es `acento.base` |
| en línea, aceptado, llamadas recibidas (`contactsStatusFgOnline`, `dialogsOnlineBadgeFg`, `boxTextFgGood`) | `estado.exito` |
| avisos (`historyPeer8*`, `outdateSoonBg`, estrellas) | `estado.advertencia` |
| los ocho colores de los participantes, iconos de ajustes, archivos | ANSI de `terminal` (rojo 1, verde 2, amarillo 3, azul 4, morado 5, rosa 13, cian 6); el naranja es `estado.advertencia` |
| visor de medios, llamadas, billetera | los tokens del **oscuro** en las dos variantes, porque Telegram los pinta siempre oscuros |
| sombras y velos | `fondo.complementario` (el casi negro) con alfa |

Todo sale resuelto a `#rrggbb[aa]`, sin referencias: Telegram copia una referencia con el valor que tenga en ese
momento, y así el archivo no depende del orden.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos telegram            # simula
.venv/bin/python herramientas/generar.py --modulos telegram --aplicar
.venv/bin/pytest -k telegram
```

Para una versión nueva de Telegram: se reemplaza `fuentes/base/telegram-palette/colors.palette` por el de la
confirmación de lib_ui que use esa etiqueta de tdesktop. Si aparece una clave con color propio que no está en `TABLA`,
`generar.py` falla y la nombra; `test_telegram_tabla_sin_claves_huerfanas` avisa de las claves retiradas.

Pruebas: `test_telegram_temas` (el zip y su contenido, todas las claves en el orden de la paleta, ningún color fuera del
maestro, el fondo liso, contraste ≥ 4,5:1 del texto sobre las burbujas, con el alfa compuesto, y sobre los fondos, y el
acento de cada variante en la selección, los botones y los mensajes propios).
