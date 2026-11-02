# Lliphi: los dieciséis colores ANSI de la terminal en la consola IPython de Spyder.
# GENERADO por herramientas/generar.py desde complementos/spyder; no editar.
#
# Spyder lo ejecuta al arrancar cada consola (Preferencias → Consola IPython → Inicio → «Ejecutar un archivo»). La
# consola (qtconsole) tiene sus colores ANSI fijos, pero atiende la secuencia OSC 4 de xterm, que cambia uno: aquí se
# escriben los dieciséis de la variante del esquema de sintaxis elegido en Spyder. Con un esquema que no sea de
# Lliphi no escribe nada. No deja nombres en el espacio de variables.


def _lliphi_consola():
    import configparser
    import os
    import sys

    colores = {"lliphi/claro": ["#db1a22", "#2640d3", "#067c75", "#637703", "#315bef", "#ae20e7", "#017b87", "#607275", "#c00115", "#1b29be", "#036963", "#546502", "#2a4fd0", "#9802cd", "#006872", "#4f6164"], "lliphi/oscuro": ["#2640d3", "#fe3762", "#20aba2", "#c8ed17", "#eb3131", "#bd37f7", "#2fbfcf", "#99adb0", "#223cbf", "#e73259", "#1c948c", "#a9c413", "#dd2e2e", "#aa32e1", "#2aaab8", "#819294"]}
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
