"""Temas de Telegram Desktop desde los tokens: `Lliphi Claro.tdesktop-theme` y `Lliphi Oscuro.tdesktop-theme`.

Un `.tdesktop-theme` es un zip con `colors.tdesktop-theme` (líneas `clave: #rrggbb[aa];`) y, si se quiere, el fondo del
chat (`background.*` o, en mosaico, `tiled.*`). Telegram lo aplica al abrirlo. Las claves y su orden salen de la paleta
por omisión de la versión instalada, `fuentes/base/telegram-palette/colors.palette` (lib_ui, GPL-3.0-or-later), que
este módulo solo lee:

- una clave de la tabla `TABLA` toma su color de los tokens (un semántico, un ANSI del grupo `terminal`, con un alfa
  si hace falta, o el valor de otra clave);
- una clave que en la paleta es una referencia (`menuBg: windowBg;`) o tiene respaldo (`#hex | clave`) y no está en la
  tabla hereda, ya resuelto, el color de la clave a la que apunta;
- una clave con un color literal que no está en la tabla es un error: ningún color de Telegram pasa a lo generado.

Todo sale resuelto a `#rrggbb[aa]` (Telegram copia una referencia con el valor que tenga en ese momento, así que un
archivo sin referencias no depende del orden). Las superficies que Telegram pinta siempre oscuras (visor de medios,
llamadas, billetera) toman los tokens del oscuro en las dos variantes (prefijo `o:`); los botones de color con texto
blanco, los del claro (`c:`). Los mensajes propios llevan el acento con alfa sobre el fondo del chat, de modo que la
burbuja es un tinte sobrio del acento y no un color nuevo; el fondo del chat es liso (`tiled.png` de un solo color)
para que el tinte y el contraste no dependan de una imagen. Ningún hex se escribe aquí: la prueba lo comprueba."""
from __future__ import annotations

import re
import struct
import zipfile
import zlib
from pathlib import Path

from nucleo import hexa, semanticos

BASE = Path(__file__).resolve().parents[2] / "fuentes" / "base" / "telegram-palette" / "colors.palette"

# fondo del chat (el mosaico liso) por variante: en el claro, el de ventana (las burbujas de vista resaltan sobre él);
# en el oscuro, el negro de Nothing
FONDO_CHAT = {"claro": "fondo.ventana", "oscuro": "fondo.vista"}

# abreviaturas de la tabla; una tupla es (claro, oscuro)
NEGRO = "fondo.complementario"            # sombras y velos: el casi negro de los tokens
BLANCO = "texto.sobre-acento"             # el blanco de los tokens
PELIGRO = ("estado.error", "acento.base")   # fondo con texto blanco: el error del oscuro es un rojo claro para texto
MUDO = ("texto.inactivo", "borde.separador")  # insignias silenciadas con número blanco
SOBRE_COLOR = (BLANCO, "fondo.vista")     # iniciales e iconos sobre los colores ANSI (oscuros en el claro, claros en el oscuro)

