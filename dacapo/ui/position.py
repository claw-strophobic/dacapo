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
	# Horizontal
	alignH = ''
	posH = 0
	posRefH = ''
	maxWidth = 0
	# Vertical
	alignV = ''
	posV = 0
	posRefV = ''
	maxHeight = 0

	def __init__(self):
		super(Position, self).__init__()

	def grabXMLData(self, xml):
		# Horizontal
		try: self.posH = int(xml.find('posH').text)
		except: pass
		try: self.alignH = xml.find('alignH').text
		except: pass
		try: self.posRefH = xml.find('posRefH').text
		except: pass
		try: self.maxWidth = int(xml.find('max-width').text)
		except: pass
		# Vertical
		try: self.posV = int(xml.find('posV').text)
		except: pass
		try: self.alignV = xml.find('alignV').text
		except: pass
		try: self.posRefV = xml.find('posRefV').text
		except: pass
		try: self.maxHeight = int(xml.find('max-height').text)
		except: pass
