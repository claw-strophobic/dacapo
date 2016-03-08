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

find_between = dacapo.ui.interface_blitobject.find_between

class BlitField(dacapo.ui.field.Field, dacapo.ui.interface_blitobject.BlitInterface):

	EXAMPLES = {
		"artist": "Killing Joke",
		"albumartist": "Killing Joke",
		"album": "Pylon",
		"title": "Into The Unknown",
		"date": "2015",
		"discnumber" :"1/2",
		"genre": "Post-Punk",
		"tracknumber": "10/10",
		"comments": u"Dies ist ein Kommentar.\nEr geht über zwei Zeilen.",
	}

	def __init__(self, name):
		super(BlitField, self).__init__(name)
		self.renderedData = None
		self.renderedSize = None
		self.sysFont = None
		## dacapo.ui.field.Field.__init__(name)
		## dacapo.ui.interface_blitobject.BlitObject.__init__()

	def getExampleData(self, key):
		res = ""
		if self.EXAMPLES.has_key(key):
			res = self.EXAMPLES[key]
		return res

	def getReplacedContent(self):
		text = s = self.content
		while True :
			text = find_between(s, '%', '%')
			if text == '' : break
			s = s.replace('%' + text + '%', self.getExampleData(text))
		return s


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

	def getRenderedData(self):
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

