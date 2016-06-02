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
		self.backup = False
		self.CONFIG = None


	def setBlitRect(self, pos, size):
		self.blitPos = pos
		self.renderedSize = size
		try: self.rect = pygame.Rect(self.blitPos, self.renderedSize)
		except: pass
		return

	def getSavedBackground(self):
		if (self.blitField is None):
			return None
		return self.blitField.savedBackground

	def doSaveBackground(self, screen):
		if (self.backup is False): return
		if (self.blitField is None): return

		try:
			if (self.blitField.isPicField):
				print("Try Saving Background for %s Size: %s" % (self.name,self.rect.size))
				image = pygame.Surface(self.rect.size)
				winState = self.CONFIG.getConfig('TEMP', 'gui', 'winState')
				color = self.CONFIG.getConfig('gui', winState, 'backgroundColor')
				print("Try Filling Background with color %s for state %s for %s Size: %s" % (str(color), winState, self.name,self.rect.size))
				self.blitField.doFillBackground(image, color)
				print("Saving Background: {!s}".format(type(image)))
				self.blitField.savedBackground = image
			else:
				self.blitField.savedBackground = screen.subsurface(self.rect).copy()
			self.blitField.savedBackgroundRect = self.rect.copy()
			if (self.blitField.isPicField):
				print("Saving Background for %s Rect: %s" % (self.name,self.blitField.savedBackgroundRect))
		except pygame.error, err:
			self.blitField.savedBackground = None
			logging.warning("Error saving Background on %s: %s" % (self.name, err))
		except:
			import sys
			self.blitField.savedBackground = None
			logging.warning("Error saving Background on %s" % (self.name))
			logging.warning(sys.exc_info()[0])
		return

	def doRestoreBackground(self, screen):
		if (self.backup is False): return
		if (self.blitField is None): return

		if self.blitField.savedBackground is None:
			return
		if (self.blitField.isPicField):
			print("Restoring Background for %s Rect: %s" % (self.name,self.blitField.savedBackgroundRect))
		try:
			screen.blit(self.blitField.savedBackground, self.blitField.savedBackgroundRect)
			if (self.blitField.isLyricField) or (self.blitField.isPicField):
				pygame.display.update(self.blitField.savedBackgroundRect)
		except pygame.error, err:
			logging.warning("Error at self.screen.blit(%s, (%s)) . %s " % (self.name, self.blitField.savedBackgroundRect, err))
			return False

		return
