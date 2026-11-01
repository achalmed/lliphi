"""studio/tests/test_ventana.py — la ventana de Lliphi Studio: se construye con todas sus secciones, navega y las
secciones leen la copia del proyecto (conftest.py)."""
from __future__ import annotations

from lliphi_studio import ventana


def test_la_ventana_y_sus_secciones(lliphi, app):
    v = ventana.Ventana()
    ids = [p[0] for p in ventana.PAGINAS if p[0] in v.paginas]
    assert v._page_order == ids and {"dashboard", "despliegue"} <= set(ids)
    for id_ in ids:
        v.navigate(id_)
        assert v.ui.stack.currentWidget() is v.controllers[id_].widget
    assert v.ui.windowTitle().startswith("Lliphi Studio")
    esperar(v, app)
    v.ui.close()


def esperar(v, app, segundos: float = 90) -> None:
    """Que terminen las lecturas en segundo plano antes de cerrar (un QThread vivo al salir aborta)."""
    import time
    fin = time.monotonic() + segundos
    while any(w.isRunning() for w in v._workers) and time.monotonic() < fin:
        app.processEvents()
        time.sleep(0.05)
