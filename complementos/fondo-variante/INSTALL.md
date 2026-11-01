# Instalar «el fondo sigue a la variante»

## Instalar a mano

```bash
mkdir -p ~/.local/share/lliphi ~/.config/autostart
cp seguir-variante.py ~/.local/share/lliphi/
cp lliphi-fondo-variante.desktop ~/.config/autostart/
python3 ~/.local/share/lliphi/seguir-variante.py --vigilar &   # o cierra y abre la sesión
```

## Actualizar

Sustituye los dos archivos y vuelve a arrancar la vigilancia (o la sesión).

## Desinstalar

Borra `~/.local/share/lliphi/seguir-variante.py` y `~/.config/autostart/lliphi-fondo-variante.desktop`; la vigilancia
en marcha termina al cerrar la sesión (o con `pkill -f seguir-variante.py`).
