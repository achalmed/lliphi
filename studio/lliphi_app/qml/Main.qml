// Main.qml — Lliphi Studio sobre GuiComun.VentanaBase: una mesa de diseño (rediseño del 2026-11-18, decisiones 5.51).
// A la izquierda, las rampas de color de los tokens (PanelRampas); a la derecha, la maqueta del escritorio pintada con
// ellos, en claro o en oscuro, que se repinta cuando cambian (Maqueta, tipo «escritorio»), o la página del área elegida
// (PaginaArea: su vista previa, sus destinos y lo instalado frente a lo generado); al pie, los destinos con su estado y
// «Generar lo que cambió» (PanelDestinos). Generar, instalar y desinstalar abren los seis pasos abajo; la salida, plegada
// (F4). Los colores de Lliphi aparecen solo como datos (las rampas, las maquetas); la ventana viste Kirigami.Theme.
// Avisos: lo efímero, a la barra de estado; lo demás, a las notificaciones de KDE (Mensajes de gui-comun). Ninguna orden
// ni escritura aquí: todo lo hacen los controladores de Python (studio.*).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtCore
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaBase {
    id: ventana

    readonly property var centro: studio.centro
    readonly property var registro: studio.acciones
    property bool mostrarSalida: false
    property bool mostrarPasos: false
    property alias pasoMostrado: panelPasos.paso
    // la variante que se mira en la mesa: la que se eligió o, mientras no se elija, la del escritorio (sigue su cambio en vivo)
    property string variante: ""
    readonly property bool escritorioOscuro: Kirigami.ColorUtils.brightnessForColor(Kirigami.Theme.backgroundColor) === Kirigami.ColorUtils.Dark
    readonly property string varianteVista: variante || (escritorioOscuro ? "oscuro" : "claro")
    readonly property var datosVariante: (centro.sistema.variantes || []).find(x => x.variante === ventana.varianteVista) || ({})
    // lo efímero va a la barra de estado (6 s); lo demás, a las notificaciones del escritorio
    property string pista: ""
    property double inicioTarea: 0
    function avisar(texto, tipo) {
        if (tipo === "informacion") { ventana.pista = texto; relojPista.restart() }
        else ventana.notificar(texto, tipo)
    }
    Timer { id: relojPista; interval: 6000; onTriggered: ventana.pista = "" }
    onVarianteVistaChanged: marcarVariante()
    function marcarVariante() {
        registro.marcar("ver.variante.claro", varianteVista === "claro")
        registro.marcar("ver.variante.oscuro", varianteVista === "oscuro")
    }

    title: (centro.datosArea.titulo || "Lliphi") + " — Lliphi Studio"
    width: 1360
    height: 900
    minimumWidth: 1000
    acciones: registro
    tareas: studio.tareas
    consola: studio.consola
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    claveAjustes: "ventana"

    Settings {
        category: "centro"
        property alias salida: ventana.mostrarSalida
    }
    onMostrarSalidaChanged: registro.marcar("ver.salida", mostrarSalida)
    Component.onCompleted: { registro.marcar("ver.salida", mostrarSalida); marcarVariante() }

    // ------------------------------------------------------------------ lo que Python pide a la interfaz
    Connections {
        target: studio.interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "salida": ventana.mostrarSalida = !ventana.mostrarSalida; break
            case "pasos": ventana.mostrarPasos = true; break
            case "respaldos": dialogoRespaldos.open(); break
            case "sesion": dialogoSesion.open(); break
            case "venv": dialogoVenv.open(); break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            case "aviso": ventana.avisar(datos.texto, datos.tipo || "informacion"); break
            case "variante": ventana.variante = datos.nombre || ""; ventana.marcarVariante(); break
            }
        }
    }
    Connections { target: studio.espacio; function onAviso(texto, tipo) { ventana.avisar(texto, tipo) } }
    Connections { target: studio.destinos; function onAviso(texto, tipo) { ventana.avisar(texto, tipo) } }
    Connections { target: studio.operaciones; function onAviso(texto, tipo) { ventana.avisar(texto, tipo) } }
    Connections { target: studio.centro; function onAviso(texto, tipo) { ventana.avisar(texto, tipo) } }
    Connections { target: studio.escritura; function onAviso(texto, tipo) { ventana.avisar(texto, tipo) } }
    // una tarea larga (más de 10 s) que termina con la ventana sin foco avisa en Plasma; las de escritura, instalación y
    // eliminación ya las avisa VentanaBase, y un fallo llega como error presentable
    Connections {
        target: studio.tareas
        function onIniciada(nombre) { ventana.inicioTarea = Date.now() }
        function onResultado(r) {
            const propia = !r.operacion || r.operacion === "lectura" || r.operacion === "simulacion"
            if (propia && r.nivel === "ok" && !ventana.active && ventana.inicioTarea && Date.now() - ventana.inicioTarea > 10000)
                ventana.notificar("Terminó: " + r.nombre.replace(/^(Ejecutando|Simulando): /, ""), "positivo")
        }
    }

    // ------------------------------------------------------------------ cabecera: el área, releer, verificar, la salida
    header: QQC2.ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: Kirigami.Units.smallSpacing
            QQC2.ToolButton {
                visible: ventana.centro.area !== "diseno"
                icon.name: "go-previous"
                text: "Mesa de diseño"
                onClicked: ventana.registro.accion("ver.area.diseno").disparar()
                Accessible.name: "Volver a la mesa de diseño"
                QQC2.ToolTip.text: "Las rampas, la maqueta del escritorio y los destinos (Ctrl+1)"
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
            }
            QQC2.ToolSeparator { visible: ventana.centro.area !== "diseno" }
            Kirigami.Icon { source: ventana.centro.datosArea.icono || "preferences-system"; implicitWidth: Kirigami.Units.iconSizes.smallMedium; implicitHeight: implicitWidth }
            QQC2.Label { text: ventana.centro.datosArea.titulo || ""; font.bold: true }
            Item { Layout.fillWidth: true }
            BotonAccion { accion: ventana.registro.accion("ver.releer"); conTexto: false }
            BotonAccion { accion: ventana.registro.accion("proyecto.verificar"); conTexto: true }
            BotonAccion { accion: ventana.registro.accion("proyecto.comprobar"); conTexto: true }
            QQC2.ToolSeparator {}
            BotonAccion { accion: ventana.registro.accion("ver.salida"); conTexto: false }
        }
    }

    // ------------------------------------------------------------------ la mesa: rampas | maqueta (o el área); al pie, los
    // destinos; debajo, los seis pasos y la salida
    QQC2.SplitView {
        anchors.fill: parent
        orientation: Qt.Vertical

        QQC2.SplitView {
            QQC2.SplitView.fillHeight: true
            orientation: Qt.Horizontal

            PanelRampas {
                QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 22
                QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 16
                v: ventana.datosVariante
                error: ventana.centro.sistema.error || ""
                onCopiado: hex => { studio.espacio.copiar(hex); ventana.avisar("Copiado " + hex, "informacion") }
            }
            StackLayout {
                QQC2.SplitView.fillWidth: true
                clip: true
                currentIndex: ventana.centro.area === "diseno" ? 0 : 1
                // la maqueta del escritorio, con el cambio de claro a oscuro
                ColumnLayout {
                    spacing: 0
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.margins: Kirigami.Units.largeSpacing
                        Layout.bottomMargin: 0
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            Kirigami.Heading { level: 2; text: "Maqueta del escritorio" }
                            QQC2.Label {
                                Layout.fillWidth: true
                                text: "Pintada con los tokens de " + (ventana.datosVariante.titulo || "") + "; se repinta al cambiar tokens.json. El escritorio no se toca."
                                color: Kirigami.Theme.disabledTextColor
                                elide: Text.ElideRight
                            }
                        }
                        QQC2.ButtonGroup { id: grupoVariante }
                        Repeater {
                            model: [["claro", "Claro", "weather-clear"], ["oscuro", "Oscuro", "weather-clear-night"]]
                            delegate: QQC2.ToolButton {
                                required property var modelData
                                text: modelData[1]
                                icon.name: modelData[2]
                                checkable: true
                                checked: ventana.varianteVista === modelData[0]
                                QQC2.ButtonGroup.group: grupoVariante
                                onClicked: ventana.registro.accion("ver.variante." + modelData[0]).disparar()
                                Accessible.name: "Maqueta en Lliphi " + modelData[1]
                            }
                        }
                    }
                    Maqueta {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Kirigami.Units.largeSpacing
                        tipo: "escritorio"
                        colores: ventana.datosVariante.maqueta || ({})
                        variante: ventana.datosVariante
                        escritorio: ventana.centro.sistema.escritorio || ({})
                        titulo: ventana.datosVariante.titulo || ""
                    }
                }
                PaginaArea {}
            }
        }
        PanelDestinos {
            QQC2.SplitView.preferredHeight: Kirigami.Units.gridUnit * 11
            QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 5
        }
        PanelPasos {
            id: panelPasos
            visible: ventana.mostrarPasos && studio.escritura.hayPlan
            QQC2.SplitView.preferredHeight: Kirigami.Units.gridUnit * 14
            QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 8
            onCerrar: ventana.mostrarPasos = false
        }
        PanelInferior {
            visible: ventana.mostrarSalida
            QQC2.SplitView.preferredHeight: Kirigami.Units.gridUnit * 9
            QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 5
            consola: studio.consola
            onCerrar: ventana.mostrarSalida = false
        }
    }

    footer: BarraEstado {
        resumen: studio.espacio.resumen
        contexto: ventana.pista || studio.espacio.contexto
        tareas: studio.tareas
        onProgresoPulsado: ventana.mostrarSalida = true
    }

    // ------------------------------------------------------------------ diálogos
    Kirigami.PromptDialog {
        id: dialogoVenv
        title: "El entorno de las órdenes"
        subtitle: (studio.ajustes.hayVenv ? "generar.py, instalar.py, sesion.py y paleta.py corren con " + studio.ajustes.interprete + " (el .venv del proyecto, con coloraide); la ventana, con el Python del sistema."
                                          : "No existe el .venv del proyecto: las órdenes corren con el Python de la ventana y paleta.py (coloraide) fallará; lo demás no lo necesita.")
                  + "\n\nPara crearlo (sin sudo ni apt; PySide6 no va ahí):\n" + studio.ajustes.ordenVenv
        standardButtons: Kirigami.Dialog.Close
        customFooterActions: [Kirigami.Action { text: "Copiar la orden"; icon.name: "edit-copy"; onTriggered: { studio.espacio.copiar(studio.ajustes.ordenVenv); dialogoVenv.close() } }]
    }
    DialogoRespaldos { id: dialogoRespaldos; onAplicar: ventana.registro.accion("op.aplicar").disparar() }
    DialogoSesion { id: dialogoSesion; onAplicar: ventana.registro.accion("op.aplicar").disparar() }
    dialogoAjustes: DialogoAjustesStudio {}
}
