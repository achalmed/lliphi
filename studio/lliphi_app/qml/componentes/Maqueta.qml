// Maqueta — una ventana de muestra pintada con los colores de los tokens de una variante, como la vista previa de
// Colores en las Preferencias del sistema: barra de título (encabezado), barra lateral (ventana), una vista con filas
// alternas y una elegida (selección), un botón, un botón de acento, un enlace, un aviso de cada estado, un tooltip y un
// separador. Los colores llegan como DATOS (`colores`, de servicios/diseno.py: fondo_ventana, texto_normal…); la
// ventana del studio sigue vistiendo Kirigami.Theme. `tipo` cambia lo que se muestra dentro (ventana, controles).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Rectangle {
    id: raiz
    property var colores: ({})
    property string titulo: ""
    property string tipo: "ventana"          // "ventana" · "controles" (Kvantum)
    readonly property var c: colores || ({})

    implicitWidth: Kirigami.Units.gridUnit * 22
    implicitHeight: Kirigami.Units.gridUnit * 14
    radius: Kirigami.Units.cornerRadius
    color: c.fondo_ventana || "transparent"
    border.width: 1
    border.color: c.borde_separador || Kirigami.Theme.disabledTextColor
    clip: true
    Accessible.role: Accessible.Graphic
    Accessible.name: "Vista previa de " + titulo + " pintada con sus tokens"

    // barra de título
    Rectangle {
        id: barra
        width: parent.width
        height: Kirigami.Units.gridUnit * 1.6
        color: c.fondo_encabezado || "transparent"
        radius: raiz.radius
        Row {
            anchors.left: parent.left
            anchors.leftMargin: Kirigami.Units.smallSpacing * 2
            anchors.verticalCenter: parent.verticalCenter
            spacing: Kirigami.Units.smallSpacing
            Repeater {
                model: [raiz.c.acento_base, raiz.c.texto_inactivo, raiz.c.texto_inactivo]
                delegate: Rectangle { required property var modelData; width: Kirigami.Units.gridUnit * 0.6; height: width; radius: width / 2; color: modelData || "transparent" }
            }
        }
        Text { anchors.centerIn: parent; text: raiz.titulo; color: c.texto_normal || "transparent"; font.bold: true }
    }

    RowLayout {
        anchors.top: barra.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        spacing: 0
        // barra lateral
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: Kirigami.Units.gridUnit * 6
            color: c.fondo_ventana || "transparent"
            Column {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing
                spacing: 2
                Repeater {
                    model: ["Inicio", "Documentos", "Imágenes", "Música"]
                    delegate: Rectangle {
                        required property string modelData
                        required property int index
                        width: parent.width
                        height: Kirigami.Units.gridUnit * 1.3
                        radius: 3
                        color: index === 1 ? (raiz.c.seleccion_fondo || "transparent") : "transparent"
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            x: Kirigami.Units.smallSpacing
                            text: modelData
                            color: index === 1 ? (raiz.c.seleccion_texto || "transparent") : (raiz.c.texto_normal || "transparent")
                        }
                    }
                }
            }
        }
        Rectangle { Layout.fillHeight: true; Layout.preferredWidth: 1; color: c.borde_separador || "transparent" }
        // la vista
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: c.fondo_vista || "transparent"
            Column {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing
                spacing: Kirigami.Units.smallSpacing
                visible: raiz.tipo === "ventana"
                Repeater {
                    model: ["informe.pdf", "notas.md", "paleta.json"]
                    delegate: Rectangle {
                        required property string modelData
                        required property int index
                        width: parent.width
                        height: Kirigami.Units.gridUnit * 1.2
                        color: index % 2 ? (raiz.c.fondo_vista_alterno || "transparent") : "transparent"
                        Text { anchors.verticalCenter: parent.verticalCenter; x: 4; text: modelData; color: raiz.c.texto_normal || "transparent" }
                        Text { anchors.verticalCenter: parent.verticalCenter; anchors.right: parent.right; anchors.rightMargin: 4; text: "hoy"; color: raiz.c.texto_secundario || "transparent" }
                    }
                }
                Text { text: "Un enlace a la documentación"; color: raiz.c.enlace || "transparent"; font.underline: true }
                Row {
                    spacing: Kirigami.Units.smallSpacing
                    Repeater {
                        model: [["Error", raiz.c.estado_error], ["Aviso", raiz.c.estado_advertencia], ["Hecho", raiz.c.estado_exito], ["Info", raiz.c.estado_info]]
                        delegate: Text { required property var modelData; text: modelData[0]; color: modelData[1] || "transparent"; font.bold: true }
                    }
                }
            }
            // los controles (Kvantum): campo, casilla, deslizador, botones
            Column {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.smallSpacing * 2
                spacing: Kirigami.Units.smallSpacing * 2
                visible: raiz.tipo === "controles"
                Rectangle {
                    width: parent.width; height: Kirigami.Units.gridUnit * 1.4; radius: 4
                    color: raiz.c.fondo_vista || "transparent"; border.width: 1; border.color: raiz.c.foco || "transparent"
                    Text { anchors.verticalCenter: parent.verticalCenter; x: 6; text: "Buscar…"; color: raiz.c.texto_inactivo || "transparent" }
                }
                Row {
                    spacing: Kirigami.Units.smallSpacing
                    Rectangle { width: Kirigami.Units.gridUnit * 0.9; height: width; radius: 3; color: raiz.c.acento_base || "transparent"
                                Text { anchors.centerIn: parent; text: "✓"; color: raiz.c.texto_sobre_acento || "transparent" } }
                    Text { text: "Casilla marcada"; color: raiz.c.texto_normal || "transparent" }
                }
                Rectangle {
                    width: parent.width; height: 4; radius: 2; color: raiz.c.fondo_boton || "transparent"
                    Rectangle { width: parent.width * 0.6; height: parent.height; radius: 2; color: raiz.c.acento_base || "transparent" }
                }
            }
            // botones y tooltip
            Row {
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.margins: Kirigami.Units.smallSpacing
                spacing: Kirigami.Units.smallSpacing
                Rectangle {
                    width: cancelar.implicitWidth + 16; height: Kirigami.Units.gridUnit * 1.4; radius: 4
                    color: raiz.c.fondo_boton || "transparent"; border.width: 1; border.color: raiz.c.borde_sutil || "transparent"
                    Text { id: cancelar; anchors.centerIn: parent; text: "Cancelar"; color: raiz.c.texto_normal || "transparent" }
                }
                Rectangle {
                    width: aceptar.implicitWidth + 16; height: Kirigami.Units.gridUnit * 1.4; radius: 4
                    color: raiz.c.acento_base || "transparent"
                    Text { id: aceptar; anchors.centerIn: parent; text: "Aceptar"; color: raiz.c.texto_sobre_acento || "transparent"; font.bold: true }
                }
            }
            Rectangle {
                visible: raiz.tipo === "ventana"
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: Kirigami.Units.smallSpacing
                width: consejo.implicitWidth + 12; height: consejo.implicitHeight + 8; radius: 4
                color: raiz.c.fondo_tooltip || "transparent"
                Text { id: consejo; anchors.centerIn: parent; text: "Un tooltip"; color: raiz.c.texto_tooltip || raiz.c.texto_normal || "transparent" }
            }
        }
    }
}
