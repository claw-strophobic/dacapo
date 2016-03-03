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
import dacapo.ui.lyricfont
import dacapo.ui.field
import dacapo.ui.position

class Gui(dacapo.ui.configelement.ConfigElement):

	name = ''
	height = 0
	width = 0
	backgroundColor = None
	mouseVisible = False
	fields = {}
	lyricFont = None
	pictureArea = None


	def __init__(self, name):
		super(Gui, self).__init__()
		self.name = name
		self.lyricFont = dacapo.ui.lyricfont.LyricFont()
		self.pictureArea = dacapo.ui.position.Position()

	def grabXMLData(self, xml):
		super(Gui, self).grabXMLData(xml)
		self.lyricFont.grabXMLData(xml.find('lyricFont'))
		fields = xml.find('fields')
		for child in fields:
			f = dacapo.ui.field.Field(child.tag)
			f.grabXMLData(child)
			self.fields[child.tag] = f

	def printValues(self):
		print('\nGui: {!s} {!s}x{!s} Background: {!s} Maus: {!s}'.format(self.name, self.height, self.width, self.backgroundColor, self.mouseVisible))
		self.lyricFont.printValues()
		for k,f in self.fields.iteritems():
			f.printValues()
