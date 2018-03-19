#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# dacapoui.py
# Copyright (C) 2013 Thomas Korell <claw.strophob@music-desktop>
# 
# dacapo is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dacapo is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
	this is the graphical call for the dacapo.
	it uses Gtk+ as a filechooser with some
	checkbuttons. 
	the options are stored in the temporary config.
	it then calls the dacapo.play() function, which
	reads the config to get the options.
'''
import sys
import gettext
t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

from dacapo import errorhandling
try :
	from gi.repository import Gtk
	import os, sys
	from config import readconfig
	from dacapoHelp import SHOWPIC_CHOICES
	import dacapo 
	from pkg_resources import resource_string
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

UI_CHK_BT = {_("Shuffle Mode") : "shuffle" , _("Resume Playlist") : "resume",
	"Fullscreen Mode" : "fullscreen", "Show Synced Lyrics (karaoke)" : "showLyricsSynced"}

CONFIG = readconfig.getConfigObject()

class GUI(Gtk.FileChooserDialog):
	DEBUG = False
	
	def __init__(self):
		super(GUI, self).__init__(_("Open audiofile(s) or playlist"),
                                      None,
                                      Gtk.FileChooserAction.OPEN,
                                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		icon = readconfig.getConfigDir() + CONFIG.getConfig('gui', 'misc', 'icon')
		vbox = self.get_content_area()

		try :
			self.set_icon_from_file(icon)
		except:
			errorhandling.Error.show() 
			pass
		filter = Gtk.FileFilter()
		filter.set_name(_("Music files"))
		filter.add_pattern("*.m3u");
		filter.add_pattern("*.flac");
		filter.add_pattern("*.mp3");
		filter.add_pattern("*.ogg");
		filter.add_pattern("*.wma");
		self.add_filter(filter)

		self.chkVal = dict()

		grid = Gtk.Grid()
		grid.set_column_spacing(10)
		grid.set_margin_left(10)
		grid.set_halign(Gtk.Align.START)
		grid.set_valign(Gtk.Align.CENTER)
		grid.set_row_spacing(4)
		grid.set_column_homogeneous(False)
		label = Gtk.Label(_("Show Pictures"), xalign=0)
		grid.add(label)
		## Create ComboBox
		type_store = Gtk.ListStore(int, str)
		for i, tP in enumerate(SHOWPIC_CHOICES):
			if tP <> 'help':
				type_store.append((i,_(tP)))
		cmbPics = Gtk.ComboBox.new_with_model(type_store)
		cmbPics.set_name('showPics')
		renderer = Gtk.CellRendererText()
		cmbPics.set_active(\
			SHOWPIC_CHOICES.index(CONFIG.getConfig('gui', 'misc', 'showPics')))
		cmbPics.connect('changed', self.changed_cb, cmbPics.get_name() )
		cmbPics.pack_start(renderer, True)
		cmbPics.add_attribute(renderer, 'text', 1)
		cmbPics.set_entry_text_column(1)
		grid.attach_next_to(cmbPics, label, Gtk.PositionType.RIGHT, 1, 1)
		self.chkVal[cmbPics.get_name()] = CONFIG.getConfig('gui', 'misc', cmbPics.get_name())
		row = 1
		col = 0

		for key in UI_CHK_BT.iterkeys():
			label = Gtk.Label(key, xalign=0)
			obj = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
			obj.set_name(UI_CHK_BT[key])
			self.chkVal[UI_CHK_BT[key]] = CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key])
			obj.set_active(CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key]))
			obj.connect("notify::active", self.callback)
			grid.attach(label, col, row, 1, 1)
			grid.attach_next_to(obj, label, Gtk.PositionType.RIGHT, 1, 1)
			row += 1
			if row >= 2:
				row = 0
				col += 2

		vbox.add(grid)
		self.connect("delete-event", Gtk.main_quit)
		self.show_all()

	def callback(self, widget, name):
		# print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
		self.chkVal[widget.get_name()] = widget.get_active()

	def changed_cb(self, cmbPics, data):
		model = cmbPics.get_model()
		index = cmbPics.get_active()
		self.chkVal[data] =SHOWPIC_CHOICES[index]
		print("{!s} : {!s}".format(data, self.chkVal[data]))
		return
	


def main():
	global CONFIG
	dialog = GUI()
	response = dialog.run()
	if response == Gtk.ResponseType.ACCEPT:
		print(dialog.chkVal)
		file = dialog.get_filename()
		basedir = os.path.dirname(os.path.realpath(__file__))
		args = []
		args.append(os.path.join(basedir, __file__))
		args.append(file)
		sys.argv = args

		for key in dialog.chkVal.iterkeys():
			CONFIG.setConfig('gui', 'misc', key, dialog.chkVal[key])

		dialog.destroy()
		if args <> [] :
			try:
				dacapo.play(CONFIG)
			except SystemExit:
				pass
			except:
				errorhandling.Error.show()
				pass
		
if __name__ == "__main__":
	sys.exit(main())
        
