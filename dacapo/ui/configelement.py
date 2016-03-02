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


class ConfigElement(object):
	BOOLS = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']

	def __init__(self):
		super(ConfigElement, self).__init__()

	def checkBool(self, test):
		res = True if test.lower() in self.BOOLS else False
		return res

	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			if not callable(attr) and not attr.startswith("__"):
				yield attr, value