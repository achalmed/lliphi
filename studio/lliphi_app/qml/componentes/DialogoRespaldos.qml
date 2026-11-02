// DialogoRespaldos — «Respaldos y volver atrás…»: cada respaldo del instalador ($XDG_STATE_HOME/lliphi/respaldos/<fecha>)
// con sus archivos y su UNDO.sh; elegir uno fija la operación «Volver atrás con un respaldo»: F5 enseña el guion,
// Ctrl+Intro lo corre tras confirmar. Nada se borra desde aquí.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.Dialog {
    id: dialogo
    signal aplicar()
    title: "Respaldos del instalador"
    preferredWidth: Kirigami.Units.gridUnit * 36
    preferredHeight: Kirigami.Units.gridUnit * 22
    standardButtons: Kirigami.Dialog.Close
    readonly property var lista: destinos.respaldos
    customFooterActions: [
        Kirigami.Action { text: "Ver el UNDO.sh (F5)"; icon.name: "document-preview"; enabled: operaciones.respaldo !== ""; onTriggered: { operaciones.fijar("revertir"); operaciones.simular(); dialogo.close() } },
        Kirigami.Action { text: "Volver atrás…"; icon.name: "edit-undo"; enabled: operaciones.respaldo !== ""; onTriggered: { operaciones.fijar("revertir"); dialogo.close(); dialogo.aplicar() } }
    ]
    ColumnLayout {
        spacing: Kirigami.Units.smallSpacing
        QQC2.Label { Layout.fillWidth: true; Layout.margins: Kirigami.Units.largeSpacing; wrapMode: Text.WordWrap; opacity: 0.8
                     text: dialogo.lista.length === 0 ? "No hay respaldos: el instalador deja uno por cada instalación o desinstalación aplicada (instalar.py --aplicar)."
                                                      : "Elige un respaldo. Su UNDO.sh restaura byte a byte lo que esa instalación cambió y retira lo que puso; el respaldo queda." }
        ListView {
            id: vista
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: dialogo.lista
            currentIndex: -1
            delegate: QQC2.ItemDelegate {
                required property var modelData
                required property int index
                width: ListView.view.width
                highlighted: operaciones.respaldo === modelData.carpeta
                icon.name: "edit-undo"
                text: modelData.nombre + " · " + modelData.archivos + " archivo(s)"
                Accessible.name: "Respaldo " + modelData.nombre
                onClicked: { operaciones.fijarRespaldo(modelData.carpeta); vista.currentIndex = index }
                QQC2.ToolTip.text: modelData.carpeta
                QQC2.ToolTip.visible: hovered
            }
            Kirigami.PlaceholderMessage { anchors.centerIn: parent; width: parent.width - Kirigami.Units.largeSpacing * 4; visible: dialogo.lista.length === 0; text: "Sin respaldos"; icon.name: "edit-undo" }
        }
    }
}
