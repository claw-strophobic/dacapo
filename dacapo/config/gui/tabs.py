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
import os
_ = t.ugettext

UI_ALIGN_H = {_("Left") : "left" , _("Right") : "right",	"Center" : "center"}
UI_ALIGN_V = {_("Top") : "top" , _("Bottom") : "bottom",	"Middle" : "center"}
UI_CONVERT = {_("Lowercase") : "lower" , _("Uppercase") : "upper"}
UI_OPERATOR = {_("Empty") : "empty" , _("Not empty") : "notempty"}
UI_SINKTYPE = {_("Alsa") : "alsa" , _("JACK") : "jack"}
CSSFILE = os.path.join(os.path.dirname(__file__), 'configurator.css')

class PreviewTab(Gtk.Box, dacapo.ui.interface_blitobject.BlitInterface):

	def __init__(self, main, guiType):
		Gtk.Box.__init__(self)
		self.guiType = guiType
		self.screen = None
		self.window = main

	def on_preview(self, *data):
		import types
		import operator
		g = CONFIG.gui[self.guiType]
		CONFIG.setConfig('TEMP', 'gui', 'winState', self.guiType)
		resolution = (g.width, g.height)
		FPS = 30
		fpsClock = pygame.time.Clock()
		fpsClock.tick(FPS)
		try:
			if self.guiType == "fullscreen":
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
		if isinstance(obj, types.ListType):
			sorted_x = sorted(obj, key=operator.attrgetter('zIndex'))
			for o in sorted_x:
				self.doBlitObject(self.screen, o, True)
		else:
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



class BackgroundTab(PreviewTab):

	def __init__(self, main, guiType):
		super(BackgroundTab, self).__init__(main, guiType)
		backcolorchooser = MyColorChooserWidget(guiType)
		s = Gdk.Screen.get_default()
		g = CONFIG.gui[guiType]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)

		if guiType == 'window':
			labelWidth = Gtk.Label(_('Window width'), xalign=0)
			labelHeight = Gtk.Label(_('Window height'), xalign=0)
		else:
			labelWidth = Gtk.Label(_('Fullscreen width'), xalign=0)
			labelHeight = Gtk.Label(_('Fullscreen height'), xalign=0)
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

		labelMouseVisible = Gtk.Label(_('Show the mouse cursor'), xalign=0)
		grid.attach_next_to(labelMouseVisible, labelHeight, Gtk.PositionType.BOTTOM, 1, 1)
		self.mouseVisible = Gtk.CheckButton()
		self.mouseVisible.set_active(g.mouseVisible)
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
			#CONFIG.readConfig()
			g = CONFIG.gui[self.guiType]
			g.initFields()
			for field in g.fields:
				if not g.fields[field].isPicField and hasattr(g.fields[field], 'zIndex'):
					a.append(g.fields[field].getBlitObject())
			a.append(audio.getCover())
			return a

	def onColorSet( self, obj, colorchooser):
		color = colorchooser.get_rgba()
		g = CONFIG.gui[self.guiType]
		g.setValue('backgroundColor', color)


	def onToggled(self, obj, data):
		v = obj.get_active()
		g = CONFIG.gui[self.guiType]
		g.setValue(data, v)

	def onValueChanged(self, obj, data):
		v = obj.get_value_as_int()
		g = CONFIG.gui[self.guiType]
		g.setValue(data, v)


class FieldTab(PreviewTab):

	def __init__(self, main, guiType):
		super(FieldTab, self).__init__(main, guiType)
		self.field = None
		g = CONFIG.gui[guiType]
		self.set_border_width(10)
		vbox = Gtk.VBox()
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)
		vbox.set_spacing(10)
		self.notebook = Gtk.Notebook()

		self.fields = get_field_combo(guiType)
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
		self.page_layout = FieldLayoutTab(self)
		self.notebook.append_page(self.page_layout, Gtk.Label(_("Layout settings")))
		vbox.add(self.notebook)
		self.add(vbox)

	def on_field_combo_changed(self, combo):
		window = self.window
		combo_iter = combo.get_active_iter()
		if not combo_iter:
			return
		model = combo.get_model()
		fieldName = model.get_value(combo_iter, 0)
		field = model.get_value(combo_iter, 1)
		if field is None:
			return
		self.field = field
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		self.apply_button.set_sensitive(True)
		if audio is not None:
			self.prev_button.set_sensitive(True)
		i = self.notebook.get_n_pages()
		for x in range(0, i):
			p = self.notebook.get_nth_page(x)
			p.fillFields()
		window.statusbar.push(window.context_id, _("Selected field: ") + fieldName)


	def getBlitObject( self ):
		audio = CONFIG.getConfig('TEMP', Key='AUDIOFILE')
		if audio is None or self.field is None:
			return None
		else:
			self.field.initFields()
			return self.field.getBlitObject()

	def on_applied(self, *data):
		window = self.window
		i = self.notebook.get_n_pages()
		for x in range(0, i):
			p = self.notebook.get_nth_page(x)
			p.apply()
		window.statusbar.push(window.context_id, _("Applied the settings."))

