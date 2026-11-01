# Inicio de sesión (SDDM) (`sddm`)

La pantalla de inicio de sesión, derivada de WhiteSur-dark (que deriva de Breeze): fondo de Lliphi, acento en el foco
del campo, Inter. **No es la pantalla de bloqueo** (esa es de Plasma, módulo `carga-bloqueo`) ni parte del tema
global: la dibuja el saludador de SDDM, fuera de la sesión del usuario.

Es un **complemento**: existía antes de la reingeniería y se conserva fuera del tema global, porque no es parte de un
`Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- Formato: tema de SDDM (`metadata.desktop` con `[SddmGreeterTheme]`, `Main.qml`, `theme.conf`) en
  `/usr/share/sddm/themes/lliphi/`, más `/etc/sddm.conf.d/99-lliphi.conf`.
- `instalar_sddm.py`: la única pieza con root (un solo `pkexec`); no pisa nada que no sea suyo y deja `UNDO.sh`. Se
  llama con `python3 herramientas/instalar.py sddm [--aplicar]` (o el atajo `herramientas/instalar_sddm.py`).
- Construcción: `fondos` (la imagen) y la base WhiteSur-kde; sustituciones protegidas por `assert`.
- Vista previa sin root: `sddm-greeter-qt6 --test-mode --theme generado/sddm/lliphi`. Lo generado: `generado/sddm/lliphi/`.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos sddm --aplicar
python3 herramientas/instalar.py sddm                 # simula la instalación (con root: --aplicar)
```

Pruebas: `test_inicio_de_sesion_sddm`.
