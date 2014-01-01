#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
#! /usr/bin/python
###############################################################################
# small GTK/GStreamer Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
###############################################################################
'''
	this module creates the logger and the threading for
	the player. it gets the options either from the 
	commandline (argparse) or the Gtk+ -gui (config).
	the playlist is generated and finally it calls the ui/player.
'''
import errorhandling
import sys
import os
import dacapoHelp
try:
	import threading
	from config import readconfig
	from playlist import generate
	from ui import player
	import logging
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #

oConfig = readconfig.getConfigObject()

levels = {'CRITICAL' : logging.CRITICAL,
    'ERROR' : logging.ERROR,
    'WARNING' : logging.WARNING,
    'INFO' : logging.INFO,
    'DEBUG' : logging.DEBUG
}
strLogLevel = levels[oConfig.getConfig('debug', ' ', 'logLevel')]
try:
	logging.basicConfig(filename=oConfig.getConfig('debug', ' ', 'logFile'), 
		filemode='w',
		level=strLogLevel, 
		format='%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s', 
		datefmt='%Y-%m-%d %H:%M:%S')
except :
	errorhandling.Error.show()
	sys.exit(2)

logging.debug('Starte den GPlayer...')

# ----------- Klassendefinitionen ----------------------------- #



# -------------------- Main() -----------------------------------------------------------------
 
def play(config=None):
	import string
	from sys import version_info
	# check for version > 2.6
	# if version_info < (2,7) :
	#	from optparse import OptionParser as myArg
	#	print "Lade >>optparse<<"
	#else :
	global oConfig

	if not config == None : oConfig=config

	bDebugP = oConfig.getConfig('debug', ' ', 'debugPL')
	bDebugM = oConfig.getConfig('debug', ' ', 'debugM')
	bDebugG = oConfig.getConfig('debug', ' ', 'debugGUI')
	bDebugS = oConfig.getConfig('debug', ' ', 'debugS')

	bReplayGain = oConfig.getConfig('audio_engine', 'audio_engine', 'replayGain')
	sDiaShow = oConfig.getConfig('gui', 'misc', 'showPics')
	bFullscreen = oConfig.getConfig('gui', 'misc', 'fullscreen')

	bShowSyncedLyrics  = oConfig.getConfig('gui', 'misc', 'showLyricsSynced')
	bshowLyricAsPic  = oConfig.getConfig('gui', 'misc', 'showLyricsAsPics')

	bNoGUI = False
	bResume = oConfig.getConfig('gui', 'misc', 'resume')
	

	oPlaylist = generate.PlayList(bDebug = bDebugP)
	
	args = dacapoHelp.parser.parse_args()
	
	if args.showPics == 'help':
		dacapoHelp.showPicsHelp()
		return

	if args.fullhelp:
		dacapoHelp.showFullHelp()
		return

	if args.debug:
		bDebugG = True
		bDebugM = True
		bDebugS = True
		bDebugP = True
		oPlaylist.setDebug(bDebugP)

	if args.debugPL:
		bDebugP = True
		oPlaylist.setDebug(True)

	if args.debugGUI:
		bDebugG = True

	if args.debugMETA:
		bDebugM = True

	if args.debugS:
		bDebugS = True

	if args.fullscreen:
		bFullscreen = True

	if args.window:
		bFullscreen = False

	if args.shuffle:
		oPlaylist.setShuffel(True)

	if args.noReplayGain:
		bReplayGain = False

	if args.nogui:
		bNoGUI = True

	if args.resume:
		bResume = True

	if args.showPics:
		sDiaShow = args.showPics

	if args.playlist:
		oPlaylist.setIsPlaylist(True)

	if args.showLyricAsPic:
		bshowLyricAsPic = True

	if args.showLyricNotAsPic:
		bshowLyricAsPic = False

	if args.showSyncedLyrics:
		bShowSyncedLyrics = True

	if args.showNotSyncedLyrics:
		bShowSyncedLyrics = False

	if args.debug : print "Debug fuer alles angeschaltet"
	if bDebugG : print "Debug GUI angeschaltet"
	if bDebugP : print "Debug PL angeschaltet"
	if bDebugM : print "Debug META angeschaltet"
	if bDebugS : print "Debug GStreamer angeschaltet"

	if bDebugG and bFullscreen : print "Fullscreen angeschaltet"
	if bDebugS and not bReplayGain : print "Replay-Gain ist ausgeschaltet"
	if bDebugP and args.playlist : print "Playlist aktiviert. "
	if bDebugP and args.resume : print "Playlist-Resume aktiviert. "
	if bDebugP and args.shuffle : print "Shuffle angeschaltet"
	if sDiaShow and bDebugG :  print "showPics: %s" % (sDiaShow)
	if bDebugG and bNoGUI : print "GUI wird nicht verwendet!"

	bShowGUI = True
	if bNoGUI == True: bShowGUI = False
	
	oConfig.setDebug('debugPL', bDebugP)
	oConfig.setDebug('debugM', bDebugM)
	oConfig.setDebug('debugGUI', bDebugG)
	oConfig.setDebug('debugS', bDebugS)

	oConfig.setConfig('audio_engine', 'audio_engine', 'replayGain', bReplayGain)
	oConfig.setConfig('TEMP', Key='SHOWGUI', Value=bShowGUI)
	oConfig.setConfig('TEMP', Key='RESUME', Value=bResume)
	oConfig.setConfig('TEMP', Key='FULLSCREEN', Value=bFullscreen)

	oConfig.setConfig('gui', 'misc', 'showLyricsSynced', bShowSyncedLyrics)
	oConfig.setConfig('gui', 'misc', 'showLyricsAsPics', bshowLyricAsPic)
	oConfig.setConfig('gui', 'misc', 'showPics', sDiaShow)

	if len(args.FILE) <= 0 and \
	  bResume == False :
		sys.stderr.write(dacapoHelp.getLangText('gui', 'nofile') + '\n') 
		return 

	oPlaylist.setInput(args.FILE)
	if bResume : oPlaylist.resume()
	else: oPlaylist.proceed()

	# Threading. Die GUI läuft in einem Thread, die GStreamer-Verarbeitung
	# in einem anderen..
	# Hauptschalter erstellen. Erst wenn dieser angeschaltet wird, beenden
	# alle Module. 
	hauptschalter = threading.Event()

	# Ausschalter erstellen. Dieser wird an die beiden Threads übergeben
	# und veranlasst die GStreamer-Verarbeitung bei Ende auch
	# aufzuräumen und sich zu beenden.
	ausschalter = threading.Event()

	# Klasseninstanzen erstellen und die Schalter übergeben.
	GUI = player.playerGUI(oPlaylist, ausschalter, hauptschalter)
	   
	# Starten
	#GUI.start()
	GUI.run()
	# Hier wird gewartet bis der Hauptschalter umgelegt wurde.
	hauptschalter.wait()

	# Meldung von der Hauptprozedur
	# print "Hauptprozedur ist fertig"	
	del oConfig
	del oPlaylist
	sys.exit()




# -------------------- main() -----------------------------------------------------------------



if __name__ == '__main__':
	play()
	

