"""Aplicación de Kvantum: tema activo en `Kvantum/kvantum.kvconfig` y estilo de widgets en `kdeglobals`."""
from __future__ import annotations


def aplicar(ctx) -> int:
    kvdir = ctx.CONFIG / "Kvantum"
    if "kvantum" in ctx.modulos and kvdir.exists():
        tema_kv = ctx.marca["id_esquema"][ctx.variante]
        (kvdir / "kvantum.kvconfig").write_text(f"[General]\ntheme={tema_kv}\n", encoding="utf-8")
        for grupo, claves in ctx.codigo("kvantum").valores(ctx.marca, ctx.variante).items():
            for clave, valor in claves.items():
                ctx.kwrite("kdeglobals", [grupo.split("][")[1]], clave, valor)
        ctx.decir(f"Kvantum: tema {tema_kv}, estilo kvantum")
    return 0
