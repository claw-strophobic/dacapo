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
import pygame
import gettext
t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

class MyFontChooserWidget(Gtk.FontChooserWidget):

    def __init__(self):
		super(MyFontChooserWidget, self).__init__()

		# a font chooser
		# self.font_chooser = Gtk.FontChooserWidget()
		# a default font
		# self.font_chooser.set_font("Sans")
		# a text to preview the font
		#self.font_chooser.set_preview_text(
		#	"This is an example of preview text!")

		# connect signal from the font chooser to the callback function
		self.connect("notify::font", self.font_cb)

		# add the font chooser to the window
		# self.add(self.font_chooser)

    # callback function:
    def font_cb(self, event, user_data):
		# print in the terminal
        print("You chose the font " + self.get_font())


class Configurator(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title=_("dacapo configurator"))
		pygame.init()
		fonts = pygame.font.get_fonts()
		for font in fonts:
			print font
		self.set_border_width(3)
		self.font_chooser = MyFontChooserWidget()

		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		self.page_window = Gtk.Box()
		self.page_window.set_border_width(10)
		self.page_window.add(Gtk.Label('Window-Settings!'))
		self.page_window.add(self.font_chooser)
		self.notebook.append_page(self.page_window, Gtk.Label(_("GUI Window")))
		self.page_fullscreen = Gtk.Box()
		self.page_fullscreen.set_border_width(10)
		self.page_fullscreen.add(Gtk.Label('Fullscreen-Settings!'))
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
win = Configurator()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()