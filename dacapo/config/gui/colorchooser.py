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

class MyColorChooserWidget(Gtk.ColorChooserWidget):

	def __init__(self):
		super(MyColorChooserWidget, self).__init__()
		self.set_property("show-editor", True)
		box = None
		self.print_attr(self)

				##if type(attr).__name__ == "SearchEntry":
		# members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]
		# print members
		provider = Gtk.CssProvider()
		provider.load_from_data('.entry { background: white; }')
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.set_use_alpha(False)

		self.connect("color-activated", self.color_activated)

	def print_attr(self, box):
		for attr in box:
			if str.lower(type(attr).__name__) == "box":
				print('\n\t {!s}'.format(type(attr).__name__))
				self.print_attr(attr)
			elif str.lower(type(attr).__name__) == "grid":
				print('\n\t {!s}'.format(type(attr).__name__))
				self.print_attr(attr)
			elif str.lower(type(attr).__name__) == "gtk.coloreditor":
				print('\n\t {!s}'.format(type(attr).__name__))
				self.print_attr(attr)
			else:
				print('Colorchooser attr-Type {!s}'.format(type(attr).__name__))

	def color_activated(colorchooserwidget, color):
		red = (color.red * 255)
		green = (color.green * 255)
		blue = (color.blue * 255)

		print("Hex: #%02x%02x%02x" % (red, green, blue))

	def set_rgba(self, color):
		super(MyColorChooserWidget, self).set_rgba(color)
		self.color_activated(color)