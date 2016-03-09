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
from dacapo.config.gui.tabs import *

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
import pygame
from dacapo.config import readconfig

class Configurator(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title=_("dacapo configurator"))
		self.set_border_width(3)

		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Window settings
		self.page_window = GuiTab('window')
		self.notebook.append_page(self.page_window, Gtk.Label(_("GUI Window")))


		# 2nd tab -> Window-Fields
		self.page_fields_window = FieldTab('window')
		self.notebook.append_page(self.page_fields_window, Gtk.Label(_("Window fields")))

		# 3rd tab -> Fullscreen settings
		self.page_fullscreen = GuiTab('fullscreen')
		self.notebook.append_page(self.page_fullscreen, Gtk.Label(_("GUI Fullscreen")))

		# 4th tab -> Fullscreen-Fields
		self.page_fields_fullscreen = FieldTab('fullscreen')
		self.notebook.append_page(self.page_fields_fullscreen, Gtk.Label(_("Fullscreen fields")))

		self.page_metadata = Gtk.Box()
		self.page_metadata.set_border_width(10)
		self.page_metadata.add(Gtk.Label(_('Metadata-Settings!')))
		self.notebook.append_page(self.page_metadata, Gtk.Label(_("Metadata")))
		self.page_debug = Gtk.Box()
		self.page_debug.set_border_width(10)
		self.page_debug.add(Gtk.Label(_('Audio & Debug-Settings!')))
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