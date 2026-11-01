"""El fondo sigue a la variante (decisiones 4.26): un programa pequeño que, al cambiar el esquema de color entre Lliphi
Claro y Lliphi Oscuro (con el tema global o a mano), pone en cada escritorio la imagen de la variante del mismo
paquete de fondo de Lliphi que el usuario tenga elegido; y su archivo de inicio automático, para que vigile desde que
empieza la sesión.

Plasma no cambia el fondo al aplicar un tema global, y con un paquete de imagen clara y oscura elige por los colores
del estilo de Plasma, que en Lliphi Claro declara su panel oscuro (decisiones 4.16): sin esto, el fondo se queda en la
variante anterior. La fuente es `seguir.py`, con marcas que se sustituyen al construir (`@DOMINIO@`, los ids de los
esquemas y el nombre). Se instala en `$XDG_DATA_HOME/lliphi/` y `$XDG_CONFIG_HOME/autostart/`."""
from __future__ import annotations

from pathlib import Path

from nucleo import escribir

FUENTE = Path(__file__).resolve().parent / "seguir.py"
PROGRAMA = "seguir-variante.py"
INICIO = "lliphi-fondo-variante.desktop"


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    texto = (FUENTE.read_text(encoding="utf-8").replace("@NOMBRE@", marca["nombre"]).replace("@DOMINIO@", marca["dominio_inverso"])
             .replace("@ESQUEMA_CLARO@", marca["id_esquema"]["claro"]).replace("@ESQUEMA_OSCURO@", marca["id_esquema"]["oscuro"]))
    escribir(destino / PROGRAMA, texto, hechos)
    (destino / PROGRAMA).chmod(0o755)
    escribir(destino / INICIO, "\n".join([
        "[Desktop Entry]", "Type=Application", f"Name={marca['nombre']}: el fondo sigue a la variante",
        f"Comment=Pone la imagen clara u oscura del fondo de {marca['nombre']} al cambiar entre {marca['nombre_esquema']['claro']} y {marca['nombre_esquema']['oscuro']}",
        # sin rutas de la máquina: la carpeta de datos se resuelve al arrancar
        f"Exec=sh -c 'exec python3 \"${{XDG_DATA_HOME:-$HOME/.local/share}}/{marca['id']}/{PROGRAMA}\" --vigilar'",
        "X-KDE-autostart-phase=2", "NoDisplay=true", "Terminal=false", ""]), hechos)
    return hechos
