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
from quodlibet.qltk.wlw import WaitLoadWindow
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from mutagen.flac import FLAC, Picture
from quodlibet import qltk, app
import traceback, sys
import gettext
t = gettext.translation('dacapo-plugins', "/usr/share/locale/")
t.install()


class CountImages(SongsMenuPlugin):
	PLUGIN_ID = "CountPictures"
	PLUGIN_NAME = _('Count Pictures in Audiofile')
	PLUGIN_DESC = _("Counts the pictures in an audio file and stores the result in the tag PICTURES, so that you can use it in Quod Libet.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		super(CountImages, self).__init__(*args, **kwargs)

	def plugin_handles(self, songs):
		result = False
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				self.counter += 1
				result = True
		return result

	def plugin_songs(self, songs):

		if (songs is None) or (len(songs) <= 0):
			return True

		if not qltk.ConfirmAction(self.plugin_window,
			_(self.PLUGIN_NAME),
			_("Check {!s} files?").format(len(songs))
								  ).run():
			return True

		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Counting pictures.\n\n%(current)d/%(total)d Songs done."))
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				flacFilePath = song.get("~filename", "")
				try:
					self.countImages(song)
				except:
					win.destroy()
					self.printError()
					return False
			if win.step():
				break
		win.destroy()


	def countImages(self, song):
		audio = FLAC(song.get("~filename", ""))
		count = "0"
		## if file has no images -> set to 0
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			pass
		else:
			count = str(len(audio.pictures))

		del audio

		if not "pictures" in song:
			song["pictures"] = count

		if song["pictures"] <> count:
			song["pictures"] = count

		return

	def printError(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		for line in lines:
			print(line)

