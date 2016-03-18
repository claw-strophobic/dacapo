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

	def __init__(self, pic):
		super(BlitPicture, self).__init__()
		self.debug = True
		self.__data = pic
		self.__renderedData = self.scalePic(pic)
		self.__renderedSize = self.__renderedData.get_size()

	def scalePic(self, pic):
		from dacapo.config.gui import *
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		winWidth = g.pictureArea.maxWidth
		winHeight = g.pictureArea.maxHeight

		# --> skalieren -------------------------------
		print("Pic-Area: {!s} * {!s} at {!s}, {!s}".format(winWidth, winHeight, g.pictureArea.posH, g.pictureArea.posV))
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
		blitObj = dacapo.ui.blitobject.BlitObject('picture')
		if (self.__renderedData is None) or (self.__renderedSize is None):
			return blitObj
		winstate = CONFIG.getConfig('TEMP', 'gui', 'winState')
		g = CONFIG.gui[winstate]
		# get the screen-size
		width = g.pictureArea.maxWidth
		height = g.pictureArea.maxHeight
		w = g.pictureArea.posH
		h = g.pictureArea.posV
		picW, picH = self.__renderedSize
		# --> calculate the position ---------------------------
		w += (width - picW) / 2
		h += (height - picH) / 2
		renderedSize = self.__renderedSize
		blitPos = (w, h)
		blitObj.setBlitRect(blitPos, renderedSize)
		blitObj.__renderedData = self.__renderedData
		return blitObj
