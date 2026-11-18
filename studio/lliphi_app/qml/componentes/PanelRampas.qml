// PanelRampas — la columna izquierda de la mesa de diseño (rediseño del 2026-11-18): las rampas de color de
// tokens/tokens.json de la variante que se mira (los neutros por luminosidad con el paso de L entre vecinos, el acento y
// sus variantes, los estados, los 16 ANSI), los semánticos que pinta la maqueta y los contrastes WCAG con su veredicto.
// Cada cuadro MUESTRA un token (es un dato: `color: m.hex`, y el texto encima, el negro o el blanco que más contrasta,
// calculado en servicios/diseno.py); el cromo del panel viste Kirigami.Theme. Un clic en un cuadro copia su hex. Editar
// es abrir los ajustes de la paleta y correr paleta.py: la maqueta se repinta sola al cambiar los tokens.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: raiz
    property var v: ({})                    // la variante (servicios/diseno.py)
    property string error: ""
    readonly property var registro: studio.acciones
    readonly property color borde: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, Kirigami.Theme.frameContrast)
    signal copiado(string hex)

    clip: true
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff

    ColumnLayout {
        width: raiz.availableWidth
        spacing: Kirigami.Units.smallSpacing

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            Layout.bottomMargin: 0
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0
                Kirigami.Heading { level: 3; text: "Tokens" }
                QQC2.Label {
                    Layout.fillWidth: true
                    text: (raiz.v.titulo || "") + (raiz.v.acento ? " · acento " + raiz.v.acento : "")
                    color: Kirigami.Theme.disabledTextColor
                    elide: Text.ElideRight
                }
            }
            BotonAccion { accion: raiz.registro.accion("archivo.esquema"); conTexto: false }
            BotonAccion { accion: raiz.registro.accion("op.paleta"); conTexto: false }
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            visible: raiz.error !== ""
            type: Kirigami.MessageType.Error
            text: "No se pudieron leer los tokens: " + raiz.error
        }

        Seccion { texto: "Neutros, de oscuro a claro (L de OKLCH)" }
        Rampa { muestras: raiz.v.neutros || []; conPaso: true }
        Seccion { texto: "Acento y sus variantes" }
        Rampa { muestras: raiz.v.acentos || [] }
        Seccion { texto: "Estados" }
        Rampa { muestras: raiz.v.estados || [] }
        Seccion { texto: "Terminal: los 16 ANSI" }
        Rampa { muestras: (raiz.v.ansi || []).slice(0, 8); corto: true }
        Rampa { muestras: (raiz.v.ansi || []).slice(8, 16); corto: true }

        Seccion { texto: "Semánticos (lo que pinta la maqueta)" }
        Repeater {
            model: raiz.v.semanticos || []
            delegate: QQC2.ItemDelegate {
                id: fila
                required property var modelData
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.smallSpacing
                Layout.rightMargin: Kirigami.Units.smallSpacing
                topPadding: 0
                bottomPadding: 0
                onClicked: raiz.copiado(modelData.hex)
                Accessible.name: modelData.nombre + " " + modelData.hex + ": copiar el hex"
                QQC2.ToolTip.text: modelData.oklch + " · clic: copiar " + modelData.hex
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                contentItem: RowLayout {
                    spacing: Kirigami.Units.smallSpacing
                    Rectangle {
                        Layout.preferredWidth: Kirigami.Units.iconSizes.small
                        Layout.preferredHeight: Kirigami.Units.iconSizes.small
                        color: fila.modelData.hex
                        border.width: 1
                        border.color: raiz.borde
                    }
                    QQC2.Label { text: fila.modelData.nombre; elide: Text.ElideRight; Layout.fillWidth: true }
                    QQC2.Label { text: fila.modelData.hex; font: Kirigami.Theme.fixedWidthFont; color: Kirigami.Theme.disabledTextColor }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Seccion { texto: "Contrastes WCAG 2.x"; Layout.fillWidth: true }
            EtiquetaNivel {
                Layout.rightMargin: Kirigami.Units.largeSpacing
                visible: text !== ""
                text: (raiz.v.fallan || 0) ? raiz.v.fallan + " no llegan" : (raiz.v.contrastes || []).length ? "todos cumplen" : ""
                nivel: (raiz.v.fallan || 0) ? "negativo" : "positivo"
            }
        }
        QQC2.Label {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            text: "Texto: AA ≥ 4,5 · AAA ≥ 7. Controles y foco: ≥ 3."
            color: Kirigami.Theme.disabledTextColor
            font: Kirigami.Theme.smallFont
            wrapMode: Text.WordWrap
        }
        Repeater {
            model: raiz.v.contrastes || []
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.largeSpacing
                Layout.rightMargin: Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.smallSpacing
                Rectangle {
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 2.4
                    Layout.preferredHeight: Kirigami.Units.gridUnit * 1.4
                    color: modelData.hexFondo
                    border.width: 1
                    border.color: raiz.borde
                    Accessible.role: Accessible.Graphic
                    Accessible.name: modelData.frente + " sobre " + modelData.fondo
                    Text { anchors.centerIn: parent; text: "Aa"; color: modelData.hexFrente; font.bold: true }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    QQC2.Label { text: modelData.que; elide: Text.ElideRight; Layout.fillWidth: true }
                    QQC2.Label {
                        text: modelData.textoRazon + " · " + modelData.frente + " sobre " + modelData.fondo
                        color: Kirigami.Theme.disabledTextColor
                        font: Kirigami.Theme.smallFont
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
                EtiquetaNivel { visible: text !== ""; text: modelData.veredicto.replace(" (sin requisito)", ""); nivel: modelData.nivel }
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }

    component Seccion: Kirigami.ListSectionHeader {
        property string texto: ""
        text: texto
        Layout.fillWidth: true
    }

    // una rampa: los cuadros seguidos, sin espacio entre ellos, como una escala; dentro, el nombre corto y la L (o el
    // número del color ANSI); al pasar, el nombre, el hex, el OKLCH y el paso de L; un clic copia el hex
    component Rampa: Rectangle {
        id: rampa
        property var muestras: []
        property bool conPaso: false
        property bool corto: false
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.largeSpacing
        Layout.preferredHeight: Kirigami.Units.gridUnit * (corto ? 1.6 : 2.6)
        visible: muestras.length > 0
        color: "transparent"
        border.width: 1
        border.color: raiz.borde
        Row {
            anchors.fill: parent
            anchors.margins: 1
            Repeater {
                model: rampa.muestras
                delegate: Rectangle {
                    id: cuadro
                    required property var modelData
                    required property int index
                    width: parent.width / Math.max(1, rampa.muestras.length)
                    height: parent.height
                    color: modelData.hex
                    Accessible.role: Accessible.Button
                    Accessible.name: modelData.nombre + " " + modelData.hex + (modelData.oklch ? " " + modelData.oklch : "") + ": copiar el hex"
                    Column {
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        anchors.margins: Kirigami.Units.smallSpacing / 2
                        Text {
                            text: rampa.corto ? cuadro.modelData.nombre.replace("color", "") : cuadro.modelData.nombre.replace(/^(neutro|acento)-?/, "") || cuadro.modelData.nombre
                            color: cuadro.modelData.texto
                            font: Kirigami.Theme.smallFont
                            width: cuadro.width - Kirigami.Units.smallSpacing
                            elide: Text.ElideRight
                        }
                        Text {
                            visible: !rampa.corto && cuadro.modelData.l >= 0
                            text: cuadro.modelData.l >= 0 ? cuadro.modelData.l.toFixed(2) : ""
                            color: cuadro.modelData.texto
                            font: Kirigami.Theme.smallFont
                            width: cuadro.width - Kirigami.Units.smallSpacing
                            elide: Text.ElideRight
                        }
                    }
                    MouseArea {
                        id: zona
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: raiz.copiado(cuadro.modelData.hex)
                    }
                    QQC2.ToolTip.visible: zona.containsMouse
                    QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                    QQC2.ToolTip.text: cuadro.modelData.nombre + " · " + cuadro.modelData.hex
                                       + (cuadro.modelData.oklch ? " · " + cuadro.modelData.oklch : "")
                                       + (rampa.conPaso && cuadro.index > 0 ? " · ΔL " + (cuadro.modelData.paso > 0 ? "+" : "") + cuadro.modelData.paso.toFixed(3) : "")
                }
            }
        }
    }
}
