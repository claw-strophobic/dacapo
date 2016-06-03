#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
from dacapo.config.gui import *
import pprint

class MyColorChooserWidget(Gtk.ColorChooserWidget):

	def __init__(self):
		super(MyColorChooserWidget, self).__init__()
		self.set_property("show-editor", True)
		self.colorEditor = None
		self.entryField = None
		self.get_attr(self)
		# self.print_attr(self.colorEditor)
		# pprint.pprint(self.my_even_fancier_attribute_getter(self.colorEditor))
		if (self.entryField is not None):
			self.entryField.connect("changed", self.color_activated)
		provider = Gtk.CssProvider()
		provider.load_from_data('.entry { background: white; }')
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.set_use_alpha(False)

		self.connect("color-activated", self.color_activated)

	def color_activated(self, entry):
		color = self.get_rgba()

	def connect_color_activated(self, method):
		self.entryField.connect("changed", method, self)

	def get_attr(self, obj):
		for attr in obj:
			if str.lower(type(attr).__name__) == "box":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "grid":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "gtk.coloreditor":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "overlay":
				self.colorEditor = attr
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "entry":
				self.entryField = attr

	def my_even_fancier_attribute_getter(self, obj):
		return [(attr, value) for attr, value in obj.__dict__.items() if not callable(value)]
