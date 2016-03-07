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

	EXAMPLES = {
		"artist": "Killing Joke",
		"albumartist": "Killing Joke",
		"album": "Pylon",
		"title": "Into The Unknown",
		"date": "2015",
		"discnumber" :"1/2",
		"genre": "Post-Punk",
		"tracknumber": "10/10",
	}

	def __init__(self, name):
		dacapo.ui.field.Field.__init__(name)
		dacapo.ui.interface_blitobject.BlitObject.__init__()
		pygame.init()
		self.blitObj = dacapo.ui.blitobject.BlitObject(name)


	def getExampleData(self, key):
		res = ""
		if self.EXAMPLES.has_key(key):
			res = self.EXAMPLES[key]
		return res

	def getBlitObject( self ):
		renderedSize = self.renderedSize
		blitPos = (self.pos.posV, self.pos.posH)
		self.blitObj.setBlitRect(blitPos, renderedSize)
		self.blitObj.renderedData = self.renderedData
		return self.blitObj

	def getRenderedData(self):
		if (self.sysFont == None):
			try: self.sysFont = pygame.font.SysFont(self.font.fontName, self.font.fontSize)
			except: return None
		if (self.renderedData == None):
			try: self.renderedData = self.sysFont.render(self.content, True,self.font.fontColor)
			except: return None
		self.renderedSize = self.renderedData.get_size()
		return self.renderedData

