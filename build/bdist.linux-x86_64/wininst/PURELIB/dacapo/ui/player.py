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
	this module handles the pygame-GUI and from here the
	playlist, the GStreamer-module as well as the metadata.
	one could say, it the core of the dacapo.
'''

import sys
import os
import platform
from dacapo import errorhandling
if platform.system() == 'Windows':
	try:
		from ctypes import windll
	except ImportError, err:
		errorhandling.Error.show()
		sys.exit(2)
#   os.environ['SDL_VIDEODRIVER'] = 'directx'
try:
	# aus irgendeinem Grunde braucht Windows gtk für gobjects-import in dacapoGST
	import gtk
	from pygame.locals import *	
	import pygame
	from dacapo.metadata import *
	from dacapo.dacapoGST import GstPlayer
	from dacapo.config import readconfig
	from dacapo.dacapoHelp import SHOWPIC_CHOICES
	import random
	import logging
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #

HOMEDIR = os.path.expanduser('~')
CONFIG_DIR = HOMEDIR + '/.dacapo/'
LIST_NAME = CONFIG_DIR + 'lastPlaylistNumber.tmp'

# ----------- Klassendefinitionen ----------------------------- #


class playerGUI():

	def __init__(self, oPlaylist, 
					ausschalter, hauptschalter):

		self.ausschalter = ausschalter
		self.hauptschalter = hauptschalter
		pygame.init()
		pygame.key.set_repeat(1, 1)
		# Legt fest, wie oft Tastendruecke automatisch wiederholt werden
		# Das erste Argument gibt an ab wann, das zweite in welchen
		# Intervallen der Tastendruck wiederholt wird
		# self.oConfig = readconfig.getConfigObject()
		self.oConfig = readconfig.getConfigObject()
		self.ShowGUI = bool(self.oConfig.getConfig('TEMP', Key='SHOWGUI'))
		bResume = self.oConfig.getConfig('TEMP', Key='RESUME')
		self.clock = pygame.time.Clock()
		# Erstellt einen Zeitnehmer
		self.setDebug(self.oConfig.getConfig('debug', ' ', 'debugGUI'))
		self.setGSDebug(self.oConfig.getConfig('debug', ' ', 'debugS'))
		self.isGapless = self.oConfig.getConfig('audio_engine', 'audio_engine', 'gapless')
		self.resize = False

		self.setReplayGain(self.oConfig.getConfig('audio_engine', 'audio_engine', 'replayGain'))
		self.setDiaMode(self.oConfig.getConfig('gui', 'misc', 'showPics'))

		# gstPlayer wird als GTK-thread gestartet
		if self.getDebug(): logging.debug(\
			'versuche GstPlayer zu starten...')
		self.gstPlayer = GstPlayer(self, ausschalter)
		self.gstPlayer.start()
		if self.getDebug(): logging.debug(\
			'versuche GstPlayer zu starten... done.')

		self.isPlaylist = oPlaylist.isPlaylist()
		self.playlist = oPlaylist.getPlaylist()
		self.actSong = 0
		if bResume:
			datei = open(LIST_NAME, "r")
			self.actSong = int(datei.read())
			datei.close()
		self.pos = "0"
		self.status = "Stop"
		self.fullscreen = self.oConfig.getConfig('TEMP', Key='FULLSCREEN')
		self.winState = 'window'
		if self.fullscreen: self.winState = 'fullscreen'

		self.doInitDisplay()
		self.playNextSong()
		return

# -------------------- Texte anzeigen ----------------------------------------
	def find_between(self, s, first, last ):
		try:
		    start = s.index( first ) + len( first )
		    end = s.index( last, start )
		    return s[start:end]
		except ValueError:
		    return ""

	def blitText(self):
		"""In dieser Funktion werden die metadata (inkl. Bilder)
		in das Fenster projeziert.
		Zuerst wird das Fenster mit der Hintergrundfarbe gefüllt,
		welche aus der Konfiguration geholt wird.
		Dann werden die Texte aufbereitet.
		Dies geschieht mit dem Font self.font und der Farbe aus self.fontColor
		- der Font selbst wird aber an anderer Stelle berechnet.
		Abhängig von der Anzahl der Bilder werden diese berechnet,
		skaliert und geschrieben."""

		# Fenster initialisieren (mit Hintergrundfarbe füllen
		try: self.screen.fill(self.oConfig.getConfig('gui', self.winState,
												'backgroundColor'))
		except: pass

		# Fenstergröße holen
		width, height = self.resolution

		# metadata holen und aufbereiten
		if self.getDebug(): logging.debug(\
			'rendere Texte: {0}'.format(self.filename))
		textMetaVar = []
		textMetaVar.append(self.oConfig.getConfig('gui', 'metaData', 'if_playlist'))
		textMetaVar.append(self.oConfig.getConfig('gui', 'metaData', 'if_discNr'))
		i = 0
		for s in textMetaVar :
			s = s.replace('%time%', self.gstPlayer.getDuration())
			s = s.replace('%duration%', self.gstPlayer.getDuration())
			if self.isPlaylist :
				s = s.replace('%tracknumberlist%', str(self.actSong))
				s = s.replace('%tracktotallist%', str(len(self.playlist)))
			text = s
			while True :
				text = self.find_between(s, '%', '%')
				if text == '' : break
				s = s.replace('%' + text + '%', self.audioFile.getMetaData(text))

			textMetaVar[i] = s
			i += 1
			
		if not self.isPlaylist : textMetaVar[0] = ''
		if self.audioFile.getDiscNo() == "0" : textMetaVar[1] = ''		
			
		textMetaData = []
		textMetaData.append(self.oConfig.getConfig('gui', 'metaData', 'topLeft'))
		textMetaData.append(self.oConfig.getConfig('gui', 'metaData', 'topRight'))
		textMetaData.append(self.oConfig.getConfig('gui', 'metaData', 'bottomLeft'))
		textMetaData.append(self.oConfig.getConfig('gui', 'metaData', 'bottomRight'))
		
		
		i = 0
		for s in textMetaData :
			if '%time%' in s :
				self.textActTime = s
				self.posActTime = i
 
			s = s.replace('%time%', self.gstPlayer.getDuration())
			s = s.replace('%duration%', self.gstPlayer.getDuration())
			s = s.replace('%if_playlist%', textMetaVar[0])
			s = s.replace('%if_discNr%', textMetaVar[1])
			if self.isPlaylist :
				s = s.replace('%tracknumberlist%', str(self.actSong))
				s = s.replace('%tracktotallist%', str(len(self.playlist)))

			text = s
			while True :
				text = self.find_between(s, '%', '%')
				if text == '' : break
				s = s.replace('%' + text + '%', self.audioFile.getMetaData(text))

			textMetaData[i] = s
			i += 1
		
		fontMetaData = []
		for s in textMetaData :
			fontMetaData.append(self.font.render(s, True, self.fontColor))
		

		# ---------------------------------------------------------------------------
		# Texte auf das Fenster projezieren
		# Dabei wird an der rechten Spalte der verbleibende Raum mitgerechnet
		# damit da evtl. Bilder angezeigt werden können
		#  - self.wRemain = width remaining
		#  - self.hRemain = height remaining
		#       = Größe des verbleibenden Rechtecks
		#  - self.wStart = width Startposition
		#  - self.hStart = height Startposition
		#       = Linke obere Ecke des verbeliebenden Rechtecks
		#
		#  - self.txtTitleH & self.txtTitleW wird gespeichert, da hiervon abhängig
		# in der Function updateActTime() die Laufzeit/Position angezeigt wird.
		#

		self.wRemain = width
		self.hRemain = height
		self.wStart = 0
		self.hStart = 0

		if self.getDebug():
			logging.debug('blitte Texte: {0}'.format(self.filename))

		# links oben den Artist
		if self.getDebug():
			logging.debug('TopLeft: {0}'.format(textMetaData[0]))
		# if not self.screen.get_locked(): self.screen.blit(textArtist, (0, 0))
		if not self.screen.get_locked(): self.screen.blit(fontMetaData[0], (0, 0))
		if self.posActTime == 0 : self.rectActTime = (0, 0)

		# links unten den Titel
		if self.getDebug():
			logging.debug('BottomLeft: {0}'.format(textMetaData[2]))
		txtW, txtH = fontMetaData[2].get_size()
		h = (height - txtH) 
		if not self.screen.get_locked() : self.screen.blit(fontMetaData[2], (0, h)) 
		self.txtTitleH = h
		self.txtTitleW = 0
		if self.posActTime == 2 : self.rectActTime = (0, h)

		# rechts oben das Album
		if self.getDebug() : logging.debug('TopRight: {0}'.format(textMetaData[1]))
		txtW, txtH = fontMetaData[1].get_size()
		w = (width - txtW)
		h = 0
		if not self.screen.get_locked() :  self.screen.blit(fontMetaData[1], (w, h)) 
		if self.posActTime == 1 : self.rectActTime = (w, h)
		self.hRemain -= txtH
		h += txtH

		# darunter das Jahr
		# --> habe ich hinter den Albumtitel gesetzt
		# txtW, txtH = textDate.get_size()
		# w = (width - txtW)
		# self.screen.blit(textDate, (w, h)) 
		# h += txtH
		# self.hRemain -= txtH

		# darunter evtl. Kommentare
		self.showComments = self.oConfig.getConfig('gui', 'misc', 'showComments')
		
		self.startComments = h
		if self.showComments :	
			if self.getDebug() : logging.debug('Bereite Kommentare auf: {0}'.format(self.filename))
			comments = self.audioFile.getComments()
			if len(comments) > 0 :
				for t in comments :
					textComment = self.font.render(t + " ", True, self.fontColor)
					txtW, txtH = textComment.get_size()
					w = (width - txtW)
					if not self.screen.get_locked() : self.screen.blit(textComment, (w, h)) 
					h += txtH
					self.hRemain -= txtH
		self.hStart = h

		# rechts unten die Laufzeit vorsehen
		if self.getDebug() : logging.debug('BottomRight: {0}'.format(textMetaData[3]))
		txtW, txtH = fontMetaData[3].get_size()
		# textActPos = self.font.render("  :  / :   ", True, self.fontColor)
		# txtW, txtH = textActPos.get_size()
		h = (height - txtH) 
		w = (width - txtW)
		if not self.screen.get_locked() :  self.screen.blit(fontMetaData[3], (w, h)) 
		if self.posActTime == 3 : self.rectActTime = (w, h)
		self.hRemain -= txtH


		# für Haupt-Bild bzw. Diashow verbleibende Fenstergröße:
		self.winWidth = width
		self.winHeight = height - txtH * 2
		if len(self.audioFile.syncText) > 0 : 
			self.winHeight -= self.lyricFontHeight

		# Frontcover			0 		1 			2 			3 			4 				5				6
		# SHOWPIC_CHOICES = ["NO", "coverOnly", "allCover", "allPics", "diaShowAllCover", "diaShowAllPics", "help"]
		self.timerIndex = 0
		if not self.resize : self.diaIndex = 0
		else : self.diaIndex = self.diaIndex - 1

		self.diaShowPics = []
		if self.getDiaMode() < 1 :
			pass
		elif self.getDiaMode() == 1 or self.getDiaMode() > 3 :
			if self.getDebug() : logging.debug('Hole Frontcover: {0}'.format(self.filename))
			if self.resize == False : 
				self.audioFile.getFrontCover()
				self.pic = self.audioFile.getFrontCover()
		else :
			if self.getDebug() : logging.debug('Lade alle Bilder: {0}'.format(self.filename))
			if self.resize == False : 
				self.pic = self.audioFile.getFrontCover()
				self.audioFile.loadPictures()
		
		if self.getDiaMode() > 0 :
			if self.getDiaMode() < 4 : self.blitPics()
			elif not self.resize : self.blitPics()
			
		if not self.screen.get_locked() : 
			self.screen.lock()
			try: pygame.display.update()
			except pygame.error, err: logging.warning("dacapo: Error at pygame.display.update() in function blitText(). %s" % (err))
			self.screen.unlock()

		if not self.resize : self.timerIndex = self.gstPlayer.queryNumericPosition()
		if self.getDiaMode() < 1 : 
			pass
		elif self.getDiaMode() > 3 :
			if self.getDebug() : logging.debug('Bereite DiaShow vor: {0}'.format(self.filename))
			if not self.resize : self.audioFile.loadPictures()
			self.audioFile.preBlitDiaShow()

		self.resize = False
		return

 
# -------------------- Kommentare über die Bilder schreiben --------------------------------------------

	def blitComments(self):

		# Fenstergröße holen
		width, height = self.resolution

		# if self.getDebug() : print 'Schreibe evtl. Kommentare ggf. ueber die Bilder: {0}'.format(self.filename)

		# darunter evtl. Kommentare
		h = self.startComments 
		comments = self.audioFile.getComments()
		if self.getDebug() : logging.debug(' => %s Kommentare ab Position %s' % (len(comments), h))
		if len(comments) > 0 :
			for t in comments :
				textComment = self.font.render(t + " ", True, self.fontColor)
				txtW, txtH = textComment.get_size()
				w = (width - txtW)
				if not self.screen.get_locked() : self.screen.blit(textComment, (w, h)) 
				if not self.screen.get_locked() : 
					self.screen.lock()
					try: pygame.display.update((w, h, txtW, txtH))
					except pygame.error, err: logging.warning("dacapo: Error at pygame.display.update() in function blitComments(). %s" % (err))
					self.screen.unlock()
				h += txtH

		# if self.getDebug() : print 'Fertig: {0}'.format(self.filename)
		return
 
# -------------------- Bilder anzeigen ----------------------------------------------------------------

	def blitPics(self):

		# Fenstergröße holen
		width, height = self.resolution

		# --> skalieren -------------------------------
		picW, picH = self.pic.get_size()
		picH = int(round(1.0 * self.winWidth / picW * picH))
		picW = self.winWidth
		picW = int(round(1.0 * self.winHeight / picH * picW))
		picH = self.winHeight
		w = int(round(picW))
		h = int(round(picH))
		tmp = pygame.transform.scale(self.pic, (w, h))
		if self.getDebug() : logging.debug("Fensterbreite: %s Hoehe: %s  Picturebreite: %s Hoehe: %s" % (self.winWidth, self.winHeight, w, h))
		self.wRemain -= w
		self.wStart += w 
		self.pic = tmp
		# <-- skalieren -------------------------------
		# --> positionieren ---------------------------
		h = self.fontHeight
		h = int(round( (height - picH) / 2 ))
		if len(self.audioFile.syncText) > 0  and \
			self.oConfig.getConfig('gui', 'syncLyrics', 'position').upper()  == "TOP" :
				h += self.lyricFontHeight / 2
		elif len(self.audioFile.syncText) > 0  and \
			self.oConfig.getConfig('gui', 'syncLyrics', 'position').upper()  == "BOTTOM" :
				h -= self.lyricFontHeight / 2

		if self.audioFile.getNoOfPics() > 1 and self.getDiaMode() > 1 and self.getDiaMode() < 4:
			w = 0
			# h = int(round( (height - picH) / 2 ))
		else :
			w = int(round( (width - picW) / 2 ))
			# h = int(round( (height - picH) / 2 ))
		# <-- positionieren ---------------------------
		if not self.screen.get_locked() : self.screen.blit(self.pic, (w, h))
		self.setLastRect(w, h, picW, picH)

		# andere Bilder
		if self.getDiaMode() > 1 and self.getDiaMode() < 4:
			strPosH = self.hStart
			strPosW = self.wStart
			pics = self.audioFile.getMiscPic()
			for p in pics :
				if self.getDebug() : logging.debug("verarbeite Bild...")
				if self.getDebug() : logging.debug(\
					"Verbliebene Fensterbreite: %s Hoehe: %s Startposition W: %s H: %s" % (self.wRemain, self.hRemain, strPosW, strPosH))

				# --> skalieren -------------------------------
				tPicW, tPicH = p.get_size()

				proz = (self.wRemain * 100.0) / (tPicW)  
				h = int(round( (tPicH * proz) / 100.0))
				w = int(round(self.wRemain))
				if self.getDebug() : logging.debug(\
					"Picture skalieren: Originalbreite: %s Hoehe: %s PROZENT: %s -> Neue W: %s H: %s" % (tPicW, tPicH, proz, w, h))
				if h > self.hRemain :
					proz = (self.hRemain * 100.0) / (h)  
					w = int(round( (w * proz) / 100.0 ))
					h = int(round( (h * proz) / 100.0))
					if self.getDebug() : logging.debug(\
					"NEUSKALIERUNG da Bild zu hoch wurde: Originalbreite: %s Hoehe: %s PROZENT: %s -> Neue W: %s H: %s " % (tPicW, tPicH, proz, w, h))
			

				self.hRemain -= h
				tmpPic = pygame.transform.scale(p, (w, h))
				if not self.screen.get_locked() : self.screen.blit(tmpPic, (strPosW, strPosH))
				strPosH += h
				if self.hRemain <= 0 : break
		if self.oConfig.getConfig('gui', 'misc', 'overlayComments') and self.showComments : 
			self.blitComments()

		return

 


# -------------------- Diashow ----------------------------------------------------------------

	def diaShow(self):

		if self.getDebug() : logging.debug("pygame.display.get_init = %s " % (pygame.display.get_init()))
		if self.getDebug() : logging.debug("pygame.display.get_active = %s " % (pygame.display.get_active()) )
		if self.getDebug() : logging.debug("Anzahl Bilder: %s -> aktuelles Bild: Nr %s" % (len(self.diaShowPics), self.diaIndex))
		if len(self.diaShowPics) <= 1 and self.diaIndex >= 0 :
			if self.getDebug() : logging.debug("Breche diaShow ab, da Anzahl Bilder: %s " % (len(self.diaShowPics)))
			return

		# Altes Bild löschen
		# if self.diaIndex > -1 :
		try: 
			if self.getDebug() : logging.info("clearLastRect")
			self.clearLastRect()
			if self.getDebug() : logging.info("done.")
		except: 
			if self.getDebug() : 
				logging.warning("FEHLER IN diaShow() bei Bild Nr: %s --> Beim Versuch den alten Bereich zu initialisieren!" % (self.diaIndex))

		# Fenstergröße holen
		width, height = self.resolution

		# Index größer als Anzahl Bilder -> Index initialisieren
		self.diaIndex += 1 
		if self.diaIndex > (len(self.diaShowPics) -1): self.diaIndex = 0

		# if self.getDebug() : print "diaShow() -> Uebertrage Screen Nr: %s -> self.screen " % (self.diaIndex)

		## -- Hier kann es passieren, dass die Liste noch nicht aufgebaut ist... deshalb evtl. Fehler abfangen!
		try:
			picW, picH = self.diaShowPics[self.diaIndex].get_size()
			# --> positionieren ---------------------------
			w = (width - picW) / 2
			h = (height - picH) / 2
			# h = self.fontHeight
			# h = self.fontHeight / 2
			if len(self.audioFile.syncText) > 0  and \
				self.oConfig.getConfig('gui', 'syncLyrics', 'position').upper()  == "TOP" :
					h += self.lyricFontHeight / 2
			elif len(self.audioFile.syncText) > 0  and \
				self.oConfig.getConfig('gui', 'syncLyrics', 'position').upper()  == "BOTTOM" :
					h -= self.lyricFontHeight / 2

			# <-- positionieren ---------------------------

			if not self.screen.get_locked() : self.screen.blit(self.diaShowPics[self.diaIndex],(w,h)) 

			self.setLastRect(w, h, picW, picH)

			if self.oConfig.getConfig('gui', 'misc', 'overlayComments') and self.showComments :	
				self.blitComments()

			if not self.screen.get_locked() :
				if self.getDebug() : logging.info("display update")
				self.screen.lock()
				try: pygame.display.update((w, h, picW, picH))
				except pygame.error, err: logging.warning(\
					"Error at pygame.display.update() in function diaShow(). %s" % (err))
				self.screen.unlock()
				if self.getDebug() : logging.info("done.")
			else :
				if self.getDebug() : logging.warning("SCREEN IST GESPERRT! ")
		except: pass
		# self.blitSyncLyrics()

		return

# -------------------- Timer -----------------------------------------------------------------

	def updateActTime(self):

		if self.screen.get_locked() : return

		try: newPos = self.gstPlayer.queryPosition()
		except: return

		if newPos == None : return		
		if self.pos == newPos : return				

		self.pos = newPos 
		textActPos = self.textActTime.replace('%duration%', self.gstPlayer.getDuration())
		strClear = textActPos.replace('%time%', self.gstPlayer.getDuration())
		textActPos = textActPos.replace('%time%', newPos)
		
		try: 
			fontActPos = self.font.render(textActPos, True, self.fontColor)
			fontClear = self.font.render(strClear, True, self.fontColor)
		except: return

		# darüber die akutelle / Laufzeit
		# --> Größe ermitteln
		txtW, txtH = fontClear.get_size()

		w, h = self.rectActTime

		# if self.getDebug() : print "Aktuelle Position: %s " % (self.gstPlayer.queryNumericPosition())
		if self.getDiaMode() > 3 and self.gstPlayer.queryNumericPosition() > (self.timerIndex + self.diaShowTime) :
			self.diaShow()
			self.timerIndex = self.gstPlayer.queryNumericPosition()

		image = pygame.Surface([txtW, txtH])
		# Generiert ein Surface des Objektes mit der definierten Groesse
		# Siehe: Allgemeines ueber Surfaces

		image.fill(self.oConfig.getConfig('gui', self.winState, 'backgroundColor'))        
		# self.screen.blit(image, (self.txtTitleW, h))
		if not self.screen.get_locked() : self.screen.blit(image, (w, h))  
		
		# darüber die akutelle / Laufzeit
		if not self.screen.get_locked() : 
			try: self.screen.blit(fontActPos, (w, h)) 
			except pygame.error, err: 
				logging.warning(\
					"dacapo: Error at self.screen.blit(textActPos, (%s, %s)) in function updateActTime(). %s " % (w, h, err))
				self.doQuit()
		if not self.screen.get_locked() : 
			self.screen.lock()
			try: pygame.display.update((w, h, txtW, txtH))
			# try: pygame.display.flip()
			except pygame.error, err: 
				logging.error(\
					"Error at pygame.display.update((%s, %s, %s, %s)) in function updateActTime(). %s " % (w, h, txtW, txtH, err))
				logging.error(\
					"   --> vorher: self.screen.blit(textActPos, (%s, %s)) in function updateActTime()." % (w, h))
				self.doQuit()
			self.screen.unlock()

		del image

		return




# -------------------- Timer -----------------------------------------------------------------

# -------------------- Sync-Texte -----------------------------------------------------------------

	def updateSyncLyrics(self):
		if len(self.audioFile.syncText) <= 0 : return
		if self.audioFile.syncCount >= len(self.audioFile.syncText) : return
		if self.audioFile.filename <> self.gstPlayer.actualTitel : return
		if self.gstPlayer.queryPositionInMilliseconds() >= self.audioFile.syncTime[self.audioFile.syncCount] :
			self.blitSyncLyrics(nextLine=True)
			if self.audioFile.syncCount < (len(self.audioFile.syncText) ) :
				self.audioFile.syncCount += 1
		return

	def blitSyncLyrics(self, nextLine=False):
		# keine Texte = Abbruch
		if len(self.audioFile.syncText) <= 0 : return
		# List-Index > Anzahl Text-Zeilen = Abbruch
		if self.audioFile.syncCount > len(self.audioFile.syncText) : return
		if self.getDebug() : logging.debug("Soll Text darstellen: %s" % \
			(self.audioFile.syncText[self.audioFile.syncCount]))
		width, height = self.resolution
		h = self.fontHeight 
		if self.oConfig.getConfig('gui', 'syncLyrics', 'position').upper()  == "BOTTOM" :
			# Fenstergröße holen (h = Fensterschriftgröße)
			h = (self.txtTitleH - self.lyricFontRealHeight )

		# versuchen, alten Text zu löschen
		if not self.fontLyrics == None:
			txtW, txtH = self.fontLyrics.get_size()
			image = pygame.Surface([txtW, txtH])
			image.fill(self.oConfig.getConfig('gui', self.winState, 'backgroundColor'))        
			if not self.screen.get_locked() : 
				w = self.lastSyncLyricW
				self.screen.blit(image, (w, h)) 
				self.screen.lock()
				try: pygame.display.update((w, h, txtW, txtH))
				except pygame.error, err: 
					logging.error(\
						"Error at pygame.display.update((%s, %s, %s, %s)) in function updateActTime(). %s " % (w, h, txtW, txtH, err))
				self.screen.unlock() 
		# Nur die nächste Zeile rendern, wenn Zeit gekommen ist...
		if nextLine: 
			self.fontLyrics = self.lyricFont.render(self.audioFile.syncText[self.audioFile.syncCount], True, self.lyricFontColor)
		if not self.fontLyrics == None:
			txtW, txtH = self.fontLyrics.get_size()
			w = 0
			if self.oConfig.getConfig('gui', 'syncLyrics', 'style').upper()  == "CENTER" :
				w = (width - txtW) / 2
			if self.oConfig.getConfig('gui', 'syncLyrics', 'style').upper()  == "RIGHT" :
				w = (width - txtW)

			try: 
				image = pygame.Surface([txtW, txtH])
				image.fill(self.oConfig.getConfig('gui', self.winState, 'backgroundColor'))     
				self.screen.blit(image, (w, h))   
				self.screen.blit(self.fontLyrics, (w, h)) 
			except pygame.error, err: 
				logging.error("konnte Sync-Text nicht darstellen: %s" % (self.audioFile.syncText[self.audioFile.syncCount]))
				logging.error(\
					"Error at self.screen.blit(self.lyricFont, (%s, %s)) " % (w, h))
				logging.error(err)
			if not self.screen.get_locked() : 
				self.screen.lock()
				try: pygame.display.update((w, h, txtW, txtH))
				except pygame.error, err: 
					logging.error(\
						"Error at pygame.display.update((%s, %s, %s, %s)) in function updateActTime(). %s " % (w, h, txtW, txtH, err))
				self.screen.unlock()
			self.lastSyncLyricW = w
		return


# -------------------- Sync-Texte -----------------------------------------------------------------

	def run(self):
		while True:
			# Verhindert, dass das Programm zu schnell laeuft
			self.clock.tick(10)
			# pygame.event.wait()
			# if self.getDebug() : print "playerGUI - run() -> frage Status ab "
			if self.ausschalter.isSet(): break			
			
			if self.ShowGUI == True : self.updateSyncLyrics()
			if self.ShowGUI == True : self.updateActTime()
			
			for event in pygame.event.get():
				# print "--> bin in event_loop mit event ", event
				if event.type == pygame.QUIT:
					self.doQuit()
				if event.type == pygame.ACTIVEEVENT :
					if self.allwaysOnTop :
						if not self.fullscreen : 
							if self.getDebug() : logging.debug('Setze Fenster nach vorne. ')
							self.SetWindowPos(pygame.display.get_wm_info()['window'], 
								-1, 0, 0, self.resolution[0], self.resolution[1], 0x0013)
				elif event.type==VIDEORESIZE:
					# get actual size
					screen=pygame.display.set_mode(event.dict['size'],pygame.RESIZABLE)
					self.resolution = event.dict['size']
					fontSize = self.calculateNewFontSize()
					# set new fontsize
					self.font = pygame.font.SysFont(self.oConfig.getConfig('gui', self.winState, 'font'), fontSize)			
					self.blitText()
					
				elif event.type == pygame.KEYDOWN:
					# if self.getDebug() : print "--> bin in event_loop mit event ", event
					if event.key == pygame.K_ESCAPE:
						self.doQuit()
					if event.key == pygame.K_q:
						self.doQuit()
					if event.key == pygame.K_SPACE:
						self.start_stop()
					if event.key == pygame.K_f:
						self.doFullscreen()
					if event.key == pygame.K_LEFT:
						self.gstPlayer.seekPosition(float(-10))
						self.audioFile.syncCount = 0
						self.timerIndex = self.gstPlayer.queryNumericPosition()
					if event.key == pygame.K_RIGHT:
						self.gstPlayer.seekPosition(float(+10))
						self.timerIndex = self.gstPlayer.queryNumericPosition()
					# if event.key == pygame.K_LSHIFT and event.key == pygame.K_LEFT:
					#	self.gstPlayer.seekPosition(float(-30))
					# if event.key == pygame.K_RSHIFT and event.key == pygame.K_RIGHT:
					#	self.gstPlayer.seekPosition(float(+30))
					if event.key == pygame.K_DOWN:
						self.playPrevSong()
					if event.key == pygame.K_UP:
						self.playNextSong()
					if event.key == pygame.K_LESS:
						self.playPrevSong()
					if event.key == pygame.K_GREATER:
						self.playNextSong()
					if event.key == pygame.K_HOME:
						self.playFirstSong()
					if event.key == pygame.K_END:
						self.playLastSong()
				else :
					# if self.getDebug() : logging.debug("--> bin in event_loop mit event " + event + '')
					pass
				
		return


	def calculateNewFontSize(self):
		# get Rect-Size for Window
		windowWidth = self.oConfig.getConfig('gui', 'window', 'width')
		# get Rect-Size for Fullscreen
		fullscreenWidth = self.oConfig.getConfig('gui', 'fullscreen', 'width')
		# is actual Windowsize < init Window?
		if self.resolution[0] < windowWidth :
			proz = ((self.resolution[0]  * 100) / windowWidth)
			initFontSize = self.oConfig.getConfig('gui', 'window', 'fontSize')
		else :
			proz = ((self.resolution[0]  * 100) / fullscreenWidth)
			initFontSize = self.oConfig.getConfig('gui', 'fullscreen', 'fontSize')
		# new Fontsize
		fontSize = (initFontSize * proz) / 100
		logging.debug("O-Fontsize: %s -> Neue fontSize: %s - proz: %s" % (initFontSize, fontSize, proz))
		return fontSize

# -------------------- doFullscreen -----------------------------------------------------------------



	def doFullscreen(self):
		if self.fullscreen == True:
			self.fullscreen = False
		else:
			self.fullscreen = True
		self.winState = 'window'
		if self.fullscreen : self.winState = 'fullscreen'
		self.doInitDisplay()
		self.resize = True
		self.__lastWidthPos = None
		self.blitText()
		if self.getDiaMode() > 3 : self.diaShow()
		return

	def start_stop(self):
		if self.getDebug() : logging.debug('--> Status: {0} '.format(self.status ))
		if self.status == "Start":
			self.status = "Stop"
			self.gstPlayer.doUnpause()
		else:
			self.gstPlayer.doPause()
			self.status = "Start"
		return

	def playPrevSong(self):
		if self.actSong > 1:
			self.actSong -= 2
			self.playNextSong()
		return

	def playFirstSong(self):
		self.actSong = 0
		self.playNextSong()
		return

	def playLastSong(self):
		self.actSong = len(self.playlist) - 1
		self.playNextSong()
		return


# -------------------- playNextSong() -----------------------------------------------------------------



	def playNextSong(self, GAPLESS=False):
		if len(self.playlist) <= 0: self.doQuit()
		while self.actSong < len(self.playlist):
			self.filename=self.playlist[self.actSong]
			if self.getDebug() : logging.debug('Versuche folgenden Song zu spielen: {0}'.format(self.filename))
			datei = open(LIST_NAME, "w")
			datei.write(str(self.actSong))
			datei.close()
			self.fontLyrics = None
			self.actSong += 1
			
			#if os.path.isfile(self.filename):
			if mimehelp.isInMimeTypes(self.filename) :
				if self.ShowGUI == True :
					if self.getDebug() : logging.info('Versuche Metadaten zu laden ')
					self.audioFile = getAudioFile(self, self.filename)
					if self.getDebug() : 
						antwort = "Ja"
						if self.audioFile == None :
							antwort = "Nein"
						logging.info('Metadaten geladen? %s' % (antwort)  )
					if self.audioFile <> None :
						# if self.getDebug() : print 'Hole Cover: {0}'.format(self.filename)
						# self.pic = self.audioFile.getCover()
						if self.getDebug() : logging.info('Starte GStreamer: {0} '.format(self.filename))
						if GAPLESS : self.gstPlayer.doGaplessPlay(self.filename)	
						else : self.gstPlayer.doPlay(self.filename)	
						if self.getDebug() : logging.debug('Bereite Texte auf: {0} '.format(self.filename))
						self.blitText()
						if self.getDebug() : logging.debug('Alles super: {0} '.format(self.filename))
						break
					else:
						print  >> sys.stderr, "Fehler bei Nummer: ", self.actSong, " Titel: ", self.filename
						logging.error('Fehler bei Nummer: %s Titel: %s ' % (self.actSong, self.filename))
						if self.actSong >= len(self.playlist): self.doQuit()
				else :
					if self.getDebug() : logging.info('Starte GStreamer: {0} '.format(self.filename))
					if GAPLESS : self.gstPlayer.doGaplessPlay(self.filename)	
					else : self.gstPlayer.doPlay(self.filename)	
			

		if self.actSong > len(self.playlist):
			self.gstPlayer.doStop()
		return



# -------------------- doInitDisplay() -----------------------------------------------------------------


	def doInitDisplay(self):
		self.allwaysOnTop = False
		if platform.system() == 'Windows': 
			self.SetWindowPos = windll.user32.SetWindowPos
			self.allwaysOnTop = self.oConfig.getConfig('gui', 'window', 'allwaysOnTop')
		if self.getDebug() : logging.debug('Initialisiere Display ')
		try : pygame.display.init()
		except : 
			logging.error('Konnte Display nicht initialisieren! ')
			logging.error(pygame.get_error())
		if self.getDebug() : logging.debug('setze Ueberschrift ')
		try : pygame.display.set_caption(self.oConfig.getConfig('gui', 'misc', 'caption')) 
		except : 
			logging.error('Konnte Ueberschrift nicht setzen! ')
			logging.error(pygame.get_error())
		
		if self.getDebug() : logging.debug('setze Icon ')
		iconfile = TITLE_ICO = CONFIG_DIR + self.oConfig.getConfig('gui', 'misc', 'icon')
		w = self.oConfig.getConfig('gui', 'misc', 'iconsize')
		h = self.oConfig.getConfig('gui', 'misc', 'iconsize')
		icon = pygame.transform.scale(pygame.image.load(iconfile), (w, h))	
		try : pygame.display.set_icon(icon)
		except : 
			logging.warning('Konnte Icon nicht setzen! ')
			logging.warning(pygame.get_error())
		if self.getDebug() : logging.debug('hole Konfiguration ')
		self.resolution = (self.oConfig.getConfig('gui', self.winState, 'width'), self.oConfig.getConfig('gui', self.winState, 'height'))
		if self.getDebug() : logging.debug('Setze angeforderten Modus. ')
		try:
			if self.fullscreen : self.screen  = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN) 
			else : 
				self.screen  = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)	
				if self.allwaysOnTop :
					if self.getDebug() : logging.debug('Setze Fenster nach vorne. ')
					# self.SetWindowPos(pygame.display.get_wm_info()['window'], -2, x, y, 0, 0, 0x0001)
					self.SetWindowPos(pygame.display.get_wm_info()['window'], 
						-1, 0, 0, self.resolution[0], self.resolution[1], 0x0013)
		except: 
			if self.error() : logging.debug('Schiefgegangen!!! ')
			logging.error(pygame.get_error())
		if self.getDebug() : logging.debug('Font initialisieren. ')
		self.font = pygame.font.SysFont(self.oConfig.getConfig('gui', self.winState, 'font'), self.oConfig.getConfig('gui', self.winState, 'fontSize'))
		if self.getDebug() : logging.debug('Fontcolor initialisieren. ')
		self.fontColor = self.oConfig.getConfig('gui', self.winState, 'fontColor')
		fontHeightFont = self.font.render("AAA", True, self.fontColor)
		self.fontWidth, self.fontHeight = fontHeightFont.get_size()
		self.showLyricsAsPics = self.oConfig.getConfig('gui', 'misc', 'showLyricsAsPics')
		if self.getDebug() : logging.debug('LyricFont initialisieren. ')
		self.lyricFont = pygame.font.SysFont(self.oConfig.getConfig('gui', self.winState, 'lyricFont'), self.oConfig.getConfig('gui', self.winState, 'lyricFontSize'))
		if self.getDebug() : logging.debug('LyricFontColor initialisieren. ')
		self.lyricFontColor = self.oConfig.getConfig('gui', self.winState, 'lyricFontColor')
		fontHeightFont = self.lyricFont.render("AAA", True, self.lyricFontColor)
		self.lyricFontWidth, self.lyricFontHeight = fontHeightFont.get_size()
		self.lyricFontRealHeight = self.lyricFontHeight 
		self.lyricFontHeight += self.oConfig.getConfig('gui', self.winState, 'lyricFontSpace')
		

		if self.getDebug() : logging.debug('Mouse verstecken. ')
		try : pygame.mouse.set_visible(self.oConfig.getConfig('gui', self.winState, 'mouseVisible'))
		except : 
			logging.warning('Konnte Mouse nicht verstecken! ')
			logging.warning(pygame.get_error())

		self.diaShowTime = self.oConfig.getConfig('gui', 'misc', 'diaShowTime')

		return

# -------------------- doQuit() -----------------------------------------------------------------


	def doQuit(self):
		if self.getDebug() : logging.debug("aufraeumen und beenden... ")
		if self.getDebug() : logging.debug("Ausschalter setzen... ")
		self.ausschalter.set()
		if self.getDebug() : logging.debug("gstPlayer stoppen... ")
		self.gstPlayer.doStop()
		if self.getDebug() : logging.debug("gstPlayer beenden... ")
		self.gstPlayer.doEnd()
		del self.gstPlayer
		if self.getDebug() : logging.debug("audioFile beenden... ")
		try : del self.audioFile
		except : pass
		if self.getDebug() : logging.debug("pygame beenden... ")
		pygame.quit()
		if self.getDebug() : logging.debug("Hauptschalter setzen... ")
		self.hauptschalter.set()
		raise SystemExit
		if self.getDebug() : logging.debug("Feierabend... ")
		self.logFile.close()		
		readconfig.quit()
		return



	def setReplayGain(self, bRG):
		self.bRG = bRG
		return

	def getReplayGain(self):
		return self.bRG
	
	def setDebug(self, bDebug):
		self.bDebug = bDebug
		return

	def getDebug(self):
		return self.bDebug

	def setGSDebug(self, bGSDebug):
		self.bGSDebug = bGSDebug
		return

	def getGSDebug(self):
		return self.bGSDebug

	def setDiaMode(self, sDiaMode):
		self.__sDiaMode = SHOWPIC_CHOICES.index(sDiaMode)
		return

	def getDiaMode(self):
		return self.__sDiaMode

	def setLastRect(self, w, h, picW, picH):
		self.__lastWidthPos = w
		self.__lastHeightPos = h
		self.__lastPicWidth = picW
		self.__lastPicHeight = picH
		if self.getDebug() : logging.info("w: %s, h: %s, picW: %s, picH: %s" % (w, h, picW, picH))
		return

	def clearLastRect(self):
		if self.__lastWidthPos == None : return

		w = self.__lastWidthPos 
		h = self.__lastHeightPos 
		picW = self.__lastPicWidth
		picH = self.__lastPicHeight 
		if self.getDebug() : logging.info("w: %s, h: %s, picW: %s, picH: %s" % (w, h, picW, picH))

		image = pygame.Surface([picW, picH])
		image.fill(self.oConfig.getConfig('gui', self.winState, 'backgroundColor'))        
		if not self.screen.get_locked() : self.screen.blit(image, (w, h))  
		if not self.screen.get_locked() :
			self.screen.lock()
			try: pygame.display.update((w, h, picW, picH))
			except pygame.error, err: logging.error("dacapo: Error at pygame.display.update(). %s " % (err))
			self.screen.unlock()
		return



