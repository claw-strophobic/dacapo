#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
from dacapo.config.gui.tabs import *
from dacapo.metadata import *
_ = t.ugettext

UI_INFO = """
<ui>
	<menubar name='MenuBar'>
		<menu action='FileMenu'>
			<menuitem action='FileSave' />
			<menuitem action='FileSaveAs' />
			<separator />
			<menuitem action='OpenAudio' />
			<separator />
			<menuitem action='FileQuit' />
		</menu>
		<menu action='EditMenu'>
			<menuitem action='EditCopy' />
			<menuitem action='EditPaste' />
			<menuitem action='EditSomething' />
		</menu>
	</menubar>
</ui>
"""

class Configurator(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title=_("dacapo configurator"))
		self.audio = None
		CONFIG.setConfig('TEMP', Key='AUDIOFILE', Value=None)
		CONFIG.setConfig('TEMP', Key='PLAYER', Value=self)
		self.gstPlayer = self
		CONFIG.setConfig('TEMP', Key='PLAYLIST', Value=self)

		self.set_border_width(3)
		action_group = Gtk.ActionGroup("my_actions")

		self.add_file_menu_actions(action_group)
		self.add_edit_menu_actions(action_group)

		uimanager = self.create_ui_manager()
		uimanager.insert_action_group(action_group)

		menubar = uimanager.get_widget("/MenuBar")

		vbox = Gtk.VBox()

		vbox.add(menubar)

		self.notebook = Gtk.Notebook()
		vbox.add(self.notebook)

		# 1st tab -> Window settings
		self.page_window = GuiTab(self, 'window')
		self.notebook.append_page(self.page_window, Gtk.Label(_("GUI Window")))

		# 2nd tab -> Fullscreen settings
		self.page_fullscreen = GuiTab(self, 'fullscreen')
		self.notebook.append_page(self.page_fullscreen, Gtk.Label(_("GUI Fullscreen")))

		# 3rd tab -> Metadata settings
		self.page_metadata = MetaTab(self)
		self.notebook.append_page(self.page_metadata, Gtk.Label(_("Metadata")))

		# 4th tab -> Audio & Debug
		self.page_debug = AudioAndDebugTab(self)
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
		self.add(vbox)

		# Create a statusbar
		self.statusbar = Gtk.Statusbar()
		self.context_id = self.statusbar.get_context_id("start")
		self.statusbar.push(self.context_id, _("Ready..."))
		vbox.add(self.statusbar)



	def add_file_menu_actions(self, action_group):
		action_group.add_actions([
			("FileMenu", None, "File"),
			("FileSave", Gtk.STOCK_SAVE, None, None, None,
			 self.on_menu_save),
			("FileSaveAs", Gtk.STOCK_SAVE_AS, None, None, None,
			 self.on_menu_save_as),
			("OpenAudio", None, _("Open Audiofile"), "<control>O", None,
			 self.on_menu_open_audio),
			("FileQuit", Gtk.STOCK_QUIT, None, None, None,
			 self.on_menu_file_quit),
		])

	def add_edit_menu_actions(self, action_group):
		action_group.add_actions([
			("EditMenu", None, "Edit"),
			("EditCopy", Gtk.STOCK_COPY, None, None, None,
			 self.on_menu_others),
			("EditPaste", Gtk.STOCK_PASTE, None, None, None,
			 self.on_menu_others),
			("EditSomething", None, "Something", "<control><alt>S", None,
			 self.on_menu_others)
		])

	def create_ui_manager(self):
		uimanager = Gtk.UIManager()

		# Throws exception if something went wrong
		uimanager.add_ui_from_string(UI_INFO)

		# Add the accelerator group to the toplevel window
		accelgroup = uimanager.get_accel_group()
		self.add_accel_group(accelgroup)
		return uimanager

	def on_menu_open_audio(self, widget):
		dialog = Gtk.FileChooserDialog(_("Open Audiofile"),
                                      self,
                                      Gtk.FileChooserAction.OPEN,
                                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		filter = Gtk.FileFilter()
		filter.set_name(_("Flac files"))
		filter.add_mime_type("audio/flac")
		dialog.add_filter(filter)
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			file = dialog.get_filename()
			self.audio = getAudioFile(file)
			self.audio.loadFrontCover()
			CONFIG.setConfig('TEMP', Key='AUDIOFILE', Value=self.audio)
			if self.page_window.page_fields.field:
				self.page_window.page_fields.prev_button.set_sensitive(True)
			if self.page_fullscreen.page_fields.field:
				self.page_fullscreen.page_fields.prev_button.set_sensitive(True)
			self.statusbar.push(self.context_id, _("Loaded audiofile: ") + file.decode('utf-8'))

		dialog.destroy()
		return

	def on_menu_save_as(self, widget):
		dialog = Gtk.FileChooserDialog(_("Save Config File"),
                                      self,
                                      Gtk.FileChooserAction.SAVE,
                                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_SAVE_AS, Gtk.ResponseType.ACCEPT))
		dialog.set_show_hidden(True)
		response = dialog.run()
		if response == Gtk.ResponseType.ACCEPT:
			file = dialog.get_filename()
			CONFIG.saveConfig(file)
			self.statusbar.push(self.context_id, _("Saved config to: ") + file)
		else:
			self.statusbar.push(self.context_id, _("Saving canceled"))

		dialog.destroy()
		return

	def on_menu_save(self, widget):
		text = CONFIG.saveConfig()
		self.statusbar.push(self.context_id, _("Saved config. "))
		return

	def on_menu_file_new_generic(self, widget):
		print("A File|New menu item ({!s}) was selected.".format(widget.get_name()))

	def on_menu_file_quit(self, widget):
		self.statusbar.remove_all(self.context_id)
		Gtk.main_quit()

	def on_menu_others(self, widget):
		print("Menu item " + widget.get_name() + " was selected")

	def isPlaylist(self):
		return True

	def getDuration(self):
		return "3:25"

	def queryPosition(self):
		return "1:23"

	def getActSong(self):
		return 3

	def getNumberOfSongs(self):
		return 15

win = Configurator()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()