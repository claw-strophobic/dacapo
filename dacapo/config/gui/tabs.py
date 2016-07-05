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
# from  gi.repository.GObject import GEnum


class PreviewTab(Gtk.Box, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, guiType):
		Gtk.Box.__init__(self)
		self.guiType = guiType
		self.screen = None

	def on_preview(self, *data):
		import types
		import operator
		g = CONFIG.gui[self.guiType]
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.guiType)
		resolution = (g.width, g.height)
		FPS = 30
		fpsClock = pygame.time.Clock()
		fpsClock.tick(FPS)
		print("going to set pygame.display to: {!s}".format(self.guiType))
		try:
			if self.guiType == "fullscreen":
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

	def __init__(self, guiType):
		super(BackgroundTab, self).__init__(guiType)
		backcolorchooser = MyColorChooserWidget(guiType)
		s = Gdk.Screen.get_default()
		g = CONFIG.gui[guiType]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)

		if guiType == 'window':
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
		color = g.getRGBABackgroundColor()
		backcolorchooser.set_rgba(color)
		backcolorchooser.connect_color_activated(self.onColorSet)
		grid.attach_next_to(backcolorchooser, labelBackground, Gtk.PositionType.BOTTOM, 1, 10)

		self.prev_button = Gtk.Button(_("Preview"))
		self.prev_button.set_sensitive(True)
		self.prev_button.connect('clicked', self.on_preview)
		self.prev_button.set_tooltip_text(_("Click here to see a preview of this field."))
		grid.attach_next_to(self.prev_button, labelDummy, Gtk.PositionType.BOTTOM, 1, 1)
		vbox.add(grid)
		self.add(vbox)

	def getBlitObject( self ):
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.guiType)
		if audio is None:
			return None
		else:
			a = list()
			CONFIG.readConfig()
			g = CONFIG.gui[self.guiType]
			g.initFields()
			for field in g.fields:
				if not g.fields[field].isPicField and hasattr(g.fields[field], 'zIndex'):
					print('Adding field {!s}'.format(g.fields[field].name))
					a.append(g.fields[field].getBlitObject())
			a.append(audio.getCover())
			return a

	def onColorSet( self, obj, colorchooser):
		color = colorchooser.get_rgba()
		g = CONFIG.gui[self.guiType]
		g.setValue('backgroundColor', color)


	def onToggled(self, obj, data):
		v = obj.get_active()
		print('New {!s}: {!s}'.format(data, v))
		g = CONFIG.gui[self.guiType]
		g.setValue(data, v)

	def onValueChanged(self, obj, data):
		v = obj.get_value_as_int()
		print('New {!s}: {!s}'.format(data, v))
		g = CONFIG.gui[self.guiType]
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
		self.notebook = Gtk.Notebook()

		self.fields = get_field_combo(type)
		self.fields.set_tooltip_text(_("Select an existing field here."))
		self.fields.connect("changed", self.on_field_combo_changed)
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
		self.page_pos = FieldPosTab(self)
		self.notebook.append_page(self.page_pos, Gtk.Label(_("Position settings")))
		vbox.add(self.notebook)
		self.add(vbox)

	def on_field_combo_changed(self, combo):
		combo_iter = combo.get_active_iter()
		if not combo_iter:
			return
		model = combo.get_model()
		fieldName = model.get_value(combo_iter, 0)
		field = model.get_value(combo_iter, 1)
		self.field = field
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		self.apply_button.set_sensitive(True)
		if audio is not None:
			self.prev_button.set_sensitive(True)
		i = self.notebook.get_n_pages()
		for x in range(0, i):
			p = self.notebook.get_nth_page(x)
			print self.notebook.get_tab_label_text(p)
			p.fillFields()


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

class FieldChildTab(Gtk.Box):
	def __init__(self, fieldTab):
		super(FieldChildTab, self).__init__()
		self.fieldTab = fieldTab
		self.set_border_width(10)
		self.vbox = Gtk.VBox()
		self.set_border_width(10)
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(False)
		self.grid.set_column_spacing(6)


