// GENERADO por herramientas/generar.py desde tokens/; no editar.
// Disposición de Llampu: barra superior fina (lanzador, reloj, bandeja) y dock inferior flotante que se
// oculta bajo las ventanas. Se aplica solo si el usuario marca «Disposición del escritorio» al aplicar el tema.

var superior = new Panel;
superior.location = "top";
superior.height = Math.round(gridUnit * 2);           // ≈ 36 px con gridUnit 18
superior.hiding = "none";
superior.floating = false;
superior.addWidget("org.kde.plasma.kickoff");
superior.addWidget("org.kde.plasma.panelspacer");
superior.addWidget("org.kde.plasma.digitalclock");
superior.addWidget("org.kde.plasma.panelspacer");
superior.addWidget("org.kde.plasma.systemtray");

var dock = new Panel;
dock.location = "bottom";
dock.height = Math.round(gridUnit * 3);              // ≈ 56 px
dock.hiding = "windowscover";
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment = "center";
var tareas = dock.addWidget("org.kde.plasma.icontasks");
tareas.currentConfigGroup = ["General"];
tareas.writeConfig("launchers", "applications:org.kde.dolphin.desktop,applications:org.kde.konsole.desktop,applications:systemsettings.desktop");

var escritorios = desktopsForActivity(currentActivity());
for (var i = 0; i < escritorios.length; i++) {
    escritorios[i].wallpaperPlugin = "org.kde.image";
    escritorios[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    escritorios[i].writeConfig("Image", "org.llampu.horizonte");
}
