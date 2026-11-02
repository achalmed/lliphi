# GNU Octave: instalar, actualizar y desinstalar

Octave tiene que haberse abierto al menos una vez (su asistente de bienvenida crea `~/.config/octave/octave-gui.ini`):
sin ese archivo el programa no crea nada y lo dice.

## Instalar

1. Cierra Octave (no es imprescindible: el cambio se ve al abrirlo de nuevo).
2. Con el instalador de Lliphi, que respalda antes `octave-gui.ini` (simula sin `--aplicar`):

```bash
python3 herramientas/instalar.py --modulos octave --aplicar --aplicar-tema oscuro
```

   `--aplicar-tema` aplica también el tema global de Plasma. Si solo quieres Octave, instala el programa y ejecútalo:

```bash
python3 herramientas/instalar.py --modulos octave --aplicar
cp ~/.config/octave/octave-gui.ini ~/.config/octave/octave-gui.ini.antes      # tu copia
python3 ~/.local/share/lliphi/variante.d/octave.py oscuro --colores            # simula: dice qué cambiaría
python3 ~/.local/share/lliphi/variante.d/octave.py oscuro --colores --aplicar
```

3. Abre Octave. En Edit → Preferences (Editar → Preferencias), las casillas «Second color mode (light/dark)» de
   «Editor Styles», «Command Window Colors», «Variable Editor Colors» y «Workspace» quedan marcadas en el oscuro y
   desmarcadas en el claro: el programa las deja así.

## Seguir al claro y al oscuro

Octave no sigue al escritorio: el modo de color se elige a mano en Preferences, con esas cuatro casillas «Second
color mode». Con Lliphi:

- **Automático:** instala también `fondo-variante`. En cada cambio de variante su vigilancia ejecuta
  `~/.local/share/lliphi/variante.d/octave.py <variante> --aplicar`, que cambia los cuatro interruptores si los colores
  son de Lliphi (con otros colores no toca nada). Se ve al abrir Octave de nuevo.
- **A mano:** `python3 ~/.local/share/lliphi/variante.d/octave.py claro --aplicar` (o `oscuro`), o las casillas de
  Preferencias.

## Actualizar

Vuelve a ejecutar el paso 2: el programa reemplaza los colores de Lliphi por los nuevos y conserva lo demás.

## Desinstalar

Los colores se quitan desde Octave: en Preferences, el botón «Reload default colors» (o «Reload default styles» en
«Editor Styles») de cada una de las cuatro secciones, en cada modo; o devuelve tu copia (`octave-gui.ini.antes`), o
ejecuta el `UNDO.sh` del respaldo del instalador, que restaura `octave-gui.ini` tal como estaba.
