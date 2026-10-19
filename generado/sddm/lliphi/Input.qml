import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

TextField {
    id: campo
    placeholderTextColor: config.color
    palette.text: config.color
    font.pointSize: config.fontSize
    font.family: config.font
    width: parent.width
    background: Item {
        Rectangle {
            anchors.fill: parent
            color: campo.focus ? "#ffffff" : "#dddddd"
            radius: 100
            opacity: 0.45
        }
        Rectangle {   // Lliphi (mejora 7): el acento al enfocar
            anchors.fill: parent
            color: "transparent"
            radius: 100
            border.width: 2
            border.color: "#c93436"
            visible: campo.activeFocus
        }
    }
}
