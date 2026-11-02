// PanelPasos — generar, instalar o desinstalar en seis pasos visibles (docs/reingenieria.md §3.2): Plan · Afectados ·
// Conflictos · Ejecutar · Verificar · Informe. Arriba los pasos (PasosOperacion) con su cuenta; debajo, el contenido del
// paso elegido. Ejecutar (Ctrl+Intro) pide confirmación con las consecuencias del plan y su estado de operación
// (instalación, eliminación o escritura); con un conflicto que bloquea no se puede. Todo sale de studio.escritura.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var escritura: studio.escritura
    readonly property var plan: escritura.plan
    readonly property var resultado: escritura.resultado
    property int paso: 0
    signal cerrar()

    spacing: 0
    Connections { target: raiz.escritura; function onCambiado() { raiz.paso = Math.max(0, Math.min(5, raiz.escritura.alcanzado === 3 ? 0 : raiz.escritura.alcanzado - 1)) } }

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        Kirigami.Heading { level: 3; text: raiz.plan.titulo || "Sin plan"; Layout.fillWidth: true; elide: Text.ElideRight }
        EtiquetaEstado { texto: raiz.plan.estadoOperacion ? studio.acciones.accion("escr.ejecutar." + raiz.plan.tipo).operacionTexto : "" }
        BotonAccion { accion: studio.acciones.accion("escr.ejecutar"); conTexto: true }
        QQC2.ToolButton {
            icon.name: "window-close"
            onClicked: { raiz.escritura.descartar(); raiz.cerrar() }
            Accessible.name: "Cerrar los pasos"
            QQC2.ToolTip.text: "Cerrar (descarta el plan si no se ejecutó)"
            QQC2.ToolTip.visible: hovered
        }
    }
    PasosOperacion {
        Layout.fillWidth: true
        Layout.leftMargin: Kirigami.Units.smallSpacing
        pasos: raiz.escritura.pasos
        alcanzado: raiz.escritura.alcanzado
        actual: raiz.paso
        cuentas: raiz.escritura.cuentas
        onElegido: p => raiz.paso = p
    }
    Kirigami.Separator { Layout.fillWidth: true }

    StackLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        currentIndex: raiz.paso

        // 1 Plan
        ColumnLayout {
            spacing: Kirigami.Units.smallSpacing
            QQC2.Label { Layout.fillWidth: true; Layout.margins: Kirigami.Units.largeSpacing; wrapMode: Text.WordWrap; text: raiz.plan.descripcion || "" }
            QQC2.TextField {
                Layout.fillWidth: true
                Layout.leftMargin: Kirigami.Units.largeSpacing
                Layout.rightMargin: Kirigami.Units.largeSpacing
                readOnly: true
                text: raiz.plan.orden || ""
                font: Kirigami.Theme.fixedWidthFont
                Accessible.name: "Orden exacta que se ejecutará"
            }
            QQC2.Label {
                Layout.margins: Kirigami.Units.largeSpacing
                text: (raiz.plan.afectados || []).length + " ruta(s) afectadas, de las que cambian " + (raiz.plan.cambian || 0) + " · "
                      + (raiz.plan.conflictos || []).length + " conflicto(s) o aviso(s)" + (raiz.plan.bloqueado ? " · BLOQUEADO" : "")
                color: raiz.plan.bloqueado ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.textColor
            }
            Item { Layout.fillHeight: true }
        }
        // 2 Afectados
        ListView {
            clip: true
            model: raiz.plan.afectados || []
            QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
            Accessible.name: "Rutas afectadas"
            delegate: RowLayout {
                required property var modelData
                width: ListView.view.width
                spacing: Kirigami.Units.smallSpacing
                Item {
                    Layout.leftMargin: Kirigami.Units.smallSpacing
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 6
                    implicitHeight: accion.implicitHeight
                    EtiquetaEstado { id: accion; texto: modelData.accion; nivel: modelData.nivel }
                }
                QQC2.Label { text: modelData.ruta; font: Kirigami.Theme.fixedWidthFont; elide: Text.ElideMiddle; Layout.fillWidth: true }
                QQC2.Label { text: modelData.detalle; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; elide: Text.ElideRight; Layout.maximumWidth: Kirigami.Units.gridUnit * 20 }
            }
        }
        // 3 Conflictos
        ColumnLayout {
            Kirigami.PlaceholderMessage {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: (raiz.plan.conflictos || []).length === 0
                icon.name: "checkmark"
                text: "Sin conflictos"
                explanation: "Nada ajeno en los destinos, nada que falte en generado/ y ninguna herramienta ausente."
            }
            Repeater {
                model: raiz.plan.conflictos || []
                delegate: Kirigami.InlineMessage {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.margins: Kirigami.Units.smallSpacing
                    visible: true
                    type: modelData.bloquea ? Kirigami.MessageType.Error : Kirigami.MessageType.Information
                    text: (modelData.bloquea ? "Bloquea: " : "") + (modelData.ruta ? modelData.ruta + ": " : "") + modelData.motivo
                }
            }
            Item { Layout.fillHeight: true; visible: (raiz.plan.conflictos || []).length > 0 }
        }
        // 4 Ejecutar
        Kirigami.PlaceholderMessage {
            icon.name: raiz.resultado.codigo === 0 ? "checkmark" : raiz.resultado.codigo > 0 ? "dialog-error" : "system-run"
            text: raiz.resultado.codigo < 0 ? (raiz.plan.bloqueado ? "Con un conflicto que bloquea no se ejecuta" : "Listo para ejecutar")
                : raiz.resultado.codigo === 0 ? "La orden terminó bien" : "La orden falló (código " + raiz.resultado.codigo + ")"
            explanation: raiz.resultado.codigo < 0 ? "Ctrl+Intro pide confirmación con lo que cambia y corre: " + (raiz.plan.orden || "") : "La salida íntegra está en el panel inferior (F4)."
        }
        // 5 Verificar
        Kirigami.PlaceholderMessage {
            icon.name: raiz.resultado.verificado === true ? "checkmark" : raiz.resultado.verificado === false ? "dialog-warning" : "view-refresh"
            text: raiz.resultado.verificado === true ? "Verificado" : raiz.resultado.verificado === false ? "La verificación no pasa" : "Sin verificar"
            explanation: raiz.resultado.detalle || "La verificación es aparte del éxito: comprueba en el disco que cada ruta quedó como el plan decía."
        }
        // 6 Informe
        ColumnLayout {
            spacing: 0
            RowLayout {
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.smallSpacing
                QQC2.Label { text: raiz.resultado.rutaInforme ? "Guardado en la caché del studio" : ""; color: Kirigami.Theme.disabledTextColor; Layout.fillWidth: true }
                QQC2.Button {
                    text: "Abrir el informe"
                    icon.name: "document-open"
                    enabled: !!raiz.resultado.rutaInforme
                    onClicked: studio.espacio.abrir(raiz.resultado.rutaInforme)
                }
            }
            VistaTexto { Layout.fillWidth: true; Layout.fillHeight: true; texto: raiz.resultado.informe || ""; markdown: true; mensajeVacio: "El informe aparece al terminar"; iconoVacio: "text-markdown" }
        }
    }
}
