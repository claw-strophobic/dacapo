#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import dacapo.ui.interface_blitobject
import dacapo.ui.blitobject
import pygame

class BlitPicture(dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, pic, zIndex=-1):
		super(BlitPicture, self).__init__()
		self.debug = True
		self.data = pic
		self.renderedData = self.scalePic(pic)
		self.renderedSize = None if self.renderedData is None else self.renderedData.get_size()
		self.zIndex = zIndex
		self.savedBackground = None

	def scalePic(self, pic):
		from dacapo.config.gui import *
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		if (g.picField is None): return None
		winWidth = g.picField.maxWidth
		winHeight = g.picField.maxHeight

		# --> skalieren -------------------------------
		if self.debug : logging.debug("Pic-Area: {!s} * {!s} at {!s}, {!s}".format(winWidth, winHeight, g.picField.pos.posH, g.picField.pos.posV))
		picW, picH = pic.get_size()

		if picW == 0 : picW = 1
		proz = (winWidth * 100.0) / (picW)
		h = int(round( (picH * proz) / 100.0))
		w = int(round(winWidth))
		if self.debug : logging.debug("Picture skalieren: " \
			"Originalbreite: %s Hoehe: %s PROZENT: %s " \
			"-> Neue W: %s H: %s" % (picW, picH, proz, w, h))
		if h > winHeight :
			proz = (winHeight * 100.0) / (h)
			w = int(round( (w * proz) / 100.0 ))
			h = int(round( (h * proz) / 100.0))
			if self.debug : logging.debug(\
				"NEUSKALIERUNG da Bild zu hoch wurde: "\
				"Originalbreite: %s Hoehe: %s PROZENT: %s " \
				"-> Neue W: %s H: %s " % (picW, picH, proz, w, h))
		result = pygame.transform.scale(pic, (w, h))
		# <-- skalieren -------------------------------

		if self.debug : logging.info("done.")
		return result


	def getBlitObject( self ):
		from dacapo.config.gui import *
		blitObj = dacapo.ui.blitobject.BlitObject('picture', zIndex=self.zIndex)
		if (self.renderedData is None) or (self.renderedSize is None):
			return blitObj
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		# get the screen-size
		width = g.picField.maxWidth
		height = g.picField.maxHeight
		w = g.picField.pos.posH
		h = g.picField.pos.posV
		picW, picH = self.renderedSize
		# --> calculate the position ---------------------------
		w += (width - picW) / 2
		h += (height - picH) / 2
		renderedSize = self.renderedSize
		blitPos = (w, h)
		blitObj.setBlitRect(blitPos, renderedSize)
		blitObj.renderedData = self.renderedData
		blitObj.blitField = self
		return blitObj
