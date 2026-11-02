// Resumen — el destino actual en Markdown: qué entrega, su estado generado e instalado, sus dependencias, los pares
// origen → destino de su instalación y el último respaldo del instalador.
import QtQuick
import GuiComun

VistaTexto {
    readonly property var d: destinos
    texto: d.resumenMarkdown
    markdown: true
    mensajeVacio: "Ningún destino"
    iconoVacio: "preferences-desktop-theme-global"
    nombreAccesible: "Resumen de " + (d.nombre || "ningún destino")
}
