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
from dacapo.config.gui.colorchooser import MyColorChooserWidget

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
		self.get_attr(self)

		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.colorchooser = MyColorChooserWidget()
		self.colorchooser.connect_color_activated(self.color_cb)

		box.add(self.colorchooser)
		self.add(box)
		# connect signal from the font chooser to the callback function
		self.connect("notify::font", self.font_cb)
		# self.printValues()

	def get_attr(self, obj):
		for attr in obj:
			if str.lower(type(attr).__name__) == "box":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "grid":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "gtk.coloreditor":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "gtkcoloreditor":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "stack":
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "overlay":
				self.colorEditor = attr
				self.get_attr(attr)
			elif str.lower(type(attr).__name__) == "searchentry":
				# print('SearchEntry gefunden \n\tName: {!s} \n\tType:{!s} \n\tObject: {!s}'.format(type(attr).__name__, type(attr), attr))
				self.searchEntry = attr
				self.searchEntry.set_tooltip_text(_("Search here for a font name."))
			elif str.lower(type(attr).__name__) == "entry":
				# print('Entry gefunden \n\tName: {!s} \n\tType:{!s} \n\tObject: {!s}'.format(type(attr).__name__, type(attr), attr))
				self.entry = attr
				self.entry.set_tooltip_text(_("Change here the text of the preview."))
			else:
				continue

	# callback function:
	def font_cb(self, event, user_data):
		# print in the terminal
		#print("You chose the font " + self.get_font())
		return

	# callback function:
	def color_cb(self, event, user_data):
		self.setFGcolor(self.colorchooser.get_rgba())
		return

	def set_font(self, fontName, fontWeight, fontStyle, fontSize):
		from gi.repository import Pango
		pangoFontDesc = Pango.FontDescription()
		pangoFontDesc.set_family(fontName)
		pangoFontDesc.set_size(fontSize * 1024)
		try:
			w = getattr(Pango.Weight, fontWeight.upper())
			pangoFontDesc.set_weight(w)
		except: pass
		try:
			s = getattr(Pango.Style, fontStyle.upper())
			pangoFontDesc.set_style(s)
		except: pass
		super(MyFontChooserWidget, self).set_font_desc(pangoFontDesc)
		return
		super(MyFontChooserWidget, self).set_font('{!s} {!s} {!s}'.format(fontName, fontFace, fontSize))
		self.searchEntry.set_text('{!s} {!s}'.format(fontName, fontFace))
		return

	def setBGcolor(self, type):
		g = CONFIG.gui[type]
		#print('Background-Color: {!s}'.format(g.getRGBABackgroundColor().to_string()))
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

