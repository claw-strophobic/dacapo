#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
	this module is used to print the help-messages and to
	create the argparse- and config-objects.
	it also checks, if the path for the log-file is
	set properly in the configuration-file.
'''

SHOWPIC_CHOICES = ["NO", "coverOnly", "allCover", "allPics",
	"diaShowAllCover", "diaShowAllPics", "help"]
import argparse as myArg
from dacapo import errorhandling
import os, sys
try:
	import ConfigParser
	from config import readconfig
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

oConfig = readconfig.getConfigObject()
language = oConfig.getConfig('gui', 'misc', 'language')

configLanguage = ConfigParser.ConfigParser()
configLanguage.read(readconfig.getConfigDir() + language + ".ini")
def getLangText(cap, tag) :
	try:
		return configLanguage.get(cap, tag)
	except :
		return ''

try : 
	if not os.path.isdir(os.path.dirname(oConfig.getConfig('debug', ' ', 'logFile'))) :
		raise Exception(getLangText('gui', 'missingLogPath') % (os.path.dirname(oConfig.getConfig('debug', ' ', 'logFile'))))
except :
	errorhandling.Error.show()
	sys.exit(2)

# argparse muss vor dem GStreamer-Import ausgeführt werden
# (welcher in dacapo stattfindet)
# da sonst der Hilfetext von GStreamer überschrieben wird.

parser = myArg.ArgumentParser(description=getLangText('HelpMessages', 'description'))
parser.add_argument("-R", "--resume", help=getLangText('HelpMessages', 'resume'), action="store_true")
parser.add_argument("-NG", "--nogui", help=getLangText('HelpMessages', 'nogui'), action="store_true")
parser.add_argument("-pl", "--playlist", help=getLangText('HelpMessages', 'playlist'), action="store_true")
parser.add_argument("-d", "--debug", help=getLangText('HelpMessages', 'debug'), action="store_true")
parser.add_argument("-dP", "--debugPL", help=getLangText('HelpMessages', 'debugPL'), action="store_true")
parser.add_argument("-dG", "--debugGUI", help=getLangText('HelpMessages', 'debugGUI'), action="store_true")
parser.add_argument("-dS", "--debugS", help=getLangText('HelpMessages', 'debugS'), action="store_true")
parser.add_argument("-dM", "--debugMETA", help=getLangText('HelpMessages', 'debugMETA'), action="store_true")

windowGroup = parser.add_mutually_exclusive_group()
windowGroup.add_argument("-fs", "--fullscreen", help=getLangText('HelpMessages', 'fullscreen'), action="store_true")
windowGroup.add_argument("-w", "--window", help=getLangText('HelpMessages', 'window'), action="store_true")

parser.add_argument("-s", "--shuffle", help=getLangText('HelpMessages', 'shuffle'), action="store_true")
parser.add_argument("-nrg", "--noReplayGain", help=getLangText('HelpMessages', 'noReplayGain'), action="store_true")

lyricGroup = parser.add_mutually_exclusive_group()
lyricGroup.add_argument("-lp", "--showLyricAsPic", help=getLangText('HelpMessages', 'showLyricAsPic'), action="store_true")
lyricGroup.add_argument("-nlp", "--showLyricNotAsPic", help=getLangText('HelpMessages', 'showLyricNotAsPic'), action="store_true")

syncedGroup = parser.add_mutually_exclusive_group()
syncedGroup.add_argument("-sl", "--showSyncedLyrics", help=getLangText('HelpMessages', 'showSyncedLyrics'), action="store_true")
syncedGroup.add_argument("-nsl", "--showNotSyncedLyrics", help=getLangText('HelpMessages', 'showNotSyncedLyrics'), action="store_true")

parser.add_argument("--showPics", help=getLangText('HelpMessages', 'showPics'), choices=SHOWPIC_CHOICES )
parser.add_argument("--fullhelp", help=getLangText('HelpMessages', 'fullhelp'), action="store_true")
parser.add_argument("FILE", help=getLangText('HelpMessages', 'FILE'), nargs='*')
parser.parse_args()

# -------------------- showFullHelp() -----------------------------------------------------------------

def showFullHelp():
	'''
	"Lightweight-Music-Player, spielt FLAC- oder MP3-Datei ab und zeigt das 
	Cover und metadata an. Tasten: \n 
	HOME=Erstes Lied der Playlist \n 
	END=Letztes Lied der Playlist 		
	SPACE=Pause/Start \n 
	LINKS/RECHTS=+/-10 Sekunden \n 
	UP/DOWN=Nächsten/Vorherigen Song \n 
	ESC/Q=Beenden \n 
	F=Fullscreen/Fenster")
			--> '''
	try:
		import gst
	except ImportError, err:
		print "Modul dacapo.py: Error, couldn't load module >>gst<<. %s" % (err)
		sys.exit(2)
	from sys import version_info
	import pygame

	try:
		import gtk
	except ImportError, err:
		print "Modul dacapo.py: Error, couldn't load module >>gtk<<. %s" % (err)
		sys.exit(2)
	
	print getLangText('HelpMessages', 'showFullHelp')
	print " "
	print "dacapo Version: %s" %(fver(oConfig.getConfig('version', ' ', ' ')))
	print " "
	print "Python Version: %s" %(fver(version_info))
	print " "
	print "GTK+: %s / PyGTK: %s" %(
            fver(gtk.gtk_version), fver(gtk.pygtk_version))
	print " "
	print "GStreamer: %s / PyGSt: %s" % (
            fver(gst.version()), fver(gst.pygst_version))
	print " "
	print "pyGame Version: %s / SDL: %s" % (
            pygame.version.ver, fver(pygame.get_sdl_version()))
	print " "
	return

def fver(tup):
    return ".".join(map(str, tup))


# -------------------- showPicsHelp() -----------------------------------------------------------------

def showPicsHelp():
	'''		<!-- showPics: Bilder anzeigen? Mögliche Werte: 
				NO = Keine Bilder anzeigen, nur metadata
				coverOnly = Nur Frontcover anzeigen
				allCover = alle Cover-Bilder anzeigen (Typ 3-6 / Front, Back, Leaflet, Label)
				allPics = alle Bilder
				diaShowAllCover = wie allCover aber als Diashow
				diaShowAllPics = wie allPics aber als Diashow 
			--> '''
	print getLangText('HelpMessages', 'showPicsHelp')
	return

