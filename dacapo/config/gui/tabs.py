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
from dacapo.config.gui.fontchooser import MyFontChooserWidget
from dacapo.config.gui.colorchooser import MyColorChooserWidget

class PreviewTab(Gtk.Box, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		self.type = type
		self.screen = None

	def on_preview(self, *data):
		import types
		import operator
		g = CONFIG.gui[self.type]
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.type)
		resolution = (g.width, g.height)
		FPS = 30
		fpsClock = pygame.time.Clock()
		fpsClock.tick(FPS)
		print("going to set pygame.display to: {!s}".format(self.type))
		try:
			if self.type == "fullscreen":
				self.screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
			else:
				self.screen = pygame.display.set_mode(resolution)
		except:
			print(pygame.get_error())
			return

		print("going to fill the background to: {!s}".format(g.backgroundColor))
		try: self.doFillBackground(self.screen, g.backgroundColor, True)
		except:
			print(pygame.get_error())
			return
		print("going to get blit objeckt: ")
		obj = self.getBlitObject()
		print("going to blit objeckt-type: {!s}".format(type(obj)))
		if isinstance(obj, types.ListType):
			sorted_x = sorted(obj, key=operator.attrgetter('zIndex'))
			for o in sorted_x:
				self.doBlitObject(self.screen, o, True)
		else:
			print("doBlitObject: {!s}".format(type(obj)))
			self.doBlitObject(self.screen, obj, True)
		print("going to loop: ")
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



