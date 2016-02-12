#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	Wird mit Songs aus QuodLibet aufgerufen.
#	Es wird anhand der Dacapo-Config-Einstellungen versucht eine *.lrc zu ermitteln.
#	Falls dies gelingt, wird das LyricFlag gesetzt.
#

from gi.repository import Gtk
from quodlibet import qltk
from quodlibet.qltk.wlw import WaitLoadWindow
from quodlibet.plugins.songsmenu import SongsMenuPlugin
try:
	import logging
	from dacapo.config import readconfig
	from dacapo.metadata import *
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

DEBUG=True
levels = {'CRITICAL' : logging.CRITICAL,
    'ERROR' : logging.ERROR,
    'WARNING' : logging.WARNING,
    'INFO' : logging.INFO,
    'DEBUG' : logging.DEBUG
}
strLogLevel = levels['DEBUG']
try:
	logging.basicConfig(filename='/tmp/setLyricFlag.log',
		filemode='w',
		level=strLogLevel,
		format='%(asctime)s ; %(levelname)s ; %(module)s ; %(funcName)s ; %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S')
except :
	errorhandling.Error.show()
	sys.exit(2)

class SetDacapoLyricFlag(SongsMenuPlugin):
	PLUGIN_ID = "SetDacapoLyricFlag"
	PLUGIN_NAME = _('Set dacapo Lyric Flag')
	PLUGIN_DESC = _("Sucht nach LRC-Dateien für den ausgewählten Song und setzt dementsprechend das LyricFlag-Kennzeichen.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		logging.debug(u'Starte...')
		self.config = readconfig.getConfigObject()
		self.counter = 0
		super(SetDacapoLyricFlag, self).__init__(*args, **kwargs)


	def plugin_handles(self, songs):
		result = False
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				self.counter += 1
				result = True
		return result

	def plugin_songs(self, songs):
		if not qltk.ConfirmAction(self.plugin_window,
			_('Set dacapo Lyric Flag'),
			_("Check {!s} files?").format(self.counter)
								  ).run():
			logging.debug("Verarbeitung abgebrochen!")
			return True
		logging.debug("Starte Verarbeitung!")
		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Suche nach Synchronisierten Texten.\n\n%(current)d/%(total)d Songs verarbeitet."))
		for song in songs:
			logging.debug(u'Song: %s hassynclyrics %s' % (song.list('title'), song.get('hassynclyrics')))
			if song.get("~filename", "").endswith(".flac"):
				flacFilePath = song.get("~filename", "")
				try:
					lyrics = self.getLrycs(flacFilePath)
					if(lyrics == False):
						song["hassynclyrics"] = '0'
					else:
						song["hassynclyrics"] = '1'
				except:
					return False
			if win.step():
				break
		win.destroy()


	def getLrycs(self, flacFilePath):
		audioFile = getAudioFile(flacFilePath)
		try:
			s = audioFile.syncText
			if isinstance(s, list) and len(s) > 0:
				return True
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			print ''.join('!! ' + line for line in lines)  # Log it or whatever here

		return False
