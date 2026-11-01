## Instalar a mano

```bash
mkdir -p ~/.config/Kvantum
cp -r LliphiOscuro LliphiClaro ~/.config/Kvantum/
kvantummanager --set LliphiOscuro                       # o LliphiClaro
```

Y en Preferencias del sistema → Colores y temas → Estilo de las aplicaciones, elige «kvantum-dark» (oscuro) o
«kvantum» (claro). Necesita Kvantum para Qt 6 (`qt6-style-kvantum` en Debian y Ubuntu). El tema global ya declara el
estilo; el instalador escribe además `~/.config/Kvantum/kvantum.kvconfig`.

## Actualizar

Sustituye las dos carpetas y vuelve a elegir el tema.

## Desinstalar

Elige otro estilo de aplicaciones y borra `~/.config/Kvantum/LliphiOscuro` y `~/.config/Kvantum/LliphiClaro`.
