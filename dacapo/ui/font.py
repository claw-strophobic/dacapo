#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import dacapo.ui.configelement


class Font(dacapo.ui.configelement.ConfigElement):

	def __init__(self):
		super(Font, self).__init__()
		self.fontName = ''
		self.fontSize = 0
		self.fontColor = ''

	def grabXMLData(self, xml):
		super(Font, self).grabXMLData(xml)
		self.fontName = xml.find('font').text

	def printValues(self):
		print('\nFont: {!s} Größe: {!s} Farbe: {!s}'.format(self.fontName, self.fontSize, self.fontColor))

	def getRGBAColor(self):
		from gi.repository import Gdk
		color = Gdk.RGBA()
		colorRGB = []
		for c in self.fontColor:
			colorRGB.append(str(c))
		parseThis = 'rgb(' + ','.join(colorRGB) + ')'
		color.parse(parseThis)
		return color