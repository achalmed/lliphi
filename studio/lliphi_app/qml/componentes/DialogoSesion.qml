// DialogoSesion — «Sesión de prueba…»: el Plasma anidado de sesion.py. Estado (F5), arrancar (consume RAM y disco: pide
// confirmación con la orden exacta), recargar, capturar, cerrar; y las sesiones que quedaron en la caché con su peso,
// que se borran a mano (nunca desde aquí).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.Dialog {
    id: dialogo
    signal aplicar()
    title: "Sesión de prueba (Plasma anidado)"
    preferredWidth: Kirigami.Units.gridUnit * 36
    preferredHeight: Kirigami.Units.gridUnit * 24
    standardButtons: Kirigami.Dialog.Close
    readonly property var sesiones: destinos.sesiones
    function correr(id) { operaciones.fijar(id); dialogo.close(); operaciones.simular() }
    function aplicarOp(id) { operaciones.fijar(id); dialogo.close(); dialogo.aplicar() }
    function arrancar() { dialogo.close(); studio.acciones.accion("sesion.arrancar").disparar() }   // su acción, con su confirmación
    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing
        QQC2.Label { Layout.fillWidth: true; Layout.margins: Kirigami.Units.largeSpacing; wrapMode: Text.WordWrap; opacity: 0.8
                     text: "sesion.py arranca un kwin_wayland y un plasmashell anidados con su propio HOME en $XDG_CACHE_HOME/lliphi/sesiones/, instala ahí el tema y lo aplica: tu sesión real no se toca. Consume RAM (un Plasma entero) y deja cientos de MB por sesión. Variante: " + ajustes.variante + " (Ajustes)." }
        Kirigami.FormLayout {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            RowLayout {
                Kirigami.FormData.label: "Solo lee:"
                QQC2.Button { text: "Estado"; icon.name: "dialog-information"; enabled: !tareasStudio.activa; onClicked: dialogo.correr("sesion_estado"); Accessible.name: "Estado de la sesión de prueba" }
                QQC2.Button { text: "Capturar"; icon.name: "camera-photo"; enabled: !tareasStudio.activa; onClicked: dialogo.correr("sesion_capturar"); Accessible.name: "Capturar la sesión de prueba" }
                QQC2.Button { text: "Simular arranque"; icon.name: "system-run"; enabled: !tareasStudio.activa; onClicked: dialogo.correr("sesion_arrancar"); Accessible.name: "Simular el arranque" }
            }
            RowLayout {
                Kirigami.FormData.label: "Tras confirmar:"
                QQC2.Button { text: "Arrancar…"; icon.name: "window-new"; enabled: !tareasStudio.activa; onClicked: dialogo.arrancar(); Accessible.name: "Arrancar la sesión de prueba" }
                QQC2.Button { text: "Recargar…"; icon.name: "view-refresh"; enabled: !tareasStudio.activa; onClicked: dialogo.aplicarOp("sesion_recargar"); Accessible.name: "Recargar la sesión de prueba" }
                QQC2.Button { text: "Cerrar…"; icon.name: "window-close"; enabled: !tareasStudio.activa; onClicked: dialogo.aplicarOp("sesion_cerrar"); Accessible.name: "Cerrar la sesión de prueba" }
            }
        }
        Kirigami.Heading { level: 4; Layout.leftMargin: Kirigami.Units.largeSpacing; text: "Sesiones en la caché · " + dialogo.sesiones.length }
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: dialogo.sesiones
            delegate: QQC2.ItemDelegate {
                required property var modelData
                width: ListView.view.width
                icon.name: "folder"
                text: modelData.nombre + " · " + modelData.peso
                Accessible.name: "Sesión " + modelData.nombre
                onClicked: espacio.abrirDolphin(modelData.carpeta)
                QQC2.ToolTip.text: modelData.carpeta + " (se borra a mano si ya no hace falta)"
                QQC2.ToolTip.visible: hovered
            }
            Kirigami.PlaceholderMessage { anchors.centerIn: parent; width: parent.width - Kirigami.Units.largeSpacing * 4; visible: dialogo.sesiones.length === 0; text: "Ninguna sesión en la caché"; icon.name: "window-new" }
        }
    }
}