class FieldFontTab(FieldChildTab):

	def __init__(self, fieldTab):
		super(FieldFontTab, self).__init__(fieldTab)

		## add fields
		self.font_chooser = MyFontChooserWidget()
		self.font_chooser.colorchooser.connect_color_activated(self.onColorChanged)

		self.vbox.add(self.grid)
		self.vbox.add(self.font_chooser)
		self.add(self.vbox)

	def fillFields(self):
		font_chooser = self.font_chooser
		font = self.fieldTab.field.font
		font_chooser.setBGcolor(self.fieldTab.guiType)
		fontFace = '{!s} {!s}'.format(font.fontWeight, font.fontStyle)
		## print(u"Field-Font " + font + " fontColor: " + field.font.getRGBAColor().to_string())
		font_chooser.set_font(font.name, font.fontWeight, font.fontStyle, font.fontSize)
		# font_chooser.set_font(field.font.name, fontFace, field.font.fontSize)
		font_chooser.setFGcolor(font.getRGBAColor())

	def onColorChanged(self, obj, colorchooser):
		self.color = colorchooser.get_rgba()


	def apply(self):
		color = self.font_chooser.colorchooser.get_rgba()
		self.fieldTab.field.font.setValue('fontColor', color)

		pangoFontDesc = self.font_chooser.get_font_desc()
		if pangoFontDesc is not None:
			font = pangoFontDesc.get_family()
			size = pangoFontDesc.get_size() / 1024
			weight = pangoFontDesc.get_weight()
			style = pangoFontDesc.get_style()
			# pprint(GEnum.__dict__,None,2)
			self.fieldTab.field.font.setValue('font', font)
			self.fieldTab.field.font.setValue('fontSize', size)
			self.fieldTab.field.font.setValue('fontWeight', weight.value_nick)
			self.fieldTab.field.font.setValue('fontStyle', style.value_nick)

