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
	from mutagen.oggvorbis import OggVorbis as OGG, OggVCommentDict, OggVorbisInfo
	from mutagen.flac import Picture
	import string
	import mutagen
	import pygame
	import logging
	import traceback
	import codecs      # utf8 support
	import platform
	import base64
	from dacapo.config import readconfig

except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)


class OggFile(audiofile.AudioFile):

	def __init__(self, playerGUI, filename):
		super(OggFile, self).__init__(playerGUI, filename)


	def loadFile(self):
		try:
			audiofile = file(self.filename)
			oggInfo = OggVorbisInfo(audiofile)
			self.audio = OggVCommentDict(audiofile, oggInfo)
			self.loadMetaData()
			self.fileOpen = True
		except BaseException :
			self.fileOpen = False
			logging.error("FEHLER bei %s" % (self.filename) )
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			for line in lines :
				logging.error(line)
		return


	def loadMetaData(self):
		"""
			Die FLAC-metadata werden eingelesen.
			Ursprünglich wurden die Daten einzeln
			behandelt. Mitlerweile wird das alles
			durch Ersatzvariablen in der Config-
			Datei behandelt.
			Für ein paar Sachen kann es aber
			noch ganz nütlich sein, die Felder
			einzeln aufzubereiten (z.B. TrackNr)
		"""

		for tag in self.audio.keys():
			# der darf nicht! : metadata_block_picture
			if tag.lower() == "metadata_block_picture" or \
				tag.lower() == "coverart" : continue

			self.tags[tag] = self.audio[tag]
			for text in self.audio[tag]:

				if tag == 'title' :
					if self.debug : logging.debug('Title? {0}: {1}'.format(tag, text.encode('UTF-8')) ) 
					self.setTitle(text)
				elif tag == 'artist' :
					if self.debug : logging.debug( 'Artist? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setArtist(text)
				elif tag == 'album' :
					if self.debug : logging.debug( 'Album? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setAlbum(text)
				elif tag == 'tracknumber' :
					if self.debug : logging.debug( 'Track? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setTrack(text)
				elif tag == 'tracktotal' :
					if self.debug : logging.debug( 'Tracks? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setTrackTotal(text)
				elif tag == 'discnumber' :
					if self.debug : logging.debug( 'Discnumber? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setDiscNo(text)
				elif tag == 'cddb' :
					if self.debug : logging.debug( 'CDDB? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setCDDB(text)
				elif tag == 'date' :
					if self.debug : logging.debug( 'Year? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setYear(text)
				elif tag == 'lyrics' :
					if self.debug : logging.debug( 'Lyrics? {0}: {1}'.format(tag, text.encode('UTF-8')) )
				elif 'comment' in tag :
					if self.debug : logging.debug( 'Comment? {0}: {1}'.format(tag, text.encode('UTF-8')) )
					self.setComments(text)
				else:
					if self.debug : logging.debug('Unhandled Tag {0}: {1}'.format(tag, text.encode('UTF-8')) )



	def loadFrontCover(self):
		if self.debug : logging.debug("Suche OGG-Cover... %s" % (self.filename))
		diaMode = self.guiPlayer.getDiaMode()
		cover = None

		coverdesc = []
		covertype = []

		for frame in self.audio.keys():
			for tag in self.audio[frame]:
				if frame.lower() == "coverarttype" :
					if self.debug : logging.debug("Tag %s" % (frame))
					covertype.append(tag)
				elif frame.lower() == "coverartdescription" :
					if self.debug : logging.debug("Tag %s" % (frame))
					coverdesc.append(tag)



		for frame in self.audio.keys():
			if frame.lower() == "metadata_block_picture" :
				pictures = []
				try:
					pictures.append(Picture(base64.b64decode(self.audio[frame])))
				except TypeError:
					if self.debug : logging.debug("Fehler beim Bild.")

				for pic in pictures:
					if pic.type == 3:
						cover = self.getTempPic(pic.data)
						break

			elif frame.lower() == "coverart" :
				pictures = []		
				for index, p in enumerate(self.audio[frame]) : 
					coverdesc.append("unknown")
					covertype.append(0)
					coverTemp = self.audio[frame]
					try:
						coverTemp = coverTemp and base64.b64decode(coverTemp[index])
						if self.debug : 
							logging.debug("Cover # %s Type %s Desc: %s" % (index, covertype[index], coverdesc[index]))
						if int(covertype[index]) == 3:
							cover = self.getTempPic(coverTemp)
							break
					except TypeError:
						if self.debug : logging.debug("Fehler bei Bild %s" % (index))
 

		if cover:
			if self.debug : logging.debug("... gefunden! ... ")
			self.cover = pygame.image.load(cover)
		else:
			if self.debug : logging.warning("... NICHT gefunden! ... ")
			self.cover = pygame.image.load(self.LEERCD)

		return

	def loadStoredPictures(self):
		return
		diaMode = self.guiPlayer.getDiaMode()
		pics = self.audio.pictures
		if self.debug : logging.info('Insgesamt %s Bilder' %(len(pics)))
		# wenn nur ein Bild vorhanden ->
		# abbrechen, denn dies wurde als Frontcover
		# behandelt
		if len(pics) <= 1 : 
			return

		foundBackcover = False
		for p in pics:
			if self.debug : logging.debug('Bild gefunden. Typ {0}: {1}'.format(p.type, p.desc.encode('UTF-8')) )
			if not p.type == 3:			
				if (diaMode == 3 or diaMode == 5) or (p.type > 3 and p.type < 7) :
					datei = self.getTempPic(p.data)
					if p.type == 4 and not foundBackcover and diaMode > 3 :
						foundBackcover = True
						self.setBackcover(pygame.image.load(datei))
					else :
						self.setMiscPic(pygame.image.load(datei))
		
		if self.debug : logging.info('done.')
		return

