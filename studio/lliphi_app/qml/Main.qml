// Main.qml — Lliphi Studio: el tema Lliphi en un espacio de trabajo al estilo Dolphin/Kate sobre GuiComun.VentanaStudio.
// Navegación (Destinos por rol · Estado) · centro (la tabla de destinos) · detalles (Resumen, Paleta, Diferencias,
// Registro, Operación) · panel inferior (la salida de generar.py, instalar.py, paleta.py y sesion.py) · barra de
// estado. Los colores de Lliphi aparecen solo como datos del tema (la pestaña Paleta); la ventana viste Kirigami.Theme.
// Ninguna orden ni escritura aquí: todo lo hacen los controladores de Python (espacio, destinos, operaciones, ajustes).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaStudio {
    id: ventana

    readonly property var registro: accionesStudio
    readonly property var d: destinos
    readonly property var ops: operaciones

    title: (d.hayActual ? d.nombre : espacio.textoRol) + " — Lliphi Studio"
    acciones: registro
    tareas: tareasStudio
    consola: consolaStudio
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    resumen: espacio.resumen
    contexto: espacio.contexto
    claveAjustes: "ventana"

    function accion(nombre) { return registro.accion(nombre) }
    function irAPestana(i) { ventana.mostrarDetalles = true; detalles.pestanaActual = i }
    function religarNavegacion() { navegacion.actual = Qt.binding(() => espacio.nombreNavegacion) }

    Connections {
        target: interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "filtrar": filtro.forceActiveFocus(); filtro.selectAll(); break
            case "seleccionar_todo": tabla.seleccionarTodo(); break
            case "aplicar": dialogoAplicar.abrir(); break
            case "respaldos": dialogoRespaldos.open(); break
            case "sesion": dialogoSesion.open(); break
            case "venv": dialogoVenv.open(); break
            case "pestana": irAPestana(datos.indice); break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            case "aviso": ventana.mensajes.mostrar(datos.texto, datos.tipo || "informacion"); break
            }
        }
    }
    Connections { target: espacio; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } function onFiltroCambiado() { religarNavegacion() } }
    Connections {
        target: d
        function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) }
        function onSeleccionar(fila) { if (fila >= 0) tabla.seleccionarFila(fila, true) }
    }
    Connections {
        target: ops
        function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) }
        function onTerminada(id, aplicar, codigo) { if (id === "verificar" && d.hayActual) irAPestana(2); else if (!aplicar && ops.sobreDestino) irAPestana(3) }
    }

    // ------------------------------------------------------------------ barra: la operación y el filtro
    herramientasExtra: [
        QQC2.ComboBox {
            id: selectorOperacion
            Layout.preferredWidth: Kirigami.Units.gridUnit * 16
            model: ops.lista
            textRole: "titulo"
            currentIndex: ops.indiceActual
            onActivated: index => ops.fijarPorIndice(index)
            Accessible.name: "Operación"
            QQC2.ToolTip.text: ops.descripcion
            QQC2.ToolTip.visible: hovered && ops.descripcion !== ""
            Connections { target: ops; function onCambiado() { selectorOperacion.currentIndex = ops.indiceActual } }
        },
        Kirigami.SearchField {
            id: filtro
            Layout.preferredWidth: Kirigami.Units.gridUnit * 11
            placeholderText: "Filtrar (Ctrl+F)"
            onTextChanged: d.modelo.filtrar(text)
            Keys.onEscapePressed: { text = ""; tabla.forceActiveFocus() }
            Accessible.name: "Filtrar"
        }
    ]

    // ------------------------------------------------------------------ navegación
    navegacion: PanelNavegacion {
        id: navegacion
        secciones: [
            { titulo: "Destinos", filas: d.filasRoles },
            { titulo: "Estado", filas: d.filasEstados }
        ]
        onElegida: nombre => {
            if (nombre.startsWith("estado.")) espacio.fijarEstado(nombre.substring(7))
            else { espacio.fijarEstado(""); espacio.fijarRol(nombre.length > 4 ? nombre.substring(4) : "") }
            religarNavegacion()
        }
        Component.onCompleted: religarNavegacion()
    }

    // ------------------------------------------------------------------ centro: la tabla de destinos
    centro: TablaDatos {
        id: tabla
        modelo: d.modelo
        claveAjustes: "destinos"
        umbralEstrecho: Kirigami.Units.gridUnit * 48
        mensajeVacio: d.total === 0 ? "No se leyó ningún modulo.json: ¿es esta la raíz de Lliphi? (F6 relee)" : "Ningún destino cumple el filtro «" + espacio.textoFiltro + "»"
        iconoVacio: "preferences-desktop-theme-global"
        columnas: [
            { ancho: 0, minimo: 12, conIcono: true },
            { ancho: 7, secundaria: true, estrecho: true },
            { ancho: 6, secundaria: true, estrecho: true },
            { ancho: 8, secundaria: true, estrecho: true },
            { ancho: 5, alinear: "derecha", secundaria: true },
            { ancho: 8, semantica: true },
            { ancho: 8, semantica: true },
            { ancho: 10, mono: true, secundaria: true, estrecho: true }
        ]
        onOrdenar: (columna, descendente) => d.modelo.ordenar(columna, descendente)
        onFilaActualCambiada: fila => d.fijarFila(fila)
        onActivada: fila => { d.fijarFila(fila); irAPestana(0) }
        menuContextual: MenuAcciones {
            acciones: ventana.registro
            conAtajos: false
            elementos: [
                { tipo: "accion", nombre: "op.simular" }, { tipo: "accion", nombre: "op.aplicar" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "op.generar" }, { tipo: "accion", nombre: "op.instalar" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "archivo.ajustes" }, { tipo: "accion", nombre: "archivo.manifiesto" }, { tipo: "accion", nombre: "archivo.generado" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "destino.diferencias" }, { tipo: "accion", nombre: "destino.registro" }
            ]
        }
    }

    // ------------------------------------------------------------------ detalles
    detalles: PanelDetalles {
        id: detalles
        titulo: d.hayActual ? d.nombre : ""
        subtitulo: d.hayActual ? d.textoRol + " · " + d.resumenCorto : ""
        icono: d.icono
        mensajeVacio: "Elige un destino en la tabla: su resumen, la paleta de los tokens, sus diferencias y su registro"
        iconoVacio: "preferences-desktop-theme-global"
        accionesCabecera: [ventana.accion("op.simular"), ventana.accion("op.aplicar"), ventana.accion("archivo.generado")]
        pestanas: [
            { titulo: "Resumen" },
            { titulo: "Paleta", contador: d.paleta.length },
            { titulo: "Diferencias", contador: d.nDiferencias },
            { titulo: "Registro" },
            { titulo: "Operación" }
        ]
        Resumen {}
        Paleta {}
        Diferencias {}
        Registro {}
        Operacion {}
    }

    inferior: PanelInferior { consola: consolaStudio }

    // ------------------------------------------------------------------ diálogos
    Kirigami.PromptDialog {
        id: dialogoAplicar
        title: "Aplicar: " + ops.titulo
        subtitle: ops.textoConfirmacion
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [Kirigami.Action { text: ops.instala ? "Instalar o escribir, con respaldo" : "Aplicar"; icon.name: "dialog-ok-apply"; enabled: ops.puedeAplicar; onTriggered: { ops.aplicar(); dialogoAplicar.close() } }]
        function abrir() {
            if (!ops.puedeAplicar) { ventana.mensajes.mostrar(ops.motivoNoAplicar, "aviso"); return }
            open()
        }
    }
    Kirigami.PromptDialog {
        id: dialogoVenv
        title: "El entorno de las órdenes"
        subtitle: (ajustes.hayVenv ? "generar.py, instalar.py, sesion.py y paleta.py corren con " + ajustes.interprete + " (el .venv del proyecto, con coloraide); la ventana, con el Python del sistema."
                                   : "No existe el .venv del proyecto: las órdenes corren con el Python de la ventana y paleta.py (coloraide) fallará; lo demás no lo necesita.")
                  + "\n\nPara crearlo (sin sudo ni apt; PySide6 no va ahí):\n" + ajustes.ordenVenv
        standardButtons: Kirigami.Dialog.Close
        customFooterActions: [Kirigami.Action { text: "Copiar la orden"; icon.name: "edit-copy"; onTriggered: { espacio.copiar(ajustes.ordenVenv); dialogoVenv.close() } }]
    }
    DialogoRespaldos { id: dialogoRespaldos; onAplicar: dialogoAplicar.abrir() }
    DialogoSesion { id: dialogoSesion; onAplicar: dialogoAplicar.abrir() }
    dialogoAjustes: DialogoAjustesStudio {}
}
