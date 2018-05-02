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
from quodlibet import qltk, app
from quodlibet.qltk.wlw import WaitLoadWindow
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from mutagen.flac import FLAC
import subprocess
import traceback, sys
import gettext
t = gettext.translation('dacapo-plugins', "/usr/share/locale/")
_ = t.ugettext

class ConfirmAction(qltk.Message):
	"""A message dialog that asks a yes/no question."""

	def __init__(self, *args, **kwargs):
		kwargs["buttons"] = Gtk.ButtonsType.YES_NO
		super(ConfirmAction, self).__init__(
			Gtk.MessageType.WARNING, *args, **kwargs)

	def run(self, destroy=True):
		"""Returns True if yes was clicked, False otherwise."""
		resp = super(qltk.Message, self).run()
		if destroy:
			self.destroy()
		if resp == Gtk.ResponseType.YES:
			return True
		else:
			return False

class OpenDacapo(SongsMenuPlugin):
	PLUGIN_ID = "OpenSyncLyrics"
	PLUGIN_NAME = _('Open Song in dacapo')
	PLUGIN_DESC = _("Opens the Song in dacapo).")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		super(OpenDacapo, self).__init__(*args, **kwargs)

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

		if (len(songs) > 1) and not ConfirmAction(self.plugin_window,
			_(self.PLUGIN_NAME),
			_("Open {!s} files in dacapo?").format(len(songs))
								  ).run():
			return True

		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Checking...\n\n%(current)d/%(total)d Songs done."))
		args = []
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				args.append(song.get("~filename", ""))
			if win.step():
				break
		try:
			program = 'dacapo'
			subprocess.call([program]+args)
		except:
			win.destroy()
			self.printError()
			return False
		win.destroy()


	def printError(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		for line in lines:
			print(line)

