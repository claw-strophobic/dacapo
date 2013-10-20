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
from dacapo import errorhandling
try :
	import gtk
	import gtk.glade
	import os, sys
	import subprocess
	from config import readconfig
	from dacapoHelp import SHOWPIC_CHOICES, getLangText
	import dacapo 
	from pkg_resources import resource_string
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

UI_FILE = "dacapoui.glade"
UI_CHK_BT = {"checkShuffle" : "shuffle" , "checkResume" : "resume", 
	"checkFullscreen" : "fullscreen", "checkLyrics" : 
	"showLyricsAsPics", "checkSynced" : "showLyricsSynced"}
PLAYER_ARGS = []
CONFIG = readconfig.getConfigObject()

class GUI:
	DEBUG = False
	
	def __init__(self):
		ui_file = resource_string(__name__, UI_FILE)

		self.builder = gtk.Builder()
		self.builder.add_from_string(ui_file)
		self.builder.connect_signals(self)

		self.window = self.builder.get_object('dialog1')
		self.window.set_title(CONFIG.getConfig('gui', 'misc', 'caption'))
		icon = readconfig.getConfigDir() + CONFIG.getConfig('gui', 'misc', 'icon')
		try :
			self.window.set_icon_from_file(icon)
		except:
			errorhandling.Error.show() 
			pass
		filter = self.builder.get_object('filefilter1')
		filter.add_pattern("*.m3u");
		filter.add_pattern("*.flac");
		filter.add_pattern("*.mp3");
		filter.add_pattern("*.ogg");
		filter.add_pattern("*.wma");

		self.chkVal = dict()

		vbox2 = self.builder.get_object('vbox2')
		cmbPics = gtk.combo_box_new_text()
		cmbPics.set_title("Show Cover")
		cmbPics.set_name("showPics")
		for t in SHOWPIC_CHOICES :
			if t <> 'help' :
				cmbPics.append_text(getLangText('gui', t))

		cmbPics.set_active(\
			SHOWPIC_CHOICES.index(CONFIG.getConfig('gui', 'misc', cmbPics.name)))
		cmbPics.connect('changed', self.changed_cb, cmbPics.get_name() )
		vbox2.add(cmbPics)
		self.chkVal[cmbPics.get_name()] = CONFIG.getConfig('gui', 'misc', cmbPics.get_name())

		for key in UI_CHK_BT.iterkeys():
			obj = self.builder.get_object(key)
			obj.set_label(getLangText('gui', key))
			self.chkVal[UI_CHK_BT[key]] = CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key])
			obj.set_label(getLangText('gui', key))
			obj.set_active(CONFIG.getConfig('gui', 'misc', UI_CHK_BT[key]))
			obj.connect("toggled", self.callback, UI_CHK_BT[key])
			

		self.window.connect("destroy", self.destroy)
		self.window.show_all()

	def callback(self, widget, data=None):
		# print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
		self.chkVal[data] = widget.get_active()

	def changed_cb(self, cmbPics, data):
		model = cmbPics.get_model()
		index = cmbPics.get_active()
		self.chkVal[data] =SHOWPIC_CHOICES[index]
		return
	
	def on_buttonCancel_clicked (self, button):
		gtk.main_quit()
		
	def on_buttonOK_clicked (self, button):
		global PLAYER_ARGS
		import copy
		if self.window.get_filename() == None and\
		  self.chkVal['resume'] == False :
			self.info_msg(getLangText('gui', 'nofile'))
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
		gtk.main_quit()
		
				
	def destroy(window, self):
		gtk.main_quit()


	
	def info_msg(self, msg):
		"""
		Zeigt einen Meldungstext an
		"""
		dlg = gtk.MessageDialog(parent=self.window, 
		type=gtk.MESSAGE_INFO,
		buttons=gtk.BUTTONS_OK,
		message_format=msg
		)
		dlg.run()
		dlg.destroy()
		
def main():
	global PLAYER_ARGS
	app = GUI()
	gtk.main()
	sys.argv = PLAYER_ARGS
	if PLAYER_ARGS <> [] : dacapo.play(CONFIG)
		
if __name__ == "__main__":
    sys.exit(main())