class FieldChildTab(Gtk.Box):
	def __init__(self, fieldTab):
		super(FieldChildTab, self).__init__()
		self.window = self.get_toplevel()
		screen = Gdk.Screen.get_default()
		css_provider = Gtk.CssProvider()
		css_provider.load_from_path(CSSFILE)
		context = Gtk.StyleContext()
		context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
		self.fieldTab = fieldTab
		self.set_border_width(10)
		self.vbox = Gtk.VBox()
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(False)
		self.grid.set_column_spacing(10)
		self.grid.set_row_spacing(10)


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
		font_chooser.set_font(font.name, font.fontWeight, font.fontStyle, font.fontSize)
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
			self.fieldTab.field.font.setValue('font', font)
			self.fieldTab.field.font.setValue('fontSize', size)
			self.fieldTab.field.font.setValue('fontWeight', weight.value_nick)
			self.fieldTab.field.font.setValue('fontStyle', style.value_nick)

class FieldPosTab(FieldChildTab):

	def __init__(self, fieldTab):
		super(FieldPosTab, self).__init__(fieldTab)
		g = CONFIG.gui[self.fieldTab.guiType]

		labelPosH = Gtk.Label(_('The horizontal position'), xalign=0)
		labelPosV = Gtk.Label(_('The vertical position'), xalign=0)
		labelRefH = Gtk.Label(_('The horizontal reference position'), xalign=0)
		labelRefV = Gtk.Label(_('The vertical reference position'), xalign=0)
		labelAlignH = Gtk.Label(_('The horizontal alignment'), xalign=0)
		labelAlignV = Gtk.Label(_('The vertical alignment'), xalign=0)
		labelWidth = Gtk.Label(_('Maximal field width'), xalign=0)
		labelHeight = Gtk.Label(_('Maximal field height'), xalign=0)
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

		self.grid.attach_next_to(labelAlignH, self.comboRefHFields, Gtk.PositionType.RIGHT, 1, 1)
		self.comboAlignH = get_simple_combo(UI_ALIGN_H)
		self.comboAlignH.set_tooltip_text(_("Select the horizontal alignment for the field on the screen here."))
		self.grid.attach_next_to(self.comboAlignH, labelAlignH, Gtk.PositionType.RIGHT, 1, 1)

		# Vertical Position
		self.grid.attach_next_to(labelPosV, labelPosH, Gtk.PositionType.BOTTOM, 1, 1)
		self.posV_spinbutton = Gtk.SpinButton()
		self.posV_spinbutton.set_tooltip_text(_("Set here the vertical position of the field."))
		self.grid.attach_next_to(self.posV_spinbutton, labelPosV, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelRefV, self.posV_spinbutton, Gtk.PositionType.RIGHT, 1, 1)
		self.comboRefVFields = get_field_combo(self.fieldTab.guiType)
		self.comboRefVFields.set_tooltip_text(_("Select an existing field here."))
		self.grid.attach_next_to(self.comboRefVFields, labelRefV, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelAlignV, self.comboRefVFields, Gtk.PositionType.RIGHT, 1, 1)
		self.comboAlignV = get_simple_combo(UI_ALIGN_V)
		self.comboAlignV.set_tooltip_text(_("Select the vertical alignment for the field on the screen here."))
		self.grid.attach_next_to(self.comboAlignV, labelAlignV, Gtk.PositionType.RIGHT, 1, 1)


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
		adjustment = Gtk.Adjustment(fieldpos.posH, (g.width * -1), g.width, 1, 10, 0)
		self.posH_spinbutton.set_adjustment(adjustment)
		self.posH_spinbutton.set_value(fieldpos.posH)

		adjustment = Gtk.Adjustment(fieldpos.posV, (g.width * -1), g.width, 1, 10, 0)
		self.posV_spinbutton.set_adjustment(adjustment)
		self.posV_spinbutton.set_value(fieldpos.posV)

		adjustment = Gtk.Adjustment(fieldpos.maxWidth, 0, g.width, 1, 10, 0)
		self.width_spinbutton.set_adjustment(adjustment)
		self.width_spinbutton.set_value(fieldpos.maxWidth)

		adjustment = Gtk.Adjustment(fieldpos.maxHeight, 0, g.width, 1, 10, 0)
		self.height_spinbutton.set_adjustment(adjustment)
		self.height_spinbutton.set_value(fieldpos.maxHeight)

		set_combo_active_value(self.comboRefHFields, fieldpos.posRefH)
		set_combo_active_value(self.comboRefVFields, fieldpos.posRefV)

		set_combo_active_value(self.comboAlignH, fieldpos.alignH)
		set_combo_active_value(self.comboAlignV, fieldpos.alignV)

	def apply(self):
		fieldpos = self.fieldTab.field.pos
		posH = self.posH_spinbutton.get_value()
		posV = self.posV_spinbutton.get_value()
		fieldpos.setValue('posH', posH)
		fieldpos.setValue('posV', posV)

		posRefH = get_combo_active_value(self.comboRefHFields)
		fieldpos.setValue('posRefH', posRefH)
		posRefV = get_combo_active_value(self.comboRefVFields)
		fieldpos.setValue('posRefV', posRefV)

		alignH = get_combo_active_value(self.comboAlignH)
		fieldpos.setValue('alignH', alignH)
		alignV = get_combo_active_value(self.comboAlignV)
		fieldpos.setValue('alignV', alignV)

		maxW = self.width_spinbutton.get_value()
		maxH = self.height_spinbutton.get_value()
		fieldpos.setValue('maxWidth', maxW)
		fieldpos.setValue('maxHeight', maxH)


