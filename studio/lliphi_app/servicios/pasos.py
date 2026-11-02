"""studio/lliphi_app/servicios/pasos.py — generar, instalar y desinstalar en seis pasos visibles, sin Qt (reingeniería
2026-11-02, `docs/reingenieria.md` §3.2; la misma idea que Filesystem Studio):

    1 Plan          qué orden de Lliphi y sobre qué destinos
    2 Afectados     cada par origen → destino con su acción: crear, reemplazar, igual (no cambia), retirar, regenerar
    3 Conflictos    lo que bloquea (lo ajeno, lo que falta en generado/, una herramienta) y lo que se omite (una base que
                    no está); con un bloqueo no se ejecuta
    4 Ejecutar      la orden (`generar.py`/`instalar.py` con `--aplicar`), tras confirmar
    5 Verificar     aparte del éxito: cada destino quedó con la suma de lo generado, o se retiró; lo generado coincide
    6 Informe       el resultado en Markdown

El plan sale del núcleo (`pares_de`, `ajeno`, `comprobar_dependencias`, el manifiesto), cargado por ruta: lo mismo
que decidirá `instalar.py`.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from lliphi_app.servicios import areas, operaciones as ops, proyecto

TIPOS = {"instalar": "Instalar", "desinstalar": "Desinstalar", "generar": "Generar"}
ESTADO_OPERACION = {"instalar": "instalacion", "desinstalar": "eliminacion", "generar": "escritura"}


@dataclass
class Plan:
    tipo: str
    ids: list[str]
    descripcion: str
    orden: ops.Orden
    afectados: list[dict] = field(default_factory=list)      # {ruta, accion, detalle, nivel}
    conflictos: list[dict] = field(default_factory=list)     # {ruta, motivo, bloquea}
    hecho_en: float = field(default_factory=time.time)

    @property
    def titulo(self) -> str:
        return f"{TIPOS[self.tipo]} " + (", ".join(self.ids) if self.ids else "todo")

    @property
    def bloqueado(self) -> bool:
        return any(c["bloquea"] for c in self.conflictos)

    @property
    def cambian(self) -> int:
        return sum(a["accion"] not in ("igual",) for a in self.afectados)

    def como_dict(self) -> dict:
        return {"tipo": self.tipo, "titulo": self.titulo, "descripcion": self.descripcion, "orden": self.orden.texto(),
                "afectados": self.afectados, "conflictos": self.conflictos, "bloqueado": self.bloqueado, "cambian": self.cambian,
                "estadoOperacion": ESTADO_OPERACION[self.tipo]}


def _instalables(ids: list[str]) -> list[str]:
    return [m.id for m in proyecto.modulos() if m.clase == "paquete" and m.datos.get("instalacion")
            and (not ids or m.id in ids) and m.id not in ("sddm", "gtk")]


def planificar_instalar(ids: list[str]) -> Plan:
    ins = areas.instalacion_mod()
    seleccion = _instalables(ids)
    args = ["--modulos", ",".join(ids)] if ids else []
    plan = Plan("instalar", list(ids), "Copia lo generado a tu escritorio (~/.local/share y ~/.config). Antes respalda con su suma lo "
                "que cambia y deja UNDO.sh; anota cada ruta en el manifiesto.", ops.Orden(proyecto.orden("instalar", *args, "--aplicar"), proyecto.raiz()))
    for falta in ins.comprobar_dependencias(seleccion):
        plan.conflictos.append({"ruta": "", "motivo": f"falta {falta}", "bloquea": True})
    for id_ in seleccion:
        for par in areas.comparar(id_):
            accion, detalle, nivel = {"igual": ("igual", "ya está como lo generado: se vuelve a copiar idéntico", ""),
                                      "falta": ("crear", "", "positivo"),
                                      "distinto": ("reemplazar", "instalado por Lliphi y cambiado después: queda en el respaldo", "neutro"),
                                      "ajeno": ("no se toca", "", "negativo"),
                                      "sin_generar": ("no se puede", "", "negativo")}[par["estado"]]
            plan.afectados.append({"ruta": par["destinoCorto"], "origen": par["origenCorto"], "accion": accion, "detalle": detalle,
                                   "nivel": nivel, "destino": id_})
            if par["estado"] == "ajeno":
                plan.conflictos.append({"ruta": par["destinoCorto"], "motivo": "hay un archivo que Lliphi no instaló: instalar.py no lo toca "
                                        "y se detiene (retírelo usted o instale en otro usuario)", "bloquea": True})
            if par["estado"] == "sin_generar":
                plan.conflictos.append({"ruta": par["origenCorto"], "motivo": "falta en generado/: genere antes", "bloquea": True})
        _pares, omitidos = ins.pares_de([id_])
        for o in omitidos:
            plan.conflictos.append({"ruta": "", "motivo": o, "bloquea": False})
    if not seleccion:
        plan.conflictos.append({"ruta": "", "motivo": "ningún destino de la selección se instala con archivos propios", "bloquea": True})
    return plan


def planificar_desinstalar() -> Plan:
    ins = areas.instalacion_mod()
    plan = Plan("desinstalar", [], "Retira de tu escritorio lo que instaló Lliphi (lo que dice el manifiesto). El respaldo y su UNDO.sh "
                "quedan; las dependencias de terceros (Colloid, Papirus, cursores, tipografías) no se retiran.",
                ops.Orden(proyecto.orden("instalar", "desinstalar", "--aplicar"), proyecto.raiz()))
    if not ins.MANIFIESTO.exists():
        plan.conflictos.append({"ruta": "", "motivo": "no hay nada instalado por Lliphi (sin manifiesto)", "bloquea": True})
        return plan
    m = json.loads(ins.MANIFIESTO.read_text(encoding="utf-8"))
    for ruta, suma in m.get("rutas", {}).items():
        p = Path(ruta)
        cambiado = p.exists() and ins.sha_dir(p) != suma
        plan.afectados.append({"ruta": areas._corta(p), "origen": "", "accion": "retirar" if p.exists() else "ya no está",
                               "detalle": "cambiado después de instalar: se retira igual" if cambiado else "", "nivel": "negativo" if p.exists() else "",
                               "destino": ""})
    return plan


def planificar_generar(ids: list[str], verificacion=None) -> Plan:
    args = ["--modulos", ",".join(ids)] if ids else []
    plan = Plan("generar", list(ids), "Reescribe generado/ (y sitio/generado/) desde los tokens y los módulos. Es reversible con git.",
                ops.Orden(proyecto.orden("generar", *args, "--aplicar"), proyecto.raiz()))
    vigente = verificacion is not None and verificacion.vigente
    for m in proyecto.modulos():
        if ids and m.id not in ids:
            continue
        if m.clase not in ("paquete",) and m.id != "global":
            continue
        dif = (verificacion.diferencias.get(m.id) or []) if vigente else None
        if dif:
            for x in dif:
                plan.afectados.append({"ruta": f"generado/{m.id}/{x}", "origen": "", "accion": "cambia", "detalle": "según la última verificación",
                                       "nivel": "neutro", "destino": m.id})
        else:
            n = sum(1 for p in m.generado.rglob("*") if p.is_file()) if m.generado.is_dir() else 0
            plan.afectados.append({"ruta": f"generado/{m.id}/", "origen": "", "accion": "igual" if vigente else "regenerar",
                                   "detalle": (f"{n} archivo(s); la última verificación no ve cambios" if vigente else
                                               f"{n} archivo(s); sin una verificación vigente no se sabe cuáles cambian"),
                                   "nivel": "", "destino": m.id})
    if not plan.afectados:
        plan.conflictos.append({"ruta": "", "motivo": "nada que generar en la selección", "bloquea": True})
    return plan


def verificar_instalar(plan: Plan) -> tuple[bool, str]:
    """Cada destino del plan (salvo lo ajeno) tiene ahora la suma de lo generado."""
    malos = []
    for id_ in {a["destino"] for a in plan.afectados if a["accion"] in ("crear", "reemplazar", "igual")}:
        for par in areas.comparar(id_):
            if par["estado"] not in ("igual",):
                malos.append(par["destinoCorto"])
    return (not malos, f"{len(malos)} ruta(s) no coinciden con lo generado: {', '.join(malos[:3])}" if malos
            else f"{sum(a['accion'] in ('crear', 'reemplazar', 'igual') for a in plan.afectados)} ruta(s) con la suma de lo generado")


def verificar_desinstalar(plan: Plan) -> tuple[bool, str]:
    casa = str(proyecto.home())
    quedan = [a["ruta"] for a in plan.afectados if a["accion"] == "retirar" and Path(a["ruta"].replace("~", casa, 1)).exists()]
    sin_manifiesto = not areas.instalacion_mod().MANIFIESTO.exists()
    ok = not quedan and sin_manifiesto
    return ok, ("todo retirado y el manifiesto borrado" if ok else f"quedan {len(quedan)} ruta(s)" + ("" if sin_manifiesto else " y el manifiesto"))


def informe(plan: Plan, codigo: int, verificacion: tuple[bool, str] | None, duracion: float) -> str:
    lineas = [f"# {plan.titulo}", "", f"- fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}", f"- orden: `{plan.orden.texto()}`",
              f"- resultado: {'terminó bien' if codigo == 0 else f'falló (código {codigo})'} en {duracion:.1f} s",
              f"- verificación: {('pasa · ' if verificacion[0] else 'NO pasa · ') + verificacion[1] if verificacion else 'no se hizo'}", "",
              plan.descripcion, "", "## Afectados", "", "| ruta | acción | detalle |", "|---|---|---|"]
    lineas += [f"| `{a['ruta']}` | {a['accion']} | {a['detalle']} |" for a in plan.afectados] or ["| — | — | — |"]
    if plan.conflictos:
        lineas += ["", "## Conflictos y avisos", ""] + [f"- {'**bloquea**: ' if c['bloquea'] else ''}{c['ruta'] + ': ' if c['ruta'] else ''}{c['motivo']}" for c in plan.conflictos]
    return "\n".join(lineas) + "\n"
