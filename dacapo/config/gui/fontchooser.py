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

class MyFontChooserWidget(Gtk.FontChooserWidget):

	def __init__(self):
		super(MyFontChooserWidget, self).__init__()
		provider = Gtk.CssProvider()
		provider.load_from_data('.entry { background: white; }')
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		self.set_show_preview_entry(True)
		self.grid = None
		self.entry = None
		for attr in self:
			self.grid = attr
			break
		if self.grid <> None:
			for attr in self.grid:
				if type(attr).__name__ == "SearchEntry":
					self.searchEntry = attr
					self.searchEntry.set_tooltip_text(_("Search here for a font name."))
				if type(attr).__name__ == "Entry":
					self.entry = attr
					self.entry.set_tooltip_text(_("Change here the text of the preview."))

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.colorchooser = Gtk.ColorChooserWidget(show_editor=True)
		box.add(self.colorchooser)
		self.add(box)
		# connect signal from the font chooser to the callback function
		self.connect("notify::font", self.font_cb)
		# self.printValues()


	# callback function:
	def font_cb(self, event, user_data):
		# print in the terminal
		print("You chose the font " + self.get_font())
		return

	def set_font(self, fontName, fontSize):
		super(MyFontChooserWidget, self).set_font('{!s} {!s}'.format(fontName, fontSize))
		self.searchEntry.set_text(fontName)
		return

	def setBGcolor(self, type):
		g = CONFIG.gui[type]
		print('Background-Color: {!s}'.format(g.getRGBABackgroundColor().to_string()))
		self.entry.override_background_color(Gtk.StateFlags.NORMAL, g.getRGBABackgroundColor())
		return

	def setFGcolor(self, color):
		self.colorchooser.set_rgba(color)
		self.entry.override_color(Gtk.StateFlags.NORMAL, color)
		self.colorchooser.set_property("show-editor", True)
		return


	def printValues(self):
		print("Los gehts...")
		for attr in self:
			print('Field: {!s}'.format(attr.__dict__))
			grid = attr
			break
		for attr in grid:
			print('Field: {!s}'.format(type(attr).__name__))
			print('Field: {!s}'.format(type(attr).__dict__))
		return

