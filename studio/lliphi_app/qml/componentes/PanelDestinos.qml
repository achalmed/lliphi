// PanelDestinos — el pie de la mesa de diseño (rediseño del 2026-11-18): cada área con sus destinos y, de cada uno, el
// estado de lo generado como un punto en color de estado (al día: positivo · desfasado: negativo · sin comprobar:
// neutro · sin generar: tenue) y, si algo pide atención, su texto (desfasado, sin generar, instalación modificada).
// «Generar lo que cambió» (F5) prepara el plan de los desfasados o, si la última verificación ya no es vigente, verifica
// antes; Ctrl+Intro lo ejecuta tras confirmar (los seis pasos). Un área o un destino abre su página a la derecha.
// Todo sale de studio.centro (grupos, cambios) y de studio.destinos; los colores, de Kirigami.Theme.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var centro: studio.centro
    readonly property var cambios: centro.cambios
    spacing: 0

    function colorDe(nivel) {
        return ({ positivo: Kirigami.Theme.positiveTextColor, negativo: Kirigami.Theme.negativeTextColor,
                  neutro: Kirigami.Theme.neutralTextColor, activo: Kirigami.Theme.activeTextColor })[nivel] || Kirigami.Theme.disabledTextColor
    }

    RowLayout {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.smallSpacing
        Layout.topMargin: Kirigami.Units.smallSpacing
        Layout.bottomMargin: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Heading { level: 4; text: "Destinos" }
        QQC2.Label {
            Layout.fillWidth: true
            text: "Lliphi " + studio.ajustes.version + " · última verificación: " + studio.destinos.fechaVerificacion
            color: Kirigami.Theme.disabledTextColor
            elide: Text.ElideRight
        }
        QQC2.Label {
            text: raiz.cambios.texto || ""
            color: raiz.colorDe(raiz.cambios.nivel)
            elide: Text.ElideRight
            Layout.maximumWidth: Kirigami.Units.gridUnit * 26
        }
        BotonAccion { accion: studio.acciones.accion("escr.generar_cambios"); conTexto: true }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    QQC2.ScrollView {
        id: desplazable
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        contentWidth: availableWidth
        QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff

        // dos columnas que se apilan cada una por su cuenta (sin filas comunes), o una si no hay ancho
        RowLayout {
            id: columnas
            width: desplazable.availableWidth
            spacing: Kirigami.Units.largeSpacing
            readonly property bool dos: width > Kirigami.Units.gridUnit * 64
            // el corte que reparte las líneas: cada área pesa sus destinos más uno
            readonly property int corte: {
                const g = raiz.centro.grupos
                const total = g.reduce((s, x) => s + x.destinos.length + 1, 0)
                let suma = 0
                for (let i = 0; i < g.length; i++) {
                    suma += g[i].destinos.length + 1
                    if (suma >= total / 2)
                        return i + 1
                }
                return g.length
            }
            Repeater {
                model: columnas.dos ? [raiz.centro.grupos.slice(0, columnas.corte), raiz.centro.grupos.slice(columnas.corte)] : [raiz.centro.grupos]
                delegate: ColumnLayout {
                    id: columna
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1                      // las columnas, del mismo ancho
                    Layout.alignment: Qt.AlignTop
                    spacing: 0
                    Repeater {
                        model: columna.modelData
                        delegate: Grupo {}
                    }
                }
            }
        }
    }

    // un área: su nombre (lleva a su página) y sus destinos, cada uno con el punto de lo generado
    component Grupo: RowLayout {
        id: grupo
        required property var modelData
        Layout.fillWidth: true
        spacing: Kirigami.Units.smallSpacing
        QQC2.ItemDelegate {
            Layout.preferredWidth: Kirigami.Units.gridUnit * 10
            Layout.alignment: Qt.AlignTop
            text: grupo.modelData.titulo
            icon.name: grupo.modelData.icono
            highlighted: raiz.centro.area === grupo.modelData.id
            onClicked: raiz.centro.fijarArea(grupo.modelData.id)
            Accessible.name: "Abrir el área " + grupo.modelData.titulo
            QQC2.ToolTip.text: grupo.modelData.que
            QQC2.ToolTip.visible: hovered
            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
        }
        Flow {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop
            spacing: 0
            QQC2.Label {
                visible: grupo.modelData.destinos.length === 0
                height: Kirigami.Units.gridUnit * 1.8
                verticalAlignment: Text.AlignVCenter
                leftPadding: Kirigami.Units.smallSpacing
                text: grupo.modelData.nota || "Sin destinos"
                color: Kirigami.Theme.disabledTextColor
            }
            Repeater {
                model: grupo.modelData.destinos
                delegate: QQC2.ItemDelegate {
                    id: destino
                    required property var modelData
                    readonly property bool pendiente: ["desfasado", "sin_generar"].indexOf(modelData.clave_generado) >= 0
                    readonly property string atencion: (pendiente ? modelData.generado.toLowerCase() : "")
                                                       + (modelData.clave_instalacion === "modificado" ? (pendiente ? " · " : "") + "instalación modificada" : "")
                    highlighted: raiz.centro.area === grupo.modelData.id && raiz.centro.destino === modelData.id
                    onClicked: raiz.centro.irADestino(modelData.id)
                    Accessible.name: modelData.nombre + ": generado " + modelData.generado.toLowerCase() + ", " + modelData.instalacion.toLowerCase()
                    QQC2.ToolTip.text: "Generado: " + modelData.generado.toLowerCase() + " · " + modelData.instalacion.toLowerCase()
                    QQC2.ToolTip.visible: hovered
                    QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                    contentItem: RowLayout {
                        spacing: Kirigami.Units.smallSpacing
                        QQC2.Label { text: "●"; color: destino.highlighted ? Kirigami.Theme.highlightedTextColor : raiz.colorDe(destino.modelData.nivel_generado) }
                        QQC2.Label { text: destino.modelData.nombre; color: destino.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor }
                        QQC2.Label {
                            visible: destino.atencion !== ""
                            text: destino.atencion
                            color: destino.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.negativeTextColor
                            font: Kirigami.Theme.smallFont
                        }
                    }
                }
            }
        }
    }
}
