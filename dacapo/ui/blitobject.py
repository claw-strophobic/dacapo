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


class BlitObject(object):

	def __init__(self, name):
		super(BlitObject, self).__init__()
		self.name = name
		self.rect = pygame.Rect(0,0,0,0)
		self.renderedData = None
		self.blitPos = 0
		self.renderedSize = 0

	def setBlitRect(self, pos, size):
		self.blitPos = pos
		self.renderedSize = size
		try: self.rect = pygame.Rect(self.blitPos,self.renderedSize)
		except: pass
		return

