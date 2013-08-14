#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Dieses Modul enthält eine Klasse um Audiodateien zu verarbeiten (momentan FLAC und MP3). """
import sys
import os
from dacapo import errorhandling
try:
	from dacapo.metadata import audiofile
	import logging
	import traceback
	from mutagen.id3 import ID3, APIC
	from mutagen.mp3 import MP3
	import string
	import mutagen
	import pygame
	import random
	import logging
	import traceback
	import codecs      # utf8 support
	import copy
	import platform
	from dacapo.config import readconfig

except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)


class Mp3File(audiofile.AudioFile):

	def __init__(self, playerGUI, filename):
		super(Mp3File, self).__init__(playerGUI, filename)

	def loadFile(self):
		try:
			if self.debug : logging.debug("Versuche MP3-Datei zu laden -> %s " % (self.filename))
			self.audio = MP3(self.filename, ID3=ID3)
			if self.debug : logging.debug("Versuche MP3-metadata zu lesen -> %s " % (self.filename))
			self.loadMetaData()
			if self.debug : logging.debug("alles super ... ")
			self.fileOpen = True
		except BaseException :
			self.fileOpen = False
			logging.error("FEHLER bei %s" % (self.filename) )
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			for line in lines :
				logging.error(line)
		return

	def translateTags(self):
		'''
			Die ID3-Tags werden in VLAC-Tags übersetzt.
			Zuerst werden die Standard-Werte übernommen.
			Danach werden sie ggf. mit Werten aus der 
			Config-Datei überschrieben.			
		'''
		# http://www.unixgods.org/~tilo/ID3/docs/ID3_comparison.html
		# http://www.id3.org/id3v2.4.0-frames.txt
		IDS = {"TIT1": "grouping",
			   "TIT2": "title",
			   "TIT3": "version",
			   "TPE1": "artist",
			   "TPE2": "performer",
			   "TPE3": "conductor",
			   "TPE4": "arranger",
			   "TEXT": "lyricist",
			   "TCOM": "composer",
			   "TENC": "encodedby",
			   "TALB": "album",
			   "TRCK": "tracknumber",
			   "TPOS": "discnumber",
			   "TSRC": "isrc",
			   "TCOP": "copyright",
			   "TPUB": "organization",
			   "TSST": "discsubtitle",
			   "TOLY": "author",
			   "TMOO": "mood",
			   "TBPM": "bpm",
			   "TDRC": "date",
			   "TDOR": "originaldate",
			   "TOAL": "originalalbum",
			   "TOPE": "originalartist",
			   "WOAR": "website",
			   "TSOP": "artistsort",
			   "TSOA": "albumsort",
			   "TSOT": "titlesort",
			   "TSO2": "albumartistsort",
			   "TSOC": "composersort",
			   "TMED": "media",
			   "TCMP": "compilation",
			   # TLAN requires an ISO 639-2 language code, check manually
			   #"TLAN": "language"
		}

		mp3Tags = copy.deepcopy(IDS)
		configTags = self.config.getConfig('gui', 'metaData', 'MP3-Tags')
		for tag in configTags :
			mp3Tags[tag] = configTags[tag]

		return mp3Tags


	def loadMetaData(self):
		"""
			Die MP3-metadata werden eingelesen.
			Ursprünglich wurden die Daten einzeln
			behandelt. Mitlerweile wird das alles
			durch Ersatzvariablen in der Config-
			Datei behandelt.
			Für ein paar Sachen kann es aber
			noch ganz nütlich sein, die Felder
			einzeln aufzubereiten (z.B. TrackNr)
		"""
		mp3Tags = self.translateTags()

		for tag in self.audio.keys():
			bFirst = True
			if mp3Tags.has_key(tag) : 
				realTag = mp3Tags[tag]
			else:
				realTag = tag
			self.tags[realTag] = self.audio[tag]
			

		if self.debug : logging.debug("-> Versuche Titel zu lesen: %s" % (self.filename))
		if self.audio.has_key('TIT2'):
			self.songtitle = " " + self.audio["TIT2"][0]
			if self.debug : logging.debug( "... geschafft! ... %s " % (self.songtitle))
		else:
			self.songtitle = " ????" 
			if self.debug : logging.warning( "... NICHT geschafft! ... ")

		if self.debug : logging.debug("-> Versuche Artist zu lesen: %s" % (self.filename))
		if self.audio.has_key('TPE1'):
			self.artist = " " + self.audio["TPE1"][0]
			if self.debug : logging.debug( "... geschafft! ... %s " % (self.artist))
		elif self.audio.has_key('TPE2'):
		    self.artist = " " + self.audio["TPE2"][0]
		if self.audio.has_key('TALB'):
			self.album = self.audio["TALB"][0] + " "
		if self.audio.has_key('TRCK'):
			self.setTrack(self.audio["TRCK"][0])
			# self.tracknumber = self.audio["TRCK"][0]
		else:
			self.tracknumber = "??"
		if self.audio.has_key('TDRC'):
			self.date = self.audio["TDRC"][0].get_text() 
		else:
			self.date = "???? "

		if self.debug : logging.debug("LENGTH? %s" % (self.audio.info.length))



	def loadFrontCover(self):
		"""
			Es wird nur nach dem Frontcover (Typ 3) gesucht
		"""
		if self.debug : logging.debug("Suche MP3-Cover... %s" % (self.filename))
		diaMode = self.guiPlayer.getDiaMode()
		datei = None

		for tag in self.audio.keys():
			if 'APIC' in tag:
				if self.audio[tag].type == 3:
					if self.debug : logging.debug('Cover gefunden. Typ {0}: {1}'.format(self.audio[tag].type, tag) )
					datei = self.getTempPic(self.audio[tag].data)
					break

		if datei:
			if self.debug : logging.debug("... gefunden! ... ")
			self.cover = pygame.image.load(datei)
		else:
			if self.debug : logging.warning("... NICHT gefunden! ... ")
			self.cover = pygame.image.load(self.LEERCD)

		return

		
	def loadStoredPictures(self):
		"""
			Es werden nur nach dem weiteren Bilder (Typ <> 3) gesucht
		"""
		import StringIO
		if self.debug : logging.debug("Suche MP3-Bilder... %s" % (self.filename))
		diaMode = self.guiPlayer.getDiaMode()
		datei = None
		if diaMode > 1:
			for tag in self.audio.keys():
				if 'APIC' in tag:
					if not self.audio[tag].type == 3:
						if (diaMode == 3 or diaMode == 5) or (self.audio[tag].type > 3 and self.audio[tag].type < 7) :
							if self.debug : logging.debug('Bild gefunden. Typ {0}: {1}'.format(self.audio[tag].type, tag) )
							datei = self.getTempPic(self.audio[tag].data)
							self.setMiscPic(pygame.image.load(datei))



