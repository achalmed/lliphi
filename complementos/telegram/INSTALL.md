## Instalar

Requiere Telegram Desktop 7.3 o posterior (las claves son las de 7.3.3; una versión más nueva ignora lo que falte y
pone sus colores por omisión en las claves nuevas). El instalador de Lliphi **no toca Telegram**: Telegram guarda el
tema aplicado, cifrado, en su carpeta de datos (`tdata/`), no en una carpeta XDG.

Telegram guarda **dos temas**: uno para el modo diurno y otro para el nocturno. Al aplicar un tema, lo guarda en el
del modo en que esté en ese momento. Para tener los dos:

1. Si está activo, apaga el **modo nocturno automático**: Ajustes → Ajustes de chat → «Modo nocturno automático»
   («Auto-night mode») → «Desactivado». Mientras siga en «Sistema», Telegram no deja cambiar de modo a mano.
2. Con el **modo nocturno apagado** (menú principal ☰ → «Modo nocturno»), abre `Lliphi Claro.tdesktop-theme` y pulsa
   «Mantener cambios» («Keep changes»). Para abrirlo, entra en Ajustes → Ajustes de chat → «Fondo del chat» → «Elegir
   desde archivo» («Choose from file»), que acepta archivos de tema. También puedes enviarlo a Mensajes guardados y
   pulsar sobre él. Un doble clic en el gestor de archivos **no** sirve: Telegram toma el archivo como algo que
   enviar a un chat.
3. Activa el **modo nocturno** en el menú principal, abre `Lliphi Oscuro.tdesktop-theme` y pulsa «Mantener cambios».
4. Vuelve a poner el modo nocturno automático en **«Sistema»**. A partir de ahí Telegram pasa solo de Lliphi Claro a
   Lliphi Oscuro cuando Plasma cambia de variante (lee la preferencia de color del sistema, la que fijan los temas
   globales de Lliphi), sin la vigilancia de `fondo-variante`.

Los archivos están en `generado/telegram/` de esta copia de Lliphi, o en las versiones publicadas. Con el Snap,
Telegram solo lee archivos de tu carpeta personal que no estén ocultos (no lee `~/.cache` ni `~/.local`, por ejemplo);
`~/Documents/…` o `~/Descargas` sirven.

## Actualizar

Repite los pasos 1 a 4 con los archivos nuevos: un tema abierto reemplaza al guardado del modo en que estés.

## Desinstalar

En cada modo (diurno y nocturno), Ajustes → Ajustes de chat → «Temas de color» y elige uno de los de Telegram
(«Clásico», «Día», «Noche»…). Telegram no deja copia del archivo fuera de su `tdata/`.
