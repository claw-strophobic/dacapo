#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import xml.etree.ElementTree as ET

class Condition(object):

	name = ''
	content = ''
	operator = ''
	operand = ''
	type = 'cond'

	def __init__(self):
		pass

	def grabXMLData(self, xml):
		self.name = xml.tag
		self.operator = xml.get("operator", "ne")
		self.operand = xml.get("operand", " ").lower()
		self.content = xml.text

	def checkOperand(self, operand):
		test = False
		if (self.operator == 'notempty') \
			and (operand <> None) and (operand):
			test = True
		elif (self.operator == 'empty') and (operand == None):
			test = True
		elif (self.operator == 'empty') \
				and (operand <> None) and (not operand):
			test = True
		return test


	def printValues(self):
		print('Condition: {!s} {!s} {!s} {!s}'.format(self.name, self.content, self.operator, self.operand))