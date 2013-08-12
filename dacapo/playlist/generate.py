#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#! /usr/bin/python
################################################################################
# small Gnome Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
################################################################################


# contentType = mimetypes.guess_type(self.path) # Mimetype herausfinden
# import mimetypes

"""Dieses Modul enthält die Playlist-Verarbeitung / -Aufbereitung. """
from dacapo import errorhandling
try:
	import sys, os
	import random
	import mimetypes
	from dacapo.metadata import mimehelp
	import pickle
	import logging
	import traceback
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #
HOMEDIR = os.path.expanduser('~')
CONFIG_DIR = HOMEDIR + '/.dacapo/'
LIST_NAME = CONFIG_DIR + 'lastPlaylist.tmp'

### Klassendefinitionen



class PlayList(object):

	def __init__(self, bIsPlaylist = False, bShuffel = False, bDebug = False):
		self.setDebug( bDebug )
		self.setShuffel( bShuffel )
		self.setIsPlaylist( bIsPlaylist )
		self.__List = []
		mimetypes.init()


#-------- Setter -----------------------------#
	
	def setDebug(self, bDebug):
		self.__bDebug = bDebug

	def setShuffel(self, bShuffel):
		self.__bShuffel = bShuffel

	def setIsPlaylist(self, bPlaylist):
		self.__bPlaylist = bPlaylist

	def setInput(self, Files) :
		self.__Files = Files

#-------- Getter -----------------------------#

	def isDebug(self):
		return self.__bDebug

	def isShuffel(self):
		return self.__bShuffel

	def isPlaylist(self):
		return self.__bPlaylist

	def getInput(self) :
		return self.__Files

	def getPlaylist(self) :
		return self.__List

#-------- Funktionen -------------------------#

	def appendList(self, song) :
		if os.path.isfile(song):
			contentType = mimetypes.guess_type(song) # Mimetype herausfinden
			if self.isDebug() : logging.debug("appendList() -> Angegebene Datei ist vom Typ: %s" % (contentType[0]) )
			if contentType[0] in mimehelp.FLAC_MIMES \
			or contentType[0] in mimehelp.OGG_MIMES \
			or contentType[0] in mimehelp.WMA_MIMES \
			or contentType[0] in mimehelp.MPG_MIMES : 
				self.__List.append(song)
			elif contentType[0] == None or contentType[0] == 'audio/x-mpegurl' : self.readPlaylist()
		else : 
			print >> sys.stderr, "FEHLER: Kann Datei %s nicht finden. " % (song)
			logging.warning("appendList() -> Kann Datei %s nicht finden. " % (song) )
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			for line in lines :
				logging.warning(line)


	def resume(self):
		datei = open(LIST_NAME, "r")
		self.__List = pickle.load(datei)
		datei.close()
		return

	def proceed(self):
		if self.isPlaylist() :
			self.readPlaylist()
			if self.isDebug() :
				for f in self.getPlaylist() :
					logging.debug("In Playlist(en) gefunden: %s" % (f))

			if self.isShuffel() : self.shuffleList()
		else:	

			for f in self.getInput() :
				if f == None : break
				if os.path.isdir(f): self.walkPath(f)
				else : self.appendList(f)

			if self.isShuffel() : self.shuffleList()

			if self.isDebug() :
				for f in self.getPlaylist() :
					logging.debug("Folgende Dateien gefunden: %s" % (f))

		# self.tf = tempfile.NamedTemporaryFile(prefix='dacapo-', delete=False)
		datei = open(LIST_NAME, "w")
		pickle.dump(self.getPlaylist(), datei)
		datei.close()
		return

	def shuffleList(self) :
		random.seed()
		random.shuffle(self.__List)

	def sortList(self) :
		self.__List.sort()

	def walkPath(self, startPath):
		for root, dirs, files in os.walk(startPath):
			for filename in files:
				self.appendList( os.path.join(root, filename) )
		
		self.sortList()
		return



	def readPlaylist(self):
		for f in self.getInput() :
			if os.path.isfile(f):
				try:
					datei = open(f, "r")
					for zeile in datei:
						if not "#" in zeile:
							self.appendList(zeile.strip())
					datei.close()
					self.setIsPlaylist(True)
				except BaseException :
					print >> sys.stderr, " FEHLER: Kann Playlist %s nicht oeffnen! " % (f)
					logging.error("readPlaylist() -> Kann Datei %s nicht oeffnen. " % (f) )
					exc_type, exc_value, exc_traceback = sys.exc_info()
					lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
					for line in lines :
						logging.error(line)
			else:
				print >> sys.stderr, " FEHLER: Kann Playlist %s nicht finden. " % (f)
				logging.error("readPlaylist() -> Kann Datei %s nicht finden. " % (f) )
		return 


if __name__ == '__main__':
	print __doc__
	print dir()
	exit(0)	

