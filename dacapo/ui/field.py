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
import dacapo.ui.fieldfont


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
		self.maxWidth = 0
		self.maxHeight = 0
		self.pos = dacapo.ui.position.Position()
		self.font = dacapo.ui.fieldfont.FieldFont()
		self.isTimeField = False
		self.isLyricField = False
		self.isPicField = False

	def setVars(self):
		extendvars = {
			'comments': {
				'target': 'comments',
				'type': 'text',
			},
			'value': {
				'target': 'content',
				'type': 'text',
			},
			'multiLine': {
				'target': 'multiLine',
				'type': 'boolean',
			},
			'overlay': {
				'target': 'overlay',
				'type': 'boolean',
			},
			'splitSpaces': {
				'target': 'splitSpaces',
				'type': 'boolean',
			},
			'zIndex': {
				'target': 'zIndex',
				'type': 'int',
			},
			'maxWidth': {
				'target': 'maxWidth',
				'type': 'int',
			},
			'maxHeight': {
				'target': 'maxHeight',
				'type': 'int',
			},
		}
		self.vars.update(extendvars)

	def test(self):
		res = True
		if not isinstance(self.name, basestring) or len(self.name) <= 0:
			#print('Field: {!s} {!s} IsString: {!s} Len: {!s}'.format(self.name, isinstance(self.name, basestring),len(self.name)))
			res = False
		if not isinstance(self.content, basestring) or len(self.content) <= 0:
			#print('Content: {!s} {!s} IsString: {!s} Len: {!s}'.format(self.content, isinstance(self.content, basestring),len(self.content)))
			res = False
		return res

	def grabXMLData(self, xml):
		super(Field, self).grabXMLData(xml)
		from lxml import etree
		self.font.grabXMLData(xml)
		self.pos.grabXMLData(xml)
		if (self.content.find('%time%') > -1): self.isTimeField = True
		if (self.content.find('%synclyrics%') > -1): self.isLyricField = True
		if (self.content.find('%pictures%') > -1): self.isPicField = True


	def printValues(self):
		print('Field: {!s} Content: {!s} Pos: {!s}x{!s} Font: {!s}'.format(self.name, self.content, self.pos.posH, self.pos.posV, self.font.name))
		members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]
		## print(dict(self))
		# print members