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
	from mutagen.flac import FLAC, Picture
	import string
	import mutagen
	import pygame
	import random
	import logging
	import traceback
	import codecs      # utf8 support
	import platform
	from dacapo.config import readconfig

except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)


class FlacFile(audiofile.AudioFile):

	def __init__(self, playerGUI, filename):
		super(FlacFile, self).__init__(playerGUI, filename)


	def loadFile(self):
		try:
			self.audio = FLAC(self.filename)	
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

		if self.debug : logging.debug("LENGTH? %s" % (self.audio.info.length) )


	def loadFrontCover(self):
		pics = self.audio.pictures		
		if self.debug : logging.debug('Insgesamt %s Bilder' %(len(pics)))
		datei = None
		if len(pics) > 0:
			# Versuchen ein Frontcover laut Deklaration zu finden
			# oder, wenn es nur ein Bild gibt, dieses nehmen
			for p in pics:
				if p.type == 3 or len(pics) == 1:
					datei = self.getTempPic(p.data)
					break

			# Wenn nix gefunden wurde, nehmen wir das erste Bild
			if not datei :
				for p in pics:
					datei = self.getTempPic(p.data)
					break
				
		if datei :
			self.setCover(pygame.image.load(datei))
		else:
			self.setCover(pygame.image.load(self.LEERCD))		
		return

	def loadStoredPictures(self):
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

