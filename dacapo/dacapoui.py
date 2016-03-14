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
	it uses Gtk+ and glade as a filechooser with some 
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
	import subprocess
	from config import readconfig
	from dacapoHelp import SHOWPIC_CHOICES
	import dacapo 
	from pkg_resources import resource_string
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

UI_CHK_BT = {_("Shuffle Mode") : "shuffle" , _("Resume Playlist") : "resume",
	"Fullscreen Mode" : "fullscreen", "Show Song Lyrics" :
	"showLyricsAsPics", "Show Synced Lyrics (karaoke)" : "showLyricsSynced"}
PLAYER_ARGS = []
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

		## Create ComboBox
		type_store = Gtk.ListStore(int, str)
		for i, tP in enumerate(SHOWPIC_CHOICES):
			if tP <> 'help':
				type_store.append((i,_(tP)))
		cmbPics = Gtk.ComboBox.new_with_model(type_store)
		renderer = Gtk.CellRendererText()
		cmbPics.set_active(\
			SHOWPIC_CHOICES.index(CONFIG.getConfig('gui', 'misc', 'showPics')))
		cmbPics.connect('changed', self.changed_cb, cmbPics.get_name() )
		cmbPics.pack_start(renderer, True)
		cmbPics.add_attribute(renderer, 'text', 1)
		cmbPics.set_entry_text_column(1)
		vbox.add(cmbPics)
		self.chkVal[cmbPics.get_name()] = CONFIG.getConfig('gui', 'misc', cmbPics.get_name())

		for key in UI_CHK_BT.iterkeys():
			obj = Gtk.CheckButton(key)
			self.chkVal[UI_CHK_BT[key]] = CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key])
			obj.set_active(CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key]))
			obj.connect("toggled", self.callback, UI_CHK_BT[key])
			vbox.add(obj)
			
		self.connect("delete-event", Gtk.main_quit)
		self.show_all()

	def callback(self, widget, data=None):
		# print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
		self.chkVal[data] = widget.get_active()

	def changed_cb(self, cmbPics, data):
		model = cmbPics.get_model()
		index = cmbPics.get_active()
		self.chkVal[data] =SHOWPIC_CHOICES[index]
		print(self.chkVal[data])
		return
	
	def on_buttonCancel_clicked (self, button):
		Gtk.main_quit()
		
	def on_buttonOK_clicked (self, button):
		global PLAYER_ARGS
		import copy
		if self.window.get_filename() == None and\
		  self.chkVal['resume'] == False :
			self.info_msg(_('gui', 'nofile'))
			return
		path = None
		if getattr(sys, 'frozen', None):
			basedir = sys._MEIPASS
		else:
			basedir = os.path.dirname(os.path.realpath(__file__))
		args = []
		args.append(os.path.join(basedir, __file__))
		path = self.window.get_filename()
		args.append(path)

		for key in self.chkVal.iterkeys():
			CONFIG.setConfig('gui', 'misc', key, self.chkVal[key])


		self.window.destroy()
		PLAYER_ARGS = copy.deepcopy(args)
		Gtk.main_quit()
		
				
	def destroy(window, self):
		self.destroy()
		Gtk.main_quit()


	
	def info_msg(self, msg):
		"""
		Zeigt einen Meldungstext an
		"""
		dlg = Gtk.MessageDialog(parent=self.window,
		type=Gtk.MESSAGE_INFO,
		buttons=Gtk.BUTTONS_OK,
		message_format=msg
		)
		dlg.run()
		dlg.destroy()
		
def main():
	global PLAYER_ARGS
	global CONFIG
	app = GUI()
	response = app.run()
	sys.argv = PLAYER_ARGS	
	if PLAYER_ARGS <> [] :
		try:
			dacapo.play(CONFIG)
		except SystemExit:
			pass
		except:
			errorhandling.Error.show()
			pass				
		
if __name__ == "__main__":
    sys.exit(main())
        
