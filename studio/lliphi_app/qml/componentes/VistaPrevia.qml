// VistaPrevia — lo propio de la página de cada área, para VER el tema antes de leer estados (como la vista previa de
// cada módulo de las Preferencias del sistema), siempre claro y oscuro lado a lado y siempre desde los tokens o lo
// generado, como datos:
//   esquemas · plasma   → la maqueta de una ventana en cada variante
//   kvantum             → la maqueta con controles (campo, casilla, deslizador, botones)
//   konsole             → una terminal de muestra con sus colores ANSI
//   editores            → un fragmento de código con los colores de sintaxis (la tabla de los editores sale de los ANSI)
//   fondos              → las imágenes generadas, claro y oscuro
//   tipografia          → las familias en su tamaño y si están instaladas (fc-list)
//   iconos              → los temas de iconos y cursores que nombra el tema, si están, y unos iconos de muestra
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Loader {
    id: raiz
    property string area: ""
    readonly property var variantes: (studio.centro.sistema.variantes || [])
    sourceComponent: ({ esquemas: cMaquetas, plasma: cMaquetas, kvantum: cControles, konsole: cTerminal, editores: cCodigo,
                        fondos: cFondos, tipografia: cTipografia, iconos: cIconos })[area] || null
    visible: sourceComponent !== null

    Component {
        id: cMaquetas
        RowLayout {
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: raiz.variantes
                delegate: Maqueta { required property var modelData; colores: modelData.maqueta; titulo: modelData.titulo; Layout.fillWidth: true; Layout.preferredHeight: Kirigami.Units.gridUnit * 13 }
            }
        }
    }
    Component {
        id: cControles
        RowLayout {
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: raiz.variantes
                delegate: Maqueta { required property var modelData; colores: modelData.maqueta; titulo: modelData.titulo; tipo: "controles"; Layout.fillWidth: true; Layout.preferredHeight: Kirigami.Units.gridUnit * 10 }
            }
        }
    }
    Component {
        id: cTerminal
        RowLayout {
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: raiz.variantes
                delegate: Rectangle {
                    id: terminal
                    required property var modelData
                    readonly property var a: modelData.ansi || []
                    function ansi(i) { return a.length > i ? a[i].hex : "transparent" }
                    Layout.fillWidth: true
                    implicitHeight: lineas.implicitHeight + Kirigami.Units.largeSpacing * 2
                    radius: Kirigami.Units.cornerRadius
                    color: (modelData.terminal || {}).fondo || "transparent"
                    Accessible.role: Accessible.Graphic
                    Accessible.name: "Terminal de muestra en " + modelData.titulo
                    Column {
                        id: lineas
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.largeSpacing
                        spacing: 2
                        Text { text: modelData.titulo; color: (terminal.modelData.terminal || {}).texto || "transparent"; font: Kirigami.Theme.fixedWidthFont }
                        Row { Text { text: "usuario@lliphi"; color: terminal.ansi(2); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: ":"; color: (terminal.modelData.terminal || {}).texto || "transparent"; font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "~/proyectos"; color: terminal.ansi(4); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "$ git status"; color: (terminal.modelData.terminal || {}).texto || "transparent"; font: Kirigami.Theme.fixedWidthFont } }
                        Text { text: "  modificado:   tokens.json"; color: terminal.ansi(1); font: Kirigami.Theme.fixedWidthFont }
                        Text { text: "  nuevo:        lliphi.colors"; color: terminal.ansi(2); font: Kirigami.Theme.fixedWidthFont }
                        Text { text: "aviso: 2 archivos sin preparar"; color: terminal.ansi(3); font: Kirigami.Theme.fixedWidthFont }
                        Text { text: "# un comentario tenue"; color: (terminal.modelData.terminal || {})["texto-tenue"] || "transparent"; font: Kirigami.Theme.fixedWidthFont }
                        Row {
                            spacing: 0
                            Repeater { model: 16; delegate: Rectangle { required property int index; width: Kirigami.Units.gridUnit * 1.1; height: Kirigami.Units.gridUnit * 0.8; color: terminal.ansi(index) } }
                        }
                    }
                }
            }
        }
    }
    Component {
        id: cCodigo
        RowLayout {
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: raiz.variantes
                delegate: Rectangle {
                    id: editor
                    required property var modelData
                    readonly property var a: modelData.ansi || []
                    function ansi(i) { return a.length > i ? a[i].hex : "transparent" }
                    readonly property color texto: (modelData.terminal || {}).texto || "transparent"
                    Layout.fillWidth: true
                    implicitHeight: codigo.implicitHeight + Kirigami.Units.largeSpacing * 2
                    radius: Kirigami.Units.cornerRadius
                    color: (modelData.maqueta || {}).fondo_vista || "transparent"
                    Accessible.role: Accessible.Graphic
                    Accessible.name: "Código de muestra en " + modelData.titulo
                    Column {
                        id: codigo
                        anchors.fill: parent
                        anchors.margins: Kirigami.Units.largeSpacing
                        spacing: 2
                        Text { text: editor.modelData.titulo; color: editor.texto; font: Kirigami.Theme.fixedWidthFont; opacity: 0.7 }
                        Row { Text { text: "def "; color: editor.ansi(5); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "contraste"; color: editor.ansi(4); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "(a, b):"; color: editor.texto; font: Kirigami.Theme.fixedWidthFont } }
                        Row { Text { text: "    # WCAG 2.x"; color: (editor.modelData.terminal || {})["texto-tenue"] || "transparent"; font: Kirigami.Theme.fixedWidthFont } }
                        Row { Text { text: "    return "; color: editor.ansi(5); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "(la + 0.05)"; color: editor.texto; font: Kirigami.Theme.fixedWidthFont }
                              Text { text: " / "; color: editor.ansi(6); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "(lb + 0.05)"; color: editor.texto; font: Kirigami.Theme.fixedWidthFont } }
                        Row { Text { text: "print("; color: editor.texto; font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "\"AA\""; color: editor.ansi(2); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: ", "; color: editor.texto; font: Kirigami.Theme.fixedWidthFont }
                              Text { text: "4.5"; color: editor.ansi(3); font: Kirigami.Theme.fixedWidthFont }
                              Text { text: ")"; color: editor.texto; font: Kirigami.Theme.fixedWidthFont } }
                    }
                }
            }
        }
    }
    Component {
        id: cFondos
        Flow {
            spacing: Kirigami.Units.largeSpacing
            Repeater {
                model: studio.centro.fondos
                delegate: ColumnLayout {
                    required property var modelData
                    spacing: Kirigami.Units.smallSpacing / 2
                    RowLayout {
                        spacing: Kirigami.Units.smallSpacing
                        Image { source: modelData.claro; sourceSize.width: Kirigami.Units.gridUnit * 11; asynchronous: true; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: Kirigami.Units.gridUnit * 11; Layout.preferredHeight: Kirigami.Units.gridUnit * 6.2 }
                        Image { source: modelData.oscuro; sourceSize.width: Kirigami.Units.gridUnit * 11; asynchronous: true; fillMode: Image.PreserveAspectFit; Layout.preferredWidth: Kirigami.Units.gridUnit * 11; Layout.preferredHeight: Kirigami.Units.gridUnit * 6.2 }
                    }
                    QQC2.Label { text: modelData.nombre + " · " + modelData.tamanos.join(" · "); color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont }
                }
            }
        }
    }
    Component {
        id: cTipografia
        ColumnLayout {
            spacing: Kirigami.Units.smallSpacing
            QQC2.Label { text: "Tamaño base: " + ((studio.centro.sistema.tipografia || {}).tamano || "—"); color: Kirigami.Theme.disabledTextColor }
            Repeater {
                model: studio.centro.fuentes
                delegate: RowLayout {
                    required property var modelData
                    spacing: Kirigami.Units.largeSpacing
                    QQC2.Label {
                        text: "El veloz murciélago hindú comía feliz cardillo y kiwi — 0123456789"
                        font.family: modelData.familia
                        font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.3
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    QQC2.Label { text: modelData.familia; font.bold: true }
                    EtiquetaEstado {
                        texto: modelData.generica ? "genérica" : modelData.instalada === undefined || modelData.instalada === null ? "sin fc-list" : modelData.instalada ? "instalada" : "no instalada"
                        nivel: modelData.generica ? "" : modelData.instalada ? "positivo" : "neutro"
                    }
                }
            }
        }
    }
    Component {
        id: cIconos
        ColumnLayout {
            spacing: Kirigami.Units.smallSpacing
            Flow {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Repeater {
                    model: (studio.centro.iconos.temas || [])
                    delegate: EtiquetaEstado { required property var modelData; texto: modelData.que + ": " + modelData.tema + (modelData.instalado ? "" : " (falta)"); nivel: modelData.instalado ? "positivo" : "neutro"; icono: "preferences-desktop-icons" }
                }
            }
            Row {
                spacing: Kirigami.Units.largeSpacing
                Repeater {
                    model: ["folder", "folder-documents", "folder-pictures", "folder-download", "text-x-generic", "application-pdf", "utilities-terminal", "system-file-manager"]
                    delegate: Kirigami.Icon { required property string modelData; source: modelData; width: Kirigami.Units.iconSizes.large; height: width }
                }
            }
            QQC2.Label { text: "Los iconos de muestra son los del tema activo del escritorio; los temas de arriba son de terceros (instalar.py dependencias)."; color: Kirigami.Theme.disabledTextColor; font: Kirigami.Theme.smallFont; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
    }
}