class FieldPosTab(FieldChildTab):

	def __init__(self, fieldTab):
		super(FieldPosTab, self).__init__(fieldTab)
		g = CONFIG.gui[self.fieldTab.guiType]

		labelPosH = Gtk.Label(_('The horizontal position'))
		labelPosV = Gtk.Label(_('The vertical position'))
		labelRefH = Gtk.Label(_('The horizontal reference position'))
		labelRefV = Gtk.Label(_('The vertical reference position'))
		labelWidth = Gtk.Label(_('Maximal field width'))
		labelHeight = Gtk.Label(_('Maximal field height'))
		labelDummy = Gtk.Label(' ')

		# Horizontal Position
		self.grid.add(labelPosH)
		self.posH_spinbutton = Gtk.SpinButton()
		self.posH_spinbutton.set_tooltip_text(_("Set here the horizontal position of the field."))
		self.grid.attach_next_to(self.posH_spinbutton, labelPosH, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelRefH, self.posH_spinbutton, Gtk.PositionType.RIGHT, 1, 1)
		self.comboRefHFields = get_field_combo(self.fieldTab.guiType)
		self.comboRefHFields.set_tooltip_text(_("Select an existing field here."))
		self.grid.attach_next_to(self.comboRefHFields, labelRefH, Gtk.PositionType.RIGHT, 1, 1)

		# Vertical Position
		self.grid.attach_next_to(labelPosV, labelPosH, Gtk.PositionType.BOTTOM, 1, 1)
		self.posV_spinbutton = Gtk.SpinButton()
		self.posV_spinbutton.set_tooltip_text(_("Set here the vertical position of the field."))
		self.grid.attach_next_to(self.posV_spinbutton, labelPosV, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelRefV, self.posV_spinbutton, Gtk.PositionType.RIGHT, 1, 1)
		self.comboRefVFields = get_field_combo(self.fieldTab.guiType)
		self.comboRefVFields.set_tooltip_text(_("Select an existing field here."))
		self.grid.attach_next_to(self.comboRefVFields, labelRefV, Gtk.PositionType.RIGHT, 1, 1)


		# Max width and height
		self.grid.attach_next_to(labelWidth, labelPosV, Gtk.PositionType.BOTTOM, 1, 1)
		self.width_spinbutton = Gtk.SpinButton()
		self.width_spinbutton.set_tooltip_text(_("Set here the maximal pixel width of the field. Leave 0 for no max.") + " (max {!s})".format(g.width))
		self.grid.attach_next_to(self.width_spinbutton,labelWidth, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelHeight, labelWidth, Gtk.PositionType.BOTTOM, 1, 1)
		self.height_spinbutton = Gtk.SpinButton()
		self.height_spinbutton.set_tooltip_text(_("Set here the maximal pixel height of the field. Leave 0 for no max.") + " (max {!s})".format(g.height))
		self.grid.attach_next_to(self.height_spinbutton,labelHeight, Gtk.PositionType.RIGHT, 1, 1)

		self.vbox.add(self.grid)
		self.add(self.vbox)

	def fillFields(self):
		g = CONFIG.gui[self.fieldTab.guiType]
		fieldpos = self.fieldTab.field.pos
		adjustment = Gtk.Adjustment(fieldpos.posH, 0, int(g.width), 1, 10, 0)
		self.posH_spinbutton.set_adjustment(adjustment)
		self.posH_spinbutton.set_value(fieldpos.posH)

		adjustment = Gtk.Adjustment(fieldpos.posV, 0, int(g.width), 1, 10, 0)
		self.posV_spinbutton.set_adjustment(adjustment)
		self.posV_spinbutton.set_value(fieldpos.posV)

		adjustment = Gtk.Adjustment(fieldpos.maxWidth, 0, int(g.width), 1, 10, 0)
		self.width_spinbutton.set_adjustment(adjustment)
		self.width_spinbutton.set_value(fieldpos.maxWidth)

		adjustment = Gtk.Adjustment(fieldpos.maxHeight, 0, int(g.width), 1, 10, 0)
		self.height_spinbutton.set_adjustment(adjustment)
		self.height_spinbutton.set_value(fieldpos.maxHeight)
		model = self.comboRefHFields.get_model()
		i = 0
		self.comboRefHFields.set_active(0)
		if fieldpos.posRefH is not None:
			for row in model:
				if row[0] == fieldpos.posRefH:
					self.comboRefHFields.set_active(i)
					break
				i += 1

		model = self.comboRefVFields.get_model()
		self.comboRefVFields.set_active(0)
		i = 0
		if fieldpos.posRefV is not None:
			for row in model:
				if row[0] == fieldpos.posRefV:
					self.comboRefVFields.set_active(i)
					break
				i += 1

	def apply(self):
		fieldpos = self.fieldTab.field.pos
		posH = self.posH_spinbutton.get_value()
		posV = self.posV_spinbutton.get_value()
		fieldpos.setValue('posH', posH)
		fieldpos.setValue('posV', posV)

		model = self.comboRefHFields.get_model()
		combo_iter = self.comboRefHFields.get_active_iter()
		if combo_iter is not None:
			fieldName = model.get_value(combo_iter, 0)
			posRefH = fieldName
			fieldpos.setValue('posRefH', posRefH)
		model = self.comboRefVFields.get_model()
		combo_iter = self.comboRefVFields.get_active_iter()
		if combo_iter is not None:
			fieldName = model.get_value(combo_iter, 0)
			posRefV = fieldName
			fieldpos.setValue('posRefV', posRefV)
		print("posRefH: {!s} posRefV: {!s}".format(posRefH, posRefV))
		maxW = self.width_spinbutton.get_value()
		maxH = self.height_spinbutton.get_value()
		fieldpos.setValue('maxWidth', maxW)
		fieldpos.setValue('maxHeight', maxH)


class GuiTab(Gtk.Box):

	def __init__(self, guiType):
		Gtk.Box.__init__(self)
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_background = BackgroundTab(guiType)
		self.notebook.append_page(self.page_background, Gtk.Label(_("Background")))

		# 2nd tab -> Field settings
		# self.page_font = LyricfontTab(type)
		# self.notebook.append_page(self.page_font, Gtk.Label(_("Lyric-Font")))
		self.page_fields = FieldTab(guiType)
		self.notebook.append_page(self.page_fields, Gtk.Label(_("Fields")))


def get_field_combo(type):
	type_store = Gtk.ListStore(str, object)
	g = CONFIG.gui[type]
	type_store.append(['', None])
	for key in g.fields:
		type_store.append([key, g.fields[key]])
	field_combo = Gtk.ComboBox.new_with_model(type_store)
	field_combo.type = type
	renderer = Gtk.CellRendererText()
	field_combo.pack_start(renderer, True)
	field_combo.add_attribute(renderer, 'text', 0)
	field_combo.set_entry_text_column(0)
	return field_combo

