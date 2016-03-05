#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import dacapo.ui.font

class LyricFont(dacapo.ui.font.Font):

	def __init__(self):
		super(LyricFont, self).__init__()
		self.posV = 0
		self.alignH = 'center'

	def printValues(self):
		print('\nLyricFont: {!s} Größe: {!s} Farbe: {!s} posV: {!s} alignH: {!s}'.format(self.fontName, self.fontSize, self.fontColor, self.posV, self.alignH))
