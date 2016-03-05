#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
from dacapo.config import readconfig

t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

CONFIG = readconfig.getConfigObject()

class MyFontChooserWidget(Gtk.FontChooserWidget):

	def __init__(self):
		super(MyFontChooserWidget, self).__init__()
		provider = Gtk.CssProvider()
		provider.load_from_data('.entry { background: white; }')
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		# a font chooser
		# self.font_chooser = Gtk.FontChooserWidget()
		# a default fontfield.font.fontSize
		# self.font_chooser.set_font("Sans")
		# a text to preview the font
		#self.font_chooser.set_preview_text(
		#	"This is an example of preview text!")
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
				if type(attr).__name__ == "Entry":
					self.entry = attr

		## print(dir(Gtk.FontChooserWidget))
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.colorchooser = Gtk.ColorChooserWidget(show_editor=True)
		box.add(self.colorchooser)
		self.add(box)

		##self.entry_desc.connect("changed", self.on_entry_desc_changed)
		##vbox.pack_start(self.entry_desc, True, True, 0)

		# connect signal from the font chooser to the callback function
		self.connect("notify::font", self.font_cb)
		# self.printValues()

		# add the font chooser to the window
		# self.add(self.font_chooser)


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

	def setFGcolor(self, field):
		self.colorchooser.set_rgba(field.font.getRGBAColor())
		self.entry.override_color(Gtk.StateFlags.NORMAL, field.font.getRGBAColor())
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


class Configurator(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title=_("dacapo configurator"))
		self.set_border_width(3)

		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		self.page_window = Gtk.Box()
		vbox = Gtk.VBox()
		self.page_window.set_border_width(10)
		vbox.add(Gtk.Label(_('Window-Settings')))
		## add fields
		font_chooser = MyFontChooserWidget()
		self.window_fields = self.get_field_combo('window', font_chooser)
		vbox.add(self.window_fields)
		vbox.add(font_chooser)
		self.page_window.add(vbox)
		self.notebook.append_page(self.page_window, Gtk.Label(_("GUI Window")))

		self.page_fullscreen = Gtk.Box()
		vbox = Gtk.VBox()
		self.page_fullscreen.set_border_width(10)
		vbox.add(Gtk.Label(_('Fullscreen-Settings')))
		## add fields
		font_chooser = MyFontChooserWidget()
		self.fullscreen_fields = self.get_field_combo('fullscreen', font_chooser)
		vbox.add(self.fullscreen_fields)
		vbox.add(font_chooser)
		self.page_fullscreen.add(vbox)
		self.notebook.append_page(self.page_fullscreen, Gtk.Label(_("GUI Fullscreen")))

		self.page_metadata = Gtk.Box()
		self.page_metadata.set_border_width(10)
		self.page_metadata.add(Gtk.Label('Metadata-Settings!'))
		self.notebook.append_page(self.page_metadata, Gtk.Label(_("Metadata")))
		self.page_debug = Gtk.Box()
		self.page_debug.set_border_width(10)
		self.page_debug.add(Gtk.Label('Audio & Debug-Settings!'))
		self.notebook.append_page(self.page_debug, Gtk.Label(_("Audio & Debug")))


		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		self.page2.add(Gtk.Label('A page with an image for a Title.'))
		self.notebook.append_page(
			self.page2,
			Gtk.Image.new_from_icon_name(
				"help-about",
				Gtk.IconSize.MENU
			)
		)

	def get_field_combo(self, type, font_chooser):
		type_store = Gtk.ListStore(str, object)
		g = CONFIG.gui[type]
		for key in g.fields:
			type_store.append([key, g.fields[key]])
		field_combo = Gtk.ComboBox.new_with_model(type_store)
		field_combo.type = type
		field_combo.font_chooser = font_chooser
		renderer = Gtk.CellRendererText()
		field_combo.pack_start(renderer, True)
		field_combo.add_attribute(renderer, 'text', 0)
		field_combo.connect("changed", self.on_field_combo_changed)
		field_combo.set_entry_text_column(0)
		return field_combo

	def on_field_combo_changed(self, combo):
		combo_iter = combo.get_active_iter()
		if not combo_iter:
			return
		model = combo.get_model()
		fieldName = model.get_value(combo_iter, 0)
		print("You chose the field " + fieldName)
		field = model.get_value(combo_iter, 1)
		font_chooser = combo.font_chooser
		font_chooser.setBGcolor(combo.type)
		font = '{!s} {!s}'.format(field.font.fontName, field.font.fontSize)
		print("Field-Font " + font + " fontColor: " + field.font.getRGBAColor().to_string())
		font_chooser.set_font(field.font.fontName, field.font.fontSize)
		font_chooser.setFGcolor(field)


win = Configurator()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()