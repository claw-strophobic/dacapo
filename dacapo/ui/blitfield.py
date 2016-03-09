#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import dacapo.ui.field
import dacapo.ui.interface_blitobject
import dacapo.ui.blitobject
import dacapo.config.gui
import pygame

CONFIG = dacapo.config.gui.CONFIG

class BlitField(dacapo.ui.field.Field, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, name):
		super(BlitField, self).__init__(name)
		self.data = None
		self.renderedData = None
		self.renderedSize = None
		self.sysFont = None
		self._debug = True

	def getReplacedContent(self):
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		if audio is None:
			return ''
		s = self.content
		s = audio.replaceTags(s)
		return s

	def getRenderedData(self):
		"""
		In dieser Funktion werden die metadata in die Variablen
		gelesen und anhand der parametresierten Werte gerendert.
		In doBlitText werden diese dann weiter verarbeitet.
		Zurückgegeben wird ein Dictionary mit den Keys:
			- Feldname
				- ['data'] -> die aufbereiteten Daten
				- ['renderedData'] -> die gerenderten Daten
		"""
		# metadata holen und aufbereiten
		if (self.sysFont is None):
			if (not pygame.font.get_init()):
				pygame.font.init()
			try: self.sysFont = pygame.font.SysFont(self.font.fontName, self.font.fontSize)
			except pygame.error, err:
				print(u"Error at pygame.font.SysFont(%s, %s) . %s " % (
						self.font.fontName, self.font.fontSize, err))
				return None

		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		player = CONFIG.getConfig('TEMP', Key='PLAYER')
		assert isinstance(player.gstPlayer, object)
		gstPlayer = player.gstPlayer
		isPlaylist = CONFIG.getConfig('TEMP', Key='PLAYLIST').isPlaylist()

		if self._debug: logging.debug(\
				'rendere Texte: {0}'.format(
				CONFIG.getConfig('TEMP', Key='FILENAME')
				))

		textMetaVar = {}
		textMetaVar['if_playlist'] = CONFIG.getConfig(
			'gui',
			'metaData',
			'if_playlist'
			)
		textMetaVar['if_discNr'] = CONFIG.getConfig(
			'gui',
			'metaData',
			'if_discNr'
			)

		for key1 in textMetaVar.iterkeys() :
			s = textMetaVar.get(key1)
			try:
				s = s.replace('%time%', gstPlayer.getDuration())
				s = s.replace('%duration%', gstPlayer.getDuration())
				if isPlaylist :
					s = s.replace('%tracknumberlist%', str(player.getActSong()))
					s = s.replace('%tracktotallist%', str(
							player.getNumberOfSongs()))
				text = s
				while True :
					text = self.find_between(s, '%', '%')
					if text == '' : break
					s = s.replace('%' + text + '%', audio.getMetaData(text))

				textMetaVar[key1] = s
			except: pass

		if not isPlaylist : textMetaVar['if_playlist'] = ''
		if audio.getDiscNo() == "0" : textMetaVar['if_discNr'] = ''

		vList = list()
		self.data = ''
		self.renderedData = None
		if (self.content != None) and (self.content != '') :
			s = self.content
			try:
				s = s.replace('%if_playlist%', textMetaVar['if_playlist'])
				s = s.replace('%if_discNr%', textMetaVar['if_discNr'])
				if isPlaylist :
					s = s.replace('%tracknumberlist%', str(player.getActSong()))
					s = s.replace('%tracktotallist%', str(
							player.getNumberOfSongs()))

				multi = False
				if (self.multiLine == True):
					multi = True

				s = audio.replaceTags(s)

				if '#time#' in s :
					posActTime = key1
					textActTime = s

				s = s.replace('#time#', gstPlayer.getDuration())
				s = s.replace('#duration#', gstPlayer.getDuration())

				if '#bandlogo#' in s:
					logging.debug('Try to get Bandlogo: %s: %s -> %s' % (
						key1,
						self.content,
						self.data
						))
					logo = audio.preBlitLogo(key1)
					if logo == None:
						pass
					else:
						self.renderedData = logo
						self.renderedSize = self.renderedData.get_size()
						return self.renderedData

				if multi == False:
					if (s != ''):
						self.data =  s
						if self._debug:
							logging.debug('Rendere Metadaten: %s: %s -> %s' % (
								key1,
								self.content,
								self.data
								))
						self.renderedData = self.sysFont.render(
								self.data ,
								True,
								self.__metaFields.get(key1)['fontColor']
							)
						self.renderedSize = \
							  self.renderedData.get_size()
				else:
					if self._debug:
						logging.debug('Multiline: %s:' % (s))
					if (self.splitSpaces == True):
						if self._debug: logging.debug('Split Spaces')
						s = s.replace(' ', '\\n')
					vList = s.split('\\n')
					if (len(vList) > 0):
						self.data =  vList
						image = self.get_rendered_maxwidth()
						self.renderedData = image
						self.renderedSize = image.get_size()

			except pygame.error, err:
				print("Autsch! Konnte Metadaten %s nicht rendern: %s" % (
					key1, self.data))
				logging.warning("konnte Metadaten nicht rendern: %s: %s -> %s" %
					(key1,
					self.content,
					self.data))
				logging.warning(err)

		return self.renderedData

	def get_rendered_maxwidth(self):
		maxwidth = self.maxWidth
		if self._debug:
			logging.debug('Rendere Metadaten mit Max-Width: %s %s: %s -> %s' % (
				maxwidth,
				self.name,
				self.content,
				self.data
				))
		rList = list()
		w = 0
		h = 0
		lineH = 0
		lineTest = ''
		lineSave = None
		counter = 0
		for s in self.data:
			counter += 1
			if len(lineTest) > 0:
				lineTest = lineTest + ' ' + s
			else:
				lineTest = s
			rData = self.sysFont.render(
						lineTest,
						True,
						self.font.fontColor
					)
			wT,hT = rData.get_size()
			if self._debug:
				logging.debug('Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			if wT < maxwidth and counter < len(self.data):
				lineSave = rData
				continue
			if lineSave == None:
				lineSave = rData
			if self._debug:
				logging.debug('List-Append Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			rList.append(rData)
			lineTest = ''
			lineSave = None
			if wT > w: w = wT
			h += hT
			lineH = hT

		image = pygame.Surface([w, h])
		winstate = self._config.getConfig('TEMP', 'gui', 'winState')
		image.set_colorkey(CONFIG.getConfig('gui', winstate, 'backgroundColor'))
		image.fill(CONFIG.getConfig('gui', winstate, 'backgroundColor'))
		self.savedRect = image
		hT = 0
		for r in rList:
			mW = 0
			wT,htT = r.get_size()
			if self.alignH == 'right':
				mW = w - wT
			elif self.alignH == 'center':
				mW = (w - wT) / 2

			image.blit(r, (mW, hT))
			hT += lineH

		self.renderedData = image
		return image


	def getBlitObject( self ):
		if (self.renderedData is None) or (self.renderedSize is None):
			print(u"renderedData or renderedSize is none for field {!s}. Will try to render".format((self.name)))
			self.getRenderedData()
		blitObj = dacapo.ui.blitobject.BlitObject(self.name)
		renderedSize = self.renderedSize
		blitPos = (self.pos.posV, self.pos.posH)
		blitObj.setBlitRect(blitPos, renderedSize)
		blitObj.renderedData = self.renderedData
		return blitObj

	def getRenderedData_OLD(self):
		if (self.sysFont is None):
			if (not pygame.font.get_init()):
				pygame.font.init()
			try: self.sysFont = pygame.font.SysFont(self.font.fontName, self.font.fontSize)
			except pygame.error, err:
				print(u"Error at pygame.font.SysFont(%s, %s) . %s " % (
						self.font.fontName, self.font.fontSize, err))
				return None
		if (self.renderedData is None):
			try: self.renderedData = self.sysFont.render(self.content, True, self.font.fontColor)
			except pygame.error, err:
				print(u"Error at sysFont.render(%s, %s) . %s " % (
						self.content, self.font.fontColor, err))
				return None
		self.renderedSize = self.renderedData.get_size()
		return self.renderedData

