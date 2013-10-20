# -*- coding: utf-8 -*-
# 
# Copyright (c) 2013 Thomas Korell <claw DOT strophob AT gmx DOT de>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

class Error():
	@staticmethod 
	def show():
		import sys
		import traceback

		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		msgLines = ''.join(line + '\n' for line in lines)
		print ''.join('!! ' + line for line in lines)  # Log it or whatever here

		import platform
		if platform.system() == 'Windows':
			import win32ui
			import win32con
			win32ui.MessageBox(msgLines, "Error", win32con.MB_OK)
		else :
			import gtk
			dlg = gtk.MessageDialog(None, 
				type=gtk.MESSAGE_ERROR,
				buttons=gtk.BUTTONS_OK,
				message_format=msgLines
			)
			dlg.run()
			dlg.destroy()

		return

