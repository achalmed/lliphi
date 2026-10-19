# Bases de terceros de las que Lliphi deriva (decisión del autor, 2026-10-18)

| base | origen | licencia | qué se toma |
|---|---|---|---|
| WhiteSur-kde | https://github.com/vinceliuice/WhiteSur-kde (Vince Liuice), rama master, 2026-08-07 | GPL-3.0 | estilo de Plasma (`plasma/desktoptheme`), decoración Aurorae, tema Kvantum, disposición; se recolorean con los tokens de Lliphi y se retira todo lo que imita a Apple (logotipo, semáforo, appmenu) |
| WhiteSur-dark (tema global) | `com.github.vinceliuice.WhiteSur-dark` instalado en la máquina del autor (KDE Store, Vince Liuice), copiado el 2026-10-19 a `WhiteSur-kde/plasma/look-and-feel/` sin `splash/images/background.png` | GPL-3.0; `logout/*` de KDE, GPL-2.0-or-later | pantalla de carga (indicador giratorio y disposición) y diálogo de salida; se sustituyen el logotipo de Apple por el nombre en Inter y el fondo por el de Lliphi (mejora 6) |
| Nothing | KDE Store 2116667 (jomada, Seducción Linux), 1.8, instalado en la máquina del autor | GPL-3.0-or-later | botones de la decoración (círculos con glifo), barra fina y dock que se oculta, esquema Konsole translúcido |

Lo derivado de estas bases se publica bajo GPL-3.0-or-later (REUSE.toml, `generado/desktoptheme/**`, `generado/aurorae/**`,
`generado/kvantum/**`, `fuentes/base/**`). Lo propio del proyecto (tokens, generadores, instalador, esquemas, sitio) sigue en MIT y CC BY-SA 4.0.
