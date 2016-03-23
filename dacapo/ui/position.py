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

	def setVars(self):
		self.vars = {
			'alignH': {
				'target': 'alignH',
				'type': 'text',
			},
			'posH': {
				'target': 'posH',
				'type': 'int',
			},
			'posRefH': {
				'target': 'posRefH',
				'type': 'text',
			},
			'maxWidth': {
				'target': 'maxWidth',
				'type': 'int',
			},
			'alignV': {
				'target': 'alignV',
				'type': 'text',
			},
			'posV': {
				'target': 'posV',
				'type': 'int',
			},
			'posRefV': {
				'target': 'posRefV',
				'type': 'text',
			},
			'maxHeight': {
				'target': 'maxHeight',
				'type': 'int',
			},
		}
