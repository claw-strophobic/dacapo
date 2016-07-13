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

class Condition(dacapo.ui.configelement.ConfigElement):

	def __init__(self, name=''):
		super(Condition, self).__init__()
		self.name = name
		self.content = ''
		self.comment = ''
		self.operator = ''
		self.operand = ''
		self.type = 'cond'

	def grabXMLData(self, xml):
		self.name = xml.tag
		self.operator = xml.get("operator", "notempty")
		self.operand = xml.get("operand", " ").lower()
		self.comments = xml.get("comments", " ")
		self.content = xml.text

	def checkOperand(self, operand):
		test = False
		if (self.operator == 'notempty') \
			and (operand <> None) and (operand):
			test = True
		elif (self.operator == 'empty') and (operand is None):
			test = True
		elif (self.operator == 'empty') \
				and (operand <> None) and (not operand):
			test = True
		return test

	def test(self):
		res = True
		if not isinstance(self.name, basestring) or len(self.name) <= 0:
			res = False
		if not isinstance(self.operator, basestring) or len(self.operator) <= 0:
			res = False
		if not isinstance(self.operand, basestring) or len(self.operand) <= 0:
			res = False
		if not isinstance(self.content, basestring) or len(self.content) <= 0:
			res = False
		return res

	def setVars(self):
		extendvars = {
			'comments': {
				'target': 'comments',
				'type': 'text',
			},
			'content': {
				'target': 'content',
				'type': 'text',
			},
			'operator': {
				'target': 'operator',
				'type': 'text',
			},
			'operand': {
				'target': 'operand',
				'type': 'text',
			},
		}
		self.vars.update(extendvars)


	def printValues(self):
		print('Condition: {!s} {!s} {!s} {!s}'.format(self.name, self.content, self.operator, self.operand))