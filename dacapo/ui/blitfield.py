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
import sys
from dacapo import errorhandling

class BlitField(dacapo.ui.field.Field, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, name):
		super(BlitField, self).__init__(name)
		self.data = None
		self.renderedData = None
		self.renderedSize = None
		self.sysFont = None
		self.debug = True
		self.savedBackground = None
		self.savedBackgroundRect = None

	def getReplacedContent(self):
		from dacapo.config.gui import *
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		if audio is None:
			return ''
		s = self.content
		s = audio.replaceTags(s)
		return s

	def getRenderedData(self):
		from dacapo.config.gui import *
		logging.debug('Rendering Field: {!s}'.format(self.name))
		if (self.sysFont is None):
			if (not pygame.font.get_init()):
				pygame.font.init()
			logging.debug('Creating font {!s} {!s} {!s} {!s}'.format(self.font.name, self.font.fontSize, self.font.fontWeight, self.font.fontStyle))
			try: self.sysFont = pygame.font.SysFont(self.font.name, self.font.fontSize)
			except pygame.error, err:
				logging.error(u"Error at pygame.font.SysFont(%s, %s) . %s " % (
						self.font.name, self.font.fontSize, err))
				return None
			if 'bold' in self.font.fontWeight.lower():
				self.sysFont.set_bold(True)
			if 'italic' in self.font.fontStyle.lower():
				self.sysFont.set_italic(True)
			if 'oblique' in self.font.fontStyle.lower():
				self.sysFont.set_italic(True)

		logging.debug('Font created. Rendering Field: {!s} with content {!s}'.format(self.name, self.content))
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		player = CONFIG.getConfig('TEMP', Key='PLAYER')
		assert isinstance(player.gstPlayer, object)
		gstPlayer = player.gstPlayer
		isPlaylist = CONFIG.getConfig('TEMP', Key='PLAYLIST').isPlaylist()

		logging.debug('Rendering Text: {0}'.format(CONFIG.getConfig('TEMP', Key='FILENAME')))

		textMetaVar = {}
		textMetaVar['if_playlist'] = CONFIG.getConfig('gui', 'metaData', 'if_playlist')
		textMetaVar['if_discNr'] = CONFIG.getConfig('gui', 'metaData', 'if_discNr')

		if not isPlaylist : textMetaVar['if_playlist'] = ''
		if audio.getDiscNo() == "0" : textMetaVar['if_discNr'] = ''

		vList = list()
		self.data = ''
		self.renderedData = None
		if (self.content != None):
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

				s = s.replace('#time#', gstPlayer.queryPosition())
				s = s.replace('#duration#', gstPlayer.getDuration())
				if self.convert == 'lower':
					s = s.lower()
				elif self.convert == 'upper':
					s = s.upper()

				if '#bandlogo#' in s:
					logging.debug('Try to get Bandlogo: %s: %s -> %s' % (self.name, self.content, self.data))
					logo = audio.preBlitLogo(self.name)
					if logo == None:
						pass
					else:
						self.renderedData = logo
						self.renderedSize = self.renderedData.get_size()
						return self.renderedData

				if multi == False:
					if (s != ''):
						self.data =  s
						logging.debug('Rendering Metadata: %s: %s -> %s' % (self.name, self.content, self.data))
						self.renderedData = self.sysFont.render(self.data, True, self.font.fontColor)
						self.renderedSize = self.renderedData.get_size()
				else:
					logging.debug('Multiline: %s:' % (s))
					if (self.splitSpaces == True):
						if self.debug: logging.debug('Split Spaces')
						s = s.replace(' ', '\\n')
					vList = s.split('\\n')
					if (len(vList) > 0):
						self.data =  vList
						image = self.get_rendered_maxwidth()
						self.renderedData = image
						self.renderedSize = image.get_size()

			except pygame.error, err:
				print("Autsch! Konnte Metadaten %s nicht rendern: %s" % (
					self.name, self.data))
				logging.warning("Can't render Metadata: %s: %s -> %s" % (self.name, self.content, self.data))
				logging.warning(err)

		return self.renderedData

	def get_rendered_maxwidth(self):
		from dacapo.config.gui import *
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		maxwidth = self.maxWidth
		if maxwidth == 0:
			maxwidth = g.width
		logging.debug('Rendering Metadata with Max-Width: %s %s: %s -> %s' % (maxwidth, self.name, self.content, self.data))
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
			logging.debug('Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			if wT < maxwidth and counter < len(self.data):
				lineSave = rData
				continue
			if lineSave == None:
				lineSave = rData
			logging.debug('List-Append Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
			rList.append(rData)
			lineTest = ''
			lineSave = None
			if wT > w: w = wT
			h += hT
			lineH = hT

		image = pygame.Surface([w, h])
		image.set_colorkey(g.backgroundColor)
		image.fill(g.backgroundColor)
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

		self.renderedData = image
		return image


	def getBlitObject( self ):
		from dacapo.config.gui import *
		try:
			if (self.renderedData is None) or (self.renderedSize is None):
				# print(u"renderedData or renderedSize is none for field {!s}. Will try to render".format((self.name)))
				self.getRenderedData()
			blitObj = dacapo.ui.blitobject.BlitObject(self.name, zIndex=self.zIndex)
			if (self.renderedData is None) or (self.renderedSize is None):
				return blitObj
			renderedSize = self.renderedSize
			winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
			g = CONFIG.gui[winstate]
			width = g.width
			height = g.height
			mW = self.pos.posH
			mH = self.pos.posV
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
			blitObj.renderedData = self.renderedData
			blitObj.blitField = self
			blitObj.CONFIG = CONFIG
			if self.isTimeField:blitObj.backup = True
			if self.isLyricField:blitObj.backup = True
			return blitObj
		except: # catch *all* exceptions
			print(sys.exc_info())
			errorhandling.Error.show()
			##event = pygame.event.Event(pygame.event.EventType(pygame.QUIT))
			##pygame.event.post(event)
			pygame.quit()


	def replaceData(self, data):
		self.content = data
		self.renderedData = None
		return

