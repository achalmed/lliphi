// Maqueta — lo que Lliphi pinta, dibujado con los tokens de una variante. Tres formas (`tipo`):
//   escritorio  la mesa de diseño (rediseño del 2026-11-18): el fondo que pone la disposición, la barra superior fina
//               (lanzador, ventana activa, bandeja y reloj), una ventana con su decoración, una Konsole con los 16 ANSI,
//               una notificación y el dock flotante, con los radios, las opacidades y las familias de los tokens;
//   ventana     una ventana sola (las páginas de esquemas y Plasma): barra de título, barra lateral, una vista con filas
//               alternas y una elegida, un enlace, los estados, un tooltip y los botones;
//   controles   la misma ventana con los controles que pinta Kvantum (campo, casilla, deslizador, botones).
// Todo color, radio y familia de aquí dentro es un DATO de tokens/tokens.json (servicios/diseno.py: `colores` son los
// semánticos; `variante`, la variante entera; `escritorio`, radios, opacidades y familias): enseña el tema, no viste la
// ventana del studio, que sigue a Kirigami.Theme. Cambian los tokens y la maqueta se repinta (studio.centro los vigila).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Item {
    id: raiz
    property var colores: ({})
    property var variante: ({})
    property var escritorio: ({})
    property string titulo: ""
    property string tipo: "ventana"          // "escritorio" · "ventana" · "controles" (Kvantum)
    readonly property var c: colores || ({})
    readonly property var e: escritorio || ({})
    readonly property var r: e.radios || ({})
    readonly property var t: (variante || {}).terminal || ({})
    readonly property string familia: e.familia || Kirigami.Theme.defaultFont.family
    readonly property string mono: e.mono || Kirigami.Theme.fixedWidthFont.family
    function ansi(i) { const a = (raiz.variante || {}).ansi || []; return a.length > i ? a[i].hex : "transparent" }
    function radio(nombre) { return raiz.r[nombre] !== undefined ? raiz.r[nombre] : Kirigami.Units.cornerRadius }

    implicitWidth: Kirigami.Units.gridUnit * 22
    implicitHeight: Kirigami.Units.gridUnit * 14
    Accessible.role: Accessible.Graphic
    Accessible.name: (tipo === "escritorio" ? "Maqueta del escritorio en " : "Vista previa de ") + titulo + " pintada con sus tokens"

    // ------------------------------------------------------------------ una ventana o sus controles, sola
    Ventana {
        anchors.fill: parent
        visible: raiz.tipo !== "escritorio"
        contenido: raiz.tipo
        nombre: raiz.titulo
    }

    // ------------------------------------------------------------------ el escritorio
    Item {
        id: mesa
        anchors.fill: parent
        visible: raiz.tipo === "escritorio"
        clip: true

        Rectangle { anchors.fill: parent; color: raiz.c.fondo_ventana || "transparent" }
        Image {
            anchors.fill: parent
            source: mesa.visible ? ((raiz.variante || {}).fondo || "") : ""
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            sourceSize.width: 1600
        }

        // la barra superior fina de la disposición: lanzador, la ventana activa, la bandeja y el reloj
        Rectangle {
            id: barraSuperior
            width: parent.width
            height: Kirigami.Units.gridUnit * 1.3
            color: Qt.alpha(raiz.c.fondo_ventana || "transparent", raiz.e.opacidadPanel || 1)
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.largeSpacing
                Text { text: "●"; color: raiz.c.acento_base || "transparent"; font.family: raiz.familia }
                Text { text: "Dolphin"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia; font.bold: true }
                Text { text: "Archivo   Editar   Ver"; color: raiz.c.texto_secundario || "transparent"; font.family: raiz.familia }
                Item { Layout.fillWidth: true }
                Text { text: "◐  ▲  ♪"; color: raiz.c.texto_secundario || "transparent"; font.family: raiz.familia }
                Text { text: "mié 18 nov  10:42"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia }
            }
        }

        Ventana {
            x: mesa.width * 0.05
            y: barraSuperior.height + mesa.height * 0.06
            width: mesa.width * 0.6
            height: mesa.height * 0.58
            contenido: "ventana"
            nombre: "Documentos — Dolphin"
        }

        // Konsole, con los colores de la terminal y los 16 ANSI
        Rectangle {
            x: mesa.width * 0.47
            y: mesa.height * 0.42
            width: mesa.width * 0.48
            height: mesa.height * 0.38
            radius: raiz.radio("ventana")
            color: raiz.t.fondo || "transparent"
            border.width: 1
            border.color: raiz.c.borde_separador || "transparent"
            clip: true
            Rectangle {
                id: tituloKonsole
                width: parent.width
                height: Kirigami.Units.gridUnit * 1.5
                radius: parent.radius
                color: raiz.c.fondo_encabezado || "transparent"
                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: parent.radius; color: parent.color }
                Botones { anchors.left: parent.left; anchors.leftMargin: Kirigami.Units.largeSpacing; anchors.verticalCenter: parent.verticalCenter }
                Text { anchors.centerIn: parent; text: "~/proyectos — Konsole"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia; font.bold: true }
            }
            Column {
                anchors.top: tituloKonsole.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: Kirigami.Units.largeSpacing
                spacing: 2
                Row {
                    Text { text: "usuario@lliphi"; color: raiz.ansi(2); font.family: raiz.mono }
                    Text { text: ":"; color: raiz.t.texto || "transparent"; font.family: raiz.mono }
                    Text { text: "~/proyectos"; color: raiz.ansi(4); font.family: raiz.mono }
                    Text { text: "$ git status"; color: raiz.t.texto || "transparent"; font.family: raiz.mono }
                }
                Text { text: "  modificado:   tokens.json"; color: raiz.ansi(1); font.family: raiz.mono }
                Text { text: "  nuevo:        lliphi.colors"; color: raiz.ansi(2); font.family: raiz.mono }
                Text { text: "aviso: 2 archivos sin preparar"; color: raiz.ansi(3); font.family: raiz.mono }
                Text { text: "# un comentario tenue"; color: raiz.t["texto-tenue"] || "transparent"; font.family: raiz.mono }
                Row {
                    topPadding: Kirigami.Units.smallSpacing
                    Repeater {
                        model: 16
                        delegate: Rectangle { required property int index; width: Kirigami.Units.gridUnit * 0.9; height: Kirigami.Units.gridUnit * 0.7; color: raiz.ansi(index) }
                    }
                }
            }
        }

        // una notificación de Plasma (los diálogos del shell, con su opacidad)
        Rectangle {
            anchors.right: parent.right
            anchors.top: barraSuperior.bottom
            anchors.margins: Kirigami.Units.largeSpacing
            width: Math.min(mesa.width * 0.3, Kirigami.Units.gridUnit * 16)
            height: aviso.implicitHeight + Kirigami.Units.largeSpacing * 2
            radius: raiz.radio("menu")
            color: Qt.alpha(raiz.c.fondo_ventana || "transparent", raiz.e.opacidadDialogo || 1)
            border.width: 1
            border.color: raiz.c.borde_sutil || "transparent"
            Column {
                id: aviso
                anchors.fill: parent
                anchors.margins: Kirigami.Units.largeSpacing
                spacing: 2
                Text { text: "Lliphi"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia; font.bold: true }
                Text { width: parent.width; text: "Lo generado está al día"; color: raiz.c.texto_secundario || "transparent"; font.family: raiz.familia; elide: Text.ElideRight }
                Rectangle {
                    width: parent.width; height: 3
                    color: raiz.c.borde_sutil || "transparent"
                    Rectangle { width: parent.width * 0.7; height: parent.height; color: raiz.c.acento_base || "transparent" }
                }
            }
        }

        // el dock flotante de la disposición, abajo y al centro
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: Kirigami.Units.largeSpacing
            width: dock.implicitWidth + Kirigami.Units.largeSpacing * 2
            height: Kirigami.Units.gridUnit * 2.6
            radius: raiz.radio("panel_flotante")
            color: Qt.alpha(raiz.c.fondo_ventana || "transparent", raiz.e.opacidadPanel || 1)
            border.width: 1
            border.color: raiz.c.borde_sutil || "transparent"
            Row {
                id: dock
                anchors.centerIn: parent
                spacing: Kirigami.Units.largeSpacing
                Repeater {
                    model: ["system-file-manager", "utilities-terminal", "internet-web-browser", "accessories-text-editor", "preferences-system"]
                    delegate: Item {
                        required property string modelData
                        required property int index
                        width: Kirigami.Units.iconSizes.medium
                        height: Kirigami.Units.gridUnit * 2.2
                        Kirigami.Icon { source: modelData; width: Kirigami.Units.iconSizes.medium; height: width; anchors.top: parent.top }
                        Rectangle {                         // la marca de la ventana abierta: un trazo, como en el dock
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            visible: index < 2
                            width: Kirigami.Units.smallSpacing * 2
                            height: 2
                            color: index === 0 ? (raiz.c.acento_base || "transparent") : (raiz.c.texto_inactivo || "transparent")
                        }
                    }
                }
            }
        }
    }

    // los botones de la decoración (cerrar en el acento; minimizar y maximizar en el gris inactivo)
    component Botones: Row {
        spacing: Kirigami.Units.smallSpacing
        Repeater {
            model: [raiz.c.acento_base, raiz.c.texto_inactivo, raiz.c.texto_inactivo]
            delegate: Text { required property var modelData; text: "●"; color: modelData || "transparent"; font.family: raiz.familia }
        }
    }

    // una ventana de Lliphi: la decoración, la barra lateral y la vista (o los controles de Kvantum)
    component Ventana: Rectangle {
        id: ventana
        property string contenido: "ventana"
        property string nombre: ""
        radius: raiz.radio("ventana")
        color: raiz.c.fondo_ventana || "transparent"
        border.width: 1
        border.color: raiz.c.borde_separador || "transparent"
        clip: true

        Rectangle {
            id: barra
            width: parent.width
            height: Kirigami.Units.gridUnit * 1.6
            color: raiz.c.fondo_encabezado || "transparent"
            radius: ventana.radius
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: parent.radius; color: parent.color }
            Botones { anchors.left: parent.left; anchors.leftMargin: Kirigami.Units.largeSpacing; anchors.verticalCenter: parent.verticalCenter }
            Text { anchors.centerIn: parent; text: ventana.nombre; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia; font.bold: true }
        }

        RowLayout {
            anchors.top: barra.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.bottomMargin: ventana.radius / 2
            spacing: 0
            // barra lateral
            Column {
                Layout.fillHeight: true
                Layout.preferredWidth: Kirigami.Units.gridUnit * 6
                leftPadding: Kirigami.Units.smallSpacing
                rightPadding: Kirigami.Units.smallSpacing
                topPadding: Kirigami.Units.smallSpacing
                spacing: 2
                Repeater {
                    model: ["Inicio", "Documentos", "Imágenes", "Música"]
                    delegate: Rectangle {
                        required property string modelData
                        required property int index
                        width: Kirigami.Units.gridUnit * 6 - Kirigami.Units.smallSpacing * 2
                        height: Kirigami.Units.gridUnit * 1.3
                        radius: raiz.radio("control")
                        color: index === 1 ? (raiz.c.seleccion_fondo || "transparent") : "transparent"
                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            x: Kirigami.Units.smallSpacing
                            text: modelData
                            font.family: raiz.familia
                            color: index === 1 ? (raiz.c.seleccion_texto || "transparent") : (raiz.c.texto_normal || "transparent")
                        }
                    }
                }
            }
            Rectangle { Layout.fillHeight: true; Layout.preferredWidth: 1; color: raiz.c.borde_separador || "transparent" }
            // la vista
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: raiz.c.fondo_vista || "transparent"
                clip: true
                Column {
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing
                    spacing: Kirigami.Units.smallSpacing
                    visible: ventana.contenido === "ventana"
                    Repeater {
                        model: ["informe.pdf", "notas.md", "paleta.json"]
                        delegate: Rectangle {
                            required property string modelData
                            required property int index
                            width: parent.width
                            height: Kirigami.Units.gridUnit * 1.2
                            radius: raiz.radio("control")
                            color: index % 2 ? (raiz.c.fondo_vista_alterno || "transparent") : "transparent"
                            Text { anchors.verticalCenter: parent.verticalCenter; x: Kirigami.Units.smallSpacing; text: modelData; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia }
                            Text { anchors.verticalCenter: parent.verticalCenter; anchors.right: parent.right; anchors.rightMargin: Kirigami.Units.smallSpacing; text: "hoy"; color: raiz.c.texto_secundario || "transparent"; font.family: raiz.familia }
                        }
                    }
                    Text { text: "Un enlace a la documentación"; color: raiz.c.enlace || "transparent"; font.underline: true; font.family: raiz.familia }
                    Row {
                        spacing: Kirigami.Units.smallSpacing
                        Repeater {
                            model: [["Error", raiz.c.estado_error], ["Aviso", raiz.c.estado_advertencia], ["Hecho", raiz.c.estado_exito], ["Info", raiz.c.estado_info]]
                            delegate: Text { required property var modelData; text: modelData[0]; color: modelData[1] || "transparent"; font.bold: true; font.family: raiz.familia }
                        }
                    }
                }
                // los controles (Kvantum): campo, casilla, deslizador
                Column {
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing * 2
                    spacing: Kirigami.Units.smallSpacing * 2
                    visible: ventana.contenido === "controles"
                    Rectangle {
                        width: parent.width; height: Kirigami.Units.gridUnit * 1.4; radius: raiz.radio("control")
                        color: raiz.c.fondo_vista || "transparent"; border.width: 1; border.color: raiz.c.foco || "transparent"
                        Text { anchors.verticalCenter: parent.verticalCenter; x: Kirigami.Units.smallSpacing; text: "Buscar…"; color: raiz.c.texto_inactivo || "transparent"; font.family: raiz.familia }
                    }
                    Row {
                        spacing: Kirigami.Units.smallSpacing
                        Rectangle {
                            width: Kirigami.Units.gridUnit * 0.9; height: width; radius: raiz.radio("control") / 2; color: raiz.c.acento_base || "transparent"
                            Text { anchors.centerIn: parent; text: "✓"; color: raiz.c.texto_sobre_acento || "transparent"; font.family: raiz.familia }
                        }
                        Text { text: "Casilla marcada"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia }
                    }
                    Rectangle {
                        width: parent.width; height: 4; radius: height / 2; color: raiz.c.fondo_boton || "transparent"
                        Rectangle { width: parent.width * 0.6; height: parent.height; radius: height / 2; color: raiz.c.acento_base || "transparent" }
                    }
                }
                // botones y tooltip
                Row {
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.margins: Kirigami.Units.smallSpacing
                    spacing: Kirigami.Units.smallSpacing
                    Rectangle {
                        width: cancelar.implicitWidth + Kirigami.Units.largeSpacing * 2; height: Kirigami.Units.gridUnit * 1.4; radius: raiz.radio("control")
                        color: raiz.c.fondo_boton || "transparent"; border.width: 1; border.color: raiz.c.borde_sutil || "transparent"
                        Text { id: cancelar; anchors.centerIn: parent; text: "Cancelar"; color: raiz.c.texto_normal || "transparent"; font.family: raiz.familia }
                    }
                    Rectangle {
                        width: aceptar.implicitWidth + Kirigami.Units.largeSpacing * 2; height: Kirigami.Units.gridUnit * 1.4; radius: raiz.radio("control")
                        color: raiz.c.acento_base || "transparent"
                        Text { id: aceptar; anchors.centerIn: parent; text: "Aceptar"; color: raiz.c.texto_sobre_acento || "transparent"; font.bold: true; font.family: raiz.familia }
                    }
                }
                Rectangle {
                    visible: ventana.contenido === "ventana"
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: Kirigami.Units.smallSpacing
                    width: consejo.implicitWidth + Kirigami.Units.largeSpacing * 2; height: consejo.implicitHeight + Kirigami.Units.smallSpacing * 2
                    radius: Math.min(raiz.radio("menu"), height / 2)
                    color: raiz.c.fondo_tooltip || "transparent"
                    Text { id: consejo; anchors.centerIn: parent; text: "Un tooltip"; color: raiz.c.texto_tooltip || raiz.c.texto_normal || "transparent"; font.family: raiz.familia }
                }
            }
        }
    }
}
