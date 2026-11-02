// Diferencias — lo que la última «Verificar lo generado» encontró en el destino actual: cada archivo de generado/ que
// difiere de una construcción nueva desde los tokens o que falta; vacío si coincide.
import QtQuick
import GuiComun

VistaTexto {
    readonly property var d: destinos
    texto: d.diferencias
    mensajeVacio: !d.hayActual ? "Ningún destino" : "Sin verificación en este studio: Proyecto › Verificar lo generado ahora (Ctrl+T)"
    iconoVacio: "view-refresh"
    nombreAccesible: "Diferencias de " + (d.nombre || "ningún destino")
}
