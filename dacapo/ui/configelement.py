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
		self.vars = {
			'name': {
				'target': 'name',
				'type': 'text',
			},
		}
		self.setVars()

	def setVars(self):
		pass

	def test(self):
		return False

	def checkBool(self, test):
		res = True if str(test).lower() in self.BOOLS else False
		return res

	def grabXMLData(self, xml, printme=False):
		d = self.__dict__
		for child in xml:
			name = child.tag
			value = child.text
			if not self.vars.has_key(name):
				continue
			target = self.vars.get(name)['target']
			elementTyp = self.vars.get(name)['type']
			if printme:
				print("Name: {!s} Value: {!s} Target: {!s} Type: {!s}".format(name, value, target, elementTyp))
			if elementTyp == "int" :
				d[target] = int(value)
			elif elementTyp == "float" :
				d[target] = float(value)
			elif elementTyp == "tuple" :
				d[target] = tuple(value)
			elif elementTyp == "color" :
				tmp = tuple(value.split(','))
				color = (int(tmp[0]), int(tmp[1]), int(tmp[2]))
				d[target] = tuple(color)
			elif elementTyp == "boolean" :
				d[target] = self.checkBool(value)
			else :
				d[target] = str(value)

	def getVarsName(self, name):
		for var in self.vars:
			if not self.vars[var].has_key('target'):
				continue
			if self.vars[var]['target'] == name:
				return var
		return False

	def getXMLData(self):
		root = etree.Element(self.name, type='dict')
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				attrType = 'text'
				attrName = self.getVarsName(attr)
				if attrName != False:
					if self.vars[attrName].has_key('type'):
						attrType = self.vars[attrName]['type']
					subel = etree.SubElement(root, attrName, type=attrType)
					subel.text = str(value)
		return root

	def addXMLData(self, root):
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				attrType = 'text'
				attrName = self.getVarsName(attr)
				if attrName != False and not (attr == 'name' and value == ''):
					if self.vars[attrName].has_key('type'):
						attrType = self.vars[attrName]['type']
					subel = etree.SubElement(root, attrName, type=attrType)
					subel.text = str(value)
		return root

	def setValue(self, key, value):
		if not self.vars.has_key(key):
			return
		d = self.__dict__
		elementTyp = self.vars.get(key)['type']
		target = self.vars.get(key)['target']
		if elementTyp == "int":
			d[target] = int(value)
		elif elementTyp == "float":
			d[target] = float(value)
		elif elementTyp == "tuple":
			d[target] = tuple(value)
		elif elementTyp == "color":
			r = int(round(value.red * 255, 0))
			b = int(round(value.blue * 255, 0))
			g = int(round(value.green * 255, 0))
			color = (r, g, b)
			d[target] = tuple(color)
			print('New color {!s}'.format(d[target]))
		elif elementTyp == "boolean":
			d[target] = self.checkBool(value)
		else:
			d[target] = str(value)

	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				yield attr, value