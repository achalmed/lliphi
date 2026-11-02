// Operación — la operación elegida: qué hace, la orden exacta de F5 y la de Ctrl+Intro, qué toca, y el plan (la última
// simulación) y el registro (la última aplicación) guardados en la caché del studio.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var o: operaciones
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.FormLayout {
            Layout.fillWidth: true
            QQC2.Label { Kirigami.FormData.label: "Operación:"; text: pagina.o.titulo + " (" + pagina.o.grupo + ")"; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Qué hace:"; text: pagina.o.descripcion; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: pagina.o.verbo + " (F5):"; text: pagina.o.ordenSimular; font: Kirigami.Theme.fixedWidthFont; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Aplicar (Ctrl+Intro):"; visible: pagina.o.escribe; text: pagina.o.ordenAplicar; font: Kirigami.Theme.fixedWidthFont; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Toca:"; text: pagina.o.queToca; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Reversible:"; visible: pagina.o.instala; text: "el instalador respalda con SHA-256 y deja UNDO.sh (Herramientas › Respaldos y volver atrás…)"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: !pagina.o.puedeSimular && pagina.o.motivoNoSimular !== "" && !pagina.o.enCurso
            type: Kirigami.MessageType.Information
            text: pagina.o.motivoNoSimular
        }
        RowLayout {
            BotonAccion { accion: accionesStudio.accion("op.simular"); conTexto: true }
            BotonAccion { accion: accionesStudio.accion("op.aplicar"); conTexto: true }
            BotonAccion { accion: accionesStudio.accion("op.cancelar"); conTexto: true }
        }
        Kirigami.Heading { level: 4; text: "Plan (la última simulación)" }
        VistaTexto { Layout.fillWidth: true; Layout.preferredHeight: Kirigami.Units.gridUnit * 14; texto: pagina.o.plan; mensajeVacio: "Sin simulación guardada: F5"; iconoVacio: "system-run"; nombreAccesible: "Plan de " + pagina.o.titulo }
        Kirigami.Heading { level: 4; visible: pagina.o.escribe; text: "Registro (la última aplicación)" }
        VistaTexto { Layout.fillWidth: true; visible: pagina.o.escribe; Layout.preferredHeight: Kirigami.Units.gridUnit * 14; texto: pagina.o.registro; mensajeVacio: "Nunca se aplicó desde este studio"; iconoVacio: "text-x-log"; nombreAccesible: "Registro de " + pagina.o.titulo }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
