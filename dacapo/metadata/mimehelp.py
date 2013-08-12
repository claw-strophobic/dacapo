#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#! /usr/bin/python
################################################################################
# small Gnome Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
################################################################################



"""
	Dieses Modul enthält die Mime-Typen der Audio-Formate. 
	Um Probleme zu vermeiden, werden diese der Liste 
	zugefügt.
	Für die anderen Module werden Vergleichslisten
	zur Verfügung gestellt.
"""
from dacapo import errorhandling
try:
	import mimetypes as types
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #
WMA_MIMES = ["audio/x-ms-wma", "audio/x-ms-wmv", "video/x-ms-asf",
             "audio/x-wma", "video/x-wmv"]
MPG_MIMES = ["audio/mp3", "audio/x-mp3", "audio/mpeg", "audio/mpg",
             "audio/x-mpeg"]
FLAC_MIMES = ["audio/flac"]
OGG_MIMES = ["audio/ogg"]

types.add_type('audio/flac', '.flac')
types.add_type('audio/ogg', '.ogg')
types.add_type('audio/x-wma', '.wma')
types.add_type('audio/mp3', '.mp3')
types.init()