TABLA: dict[str, str | tuple[str, str]] = {
    # básico
    "windowBg": "fondo.vista", "windowFg": "texto.normal", "windowBgOver": "fondo.ventana",
    "windowBgRipple": "fondo.ventana-alterno", "windowSubTextFg": "texto.inactivo", "windowSubTextFgOver": "texto.inactivo",
    "windowBoldFg": "texto.normal", "windowBoldFgOver": "texto.normal", "windowBgActive": "acento.base",
    "windowFgActive": BLANCO, "windowActiveTextFg": "acento.texto", "windowShadowFg": NEGRO,
    "windowShadowFgFallback": "fondo.ventana", "shadowFg": f"{NEGRO}/18", "slideFadeOutBg": f"{NEGRO}/3c",
    "imageBg": NEGRO, "imageBgTransparent": BLANCO,
    # controles
    "activeButtonBgOver": "hover", "activeButtonBgRipple": "acento.suave", "activeButtonSecondaryFg": f"{BLANCO}/b3",
    "activeLineFg": "foco", "activeLineFgError": "estado.error",
    "lightButtonBgOver": "acento.base/14", "lightButtonBgRipple": "acento.base/26",
    "attentionButtonFg": "estado.error", "attentionButtonFgOver": "estado.error",
    "attentionButtonBgOver": "estado.error/14", "attentionButtonBgRipple": "estado.error/26",
    "menuIconFg": "texto.inactivo", "menuIconFgOver": "texto.secundario", "menuSubmenuArrowFg": "texto.secundario",
    "menuFgDisabled": "texto.inactivo/99", "menuSeparatorFg": "borde.sutil",
    "scrollBarBg": "texto.normal/53", "scrollBarBgOver": "texto.normal/7a", "scrollBg": "texto.normal/1a",
    "scrollBgOver": "texto.normal/2c", "smallCloseIconFg": "texto.inactivo", "smallCloseIconFgOver": "texto.secundario",
    "radialBg": f"{NEGRO}/56", "placeholderFgActive": "texto.inactivo/99", "inputBorderFg": "borde.separador",
    "filterInputBorderFg": "foco", "checkboxFg": "texto.inactivo",
    "botKbPrimaryBg": "acento.base/cc", "botKbDangerBg": ("estado.error/cc", "acento.base/cc"),
    "botKbSuccessBg": ("estado.exito/cc", "estado.exito/80"), "botKbInlinePrimaryBg": "acento.base/b3",
    "botKbInlineDangerBg": ("estado.error/b3", "acento.base/b3"), "botKbInlineSuccessBg": ("estado.exito/b3", "estado.exito/80"),
    "sliderBgInactive": "borde.separador", "tooltipBg": "fondo.tooltip", "tooltipFg": "texto.tooltip",
    "tooltipBorderFg": "fondo.tooltip",
    # barra de título propia
    "titleShadow": f"{NEGRO}/03", "titleButtonFg": "texto.inactivo", "titleButtonBgOver": "fondo.ventana-alterno",
    "titleButtonFgOver": "texto.secundario", "titleButtonCloseBgOver": PELIGRO, "titleFg": "texto.inactivo",
    "titleFgActive": "texto.normal",
    # bandeja
    "trayCounterBg": "acento.base", "trayCounterBgMute": MUDO, "trayCounterFg": BLANCO,
    "trayCounterBgMacInvert": BLANCO, "trayCounterFgMacInvert": f"{BLANCO}/01",
    # capas y cuadros
    "layerBg": f"{NEGRO}/7f", "boxTextFgGood": "estado.exito", "boxTextFgError": "estado.error", "boxTitleFg": "texto.normal",
    "boxTitleAdditionalFg": "texto.inactivo", "paymentsTipActive": "estado.exito", "photoCropPointFg": f"{BLANCO}/7f",
    "contactsStatusFgOnline": "estado.exito",
    # inicio de sesión
    "introCoverTopBg": "acento.base", "introCoverBottomBg": "acento.suave", "introCoverIconsFg": f"{BLANCO}/33",
    "introCoverPlaneTrace": f"{BLANCO}/69", "introCoverPlaneInner": "c:fondo.ventana-alterno",
    "introCoverPlaneOuter": "c:borde.separador", "introCoverPlaneTop": BLANCO,
    # lista de chats
    "dialogsDraftFg": "estado.error", "dialogsSendingIconFg": "texto.inactivo", "dialogsSentIconFg": "acento.texto",
    "dialogsUnreadBgMuted": MUDO, "dialogsOnlineBadgeFg": "estado.exito", "dialogsSentIconFgOver": "acento.texto",
    "dialogsBgActive": "seleccion.fondo", "dialogsDraftFgActive": "seleccion.texto/b3",
    "dialogsSendingIconFgActive": "seleccion.texto/99", "dialogsOnlineBadgeFgActive": "seleccion.texto",
    "searchedTextMatchBg": "ansi.color3", "searchedTextMatchFg": "fondo.vista",
    "searchedTextCurrentMatchBg": "acento.base", "searchedTextCurrentMatchFg": BLANCO,
    # historial: paneles
    "emojiPanCategories": "fondo.vista", "emojiPanHeaderBg": "fondo.vista/f2", "emojiIconFg": "texto.inactivo",
    "stickerPanDeleteBg": NEGRO, "stickerPreviewBg": "fondo.vista/b0",
    "stickerPanPremium1": "ansi.color4", "stickerPanPremium2": "ansi.color6",
    # historial: estados de los mensajes
    "historyOutIconFg": "acento.texto", "historyOutIconFgSelected": "acento.texto",
    "historySendingOutIconFg": "acento.texto/99", "historySendingInIconFg": "texto.inactivo",
    "historySendingInvertedIconFg": f"{BLANCO}/c8", "historyCallArrowInFg": "estado.exito",
    "historyCallArrowInFgSelected": "estado.exito", "callArrowFg": "estado.exito", "callArrowMissedFg": "estado.error",
    "historyUnreadBarBg": "fondo.ventana", "historyUnreadBarFg": "acento.texto",
    "historyForwardChooseBg": f"{NEGRO}/4c",
    # historial: los ocho colores de los participantes (nombres y avatares) desde los ANSI; el naranja es la advertencia
    "historyPeer1NameFg": "ansi.color1", "historyPeer1UserpicBg": "ansi.color1", "historyPeer1UserpicBg2": "ansi.color9",
    "historyPeer2NameFg": "ansi.color2", "historyPeer2UserpicBg": "ansi.color2", "historyPeer2UserpicBg2": "ansi.color10",
    "historyPeer3NameFg": "ansi.color3", "historyPeer3UserpicBg": "ansi.color3", "historyPeer3UserpicBg2": "ansi.color11",
    "historyPeer4NameFg": "ansi.color4", "historyPeer4UserpicBg": "ansi.color4", "historyPeer4UserpicBg2": "ansi.color12",
    "historyPeer5NameFg": "ansi.color5", "historyPeer5UserpicBg": "ansi.color5", "historyPeer5UserpicBg2": "ansi.color13",
    "historyPeer6NameFg": "ansi.color13", "historyPeer6UserpicBg": "ansi.color13", "historyPeer6UserpicBg2": "ansi.color5",
    "historyPeer7NameFg": "ansi.color6", "historyPeer7UserpicBg": "ansi.color6", "historyPeer7UserpicBg2": "ansi.color14",
    "historyPeer8NameFg": "estado.advertencia", "historyPeer8UserpicBg": "estado.advertencia",
    "historyPeer8UserpicBg2": "ansi.color3", "historyPeerUserpicFg": SOBRE_COLOR,
    "settingsIconBg1": "ansi.color1", "settingsIconBg2": "ansi.color2", "settingsIconBg3": "estado.advertencia",
    "settingsIconBg4": "ansi.color6", "settingsIconBg5": "ansi.color4", "settingsIconBg6": "ansi.color5",
    "settingsIconBg8": "ansi.color3", "settingsIconBgArchive": MUDO, "settingsIconFg": SOBRE_COLOR,
    # historial: burbujas. Las entrantes, de vista (claro) o de ventana alterna (oscuro); las propias, el acento con
    # alfa sobre el fondo del chat; la selección, el acento más denso
    "historyScrollBarBg": "texto.inactivo/7a", "historyScrollBarBgOver": "texto.inactivo/bc",
    "historyScrollBg": "texto.inactivo/4c", "historyScrollBgOver": "texto.inactivo/6b",
    "msgInBg": ("fondo.vista", "fondo.ventana-alterno"), "msgInBgSelected": ("acento.base/40", "acento.base/66"),
    "msgOutBg": ("acento.base/26", "acento.base/33"), "msgOutBgSelected": ("acento.base/4d", "acento.base/66"),
    "msgSelectOverlay": "acento.base/4c", "msgStickerOverlay": "acento.base/7f",
    "msgInServiceFg": "acento.texto", "msgInServiceFgSelected": "acento.texto",
    "msgOutServiceFg": "acento.texto", "msgOutServiceFgSelected": "acento.texto",
    "msgInShadow": f"{NEGRO}/29", "msgInShadowSelected": f"{NEGRO}/29", "msgOutShadow": f"{NEGRO}/1d",
    "msgOutShadowSelected": f"{NEGRO}/22",
    "msgInDateFg": "texto.inactivo", "msgInDateFgSelected": "texto.secundario",
    "msgOutDateFg": "acento.texto", "msgOutDateFgSelected": "acento.texto",
    "msgServiceFg": "texto.tooltip", "msgServiceBg": ("fondo.tooltip/b3", "fondo.tooltip/cc"),
    "msgServiceBgSelected": "acento.base/a2",
    "msgOutReplyBarColor": "acento.texto", "msgInMonoFg": "ansi.color6", "msgOutMonoFg": ("ansi.color14", "ansi.color6"),
    "msgDateImgBg": f"{NEGRO}/54", "msgDateImgBgOver": f"{NEGRO}/74", "msgDateImgBgSelected": "acento.base/87",
    "msgFileThumbLinkOutFg": "acento.texto", "msgFileThumbLinkOutFgSelected": "acento.texto",
    "msgFileInBgOver": "acento.suave", "msgFileInBgSelected": "acento.suave",
    "msgFileOutBg": "acento.base", "msgFileOutBgSelected": "acento.suave",
    "msgFile1Bg": "ansi.color4", "msgFile1BgDark": "ansi.color12", "msgFile1BgOver": "ansi.color12", "msgFile1BgSelected": "ansi.color12",
    "msgFile2Bg": "ansi.color2", "msgFile2BgDark": "ansi.color10", "msgFile2BgOver": "ansi.color10", "msgFile2BgSelected": "ansi.color10",
    "msgFile3Bg": "ansi.color1", "msgFile3BgDark": "ansi.color9", "msgFile3BgOver": "ansi.color9", "msgFile3BgSelected": "ansi.color9",
    "msgFile4Bg": "ansi.color3", "msgFile4BgDark": "ansi.color11", "msgFile4BgOver": "ansi.color11", "msgFile4BgSelected": "ansi.color11",
    # las flechas de descarga van en blanco sobre los círculos de acento y los velos oscuros (por omisión, el fondo
    # de la burbuja, que con alfa dejaría la flecha translúcida)
    "historyFileInIconFg": BLANCO, "historyFileInIconFgSelected": BLANCO, "historyFileOutIconFg": BLANCO,
    "historyFileOutIconFgSelected": BLANCO, "historyFileThumbIconFg": BLANCO, "historyFileThumbIconFgSelected": BLANCO,
    "msgWaveformInActiveSelected": "acento.suave", "msgWaveformInInactive": "borde.separador",
    "msgWaveformInInactiveSelected": "acento.base/66", "msgWaveformOutActive": "acento.texto",
    "msgWaveformOutActiveSelected": "acento.texto", "msgWaveformOutInactive": "acento.base/4d",
    "msgWaveformOutInactiveSelected": "acento.base/66", "msgBotKbOverBgAdd": f"{BLANCO}/20",
    "msgBotKbRippleBg": f"{NEGRO}/20", "youtubePlayIconBg": ("estado.error/c8", "acento.base/c8"),
    "videoPlayIconBg": f"{NEGRO}/7f", "videoPlayIconFg": BLANCO, "toastBg": "fondo.tooltip/e5", "toastFg": "texto.tooltip",
    "historyToDownShadow": f"{NEGRO}/40", "historyComposeAreaBg": "fondo.vista", "mapPointDrop": PELIGRO, "mapPointDot": BLANCO,
    # vistas generales, perfil y ajustes
    "overviewCheckBg": f"{NEGRO}/40", "overviewPhotoSelectOverlay": "acento.base/33", "profileStatusFgOver": "texto.secundario",
    "mediaPlayerDisabledFg": "acento.base/66",
    # visor de medios (siempre oscuro)
    "mediaviewFileRedCornerFg": "ansi.color1", "mediaviewFileYellowCornerFg": "estado.advertencia",
    "mediaviewFileGreenCornerFg": "ansi.color2", "mediaviewFileBlueCornerFg": "ansi.color4",
    "mediaviewMenuBg": "o:fondo.ventana-alterno", "mediaviewMenuBgOver": "o:fondo.boton", "mediaviewMenuBgRipple": "o:borde.separador",
    "mediaviewBg": "o:fondo.vista/eb", "mediaviewControlBg": f"{NEGRO}/3c", "mediaviewControlFg": "o:texto.normal",
    "mediaviewCaptionBg": f"{NEGRO}/80", "mediaviewTextLinkFg": "o:enlace", "mediaviewPlaybackActive": "o:texto.secundario",
    "mediaviewPlaybackInactive": "o:fondo.ventana-alterno", "mediaviewPlaybackActiveOver": "o:texto.normal",
    "mediaviewPlaybackInactiveOver": "o:borde.separador", "mediaviewPlaybackProgressFg": "o:texto.normal/c7",
    "mediaviewPlaybackIconRipple": "o:texto.normal/14", "mediaviewPipControlsFg": "o:texto.normal/d9",
    "mediaviewPipControlsFgOver": "o:texto.normal", "mediaviewPipPlaybackActive": "o:texto.normal/da",
    "mediaviewPipPlaybackInactive": "o:texto.normal/26", "mediaviewTransparentBg": BLANCO,
    "mediaviewTransparentFg": "c:borde.separador",
    # llamadas (siempre oscuras); contestar en el verde del claro y colgar en el rojo de Nothing, los dos con icono blanco
    "callBg": "o:fondo.ventana/f2", "callBgOpaque": "o:fondo.ventana", "callBgButton": "o:fondo.ventana/7f",
    "callNameFg": "o:texto.normal", "callStatusFg": "o:texto.inactivo", "callIconBg": "o:texto.normal/1f",
    "callIconFg": "o:texto.normal", "callIconBgActive": "o:texto.normal/e5", "callIconFgActive": "o:fondo.ventana",
    "callIconActiveRipple": "o:texto.secundario", "callAnswerBg": "c:estado.exito", "callAnswerRipple": "o:estado.exito",
    "callAnswerBgOuter": "c:estado.exito/26", "callHangupBg": "o:acento.base", "callHangupRipple": "o:acento.suave",
    "callMuteRipple": "o:texto.normal/12",
    "groupCallBg": "o:fondo.vista", "groupCallActiveFg": "o:enlace", "groupCallMembersBg": "o:fondo.ventana",
    "groupCallMembersBgOver": "o:fondo.ventana-alterno", "groupCallMembersBgRipple": "o:fondo.boton",
    "groupCallMembersFg": "o:texto.normal", "groupCallMemberActiveIcon": "o:estado.exito",
    "groupCallMemberActiveStatus": "o:estado.exito", "groupCallMemberInactiveIcon": "o:texto.inactivo",
    "groupCallMemberInactiveStatus": "o:estado.info", "groupCallMemberMutedIcon": "o:estado.error",
    "groupCallMemberNotJoinedStatus": "o:texto.inactivo", "groupCallIconFg": "o:texto.normal",
    "groupCallLive1": "c:estado.exito", "groupCallLive2": "o:estado.exito", "groupCallMuted1": "c:acento.base",
    "groupCallMuted2": "c:acento.suave", "groupCallForceMutedBar1": "o:acento.base", "groupCallForceMutedBar2": "o:acento.suave",
    "groupCallForceMutedBar3": "c:acento.suave", "groupCallForceMuted1": "c:acento.suave", "groupCallForceMuted2": "o:acento.suave",
    "groupCallForceMuted3": "o:acento.base", "groupCallMenuBg": "o:fondo.ventana-alterno", "groupCallMenuBgOver": "o:fondo.boton",
    "groupCallMenuBgRipple": "o:borde.separador", "groupCallLeaveBg": "o:acento.base/7f",
    "groupCallLeaveBgRipple": "o:acento.base/9e", "groupCallVideoTextFg": "o:texto.normal/e0",
    "groupCallVideoSubTextFg": "o:texto.normal/c0",
    # avisos del sistema operativo y ortografía
    "outdatedFg": BLANCO, "outdateSoonBg": "c:estado.advertencia", "outdatedBg": "c:estado.error",
    "spellUnderline": "estado.error/88",
    # billetera (siempre oscura)
    "walletTitleBg": "o:fondo.vista", "walletTitleButtonFg": "o:texto.inactivo", "walletTitleButtonBgOver": "o:fondo.boton",
    "walletTitleButtonFgOver": "o:texto.secundario", "walletTopBg": "o:fondo.ventana", "walletBalanceFg": "o:texto.normal",
    "walletSubBalanceFg": "o:texto.normal", "walletTopLabelFg": "o:texto.inactivo", "walletTopIconRipple": "o:texto.normal/12",
    # barra lateral de carpetas: la de ventana de Plasma, no el azul marino de Telegram
    "sideBarBg": "fondo.ventana", "sideBarBgActive": "fondo.ventana-alterno", "sideBarBgRipple": "borde.separador",
    "sideBarTextFg": "texto.secundario", "sideBarTextFgActive": "acento.texto", "sideBarIconFg": "texto.inactivo",
    "sideBarIconFgActive": "acento.texto", "sideBarBadgeBg": "acento.base", "sideBarBadgeBgMuted": MUDO,
    "sideBarBadgeFg": BLANCO,
    # varios: degradados de Premium y de las estrellas, gráficos de estadísticas, insignias
    "songCoverOverlayFg": f"{NEGRO}/66", "photoEditorItemBaseHandleFg": "acento.base",
    "premiumButtonBg1": "c:ansi.color4", "premiumButtonBg2": "c:ansi.color5", "premiumButtonBg3": "c:ansi.color13",
    "premiumButtonFg": BLANCO, "premiumIconBg1": "c:estado.advertencia", "premiumIconBg2": "c:ansi.color1",
    "premiumIconBg3": "c:ansi.color2",
    "statisticsChartInactive": "fondo.ventana/99", "statisticsChartActive": "borde.separador/d8",
    "statisticsChartLineBlue": "ansi.color4", "statisticsChartLineGreen": "ansi.color2", "statisticsChartLineRed": "ansi.color1",
    "statisticsChartLineGolden": "ansi.color3", "statisticsChartLineLightblue": "ansi.color12",
    "statisticsChartLineLightgreen": "ansi.color10", "statisticsChartLineOrange": "estado.advertencia",
    "statisticsChartLineIndigo": "acento.suave", "statisticsChartLinePurple": "ansi.color5", "statisticsChartLineCyan": "ansi.color6",
    "creditsBg1": "o:estado.advertencia", "creditsBg2": "o:ansi.color11", "creditsBg3": "o:ansi.color3",
    "creditsFg": "estado.advertencia", "creditsStroke": "c:ansi.color3", "currencyFg": "acento.texto",
    "rankAdminFg": "estado.exito", "rankOwnerFg": "ansi.color5",
}

