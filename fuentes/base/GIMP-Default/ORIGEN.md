Tema «Default» de GIMP 3.2 (los autores de GIMP, https://www.gimp.org; GPL-3.0-or-later), copiado el 2026-11-01 de
`/usr/share/gimp/3.0/themes/Default/` del paquete `gimp-data` 3.2.2-1ubuntu0.26.04.1 de Kubuntu 26.04, con la hoja del
tema «System» (`/usr/share/gimp/3.0/themes/System/gimp.css`) como `system.css`, como base del tema de GIMP de Lliphi
(decisiones 5.21). No se edita: `complementos/gimp/construir.py` escribe desde los tokens los tres archivos de color
(`gimp-light.css`, `gimp-gray.css`, `gimp-dark.css`; los de aquí quedan como referencia de los diecisiete nombres),
copia `common*.css` cambiando solo la importación de `../System/gimp.css` por `system.css`, y en `ui/*.svg` cambia el
color de los puntos de los separadores y quita los colores de la página de Inkscape.
