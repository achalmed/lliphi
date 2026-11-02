// Main.qml — Lliphi Studio (reingeniería 2026-11-02): un centro de configuración del escritorio sobre GuiComun.VentanaBase,
// con la forma de las Preferencias del sistema de KDE y no la de Dolphin. A la izquierda, las áreas (sistema de diseño,
// esquemas de color, Plasma, Kvantum, Konsole, editores, fondos, tipografía, iconos, otros destinos); a la derecha, la
// página del área elegida, cada una con lo suyo. Generar, instalar y desinstalar abren los seis pasos abajo; la salida,
// plegada (F4). Los colores de Lliphi aparecen solo como datos (la paleta, las maquetas); la ventana viste
// Kirigami.Theme. Ninguna orden ni escritura aquí: todo lo hacen los controladores de Python (studio.*).
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
    Component.onCompleted: registro.marcar("ver.salida", mostrarSalida)

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
            case "aviso": ventana.notificar(datos.texto, datos.tipo || "informacion"); break
            }
        }
    }
    Connections { target: studio.espacio; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.destinos; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.operaciones; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.centro; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }
    Connections { target: studio.escritura; function onAviso(texto, tipo) { ventana.notificar(texto, tipo) } }

    // ------------------------------------------------------------------ cabecera: el área, releer, verificar, la salida
    header: QQC2.ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: Kirigami.Units.smallSpacing
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

    // ------------------------------------------------------------------ áreas | página; debajo, los seis pasos y la salida
    QQC2.SplitView {
        anchors.fill: parent
        orientation: Qt.Vertical

        RowLayout {
            QQC2.SplitView.fillHeight: true
            spacing: 0
            BarraAreas { Layout.fillHeight: true }
            Kirigami.Separator { Layout.fillHeight: true }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: ventana.centro.area === "diseno" ? 0 : 1
                PaginaDiseno {}
                PaginaArea {}
            }
        }
        PanelPasos {
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
        contexto: studio.espacio.contexto
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
