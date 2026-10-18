## Instalar a mano

```bash
kpackagetool6 -t Plasma/Theme -i lliphi
plasma-apply-desktoptheme lliphi
```

El estilo no trae `colors`: toma los colores del esquema activo. Con Lliphi Oscuro es casi negro; con Lliphi Claro, gris suave; con cualquier otro esquema, el de ese esquema, y el acento del sistema manda en la selección y el foco.

## Actualizar

```bash
kpackagetool6 -t Plasma/Theme -u lliphi
```

Si tras actualizar ves el estilo viejo, cierra la sesión y vuelve a entrar: Plasma guarda los SVG en caché por versión.

## Desinstalar

```bash
plasma-apply-desktoptheme default
kpackagetool6 -t Plasma/Theme -r lliphi
```
