"""Lo que la disposición pone en riesgo y hay que respaldar antes de instalar: si al aplicar el tema se reemplaza la
disposición y desaparece el widget de notas, Plasma borra su archivo (incidente del 2026-10-18; `estado.md`). Las
notas se respaldan siempre y `UNDO.sh` repone las que falten sin pisar las que existan. La disposición en sí la
aplica Plasma desde el tema global, solo si el usuario la pide."""
from __future__ import annotations


def respaldos(ctx) -> list:
    notas = ctx.DATA / "plasma_notes"
    cuantas = sum(1 for _ in notas.iterdir()) if notas.is_dir() else 0
    return [(notas, "completar", f"notas de Plasma ({cuantas})")]
