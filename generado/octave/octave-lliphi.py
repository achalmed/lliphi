#!/usr/bin/env python3
"""Lliphi en GNU Octave. GENERADO por herramientas/generar.py desde complementos/octave; no editar.

Octave guarda dos «modos de color» a la vez (Preferencias → «Second color mode (light/dark)»): este programa pone
«Lliphi Claro» en el primero y «Lliphi Oscuro» en el segundo, en el editor, la ventana de órdenes, el editor de variables y el
espacio de trabajo, y elige el modo de la variante. Edita solo esas claves de `octave-gui.ini`: lo demás (ventanas,
atajos, archivos recientes) queda como estaba. Octave lee los colores al arrancar: el cambio se ve al abrirlo de nuevo.

Uso:  octave-lliphi.py claro|oscuro                     # simula: dice qué cambiaría
      octave-lliphi.py claro|oscuro --colores --aplicar # escribe los colores de Lliphi y elige el modo
      octave-lliphi.py claro|oscuro --aplicar           # solo cambia de modo, si los colores ya son de Lliphi
Sin `--colores` no toca un Octave con otros colores: así lo llama la vigilancia de fondo-variante en cada cambio de
variante. Si Octave nunca se abrió (no hay `octave-gui.ini`), no crea nada. Solo biblioteca estándar.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

FRAGMENTO = {
 "claro": {
  "Scintilla": {
   "Bash\\defaultcolor": "1908516",
   "Bash\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\defaultpaper": "16514301",
   "Bash\\style0\\color": "1908516",
   "Bash\\style0\\eolfill": "false",
   "Bash\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style0\\paper": "16514301",
   "Bash\\style10\\color": "9322632",
   "Bash\\style10\\eolfill": "false",
   "Bash\\style10\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style10\\paper": "16514301",
   "Bash\\style11\\color": "29046",
   "Bash\\style11\\eolfill": "false",
   "Bash\\style11\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style11\\paper": "16514301",
   "Bash\\style12\\color": "10763064",
   "Bash\\style12\\eolfill": "false",
   "Bash\\style12\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style12\\paper": "16514301",
   "Bash\\style13\\color": "30773",
   "Bash\\style13\\eolfill": "false",
   "Bash\\style13\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style13\\paper": "16514301",
   "Bash\\style1\\color": "11940146",
   "Bash\\style1\\eolfill": "false",
   "Bash\\style1\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style1\\paper": "16514301",
   "Bash\\style2\\color": "6711148",
   "Bash\\style2\\eolfill": "false",
   "Bash\\style2\\font": "@FUENTE@, 10, 0, 1, 0",
   "Bash\\style2\\paper": "16514301",
   "Bash\\style3\\color": "8281600",
   "Bash\\style3\\eolfill": "false",
   "Bash\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style3\\paper": "16514301",
   "Bash\\style4\\color": "10763064",
   "Bash\\style4\\eolfill": "false",
   "Bash\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style4\\paper": "16514301",
   "Bash\\style5\\color": "30773",
   "Bash\\style5\\eolfill": "false",
   "Bash\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style5\\paper": "16514301",
   "Bash\\style6\\color": "30773",
   "Bash\\style6\\eolfill": "false",
   "Bash\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style6\\paper": "16514301",
   "Bash\\style7\\color": "4934995",
   "Bash\\style7\\eolfill": "false",
   "Bash\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style7\\paper": "16514301",
   "Bash\\style8\\color": "1908516",
   "Bash\\style8\\eolfill": "false",
   "Bash\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style8\\paper": "16514301",
   "Bash\\style9\\color": "9322632",
   "Bash\\style9\\eolfill": "false",
   "Bash\\style9\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style9\\paper": "16514301",
   "Diff\\defaultcolor": "1908516",
   "Diff\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\defaultpaper": "16514301",
   "Diff\\style0\\color": "1908516",
   "Diff\\style0\\eolfill": "false",
   "Diff\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style0\\paper": "16514301",
   "Diff\\style10\\color": "1275704",
   "Diff\\style10\\eolfill": "false",
   "Diff\\style10\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style10\\paper": "16514301",
   "Diff\\style11\\color": "11940146",
   "Diff\\style11\\eolfill": "false",
   "Diff\\style11\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style11\\paper": "16514301",
   "Diff\\style1\\color": "6711148",
   "Diff\\style1\\eolfill": "false",
   "Diff\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Diff\\style1\\paper": "16514301",
   "Diff\\style2\\color": "10763064",
   "Diff\\style2\\eolfill": "false",
   "Diff\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style2\\paper": "16514301",
   "Diff\\style3\\color": "3432370",
   "Diff\\style3\\eolfill": "false",
   "Diff\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style3\\paper": "16514301",
   "Diff\\style4\\color": "9322632",
   "Diff\\style4\\eolfill": "false",
   "Diff\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style4\\paper": "16514301",
   "Diff\\style5\\color": "11940146",
   "Diff\\style5\\eolfill": "false",
   "Diff\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style5\\paper": "16514301",
   "Diff\\style6\\color": "1275704",
   "Diff\\style6\\eolfill": "false",
   "Diff\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style6\\paper": "16514301",
   "Diff\\style7\\color": "9526016",
   "Diff\\style7\\eolfill": "false",
   "Diff\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style7\\paper": "16514301",
   "Diff\\style8\\color": "1275704",
   "Diff\\style8\\eolfill": "false",
   "Diff\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style8\\paper": "16514301",
   "Diff\\style9\\color": "11940146",
   "Diff\\style9\\eolfill": "false",
   "Diff\\style9\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style9\\paper": "16514301",
   "Matlab\\defaultcolor": "1908516",
   "Matlab\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\defaultpaper": "16514301",
   "Matlab\\style0\\color": "1908516",
   "Matlab\\style0\\eolfill": "false",
   "Matlab\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style0\\paper": "16514301",
   "Matlab\\style1\\color": "6711148",
   "Matlab\\style1\\eolfill": "false",
   "Matlab\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Matlab\\style1\\paper": "16514301",
   "Matlab\\style2\\color": "9322632",
   "Matlab\\style2\\eolfill": "false",
   "Matlab\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style2\\paper": "16514301",
   "Matlab\\style3\\color": "8281600",
   "Matlab\\style3\\eolfill": "false",
   "Matlab\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style3\\paper": "16514301",
   "Matlab\\style4\\color": "10763064",
   "Matlab\\style4\\eolfill": "false",
   "Matlab\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style4\\paper": "16514301",
   "Matlab\\style5\\color": "30773",
   "Matlab\\style5\\eolfill": "false",
   "Matlab\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style5\\paper": "16514301",
   "Matlab\\style6\\color": "4934995",
   "Matlab\\style6\\eolfill": "false",
   "Matlab\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style6\\paper": "16514301",
   "Matlab\\style7\\color": "1908516",
   "Matlab\\style7\\eolfill": "false",
   "Matlab\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style7\\paper": "16514301",
   "Matlab\\style8\\color": "30773",
   "Matlab\\style8\\eolfill": "false",
   "Matlab\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style8\\paper": "16514301",
   "Octave\\defaultcolor": "1908516",
   "Octave\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\defaultpaper": "16514301",
   "Octave\\style0\\color": "1908516",
   "Octave\\style0\\eolfill": "false",
   "Octave\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style0\\paper": "16514301",
   "Octave\\style1\\color": "6711148",
   "Octave\\style1\\eolfill": "false",
   "Octave\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Octave\\style1\\paper": "16514301",
   "Octave\\style2\\color": "9322632",
   "Octave\\style2\\eolfill": "false",
   "Octave\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style2\\paper": "16514301",
   "Octave\\style3\\color": "8281600",
   "Octave\\style3\\eolfill": "false",
   "Octave\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style3\\paper": "16514301",
   "Octave\\style4\\color": "10763064",
   "Octave\\style4\\eolfill": "false",
   "Octave\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style4\\paper": "16514301",
   "Octave\\style5\\color": "30773",
   "Octave\\style5\\eolfill": "false",
   "Octave\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style5\\paper": "16514301",
   "Octave\\style6\\color": "4934995",
   "Octave\\style6\\eolfill": "false",
   "Octave\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style6\\paper": "16514301",
   "Octave\\style7\\color": "1908516",
   "Octave\\style7\\eolfill": "false",
   "Octave\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style7\\paper": "16514301",
   "Octave\\style8\\color": "30773",
   "Octave\\style8\\eolfill": "false",
   "Octave\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style8\\paper": "16514301"
  },
  "editor": {
   "highlightCurrentLineColor": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xf2\\xf2\\xf3\\xf3\\xf5\\xf5\\0\\0)"
  },
  "terminal": {
   "color_b": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xf2\\xf2\\xf3\\xf3\\xf5\\xf5\\0\\0)",
   "color_c": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x31\\x31[[\\xef\\xef\\0\\0)",
   "color_f": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x1d\\x1d\\x1f\\x1f$$\\0\\0)",
   "color_s": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x31\\x31[[\\xef\\xef\\0\\0)"
  },
  "variable_editor": {
   "color_a": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xf2\\xf2\\xf3\\xf3\\xf5\\xf5\\0\\0)",
   "color_b": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xfb\\xfb\\xfc\\xfc\\xfd\\xfd\\0\\0)",
   "color_f": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x1d\\x1d\\x1f\\x1f$$\\0\\0)",
   "color_h": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x31\\x31[[\\xef\\xef\\0\\0)",
   "color_s": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xfc\\xfc\\xfc\\xfc\\xfc\\xfc\\0\\0)"
  },
  "workspaceview": {
   "color_a": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xf2\\xf2\\xf3\\xf3\\xf5\\xf5\\0\\0)",
   "color_g": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xe0\\xe0\\xe1\\xe1\\xe5\\xe5\\0\\0)",
   "color_p": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xe0\\xe0\\xe1\\xe1\\xe5\\xe5\\0\\0)"
  }
 },
 "oscuro": {
  "Scintilla_2": {
   "Bash\\defaultcolor": "15395821",
   "Bash\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\defaultpaper": "1052690",
   "Bash\\style0\\color": "15395821",
   "Bash\\style0\\eolfill": "false",
   "Bash\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style0\\paper": "1052690",
   "Bash\\style10\\color": "14257362",
   "Bash\\style10\\eolfill": "false",
   "Bash\\style10\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style10\\paper": "1052690",
   "Bash\\style11\\color": "49866",
   "Bash\\style11\\eolfill": "false",
   "Bash\\style11\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style11\\paper": "1052690",
   "Bash\\style12\\color": "15894657",
   "Bash\\style12\\eolfill": "false",
   "Bash\\style12\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style12\\paper": "1052690",
   "Bash\\style13\\color": "6931070",
   "Bash\\style13\\eolfill": "false",
   "Bash\\style13\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style13\\paper": "1052690",
   "Bash\\style1\\color": "16482682",
   "Bash\\style1\\eolfill": "false",
   "Bash\\style1\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style1\\paper": "1052690",
   "Bash\\style2\\color": "9935004",
   "Bash\\style2\\eolfill": "false",
   "Bash\\style2\\font": "@FUENTE@, 10, 0, 1, 0",
   "Bash\\style2\\paper": "1052690",
   "Bash\\style3\\color": "13673530",
   "Bash\\style3\\eolfill": "false",
   "Bash\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style3\\paper": "1052690",
   "Bash\\style4\\color": "15894657",
   "Bash\\style4\\eolfill": "false",
   "Bash\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style4\\paper": "1052690",
   "Bash\\style5\\color": "6931070",
   "Bash\\style5\\eolfill": "false",
   "Bash\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style5\\paper": "1052690",
   "Bash\\style6\\color": "6931070",
   "Bash\\style6\\eolfill": "false",
   "Bash\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style6\\paper": "1052690",
   "Bash\\style7\\color": "12369601",
   "Bash\\style7\\eolfill": "false",
   "Bash\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style7\\paper": "1052690",
   "Bash\\style8\\color": "15395821",
   "Bash\\style8\\eolfill": "false",
   "Bash\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style8\\paper": "1052690",
   "Bash\\style9\\color": "14257362",
   "Bash\\style9\\eolfill": "false",
   "Bash\\style9\\font": "@FUENTE@, 10, 0, 0, 0",
   "Bash\\style9\\paper": "1052690",
   "Diff\\defaultcolor": "15395821",
   "Diff\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\defaultpaper": "1052690",
   "Diff\\style0\\color": "15395821",
   "Diff\\style0\\eolfill": "false",
   "Diff\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style0\\paper": "1052690",
   "Diff\\style10\\color": "7325828",
   "Diff\\style10\\eolfill": "false",
   "Diff\\style10\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style10\\paper": "1052690",
   "Diff\\style11\\color": "16482682",
   "Diff\\style11\\eolfill": "false",
   "Diff\\style11\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style11\\paper": "1052690",
   "Diff\\style1\\color": "9935004",
   "Diff\\style1\\eolfill": "false",
   "Diff\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Diff\\style1\\paper": "1052690",
   "Diff\\style2\\color": "15894657",
   "Diff\\style2\\eolfill": "false",
   "Diff\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style2\\paper": "1052690",
   "Diff\\style3\\color": "8235773",
   "Diff\\style3\\eolfill": "false",
   "Diff\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style3\\paper": "1052690",
   "Diff\\style4\\color": "14257362",
   "Diff\\style4\\eolfill": "false",
   "Diff\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style4\\paper": "1052690",
   "Diff\\style5\\color": "16482682",
   "Diff\\style5\\eolfill": "false",
   "Diff\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style5\\paper": "1052690",
   "Diff\\style6\\color": "7325828",
   "Diff\\style6\\eolfill": "false",
   "Diff\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style6\\paper": "1052690",
   "Diff\\style7\\color": "15446623",
   "Diff\\style7\\eolfill": "false",
   "Diff\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style7\\paper": "1052690",
   "Diff\\style8\\color": "7325828",
   "Diff\\style8\\eolfill": "false",
   "Diff\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style8\\paper": "1052690",
   "Diff\\style9\\color": "16482682",
   "Diff\\style9\\eolfill": "false",
   "Diff\\style9\\font": "@FUENTE@, 10, 0, 0, 0",
   "Diff\\style9\\paper": "1052690",
   "Matlab\\defaultcolor": "15395821",
   "Matlab\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\defaultpaper": "1052690",
   "Matlab\\style0\\color": "15395821",
   "Matlab\\style0\\eolfill": "false",
   "Matlab\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style0\\paper": "1052690",
   "Matlab\\style1\\color": "9935004",
   "Matlab\\style1\\eolfill": "false",
   "Matlab\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Matlab\\style1\\paper": "1052690",
   "Matlab\\style2\\color": "14257362",
   "Matlab\\style2\\eolfill": "false",
   "Matlab\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style2\\paper": "1052690",
   "Matlab\\style3\\color": "13673530",
   "Matlab\\style3\\eolfill": "false",
   "Matlab\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style3\\paper": "1052690",
   "Matlab\\style4\\color": "15894657",
   "Matlab\\style4\\eolfill": "false",
   "Matlab\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style4\\paper": "1052690",
   "Matlab\\style5\\color": "6931070",
   "Matlab\\style5\\eolfill": "false",
   "Matlab\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style5\\paper": "1052690",
   "Matlab\\style6\\color": "12369601",
   "Matlab\\style6\\eolfill": "false",
   "Matlab\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style6\\paper": "1052690",
   "Matlab\\style7\\color": "15395821",
   "Matlab\\style7\\eolfill": "false",
   "Matlab\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style7\\paper": "1052690",
   "Matlab\\style8\\color": "6931070",
   "Matlab\\style8\\eolfill": "false",
   "Matlab\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Matlab\\style8\\paper": "1052690",
   "Octave\\defaultcolor": "15395821",
   "Octave\\defaultfont": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\defaultpaper": "1052690",
   "Octave\\style0\\color": "15395821",
   "Octave\\style0\\eolfill": "false",
   "Octave\\style0\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style0\\paper": "1052690",
   "Octave\\style1\\color": "9935004",
   "Octave\\style1\\eolfill": "false",
   "Octave\\style1\\font": "@FUENTE@, 10, 0, 1, 0",
   "Octave\\style1\\paper": "1052690",
   "Octave\\style2\\color": "14257362",
   "Octave\\style2\\eolfill": "false",
   "Octave\\style2\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style2\\paper": "1052690",
   "Octave\\style3\\color": "13673530",
   "Octave\\style3\\eolfill": "false",
   "Octave\\style3\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style3\\paper": "1052690",
   "Octave\\style4\\color": "15894657",
   "Octave\\style4\\eolfill": "false",
   "Octave\\style4\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style4\\paper": "1052690",
   "Octave\\style5\\color": "6931070",
   "Octave\\style5\\eolfill": "false",
   "Octave\\style5\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style5\\paper": "1052690",
   "Octave\\style6\\color": "12369601",
   "Octave\\style6\\eolfill": "false",
   "Octave\\style6\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style6\\paper": "1052690",
   "Octave\\style7\\color": "15395821",
   "Octave\\style7\\eolfill": "false",
   "Octave\\style7\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style7\\paper": "1052690",
   "Octave\\style8\\color": "6931070",
   "Octave\\style8\\eolfill": "false",
   "Octave\\style8\\font": "@FUENTE@, 10, 0, 0, 0",
   "Octave\\style8\\paper": "1052690"
  },
  "editor": {
   "highlightCurrentLineColor_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x16\\x16\\x17\\x17\\x19\\x19\\0\\0)"
  },
  "terminal": {
   "color_b_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x1b\\x1b\\x1b\\x1b\\x1d\\x1d\\0\\0)",
   "color_c_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xe2\\xe2%%))\\0\\0)",
   "color_f_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\0\\0)",
   "color_s_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xe2\\xe2%%))\\0\\0)"
  },
  "variable_editor": {
   "color_a_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x16\\x16\\x17\\x17\\x19\\x19\\0\\0)",
   "color_b_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x10\\x10\\x10\\x10\\x12\\x12\\0\\0)",
   "color_f_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xea\\xea\\xeb\\xeb\\xed\\xed\\0\\0)",
   "color_h_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xe2\\xe2%%))\\0\\0)",
   "color_s_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xfc\\xfc\\xfc\\xfc\\xfc\\xfc\\0\\0)"
  },
  "workspaceview": {
   "color_a_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x16\\x16\\x17\\x17\\x19\\x19\\0\\0)",
   "color_g_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff##$$&&\\0\\0)",
   "color_p_2": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff..//22\\0\\0)"
  }
 }
}
HUELLA = {"claro": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\xf2\\xf2\\xf3\\xf3\\xf5\\xf5\\0\\0)", "oscuro": "@Variant(\\0\\0\\0\\x43\\x1\\xff\\xff\\x1b\\x1b\\x1b\\x1b\\x1d\\x1d\\0\\0)"}                  # terminal/color_b de cada modo: si coinciden, los colores son de Lliphi
FUENTES = ["JetBrainsMono Nerd Font", "JetBrains Mono", "monospace"]
INTERRUPTORES = ["editor/color_mode", "terminal/color_mode", "variable_editor/color_mode", "workspaceview/color_mode"]
MODO = {"claro": "0", "oscuro": "1"}
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
INI = CONFIG / "octave" / "octave-gui.ini"


def leer(texto: str) -> dict[str, dict[str, str]]:
    secciones: dict[str, dict[str, str]] = {}
    grupo = "General"
    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            grupo = linea.strip()[1:-1]
        elif "=" in linea and not linea.startswith(";"):
            clave, valor = linea.split("=", 1)
            secciones.setdefault(grupo, {})[clave] = valor
    return secciones


def fusionar(texto: str, cambios: dict[str, dict[str, str]], si_falta: set[str] = frozenset()) -> str:
    """El ini con `cambios` (sección → clave → valor): reemplaza la línea de cada clave en su sección o la añade al
    final de la sección (o en una sección nueva); las demás líneas quedan tal cual. Las claves cuyo nombre acaba en
    algo de `si_falta` solo se escriben si no estaban (las fuentes que eligió el usuario se conservan)."""
    pendientes = {g: dict(c) for g, c in cambios.items()}
    salida: list[str] = []
    grupo = "General"

    def cerrar(g: str) -> None:
        resto = pendientes.pop(g, {})
        if resto:
            while salida and salida[-1] == "":
                salida.pop()
            salida.extend(f"{k}={v}" for k, v in resto.items())
            salida.append("")

    for linea in texto.splitlines():
        if linea.startswith("[") and linea.rstrip().endswith("]"):
            cerrar(grupo)
            grupo = linea.strip()[1:-1]
        elif "=" in linea and grupo in pendientes:
            clave = linea.split("=", 1)[0]
            if clave in pendientes[grupo]:
                valor = pendientes[grupo].pop(clave)
                if not any(clave.endswith(f) for f in si_falta):
                    linea = f"{clave}={valor}"
        salida.append(linea)
    cerrar(grupo)
    for g in list(pendientes):
        if pendientes[g]:
            if salida and salida[-1] != "":
                salida.append("")
            salida += [f"[{g}]", *(f"{k}={v}" for k, v in pendientes.pop(g).items()), ""]
    while salida and salida[-1] == "":
        salida.pop()
    return "\n".join(salida) + ("\n\n" if texto.endswith("\n\n") else "\n")


def fuente() -> str:
    """La primera familia monoespaciada de Lliphi que esté instalada (fc-list), o la monoespaciada del sistema."""
    fc = shutil.which("fc-list")
    for familia in FUENTES:
        if familia == "monospace" or not fc:
            break
        if subprocess.run([fc, f":family={familia}"], capture_output=True, text=True).stdout.strip():
            return familia
    return "Monospace"


def interruptores(var: str) -> dict[str, dict[str, str]]:
    cambios: dict[str, dict[str, str]] = {}
    for clave in INTERRUPTORES:
        grupo, nombre = clave.split("/")
        cambios.setdefault(grupo, {})[nombre] = MODO[var]
    return cambios


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in MODO:
        print(__doc__.split("\n\n")[2], file=sys.stderr)
        return 1
    var, escribir, colores = argv[0], "--aplicar" in argv, "--colores" in argv
    if not INI.exists():
        if colores:
            print(f"Octave: no hay {INI}; abre Octave una vez (su asistente lo crea) y vuelve a aplicar")
        return 0
    real = INI.resolve()                         # el archivo real: un enlace de dotfiles (stow) se conserva
    texto = real.read_text(encoding="utf-8")
    actual = leer(texto)
    terminal = actual.get("terminal", {})
    propios = terminal.get("color_b") == HUELLA["claro"] and terminal.get("color_b_2") == HUELLA["oscuro"]
    if not colores and not propios:
        return 0                                  # otros colores: la vigilancia no los toca
    cambios = interruptores(var)
    if colores:
        familia = fuente()
        for v in ("claro", "oscuro"):
            for grupo, claves in FRAGMENTO[v].items():
                cambios.setdefault(grupo, {}).update({k: x.replace("@FUENTE@", familia) for k, x in claves.items()})
    nuevo = fusionar(texto, cambios, si_falta={"\\font", "\\defaultfont"})
    if nuevo == texto:
        return 0
    modo = "segundo" if MODO[var] == "1" else "primer"
    que = "colores de Lliphi y " if colores and not propios else ""
    print(f"{'' if escribir else 'SIM '}Octave: {que}{modo} modo de color ({'Lliphi Oscuro' if var == 'oscuro' else 'Lliphi Claro'}); se ve al abrir Octave")
    if escribir:
        temporal = real.with_name(real.name + ".lliphi")
        temporal.write_text(nuevo, encoding="utf-8")
        temporal.replace(real)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
