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

class Position(dacapo.ui.configelement.ConfigElement):

	def __init__(self):
		super(Position, self).__init__()
		# Horizontal
		self.alignH = ''
		self.posH = 0
		self.posRefH = ''
		self.maxWidth = 0
		# Vertical
		self.alignV = ''
		self.posV = 0
		self.posRefV = ''
		self.maxHeight = 0

	def grabXMLData(self, xml):
		# Horizontal
		try: self.posH = int(xml.find('posH').text)
		except: pass
		try: self.alignH = xml.find('alignH').text
		except: pass
		try: self.posRefH = xml.find('posRefH').text
		except: pass
		try: self.maxWidth = int(xml.find('maxWidth').text)
		except: pass
		# Vertical
		try: self.posV = int(xml.find('posV').text)
		except: pass
		try: self.alignV = xml.find('alignV').text
		except: pass
		try: self.posRefV = xml.find('posRefV').text
		except: pass
		try: self.maxHeight = int(xml.find('maxHeight').text)
		except: pass
