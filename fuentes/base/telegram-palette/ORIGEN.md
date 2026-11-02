Paleta por omisión de Telegram Desktop, `ui/colors.palette` de
[desktop-app/lib_ui](https://github.com/desktop-app/lib_ui) en la confirmación
`2f29133506e174a9d4a7b78740c3f1b04c2b993c`, la que usa
[telegramdesktop/tdesktop](https://github.com/telegramdesktop/tdesktop) en la etiqueta `v7.3.3` (submódulo
`Telegram/lib_ui`), la versión instalada (Snap `telegram-desktop` 7.3.3). Desktop App Toolkit, © 2014-2026 The
Desktop App Toolkit Authors, GPL-3.0-or-later con la excepción de OpenSSL
([LEGAL](https://github.com/desktop-app/legal/blob/master/LEGAL)). Descargada el 2026-11-01 como plantilla de claves
del tema de Telegram de Lliphi (decisiones 5.30).

No se edita: `complementos/telegram/construir.py` toma de aquí el nombre, el orden y las referencias de las 586 claves
de color; ningún color de esta paleta llega a lo generado, todos salen de los tokens. Para una versión nueva de
Telegram, se reemplaza el archivo por el de la confirmación de lib_ui que use esa etiqueta de tdesktop, se actualiza
este origen y la prueba `test_telegram_temas` dice qué claves nuevas faltan por traducir.
