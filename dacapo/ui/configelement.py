#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
from lxml import etree

class ConfigElement(object):
	BOOLS = ['true', '1', 't', 'y', 'yes', 'yeah', 'yarp', 'yup', 'certainly', 'uh-huh']

	def __init__(self):
		super(ConfigElement, self).__init__()

	def checkBool(self, test):
		res = True if test.lower() in self.BOOLS else False
		return res

	def grabXMLData(self, xml):
		d = self.__dict__
		for child in xml:
			elementTyp = child.get("type", "str")
			if elementTyp == "int" :
				d[child.tag] = int(child.text)
			elif elementTyp == "float" :
				d[child.tag] = float(child.text)
			elif elementTyp == "tuple" :
				d[child.tag] = tuple(child.text)
			elif elementTyp == "color" :
				tmp = tuple(child.text.split(','))
				color = (int(tmp[0]), int(tmp[1]), int(tmp[2]))
				d[child.tag] = tuple(color)
			elif elementTyp == "boolean" :
				d[child.tag] = self.checkBool(child.text)
			else :
				pass

	def getXMLData(self):
		root = etree.Element(self.name, type='dict')
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				attrType = 'text'
				if attr == 'backgroundColor' or attr == 'fontColor':
					attrType = 'color'
				elif isinstance(attr, int):
					attrType = 'int'
				elif isinstance(attr, bool):
					attrType = 'boolean'
				elif isinstance(attr, float):
					attrType = 'float'
				elif isinstance(attr, object):
					getXML = getattr(attr, 'getXMLData', None)
					if callable(getXML):
						etree.SubElement(root, getXML())
						continue
				subel = etree.SubElement(root, attr, type=attrType)
				subel.text = str(value)
				print('Attribut {!s} type {!s} mit Wert {!s} gefunden'.format(attr, attrType, value))
		return root


	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				yield attr, value