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
import dacapo.ui.blitfield
import dacapo.ui.position

class Gui(dacapo.ui.configelement.ConfigElement):

	def __init__(self, name):
		super(Gui, self).__init__()
		self.height = 0
		self.width = 0
		self.backgroundColor = None
		self.mouseVisible = False
		self.fields = {}
		self.pictureArea = None
		self.name = name
		self.timeField = None
		self.lyricField = None
		self.picField = None

	def initFields(self):
		for field in self.fields:
			if hasattr(field, "initFields"):
				field.initFields()

	def grabXMLData(self, xml):
		super(Gui, self).grabXMLData(xml)
		fields = xml.xpath('fields')
		for child in fields[0]:
			f = dacapo.ui.blitfield.BlitField(child.tag)
			f.grabXMLData(child)
			if f.test():
				self.fields[child.tag] = f
				if f.isTimeField:
					self.timeField = f
				if f.isLyricField:
					self.lyricField = f
				if f.isPicField:
					self.picField = f

	def getXMLData(self):
		from lxml import etree
		root = super(Gui, self).getXMLData()
		fields = etree.SubElement(root, 'fields', type='dict')
		for k,f in self.fields.iteritems():
			fields.append(f.getXMLData())
		return root

	def printValues(self):
		print('\nGui: {!s} {!s}x{!s} Background: {!s} Maus: {!s}'.format(self.name, self.height, self.width, self.backgroundColor, self.mouseVisible))
		self.lyricField.printValues()
		for k,f in self.fields.iteritems():
			f.printValues()

	def getRGBABackgroundColor(self):
		from gi.repository import Gdk
		color = Gdk.RGBA()
		colorRGB = []
		for c in self.backgroundColor:
			colorRGB.append(str(c))
		parseThis = 'rgb(' + ','.join(colorRGB) + ')'
		color.parse(parseThis)
		return color

	def setVars(self):
		extendvars = {
			'height': {
				'target': 'height',
				'type': 'int',
			},
			'width': {
				'target': 'width',
				'type': 'int',
			},
			'backgroundColor': {
				'target': 'backgroundColor',
				'type': 'color',
			},
			'mouseVisible': {
				'target': 'mouseVisible',
				'type': 'boolean',
			},
		}
		self.vars.update(extendvars)

