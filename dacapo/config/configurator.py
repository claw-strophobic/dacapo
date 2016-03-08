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

from dacapo.ui.field import Field
import dacapo.ui.interface_blitobject
import dacapo.ui.blitobject

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
import pygame
from dacapo.config import readconfig

t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

CONFIG = readconfig.getConfigObject()
ALIGNH = {
		"center": _("center"),
		"left": _("left"),
		"right": _("right"),
	}

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


class PreviewTab(Gtk.Box, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		self.type = type
		self.screen = None

	def on_preview(self, *data):
		g = CONFIG.gui[self.type]
		resolution = (g.width, g.height)
		FPS = 30
		fpsClock = pygame.time.Clock()
		fpsClock.tick(FPS)
		try:
			if self.type == "fullscreen":
				self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
			else:
				self.screen = pygame.display.set_mode(resolution)
		except:
			print(pygame.get_error())
			return

		try: self.doFillBackground(self.screen, g.backgroundColor, True)
		except:
			print(pygame.get_error())
			return
		obj = self.getBlitObject()
		self.doBlitObject(self.screen, obj, True)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
						pygame.quit()
						return
				else:
					pass



class BackgroundTab(Gtk.Box):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		g = CONFIG.gui[type]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		vbox.add(Gtk.Label(_('Pictures- & Background-Settings!')))
		self.colorchooser = Gtk.ColorChooserWidget(show_editor=True)
		self.colorchooser.set_rgba(g.getRGBABackgroundColor())
		self.colorchooser.set_property("show-editor", True)
		vbox.add(self.colorchooser)
		self.add(vbox)


class FieldTab(PreviewTab):

	def __init__(self, type):
		super(FieldTab, self).__init__(type)
		self.field = None
		g = CONFIG.gui[type]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		self.set_border_width(10)
		vbox.add(Gtk.Label(_('Window-Fields-Settings')))
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)

		## add fields
		font_chooser = MyFontChooserWidget()

		self.fields = self.get_field_combo(type, font_chooser)
		self.fields.set_tooltip_text(_("Select an existing field here."))
		labelField = Gtk.Label(_('Field:'))
		grid.add(labelField)
		grid.attach_next_to(self.fields, labelField, Gtk.PositionType.RIGHT, 1, 1)
		self.prev_button = Gtk.Button(_("Preview"))
		self.prev_button.set_sensitive(False)
		self.prev_button.connect('clicked', self.on_preview)
		self.prev_button.set_tooltip_text(_("Click here to see a preview of this field."))

		grid.attach_next_to(self.prev_button, self.fields, Gtk.PositionType.RIGHT, 1, 1)

		vbox.add(grid)
		vbox.add(font_chooser)
		self.add(vbox)

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
		field = model.get_value(combo_iter, 1)
		font_chooser = combo.font_chooser
		font_chooser.setBGcolor(combo.type)
		font = '{!s} {!s}'.format(field.font.fontName, field.font.fontSize)
		## print(u"Field-Font " + font + " fontColor: " + field.font.getRGBAColor().to_string())
		font_chooser.set_font(field.font.fontName, field.font.fontSize)
		font_chooser.setFGcolor(field.font.getRGBAColor())
		self.field = field
		self.prev_button.set_sensitive(True)

	def getBlitObject( self ):
		if self.field is None:
			return None
		else:
			self.field.content = self.field.getReplacedContent()
			print(u"Preview for field {!s} with example-content: {!s}".format(self.field.name, self.field.content))
			return self.field.getBlitObject()

class LyricfontTab(Gtk.Box):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		g = CONFIG.gui[type]
		self.set_border_width(10)
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)
		vbox = Gtk.VBox()
		vbox.add(Gtk.Label(_('Lyric-Font-Settings!')))
		labelPos = Gtk.Label(_('Lyric position (vertical)'))
		grid.add(labelPos)
		adjustment = Gtk.Adjustment(int(g.lyricFont.posV), 0, int(g.height), 1, 10, 0)
		self.pos_spinbutton = Gtk.SpinButton()
		self.pos_spinbutton.set_adjustment(adjustment)
		self.pos_spinbutton.set_value(int(g.lyricFont.posV))
		self.pos_spinbutton.set_tooltip_text(_("Set here the vertical position of the lyric."))
		grid.attach_next_to(self.pos_spinbutton,labelPos, Gtk.PositionType.RIGHT, 1, 1)
		## print("height: {!s} posV: {!s}".format(g.height, self.pos_spinbutton.get_value()))

		labelAlign = Gtk.Label(_('Lyric align (horizontal)'))
		grid.attach_next_to(labelAlign, labelPos, Gtk.PositionType.BOTTOM, 1, 1)
		type_store = Gtk.ListStore(str, str)
		for key in ALIGNH:
			type_store.append([key, ALIGNH[key]])
		align_combo = Gtk.ComboBox.new_with_model(type_store)
		align_combo.set_tooltip_text(_("Set here the horizontal align of the lyric."))
		renderer = Gtk.CellRendererText()
		i = 0
		for row in type_store:
			if (row[0] == g.lyricFont.alignH):
				align_combo.set_active(i)
			i += 1

		# align_combo.set_active(type_store.get_iter(g.lyricFont.alignH))
		align_combo.pack_start(renderer, True)
		align_combo.add_attribute(renderer, 'text', 1)
		## align_combo.connect("changed", self.on_name_combo_changed)
		align_combo.set_entry_text_column(1)
		grid.attach_next_to(align_combo, labelAlign, Gtk.PositionType.RIGHT, 1, 1)

		font_chooser = MyFontChooserWidget()
		font_chooser.setBGcolor(type)
		font_chooser.setFGcolor(g.lyricFont.getRGBAColor())
		font_chooser.set_font(g.lyricFont.fontName, g.lyricFont.fontSize)
		vbox.add(grid)

		vbox.add(font_chooser)
		self.add(vbox)
		pygame.init()


class GuiTab(Gtk.Box):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_background = BackgroundTab(type)
		self.notebook.append_page(self.page_background, Gtk.Label(_("Pictures & Background")))

		# 2nd tab -> Lyricfont settings
		self.page_font = LyricfontTab(type)
		self.notebook.append_page(self.page_font, Gtk.Label(_("Lyric-Font")))


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