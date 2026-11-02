// PaginaArea — la página de un área del centro de configuración (esquemas de color, Plasma, Kvantum, Konsole, editores,
// fondos, tipografía, iconos, otros): arriba, qué es y su vista previa (VistaPrevia: el tema VISTO, claro y oscuro);
// debajo, a la izquierda, las tarjetas de sus destinos (lo generado con su fecha, la instalación, la compatibilidad) y,
// a la derecha, del destino elegido, **lo instalado frente a lo generado archivo por archivo** (igual · distinto · ajeno ·
// falta) y la diferencia del archivo elegido. Generar e instalar se preparan aquí y siguen en los seis pasos.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var centro: studio.centro
    readonly property var registro: studio.acciones
    readonly property var area: centro.datosArea
    readonly property var cuenta: centro.cuentaPares

    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon { source: raiz.area.icono || "preferences-system"; Layout.preferredWidth: Kirigami.Units.iconSizes.large; Layout.preferredHeight: Kirigami.Units.iconSizes.large }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0
            Kirigami.Heading { level: 1; text: raiz.area.titulo || "" }
            QQC2.Label { text: raiz.area.que || ""; color: Kirigami.Theme.disabledTextColor; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        BotonAccion { accion: raiz.registro.accion("escr.generar"); conTexto: true }
        BotonAccion { accion: raiz.registro.accion("escr.instalar"); conTexto: true }
    }
    VistaPrevia {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.largeSpacing
        Layout.rightMargin: Kirigami.Units.largeSpacing
        Layout.bottomMargin: Kirigami.Units.largeSpacing
        area: raiz.centro.area
    }
    Kirigami.Separator { Layout.fillWidth: true; visible: raiz.centro.tarjetas.length > 0 }

    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: raiz.centro.tarjetas.length > 0
        orientation: Qt.Horizontal

        ListView {
            id: lista
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 24
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 16
            clip: true
            spacing: Kirigami.Units.smallSpacing
            topMargin: Kirigami.Units.smallSpacing
            leftMargin: Kirigami.Units.smallSpacing
            rightMargin: Kirigami.Units.smallSpacing
            model: raiz.centro.tarjetas
            boundsBehavior: Flickable.StopAtBounds
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            Accessible.name: "Destinos de " + (raiz.area.titulo || "")
            delegate: TarjetaDestino {
                required property var modelData
                width: ListView.view.width - Kirigami.Units.smallSpacing * 2
                datos: modelData
                elegida: modelData.id === raiz.centro.destino
                onClicked: raiz.centro.fijarDestino(modelData.id)
            }
        }

        ColumnLayout {
            QQC2.SplitView.fillWidth: true
            spacing: 0
            Kirigami.ListSectionHeader {
                Layout.fillWidth: true
                text: raiz.centro.pares.length ? "Lo instalado frente a lo generado · " + raiz.cuenta.igual + " igual · " + raiz.cuenta.distinto + " distinto · "
                                                 + raiz.cuenta.ajeno + " ajeno · " + raiz.cuenta.falta + " falta"
                                               : "Lo instalado frente a lo generado"
            }
            Kirigami.PlaceholderMessage {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: raiz.centro.pares.length === 0
                icon.name: "dialog-information"
                text: raiz.centro.destino === "" ? "Elija un destino" : "Este destino no instala archivos propios"
                explanation: raiz.centro.destino === "" ? "" : "Es un componente del tema global, un tema de terceros (instalar.py dependencias) o se instala con pkexec desde la terminal."
            }
            ListView {
                id: pares
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(contentHeight, Kirigami.Units.gridUnit * 9)
                visible: raiz.centro.pares.length > 0
                clip: true
                model: raiz.centro.pares
                currentIndex: raiz.centro.par
                boundsBehavior: Flickable.StopAtBounds
                QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
                Accessible.name: "Archivos instalados del destino"
                delegate: QQC2.ItemDelegate {
                    id: filaPar
                    required property var modelData
                    required property int index
                    width: ListView.view.width
                    highlighted: ListView.isCurrentItem
                    onClicked: raiz.centro.fijarPar(index)
                    Accessible.name: modelData.destinoCorto + ": " + modelData.texto
                    contentItem: RowLayout {
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon {
                            source: ({ igual: "checkmark", distinto: "document-edit", ajeno: "dialog-warning", falta: "list-add", sin_generar: "dialog-error" })[filaPar.modelData.estado] || "text-x-generic"
                            implicitWidth: Kirigami.Units.iconSizes.small
                            implicitHeight: implicitWidth
                        }
                        QQC2.Label {
                            text: filaPar.modelData.destinoCorto
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                            font: Kirigami.Theme.fixedWidthFont
                            color: filaPar.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                        }
                        EtiquetaEstado { texto: filaPar.modelData.texto; nivel: filaPar.modelData.nivel }
                        QQC2.ToolButton {
                            icon.name: "system-file-manager"
                            onClicked: studio.espacio.abrirDolphin(filaPar.modelData.destino)
                            Accessible.name: "Mostrar en Dolphin " + filaPar.modelData.destinoCorto
                            QQC2.ToolTip.text: "Mostrar en Dolphin"
                            QQC2.ToolTip.visible: hovered
                        }
                    }
                }
            }
            VistaDiferencia {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: raiz.centro.pares.length > 0
                diferencia: raiz.centro.diferencia
                mensajeVacio: "Elija un archivo para ver lo instalado frente a lo generado"
            }
        }
    }
    Kirigami.PlaceholderMessage {
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: raiz.centro.tarjetas.length === 0 && raiz.centro.area !== "tipografia"
        icon.name: raiz.area.icono || "preferences-system"
        text: "Ningún destino en esta área"
    }
    Item { Layout.fillHeight: true; visible: raiz.centro.area === "tipografia" }
}
