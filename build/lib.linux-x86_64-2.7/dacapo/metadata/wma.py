#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Dieses Modul enthält eine Klasse um Audiodateien zu verarbeiten (momentan FLAC und WMA). """
import sys
import os
from dacapo import errorhandling
try:
	from dacapo.metadata import audiofile
	import logging
	import traceback
	import mutagen.asf
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
	import struct
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)


class WmaFile(audiofile.AudioFile):

	def __init__(self, playerGUI, filename):
		super(WmaFile, self).__init__(playerGUI, filename)

	def loadFile(self):
		try:
			if self.debug : logging.debug("Versuche WMA-Datei zu laden -> %s " % (self.filename))
			self.audio = mutagen.asf.ASF(self.filename)
			if self.debug : logging.debug("Versuche WMA-metadata zu lesen -> %s " % (self.filename))
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
			Die WMA-Tags werden in FLAC-Tags übersetzt.
			Zuerst werden die Standard-Werte übernommen.
			Danach werden sie ggf. mit Werten aus der 
			Config-Datei überschrieben.			
		'''
		#http://msdn.microsoft.com/en-us/library/dd743066%28VS.85%29.aspx
		#http://msdn.microsoft.com/en-us/library/dd743063%28VS.85%29.aspx
		#http://msdn.microsoft.com/en-us/library/dd743220%28VS.85%29.aspx
		IDS = {
		    "WM/AlbumTitle": "album",
		    "Title": "title",
		    "Author": "artist",
		    "WM/AlbumArtist": "albumartist",
		    "WM/Composer": "composer",
		    "WM/Writer": "lyricist",
		    "WM/Conductor": "conductor",
		    "WM/ModifiedBy": "remixer",
		    "WM/Producer": "producer",
		    "WM/ContentGroupDescription": "grouping",
		    "WM/SubTitle": "discsubtitle",
		    "WM/TrackNumber": "tracknumber",
		    "WM/PartOfSet": "discnumber",
		    "WM/BeatsPerMinute": "bpm",
		    "Copyright": "copyright",
		    "WM/ISRC": "isrc",
		    "WM/Mood": "mood",
		    "WM/EncodedBy": "encodedby",
		    "MusicBrainz/Track Id": "musicbrainz_trackid",
		    "MusicBrainz/Album Id": "musicbrainz_albumid",
		    "MusicBrainz/Artist Id": "musicbrainz_artistid",
		    "MusicBrainz/Album Artist Id": "musicbrainz_albumartistid",
		    "MusicBrainz/TRM Id": "musicbrainz_trmid",
		    "MusicIP/PUID": "musicip_puid",
		    "WM/Year": "date",
		    "WM/OriginalArtist": "originalartist",
		    "WM/OriginalAlbumTitle": "originalalbum",
		    "WM/AlbumSortOrder": "albumsort",
		    "WM/ArtistSortOrder": "artistsort",
		    "WM/Genre": "genre",
		    "WM/Publisher": "publisher",
		    "WM/AuthorURL": "website",
		    "Description": "comment"
		}

		wmaTags = copy.deepcopy(IDS)
		configTags = self.config.getConfig('gui', 'metaData', 'WMA-Tags')
		try:
			for tag in configTags :
				wmaTags[tag] = configTags[tag]
		except: pass

		return wmaTags


	def loadMetaData(self):
		"""
			Die WMA-metadata werden eingelesen.
			Ursprünglich wurden die Daten einzeln
			behandelt. Mitlerweile wird das alles
			durch Ersatzvariablen in der Config-
			Datei behandelt.
			Für ein paar Sachen kann es aber
			noch ganz nütlich sein, die Felder
			einzeln aufzubereiten (z.B. TrackNr)
		"""
		wmaTags = self.translateTags()

		for tag in self.audio.keys():
			if wmaTags.has_key(tag) : 
				realTag = wmaTags[tag]
			else:
				realTag = tag
			tmpListe = list()
			for elem in self.audio[tag]:
				if tag == "WM/Picture":					
					tmpListe.append(elem)
				else:
					try: tmpListe.append(unicode(elem))
					except:
						if self.debug : logging.warning("Konnte Element nicht konvertieren: %s" % (tag))
						continue
			self.tags[realTag] = tmpListe
			

		if self.debug : logging.debug("-> Versuche Titel zu lesen: %s" % (self.filename))
		if self.audio.has_key('Title'):
			self.songtitle = " " + unicode(self.audio["Title"][0])
			if self.debug : logging.debug( "... geschafft! ... %s " % (self.songtitle))
		else:
			self.songtitle = " ????" 
			if self.debug : logging.warning( "... NICHT geschafft! ... ")

		if self.debug : logging.debug("-> Versuche Artist zu lesen: %s" % (self.filename))
		if self.audio.has_key('Author'):
			self.artist = " " + unicode(self.audio["Author"][0])
			if self.debug : logging.debug( "... geschafft! ... %s " % (self.artist))
		elif self.audio.has_key('WM/AlbumArtist'):
		    self.artist = " " + unicode(self.audio["WM/AlbumArtist"][0])
		if self.audio.has_key('WM/AlbumTitle'):
			self.album = unicode(self.audio["WM/AlbumTitle"][0]) + " "
		if self.audio.has_key('WM/TrackNumber'):
			self.setTrack(unicode(self.audio["WM/TrackNumber"][0]))
		else:
			self.tracknumber = "??"
		if self.audio.has_key('WM/Year'):
			self.date = unicode(self.audio["WM/Year"][0] )
		else:
			self.date = "???? "




	def loadFrontCover(self):
		"""
			Es wird nur nach dem Frontcover (Typ 3) gesucht
		"""
		if self.debug : logging.debug("Suche WMA-Cover... %s" % (self.filename))
		diaMode = self.guiPlayer.getDiaMode()
		datei = None
		
		for image in self.audio.get("WM/Picture", []):
			(mime, data, type) = self.unpack_image(image.value)
			if type == 3:  # Only cover images
				datei = self.getTempPic(data)
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
		if self.debug : logging.debug("Suche WMA-Bilder... %s" % (self.filename))
		diaMode = self.guiPlayer.getDiaMode()
		datei = None
		if diaMode > 1:
			for image in self.audio.get("WM/Picture", []):
				(mime, data, type) = self.unpack_image(image.value)
				if not type == 3:
					if (diaMode == 3 or diaMode == 5) or (type > 3 and type < 7) :
						if self.debug : logging.debug('Bild gefunden. Typ {0}'.format(type) )
						self.setMiscPic(pygame.image.load(self.getTempPic(data)))

		return

	def unpack_image(self, data):
		"""
		(bei quodlibet geklaut)
		Helper function to unpack image data from a WM/Picture tag.

		The data has the following format:
		1 byte: Picture type (0-20), see ID3 APIC frame specification at
		http://www.id3.org/id3v2.4.0-frames
		4 bytes: Picture data length in LE format
		MIME type, null terminated UTF-16-LE string
		Description, null terminated UTF-16-LE string
		The image data in the given length
		"""
		(type, size) = struct.unpack_from("<bi", data)
		pos = 5
		mime = ""
		while data[pos:pos + 2] != "\x00\x00":
		    mime += data[pos:pos + 2]
		    pos += 2
		pos += 2
		description = ""
		while data[pos:pos + 2] != "\x00\x00":
		    description += data[pos:pos + 2]
		    pos += 2
		pos += 2
		image_data = data[pos:pos + size]
		return (mime.decode("utf-16-le"), image_data, type)


