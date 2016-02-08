#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#	Wird mit Songs aus QuodLibet aufgerufen.
#	Es wird anhand der Dacapo-Config-Einstellungen versucht eine *.lrc zu ermitteln.
#	Falls dies gelingt, wird das LyricFlag gesetzt.
#

from gi.repository import Gtk
from quodlibet import qltk
from quodlibet.qltk.wlw import WaitLoadWindow
from quodlibet.qltk.chooser import FileChooser
from quodlibet.plugins.songsmenu import SongsMenuPlugin

class addImage(SongsMenuPlugin):
	PLUGIN_ID = "AddImage"
	PLUGIN_NAME = _('Add Image To Audiofile')
	PLUGIN_DESC = _("Add an Image to the audio file with selected image type.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		super(addImage, self).__init__(*args, **kwargs)


	def plugin_handles(self, songs):
		result = False
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				self.counter += 1
				result = True
		return result

	def plugin_songs(self, songs):
		if not qltk.ConfirmAction(self.plugin_window,
			_(self.PLUGIN_NAME),
			_("{!s} {!s}".format(self.counter, "Dateien verarbeiten?"))
								  ).run():
			return True

		choose = FileChooser(self.plugin_window, _("Select Image File"))
		files = choose.run()
		choose.destroy()
		print(files)
		win = WaitLoadWindow(
			self.plugin_window, len(songs),
			_("Adding Image.\n\n%(current)d/%(total)d Songs done."))
		for song in songs:
			if song.get("~filename", "").endswith(".flac"):
				flacFilePath = song.get("~filename", "")
				try:
					self.setImage(flacFilePath)
				except:
					return False
			if win.step():
				break
		win.destroy()


	def setImage(self, flacFilePath):
		return False
