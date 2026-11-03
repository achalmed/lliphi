// PaginaDiseno — el sistema de diseño con su color real: claro y oscuro LADO A LADO, cada uno con la maqueta de una
// ventana pintada con sus tokens, la escala de neutros (muestras grandes con L, C, H y hex, y el paso de L entre
// vecinas), el acento y sus variantes, los estados, los 16 colores ANSI y los contrastes WCAG de los pares que importan
// con su veredicto. Todo sale de studio.centro.sistema (servicios/diseno.py, desde tokens/tokens.json): los colores son
// datos; la página viste Kirigami.Theme. Editar es abrir los ajustes de la paleta y correr paleta.py (docs/reingenieria.md §3.4).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: raiz
    readonly property var sistema: studio.centro.sistema
    readonly property var registro: studio.acciones
    clip: true
    contentWidth: availableWidth

    ColumnLayout {
        width: raiz.availableWidth
        spacing: Kirigami.Units.largeSpacing

        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            Layout.bottomMargin: 0
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0
                Kirigami.Heading { level: 1; text: "Sistema de diseño" }
                QQC2.Label {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    color: Kirigami.Theme.disabledTextColor
                    text: "Los tokens (tokens/tokens.json) son la única fuente: la escribe paleta.py desde las ternas OKLCH de modulos/esquema/ajustes.json y de ella sale todo lo generado."
                }
            }
            BotonAccion { accion: raiz.registro.accion("archivo.esquema"); conTexto: true }
            BotonAccion { accion: raiz.registro.accion("op.paleta"); conTexto: true }
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            visible: !!raiz.sistema.error
            type: Kirigami.MessageType.Error
            text: "No se pudieron leer los tokens: " + (raiz.sistema.error || "")
        }

        // claro y oscuro, lado a lado
        GridLayout {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing
            Layout.rightMargin: Kirigami.Units.largeSpacing
            columns: raiz.availableWidth > Kirigami.Units.gridUnit * 50 ? 2 : 1
            columnSpacing: Kirigami.Units.largeSpacing * 2
            rowSpacing: Kirigami.Units.largeSpacing
            Repeater {
                model: raiz.sistema.variantes || []
                delegate: ColumnaVariante { required property var modelData; v: modelData; Layout.fillWidth: true; Layout.alignment: Qt.AlignTop }
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }

    component ColumnaVariante: ColumnLayout {
        id: col
        property var v: ({})
        spacing: Kirigami.Units.smallSpacing
        RowLayout {
            Kirigami.Heading { level: 2; text: col.v.titulo || "" }
            EtiquetaNivel { visible: text !== ""; text: "acento " + (col.v.acento || ""); icono: "color-picker" }
            EtiquetaNivel {
                visible: text !== ""; text: (col.v.fallan || 0) ? col.v.fallan + " par(es) no llegan" : "todos los pares cumplen"
                nivel: (col.v.fallan || 0) ? "negativo" : "positivo"
            }
        }
        Maqueta { Layout.fillWidth: true; Layout.preferredHeight: Kirigami.Units.gridUnit * 14; colores: col.v.maqueta; titulo: col.v.titulo || "" }

        Kirigami.ListSectionHeader { text: "Neutros, de oscuro a claro (L de OKLCH)"; Layout.fillWidth: true }
        Flow {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Repeater { model: col.v.neutros || []; delegate: Muestra { required property var modelData; m: modelData; conPaso: true } }
        }
        Kirigami.ListSectionHeader { text: "Acento y sus variantes · estados"; Layout.fillWidth: true }
        Flow {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            Repeater { model: (col.v.acentos || []).concat(col.v.estados || []); delegate: Muestra { required property var modelData; m: modelData } }
        }
        Kirigami.ListSectionHeader { text: "Terminal: los 16 colores ANSI sobre su fondo"; Layout.fillWidth: true }
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: ansi.implicitHeight + Kirigami.Units.smallSpacing * 2
            radius: Kirigami.Units.cornerRadius
            color: (col.v.terminal || {}).fondo || "transparent"
            Grid {
                id: ansi
                anchors.centerIn: parent
                columns: 8
                spacing: Kirigami.Units.smallSpacing
                Repeater {
                    model: col.v.ansi || []
                    delegate: Rectangle {
                        required property var modelData
                        width: Kirigami.Units.gridUnit * 2.4; height: Kirigami.Units.gridUnit * 1.6; radius: 3
                        color: modelData.hex
                        QQC2.ToolTip.text: modelData.nombre + " · " + modelData.hex + " · " + modelData.oklch
                        QQC2.ToolTip.visible: zona.containsMouse
                        MouseArea { id: zona; anchors.fill: parent; hoverEnabled: true }
                        Text { anchors.centerIn: parent; text: modelData.nombre.replace("color", ""); color: modelData.texto; font.pixelSize: Kirigami.Units.gridUnit * 0.6 }
                    }
                }
            }
        }
        Kirigami.ListSectionHeader { text: "Contrastes WCAG 2.x (texto: AA ≥ 4,5 · AAA ≥ 7; controles: ≥ 3)"; Layout.fillWidth: true }
        Repeater {
            model: col.v.contrastes || []
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Rectangle {
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 4.5
                    Layout.preferredHeight: Kirigami.Units.gridUnit * 1.5
                    radius: 3
                    color: modelData.hexFondo
                    border.width: 1
                    border.color: Qt.alpha(Kirigami.Theme.textColor, 0.15)
                    Text { anchors.centerIn: parent; text: "Texto Aa"; color: modelData.hexFrente; font.bold: true }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    QQC2.Label { text: modelData.que; elide: Text.ElideRight; Layout.fillWidth: true }
                    QQC2.Label { text: modelData.frente + " sobre " + modelData.fondo; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; elide: Text.ElideRight; Layout.fillWidth: true }
                }
                QQC2.Label { text: modelData.textoRazon; font: Kirigami.Theme.fixedWidthFont }
                Item {
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 8
                    implicitHeight: veredicto.implicitHeight
                    EtiquetaNivel { id: veredicto; visible: text !== ""; text: modelData.veredicto; nivel: modelData.nivel }
                }
            }
        }
    }

    // una muestra grande: el color, su nombre, L/C/H y su hex (y el paso de L desde la anterior en una escala)
    component Muestra: Rectangle {
        property var m: ({})
        property bool conPaso: false
        width: Kirigami.Units.gridUnit * 5.6
        height: Kirigami.Units.gridUnit * 5.2
        radius: Kirigami.Units.cornerRadius
        color: m.hex || "transparent"
        border.width: 1
        border.color: Qt.alpha(Kirigami.Theme.textColor, 0.15)
        Accessible.role: Accessible.StaticText
        Accessible.name: (m.nombre || "") + " " + (m.hex || "") + " " + (m.oklch || "")
        Column {
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.margins: Kirigami.Units.smallSpacing
            Text { text: m.nombre || ""; color: m.texto || "transparent"; font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.62 }
            Text { text: m.l >= 0 ? "L " + m.l.toFixed(3) + (parent.parent.conPaso && m.paso ? "  Δ" + (m.paso > 0 ? "+" : "") + m.paso.toFixed(3) : "") : ""; color: m.texto || "transparent"; font.pixelSize: Kirigami.Units.gridUnit * 0.55; font.family: Kirigami.Theme.fixedWidthFont.family }
            Text { text: m.l >= 0 ? "C " + m.c.toFixed(3) + "  H " + m.h.toFixed(0) : ""; color: m.texto || "transparent"; font.pixelSize: Kirigami.Units.gridUnit * 0.55; font.family: Kirigami.Theme.fixedWidthFont.family }
            Text { text: m.hex || ""; color: m.texto || "transparent"; font.pixelSize: Kirigami.Units.gridUnit * 0.6; font.family: Kirigami.Theme.fixedWidthFont.family }
        }
    }
}