class BackgroundTab(PreviewTab):

	def __init__(self, type):
		super(BackgroundTab, self).__init__(type)
		s = Gdk.Screen.get_default()
		g = CONFIG.gui[type]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)

		if type == 'window':
			labelWidth = Gtk.Label(_('Window width'))
			labelHeight = Gtk.Label(_('Window height'))
		else:
			labelWidth = Gtk.Label(_('Fullscreen width'))
			labelHeight = Gtk.Label(_('Fullscreen height'))
		labelDummy = Gtk.Label(' ')

		grid.add(labelWidth)
		adjustment = Gtk.Adjustment(int(g.width), 0, int(s.get_width()), 1, 10, 0)
		self.width_spinbutton = Gtk.SpinButton()
		self.width_spinbutton.set_adjustment(adjustment)
		self.width_spinbutton.set_value(int(g.width))
		self.width_spinbutton.set_tooltip_text(_("Set here the pixel width of the display.") + " (max {!s})".format(s.get_width()))
		self.width_spinbutton.connect('value-changed', self.onValueChanged, 'width')
		grid.attach_next_to(self.width_spinbutton,labelWidth, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(labelHeight, labelWidth, Gtk.PositionType.BOTTOM, 1, 1)
		adjustment = Gtk.Adjustment(int(g.height), 0, int(s.get_height()), 1, 10, 0)
		self.height_spinbutton = Gtk.SpinButton()
		self.height_spinbutton.set_adjustment(adjustment)
		self.height_spinbutton.set_value(int(g.height))
		self.height_spinbutton.set_tooltip_text(_("Set here the pixel height of the display." + " (max {!s})".format(s.get_height())))
		self.height_spinbutton.connect('value-changed', self.onValueChanged, 'height')
		grid.attach_next_to(self.height_spinbutton,labelHeight, Gtk.PositionType.RIGHT, 1, 1)

		labelMouseVisible = Gtk.Label(_('Show the mouse cursor'))
		grid.attach_next_to(labelMouseVisible, labelHeight, Gtk.PositionType.BOTTOM, 1, 1)
		self.mouseVisible = Gtk.CheckButton()
		self.mouseVisible.connect("toggled", self.onToggled, 'mouseVisible')
		grid.attach_next_to(self.mouseVisible, labelMouseVisible, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(labelDummy, labelMouseVisible, Gtk.PositionType.BOTTOM, 1, 7)

		labelBackground = Gtk.Label(_('Background colour'))
		grid.attach_next_to(labelBackground, self.width_spinbutton, Gtk.PositionType.RIGHT, 1, 1)
		self.colorchooser = MyColorChooserWidget()
		self.colorchooser.set_rgba(g.getRGBABackgroundColor())
		self.colorchooser.connect_color_activated(self.onColorSet)
		grid.attach_next_to(self.colorchooser, labelBackground, Gtk.PositionType.BOTTOM, 1, 10)

		self.prev_button = Gtk.Button(_("Preview"))
		self.prev_button.set_sensitive(True)
		self.prev_button.connect('clicked', self.on_preview)
		self.prev_button.set_tooltip_text(_("Click here to see a preview of this field."))
		grid.attach_next_to(self.prev_button, labelDummy, Gtk.PositionType.BOTTOM, 1, 1)
		vbox.add(grid)
		self.add(vbox)

	def getBlitObject( self ):
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.type)
		if audio is None:
			return None
		else:
			a = list()
			CONFIG.readConfig()
			g = CONFIG.gui[self.type]
			g.initFields()
			for field in g.fields:
				if not g.fields[field].isPicField and hasattr(g.fields[field], 'zIndex'):
					print('Adding field {!s}'.format(g.fields[field].name))
					a.append(g.fields[field].getBlitObject())
			a.append(audio.getCover())
			return a

	def onColorSet( self, obj, colorchooser):
		color = self.colorchooser.get_rgba()
		g = CONFIG.gui[self.type]
		g.setValue('backgroundColor', color)


	def onToggled(self, obj, data):
		v = obj.get_active()
		print('New {!s}: {!s}'.format(data, v))
		g = CONFIG.gui[self.type]
		g.setValue(data, v)

	def onValueChanged(self, obj, data):
		v = obj.get_value_as_int()
		print('New {!s}: {!s}'.format(data, v))
		g = CONFIG.gui[self.type]
		g.setValue(data, v)


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
		self.font_chooser = MyFontChooserWidget()
		self.notebook = Gtk.Notebook()

		self.fields = self.get_field_combo(type, self.font_chooser)
		self.fields.set_tooltip_text(_("Select an existing field here."))
		labelField = Gtk.Label(_('Field:'))
		grid.add(labelField)
		grid.attach_next_to(self.fields, labelField, Gtk.PositionType.RIGHT, 1, 1)
		self.prev_button = Gtk.Button(_("Preview"))
		self.prev_button.set_sensitive(False)
		self.prev_button.connect('clicked', self.on_preview)
		self.prev_button.set_tooltip_text(_("Click here to see a preview of this field."))
		grid.attach_next_to(self.prev_button, self.fields, Gtk.PositionType.RIGHT, 1, 1)

		self.apply_button = Gtk.Button(_("apply"))
		self.apply_button.set_sensitive(False)
		self.apply_button.connect('clicked', self.on_applied)
		self.apply_button.set_tooltip_text(_("Click here to see apply the settings of this field."))
		grid.attach_next_to(self.apply_button, self.prev_button, Gtk.PositionType.RIGHT, 1, 1)

		vbox.add(grid)
		page_font = FieldFontTab(self)
		self.notebook.append_page(page_font, Gtk.Label(_("Font settings")))
		page_pos = FieldPosTab(self)
		self.notebook.append_page(page_pos, Gtk.Label(_("Position settings")))
		vbox.add(self.notebook)
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
		self.field = field
		font_chooser = combo.font_chooser
		font_chooser.setBGcolor(combo.type)
		font = '{!s} {!s}'.format(field.font.name, field.font.fontSize)
		## print(u"Field-Font " + font + " fontColor: " + field.font.getRGBAColor().to_string())
		font_chooser.set_font(field.font.name, field.font.fontSize)
		font_chooser.setFGcolor(field.font.getRGBAColor())
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		self.apply_button.set_sensitive(True)
		if audio is not None:
			self.prev_button.set_sensitive(True)

	def getBlitObject( self ):
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		if audio is None or self.field is None:
			return None
		else:
			#self.field.content = self.field.getReplacedContent()
			#print(u"Preview for field {!s} with example-content: {!s}".format(self.field.name, self.field.content))
			return self.field.getBlitObject()

	def on_applied(self, *data):
		i = self.notebook.get_n_pages()
		for x in range(0, i):
			p = self.notebook.get_nth_page(x)
			print self.notebook.get_tab_label_text(p)
			p.apply()


class FieldFontTab(Gtk.Box):

	def __init__(self, fieldTab):
		super(FieldFontTab, self).__init__()
		self.fieldTab = fieldTab
		self.set_border_width(10)
		vbox = Gtk.VBox()
		self.set_border_width(10)
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)

		## add fields
		self.fieldTab.font_chooser.colorchooser.connect_color_activated(self.onColorChanged)

		vbox.add(grid)
		vbox.add(self.fieldTab.font_chooser)
		self.add(vbox)

	def onColorChanged(self, obj, colorchooser):
		self.color = colorchooser.get_rgba()


	def apply(self):
		color = self.fieldTab.font_chooser.colorchooser.get_rgba()
		fontFace = self.fieldTab.font_chooser.get_font_face()
		fontFamily = self.fieldTab.font_chooser.get_font_family()
		font = fontFace.get_face_name()
		print(font)
		font = fontFamily.get_name()
		print(font)
		size = self.fieldTab.font_chooser.get_font_size() / 1024
		print(font + " Size: " + str(size))
		self.fieldTab.field.font.setValue('font', font)
		self.fieldTab.field.font.setValue('fontSize', size)
		self.fieldTab.field.font.setValue('fontColor', color)

