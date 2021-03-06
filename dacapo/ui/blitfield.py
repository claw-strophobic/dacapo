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
import re

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

	def initFields(self):
		self.renderedData = None
		self.renderedSize = None
		self.sysFont = None

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

		try: logging.debug(u'Font created. Rendering Field: {!s} with content {!s}'.format(self.name, self.content))
		except: pass
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

				multi = self.multiLine

				s = audio.replaceTags(s)

				s = s.replace('#time#', gstPlayer.queryPosition())
				s = s.replace('#duration#', gstPlayer.getDuration())
				if self.convert == 'lower':
					s = s.lower()
				elif self.convert == 'upper':
					s = s.upper()

				if '#bandlogo#' in s.lower():
					logging.debug('Try to get Bandlogo: %s: %s -> %s' % (self.name, self.content, self.data))
					logo = audio.preBlitLogo(self.name)
					if logo == None:
						logging.debug('Got no Bandlogo')
						pass
					else:
						logging.debug('Rendering Bandlogo')
						self.renderedData = logo
						self.renderedSize = self.renderedData.get_size()
						return self.renderedData

				if multi == False:
					self.data =  s
					logging.debug('Rendering Metadata: %s: %s -> %s' % (self.name, self.content, self.data))
					self.renderedData = self.sysFont.render(self.data, True, self.font.fontColor)
					self.renderedSize = self.renderedData.get_size()
				else:
					logging.debug('Multiline: %s:' % (s))
					if (self.splitSpaces == True):
						logging.debug('Split Spaces')
						s = s.replace(' ', '\n')
					try:
						insensitive_text = re.compile(re.escape('\\n'), re.IGNORECASE)
						s = insensitive_text.sub('\n', s)
					except:
						pass
					vList = s.splitlines(True)
					self.data =  vList
					image = self.getRenderedMultiline(vList)
					self.renderedData = image
					self.renderedSize = image.get_size()

			except pygame.error, err:
				logging.warning("Can't render Metadata: %s: %s -> %s" % (self.name, self.content, self.data))
				logging.warning(err)

		return self.renderedData

	def getRenderedMultiline(self, vList):
		from dacapo.config.gui import *

		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		if (CONFIG is None) or (CONFIG.gui is None) or not (CONFIG.gui.has_key(winstate)):
			CONFIG = readconfig.getConfigObject()
		if not CONFIG.gui.has_key(winstate):
			return None
		g = CONFIG.gui[winstate]
		logging.debug('Rendering Multiline Metadata: %s: %s -> %s' % (self.name, self.content, vList))
		rList = list()
		maxwidth = self.pos.maxWidth
		if maxwidth == 0:
			maxwidth = g.width
		w = maxwidth
		h = 0
		lineH = 0
		for s in vList:
			try:
				insensitive_text = re.compile(re.escape('\n'), re.IGNORECASE)
				s = insensitive_text.sub('', s)
			except:
				pass
			logging.debug('Trying Text: %s ' % (s))
			s_org = s
			s_spaces = maxwidth
			count = 0
			while s_spaces > 0:
				count += 1
				s_temp = s[0:s_spaces].strip()
				if len(s_temp) <= 0:
					break
				s_hang = s[s_spaces:].strip()
				s_spaces = s_temp.rfind(' ')
				rData = self.sysFont.render(s_temp, True, self.font.fontColor)
				wT, hT = rData.get_size()
				logging.debug('Text: %s Hang: %s Width: %s Next Space: %s' % (s_temp, s_hang, wT, s_spaces))
				if wT <= maxwidth:
					try: logging.debug(u'List-Append Text: {!s} Text-Height: {!s}'.format(s_temp, hT))
					except: pass
					rList.append(rData)
					h += hT
					lineH = hT
					if s_temp == s_org:
						break
					s = s_hang.strip()
					s_spaces = maxwidth
				if count > 99: ## Emergency Break
					break


		logging.debug('Found {!s} Lines with Line-Height: {!s}'.format(len(rList), lineH))
		maxheight = self.pos.maxHeight
		if maxheight == 0:
			maxheight = g.height
		if h > maxheight:
			h = maxheight
		image = pygame.Surface([w, h])
		image.set_colorkey(g.backgroundColor)
		image.fill(g.backgroundColor)
		self.savedRect = image
		hT = 0
		i = 0
		for r in rList:
			i += 1
			mW = 0
			wT,htT = r.get_size()
			if self.alignment == 'right':
				mW = w - wT
			elif self.alignment == 'center':
				mW = (w - wT) / 2

			logging.debug('Blitting line {!s} position: {!s}, {!s}'.format(i, mW, hT))
			image.blit(r, (mW, hT))
			hT += lineH
			if hT >= maxheight:
				break

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
				logging.debug("V-Position of {!s} is relative to {!s}: {!s} + height: {!s}".format(self.name, posRefV.name, refPosH, refHeight))

			logging.debug("Align position of {!s} is horizontal: {!s} {!s} vertical: {!s} {!s}".format(self.name, self.pos.alignH, self.pos.posH, self.pos.alignV, self.pos.posV))
			## align left or right or center
			if self.pos.alignH == 'left':
				mW += self.pos.posH
			elif self.pos.alignH == 'right':
				mW += self.pos.posH + textWidth
				mW = width - mW
			elif self.pos.alignH == 'center':
				mW += (width - textWidth) / 2

			## align top or bottom or middle
			if self.pos.alignV == 'top':
				mH += self.pos.posV
			elif self.pos.alignV == 'bottom':
				mH += self.pos.posV + textHeight
				mH = height - mH
			elif self.pos.alignV == 'center':
				mH += (height - textHeight) / 2

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
			##pygame.quit()


	def replaceData(self, data):
		self.content = data
		self.renderedData = None
		return

