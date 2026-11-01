"""Aplicación en Konsole (mejoras 5 y 9): el perfil por defecto toma el esquema de Lliphi y, si está instalada,
JetBrains Mono Nerd Font; lo demás del perfil no se toca. El perfil se respalda antes de instalar."""
from __future__ import annotations

from pathlib import Path

FUENTE_KONSOLE = "JetBrainsMono Nerd Font,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"   # mejora 9 (decisiones 4.14)


def perfil_konsole(data: Path, config: Path) -> Path | None:
    """El perfil por defecto de Konsole (`konsolerc` → [Desktop Entry] DefaultProfile), si existe en XDG_DATA_HOME."""
    rc = config / "konsolerc"
    if not rc.exists():
        return None
    grupo = None
    for linea in rc.read_text(encoding="utf-8", errors="ignore").splitlines():
        if linea.startswith("["):
            grupo = linea.strip()
        elif grupo == "[Desktop Entry]" and linea.startswith("DefaultProfile="):
            perfil = data / "konsole" / linea.split("=", 1)[1].strip()
            return perfil if perfil.exists() else None
    return None


def fijar_esquema_konsole(perfil: Path, esquema: str, fuente: str | None = None) -> None:
    """Mejora 5: escribe `ColorScheme=<esquema>` en [Appearance] y deja intacto lo demás (historial…). Mejora 9: con
    `fuente`, escribe también `Font=` (solo se pasa si la familia está instalada, para no perder los iconos del prompt).
    Se edita el archivo real: si el perfil es un enlace (dotfiles con stow) el enlace se conserva."""
    real = perfil.resolve()
    lineas = real.read_text(encoding="utf-8").splitlines()
    claves = {"ColorScheme": esquema, **({"Font": fuente} if fuente else {})}
    grupo, hechas, salida = None, set(), []
    for linea in lineas:
        if linea.startswith("["):
            if grupo == "[Appearance]":
                salida += [f"{k}={v}" for k, v in claves.items() if k not in hechas]; hechas |= set(claves)
            grupo = linea.strip()
        elif grupo == "[Appearance]" and (clave := linea.split("=", 1)[0]) in claves:
            linea = f"{clave}={claves[clave]}"; hechas.add(clave)
        salida.append(linea)
    if hechas != set(claves):
        if grupo == "[Appearance]":
            salida += [f"{k}={v}" for k, v in claves.items() if k not in hechas]
        else:
            salida += ["", "[Appearance]", *[f"{k}={v}" for k, v in claves.items()]]
    real.write_text("\n".join(salida) + "\n", encoding="utf-8")


def respaldos(ctx) -> list:
    perfil = perfil_konsole(ctx.DATA, ctx.CONFIG)
    return [(perfil, "reponer", f"perfil de Konsole {perfil.name}")] if perfil else []


def aplicar(ctx) -> int:
    if "konsole" not in ctx.modulos:
        return 0
    perfil = perfil_konsole(ctx.DATA, ctx.CONFIG)
    esquema_konsole = ctx.marca["nombre_esquema"][ctx.variante]
    if perfil and (ctx.DATA / "konsole" / f"{esquema_konsole}.colorscheme").exists():
        hay_mono = ctx.ejecutar(["fc-list", ":family=JetBrainsMono Nerd Font"]).stdout.strip() != ""
        fijar_esquema_konsole(perfil, esquema_konsole, FUENTE_KONSOLE if hay_mono else None)
        ctx.decir(f"Konsole: perfil {perfil.name} con el esquema {esquema_konsole}"
                  + (" y JetBrainsMono Nerd Font" if hay_mono else " (la fuente no se toca: falta JetBrainsMono Nerd Font)") + " (ventanas nuevas)")
    else:
        ctx.decir("Konsole: sin perfil por defecto propio; elige el esquema en Configurar Konsole → Perfiles")
    return 0
