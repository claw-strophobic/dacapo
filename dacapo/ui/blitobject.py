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
		self.savedBackground = None

	def setBlitRect(self, pos, size):
		self.blitPos = pos
		self.renderedSize = size
		try: self.rect = pygame.Rect(self.blitPos, self.renderedSize)
		except: pass
		return

	def doSaveBackground(self, screen):
		try: self.savedBackground = screen.subsurface(self.rect).copy()
		except: self.savedBackground = None
		return

	def doRestoreBackground(self, screen):
		if self.savedBackground == None:
			return
		try: screen.blit(self.savedBackground, self.rect)
		except pygame.error, err:
			logging.warning("Error at self.screen.blit(%s, (%s)) . %s " % (self.name, self.rect, err))
			return False
		return
