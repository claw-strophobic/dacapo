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
import gettext
t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

try:
	from config import readconfig
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

oConfig = readconfig.getConfigObject()
language = oConfig.getConfig('gui', 'misc', 'language')

try : 
	if not os.path.isdir(os.path.dirname(oConfig.getConfig('debug', ' ', 'logFile'))) :
		raise Exception(_('The logfile-path: {!s} is missing. Please check the configuration.').format(os.path.dirname(oConfig.getConfig('debug', ' ', 'logFile'))))
except :
	errorhandling.Error.show()
	sys.exit(2)

# argparse muss vor dem GStreamer-Import ausgeführt werden
# (welcher in dacapo stattfindet)
# da sonst der Hilfetext von GStreamer überschrieben wird.

parser = myArg.ArgumentParser(description=_('Lightweight-Music-Player, who plays FLAC- or MP3-file and shows CD-cover, pictures and metadata, as well as song-lyrics (as a picture and/or synced).'))
parser.add_argument("-R", "--resume", help=_('start on the last position from the last playlist'), action="store_true")
parser.add_argument("-NG", "--nogui", help=_('show no metadata, pictures etc.'), action="store_true")
parser.add_argument("-pl", "--playlist", help=_('the given file is a playlist'), action="store_true")
parser.add_argument("-d", "--debug", help=_('print all debug messages to the logfile - from all modules'), action="store_true")
parser.add_argument("-dP", "--debugPL", help=_('print debug messages to the logfile from the playlist modules'), action="store_true")
parser.add_argument("-dG", "--debugGUI", help=_('print debug messages to the logfile from the GUI modules'), action="store_true")
parser.add_argument("-dS", "--debugS", help=_('print debug messages to the logfile from the GStreamer modules'), action="store_true")
parser.add_argument("-dM", "--debugMETA", help=_('print debug messages to the logfile from the metadata modules'), action="store_true")

windowGroup = parser.add_mutually_exclusive_group()
windowGroup.add_argument("-fs", "--fullscreen", help=_('show the ui in fullscreen mode'), action="store_true")
windowGroup.add_argument("-w", "--window", help=_('show the ui in window mode'), action="store_true")

parser.add_argument("-s", "--shuffle", help=_('play the songs from the playlist in random order'), action="store_true")
parser.add_argument("-nrg", "--noReplayGain", help=_('do not use ReplayGain'), action="store_true")

lyricGroup = parser.add_mutually_exclusive_group()
lyricGroup.add_argument("-lp", "--showLyricAsPic", help=_('show song lyrics as pictures'), action="store_true")
lyricGroup.add_argument("-nlp", "--showLyricNotAsPic", help=_('do not show song lyrics as pictures'), action="store_true")

syncedGroup = parser.add_mutually_exclusive_group()
syncedGroup.add_argument("-sl", "--showSyncedLyrics", help=_('show synced song lyrics (like karaoke)'), action="store_true")
syncedGroup.add_argument("-nsl", "--showNotSyncedLyrics", help=_('do not show synced song lyrics (like karaoke)'), action="store_true")

parser.add_argument("--showPics", help=_('show pictures. Type "--showPics help"  to get a list of possible options.'), choices=SHOWPIC_CHOICES )
parser.add_argument("--fullhelp", help=_('show a long help message'), action="store_true")
parser.add_argument("--fonthelp", help=_('show available fonts'), action="store_true")
parser.add_argument("FILE", help=_('the file(s) or playlist(s) which should be played'), nargs='*')
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
		from gi.repository import Gtk
	except ImportError, err:
		print "Modul dacapo.py: Error, couldn't load module >>gtk<<. %s" % (err)
		sys.exit(2)
	
	print _('''
Lightweight-Music-Player,  who plays FLAC- or MP3-file and shows CD-cover,
pictures and metadata, as well as song-lyrics (as a picture and/or synced). \n
Keys while playing:\n
	HOME=First song from playlist
	END=Last song from playlist
	SPACE=Pause/Start
	LEFT/RIGHT=+/-10 Seconds
	UP/DOWN=Next/Previous Song
	ESC/Q=Quit
	F=Fullscreen/Window'
			''')
	print " "
	print "dacapo Version: %s" %(fver(oConfig.getConfig('version', ' ', ' ')))
	print " "
	print "Python Version: %s" %(fver(version_info))
	print " "
	print "GTK+: %s" %(fver(Gtk._version))
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
	print _('''
showPics: Display pictures? Possible values are:
			NO = Show no pictures at all, only metadata
			coverOnly = show only frontcover
			allCover = show all cover (Type 3-6 / Front, Back, Leaflet, Label)
			allPics = show all pictures
			diaShowAllCover = like allCover, but shown as a slideshow
			diaShowAllPics = like allPics, but shown as a slideshow
			help = print this help and quit
	''')
	return

# -------------------- showPicsHelp() -----------------------------------------------------------------

def showFontHelp():
	import pygame
	pygame.init()
	fonts = pygame.font.get_fonts()
	for font in fonts:		
		print font 		
