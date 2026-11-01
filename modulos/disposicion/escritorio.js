// Disposición de @NOMBRE@: los paneles y sus widgets salen de modulos/disposicion/ajustes.json (por omisión, barra
// superior fina y dock inferior flotante que se aparta de las ventanas). Se aplica solo si el usuario marca
// «Disposición del escritorio» al aplicar el tema (o con plasma-apply-lookandfeel --resetLayout).

var paneles = @PANELES@;

for (var i = 0; i < paneles.length; i++) {
    var d = paneles[i];
    var panel = new Panel;
    panel.location = d.ubicacion;
    panel.height = Math.round(gridUnit * d.alto);      // gridUnit ≈ 18 px
    panel.hiding = d.ocultar;                          // none · autohide · dodgewindows · windowsgobelow
    panel.floating = d.flotante;
    if (d.longitud) panel.lengthMode = d.longitud;
    if (d.alineacion) panel.alignment = d.alineacion;
    for (var j = 0; j < d.widgets.length; j++) {
        var w = d.widgets[j];
        var widget = panel.addWidget(w.tipo);
        for (var grupo in (w.config || {})) {
            widget.currentConfigGroup = grupo.split("/");
            for (var clave in w.config[grupo]) widget.writeConfig(clave, w.config[grupo][clave]);
        }
    }
}

var escritorios = desktopsForActivity(currentActivity());
for (var k = 0; k < escritorios.length; k++) {
    escritorios[k].wallpaperPlugin = "org.kde.image";
    escritorios[k].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    // por ruta del paquete: en Plasma 6.6 el nombre de un paquete de usuario no se resolvía (docs/validacion.md §3);
    // con un solo argumento, userDataPath devuelve la carpeta de datos y no la de fondos: el tipo va primero (validacion.md §9)
    escritorios[k].writeConfig("Image", "file://" + userDataPath("data", "wallpapers") + "/@FONDO@");
}
