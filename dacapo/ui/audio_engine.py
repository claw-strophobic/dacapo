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

class AudioEngine(dacapo.ui.configelement.ConfigElement):

	def __init__(self, name):
		super(AudioEngine, self).__init__()
		self.fields = {}
		self.name = name

	def setVars(self):
		extendvars = {
			'sinkType': {
				'target': 'sinkType',
				'type': 'text',
			},
			'replayGain': {
				'target': 'replayGain',
				'type': 'boolean',
			},
			'gapless': {
				'target': 'gapless',
				'type': 'boolean',
			},
		}
		self.vars.update(extendvars)

	def printValues(self):
		print("\n\nHere comes the audio_engine:\n")
		for k,f in self.fields.iteritems():
			f.printValues()



