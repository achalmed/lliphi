// BarraAreas — la barra lateral de un centro de configuración, como las Preferencias del sistema de KDE: cada área con
// su icono y cuántos destinos tiene; al pie, la versión de Lliphi y el estado de lo generado (la última verificación).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Rectangle {
    id: raiz
    readonly property var centro: studio.centro
    color: Kirigami.Theme.backgroundColor
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    implicitWidth: Kirigami.Units.gridUnit * 13

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        Kirigami.ListSectionHeader { text: "Apariencia de Lliphi"; Layout.fillWidth: true }
        Repeater {
            model: raiz.centro.areas
            delegate: QQC2.ItemDelegate {
                id: entrada
                required property var modelData
                required property int index
                Layout.fillWidth: true
                highlighted: raiz.centro.area === modelData.id
                text: modelData.titulo
                icon.name: modelData.icono
                onClicked: raiz.centro.fijarArea(modelData.id)
                Accessible.name: modelData.titulo + (modelData.cuantos ? ", " + modelData.cuantos + " destinos" : "")
                QQC2.ToolTip.text: modelData.que + " (Ctrl+" + ((index + 1) % 10) + ")"
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                contentItem: RowLayout {
                    spacing: Kirigami.Units.smallSpacing
                    Kirigami.Icon { source: entrada.modelData.icono; implicitWidth: Kirigami.Units.iconSizes.smallMedium; implicitHeight: implicitWidth }
                    QQC2.Label { text: entrada.modelData.titulo; elide: Text.ElideRight; Layout.fillWidth: true; color: entrada.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor }
                    QQC2.Label { visible: entrada.modelData.cuantos > 0; text: entrada.modelData.cuantos; color: entrada.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.disabledTextColor }
                }
            }
        }
        Item { Layout.fillHeight: true }
        Kirigami.Separator { Layout.fillWidth: true }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            spacing: 0
            QQC2.Label { text: "Lliphi " + studio.ajustes.version; font.bold: true }
            QQC2.Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "Última verificación de lo generado: " + studio.destinos.fechaVerificacion + " (Ctrl+T)"
                color: Kirigami.Theme.disabledTextColor
                font: Kirigami.Theme.smallFont
            }
        }
    }
}
