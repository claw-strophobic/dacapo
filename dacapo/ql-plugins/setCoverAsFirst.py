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


class SetFrontCoverAsFirst(SongsMenuPlugin):
	PLUGIN_ID = "SetFrontCoverAsFirstImage"
	PLUGIN_NAME = _('Set frontcover 1st image')
	PLUGIN_DESC = _("Set the front coverart as first image in the audiofile (if it is not already the first).")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		super(SetFrontCoverAsFirst, self).__init__(*args, **kwargs)

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
			_("Check {!s} files?".format(len(songs)))
								  ).run():
			return True

		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Checking...\n\n%(current)d/%(total)d Songs done."))
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
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
		## if file has no images -> leave
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			return

		## if first image is frontcover -> leave
		img = audio.pictures[0]
		if img.type == 3:
			return

		## ok, we have to lookup the data...
		images = list()
		frontcover = None
		for img in audio.pictures:
			if img.type == 3:
				frontcover = img
			else:
				images.append(img)

		## if file has no frontcover -> leave
		if (frontcover is None):
			print(_("No frontcover found in {!s}.").format(song.get("~filename", "")))
			return

		## first,clear all pictures, then add the frontcover
		try:
			audio.clear_pictures()
			audio.add_picture(frontcover)
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

