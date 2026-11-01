"""Construir y desplegar: validación, construcción, pruebas, empaquetado, instalación en el escritorio real y
reversión. Cada tarjeta corre una orden de Lliphi; lo que escribe se simula primero y pide confirmación. No hay botón de
publicar ni de `git push`: eso queda al autor."""
from __future__ import annotations

import shutil

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidgetItem, QPushButton,
                               QTextBrowser, QVBoxLayout, QWidget)

from gui_comun.diseno import icono_trazo, variante
from gui_comun.widgets.tarjetas import ListaConVacio, Tarjeta, encabezado, pagina_desplazable, rejilla_pareja, seccion

from lliphi_studio import proyecto
from lliphi_studio.comun import Codigo, TarjetaOrden, nota


class Pagina:
    def __init__(self, v):
        self.v = v
        contenido = QWidget()
        raiz = QVBoxLayout(contenido)
        raiz.setSpacing(12)
        raiz.addWidget(encabezado("Construir y desplegar", "Paleta, construcción, validación, pruebas y empaquetado del "
                                  "proyecto; instalación en tu escritorio con el instalador reversible (respaldo y UNDO.sh) "
                                  "y la vuelta atrás. «Simular» no escribe nada."))
        raiz.addWidget(seccion("Proyecto"))
        r = rejilla_pareja(3)
        py = proyecto.orden
        self.sel_modulo = QComboBox()
        self.sel_modulo.addItem("todos los módulos", "")
        for m in proyecto.modulos():
            self.sel_modulo.addItem(f"{m.nombre} ({m.id})", m.id)
        tarjetas = []
        t = TarjetaOrden("Paleta", "Mide los 25 pares de contraste y los 16 colores de la terminal desde "
                         "<code>modulos/esquema/ajustes.json</code>; «Aplicar» reescribe <code>tokens/tokens.json</code>.", "paleta")
        t.boton("Simular", lambda: v.correr(py("paleta"), "Paleta (informe)"))
        t.boton("Aplicar", lambda: self._aplicar(py("paleta", "--aplicar"), "Paleta", "Reescribe tokens/tokens.json."), "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Construir", "Construye <code>generado/</code> y <code>sitio/generado/</code> desde los tokens y los "
                         "módulos; «Simular» dice qué archivos cambiarían.", "capas")
        t.extra.addWidget(self.sel_modulo, 1)
        t.boton("Simular", lambda: v.correr(py("generar", *self._modulos()), "Construir (simulación)"))
        t.boton("Aplicar", lambda: self._aplicar(py("generar", *self._modulos(), "--aplicar"), "Construir",
                                                 "Escribe generado/ (y sitio/generado/ si son todos)."), "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Verificar y validar", "Que lo versionado sea una construcción nueva (sin ediciones a mano) y que "
                         "cada módulo cumpla su contrato: manifiesto, dependencias, estructura de KDE e integración.", "verificar")
        t.boton("Verificar", lambda: v.correr(py("generar", "verificar"), "Verificar"))
        t.boton("Validar", lambda: v.correr(py("generar", "validar"), "Validar"), "primario")
        tarjetas.append(t)
        pytest = proyecto.raiz() / ".venv" / "bin" / "pytest"
        t = TarjetaOrden("Pruebas y licencias", "Las pruebas del proyecto (tokens, contraste, deriva, estructura, "
                         "instalación reversible en un HOME temporal) y <code>reuse lint</code>.", "verificar")
        t.boton("Pruebas", lambda: v.correr([str(pytest) if pytest.exists() else "pytest", "-q"], "Pruebas"), "primario")
        reuse = proyecto.raiz() / ".venv" / "bin" / "reuse"
        t.boton("Licencias", lambda: v.correr([str(reuse) if reuse.exists() else "reuse", "lint"], "reuse lint"))
        tarjetas.append(t)
        t = TarjetaOrden("Sitio", "Renderiza el sitio oficial con Quarto (<code>sitio/_site</code>) y lo abre en el navegador.", "globo")
        t.boton("Renderizar", lambda: v.correr(["quarto", "render", "sitio"], "Sitio (quarto render)"), "primario")
        t.boton("Abrir", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(proyecto.raiz() / "sitio" / "_site" / "index.html"))))
        tarjetas.append(t)
        t = TarjetaOrden("Empaquetar", "Un tarball por paquete, <code>SHA256SUMS</code>, notas y la ficha de la KDE Store en "
                         "<code>dist/</code> (fuera de git). Publicar la versión y subir a la tienda es del autor.", "paquete")
        t.boton("Ver ficha", self._ficha)
        t.boton("Empaquetar", lambda: self._aplicar(py("generar", "empaquetar"), "Empaquetar", "Reescribe dist/."), "primario")
        tarjetas.append(t)
        for i, t in enumerate(tarjetas):
            r.addWidget(t, i // 3, i % 3)
        raiz.addLayout(r)

        raiz.addWidget(seccion("Tu escritorio"))
        raiz.addWidget(nota("Esto sí toca tu sesión: copia a <code>~/.local/share</code> y <code>~/.config</code>, respalda "
                            "con SHA-256 lo que Plasma reescribe y deja un <code>UNDO.sh</code>. Para probar sin tocarla, usa "
                            "la <b>Vista en vivo</b> (sesión de prueba)."))
        r2 = rejilla_pareja(3)
        self.sel_variante = QComboBox()
        self.sel_variante.addItem("sin aplicar el tema", "")
        self.sel_variante.addItem("y aplicar Lliphi Oscuro", "oscuro")
        self.sel_variante.addItem("y aplicar Lliphi Claro", "claro")
        tarjetas = []
        t = TarjetaOrden("Instalar", "Copia lo generado a su sitio de KDE (nunca en <code>/usr</code>); con una variante, "
                         "además aplica el tema global y cada módulo en la sesión.", "descarga")
        t.extra.addWidget(self.sel_variante, 1)
        t.boton("Simular", lambda: v.correr(proyecto.orden("instalar", *self._modulos()), "Instalar (simulación)"))
        t.boton("Instalar", self._instalar, "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Comprobar", "Que lo instalado esté completo y sea de esta versión, que KDE reconozca cada paquete "
                         "(<code>kpackagetool6 --show</code>) y que existan los iconos, cursores y tipografías que nombra.", "verificar")
        t.boton("Estado", lambda: v.correr(proyecto.orden("instalar", "estado"), "Estado de la instalación"))
        t.boton("Comprobar", lambda: v.correr(proyecto.orden("instalar", "comprobar"), "Comprobar"), "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Dependencias de terceros", "Papirus (y el superpuesto de carpetas), los cursores WhiteSur y la "
                         "tipografía, descargados a tu usuario; sin root.", "enlace")
        t.boton("Simular", lambda: v.correr(proyecto.orden("instalar", "dependencias"), "Dependencias (simulación)"))
        t.boton("Instalar", lambda: self._aplicar(proyecto.orden("instalar", "dependencias", "--aplicar"), "Dependencias",
                                                  "Descarga de GitHub a ~/.local/share/icons y fonts."), "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Inicio de sesión (SDDM)", "El tema de SDDM va a <code>/usr/share/sddm/themes</code> con "
                         "<code>pkexec</code> (pide tu contraseña en el diálogo del sistema).", "candado")
        t.boton("Simular", lambda: v.correr(proyecto.orden("instalar", "sddm"), "SDDM (simulación)"))
        t.boton("Instalar", lambda: self._aplicar(proyecto.orden("instalar", "sddm", "--aplicar"), "SDDM",
                                                  "Escribe en /usr/share/sddm con pkexec."), "primario")
        tarjetas.append(t)
        t = TarjetaOrden("Desinstalar", "Retira lo que instaló Lliphi según su manifiesto (no lo de terceros). Para volver "
                         "exactamente a lo de antes, mejor el <code>UNDO.sh</code> de abajo.", "quitar")
        t.boton("Simular", lambda: v.correr(proyecto.orden("instalar", "desinstalar"), "Desinstalar (simulación)"))
        t.boton("Desinstalar", lambda: self._aplicar(proyecto.orden("instalar", "desinstalar", "--aplicar"), "Desinstalar",
                                                     "Borra lo instalado por Lliphi."), "peligro")
        tarjetas.append(t)
        for i, t in enumerate(tarjetas):
            r2.addWidget(t, i // 3, i % 3)
        raiz.addLayout(r2)

        raiz.addWidget(seccion("Respaldos y vuelta atrás"))
        tr = Tarjeta()
        tr.cuerpo.addWidget(nota("Cada instalación deja aquí una carpeta con lo que había antes (con sus sumas) y un "
                                 "<code>UNDO.sh</code> que lo repone y retira lo instalado. «Revertir» lo ejecuta."))
        self.lista_resp = ListaConVacio("No hay respaldos: Lliphi no se ha instalado con este usuario.")
        self.lista_resp.setMinimumHeight(180)
        tr.cuerpo.addWidget(self.lista_resp)
        fila = QHBoxLayout()
        fila.addStretch(1)
        b = QPushButton(icono_trazo("documento"), " Ver UNDO.sh")
        b.clicked.connect(self._ver_undo)
        fila.addWidget(b)
        b = QPushButton(icono_trazo("carpeta"), " Abrir carpeta")
        b.clicked.connect(lambda: self._sel() and QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._sel().carpeta))))
        fila.addWidget(b)
        b = variante(QPushButton(icono_trazo("volver"), " Revertir…"), "peligro")
        b.clicked.connect(self._revertir)
        fila.addWidget(b)
        tr.cuerpo.addLayout(fila)
        raiz.addWidget(tr)
        raiz.addStretch(1)
        self.widget = pagina_desplazable(contenido)
        self.al_cambiar_proyecto()

    def al_cambiar_proyecto(self) -> None:
        lista = self.lista_resp.lista
        lista.clear()
        for r in proyecto.respaldos():
            it = QListWidgetItem(icono_trazo("archivo"), f"{r.carpeta.name}\n{r.archivos} archivos · {r.carpeta}")
            it.setData(Qt.UserRole, r)
            lista.addItem(it)
        self.lista_resp.actualizar()

    def _modulos(self) -> list[str]:
        m = self.sel_modulo.currentData()
        return ["--modulos", m] if m else []

    def _aplicar(self, argv: list[str], nombre: str, que: str) -> None:
        if self.v.confirmar(nombre, f"{que}\n\n¿Seguir? («Simular» muestra antes qué haría.)"):
            self.v.correr(argv, nombre)

    def _instalar(self) -> None:
        variante_ = self.sel_variante.currentData()
        extra = ["--aplicar-tema", variante_] if variante_ else []
        texto = ("Copia Lliphi a tu usuario con respaldo y UNDO.sh" + (f" y APLICA Lliphi {variante_.capitalize()} a tu sesión "
                 "(tema global, colores, estilo, decoración, iconos, fondo, Kvantum)" if variante_ else "") + ".")
        self._aplicar(proyecto.orden("instalar", *self._modulos(), "--aplicar", *extra), "Instalar en tu escritorio", texto)

    def _sel(self):
        it = self.lista_resp.lista.currentItem()
        if it is None:
            self.v.marco.avisar("Elige un respaldo", "De la lista de respaldos.", "aviso")
            return None
        return it.data(Qt.UserRole)

    def _ver_undo(self) -> None:
        r = self._sel()
        if r:
            self._dialogo(f"UNDO.sh de {r.carpeta.name}", r.undo.read_text(encoding="utf-8", errors="replace"))

    def _revertir(self) -> None:
        r = self._sel()
        if r and self.v.confirmar("Revertir", f"Ejecuta {r.undo}: repone lo respaldado el {r.carpeta.name} y retira lo "
                                  "que Lliphi instaló entonces. Mira antes el UNDO.sh.\n\n¿Revertir?"):
            self.v.correr(["bash", str(r.undo)], f"Revertir {r.carpeta.name}")

    def _ficha(self) -> None:
        ficha = proyecto.raiz() / "dist" / "FICHA-KDE-STORE.md"
        if not ficha.exists():
            self.v.marco.avisar("Sin ficha", "Empaqueta primero (dist/ está fuera de git).", "aviso")
            return
        self._dialogo("Ficha de la KDE Store", ficha.read_text(encoding="utf-8"), markdown=True)

    def _dialogo(self, titulo: str, texto: str, markdown: bool = False) -> None:
        d = QDialog(self.v.ui)
        d.setWindowTitle(titulo)
        d.resize(820, 560)
        lay = QVBoxLayout(d)
        if markdown:
            w = QTextBrowser()
            w.setMarkdown(texto)
        else:
            w = Codigo(self.v.tokens)
            w.setPlainText(texto)
        lay.addWidget(w)
        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.rejected.connect(d.reject)
        lay.addWidget(bb)
        d.exec()
