#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import pygame
import logging

class BlitObject(object):

	def __init__(self, name, zIndex=0):
		super(BlitObject, self).__init__()
		self.name = name
		self.rect = pygame.Rect(0, 0, 0, 0)
		self.renderedData = None
		self.blitPos = 0
		self.renderedSize = 0
		self.zIndex = zIndex
		self.blitField = None


	def setBlitRect(self, pos, size):
		self.blitPos = pos
		self.renderedSize = size
		try: self.rect = pygame.Rect(self.blitPos, self.renderedSize)
		except: pass
		return

	def getSavedBackground(self):
		print("field is {!s} field.savedBackground is {!s}".format(type(self.blitField), type(self.blitField.savedBackground)))
		if (self.blitField is None):
			return False
		return self.blitField.savedBackground

	def doSaveBackground(self, screen):
		if (self.blitField is None): return
		try:
			self.blitField.savedBackground = screen.subsurface(self.rect).copy()
			print("Saved screen(%s, (%s))." % (self.name, self.rect))
		except pygame.error, err:
			self.blitField.savedBackground = None
			print("Error at saving screen(%s, (%s)) . %s " % (self.name, self.rect, err))
		return

	def doRestoreBackground(self, screen):
		if (self.blitField is None): return
		if self.blitField.savedBackground is None:
			return
		try: screen.blit(self.blitField.savedBackground, self.rect)
		except pygame.error, err:
			logging.warning("Error at self.screen.blit(%s, (%s)) . %s " % (self.name, self.rect, err))
			return False
		return
