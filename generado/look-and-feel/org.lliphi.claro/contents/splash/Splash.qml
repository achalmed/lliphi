// GENERADO por herramientas/generar.py desde fuentes/base/WhiteSur-kde (GPL-3.0) y tokens/; no editar
import QtQuick 2.5


Image {
    id: root
    source: "images/background.png"

    property int stage

    onStageChanged: {
        if (stage == 1) {
            introAnimation.running = true
        }
    }


    Item {
        id: content
        anchors.fill: parent
        opacity: 0
        TextMetrics {
            id: units
            text: "M"
            property int gridUnit: boundingRect.height
            property int largeSpacing: units.gridUnit
            property int smallSpacing: Math.max(2, gridUnit/4)
        }

        Text {
            id: logo
            // Lliphi: el nombre en Inter en lugar del logotipo de Apple de WhiteSur
            anchors.centerIn: parent
            textFormat: Text.StyledText
            text: "Lliphi<font color='#315bef'>.</font>"
            color: "#1d1f24"
            font.family: "Inter"
            font.weight: Font.Light
            font.pixelSize: units.gridUnit * 4
            font.letterSpacing: units.gridUnit * 0.15
        }

        Image {
            id: busyIndicator
            //in the middle of the remaining space
            y: parent.height - (parent.height - logo.y) / 2 - height/2
            anchors.horizontalCenter: parent.horizontalCenter
            source: "images/loading-00.svg"
            sourceSize.height: units.gridUnit * 1.5
            sourceSize.width: units.gridUnit * 1.5
            RotationAnimator on rotation {
                id: rotationAnimator
                from: 0
                to: 360
                duration: 800
                loops: Animation.Infinite
            }
        }

    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: 1000
        easing.type: Easing.InOutQuad
    }
}
