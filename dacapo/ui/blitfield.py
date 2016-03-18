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
import pygame

class BlitField(dacapo.ui.field.Field, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, name):
		super(BlitField, self).__init__(name)
		self.__data = None
		self.__renderedData = None
		self.__renderedSize = None
		self.__sysFont = None
		self.__debug = True

	def getReplacedContent(self):
		from dacapo.config.gui import *
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
		from dacapo.config.gui import *
		if (self.__sysFont is None):
			if (not pygame.font.get_init()):
				pygame.font.init()
			try: self.__sysFont = pygame.font.SysFont(self.font.fontName, self.font.fontSize)
			except pygame.error, err:
				print(u"Error at pygame.font.SysFont(%s, %s) . %s " % (
						self.font.fontName, self.font.fontSize, err))
				return None

		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		player = CONFIG.getConfig('TEMP', Key='PLAYER')
		assert isinstance(player.gstPlayer, object)
		gstPlayer = player.gstPlayer
		isPlaylist = CONFIG.getConfig('TEMP', Key='PLAYLIST').isPlaylist()

		if self.__debug: logging.debug(\
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
		self.__data = ''
		self.__renderedData = None
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
					posActTime = self.name
					textActTime = s

				s = s.replace('#time#', gstPlayer.getDuration())
				s = s.replace('#duration#', gstPlayer.getDuration())

				if '#bandlogo#' in s:
					logging.debug('Try to get Bandlogo: %s: %s -> %s' % (
						self.name,
						self.content,
						self.__data
						))
					logo = audio.preBlitLogo(self.name)
					if logo == None:
						pass
					else:
						self.__renderedData = logo
						self.__renderedSize = self.__renderedData.get_size()
						return self.__renderedData

				if multi == False:
					if (s != ''):
						self.__data =  s
						if self.__debug:
							logging.debug('Rendere Metadaten: %s: %s -> %s' % (
								self.name,
								self.content,
								self.__data
								))
						self.__renderedData = self.__sysFont.render(self.__data, True, self.font.fontColor)
						self.__renderedSize = self.__renderedData.get_size()
				else:
					if self.__debug:
						logging.debug('Multiline: %s:' % (s))
					if (self.splitSpaces == True):
						if self.__debug: logging.debug('Split Spaces')
						s = s.replace(' ', '\\n')
					vList = s.split('\\n')
					if (len(vList) > 0):
						self.__data =  vList
						image = self.get_rendered_maxwidth()
						self.__renderedData = image
						self.__renderedSize = image.get_size()

			except pygame.error, err:
				print("Autsch! Konnte Metadaten %s nicht rendern: %s" % (
					self.name, self.__data))
				logging.warning("konnte Metadaten nicht rendern: %s: %s -> %s" %
								(self.name,
					self.content,
					self.__data))
				logging.warning(err)

		return self.__renderedData

	def get_rendered_maxwidth(self):
		from dacapo.config.gui import *
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		maxwidth = self.maxWidth
		if maxwidth == 0:
			maxwidth = CONFIG.getConfig('gui', winstate, 'width')
		if self.__debug:
			logging.debug('Rendere Metadaten mit Max-Width: %s %s: %s -> %s' % (
				maxwidth,
				self.name,
				self.content,
				self.__data
				))
		rList = list()
		w = 0
		h = 0
		lineH = 0
		lineTest = ''
		lineSave = None
		counter = 0
		for s in self.__data:
			counter += 1
			if len(lineTest) > 0:
				lineTest = lineTest + ' ' + s
			else:
				lineTest = s
			rData = self.__sysFont.render(
						lineTest,
						True,
						self.font.fontColor
					)
			wT,hT = rData.get_size()
			if self.__debug:
				logging.debug('Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			if wT < maxwidth and counter < len(self.__data):
				lineSave = rData
				continue
			if lineSave == None:
				lineSave = rData
			if self.__debug:
				logging.debug('List-Append Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			rList.append(rData)
			lineTest = ''
			lineSave = None
			if wT > w: w = wT
			h += hT
			lineH = hT

		image = pygame.Surface([w, h])
		image.set_colorkey(CONFIG.getConfig('gui', winstate, 'backgroundColor'))
		image.fill(CONFIG.getConfig('gui', winstate, 'backgroundColor'))
		self.savedRect = image
		hT = 0
		for r in rList:
			mW = 0
			wT,htT = r.get_size()
			if self.pos.alignH == 'right':
				mW = w - wT
			elif self.pos.alignH == 'center':
				mW = (w - wT) / 2

			image.blit(r, (mW, hT))
			hT += lineH

		self.__renderedData = image
		return image


	def getBlitObject( self ):
		from dacapo.config.gui import *
		if (self.__renderedData is None) or (self.__renderedSize is None):
			print(u"renderedData or renderedSize is none for field {!s}. Will try to render".format((self.name)))
			self.getRenderedData()
		blitObj = dacapo.ui.blitobject.BlitObject(self.name)
		if (self.__renderedData is None) or (self.__renderedSize is None):
			return blitObj
		renderedSize = self.__renderedSize
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		width = CONFIG.getConfig('gui', winstate, 'width')
		height = CONFIG.getConfig('gui', winstate, 'height')
		g = CONFIG.gui[winstate]
		mW = 0
		mH = 0
		textWidth, textHeight = renderedSize
		# align relatively to another object
		if (self.pos.posRefH != '') and (g.fields.has_key(self.pos.posRefH)):
			posRefH = g.fields[self.pos.posRefH].getBlitObject()
			refPosW, refPosH = posRefH.blitPos
			refWidth, refHeight = posRefH.renderedSize
			mW = refPosW + refWidth

		if (self.pos.posRefV != '') and (g.fields.has_key(self.pos.posRefV)):
			posRefV = g.fields[self.pos.posRefV].getBlitObject()
			refPosW, refPosH = posRefV.blitPos
			refWidth, refHeight = posRefV.renderedSize
			mH = refPosH + refHeight

		## align left or right or center
		if self.pos.alignH == 'left':
			mW += self.pos.posH
		elif self.pos.alignH == 'right':
			mW += self.pos.posH + textWidth
			mW = width - mW
		elif self.pos.alignH == 'center':
			mW = (width - textWidth) / 2

		## align top or bottom or middle
		if self.pos.alignV == 'top':
			mH += self.pos.posV
		elif self.pos.alignV == 'bottom':
			mH += self.pos.posV + textHeight
			mH = height - mH
		elif self.pos.alignV == 'center':
			mH = (height - textHeight) / 2

		blitPos = (mW, mH)
		blitObj.setBlitRect(blitPos, renderedSize)
		blitObj.__renderedData = self.__renderedData
		return blitObj

	def getRenderedData_OLD(self):
		if (self.__sysFont is None):
			if (not pygame.font.get_init()):
				pygame.font.init()
			try: self.__sysFont = pygame.font.SysFont(self.font.fontName, self.font.fontSize)
			except pygame.error, err:
				print(u"Error at pygame.font.SysFont(%s, %s) . %s " % (
						self.font.fontName, self.font.fontSize, err))
				return None
		if (self.__renderedData is None):
			try: self.__renderedData = self.__sysFont.render(self.content, True, self.font.fontColor)
			except pygame.error, err:
				print(u"Error at sysFont.render(%s, %s) . %s " % (
						self.content, self.font.fontColor, err))
				return None
		self.__renderedSize = self.__renderedData.get_size()
		return self.__renderedData

