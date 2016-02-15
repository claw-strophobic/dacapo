#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#

from gi.repository import Gtk
from quodlibet import qltk
from quodlibet.qltk.wlw import WaitLoadWindow
from quodlibet.qltk.chooser import FileChooser
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from mutagen.flac import FLAC, Picture
import mimetypes
import traceback, sys
import gettext
t = gettext.translation('dacapo-plugins', "/usr/share/locale/")
t.install()

class RemoveImageFileChooser(qltk.ConfirmAction):
	TYPE = {
		0: "Other",
		1: "32x32 pixels 'file icon' (PNG only)",
		2: "Other file icon",
		3: "Cover (front)",
		4: "Cover (back)",
		5: "Leaflet page",
		6: "Media (e.g. label side of CD)",
		7: "Lead artist/lead performer/soloist",
		8: "Artist/performer",
		9: "Conductor",
		10: "Band/Orchestra",
		11: "Composer",
		12: "Lyricist/text writer",
		13: "Recording Location",
		14: "During recording",
		15: "During performance",
		16: "Movie/video screen capture",
		17: "A bright coloured fish",
		18: "Illustration",
		19: "Band/artist logotype",
		20: "Publisher/Studio logotype"
	}

	def __init__(self, parent, title, msg):
		super(RemoveImageFileChooser, self).__init__(parent, title, msg)
		## Create ComboBox
		type_store = Gtk.ListStore(int, str)
		for key in self.TYPE:
			type_store.append([key, self.TYPE[key]])
		area = self.get_content_area()

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.add(vbox)

		label = Gtk.Label()
		label.set_text(_("Description"))
		label.set_justify(Gtk.Justification.LEFT)
		label.set_halign(Gtk.Align.START)
		vbox.pack_start(label, True, True, 0)

		self.entry_desc = Gtk.Entry()
		self.entry_desc.connect("changed", self.on_entry_desc_changed)
		vbox.pack_start(self.entry_desc, True, True, 0)

		label = Gtk.Label()
		label.set_text(_("Type"))
		label.set_justify(Gtk.Justification.LEFT)
		label.set_halign(Gtk.Align.START)
		vbox.pack_start(label, True, True, 0)

		name_combo = Gtk.ComboBox.new_with_model(type_store)
		renderer = Gtk.CellRendererText()
		name_combo.set_active(3)
		name_combo.pack_start(renderer, True)
		name_combo.add_attribute(renderer, 'text', 1)
		name_combo.connect("changed", self.on_name_combo_changed)
		name_combo.set_entry_text_column(1)
		vbox.add(name_combo)
		area.add(vbox)
		self.show_all()
		## Set default type
		self.imgType = 3

	def on_name_combo_changed(self, combo):
		combo_iter = combo.get_active_iter()
		if combo_iter:
			model = combo.get_model()
			row_id = model.get_value(combo_iter, 0)
			self.imgType = row_id

	def on_entry_desc_changed(self, entry_desc):
		self.entry_desc_text = entry_desc.get_text()

	def get_description(self):
		return self.entry_desc_text

	def get_type(self):
		return self.imgType

class RemoveImage(SongsMenuPlugin):
	PLUGIN_ID = "RemoveImage"
	PLUGIN_NAME = _('Remove Image from Audiofile')
	PLUGIN_DESC = _("Remove an Image from the audio file with selected image type.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'
	JPG_MIMES = ["image/jpeg"]
	PNG_MIMES = ["image/png"]

	def __init__(self, *args, **kwargs):
		self.counter = 0
		self.imgFiles = list()
		mimetypes.add_type('image/jpeg', '.jpeg')
		mimetypes.add_type('image/jpeg', '.jpg')
		mimetypes.add_type('image/png', '.png')
		super(RemoveImage, self).__init__(*args, **kwargs)

	def plugin_handles(self, songs):
		result = False
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				self.counter += 1
				result = True
		return result

	def plugin_songs(self, songs):

		choose = RemoveImageFileChooser(self.plugin_window, _(self.PLUGIN_NAME), _("Which image should be removed?"))
		if not choose.run():
			return True
		self.desc = choose.get_description()
		self.type = choose.get_type()
		choose.destroy()

		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Removing Image.\n\n%(current)d/%(total)d Songs done."))
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				flacFilePath = song.get("~filename", "")
				try:
					self.removeImage(song)
				except:
					win.destroy()
					self.printError()
					return False
			if win.step():
				break
		win.destroy()


	def removeImage(self, song):
		audio = FLAC(song.get("~filename", ""))
		store = False
		## if file has no images -> leave
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			return
		images = list()
		for img in audio.pictures:
			if img.type == self.type \
			and img.desc == self.desc:
				store = True
			else:
				images.append(img)

		if store:
			## first,clear all pictures, then add the frontcover
			try:
				audio.clear_pictures()
			except:
				self.printError()
				return False
			## now add all other images
			for img in images:
				try:
					audio.add_picture(img)
				except:
					self.printError()
					return False
			audio.save()
		return

	def printError(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		for line in lines:
			print(line)

