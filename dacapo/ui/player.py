#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ##############################################################################
#! /usr/bin/python
# ##############################################################################
# small GTK/GStreamer Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
# ##############################################################################

'''
	this module handles the pygame-GUI and from here the
	playlist, the GStreamer-module as well as the metadata.
	one could say, it is the core of the dacapo.
'''

import sys
import os
import platform
from dacapo import errorhandling
from types import *

if platform.system() == 'Windows':
	try:
		from ctypes import windll
	except ImportError, err:
		errorhandling.Error.show()
		sys.exit(2)
# os.environ['SDL_VIDEODRIVER'] = 'directx'
try:
	from pygame.locals import *
	import pygame
	import operator
	from dacapo.ui import renderfonts
	from dacapo.metadata import *
	from dacapo.dacapoGST import GstPlayer
	from dacapo.config import readconfig
	from dacapo.dacapoHelp import SHOWPIC_CHOICES
	from dacapo.config.gui import *
	import logging
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #

HOMEDIR = os.path.expanduser('~')
CONFIG_DIR = HOMEDIR + '/.dacapo/'
LIST_NAME = CONFIG_DIR + 'lastPlaylistNumber.tmp'


# ----------- Klassendefinitionen ----------------------------- #


class playerGUI(dacapo.ui.interface_blitobject.BlitInterface):
	def __init__(self, ausschalter, hauptschalter):
		super(playerGUI, self).__init__()
		self._ausschalter = ausschalter
		self._hauptschalter = hauptschalter
		pygame.init()
		pygame.key.set_repeat(1, 1)
		# Legt fest, wie oft Tastendruecke automatisch wiederholt werden
		# Das erste Argument gibt an ab wann, das zweite in welchen
		# Intervallen der Tastendruck wiederholt wird
		# self._config = readconfig.getConfigObject()
		self._config = readconfig.getConfigObject()
		self._config.setConfig('TEMP', Key='PLAYER', Value=self)
		self._showGUI = bool(self._config.getConfig('TEMP', Key='SHOWGUI'))
		bResume = self._config.getConfig('TEMP', Key='RESUME')
		# Erstellt einen Zeitnehmer
		self._debug = self._config.getConfig('debug', ' ', 'debugGUI')
		self._gapless = self._config.getConfig('audio_engine', 'audio_engine', 'gapless')
		self._resize = False

		self.replayGain = self._config.getConfig('audio_engine', 'audio_engine', 'replayGain')
		self.set_slide_mode(self._config.getConfig('gui', 'misc', 'showPics'))

		# gstPlayer wird als GTK-thread gestartet
		if self._debug: logging.debug( \
			'versuche GstPlayer zu starten...')
		self._gstPlayer = GstPlayer(ausschalter)
		self._gstPlayer.start()
		if self._debug: logging.debug( \
			'versuche GstPlayer zu starten... done.')
		oPlaylist = self._config.getConfig(
			'TEMP', Key='PLAYLIST')
		self.isPlaylist = oPlaylist.isPlaylist()
		self.playlist = oPlaylist.getPlaylist()
		self.actSong = 0
		if bResume:
			datei = open(LIST_NAME, "r")
			self.actSong = int(datei.read())
			datei.close()
		self.pos = "0"
		self.status = "Stop"
		self.fullscreen = self._config.getConfig('TEMP', Key='FULLSCREEN')
		self.winState = 'window'
		if self.fullscreen: self.winState = 'fullscreen'

		self.init_display()
		self.play_next_song()
		return

	# -------------------- Texte anzeigen ----------------------------------------

	def display_text(self):
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
		self._actScreen = None
		try:
			g = CONFIG.gui[self.winState]
			print("going to fill the background to: {!s}".format(g.backgroundColor))
			try: self.doFillBackground(self.screen, g.backgroundColor, True)
			except:
				print(pygame.get_error())
				return
			print("going to get blit object... ")
			obj = self.getBlitObject()
			sorted_x = sorted(obj, key=operator.attrgetter('zIndex'))
			for o in sorted_x:
				self.doBlitObject(self.screen, o, True)
		except:
			logging.error("Error at blit-object %s " % (sys.exc_info()[0]))
			errorhandling.Error.show()


		self.timerIndex = 0

		self.diaShowPics = []
		self.diaIndex = - 1
		# der Bereich der aktuellen Position wird bereinigt
		## key1 = self._metaFields.get('TIME')['posActTime']
		## self.clearRect(self._metaFields, key1)
		self._saveScreen = self.screen.copy()
		self._actScreen = self.screen.copy()

		if not self._resize: self.timerIndex = self._gstPlayer.queryNumericPosition()
		if not self._resize:
			self.audioFile.loadPictures()
		self.diaShowPics = self.audioFile.preBlitDiaShow()
		self.slide_show()

		self._resize = False
		return

	# -------------------- slideshow ----------------------------------------------------------------

	def slide_show(self):
		return
		if self._debug: logging.debug("pygame.display.get_init = %s " % (pygame.display.get_init()))
		if self._debug: logging.debug("pygame.display.get_active = %s " % (pygame.display.get_active()))
		if self._debug: logging.debug(
			"Anzahl Bilder: %s -> aktuelles Bild: Nr %s" % (len(self.diaShowPics), self.diaIndex))
		if len(self.diaShowPics) <= 1 and self.diaIndex >= 0:
			if self._debug: logging.debug("Breche diaShow ab, da Anzahl Bilder: %s " % (len(self.diaShowPics)))
			return
		if len(self.diaShowPics) < self.diaIndex:
			if self._debug:
				logging.debug("Breche diaShow ab, da diaIndex: %s > Anzahl Bilder: %s "
							  % (self.diaIndex, len(self.diaShowPics)))
			return

		g = CONFIG.gui[self.winState]
		if (g.picField is None): return

		g.picField.replaceData(self.audioFile.syncText[self.audioFile.syncCount])
		obj = g.lyricField.getBlitObject()
		self.doBlitObject(self.screen, obj, True)
		# Fenstergröße holen
		picPlace = self._config.getConfig('gui', self.winState, 'pictures')
		width = picPlace['width']
		height = picPlace['height']
		w = picPlace['posH']
		h = picPlace['posV']
		picRect = Rect(w, h, width, height)
		wWidth, wHeight = self.resolution
		clearRect = Rect(0, 0, wWidth, wHeight)

		# delete the old picture
		if self.diaIndex > -1:
			# get the hole screen back, because on slow machines
			# the time-pos can make trouble
			tmp = self._saveScreen.subsurface(clearRect).copy()
			self.blit_rect(
				tmp,
				clearRect,
				text="clear picture area",
				update=False
			)

		# if Index bigger than number of pics -> initialize the Index
		self.diaIndex += 1
		if self.diaIndex > (len(self.diaShowPics) - 1): self.diaIndex = 0

		## -- Hier kann es passieren, dass die Liste noch nicht aufgebaut ist... deshalb evtl. Fehler abfangen!
		try:
			picW, picH = self.diaShowPics[self.diaIndex].get_size()
			# --> positionieren ---------------------------
			w += (width - picW) / 2
			h += (height - picH) / 2

			# <-- positionieren ---------------------------
			self.blit_rect(
				self.diaShowPics[self.diaIndex],
				Rect(w, h, picW, picH),
				text="slide_show Bild Nr: " + str(self.diaIndex),
				update=False
			)
			##self.blit_sync_lyrics(nextLine=False)
			self.update_overlay_text()
			## save the actual without time display
			self._actScreen = self.screen.copy()
			self.update_act_time(force=True)
			pygame.display.update(picRect)
		except:
			logging.error( \
				"Error at slide-show picture (%s). %s " % (
					self.diaIndex, sys.exc_info()[0]))

		return

	# -------------------- slideshow ----------------------------------------------------------------



	# -------------------- Timer -----------------------------------------------------------------

	def update_act_time(self, force=False):
		if self.screen.get_locked(): return

		try:
			newPos = self._gstPlayer.queryPosition()
		except:
			return

		if newPos == None: return

		if (self.pos == newPos) and (force == False): return

		g = CONFIG.gui[self.winState]
		if (g.timeField is None): return
		g.timeField.getRenderedData()
		obj = g.timeField.getBlitObject()
		self.doBlitObject(self.screen, obj, True)
		return
		## if self._metaFields.get('TIME')['textActTime'] == None: return

		# if self._debug : print "Aktuelle Position: %s " % (self._gstPlayer.queryNumericPosition())
		if self._gstPlayer.queryNumericPosition() > (self.timerIndex + self.diaShowTime):
			if not force:
				self.slide_show()
			self.timerIndex = self._gstPlayer.queryNumericPosition()

		key1 = self._metaFields.get('TIME')['posActTime']
		self.clearUpdateRect(self._metaFields, key1)

		self.pos = newPos
		## self._metaFields = self.metaFontsObject.getRenderedActTime()
		try:
			self.blit_rect(
				self._metaFields.get(key1)['renderedData'],
				Rect(
					self._metaFields.get(key1)['blitPos'],
					self._metaFields.get(key1)['renderedSize']
				),
				text=self._metaFields.get(key1)['data'],
				update=True
			)
		except:
			pass

		return


	# -------------------- Timer -----------------------------------------------------------------

	# -------------------- Sync-Texte -----------------------------------------------------------------

	def update_sync_lyrics(self):
		if len(self.audioFile.syncText) <= 0: return
		if self.audioFile.syncCount >= len(self.audioFile.syncText): return
		if self.audioFile.filename <> self._gstPlayer.actualTitel: return
		if self._gstPlayer.queryPositionInMilliseconds() >= self.audioFile.syncTime[self.audioFile.syncCount]:
			self.blit_sync_lyrics(nextLine=True)
			if self.audioFile.syncCount < (len(self.audioFile.syncText) ):
				self.audioFile.syncCount += 1
		return

	def blit_sync_lyrics(self, nextLine=False):
		if len(self.audioFile.syncText) <= 0: return
		if self.audioFile.syncCount > len(self.audioFile.syncText): return
		g = CONFIG.gui[self.winState]
		if (g.lyricField is None): return

		g.lyricField.replaceData(self.audioFile.syncText[self.audioFile.syncCount])
		obj = g.lyricField.getBlitObject()
		self.doBlitObject(self.screen, obj, True)
		return


	# -------------------- Sync-Texte -----------------------------------------------------------------

	def run(self):
		# Verhindert, dass das Programm zu schnell laeuft
		FPS = 30
		fpsClock = pygame.time.Clock()
		if self._debug: logging.debug("going to loop...")
		while True:
			try:
				if self._ausschalter.isSet(): break

				if self._showGUI == True: self.update_sync_lyrics()
				if self._showGUI == True: self.update_act_time()

				for event in pygame.event.get():
					# if self._debug : logging.debug("--> bin in event_loop mit event: %s " % (event))
					if event.type == pygame.QUIT:
						self.quit()
					if event.type == pygame.ACTIVEEVENT:
						if self.allwaysOnTop:
							if not self.fullscreen:
								if self._debug: logging.debug('Setze Fenster nach vorne. ')
								self.SetWindowPos(pygame.display.get_wm_info()['window'],
												  -1, 0, 0, self.resolution[0], self.resolution[1], 0x0013)
					elif event.type == VIDEORESIZE:
						# get actual size
						screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
						self.resolution = event.dict['size']
					# self.doBlitText()

					elif event.type == pygame.KEYDOWN:
						if self._debug: logging.debug("Keydown-Event: %s" % (event.key))
						if event.key == pygame.K_ESCAPE:
							self.quit()
						if event.key == pygame.K_q:
							self.quit()
						if event.key == pygame.K_SPACE:
							self.start_stop()
						if event.key == pygame.K_f:
							self.toggle_fullscreen()
						if event.key == pygame.K_LEFT:
							self._gstPlayer.seekPosition(self.seekSecs * float(-1))
							self.audioFile.syncCount = 0
							self.timerIndex = self._gstPlayer.queryNumericPosition()
						if event.key == pygame.K_RIGHT:
							self._gstPlayer.seekPosition(self.seekSecs)
							self.timerIndex = self._gstPlayer.queryNumericPosition()
						# if event.key == pygame.K_LSHIFT and event.key == pygame.K_LEFT:
						#	self._gstPlayer.seekPosition(float(-30))
						# if event.key == pygame.K_RSHIFT and event.key == pygame.K_RIGHT:
						#	self._gstPlayer.seekPosition(float(+30))
						if event.key == pygame.K_DOWN:
							self.play_prev_song()
						if event.key == pygame.K_UP:
							self.play_next_song()
						if event.key == pygame.K_LESS:
							self.play_prev_song()
						if event.key == pygame.K_GREATER:
							self.play_next_song()
						if event.key == pygame.K_HOME:
							self.play_first_song()
						if event.key == pygame.K_END:
							self.play_last_song()
					else:
						# if self._debug : logging.debug("--> bin in event_loop mit event " + event + '')
						pass
				fpsClock.tick(FPS)
			except Exception, err:
				errorhandling.Error.show()
				sys.exit(2)
		return


	# -------------------- doFullscreen -----------------------------------------------------------------



	def toggle_fullscreen(self):
		if self.fullscreen == True:
			self.fullscreen = False
			if self._debug: logging.debug('Going to window-mode')
		else:
			self.fullscreen = True
			if self._debug: logging.debug('Going to fullscreen-mode')
		self.winState = 'window'
		if self.fullscreen: self.winState = 'fullscreen'
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.winState)
		self.init_display()
		self._resize = True
		self.__lastWidthPos = None
		self.display_text()
		return

	def start_stop(self):
		if self._debug: logging.debug('--> Status: {0} '.format(self.status))
		if self.status == "Start":
			self.status = "Stop"
			self._gstPlayer.doUnpause()
		else:
			self._gstPlayer.doPause()
			self.status = "Start"
		return

	def play_prev_song(self):
		if self.actSong > 1:
			self.actSong -= 2
			self.play_next_song()
		return

	def play_first_song(self):
		self.actSong = 0
		self.play_next_song()
		return

	def play_last_song(self):
		self.actSong = len(self.playlist) - 1
		self.play_next_song()
		return


	# -------------------- playNextSong() -----------------------------------------------------------------



	def play_next_song(self, GAPLESS=False):
		if len(self.playlist) <= 0: self.quit()
		while self.actSong < len(self.playlist):
			self.filename = self.playlist[self.actSong]
			if self._debug: logging.debug('Versuche folgenden Song zu spielen: {0}'.format(self.filename))
			datei = open(LIST_NAME, "w")
			datei.write(str(self.actSong))
			datei.close()
			self.fontLyrics = None
			self.actSong += 1

			#if os.path.isfile(self.filename):
			if mimehelp.isInMimeTypes(self.filename):
				self._config.setConfig('TEMP', Key='FILENAME', Value=self.filename)
				if self._showGUI == True:
					if self._debug: logging.info('Versuche Metadaten zu laden ')
					self.audioFile = getAudioFile(self.filename)
					self._config.setConfig('TEMP', Key='AUDIOFILE', Value=self.audioFile)
					if self._debug:
						antwort = "Ja"
						if self.audioFile == None:
							antwort = "Nein"
						logging.info('Metadaten geladen? %s' % (antwort))
					if self.audioFile <> None:
						# if self._debug : print 'Hole Cover: {0}'.format(self.filename)
						# self.pic = self.audioFile.getCover()
						if self._debug: logging.info('Starte GStreamer: {0} '.format(self.filename))
						if GAPLESS:
							self._gstPlayer.doGaplessPlay(self.filename)
						else:
							self._gstPlayer.doPlay(self.filename)
						if self._debug: logging.debug('Bereite Texte auf: {0} '.format(self.filename))
						self.display_text()
						if self._debug: logging.debug('Alles super: {0} '.format(self.filename))
						break
					else:
						print  >> sys.stderr, "Fehler bei Nummer: ", self.actSong, " Titel: ", self.filename
						logging.error('Fehler bei Nummer: %s Titel: %s ' % (self.actSong, self.filename))
						if self.actSong >= len(self.playlist): self.quit()
				else:
					if self._debug: logging.info('Starte GStreamer: {0} '.format(self.filename))
					if GAPLESS:
						self._gstPlayer.doGaplessPlay(self.filename)
					else:
						self._gstPlayer.doPlay(self.filename)

		if self.actSong > len(self.playlist):
			self._gstPlayer.doStop()
		if self._debug: logging.debug('done play next song. ')
		return


	# -------------------- doInitDisplay() -----------------------------------------------------------------


	def init_display(self):
		try:
			pygame.display.quit()
		except:
			logging.error('Could not quit pygame.display! ')
			logging.error(pygame.get_error())
		self._config.setConfig('TEMP', 'gui', 'winState', self.winState)
		self.allwaysOnTop = False
		if platform.system() == 'Windows':
			self.SetWindowPos = windll.user32.SetWindowPos
			self.allwaysOnTop = self._config.getConfig('gui', 'window', 'allwaysOnTop')
		if self._debug: logging.debug('Initialisiere Display ')
		try:
			pygame.display.init()
			if (not pygame.font.get_init()):
				pygame.font.init()
		except:
			logging.error('Konnte Display nicht initialisieren! ')
			logging.error(pygame.get_error())
			self.quit()
		if self._debug: logging.debug('setze Ueberschrift ')
		try:
			pygame.display.set_caption(self._config.getConfig('gui', 'misc', 'caption'))
		except:
			logging.error('Konnte Ueberschrift nicht setzen! ')
			logging.error(pygame.get_error())

		if self._debug: logging.debug('setze Icon ')
		iconfile = CONFIG_DIR + self._config.getConfig('gui', 'misc', 'icon')
		w = self._config.getConfig('gui', 'misc', 'iconsize')
		h = self._config.getConfig('gui', 'misc', 'iconsize')

		try:
			icon = pygame.transform.scale(pygame.image.load(iconfile), (w, h))
			pygame.display.set_icon(icon)
		except:
			logging.warning('Konnte Icon nicht setzen! ')
			logging.warning(pygame.get_error())
		if self._debug: logging.debug('hole Konfiguration ')
		self.resolution = (
			self._config.getConfig('gui', self.winState, 'width'),
			self._config.getConfig('gui', self.winState, 'height'))

		logging.debug(u'Angeforderte Größe: %s x %s' %
					  (self.resolution[0], self.resolution[1]))
		try:
			if self.fullscreen:
				if self._debug:
					logging.debug("Verfügbare Modi: %s " % (pygame.display.list_modes(0, pygame.FULLSCREEN)))
					logging.debug('Setze angeforderten Modus: %s x %s %s' %
								  (self.resolution[0], self.resolution[1], pygame.FULLSCREEN ))
				self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
			else:
				if self._debug:
					logging.debug('Setze angeforderten Modus: %s x %s %s' %
								  (self.resolution[0], self.resolution[1], pygame.RESIZABLE ))
				self.screen = pygame.display.set_mode(self.resolution)
				if self.allwaysOnTop:
					if self._debug: logging.debug('Setze Fenster nach vorne. ')
					# self.SetWindowPos(pygame.display.get_wm_info()['window'], -2, x, y, 0, 0, 0x0001)
					self.SetWindowPos(pygame.display.get_wm_info()['window'],
									  -1, 0, 0, self.resolution[0], self.resolution[1], 0x0013)
		except:
			logging.error('SCHWERER FEHLER BEIM DISPLAY INITIALISIEREN!!! ')
			logging.error(pygame.get_error())
			errorhandling.Error.show()
			self.quit()

		self.showLyricsAsPics = self._config.getConfig('gui', 'misc', 'showLyricsAsPics')
		self.seekSecs = self._config.getConfig('gui', 'misc', 'seekSeconds')
		if self._debug: logging.debug('Anzahl Sekunden für FFW/FBW: %s' % (self.seekSecs))

		if self._debug: logging.debug('Mouse verstecken. ')
		try:
			pygame.mouse.set_visible(self._config.getConfig('gui', self.winState, 'mouseVisible'))
		except:
			logging.warning('Konnte Mouse nicht verstecken! ')
			logging.warning(pygame.get_error())

		self.diaShowTime = self._config.getConfig('gui', 'misc', 'diaShowTime')
		# if self._debug : logging.debug("has focus?: %s " % (pygame.key.get_focused()))
		if self._debug: logging.debug("DISPLAY DRIVER: %s " % (pygame.display.get_driver()))
		if self._debug: logging.debug("DISPLAY INFO: %s " % (pygame.display.Info()))
		if self._debug: logging.debug("WM INFO: %s " % (pygame.display.get_wm_info()))
		if self._debug: logging.debug('done init display. ')
		return

	# -------------------- doQuit() -----------------------------------------------------------------


	def quit(self):
		if self._debug: logging.debug("aufraeumen und beenden... ")
		if self._debug: logging.debug("Ausschalter setzen... ")
		self._ausschalter.set()
		if self._debug: logging.debug("gstPlayer stoppen... ")
		self._gstPlayer.doStop()
		if self._debug: logging.debug("gstPlayer beenden... ")
		self._gstPlayer.doEnd()
		del self._gstPlayer
		if self._debug: logging.debug("audioFile beenden... ")
		try:
			del self.audioFile
		except:
			pass
		if self._debug: logging.debug("pygame beenden... ")
		pygame.quit()
		if self._debug: logging.debug("Hauptschalter setzen... ")
		self._hauptschalter.set()
		if self._debug: logging.debug("Feierabend... ")
		readconfig.quit()
		raise SystemExit
		return

	@property
	def gstPlayer(self):
		return self._gstPlayer

	@property
	def resize(self):
		return self._resize

	@property
	def slide_mode(self):
		return self._slide_mode

	#@diaMode.setter
	def set_slide_mode(self, sDiaMode):
		self._slide_mode = SHOWPIC_CHOICES.index(sDiaMode)
		return

	@property
	def replayGain(self):
		return self._replayGain

	@replayGain.setter
	def replayGain(self, bRG):
		self._replayGain = bRG
		return


	def getActSong(self):
		return self.actSong

	def getNumberOfSongs(self):
		return len(self.playlist)


	def clearRect(self, array, key):
		if not isinstance(array, dict): return
		if not array.has_key(key): return
		if not isinstance(array.get(key), dict): return
		if not array.get(key).has_key('blitPos'): return

		image = pygame.Surface(array.get(key)['renderedSize'])
		image.fill(self._config.getConfig('gui', self.winState, 'backgroundColor'))

		text = ''
		if array.get(key).has_key('data'):
			text = array.get(key)['data']
			if isinstance(array.get(key)['data'], list):
				text = ' '.join(array.get(key)['data'])

		try:
			self.blit_rect(
				image,
				Rect(
					array.get(key)['blitPos'],
					array.get(key)['renderedSize']
				),
				text="clear_rect: " + text,
				update=True
			)
		except:
			pass
		return

	def clearUpdateRect(self, array, key):
		if self._actScreen == None:
			return self.clearRect(array, key)
		if not isinstance(array, dict): return
		if not array.has_key(key): return
		if not isinstance(array.get(key), dict): return
		if not array.get(key).has_key('blitPos'): return

		picRect = Rect(
			array.get(key)['blitPos'],
			array.get(key)['renderedSize']
		)
		tmp = self._actScreen.subsurface(picRect).copy()

		text = ''
		if array.get(key).has_key('data'):
			text = array.get(key)['data']
			if isinstance(array.get(key)['data'], list):
				text = ' '.join(array.get(key)['data'])

		try:
			self.blit_rect(
				tmp,
				picRect,
				text="clear picture area",
				update=False
			)
		except:
			pass
		return

	def getBlitObject( self ):
		audio = self.audioFile
		if audio is None:
			return None
		else:
			a = list()
			CONFIG.readConfig()
			g = CONFIG.gui[self.winState]
			g.initFields()
			for field in g.fields:
				if not g.fields[field].isPicField:
					a.append(g.fields[field].getBlitObject())
			a.append(audio.getCover())
			return a