LINEA = re.compile(r"^([A-Za-z]\w*)\s*:\s*([^;|]+?)\s*(?:\|\s*([A-Za-z]\w*)\s*)?;")


def plantilla(ruta: Path = BASE) -> list[tuple[str, str, str | None]]:
    """(clave, valor por omisión, clave de respaldo) de cada color de la paleta de Telegram, en su orden."""
    salida = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = LINEA.match(linea)
        if m:
            salida.append((m[1], m[2], m[3]))
    return salida


def token(tokens: dict, variante: str, spec: str | tuple[str, str]) -> str:
    """Una entrada de la tabla → `#rrggbb[aa]`: `[c:|o:]<semántico o ansi.colorN>[/<alfa>]`."""
    if isinstance(spec, tuple):
        spec = spec[0 if variante == "claro" else 1]
    nombre, _, alfa = spec.partition("/")
    if nombre[:2] in ("c:", "o:"):
        variante, nombre = ("claro" if nombre[0] == "c" else "oscuro"), nombre[2:]
    if nombre.startswith("ansi."):
        h = hexa(tokens["terminal"][variante][nombre[5:]])
    else:
        h = semanticos(tokens, variante)[nombre]
    return h.lower() + alfa.lower()


def colores(tokens: dict, variante: str) -> dict[str, str]:
    """Clave de Telegram → `#rrggbb[aa]`, todas resueltas, en el orden de la paleta."""
    filas = plantilla()
    por_clave = {k: (v, r) for k, v, r in filas}
    hechos: dict[str, str] = {}

    def resolver(clave: str, camino: tuple[str, ...] = ()) -> str:
        if clave in hechos:
            return hechos[clave]
        if clave in camino:
            raise ValueError("referencia circular: " + " → ".join((*camino, clave)))
        valor, respaldo = por_clave[clave]
        if clave in TABLA:
            color = token(tokens, variante, TABLA[clave])
        elif not valor.startswith("#"):
            color = resolver(valor, (*camino, clave))
        elif respaldo:
            color = resolver(respaldo, (*camino, clave))
        else:
            raise KeyError(f"Telegram: la clave {clave} tiene un color propio ({valor}) y no está en TABLA")
        hechos[clave] = color
        return color

    return {k: resolver(k) for k, _, _ in filas}


