# @NOMBRE@: los dieciséis colores ANSI de la terminal en la consola IPython de Spyder.
# GENERADO por herramientas/generar.py desde complementos/spyder; no editar.
#
# Spyder lo ejecuta al arrancar cada consola (Preferencias → Consola IPython → Inicio → «Ejecutar un archivo»). La
# consola (qtconsole) tiene sus colores ANSI fijos, pero atiende la secuencia OSC 4 de xterm, que cambia uno: aquí se
# escriben los dieciséis de la variante del esquema de sintaxis elegido en Spyder. Con un esquema que no sea de
# @NOMBRE@ no escribe nada. No deja nombres en el espacio de variables.


def _lliphi_consola():
    import configparser
    import os
    import sys

    colores = "@COLORES@"
    config = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    ini = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        ini.read(os.path.join(config, "spyder-py3", "config", "spyder.ini"), encoding="utf-8")
        elegido = ini.get("appearance", "selected", fallback="").strip().strip("'\"")
    except (OSError, configparser.Error):
        return
    if elegido not in colores:
        return
    # spyder-kernels envuelve `write` durante el arranque y antepone «Output from spyder call 'safe_exec'» a lo que se
    # imprime; las secuencias no se ven, así que se escriben con la función que el envoltorio guarda (`_write`)
    escribir = getattr(sys.stdout.write, "_write", sys.stdout.write)
    escribir("".join(f"\033]4;{i};rgb:{c[1:3]}/{c[3:5]}/{c[5:7]}\007" for i, c in enumerate(colores[elegido])))
    sys.stdout.flush()


_lliphi_consola()
del _lliphi_consola
