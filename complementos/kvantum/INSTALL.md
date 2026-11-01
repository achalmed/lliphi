## Instalar a mano

```bash
mkdir -p ~/.config/Kvantum
cp -r Lliphi ~/.config/Kvantum/
kvantummanager --set Lliphi                             # una vez: la variante la elige el estilo
```

Y en Preferencias del sistema → Colores y temas → Estilo de las aplicaciones, elige «kvantum-dark» (oscuro) o
«kvantum» (claro). Necesita Kvantum para Qt 6 (`qt6-style-kvantum` en Debian y Ubuntu). El tema global ya declara el
estilo; el instalador escribe además `~/.config/Kvantum/kvantum.kvconfig`.

## Actualizar

Sustituye la carpeta `Lliphi`.

## Desinstalar

Elige otro estilo de aplicaciones y borra `~/.config/Kvantum/Lliphi` (y, de versiones anteriores, `LliphiOscuro` y `LliphiClaro`).
