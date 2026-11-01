# Tema global (`global`)

El proyecto principal de Lliphi: los dos paquetes **Plasma/LookAndFeel** `org.lliphi.claro` y `org.lliphi.oscuro`,
que integran los seis módulos y permiten aplicarlos juntos desde Preferencias del sistema → Tema global o con
`plasma-apply-lookandfeel`. Arquitectura completa: [`docs/arquitectura.md`](../docs/arquitectura.md).

## Responsabilidad

| hace | no hace |
|---|---|
| Declara qué componentes forman el tema (`contents/defaults`), con los identificadores que cada módulo le da | Copiar dentro de sí los paquetes de otros módulos: esquema, estilo, decoración, fondo y Kvantum se instalan en su propio sitio de KDE |
| Integra lo que KDE exige dentro del paquete: pantalla de carga y de salida (`carga-bloqueo`) y disposición (`disposicion`) | Dibujar el bloqueo de pantalla: en Plasma 6.6 su interfaz es del paquete de shell |
| Pone lo suyo: metadatos, tipografía (Inter, Inter Medium, JetBrains Mono Nerd Font) y vistas previas | Escribir en línea identificadores ajenos (lo vigila `test_defaults_compuestos_por_los_modulos`) |
| Aplica el tema en la sesión (`aplicar.py`) y declara qué configuración se respalda antes | Instalar lo de terceros por su cuenta: lo nombra y `externas.py` lo trae a petición |

## Estructura

```
global/
├── modulo.json      manifiesto: clase paquete, formato Plasma/LookAndFeel, integra y referencia, instalación
├── construir.py     metadata.json, composición de contents/defaults, integración de componentes, vistas previas
├── aplicar.py       plasma-apply-lookandfeel, menús de Breeze, tipografía en vivo; CONFIGS que se respaldan
├── externas.py      tipografía de terceros: JetBrains Mono Nerd Font (descarga) e Inter (comprobación)
├── INSTALL.md       instalación a mano (la publica el sitio)
└── README.md
```

Lo generado: `generado/global/org.lliphi.{claro,oscuro}/` (`metadata.json`, `contents/defaults`,
`contents/{splash,logout,layouts,previews}/`).

## Cómo se compone `contents/defaults`

Cada módulo expone `valores(marca, variante)` en su `construir.py` con las claves de las que es dueño:

| grupo | clave | dueño |
|---|---|---|
| `[kdeglobals][KDE]` | `widgetStyle` | `kvantum` |
| `[kdeglobals][Icons]` | `Theme` | `iconos-cursores` |
| `[kdeglobals][General]` | `ColorScheme` | `esquema` |
| `[kdeglobals][General]`, `[kdeglobals][WM]` | tipografía | `global` |
| `[plasmarc][Theme]` | `name` | `estilo` |
| `[Wallpaper]` | `Image` | `fondos` |
| `[kcminputrc][Mouse]` | `cursorTheme` | `iconos-cursores` |
| `[kwinrc][org.kde.kdecoration2]` | `library`, `theme`, botones | `decoracion` |
| `[kwinrc][WindowSwitcher]`, `[kwinrc][DesktopSwitcher]` | `LayoutName` | `disposicion` |
| `[KSplash]` | `Theme` | `carga-bloqueo` |

`construir.py` las reúne en el orden de `GRUPOS` y falla si dos módulos reclaman la misma clave. Los aportantes son
los de `dependencias.referencia` e `integra` del manifiesto. El resultado es byte a byte el `defaults` de la 0.3.0.

## Dependencias

- Construcción: integra `carga-bloqueo` y `disposicion` (y, a través de ellos, `fondos`).
- Referencias (identificadores que declara): `esquema`, `estilo`, `decoracion`, `iconos-cursores`, `fondos`, `kvantum`.
- Sistema: `plasma-apply-lookandfeel` (obligatorio para aplicar); `kwriteconfig6`, `dbus-send` (opcionales).
- Terceros: Inter (paquete `fonts-inter`), JetBrains Mono Nerd Font (`instalar.py dependencias --aplicar`).
- Hereda de Breeze (`X-KDE-fallbackPackage=org.kde.breeze.desktop`) lo que no trae: bloqueo, selectores, OSD.

## Desarrollar

```bash
.venv/bin/python herramientas/generar.py --modulos global            # simula: qué cambiaría
.venv/bin/python herramientas/generar.py --modulos global --aplicar  # escribe generado/global/
.venv/bin/python herramientas/generar.py validar                     # referencias e integración
python3 herramientas/instalar.py --modulos global --aplicar          # instala solo el tema global
```

- Para **cambiar un identificador** (otro esquema, otro estilo…), cambia el `valores()` del módulo dueño, no este.
- Para **integrar un componente nuevo**, créalo con `clase: componente` e `integracion.en: global`, y añádelo a
  `dependencias.integra` de `modulo.json`.
- Para **cambiar la tipografía**, `valores()` de `construir.py` (y `FUENTE_KONSOLE` de `complementos/konsole`).
- Pruebas: `test_tema_global_estructura`, `test_defaults_compuestos_por_los_modulos`, `test_componentes_dentro_del_tema_global`.
