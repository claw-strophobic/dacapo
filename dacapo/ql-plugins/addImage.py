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


class AddImageFileChooser(FileChooser):
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

	def __init__(self, parent):
		super(AddImageFileChooser, self).__init__(parent, _("Select Image File"))
		## Create Filter
		filter = Gtk.FileFilter()
		filter.set_name("Image files")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/png")
		self.add_filter(filter)
		## Create ComboBox
		type_store = Gtk.ListStore(int, str)
		for key in self.TYPE:
			type_store.append([key, self.TYPE[key]])
		vbox = self.get_content_area()
		name_combo = Gtk.ComboBox.new_with_model(type_store)
		renderer = Gtk.CellRendererText()
		name_combo.set_active(3)
		name_combo.pack_start(renderer, True)
		name_combo.add_attribute(renderer, 'text', 1)
		name_combo.connect("changed", self.on_name_combo_changed)
		name_combo.set_entry_text_column(1)
		vbox.add(name_combo)
		self.show_all()
		## Set default type
		self.imgType = 3

	def on_name_combo_changed(self, combo):
		combo_iter = combo.get_active_iter()
		if combo_iter:
			model = combo.get_model()
			row_id = model.get_value(combo_iter, 0)
			self.imgType = row_id

class AddImage(SongsMenuPlugin):
	PLUGIN_ID = "AddImage"
	PLUGIN_NAME = _('Add Image To Audiofile')
	PLUGIN_DESC = _("Add an Image to the audio file with selected image type.")
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
		super(AddImage, self).__init__(*args, **kwargs)

	def plugin_handles(self, songs):
		result = False
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				self.counter += 1
				result = True
		return result

	def plugin_songs(self, songs):

		choose = AddImageFileChooser(self.plugin_window)
		files = choose.run()
		choose.destroy()

		if (files == None) or (len(files) <= 0):
			return True

		for file in files:
			contentType = mimetypes.guess_type(file) # get Mimetype
			mimeType = contentType[0]
			if (mimeType in self.JPG_MIMES) or (mimeType in self.PNG_MIMES):
				imgdata = open(file).read()
				img = Picture()
				img.mime = mimeType
				img.type = choose.imgType
				img.desc = choose.TYPE[choose.imgType]
				img.data = imgdata
				self.imgFiles.append(img)

		if not qltk.ConfirmAction(self.plugin_window,
			_(self.PLUGIN_NAME),
			_("Add {!s} images as type \n\n<b>&gt;&gt; {!s} &lt;&lt;</b>\n\nto {!s} files?".format(
					len(files), choose.TYPE[choose.imgType], self.counter))
								  ).run():
			return True

		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Adding Image.\n\n%(current)d/%(total)d Songs done."))
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				flacFilePath = song.get("~filename", "")
				try:
					self.setImage(song)
				except:
					win.destroy()
					self.printError()
					return False
			if win.step():
				break
		win.destroy()


	def setImage(self, song):
		audio = FLAC(song.get("~filename", ""))
		if len(self.imgFiles) <= 0:
			return

		for p in self.imgFiles:
			try:
				audio.add_picture(p)
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