def texto_colores(tokens: dict, marca: dict, variante: str) -> str:
    c = colores(tokens, variante)
    cabecera = (f"// {marca['nombre_esquema'][variante]} para Telegram Desktop.\n"
                f"// GENERADO por herramientas/generar.py (complementos/telegram) desde tokens/; no editar.\n"
                f"// Claves y orden: la paleta de lib_ui de Telegram Desktop 7.3.3 (GPL-3.0-or-later); colores de "
                f"{marca['nombre']} ({marca['licencia_activos']}). {marca['repositorio']}\n\n")
    return cabecera + "".join(f"{k}: {v};\n" for k, v in c.items())


def png_liso(hex6: str, lado: int = 16) -> bytes:
    """PNG RGB de un solo color, byte a byte igual en cada generación (sin Pillow)."""
    r, g, b = (int(hex6.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    datos = zlib.compress((b"\x00" + bytes((r, g, b)) * lado) * lado, 9)

    def trozo(tipo: bytes, cuerpo: bytes) -> bytes:
        return struct.pack(">I", len(cuerpo)) + tipo + cuerpo + struct.pack(">I", zlib.crc32(tipo + cuerpo) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", lado, lado, 8, 2, 0, 0, 0))
            + trozo(b"IDAT", datos) + trozo(b"IEND", b""))


def fondo_chat(tokens: dict, variante: str) -> str:
    return semanticos(tokens, variante)[FONDO_CHAT[variante]]


def empaquetar(archivos: dict[str, bytes], destino: Path) -> None:
    """Zip reproducible (fechas y permisos fijos, orden alfabético): la prueba de deriva compara bytes."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre in sorted(archivos):
            info = zipfile.ZipInfo(nombre, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, archivos[nombre])


def generar(tokens: dict, marca: dict, destino: Path) -> list[Path]:
    hechos: list[Path] = []
    for v in ("claro", "oscuro"):
        archivos = {"colors.tdesktop-theme": texto_colores(tokens, marca, v).encode("utf-8"),
                    "tiled.png": png_liso(fondo_chat(tokens, v))}
        for nombre, datos in archivos.items():     # el contenido suelto, para leerlo y compararlo en el repositorio
            ruta = destino / v / nombre
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(datos)
            hechos.append(ruta)
        paquete = destino / f"{marca['nombre_esquema'][v]}.tdesktop-theme"
        empaquetar(archivos, paquete)
        hechos.append(paquete)
    return hechos
