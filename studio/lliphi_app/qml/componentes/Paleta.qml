// Paleta — los tokens de color de Lliphi (primitivas, semánticos y terminal, claro y oscuro) como DATOS del tema: cada
// muestra pinta su hex porque ese es el dato que se enseña; todo lo demás (texto, fondos, bordes) viste Kirigami.Theme.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

QQC2.ScrollView {
    id: pagina
    readonly property var grupos: destinos.paleta
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    Accessible.name: "Paleta de los tokens"
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.PlaceholderMessage { Layout.fillWidth: true; visible: pagina.grupos.length === 0; text: "Sin tokens"; explanation: "No se pudo leer tokens/tokens.json."; icon.name: "color-management" }
        QQC2.Label { Layout.fillWidth: true; visible: pagina.grupos.length > 0; wrapMode: Text.WordWrap; opacity: 0.8
                     text: "tokens/tokens.json: la fuente de verdad del color (OKLCH → hex). Los colores son del tema, no de esta ventana. Clic en una muestra copia su hex." }
        Repeater {
            model: pagina.grupos
            delegate: ColumnLayout {
                required property var modelData
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Heading { level: 4; text: modelData.titulo + " · " + modelData.colores.length }
                Flow {
                    Layout.fillWidth: true
                    spacing: Kirigami.Units.smallSpacing
                    Repeater {
                        model: modelData.colores
                        delegate: Rectangle {
                            id: muestra
                            required property var modelData
                            width: Kirigami.Units.gridUnit * 7
                            height: Kirigami.Units.gridUnit * 3.2
                            radius: Kirigami.Units.smallSpacing
                            color: modelData.hex                                  // el dato del token
                            border.width: 1
                            border.color: Kirigami.Theme.disabledTextColor
                            Accessible.name: modelData.nombre + " " + modelData.hex
                            Accessible.role: Accessible.Button
                            Rectangle {
                                anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
                                height: etiqueta.implicitHeight + Kirigami.Units.smallSpacing
                                color: Kirigami.Theme.backgroundColor
                                opacity: 0.92
                                radius: parent.radius
                                ColumnLayout {
                                    id: etiqueta
                                    anchors { left: parent.left; right: parent.right; leftMargin: Kirigami.Units.smallSpacing; rightMargin: Kirigami.Units.smallSpacing }
                                    spacing: 0
                                    QQC2.Label { Layout.fillWidth: true; text: muestra.modelData.nombre; elide: Text.ElideRight; font.bold: true }
                                    QQC2.Label { Layout.fillWidth: true; text: muestra.modelData.hex + "  " + muestra.modelData.oklch; elide: Text.ElideRight; font: Kirigami.Theme.smallFont; opacity: 0.8 }
                                }
                            }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: espacio.copiar(muestra.modelData.hex) }
                            QQC2.ToolTip.text: modelData.nombre + ": " + modelData.hex + " · " + modelData.oklch
                            QQC2.ToolTip.visible: zona.hovered
                            HoverHandler { id: zona }
                        }
                    }
                }
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
