#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Dieses Modul enthält eine Klasse um die metadata einer Audiodatei 
    zu verarbeiten. 
    Für die einzelnen Formate (FLAC, MP3 usw.) wird von dieser Klasse
    abgeleitet und die folgenden Methoden implementiert:

    def loadFile(self):
    def loadFrontCover(self):
    def loadStoredPictures(self):

"""
from dacapo import errorhandling
import sys
import os
try:
    import pygame
except:
    pass
try:
    import random
    import logging
    import codecs      # utf8 support
    import StringIO
    from dacapo.config import readconfig
    from dacapo.ui.blitpicture import BlitPicture
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #
HOMEDIR = os.path.expanduser('~')
CONFIG = readconfig.getConfigObject()

class AudioFile(object):

	def __init__(self, filename):
		self.fileOpen = False
		self.syncLyricFile = None
		self.guiPlayer = CONFIG.getConfig('TEMP', Key='PLAYER')
		self.LEERCD = HOMEDIR + '/.dacapo/' + CONFIG.getConfig('gui', 'misc', 'picNoCover')
		self.debug = CONFIG.getConfig('debug', ' ', 'debugM')
		self.mp3Tags = CONFIG.getConfig('gui', 'metaData', 'MP3-Tags')
		self.fileOpen = False
		self.filename = filename
		self.clearTags()
		self.tags = dict()
		self.loadFile()
		self.addConditions()
		self.syncLyrics = CONFIG.getConfig('gui', 'misc', 'showLyricsSynced')
		# synchronisierte Texte laden?
		if self.syncLyrics == True: self.setSyncLyrics()

	def find_between(self, s, first, last ):
		try:
			start = s.index( first ) + len( first )
			end = s.index( last, start )
			return s[start:end].lower()
		except ValueError:
			return ""


	def setSyncLyrics(self):
		self.syncTime, self.syncText = self.loadSyncLyrics()

	def replaceTags(self, s):
		import re
		i = 0
		while True :
			i += 1
			if i > 99:
				logging.warning(u'Maximal recursion reached. Giving up on {!s}'.format(s))
				break
			text = self.find_between(s, '%', '%')
			if not isinstance(text, basestring):
				break
			if not isinstance(s, basestring):
				break

			if text == '' : break
			if (text.lower() == 'time') or (text.lower() == 'duration') or (text.lower() == 'bandlogo') :
				try:
					insensitive_text = re.compile(re.escape('%' + text + '%'), re.IGNORECASE)
					t = '#' + text.lower() + '#'
					s = insensitive_text.sub(t, s)
				except:
					pass
				logging.debug(u'Returning FIX DATA (%s) = %s' % (s, type(s)))
			res = self.getMetaData(text)
			logging.debug(u'Returning Metadata (%s) = %s' % (res, type(res)))
			if isinstance(res, list) :
				t = '\n'.join(res)
				logging.debug(u'Returning value is a list: %s:' % (t))
			else:
				t = res

			if not isinstance(t, basestring):
				t = ''
			try:
				insensitive_text = re.compile(re.escape('%' + text + '%'), re.IGNORECASE)
				s = insensitive_text.sub(t, s)
			except:
				pass
		return s

	def addConditions(self):
		conditions = CONFIG.getConfig('cond', '')
		for key in conditions.iterkeys() :
			cond = conditions[key]
			logging.debug("Condition:  %s Operator: %s Operand: %s Value: %s" % (
				cond.name,
				cond.operator,
				cond.operand,
				cond.content
				))
			operand = self.getMetaData(cond.operand)
			logging.debug("Condition:  Operand is Type: %s " % (type(operand)))

			if cond.checkOperand(operand) == True:
				logging.debug("Replace  %s " % (cond.content))
				s = self.replaceTags(cond.content)
				logging.debug("Adding:  %s zu den Tags mit Wert: %s" % (
					cond.name,
					s
				))
				self.tags[cond.name.lower()] = [s]
		del cond
		logging.debug("TAGS:  %s " % (self.tags))
		return

	def loadSyncLyrics(self):
		"""
			Hier wird versucht, eine LRC-Datei
			mit synchronisiertem Text zu finden
			und mit <<Sekunden/Text>> zu laden.
			das Ergebnis steht dann in
				self.syncTime[]  und
				self.syncText[]  und
				self.syncCount   als counter mit 0
		"""
		syncedTag = CONFIG.getConfig('gui', 'syncLyrics', 'tag')
		syncedDir = CONFIG.getConfig('gui', 'syncLyrics', 'dir')
		self.syncLyricFile = None
		# Ersatzvariablen auflösen
		while True :
			text = self.find_between(syncedDir, '%', '%')
			if text == '' : break
			syncedDir = syncedDir.replace('%' + text + '%', self.getMetaData(text))

		syncTime = list()
		syncText = list()
		lines = list()
		pathName = os.path.dirname(self.filename)
		fullFileName = os.path.basename(self.filename)
		fileName, fileExtension = os.path.splitext(fullFileName)
		lrcFile = fileName + ".lrc"
		# 1. In der Audio-Datei im TAG lt. config
		logging.debug("Versuche LRC-Text aus Tag zu laden -> %s " % (syncedTag))
		text = self.getMetaData(syncedTag)

		# 2. In der Audio-Datei im TAG "syncedlyrics"
		if len(text) <= 0 and syncedTag <> "syncedlyrics":
			logging.debug("Versuche LRC-Text aus Tag zu laden -> %s " % ("syncedlyrics"))
			text = self.getMetaData("syncedlyrics")

		# 3. Im Verzeichnis lt. config mit selben Namen wie Audio-Datei aber der Erweiterung *.lrc
		if len(text) <= 0 and len(syncedDir) > 0:
			try:
				# testPath = os.path.normpath(os.path.join(pathName, syncedDir))
				testPath = os.path.join(pathName, syncedDir)
				testFile = testPath + "/" + lrcFile
				logging.debug("Versuche LRC-Datei zu laden -> %s " % (testFile))
				if os.path.isfile(testFile) :
					f = codecs.open(testFile, 'r', 'utf-8')
					self.syncLyricFile = testFile
					try: text = f.read()
					except:
						logging.error("Konnte Datei %s nicht lesen" % (testFile) )
						f.close()
						f = open(testFile, 'r')
						try: text = f.read()
						except:
							self.syncLyricFile = None
							logging.error("Konnte Datei %s nicht lesen" % (testFile) )
					finally: f.close()
			except:
				logging.error("Konnte Datei %s %s nicht oeffnen" % (pathName, syncedDir) )

		# 4. Im Verzeichnis der Audio-Datei mit selben Namen aber der Erweiterung *.lrc
		if len(text) <= 0:
			testFile = pathName + "/" + lrcFile
			logging.debug("Versuche LRC-Datei zu laden -> %s " % (testFile))
			if os.path.isfile(testFile) :
				f = codecs.open(testFile, 'r', 'utf-8')
				self.syncLyricFile = testFile
				try: text = f.read()
				except:
					logging.error("Konnte Datei %s nicht lesen" % (testFile) )
					f.close()
					f = open(testFile, 'r')
					try: text = f.read()
					except:
						self.syncLyricFile = None
						logging.error("Konnte Datei %s nicht lesen" % (testFile) )
				finally: f.close()

		# Gefunden?
		if len(text) > 0 :
			lines = text.splitlines()
			for line in lines:
				lineTime = line[line.find("[")+1:line.find("]")]
				lineText = line[line.find("]")+1:]
				if len(lineTime) > 0:
					try : minutes = int(lineTime[:lineTime.find(":")])
					except : continue
					if "." in lineTime :
						try: seconds = int(lineTime[lineTime.find(":")+1:lineTime.find(".")])
						except: seconds = 0
						try: msecs = int(lineTime[lineTime.find(".")+1:])
						except: msecs = 0
					else :
						try: seconds = int(lineTime[lineTime.find(":")+1:])
						except: seconds = 0
						msecs = 0

					seconds += ( minutes * 60 )
					msecs += (seconds * 1000)
					syncTime.append(msecs)
					if len(lineText) > 0:
						syncText.append(lineText)
					else :
						syncText.append("  ")
					logging.debug("Sekunden: %s lineTime: %s Text: %s " % (seconds, lineTime, lineText))
		return (syncTime, syncText)

	def getMetaData(self, key):
		"""
			Hier werden die metadata zurück gegeben.
			In der Konfigurationsdatei wird festgelegt,
			welche Daten wo angezeigt werden.
			Da diese Variablen sich auf FLAC-Tags
			beziehen, muss bei MP3 vorher umgesetzt
			werden.
			Auch diese Umsetzung wird u.a. in der Config-
			Datei festgelegt.
		"""
		# Besonderheit, da auch gerne mal tracknumber = "5/7"
		# gespeichert wird... (gerade bei MP3)
		key = key.lower()
		logging.debug("Angeforderter Key: %s" % (key))
		if key == "tracknumber" :
			logging.debug("Angeforderter Key %s (%s) = %s" % (key, self.getTrack(), type(self.getTrack())))
			return self.getTrack()
		if key == "tracktotal" :
			logging.debug("Angeforderter Key %s (%s) = %s" % (key, self.getTrackTotal(), type(self.getTrackTotal())))
			return self.getTrackTotal()
		if "comment" in key : return self.getComments()
		if key == "bandlogo" :
			logging.debug("Angeforderter Key %s = %s" % (key, type(self.getLogo())))
			return self.getLogo()
		value = ""
		valueList = list()
		bFirst = True
		if self.tags.has_key(key) :
			try :
				for text in self.tags[key]:
					logging.debug("Angeforderter Key %s (%s) = %s" % (key, text, type(text)))
					if isinstance(text, str) or isinstance(text, unicode):
						if bFirst : value = text
						else: value += '\n' + text
						valueList.append(text)
					else :
						if bFirst : value = text.get_text()
						else: value += '\n' + text.get_text()
						valueList.append(text.get_text())
					bFirst = False
			except : pass
		logging.debug("Zurueck Key: %s Value %s" % (key, value))
		return valueList




	def loadPictures(self) :
		showLyrics = self.guiPlayer.showLyricsAsPics
		showWhenSynced = CONFIG.getConfig('gui', 'misc', 'showLyricsWhenSynced')
		self.setMiscPic()
		self.loadStoredPictures()
		# Sind Texte vorhanden? Anzeigen als Bild? Dann los!
		if (len(self.syncTime) > 0) and (showWhenSynced == False) :
			showLyrics = False
		logging.debug("Texte als Bild anzeigen? %s" % (showLyrics))
		listLyrics = list()
		if showLyrics == True :
			listLyrics = self.getLyrics()
		if len(listLyrics) > 0 :
			renderedLyrics = list()
			w = 0
			h = 0
			for strLyrics in listLyrics :
				try:
					tmpStr = strLyrics.rstrip("\n")
					if len(tmpStr) <= 0 : tmpStr = ' '
					fontLyrics = self.guiPlayer.lyricFont.render(tmpStr, True, self.guiPlayer.lyricFontColor)
					txtW, txtH = fontLyrics.get_size()
					if txtW > w : w = txtW
					h = h + txtH
					renderedLyrics.append(fontLyrics)
				except pygame.error, err:
					logging.warning("Error at lyricFont.render(fontLyrics, (%s, %s)) %s " % (0, 0, err))

			image = pygame.Surface([w, h])
			winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
			g = CONFIG.gui[winstate]
			image.fill(g.backgroundColor)
			w = 0
			h = 0
			for fontLyrics in renderedLyrics :
				try:
					image.blit(fontLyrics, (w, h))
				except pygame.error, err:
					logging.warning("Error at image.blit(fontLyrics, (%s, %s)) %s " % (0, 0, err))
				txtW, txtH = fontLyrics.get_size()
				h = h + txtH
			self.setMiscPic(image)


		return

	def getFrontCover(self):
		self.loadFrontCover()
		logging.info("done.")
		return self.cover



	# -------------------- getLyrics ----------------------------------------------------------------

	def getLyrics(self):
		listLyrics = list()
		logging.debug("Suche Lyrics in Tag: %s" %("unsyncedlyrics"))
		strLyrics = ''.join(self.getMetaData('unsyncedlyrics'))
		listLyrics = strLyrics.splitlines()
		if len(listLyrics) <= 0 :
			logging.debug("Nichts gefunden. Suche Lyrics in Tag: %s" %("lyrics"))
			strLyrics = ''.join(self.getMetaData('lyrics'))
			listLyrics = strLyrics.splitlines()
		if len(listLyrics) <= 0 and CONFIG.getConfig('gui', 'misc', 'showSyncedLyricsAsPics'):
			logging.debug("Nichts gefunden. Suche Lyrics in %s" %("syncedlyrics"))
			syncTime, listLyrics = self.loadSyncLyrics()

		if len(listLyrics) > 0 :
			logging.debug("Fündig geworden:  %s" %(listLyrics))
		else:
			logging.debug("Keine Texte gefunden. :-(")

		return listLyrics


	def preBlitLogo(self, key):
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		self.__metaFields = g.fields
		self.loadLogo()
		logging.debug("Try to blit bandlogo ")
		logo = self.getLogo()
		if (logo == None):
			logging.debug("Bandlogo skalieren: Kein: Logo gefunden ")
			return None
		if (not self.__metaFields.has_key(key)):
			logging.debug("Bandlogo skalieren: self.__metaFields hat kein Key: %s " % (key))
			return None
		picPlace = self.__metaFields[key]
		self.guiPlayer.logoPic = None
		winWidth = picPlace.pos.maxWidth
		winHeight = picPlace.pos.maxHeight
		picW, picH = logo.get_size()
		if picW == 0 : picW = 1
		proz = (winWidth * 100.0) / (picW)
		h = int(round( (picH * proz) / 100.0))
		w = int(round(winWidth))
		if h > winHeight :
			proz = (winHeight * 100.0) / (h)
			w = int(round( (w * proz) / 100.0 ))
			h = int(round( (h * proz) / 100.0))
		logging.debug("Bandlogo skalieren: " \
			"Originalbreite: %s Hoehe: %s PROZENT: %s " \
			"-> Neue W: %s H: %s" % (picW, picH, proz, w, h))
		return pygame.transform.scale(logo, (w, h))

	def getTempPic(self, data):
		datei = StringIO.StringIO()
		datei.write(data)
		datei.seek(0)
		return datei

	def getCover(self):
		if self.cover == '???': self.loadFrontCover()
		print("Pic-Type: {!s}".format(type(self.cover)))
		pic = BlitPicture(self.cover)
		return pic.getBlitObject()

	def loadLogo(self):
		return None

	def getLogo(self):
		if self.__logo == None:
			self.loadLogo()
		if self.__logo == None:
			if self.debug: logging.debug('Returning no bandlogo :-( ')
		else:
			if self.debug: logging.debug('Returning bandlogo! :-) ')
		return self.__logo

	def getMiscPic(self):
		random.seed()
		if not self.guiPlayer.resize : random.shuffle(self._MiscPictures)
		return self._MiscPictures

	def getAllPics(self):
		pics = []
		pics.append(self.getFrontCover())
		if self._Backcover <> None :
			pics.append(self._Backcover)
		return pics + self.getMiscPic()

	def getNoOfPics(self):
		return 1 + len(self._MiscPictures)


	def getTrack(self):
		return self.tracknumber

	def getTrackTotal(self):
		return self.trackTotal

	def getTrackOfTotal(self):
		track = self.getTrack()
		totals = self.getTrackTotal()
		if totals == 0 :
			return str(track)
		else:
			return '{0}/{1}'.format(track, totals)

	def getYear(self):
		return self.date

	def getDiscNo(self):
		if type(self.discNo) is str :
			logging.debug('DiscNo ist Typ Str()  %s' % (self.discNo))
			if self.discNo == "1" :
				return "0"
			elif self.discNo == "0" :
				return "0"
			else :
				return self.discNo
		elif type(self.discNo) is not None :
			logging.debug('DiscNo ist nicht None %s' % (self.discNo))
			return str(self.discNo)
		else :
			return "0"
	def getComments(self):
		return self.comments



	## --------------- Setter -----------------------------------

	def setCover(self, cover = None ):
		if cover == None :
			self.cover = "???"
		else :
			self.cover = cover

	def setBackcover(self, cover = None ):
		self._Backcover = cover

	def setMiscPic(self, cover = None ):
		if cover == None :
			self._MiscPictures = []
		else :
			self._MiscPictures.append(cover)

	def setLogo(self, logo = None ):
		if not logo == None:
			if self.debug: logging.debug('Setting bandlogo! ')
		self.__logo = logo

	def setTitle(self, title = None):
		if title == None :
			self.songtitle = "???"
		else :
			self.songtitle = title

	def setArtist(self, artist = None):
		if artist == None :
			self.artist = "???"
		else :
			self.artist = artist

	def setAlbum(self, album = None):
		if album == None :
			self.album = "???"
		else :
			self.album = album

	def setTrack(self, tracknumber = None):
		if tracknumber == None :
			self.tracknumber = 0
		else :
			if "/" in tracknumber:
				self.tracknumber = tracknumber[:tracknumber.find("/")]
				self.setTrackTotal(tracknumber[tracknumber.find("/")+1:])
			else:
				self.tracknumber = tracknumber

	def setTrackTotal(self, tracks = None):
		if tracks == None :
			self.trackTotal = "0"
		else :
			self.trackTotal = tracks

	def setDiscNo(self, number = None):
		if number == None :
			self.discNo = "0"
		else :
			self.discNo = str(number)

	def setCDDB(self, number = None):
		if number == None :
			self.cddb = 0
		else :
			self.cddb = number

	def setYear(self, date = None):
		if date == None :
			self.date = "???"
		else :
			self.date = date

	def setComments(self, comment = None):
		if comment == None :
			self.comments = []
		else :
			self.comments.append(comment)


	def clearTags(self):
		self.setCover()
		self.setBackcover()
		self.setMiscPic()
		self.setLogo()
		self.setTitle()
		self.setArtist()
		self.setAlbum()
		self.setTrack()
		self.setTrackTotal()
		self.setDiscNo()
		self.setCDDB()
		self.setYear()
		self.setComments()
		self.syncTime = []
		self.syncText = []
		self.syncCount = 0


