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
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf
from quodlibet.util import format_size, print_exc
from quodlibet.util.dprint import print_d

from quodlibet import util, qltk, print_w, app
from quodlibet.qltk.x import Button
from quodlibet.qltk.views import AllTreeView
from quodlibet.plugins.songsmenu import SongsMenuPlugin

from mutagen.flac import FLAC, Picture
import traceback, sys
import gettext
t = gettext.translation('dacapo-plugins', "/usr/share/locale/")
t.install()

class AlbumArtWindow(qltk.Window):
	"""The main window including the search list"""
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


	def __init__(self, songs):
		super(AlbumArtWindow, self).__init__()
		self.connect("delete-event", self.on_delete)
		self.image_cache = []
		self.image_cache_size = 10
		self.search_lock = False
		self.songs = songs
		self.song = self.songs[0]
		self.coverlist = []

		self.set_title(_('Album Images'))
		self.set_icon_name(Gtk.STOCK_FIND)
		self.set_default_size(800, 550)

		self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, object)
		self.treeview = treeview = AllTreeView(self.liststore)
		self.treeview.set_headers_visible(False)
		self.treeview.set_rules_hint(True)
		self.type_store = Gtk.ListStore(int, str)
		for key in self.TYPE:
			self.type_store.append([key, self.TYPE[key]])


		targets = [("text/uri-list", 0, 0)]
		targets = [Gtk.TargetEntry.new(*t) for t in targets]

		treeview.drag_source_set(
			Gdk.ModifierType.BUTTON1_MASK, targets, Gdk.DragAction.COPY)

		treeselection = self.treeview.get_selection()
		treeselection.set_mode(Gtk.SelectionMode.SINGLE)
		## treeselection.connect('changed', self.__select_callback, image)

		##self.treeview.connect("drag-data-get",
		##     self.__drag_data_get, treeselection)

		rend_pix = Gtk.CellRendererPixbuf()
		img_col = Gtk.TreeViewColumn('Thumb')
		img_col.pack_start(rend_pix, False)
		img_col.add_attribute(rend_pix, 'pixbuf', 0)
		treeview.append_column(img_col)

		rend_pix.set_property('xpad', 2)
		rend_pix.set_property('ypad', 2)
		rend_pix.set_property('width', 56)
		rend_pix.set_property('height', 56)

		# Allow drag and drop reordering of rows
		self.treeview.set_reorderable(True)
		# when a row is selected, it emits a signal
		treeselection.connect("changed", self.on_changed)


		def escape_data(data):
			for rep in ('\n', '\t', '\r', '\v'):
				data = data.replace(rep, ' ')

			return util.escape(' '.join(data.split()))

		def cell_data(column, cell, model, iter, data):
			cover = model[iter][1]

			esc = escape_data

			txt = '<b><i>%s</i></b>' % esc(cover.desc)
			txt += _('\nType: <i>{!s}</i>').format(self.TYPE[cover.type])
			txt += _('\nResolution: <i>{!s} x {!s}</i>').format(cover.width, cover.height)
			## type_col.set_active(cover.type)

			cell.markup = txt
			cell.set_property('markup', cell.markup)

		rend = Gtk.CellRendererText()
		rend.set_property('ellipsize', Pango.EllipsizeMode.END)
		info_col = Gtk.TreeViewColumn('Info', rend)
		info_col.set_cell_data_func(rend, cell_data)

		treeview.append_column(info_col)

		sw_list = Gtk.ScrolledWindow()
		sw_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		sw_list.set_shadow_type(Gtk.ShadowType.IN)
		sw_list.add(treeview)

		widget_space = 5

		left_vbox = Gtk.VBox(False, widget_space)
		left_vbox.pack_start(sw_list, True, True, 0)

		hpaned = Gtk.HPaned()
		hpaned.set_border_width(widget_space)
		hpaned.pack1(left_vbox)
		## hpaned.pack2(image)
		hpaned.set_position(275)

		self.add(hpaned)

		self.show_all()

		self.start_search()

	def start_search(self, *data):
		audio = FLAC(self.song.get("~filename", ""))
		## if file has no images -> leave
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			return
		for img in audio.pictures:
			self.__add_cover_to_list(img)
		return True

	def __add_cover_to_list(self, cover):
		try:
			pbloader = GdkPixbuf.PixbufLoader()
			pbloader.write(cover.data)
			pbloader.close()

			size = 48

			pixbuf = pbloader.get_pixbuf().scale_simple(size, size,
				GdkPixbuf.InterpType.BILINEAR)

			thumb = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
				size + 2, size + 2)
			thumb.fill(0x000000ff)
			pixbuf.copy_area(0, 0, size, size, thumb, 1, 1)
		except (GLib.GError, IOError):
			pass
		else:
			def append(data):
				self.liststore.append(data)
			GLib.idle_add(append, [thumb, cover])
			self.coverlist.append(cover)

	def on_changed(self, selection):
		# get the model and the iterator that points at the data in the model
		(model, iter) = selection.get_selected()
		# set the label to a new value depending on the selection
		cover = model[iter][1]
		## print('\nAusgewählt: {!s} {!s}').format(cover.desc, self.TYPE[cover.type])
		return True

	def on_save(self):
		audio = FLAC(self.song.get("~filename", ""))
		## if file has no images -> leave
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			return
		## first,clear all pictures, then add the images in order
		try:
			audio.clear_pictures()
		except:
			self.printError()
			return False
		for row in self.liststore:
			img = row[1]
			try:
				audio.add_picture(img)
			except:
				self.printError()
				return False
		audio.save()
		app.window.emit("artwork-changed", [self.song])
		return True

	def on_delete(self, widget, event):
		file_changed = False
		print('\n')
		i = 0
		for row in self.liststore:
			cover = row[1]
			if (self.coverlist[i] != cover):
				file_changed = True
				print('UNGLEICH')
			i += 1
			print('{!s}: {!s} {!s}').format(i, cover.desc, self.TYPE[cover.type])

		if file_changed == True and qltk.ConfirmAction(None,
				_('Images changed'), _('The images in file <b>%s</b> were changed.'
				'\n\nOverwrite?') % util.escape(self.song.get("~filename", ""))).run():
			self.on_save()
		return

class DisplayImages(SongsMenuPlugin):
	PLUGIN_ID = "DisplayImages"
	PLUGIN_NAME = _('Display images')
	PLUGIN_DESC = _("Display images that are stored in the audiofile.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.0'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		super(DisplayImages, self).__init__(*args, **kwargs)

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

		AlbumArtWindow(songs)



	def printError(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		for line in lines:
			print(line)
		qltk.ErrorMessage(None, _('Error occured'),
                _('%s.') % lines).run()
