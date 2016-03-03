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
import dacapo.ui.position
import dacapo.ui.font


class Field(dacapo.ui.configelement.ConfigElement):

	def __init__(self, name):
		super(Field, self).__init__()
		self.name = name
		self.comments = ''
		self.content = ''
		self.multiLine = False
		self.overlay = False
		self.splitSpaces = False
		self.zIndex = 0
		self.pos = dacapo.ui.position.Position()
		self.font = dacapo.ui.font.Font()

	def grabXMLData(self, xml):
		super(Field, self).grabXMLData(xml)
		self.font.grabXMLData(xml)
		self.pos.grabXMLData(xml)
		self.content = xml.find('value').text

	def printValues(self):
		print('Field: {!s} Pos: {!s}x{!s} Font: {!s}'.format(self.name, self.pos.posH, self.pos.posV, self.font.fontName))
		members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]
		print(dict(self))
		# print members