---
tipo: doc
estado: activo
titulo: 'Línea base de Lliphi (2026-10-18): la configuración del autor que le gusta, tal cual, y cómo la reproduce el tema'
---
# Línea base

El autor, tras ver 0.1.0 y 0.2.0, fijó como punto de partida **su configuración activa**, una mezcla que montó él mismo,
y pidió un solo cambio: la tipografía, a una de estilo Apple. Desde aquí se mejora, pieza a pieza, con su visto bueno.

## 1. Inventario (sesión del autor, Plasma 6.6.6, 2026-10-18 18:10)

| componente | valor activo | de dónde viene | cómo lo reproduce Lliphi |
|---|---|---|---|
| tema global | `com.github.vinceliuice.WhiteSur-dark` | WhiteSur-kde (GPL-3.0) | `org.lliphi.oscuro` con los mismos `defaults` |
| esquema de color | `WhiteSurDark` (acento azul 49,91,239) | WhiteSur-kde | `LliphiOscuro.colors` = WhiteSurDark con solo el acento de los tokens (mejora 1, decisiones 4.5, aprobada); `LliphiOscuro-tokens.colors` guarda el esquema generado por entero desde los tokens |
| estilo de Plasma | `WhiteSur-dark` (con su `colors`) | WhiteSur-kde | `lliphi-oscuro` = copia tal cual, metadata propia, fondo de Lliphi en `plasmarc` |
| estilo de widgets | `kvantum-dark`, tema Kvantum `LliphiOscuro` | WhiteSur-kde recoloreado con los tokens (rojo) | `generado/kvantum/LliphiOscuro` |
| decoración | Aurorae V2 `__aurorae__svg__Nothing`, botones `XIA` a la izquierda | Nothing (GPL-3.0-or-later) | `lliphi` = Nothing tal cual con barra de 18 px |
| iconos | `breeze-dark` | KDE | `defaults` |
| cursores | `WhiteSur-cursors` | KDE Store 1411743 (GPL-3.0) | `defaults`; dependencia externa (no se redistribuye) |
| menús Qt | Breeze `MenuOpacity=80` | — | instalador |
| tipografía (cambiada hoy) | **Inter 10** (interfaz, menús, barras; Inter Medium en títulos), **Hack 10** (monoespaciada) | Inter (OFL, instalada), Hack (MIT, instalada) | `defaults` e instalador |
| disposición | panel superior (`location=3`) y panel inferior (`location=4`) del autor | WhiteSur | no se toca (el instalador respalda `appletsrc`) |

Lo que **no** está activo: el estilo de Plasma de cristal propio de 0.2.0 (`lliphi` con SVG generados), Papirus, Bibata y
el esquema rojo de los tokens. Quedan en el repositorio como piezas opcionales.

## 2. Qué sigue (una mejora por vez, con captura y visto bueno)

1. **Hecha y aprobada por el autor (18:35)**: acento rojo de Lliphi en el esquema sin tocar lo demás (`LliphiOscuro.colors`,
   decisiones 4.5); comparación en `muestras/comparacion-linea-base-acento.png`; aplicada en la sesión con
   `plasma-apply-colorscheme LliphiOscuro`; se revierte con `plasma-apply-colorscheme WhiteSurDark`.
2. **Hecha y aprobada por el autor (18:58)**: variante clara equivalente (`org.lliphi.claro`: WhiteSur + `LliphiClaro` rojo +
   `lliphi-claro` + Kvantum `LliphiClaro`) comprobada en sesión anidada (decisiones 4.6, `validacion.md` §7); comparación
   en `muestras/comparacion-linea-base-clara.png`. No aplicada en la sesión del autor.
3. Iconos: probar Papirus con carpetas rojas junto a esta base (ya descargado) y decidir.
