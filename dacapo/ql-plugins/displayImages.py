#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#

from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from quodlibet import util, qltk, app
from quodlibet.qltk.views import AllTreeView
from quodlibet.plugins.songsmenu import SongsMenuPlugin
import addImage
import mimetypes
from mutagen.flac import FLAC
import traceback, sys, copy, ntpath
import gettext
t = gettext.translation('dacapo-plugins', "/usr/share/locale/")
t.install()

TYPE = addImage.AddImageFileChooser.TYPE

def escape_data(data):
	for rep in ('\n', '\t', '\r', '\v'):
		data = data.replace(rep, ' ')

	return util.escape(' '.join(data.split()))

class ImageArea(Gtk.VBox):
	"""The image display and saving part."""

	def __init__(self, parent, song):
		super(ImageArea, self).__init__()
		self.song = song
		self.cover = None
		self.main_win = parent

		self.image = Gtk.Image()
		self.save_button = Gtk.Button(stock=Gtk.STOCK_SAVE)
		self.save_button.set_sensitive(False)
		self.save_button.connect('clicked', self.on_save)

		close_button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
		close_button.connect('clicked', lambda x: self.main_win.close())

		self.add_button = Gtk.Button(stock=Gtk.STOCK_ADD)
		self.add_button.connect('clicked', self.on_add_clicked)
		self.sub_button = Gtk.Button(stock=Gtk.STOCK_REMOVE)
		self.sub_button.set_sensitive(False)
		self.sub_button.connect('clicked', self.on_sub_clicked)

		self.type_store = Gtk.ListStore(int, str)
		for key in TYPE:
			self.type_store.append([key, TYPE[key]])
		self.type_combo = Gtk.ComboBox.new_with_model(self.type_store)
		renderer = Gtk.CellRendererText()
		self.type_combo.set_active(3)
		self.type_combo.pack_start(renderer, True)
		self.type_combo.add_attribute(renderer, 'text', 1)
		self.type_combo.connect("changed", self.on_type_combo_changed)
		self.type_combo.set_entry_text_column(1)

		self.desc = Gtk.Entry()
		self.desc.connect("changed", self.on_desc_changed)
		self.desc.set_editable(True)

		#both labels
		label_open = Gtk.Label(label=_('Description:'))
		label_open.set_use_underline(True)
		label_open.set_mnemonic_widget(self.desc)
		label_open.set_justify(Gtk.Justification.LEFT)

		label_name = Gtk.Label(label=_('Type:'), use_underline=True)
		label_name.set_use_underline(True)
		label_name.set_mnemonic_widget(self.type_combo)
		label_name.set_justify(Gtk.Justification.LEFT)

		table = Gtk.Table(rows=2, columns=2, homogeneous=False)
		table.set_row_spacing(0, 5)
		table.set_row_spacing(1, 5)
		table.set_col_spacing(0, 5)
		table.set_col_spacing(1, 5)

		table.attach(label_open, 0, 1, 0, 1)
		table.attach(label_name, 0, 1, 1, 2)

		table.attach(self.desc, 1, 2, 0, 1)
		table.attach(self.type_combo, 1, 2, 1, 2)

		self.scrolled = Gtk.ScrolledWindow()
		self.scrolled.add_with_viewport(self.image)
		self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC,
								 Gtk.PolicyType.AUTOMATIC)

		hButtonbox = Gtk.HBox()

		bbox = Gtk.VButtonBox()
		bbox.set_spacing(6)
		bbox.set_layout(Gtk.ButtonBoxStyle.END)
		bbox.pack_start(self.save_button, True, True, 0)
		bbox.pack_start(close_button, True, True, 0)
		hButtonbox.pack_start(bbox, True, True, 0)

		p_bbox = Gtk.VButtonBox()
		p_bbox.set_spacing(6)
		p_bbox.set_layout(Gtk.ButtonBoxStyle.END)
		p_bbox.pack_start(self.add_button, True, True, 0)
		p_bbox.pack_start(self.sub_button, True, True, 0)
		hButtonbox.pack_start(p_bbox, True, True, 0)

		main_hbox = Gtk.HBox()
		main_hbox.pack_start(table, False, True, 6)
		main_hbox.pack_start(hButtonbox, True, True, 0)

		main_vbox = Gtk.VBox()
		main_vbox.pack_start(main_hbox, True, True, 0)

		self.pack_start(self.scrolled, True, True, 0)
		self.pack_start(main_vbox, False, True, 5)

	def on_save(self, *data):
		self.main_win.on_save()
		self.save_button.set_sensitive(False)

	def on_add_clicked(self, *data):
		JPG_MIMES = ["image/jpeg"]
		PNG_MIMES = ["image/png"]
		choose = addImage.AddImageFileChooser(self.main_win)
		files = choose.run()
		desc = choose.get_description()
		choose.destroy()
		if (files == None) or (len(files) <= 0):
			return True

		for file in files:
			contentType = mimetypes.guess_type(file) # get Mimetype
			mimeType = contentType[0]
			if (mimeType in JPG_MIMES) or (mimeType in PNG_MIMES):
				img = addImage.get_image_size(file)
				img.mime = mimeType
				img.type = choose.imgType
				if (len(desc) <= 0):
					img.desc = ntpath.basename(file)
				else:
					img.desc = desc
				self.main_win.add_cover_to_list(img)

		self.save_button.set_sensitive(True)

	def on_sub_clicked(self, *data):
		if (self.cover == None):
			qltk.ErrorMessage(None, _('Error'),
                _("No image selected")).run()
			return
		esc = escape_data
		txt = _('Remove {!s}').format(esc(self.cover.desc))
		txt += _('\nType: {!s}').format(TYPE[self.cover.type])
		txt += _('\nResolution: {!s} x {!s}').format(self.cover.width, self.cover.height)
		print(txt)
		if not qltk.ConfirmAction(self.main_win,
			_('Remove Image'),
			txt
								  ).run():
			return True
		for row in self.main_win.liststore:
			cover = row[1]
			if cover == self.cover:
				self.main_win.liststore.remove(row.iter)
				break

		self.save_button.set_sensitive(True)

	def on_type_combo_changed(self, combo):
		combo_iter = combo.get_active_iter()
		if combo_iter:
			model = combo.get_model()
			type = model.get_value(combo_iter, 0)
			if (type <> self.cover.type):
				self.cover.type = type
				self.save_button.set_sensitive(True)

	def on_desc_changed(self, text):
		desc = text.get_text()
		if (desc <> self.cover.desc):
			self.cover.desc = desc
			self.save_button.set_sensitive(True)

	def set_cover(self, cover):
		self.cover = cover
		self.sub_button.set_sensitive(True)
		self.desc.set_text(cover.desc)
		self.type_combo.set_active(cover.type)
		try:
			pbloader = GdkPixbuf.PixbufLoader()
			pbloader.write(cover.data)
			pbloader.close()

			alloc = self.scrolled.get_allocation()
			scale_w = alloc.width
			scale_h = alloc.height

			pb_width = cover.width
			pb_height = cover.height

			if pb_width > scale_w or pb_height > scale_h:
				pb_ratio = float(pb_width) / pb_height
				win_ratio = float(scale_w) / scale_h

				if pb_ratio > win_ratio:
					scale_w = scale_w
					scale_h = int(scale_w / pb_ratio)
				else:
					scale_w = int(scale_h * pb_ratio)
					scale_h = scale_h

				#the size is wrong if the window is about to close
				if scale_w <= 0 or scale_h <= 0:
					return

			pixbuf = pbloader.get_pixbuf().scale_simple(scale_w, scale_h,
				GdkPixbuf.InterpType.BILINEAR)
			pb_width = pixbuf.get_width()
			pb_height = pixbuf.get_height()

			thumb = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8,
				scale_w + 2, scale_h + 2)
			thumb.fill(0x000000ff)
			pixbuf.copy_area(0, 0, scale_w, scale_h, thumb, 1, 1)
		except (GLib.GError, IOError):
			pass
		else:
			self.image.set_from_pixbuf(pixbuf)


	def __scale_pixbuf(self, *data):
		pixbuf = self.image

		pb_width = pixbuf.get_width()
		pb_height = pixbuf.get_height()

		alloc = self.scrolled.get_allocation()
		width = alloc.width
		height = alloc.height

		if pb_width > width or pb_height > height:
			pb_ratio = float(pb_width) / pb_height
			win_ratio = float(width) / height

			if pb_ratio > win_ratio:
				scale_w = width
				scale_h = int(width / pb_ratio)
			else:
				scale_w = int(height * pb_ratio)
				scale_h = height

			#the size is wrong if the window is about to close
			if scale_w <= 0 or scale_h <= 0:
				return



