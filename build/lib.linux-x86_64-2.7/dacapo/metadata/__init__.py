# -*- coding: utf-8 -*-
# 
# Copyright (c) 2013 Thomas Korell <claw DOT strophob AT gmx DOT de>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from dacapo import errorhandling
import sys
import os
try:
	import mimetypes
	import logging
	import traceback
	from dacapo.metadata import mimehelp
	from dacapo.metadata import flac, mp3, ogg, wma
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

def getAudioFile(playerGUI, filename):
	'''
		Abhängig vom Audio-Typ wird eine Subklasse von Audiofile geladen.
		In dieser werden die metadata eingelesen (notfalls konvertiert) 
		und die Texte und Bilder in einer Liste aufbereitet zur Verfügung 
		gestellt.
	'''
	audioFile = None
	contentType = mimetypes.guess_type(filename) # Mimetype herausfinden
	mimeType = contentType[0]
	# if os.path.isfile(filename):
	if mimehelp.isInMimeTypes(filename) :
		# Versuche FLAC-Datei zu laden
		if mimeType in mimehelp.FLAC_MIMES: 
			try:
				audioFile = flac.FlacFile(playerGUI, filename)	
			except BaseException :
				logging.error("FEHLER bei %s" % (filename) )
				exc_type, exc_value, exc_traceback = sys.exc_info()
				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				for line in lines :
					logging.error(line)

		# Versuche MP3-Datei zu laden
		if mimeType in mimehelp.MPG_MIMES : 
			try:
				audioFile = mp3.Mp3File(playerGUI, filename)	
			except BaseException :
				logging.error("FEHLER bei %s" % (filename) )
				exc_type, exc_value, exc_traceback = sys.exc_info()
				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				for line in lines :
					logging.error(line)

		# Versuche OGG-Datei zu laden
		if mimeType in mimehelp.OGG_MIMES : 
			try:
				audioFile = ogg.OggFile(playerGUI, filename)	
			except BaseException :
				logging.error("FEHLER bei %s" % (filename) )
				exc_type, exc_value, exc_traceback = sys.exc_info()
				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				for line in lines :
					logging.error(line)

		# Versuche WMA-Datei zu laden
		if mimeType in mimehelp.WMA_MIMES : 
			try:
				audioFile = wma.WmaFile(playerGUI, filename)	
			except BaseException :
				logging.error("FEHLER bei %s" % (filename) )
				exc_type, exc_value, exc_traceback = sys.exc_info()
				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				for line in lines :
					logging.error(line)

	return audioFile

