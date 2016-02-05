#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	Wird mit einem  Startverzeichnis aufgerufen, von welchem aus 
#	rekusiv nach *.flac Dateien gesucht wird. 
#	Sollte eine Flac-Datei kein LyricFlag haben, wird
#	anhand der Config-Einstellungen wird versucht eine *.lrc zu ermitteln.
#	Falls dies gelingt, wird das LyricFlag gesetzt.
#
import unicodedata
import codecs      # utf8 support
import os, sys, shutil
import fnmatch
import string 
from urlparse import urlparse
import urllib
from pprint import pprint
import locale
from gi.repository import Gtk
from quodlibet.plugins.songsmenu import SongsMenuPlugin
try:
	import logging
	from dacapo.config import readconfig
	from dacapo.metadata import *
	from mutagen.flac import FLAC
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
	### PLUGIN_NAME = "Set dacapo Lyric Flag"
	### PLUGIN_DESC = u"Sucht nach LRC-Dateien für den ausgewählten Song und setzt dementsprechend das LyricFlag-Kennzeichen."
	PLUGIN_NAME = _('Set dacapo Lyric Flag')
	PLUGIN_DESC = _("Sucht nach LRC-Dateien für den ausgewählten Song und setzt dementsprechend das LyricFlag-Kennzeichen.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		super(SetDacapoLyricFlag, self).__init__(*args, **kwargs)
		self.config = readconfig.getConfigObject()
		logging.debug(u'Starte...')
		self.set_sensitive(True)

	def plugin_handles(self, songs):
		for song in songs:
			logging.debug(u'Dateiname: %s' % (song.get("~filename", "")))
		return True

	def plugin_song(self, song):
		try:
			logging.debug(u'Update Dateiname: %s' % (song.get("~filename", "")))
		except:
			return # File doesn't have an APEv2 tag
		### song.update(apesong)
		### mutagen.apev2.delete(song["~filename"])
		## song._song.write()

	def getMetaData(self, flacFilePath):
		aMeta = {'ARTIST': '',
				'ALBUM': '',
				'TITLE': '',
				'LOCAL-PATH': '',
				'GOTLYRICS': False,
				'HASSYNCLYRICS': '0'
				}
		audioFile = getAudioFile(flacFilePath)
		try:
			## audio = FLAC(flacFilePath)
			aMeta['ARTIST']  = ' '.join(audioFile.getMetaData("artist"))
			aMeta['ALBUM'] = ' '.join(audioFile.getMetaData("album"))
			aMeta['TITLE'] = ' '.join(audioFile.getMetaData("title"))
			s = audioFile.getMetaData("hassynclyrics")
			if isinstance(s, list) and len(s) > 0:
				## print 'Laenge von s:' + str(len(s))
				aMeta['HASSYNCLYRICS'] = s[0]

			if len(audioFile.syncText) > 0:
				aMeta['GOTLYRICS'] = True

		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			msgLines = ' '.join(line + '\n' for line in lines)
			print ''.join('!! ' + line for line in lines)  # Log it or whatever here


		return aMeta

	def setLyricFlag(self, flacFilePath, flag='0'):
		try:
			audio = FLAC(flacFilePath)
			audio["hassynclyrics"] = flag
			audio.save()
		except:
			print u'Konnte Datei {0} nicht verarbeiten!'.format(flacFilePath)

	def find(self, startPath):
		iCount = 0
		iError = 0
		iSuccess = 0
		iNoReplace = 0
		iSetFlag = 0
		logging.info(u'Meldung: ; Flac-Datei: ; Artist: ;  Album: ;  Song: ; hassynclyrics: ')
		rootPath = startPath
		pattern = '*.flac'
		for root, dirs, files in os.walk(rootPath):
			for filename in fnmatch.filter(files, pattern):
				iCount += 1
				flacFilePath = os.path.join(root, filename)
				aMeta = self.getMetaData(flacFilePath)
				if(aMeta['GOTLYRICS'] == False):
					iError += 1
					logging.info(u'LRC-Datei OHNE synchronisierte Lyrics ; %s ; %s ; %s ; %s '\
						% (unicode(flacFilePath, errors='replace'), aMeta['ARTIST'],
						aMeta['ALBUM'],
						aMeta['TITLE']))
					self.setLyricFlag(flacFilePath, '0')
				else:
					iSuccess += 1
					logging.debug(u'LRC-Datei MIT synchronisierte Lyrics: ; %s ; %s ; %s ; %s ; %s '\
						% (unicode(flacFilePath, errors='replace'), aMeta['ARTIST'],
						aMeta['ALBUM'],
						aMeta['TITLE'],
						aMeta['HASSYNCLYRICS']
						))
					if(aMeta['HASSYNCLYRICS'] == '1'):
						iNoReplace += 1
					else:
						self.setLyricFlag(flacFilePath, '1')
						iSetFlag += 1

		logging.info(u'Es wurden %i Dateien verarbeitet. ' % (iCount))
		logging.info(u'Davon konnten %i Texte zugeordnet werden. ' % (iSuccess))
		logging.info(u'Davon konnten %i keine Texte zugeordnet werden. ' % (iError))
		logging.info(u'Bei %i wurde das Flag hassynclyrics gesetzt.' % (iSetFlag))
		logging.info(u'Bei %i war das Flag schon gesetzt.' % (iNoReplace))

	def main(self):
		self.find(sys.argv[1])
		# for startPath in sys.argv:
		#    print startPath
