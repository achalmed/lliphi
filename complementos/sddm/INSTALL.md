## Instalar

Es la única pieza que necesita root, y no forma parte del tema global ni del bloqueo de pantalla.

```bash
python3 herramientas/instalar.py sddm            # simula
python3 herramientas/instalar.py sddm --aplicar  # pide la contraseña con pkexec
```

Copia `lliphi/` a `/usr/share/sddm/themes/lliphi/` y escribe `/etc/sddm.conf.d/99-lliphi.conf` (`Current=lliphi` y la
tipografía Inter). No pisa nada que no sea suyo. Vista previa sin root:

```bash
sddm-greeter-qt6 --test-mode --theme generado/sddm/lliphi
```

## Actualizar

Vuelve a ejecutar `sddm --aplicar`.

## Desinstalar

Ejecuta el `UNDO.sh` que deja en `~/.local/state/lliphi/respaldos/<fecha>_sddm/` (con pkexec): SDDM vuelve al tema
anterior en el próximo inicio.