class FieldLayoutTab(FieldChildTab):

	def __init__(self, fieldTab):
		super(FieldLayoutTab, self).__init__(fieldTab)
		g = CONFIG.gui[self.fieldTab.guiType]

		labelOverlay = Gtk.Label(_("Overlay over other elements"), xalign=0)
		labelMulti = Gtk.Label(_("Field has multi lines"), xalign=0)
		labelSplit = Gtk.Label(_("Split the field at spaces"), xalign=0)
		labelzIndex = Gtk.Label(_("Stack order of the field"), xalign=0)
		labelConvert = Gtk.Label(_("Convert content"), xalign=0)
		labelComments = Gtk.Label(_("Comments"), xalign=0)
		labelContent = Gtk.Label(_("Content"), xalign=0)
		labelAlignment = Gtk.Label(_("Alignment"), xalign=0)
		labelDummy = Gtk.Label('')

		self.grid.add(labelOverlay)
		self.overlaySwitch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
		self.overlaySwitch.set_tooltip_text(_("Should this field overlay other elements?"))
		self.grid.attach_next_to(self.overlaySwitch, labelOverlay, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelMulti, labelOverlay, Gtk.PositionType.BOTTOM, 1, 1)
		self.MultiSwitch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
		self.MultiSwitch.set_tooltip_text(_("Should this field be displayed with multi lines?"))
		self.grid.attach_next_to(self.MultiSwitch, labelMulti, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelSplit, labelMulti, Gtk.PositionType.BOTTOM, 1, 1)
		self.SpltSwitch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
		self.SpltSwitch.set_tooltip_text(_("Should this field get line breaks at spaces?"))
		self.grid.attach_next_to(self.SpltSwitch, labelSplit, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelzIndex, labelSplit, Gtk.PositionType.BOTTOM, 1, 1)
		self.zIndex_spinbutton = Gtk.SpinButton()
		self.zIndex_spinbutton.set_tooltip_text(_("Set here the stack order of the field. The higher the value the higher on the stack."))
		self.grid.attach_next_to(self.zIndex_spinbutton, labelzIndex, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelConvert, labelzIndex, Gtk.PositionType.BOTTOM, 1, 1)
		self.comboConvert = get_simple_combo(UI_CONVERT)
		self.comboConvert.set_tooltip_text(_("Select a converting type here. Uppercase - all letter in upper case / Lowercase - all letters in lower case."))
		self.grid.attach_next_to(self.comboConvert, labelConvert, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelAlignment, labelConvert, Gtk.PositionType.BOTTOM, 1, 1)
		self.comboAlignment = get_simple_combo(UI_ALIGN_H)
		self.comboAlignment.set_tooltip_text(_("Select the alingment of the text in the field."))
		self.grid.attach_next_to(self.comboAlignment, labelAlignment, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelComments, self.overlaySwitch, Gtk.PositionType.RIGHT, 1,1)
		self.txtCommentView = Gtk.TextView()
		self.txtComment = self.txtCommentView.get_buffer()
		self.txtCommentView.set_tooltip_text(_("Set a free comment here"))
		self.grid.attach_next_to(self.txtCommentView, labelComments, Gtk.PositionType.RIGHT, 1, 2)
		self.txtCommentView.get_style_context().add_class("myview")

		self.grid.attach_next_to(labelDummy, labelComments, Gtk.PositionType.BOTTOM, 1, 1)
		self.grid.attach_next_to(labelContent, labelDummy, Gtk.PositionType.BOTTOM, 1, 1)
		self.txtContentView = Gtk.TextView()
		self.txtContent = self.txtContentView.get_buffer()
		self.txtContentView.set_tooltip_text(_("Set the content of the field here"))
		self.grid.attach_next_to(self.txtContentView, labelContent, Gtk.PositionType.RIGHT, 1, 2)
		self.txtCommentView.get_style_context().add_class("myview")

		self.vbox.add(self.grid)
		self.add(self.vbox)

	def fillFields(self):
		g = CONFIG.gui[self.fieldTab.guiType]
		field = self.fieldTab.field
		self.overlaySwitch.set_active(field.overlay)
		self.MultiSwitch.set_active(field.multiLine)
		self.SpltSwitch.set_active(field.splitSpaces)
		adjustment = Gtk.Adjustment(field.zIndex, (-999), 999, 1, 10, 0)
		self.zIndex_spinbutton.set_adjustment(adjustment)
		self.zIndex_spinbutton.set_value(field.zIndex)
		set_combo_active_value(self.comboConvert, field.convert)
		set_combo_active_value(self.comboAlignment, field.alignment)
		self.txtComment.set_text('')
		if field.comments and field.comments <> 'None':
			self.txtComment.set_text(field.comments)
		self.txtContent.set_text('')
		if field.content:
			self.txtContent.set_text(field.content)


	def apply(self):
		g = CONFIG.gui[self.fieldTab.guiType]
		field = self.fieldTab.field
		field.setValue('overlay', self.overlaySwitch.get_active())
		field.setValue('multiLine', self.MultiSwitch.get_active())
		field.setValue('splitSpaces', self.SpltSwitch.get_active())
		field.setValue('zIndex', self.zIndex_spinbutton.get_value())
		field.setValue('convert', get_combo_active_value(self.comboConvert))
		field.setValue('alignment', get_combo_active_value(self.comboAlignment))
		comment = self.txtComment.get_text(self.txtComment.get_start_iter(), self.txtComment.get_end_iter(), False)
		content = self.txtContent.get_text(self.txtContent.get_start_iter(), self.txtContent.get_end_iter(), False)
		field.setValue('comments', comment)
		field.setValue('value', content)


