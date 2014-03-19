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
	from dacapo.config import readconfig
	import logging
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
M3U_MIMES = ['audio/x-mpegurl']

types.add_type('audio/flac', '.flac')
types.add_type('audio/ogg', '.ogg')
types.add_type('audio/x-wma', '.wma')
types.add_type('audio/mp3', '.mp3')
types.add_type('audio/x-mpegurl', '.m3u')
types.init()

def isInMimeTypes(song):
	oConfig = readconfig.getConfigObject()
	debug = oConfig.getConfig('debug', ' ', 'debugM')
	contentType = types.guess_type(song) # Mimetype herausfinden
	if debug : logging.debug("Angegebene Datei ist vom Typ: %s" % (contentType[0]) )
	if contentType[0] in FLAC_MIMES \
	or contentType[0] in OGG_MIMES \
	or contentType[0] in WMA_MIMES \
	or contentType[0] in MPG_MIMES : 
		return True
	else:
		return False