class AlbumArtWindow(qltk.Window):
	"""The main window including the search list"""

	def __init__(self, song, parent):
		super(AlbumArtWindow, self).__init__()
		self.connect("delete-event", self.on_delete)
		self.song = song
		self.parent = parent
		self.coverlist = []

		self.set_title(_('Album Images'))
		self.set_icon_name(Gtk.STOCK_FIND)
		self.set_default_size(820, 550)

		self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, object)
		self.treeview = treeview = AllTreeView(self.liststore)
		self.treeview.set_headers_visible(False)
		self.treeview.set_rules_hint(True)
		self.row_no = 0

		targets = [("text/uri-list", 0, 0)]
		targets = [Gtk.TargetEntry.new(*t) for t in targets]

		treeview.drag_source_set(
			Gdk.ModifierType.BUTTON1_MASK, targets, Gdk.DragAction.COPY)

		image = ImageArea(self, self.song)
		treeselection = self.treeview.get_selection()
		treeselection.set_mode(Gtk.SelectionMode.SINGLE)
		# when a row is selected, it emits a signal
		treeselection.connect('changed', self.__select_callback, image)

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


		def cell_data(column, cell, model, iter, data):
			cover = model[iter][1]

			esc = escape_data

			txt = '<b><i>%s</i></b>' % esc(cover.desc)
			txt += _('\nType: <i>{!s}</i>').format(TYPE[cover.type])
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
		# self.add(sw_list)
		widget_space = 5
		hpaned = Gtk.HPaned()
		hpaned.set_border_width(widget_space)
		hpaned.pack1(sw_list)
		hpaned.pack2(image)
		hpaned.set_position(275)

		self.add(hpaned)

		self.show_all()

		self.start_search()
		treeselection.select_path(1)

	def start_search(self, *data):
		audio = FLAC(self.song.get("~filename", ""))
		## if file has no images -> leave
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			return
		for img in audio.pictures:
			self.add_cover_to_list(img)
		return True

	def add_cover_to_list(self, cover):
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
			self.coverlist.append(copy.deepcopy(cover))

	def __select_callback(self, selection, image):
		# get the model and the iterator that points at the data in the model
		(model, iter) = selection.get_selected()
		if not iter:
			return
		# cover = model.get_value(iter, 1)
		cover = model[iter][1]
		image.set_cover(cover)

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
		count = 0
		if (audio.pictures is None) or (len(audio.pictures) <= 0):
			pass
		else:
			count = str(len(audio.pictures))

		self.song["pictures"] = count
		app.window.emit("artwork-changed", [self.song])
		del self.coverlist[:]
		self.liststore.clear()
		self.start_search()
		return True

	def on_delete(self, widget, event):
		file_changed = False
		i = 0
		if len(self.liststore) <> len(self.coverlist):
			file_changed = True

		for row in self.liststore:
			cover = row[1]
			if (self.coverlist[i].data != cover.data) \
				or (self.coverlist[i].desc != cover.desc)  \
				or (self.coverlist[i].type != cover.type) :
				file_changed = True
			i += 1

		if file_changed == True and qltk.ConfirmAction(None,
				_('Images changed'), _('The images in file <b>%s</b> were changed.'
				'\n\nOverwrite?') % util.escape(self.song.get("~filename", ""))).run():
			self.on_save()
		return

class DisplayImages(SongsMenuPlugin):
	PLUGIN_ID = "DisplayChangeImages"
	PLUGIN_NAME = _('Display & change images')
	PLUGIN_DESC = _("Display and change images that are stored in the audiofile.")
	PLUGIN_ICON = Gtk.STOCK_EXECUTE
	PLUGIN_VERSION = '1.0.1'

	def __init__(self, *args, **kwargs):
		self.counter = 0
		mimetypes.add_type('image/jpeg', '.jpeg')
		mimetypes.add_type('image/jpeg', '.jpg')
		mimetypes.add_type('image/png', '.png')
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

		for song in songs:
			AlbumArtWindow(song, self)



	def printError(self):
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		for line in lines:
			print(line)
		qltk.ErrorMessage(None, _('Error occured'),
                _('%s.') % lines).run()
