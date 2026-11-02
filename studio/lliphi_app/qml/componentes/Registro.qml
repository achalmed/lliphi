// Registro — la salida de la última orden que corrió sobre el destino actual (generar o instalar, simulada o aplicada).
import QtQuick
import GuiComun

VistaTexto {
    readonly property var d: destinos
    texto: d.registro
    mensajeVacio: !d.hayActual ? "Ningún destino" : "Ninguna orden corrió todavía sobre este destino (F5 simula, Ctrl+Intro aplica)"
    iconoVacio: "text-x-log"
    nombreAccesible: "Registro de " + (d.nombre || "ningún destino")
}
