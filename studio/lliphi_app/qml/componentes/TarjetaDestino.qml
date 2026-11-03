// TarjetaDestino — un destino del área (un módulo o un complemento): su nombre y lo que entrega, lo generado (al día,
// desfasado, sin comprobar) con la fecha de su última construcción, la instalación, la compatibilidad (el estado del
// modulo.json, «desde», lo que falta) y, si se elige, la marca de elegido. Generar e instalar se preparan desde la
// página (seis pasos): la tarjeta solo elige.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ItemDelegate {
    id: raiz
    property var datos: ({})
    property bool elegida: false
    readonly property var compat: datos.compatibilidad || ({})

    highlighted: elegida
    padding: Kirigami.Units.largeSpacing
    Accessible.name: (datos.nombre || "") + ": generado " + (datos.generado || "") + ", " + (datos.instalacion || "")

    background: Rectangle {
        radius: Kirigami.Units.cornerRadius
        color: raiz.elegida ? Qt.alpha(Kirigami.Theme.highlightColor, 0.12) : raiz.hovered ? Qt.alpha(Kirigami.Theme.highlightColor, 0.06) : Kirigami.Theme.backgroundColor
        border.width: 1
        border.color: raiz.elegida ? Kirigami.Theme.highlightColor : Qt.alpha(Kirigami.Theme.textColor, 0.15)
    }

    contentItem: ColumnLayout {
        spacing: Kirigami.Units.smallSpacing / 2
        RowLayout {
            Kirigami.Heading { level: 3; text: raiz.datos.nombre || ""; Layout.fillWidth: true; elide: Text.ElideRight }
            QQC2.Label { text: raiz.datos.formato || ""; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont }
        }
        QQC2.Label {
            text: raiz.datos.resumenCorto || ""
            wrapMode: Text.WordWrap
            maximumLineCount: 2
            elide: Text.ElideRight
            color: Kirigami.Theme.disabledTextColor
            Layout.fillWidth: true
        }
        Flow {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            EtiquetaNivel { visible: text !== ""; text: "generado: " + (raiz.datos.generado || "").toLowerCase(); nivel: raiz.datos.nivel_generado === "inactivo" ? "" : raiz.datos.nivel_generado || ""; icono: "run-build" }
            EtiquetaNivel {
                visible: text !== ""; text: (raiz.datos.instalacion || "").toLowerCase()
                nivel: raiz.datos.nivel_instalacion === "inactivo" ? "" : raiz.datos.nivel_instalacion || ""
                icono: "install"
            }
            EtiquetaNivel { visible: text !== ""; text: raiz.compat.texto || ""; nivel: raiz.compat.nivel || ""; icono: "dialog-information" }
            EtiquetaNivel { visible: text !== ""; text: raiz.datos.construccion && raiz.datos.construccion !== "—" ? "construido " + raiz.datos.construccion : ""; icono: "view-calendar" }
            EtiquetaNivel { visible: text !== ""; text: raiz.datos.privilegiado ? "pide pkexec: en la terminal" : ""; nivel: "neutro"; icono: "dialog-password" }
        }
    }
}
