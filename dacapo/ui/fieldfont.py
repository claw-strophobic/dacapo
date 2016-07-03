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

class FieldFont(dacapo.ui.configelement.ConfigElement):

	def __init__(self):
		super(FieldFont, self).__init__()
		self.name = ''
		self.fontSize = 0
		self.fontColor = ''
		self.fontStyle = ''
		self.fontWeight = ''

	def printValues(self):
		print('\nFont: {!s} Größe: {!s} Farbe: {!s}'.format(self.name, self.fontSize, self.fontColor))

	def getRGBAColor(self):
		from gi.repository import Gdk
		color = Gdk.RGBA()
		colorRGB = []
		for c in self.fontColor:
			colorRGB.append(str(c))
		parseThis = 'rgb(' + ','.join(colorRGB) + ')'
		color.parse(parseThis)
		return color

	def setVars(self):
		self.vars = {
			'font': {
				'target': 'name',
				'type': 'text',
			},
			'fontStyle': {
				'target': 'fontStyle',
				'type': 'text',
			},
			'fontWeight': {
				'target': 'fontWeight',
				'type': 'text',
			},
			'fontSize': {
				'target': 'fontSize',
				'type': 'int',
			},
			'fontColor': {
				'target': 'fontColor',
				'type': 'color',
			},
		}

