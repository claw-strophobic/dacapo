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
import platform
from dacapo import errorhandling
try:
	import sys, os, locale
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

fs_encoding = sys.getfilesystemencoding()
encoding = locale.getpreferredencoding()
stdout_encoding = sys.stdout.encoding
stdin_encoding = sys.stdin.encoding
utf8conv = lambda x : unicode(x, stdin_encoding).encode('utf8')

try:
    _fromUtf8 = lambda s : s.encode(stdin_encoding)
except AttributeError:
    _fromUtf8 = lambda s: s
	
class PlayList(object):

	def __init__(self, bIsPlaylist = False, bShuffel = False, bDebug = False):
		self.setDebug( bDebug )
		self.setShuffel( bShuffel )
		self.setIsPlaylist( bIsPlaylist )
		self.__List = []
		mimetypes.init()
		if self.isDebug(): 
			logging.debug("Betriebssytem unterstuetzt Unicode? %s" % (os.path.supports_unicode_filenames) )
			logging.debug("sys.getfilesystemencoding: %s" % (fs_encoding) )
			logging.debug("locale.getpreferredencoding: %s" % (encoding) )
			logging.debug("sys.stdin.encoding: %s" % (stdin_encoding) )
	
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
	def printoutFilename(self, song) :
		import unicodedata
		print "Song ist vom Typ: ", type(song)
				
		codes = {'stdin': stdin_encoding, 'fs_encoding': fs_encoding,
				'encoding': encoding, 'unknown': 'unknown'}
		for k, v in codes.iteritems():
			print '-' * 20 ,
			print ' ' + k + ' ' ,
			print '-' * 20 
			if k == 'unknown':
				uni_song = unicode(song, errors='replace')
			else:
				uni_song = unicode(song, v, 'ignore')
			for i, c in enumerate(uni_song):
				print i, '%04x' % ord(c), unicodedata.category(c),
				print unicodedata.name(c)

	def appendList(self, song) :
		contentType = mimetypes.guess_type(song) # Mimetype herausfinden
		if mimehelp.isInMimeTypes(song) :
			if os.path.isfile(song):
				self.__List.append(song)
				return
			if platform.system() == 'Windows':
				song = song.replace('\\', '/')
 			if os.path.isfile(os.path.realpath(unicode(song, stdin_encoding, 'ignore'))) :
				self.__List.append(os.path.realpath(unicode(song, stdin_encoding)))
			elif os.path.isfile(os.path.realpath(unicode(song, fs_encoding, 'ignore'))) :
				self.__List.append(os.path.realpath(unicode(song, fs_encoding)))
			elif os.path.isfile(os.path.realpath(unicode(song, encoding, 'ignore'))) :
				self.__List.append(os.path.realpath(unicode(song, encoding)))
			elif os.path.isfile(os.path.realpath(unicode(song, errors='replace'))) :
				self.__List.append(os.path.realpath(unicode(song, errors='replace')))
			elif os.path.isfile(song):
				self.__List.append(song)
			else:
				if self.isDebug(): self.printoutFilename(song)
				logging.warning("Kann Datei %s nicht finden. " % (song) )
		elif contentType[0] in mimehelp.M3U_MIMES : 
			self.readPlaylist()


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
					logging.debug("In Playlist(en) gefunden: %s" % (_fromUtf8(f)))

			if self.isShuffel() : self.shuffleList()
		else:	

			for f in self.getInput() :
				if f == None : break
				if platform.system() == 'Windows':
					f = f.replace('\\', '/')
				if os.path.isdir(f): self.walkPath(f)
				elif os.path.isdir(unicode(f, stdin_encoding, 'ignore')) :
					self.walkPath(unicode(f, stdin_encoding, 'ignore'))
				elif os.path.isdir(unicode(f, fs_encoding, 'ignore')) :
					self.walkPath(unicode(f, fs_encoding, 'ignore'))
				elif os.path.isdir(unicode(f, encoding, 'ignore')) :
					self.walkPath(unicode(f, encoding, 'ignore'))
				elif os.path.isdir(unicode(f, errors='replace')) :
					self.walkPath(unicode(f, errors='replace'))
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

