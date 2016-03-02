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

	fontName = ''
	fontSize = 0
	fontColor = ''

	def __init__(self):
		super(Font, self).__init__()

	def grabXMLData(self, xml):
		self.fontName = xml.find('font').text
		self.fontSize = int(xml.find('fontSize').text)
		self.fontColor = xml.find('fontColor').text

	def printValues(self):
		print('\nFont: {!s} Größe: {!s} Farbe: {!s}'.format(self.fontName, self.fontSize, self.fontColor))