class CondTab(PreviewTab):

	def __init__(self, main):
		super(CondTab, self).__init__(main, 'metaData')
		self.cond = None
		g = CONFIG.gui['metaData']
		self.set_border_width(10)
		vbox = Gtk.VBox()
		grid = Gtk.Grid()
		grid.set_column_homogeneous(False)
		grid.set_column_spacing(6)
		grid.set_row_spacing(10)
		vbox.set_spacing(10)

		labelComments = Gtk.Label(_("Comments"), xalign=0)
		labelOperator = Gtk.Label(_("Operator"), xalign=0)
		labelOperand = Gtk.Label(_("Operand"), xalign=0)
		labelContent = Gtk.Label(_("Content"), xalign=0)
		labelDummy = Gtk.Label('')
		labelDummy2 = Gtk.Label('')
		labelDummy3 = Gtk.Label('')

		self.conds = get_field_combo('metaData')
		self.conds.set_tooltip_text(_("Select an existing condition here."))
		self.conds.connect("changed", self.on_cond_combo_changed)
		labelField = Gtk.Label(_('Field:'))
		grid.add(labelField)
		grid.attach_next_to(self.conds, labelField, Gtk.PositionType.RIGHT, 1, 1)

		self.apply_button = Gtk.Button(_("apply"))
		self.apply_button.set_sensitive(False)
		self.apply_button.connect('clicked', self.on_applied)
		self.apply_button.set_tooltip_text(_("Click here to see apply the settings of this condition."))
		grid.attach_next_to(self.apply_button, self.conds, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(labelDummy, labelField, Gtk.PositionType.BOTTOM, 1, 1)

		grid.attach_next_to(labelOperand, labelDummy, Gtk.PositionType.BOTTOM, 1,1)
		self.operand = Gtk.Entry()
		grid.attach_next_to(self.operand, labelOperand, Gtk.PositionType.RIGHT, 1, 1)

		grid.attach_next_to(labelComments, labelOperand, Gtk.PositionType.BOTTOM, 1,1)
		self.txtCommentView = Gtk.TextView()
		self.txtComment = self.txtCommentView.get_buffer()
		self.txtCommentView.set_tooltip_text(_("Set a free comment here"))
		grid.attach_next_to(self.txtCommentView, labelComments, Gtk.PositionType.RIGHT, 1, 2)
		self.txtCommentView.get_style_context().add_class("myview")
		grid.attach_next_to(labelDummy2, labelComments, Gtk.PositionType.BOTTOM, 1, 1)

		grid.attach_next_to(labelOperator, labelDummy2, Gtk.PositionType.BOTTOM, 1, 1)
		self.comboOperator = get_simple_combo(UI_OPERATOR)
		self.comboOperator.set_tooltip_text(_("Select a converting type here. Uppercase - all letter in upper case / Lowercase - all letters in lower case."))
		grid.attach_next_to(self.comboOperator, labelOperator, Gtk.PositionType.RIGHT, 1, 1)


		grid.attach_next_to(labelContent, labelOperator, Gtk.PositionType.BOTTOM, 1, 1)
		self.txtContentView = Gtk.TextView()
		self.txtContent = self.txtContentView.get_buffer()
		self.txtContentView.set_tooltip_text(_("Set the content of the condition here"))
		grid.attach_next_to(self.txtContentView, labelContent, Gtk.PositionType.RIGHT, 1, 2)
		self.txtCommentView.get_style_context().add_class("myview")
		grid.attach_next_to(labelDummy3, labelContent, Gtk.PositionType.BOTTOM, 1, 1)

		vbox.add(grid)
		self.add(vbox)

	def fillFields(self):
		g = CONFIG.gui['metaData']
		field = self.cond
		set_combo_active_value(self.comboOperator, field.operator)
		self.operand.set_text(field.operand)
		self.txtComment.set_text('')
		if field.comments and field.comments <> 'None':
			self.txtComment.set_text(field.comments)
		self.txtContent.set_text('')
		if field.content:
			self.txtContent.set_text(field.content)

	def on_cond_combo_changed(self, combo):
		window = self.window
		combo_iter = combo.get_active_iter()
		if not combo_iter:
			return
		model = combo.get_model()
		fieldName = model.get_value(combo_iter, 0)
		field = model.get_value(combo_iter, 1)
		if field is None:
			return
		self.cond = field
		self.apply_button.set_sensitive(True)
		window.statusbar.push(window.context_id, _("Selected field: ") + fieldName)
		self.fillFields()


	def on_applied(self, *data):
		window = self.window
		g = CONFIG.gui['metaData']
		field = self.cond
		field.setValue('operator', get_combo_active_value(self.comboOperator))
		comment = self.txtComment.get_text(self.txtComment.get_start_iter(), self.txtComment.get_end_iter(), False)
		content = self.txtContent.get_text(self.txtContent.get_start_iter(), self.txtContent.get_end_iter(), False)
		field.setValue('comments', comment)
		field.setValue('value', content)
		window.statusbar.push(window.context_id, _("Applied the settings."))

class AudioTab(PreviewTab):

	def __init__(self, main):
		super(AudioTab, self).__init__(main, 'audio_engine')
		g = CONFIG.gui['audio_engine']
		self.set_border_width(10)
		vbox = Gtk.VBox()
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(False)
		self.grid.set_column_spacing(6)
		self.grid.set_row_spacing(10)
		vbox.set_spacing(10)

		labelSinkType = Gtk.Label(_("Sink Type"), xalign=0)
		labelReplayGain = Gtk.Label(_("ReplayGain"), xalign=0)
		labelGapless = Gtk.Label(_("Gapless"), xalign=0)

		self.grid.add(labelSinkType)
		self.comboSinkType = get_simple_combo(UI_SINKTYPE)
		self.comboSinkType.set_tooltip_text(_("Select a sink type here."))
		self.grid.attach_next_to(self.comboSinkType, labelSinkType, Gtk.PositionType.RIGHT, 1, 1)

		self.apply_button = Gtk.Button(_("apply"))
		self.apply_button.connect('clicked', self.on_applied)
		self.apply_button.set_tooltip_text(_("Click here to apply the changes of this settings."))
		self.grid.attach_next_to(self.apply_button, self.comboSinkType, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelReplayGain, labelSinkType, Gtk.PositionType.BOTTOM, 1, 1)
		self.ReplayGainSwitch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
		self.ReplayGainSwitch.set_tooltip_text(_("Use ReplayGain?"))
		self.grid.attach_next_to(self.ReplayGainSwitch, labelReplayGain, Gtk.PositionType.RIGHT, 1, 1)

		self.grid.attach_next_to(labelGapless, labelReplayGain, Gtk.PositionType.BOTTOM, 1, 1)
		self.GaplessSwitch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
		self.GaplessSwitch.set_tooltip_text(_("Use gapless playback?"))
		self.grid.attach_next_to(self.GaplessSwitch, labelGapless, Gtk.PositionType.RIGHT, 1, 1)

		vbox.add(self.grid)
		self.add(vbox)
		self.fillFields()

	def fillFields(self):
		g = CONFIG.gui['audio_engine']
		set_combo_active_value(self.comboSinkType, g.sinkType)
		self.ReplayGainSwitch.set_active(g.replayGain)
		self.GaplessSwitch.set_active(g.gapless)

	def on_applied(self, *data):
		window = self.window
		g = CONFIG.gui['audio_engine']
		g.setValue('sinkType', get_combo_active_value(self.comboSinkType))
		g.setValue('replayGain', self.ReplayGainSwitch.get_active())
		g.setValue('gapless', self.GaplessSwitch.get_active())
		window.statusbar.push(window.context_id, _("Applied the settings."))



class GuiTab(Gtk.Box):

	def __init__(self, main, guiType):
		Gtk.Box.__init__(self)
		self.main = main
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_background = BackgroundTab(main, guiType)
		self.notebook.append_page(self.page_background, Gtk.Label(_("Background")))
		self.page_fields = FieldTab(main, guiType)
		self.notebook.append_page(self.page_fields, Gtk.Label(_("Fields")))

class MetaTab(Gtk.Box):

	def __init__(self, main):
		Gtk.Box.__init__(self)
		self.main = main
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_cond = CondTab(main)
		self.notebook.append_page(self.page_cond, Gtk.Label(_("Conditions")))

class AudioAndDebugTab(Gtk.Box):

	def __init__(self, main):
		Gtk.Box.__init__(self)
		self.main = main
		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		# 1st tab -> Background settings
		self.page_audio = AudioTab(main)
		self.notebook.append_page(self.page_audio, Gtk.Label(_('Audio & Debug-Settings!')))



def get_field_combo(guiType):
	type_store = Gtk.ListStore(str, object)
	g = CONFIG.gui[guiType]
	type_store.append(['', None])
	for key in g.fields:
		type_store.append([key, g.fields[key]])
	field_combo = Gtk.ComboBox.new_with_model(type_store)
	field_combo.type = guiType
	renderer = Gtk.CellRendererText()
	field_combo.pack_start(renderer, True)
	field_combo.add_attribute(renderer, 'text', 0)
	field_combo.set_entry_text_column(0)
	return field_combo

def get_simple_combo(keyValue):
	## Create ComboBox
	type_store = Gtk.ListStore(str, str)
	type_store.append(('', ''))
	for k in keyValue.iterkeys():
		type_store.append((keyValue[k], k))
	cmb = Gtk.ComboBox.new_with_model(type_store)
	renderer = Gtk.CellRendererText()
	cmb.pack_start(renderer, True)
	cmb.add_attribute(renderer, 'text', 1)
	cmb.set_entry_text_column(1)
	return cmb

def set_combo_active_value(combo, value):
	model = combo.get_model()
	combo.set_active(0)
	i = 0
	if value is not None:
		for row in model:
			if row[0] == value:
				combo.set_active(i)
				break
			i += 1

def get_combo_active_value(combo):
	ret_val = ''
	model = combo.get_model()
	combo_iter = combo.get_active_iter()
	if combo_iter is not None:
		ret_val = model.get_value(combo_iter, 0)
	return ret_val