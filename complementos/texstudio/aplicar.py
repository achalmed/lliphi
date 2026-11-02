"""Aplicación en TeXstudio: sustituye en `texstudio.ini` solo las secciones `[formats]` y `[formatsDark]` (los
formatos de resaltado) por las de Lliphi; lo demás del archivo queda byte a byte. El archivo se respalda antes de
instalar (`respaldos()`), y si es un enlace (dotfiles con stow) se escribe el archivo real y el enlace se conserva.

Con TeXstudio abierto no se toca: al cerrarse reescribiría el archivo con los formatos que tiene en memoria. Entonces
basta cerrarlo y volver a aplicar, o cargar `lliphi.txsprofile` desde Opciones → Cargar perfil…, que hace lo mismo."""
from __future__ import annotations

from pathlib import Path


def ini_texstudio(config: Path) -> Path:
    return config / "texstudio" / "texstudio.ini"


def fundir(texto: str, secciones: dict[str, list[str]]) -> str:
    """`texto` (un INI) con las secciones nombradas en `secciones` sustituidas por sus líneas (cabecera incluida); las
    que no estaban se añaden donde estaba la primera sustituida o, si no había ninguna, tras `[General]`."""
    lineas, salida, puesto, saltar = texto.splitlines(), [], False, False
    for linea in lineas:
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            nombre = linea.strip()[1:-1]
            saltar = nombre in secciones
            if saltar and not puesto:
                for s in secciones.values():
                    salida += s
                puesto = True
            if saltar:
                continue
        if not saltar:
            salida.append(linea)
    if not puesto:
        bloque = [x for s in secciones.values() for x in s]
        general = next((i for i, x in enumerate(salida) if x.strip() == "[General]"), None)
        if general is None:
            salida = bloque + salida
        else:
            fin = next((i for i in range(general + 1, len(salida)) if salida[i].startswith("[")), len(salida))
            salida = salida[:fin] + ([""] if fin and salida[fin - 1].strip() else []) + bloque + salida[fin:]
    return "\n".join(salida).rstrip("\n") + "\n"


def respaldos(ctx) -> list:
    ini = ini_texstudio(ctx.CONFIG)
    return [(ini, "reponer", "configuración de TeXstudio (texstudio.ini)")] if ini.exists() else []


def aplicar(ctx) -> int:
    if "texstudio" not in ctx.modulos:
        return 0
    ini = ini_texstudio(ctx.CONFIG)
    perfil = f"generado/texstudio/{ctx.marca['id']}.txsprofile"
    if not ini.exists():
        ctx.decir(f"TeXstudio: sin texstudio.ini (ábrelo una vez y ciérralo, o carga {perfil} desde Opciones → Cargar perfil…)")
        return 0
    if ctx.ejecutar(["pgrep", "-x", "texstudio"]).returncode == 0:
        ctx.decir(f"TeXstudio está abierto y reescribiría sus formatos al cerrarse: ciérralo y vuelve a aplicar, o carga {perfil} desde Opciones → Cargar perfil…")
        return 0
    construir = ctx.codigo("texstudio")
    real = ini.resolve()
    secciones = {construir.SECCION[v]: construir.seccion(ctx.tokens, ctx.marca, v) for v in ("claro", "oscuro")}
    real.write_text(fundir(real.read_text(encoding="utf-8"), secciones), encoding="utf-8")
    ctx.decir("TeXstudio: formatos de Lliphi Claro y Lliphi Oscuro en texstudio.ini (sigue a la variante al abrirlo)")
    return 0
