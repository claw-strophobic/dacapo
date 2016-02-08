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
from mutagen.flac import FLAC, Picture
import mimetypes
import traceback, sys


class AddImageFileChooser(FileChooser):

	def __init__(self, parent):
		super(AddImageFileChooser, self).__init__(parent, _("Select Image File"))
		filter = Gtk.FileFilter()
		filter.set_name("Image files")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/png")
		self.add_filter(filter)


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
		if not qltk.ConfirmAction(self.plugin_window,
			_(self.PLUGIN_NAME),
			_("{!s} {!s}".format(self.counter, "Dateien verarbeiten?"))
								  ).run():
			return True

		###choose = FileChooser(self.plugin_window, _("Select Image File"))
		choose = AddImageFileChooser(self.plugin_window)
		files = choose.run()
		choose.destroy()
		print(files)
		for file in files:
			contentType = mimetypes.guess_type(file) # get Mimetype
			mimeType = contentType[0]
			if (mimeType in self.JPG_MIMES) or (mimeType in self.PNG_MIMES):
				imgdata = open(file).read()
				img = Picture()
				img.mime = mimeType
				img.type = 3
				img.desc = u'Albumcover'
				img.data = imgdata
				self.imgFiles.append(img)

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
					exc_type, exc_value, exc_traceback = sys.exc_info()
					lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
					for line in lines:
						print(line)
					return False
			if win.step():
				break
		win.destroy()


	def setImage(self, song):
		self.loadStoredPictures(song)
		return False

	def loadStoredPictures(self, song):
		audio = FLAC(song.get("~filename", ""))

		if len(self.imgFiles) <= 1:
			return

		print('Insgesamt %s Bilder' % (len(self.imgFiles)))
		for p in self.imgFiles:
			print('Bild gefunden. Typ {0}: {1}'.format(p.type, p.desc.encode('UTF-8')))
			try:
				audio.add_picture(p)
				audio.save()
				print(u'Bild hinzugefügt')

			except:
				print(u'FEHLER beim Speichern des Bildes:')
		return