class FieldPosTab(Gtk.Box):

	def __init__(self, fieldTab):
		super(FieldPosTab, self).__init__()
		self.fieldTab = fieldTab
		self.set_border_width(10)
		vbox = Gtk.VBox()
		self.set_border_width(10)
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)
		g = CONFIG.gui[self.fieldTab.type]

		labelWidth = Gtk.Label(_('Maximal field width'))
		labelHeight = Gtk.Label(_('Maximal field height'))
		labelDummy = Gtk.Label(' ')

		grid.add(labelWidth)
		adjustment = Gtk.Adjustment(int(g.width), 0, int(g.width), 1, 10, 0)
		self.width_spinbutton = Gtk.SpinButton()
		self.width_spinbutton.set_adjustment(adjustment)
		self.width_spinbutton.set_value(int(g.width))
		self.width_spinbutton.set_tooltip_text(_("Set here the pixel width of the display.") + " (max {!s})".format(g.width))
		grid.attach_next_to(self.width_spinbutton,labelWidth, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(labelHeight, labelWidth, Gtk.PositionType.BOTTOM, 1, 1)
		adjustment = Gtk.Adjustment(int(g.height), 0, int(g.height), 1, 10, 0)
		self.height_spinbutton = Gtk.SpinButton()
		self.height_spinbutton.set_adjustment(adjustment)
		self.height_spinbutton.set_value(int(g.height))
		self.height_spinbutton.set_tooltip_text(_("Set here the pixel height of the display.") + " (max {!s})".format(g.height))
		grid.attach_next_to(self.height_spinbutton,labelHeight, Gtk.PositionType.RIGHT, 1, 1)

		vbox.add(grid)
		self.add(vbox)

	def apply(self):
		maxW = self.width_spinbutton.get_value()
		maxH = self.height_spinbutton.get_value()
		self.fieldTab.field.pos.setValue('maxWidth', maxW)
		self.fieldTab.field.pos.setValue('maxHeight', maxH)


class GuiTab(Gtk.Box):

	def __init__(self, type):
		Gtk.Box.__init__(self)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_background = BackgroundTab(type)
		self.notebook.append_page(self.page_background, Gtk.Label(_("Pictures & Background")))

		# 2nd tab -> Field settings
		# self.page_font = LyricfontTab(type)
		# self.notebook.append_page(self.page_font, Gtk.Label(_("Lyric-Font")))
		self.page_fields = FieldTab(type)
		self.notebook.append_page(self.page_fields, Gtk.Label(_("Fields")))

