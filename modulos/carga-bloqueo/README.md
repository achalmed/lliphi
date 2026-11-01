# Pantallas de carga, salida y bloqueo (`carga-bloqueo`)

**Splash & Lockscreen** del encargo: la pantalla de carga (splash) y el diálogo de salida, derivados de WhiteSur-dark
(mejora 6), y el fondo de la pantalla de bloqueo (mejora 10). Es un **componente** del tema global. No es el inicio de
sesión: ese es SDDM (`complementos/sddm`), otro programa, con root.

## Por qué es un componente (comprobado en Plasma 6.6.6)

- **Carga y salida** solo se cargan desde un paquete `Plasma/LookAndFeel`: `[KSplash] Theme=<Id>` lee
  `contents/splash/Splash.qml` de ese paquete, y el diálogo de salida, `contents/logout/`. Por eso este módulo no tiene
  paquete propio: el tema global llama a `integrar()` y los archivos quedan en
  `generado/global/<Id>/contents/{splash,logout}/`. Así se desarrolla aparte y se distribuye donde KDE lo busca.
- **El bloqueo** no es del tema global: `kscreenlocker_greet` carga `lockscreen` del paquete de shell
  (`/usr/share/plasma/shells/org.kde.plasma.desktop/contents/lockscreen/LockScreen.qml`); Breeze tampoco trae
  `contents/lockscreen/`. Un QML de bloqueo dentro del tema global se ignoraría (la validación avisa si aparece). Lo que
  Lliphi controla del bloqueo es su fondo, en `kscreenlockerrc`, y sus colores (esquema y estilo).

## Responsabilidad

- `construir.py`: copia la pantalla de carga de WhiteSur-dark, sustituye el logotipo de Apple por el nombre del tema en
  Inter con el punto en el acento, oscurece el indicador en la variante clara, pone el fondo de Lliphi dentro del
  paquete y adapta `Logout.qml` para que no dependa de rutas relativas a WhiteSur. Aporta `[KSplash] Theme`.
- `aplicar.py`: con `--aplicar-tema`, el bloqueo con la imagen oscura de Lliphi en las dos variantes (para que el reloj
  blanco se lea también en el claro), solo si se instaló el complemento `fondos`.

## Estructura

```
modulos/carga-bloqueo/
├── modulo.json   componente · integracion.en = global · rutas que deben quedar dentro del paquete
├── construir.py  valores() e integrar(tokens, marca, variante, paquete, hechos)
├── aplicar.py    kscreenlockerrc [Greeter][Wallpaper][org.kde.image][General] Image y PreviewImage
├── INSTALL.md · README.md
```

## Dependencias

Construcción: `fondos` (la imagen) y la base `fuentes/base/WhiteSur-kde/plasma/look-and-feel/` (GPL-3.0); Pillow.
Las sustituciones sobre el QML de WhiteSur están protegidas por `assert`: si WhiteSur cambia, la construcción falla en
lugar de generar algo roto.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos carga-bloqueo --aplicar   # reconstruye el tema global que lo integra
python3 herramientas/instalar.py --modulos global --aplicar
ksplashqml org.lliphi.oscuro --test --window                                 # verla en una ventana
```

Pruebas: `test_pantallas_carga_y_salida`, `test_componentes_dentro_del_tema_global`, `test_variante_clara_validada`.
