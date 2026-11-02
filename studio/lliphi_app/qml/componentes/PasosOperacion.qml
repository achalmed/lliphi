// PasosOperacion — los seis pasos de una escritura, visibles (encargo del autor §3.2): Plan · Afectados · Conflictos ·
// Ejecutar · Verificar · Informe. Cada paso con su número, su estado (hecho, el siguiente, pendiente) y, al elegirlo, su
// contenido debajo. Un paso no alcanzado no se puede abrir.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

RowLayout {
    id: raiz
    property var pasos: []
    property int alcanzado: 0          // 1…6: el último hecho
    property int actual: 0             // 0…5: el que se muestra
    property var cuentas: []           // un texto corto por paso (p. ej. «12»)
    signal elegido(int paso)
    spacing: 0

    Repeater {
        model: raiz.pasos
        delegate: RowLayout {
            required property string modelData
            required property int index
            spacing: 0
            Kirigami.Separator { visible: index > 0; Layout.preferredWidth: Kirigami.Units.gridUnit; Layout.alignment: Qt.AlignVCenter }
            QQC2.ToolButton {
                id: boton
                readonly property bool hecho: index < raiz.alcanzado
                readonly property bool siguiente: index === raiz.alcanzado
                checkable: true
                checked: index === raiz.actual
                enabled: index <= raiz.alcanzado
                icon.name: hecho ? "checkmark" : (siguiente ? "go-next" : "")
                text: (index + 1) + " " + modelData + (raiz.cuentas[index] ? " · " + raiz.cuentas[index] : "")
                display: QQC2.AbstractButton.TextBesideIcon
                font.bold: checked
                onClicked: raiz.elegido(index)
                Accessible.name: "Paso " + (index + 1) + ": " + modelData + (hecho ? ", hecho" : siguiente ? ", siguiente" : ", pendiente")
            }
        }
    }
    Item { Layout.fillWidth: true }
}
