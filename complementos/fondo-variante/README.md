# El fondo y Konsole siguen a la variante (`fondo-variante`)

Al cambiar entre Lliphi Claro y Lliphi Oscuro, con el tema global de Preferencias del sistema o con el esquema de
color, Plasma no cambia el fondo; y con un paquete de imagen clara y oscura elegiría por los colores del estilo de
Plasma, que no siempre son los de la variante (hasta 4.32, Lliphi Claro declaraba su panel oscuro: decisiones 4.16).
Este complemento lo resuelve (decisiones 4.26):
un programa que escucha el aviso de KDE de cambio de colores (`org.kde.KGlobalSettings.notifyChange`) y pone en cada
escritorio la imagen de la variante (`contents/images/` o `contents/images_dark/`) **del mismo fondo de Lliphi que ya
tenga** (Horizonte, Forma, Relámpago o sus versiones firmadas), del mismo tamaño si lo hay. Si el esquema o el fondo
no son de Lliphi, no hace nada.

Konsole tampoco sigue a la variante: no tiene un esquema «del sistema». Si el perfil por defecto usa un esquema de
Lliphi, la vigilancia le pone el de la variante (`Lliphi Claro` u `Lliphi Oscuro`) para las ventanas nuevas y lo cambia
en las sesiones abiertas escribiendo en su terminal la secuencia de Konsole `ESC ] 50 ; ColorScheme=… BEL` (la misma
de `konsoleprofile`); un perfil con otro esquema no se toca (decisiones 4.28).

GTK 3 no tiene consultas de medios: si `~/.config/gtk-3.0/gtk.css` importa la hoja de una variante de Lliphi
(complemento `gtk`), la vigilancia cambia esa línea por la de la otra variante (aplicaciones GTK 3 nuevas) y pone
`color-scheme` de GSettings en `prefer-light` o `prefer-dark`; sin esa línea, GTK no se toca (decisiones 4.37). GTK 4,
libadwaita, GIMP (esquema «Sistema») y Calibre (paleta «del sistema») cambian solos.

Los programas que tampoco cambian solos (RStudio, Octave, Spyder) dejan cada uno un programa en `variante.d/`, junto a
`seguir-variante.py`: en cada cambio la vigilancia los ejecuta con la variante (`<programa>.py claro|oscuro --aplicar`;
sin `--aplicar` al simular) y cada uno decide si le toca (decisiones 5.43). Un programa nuevo no necesita tocar
`seguir.py`: basta con que su complemento instale el suyo en `{id}/variante.d/`.

Es un **complemento**: no es parte de un `Plasma/LookAndFeel`. Arquitectura: [`docs/arquitectura.md`](../../docs/arquitectura.md).

## Responsabilidad y formato

- `seguir.py`: la fuente del programa, con marcas (`@DOMINIO@`, los ids de los esquemas, el nombre) que sustituye
  `construir.py`; solo biblioteca estándar, con `kreadconfig6`, `qdbus6` y `dbus-monitor`. Simula por omisión;
  `--aplicar` cambia una vez; `--vigilar` cambia ahora y cada vez que KDE avisa.
- `construir.py`: escribe `seguir-variante.py` y el archivo de inicio automático `lliphi-fondo-variante.desktop`
  (que resuelve la carpeta de datos al arrancar, sin rutas de la máquina).
- `aplicar.py`: con `instalar.py --aplicar-tema`, pone ya la imagen de la variante y arranca la vigilancia (o la
  reinicia, para que corra el programa recién instalado).
- Se instala en `$XDG_DATA_HOME/lliphi/seguir-variante.py` y `$XDG_CONFIG_HOME/autostart/`; `desinstalar` los
  retira (la vigilancia en marcha termina al cerrar la sesión).

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos fondo-variante --aplicar
python3 ~/.local/share/lliphi/seguir-variante.py            # simula en la sesión: qué cambiaría
```

Pruebas: `test_fondo_sigue_a_la_variante`.
