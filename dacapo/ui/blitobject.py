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
		self.__rect = pygame.Rect(0, 0, 0, 0)
		self.__renderedData = None
		self.__blitPos = 0
		self.__renderedSize = 0

	def setBlitRect(self, pos, size):
		self.__blitPos = pos
		self.__renderedSize = size
		try: self.__rect = pygame.Rect(self.__blitPos, self.__renderedSize)
		except: pass
		return

