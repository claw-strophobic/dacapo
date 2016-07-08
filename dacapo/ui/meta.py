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
from dacapo.ui import condition
from lxml import etree

class Meta(dacapo.ui.configelement.ConfigElement):

	def __init__(self, name):
		super(Meta, self).__init__()
		self.fields = {}
		self.name = name

	def grabXMLData(self, xml):
		meta = xml.xpath('gui/metaData')
		for child in meta[0]:
			elementTyp = child.get("type", "str")
			if elementTyp == "cond":
				cond = condition.Condition(child.tag)
				cond.grabXMLData(child)
				if cond.test():
					self.fields[child.tag] = cond

	def getXMLData(self):
		root = super(Meta, self).getXMLData()
		fields = etree.SubElement(root, 'metaData', type='dict')
		for k,f in self.fields.iteritems():
			fields.append(f.getXMLData())
		return root

	def printValues(self):
		print("\n\nHier come the conditions:\n")
		for k,f in self.fields.iteritems():
			f.printValues()



