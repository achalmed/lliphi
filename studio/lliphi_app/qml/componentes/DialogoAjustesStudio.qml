// DialogoAjustesStudio — «Configurar Lliphi Studio…»: la variante de la sesión de prueba, la terminal y el intérprete de las órdenes.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard
import GuiComun

DialogoAjustes {
    id: dialogo
    title: "Configurar Lliphi Studio"
    readonly property var a: ajustes
    modulos: [{ titulo: "General", icono: "configure", pagina: paginaGeneral }]
    onGuardado: { dialogo.a.guardar(); ventana.mensajes.mostrar("Preferencias guardadas.", "positivo") }

    Component {
        id: paginaGeneral
        ColumnLayout {
            function guardar() { dialogo.a.variante = variante.currentValue; dialogo.a.terminal = terminal.text }
            FormCard.FormHeader { title: "Sesión de prueba" }
            FormCard.FormCard {
                FormCard.FormComboBoxDelegate {
                    id: variante
                    text: "Variante con la que arranca el Plasma anidado"
                    model: [{ value: "oscuro", text: "Lliphi Oscuro" }, { value: "claro", text: "Lliphi Claro" }]
                    textRole: "text"
                    valueRole: "value"
                    currentIndex: dialogo.a.variante === "claro" ? 1 : 0
                }
            }
            FormCard.FormHeader { title: "Las órdenes" }
            FormCard.FormCard {
                FormCard.FormTextDelegate { text: "generar.py, instalar.py, sesion.py y paleta.py corren con " + dialogo.a.interprete + (dialogo.a.hayVenv ? " (el .venv del proyecto)." : ". No existe el .venv: Herramientas › El entorno de las órdenes… dice cómo crearlo.") }
                FormCard.FormTextDelegate { text: "Proyecto: " + dialogo.a.raiz + " · Lliphi " + dialogo.a.version }
            }
            FormCard.FormHeader { title: "Sistema" }
            FormCard.FormCard {
                FormCard.FormTextFieldDelegate { id: terminal; label: "Terminal para «Abrir terminal en el proyecto»"; text: dialogo.a.terminal; placeholderText: "konsole" }
            }
        }
    }
}
