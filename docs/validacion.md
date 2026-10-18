---
tipo: doc
estado: activo
titulo: 'Validación (fase 7): instalación en una sesión limpia, capturas reales por variante y caso, defectos y límites'
---
# Validación

Fase 7 del encargo, 2026-10-18, Plasma 6.6.6 (Wayland). Método: una **sesión de Plasma anidada** en una ventana
de 1600×900 (`kwin_wayland --xwayland --exit-with-session=startplasma-wayland` bajo `dbus-run-session`) con un
`HOME` aparte en `/tmp/casa-lliphi`, de modo que la configuración del autor no se toca. En ese `HOME` se instaló
el primer lote con `herramientas/instalar.py --aplicar` (respaldo, manifiesto y `UNDO.sh` comprobados), se aplicó
cada variante con `plasma-apply-lookandfeel`, `plasma-apply-colorscheme` y `plasma-apply-wallpaperimage` **con el
DBus de la sesión anidada**, y se capturó desde dentro con `spectacle -b -n`. El usuario `prueba-tema` queda
disponible para una segunda validación con inicio de sesión real (SDDM, splash, bloqueo).

## 1. Capturas reales (`../muestras/capturas/`)

| caso | oscuro | claro | qué se comprueba |
|---|---|---|---|
| escritorio con panel superior y dock | `oscuro-01-escritorio.png` | `claro-01-escritorio.png` | panel fino de 36 px, dock flotante centrado, fondo con variante oscura |
| lanzador (Kickoff) | `oscuro-02-lanzador.png` | `claro-02-lanzador.png` | selección y foco en rojo, superficies por planos, texto legible |
| Dolphin + Konsole + notificación | `oscuro-03-…png` | `claro-03-…png` | selección en listas, foco en elemento, notificación de Plasma (tooltip/dialogs del estilo) |
| Preferencias del sistema → Colores | `oscuro-04-…png` | `claro-04-…png` | el esquema aparece y se aplica; encabezados; acento del esquema |
| Kate | `oscuro-05-kate.png` | `claro-05-kate.png` | aplicación Qt grande: menús, pestañas, barras |

Las vistas previas de los paquetes globales (`generado/look-and-feel/*/contents/previews/`) son ya estas
capturas (caso 02), no el boceto.

## 2. Resultado por componente

| componente | estado | observación |
|---|---|---|
| esquemas `LliphiClaro` / `LliphiOscuro` | **probado** | aparecen en el KCM de colores y se aplican; selección, foco, enlaces y estados con los colores de los tokens |
| tema global (`org.lliphi.claro` / `.oscuro`) | **probado** | `plasma-apply-lookandfeel -a` aplica esquema, estilo, iconos, cursores y decoración; la disposición (`--resetLayout`) crea el panel superior y el dock |
| estilo de Plasma `lliphi` (sigue el esquema) | **probado** | panel, lanzador, notificación y tooltip con los SVG propios; sigue el esquema y el acento |
| decoración Breeze coloreada | **probado** | barra de título con `[WM]` y `Colors:Header`; botones a la derecha |
| Konsole | probado parcialmente | el esquema se instala y se elige en el perfil; la paleta ANSI no se verificó sobre texto real |
| fondo `org.lliphi.horizonte` | **probado con salvedad** | `Image=org.lliphi.horizonte` por nombre no se resolvió («unknown wallpaper provider»); por **ruta del paquete** sí. El `defaults` y el layout pasan a usar la ruta (`~/.local/share/wallpapers/<Id>`) hasta entender la resolución por nombre |
| GTK generado por Plasma | no verificado | no se abrió una aplicación GTK en la sesión anidada |
| escalas 150 % y 200 % | no verificado | la sesión anidada corre a escala 1 |
| SDDM, splash, bloqueo | no verificado | fuera del primer lote; piden inicio de sesión real |

## 3. Defectos encontrados y corregidos durante la validación

1. `instalar.py` fallaba al escribir `sumas.json` cuando el `HOME` no tenía nada que respaldar (carpeta no creada). Corregido.
2. Reinstalar sobre una instalación idéntica sin manifiesto se tomaba por conflicto. Corregido: lo idéntico nunca es conflicto.
3. El fondo por nombre de paquete no carga (ver tabla). Corregido en los generadores: ruta del paquete.
4. **Incidente de método**: la primera orden `plasma-apply-lookandfeel --resetLayout` se ejecutó con el `HOME` de prueba
   pero con el DBus de la sesión del autor; no alteró su escritorio (comprobado con captura y `appletsrc`), pero pudo
   hacerlo. Regla desde entonces: toda orden `plasma-apply-*` se ejecuta con el `DBUS_SESSION_BUS_ADDRESS` de la
   sesión de prueba (se lee del entorno de su `plasmashell`), nunca con el del autor.

## 4. Límites que quedan

- Iconos de carpeta de Breeze en azul junto al acento rojo: coherente pero no ideal; un módulo de iconos (lote 3)
  podría recolorear solo las carpetas.
- La lámina de widgets (`herramientas/lamina.py`) no reproduce el foco del esquema fuera de Plasma; las capturas
  reales lo confirman en el escritorio.
- Validación con inicio de sesión real (usuario `prueba-tema`), escalas y aplicaciones GTK: pendiente para el autor
  o para una sesión posterior.
