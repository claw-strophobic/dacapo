#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkg_resources
import os, sys
import tarfile

FILE="configarchive.tar.gz"
FILE_EXISTS_MSG="The Config-Dir already exists! Overide existing files?"

def showMsg(msg):
	import platform
	if platform.system() == 'Windows':
		import win32ui
		import win32con
		answer = win32ui.MessageBox(msg, "Error", win32con.MB_OKCANCEL)
		if answer == win32con.MB_IDOK: return True
	else :
		import gtk
		dlg = gtk.MessageDialog(None, 
			type=gtk.MESSAGE_WARNING,
			buttons=gtk.BUTTONS_OK_CANCEL,
			message_format=msg
		)
		answer = dlg.run()
		dlg.destroy()
		if answer == -5 : print "True"

	return False

is_pkg = pkg_resources.resource_exists("dacapo.config", FILE)
print("does the resource exist? %s " % (is_pkg))

if is_pkg :
	res = pkg_resources.resource_stream("dacapo.config", FILE)
else :
	print("Konnte Archiv %s nicht in den Ressourcen finden" % (FILE))
	sys.exit(1)
try : tar = tarfile.open(mode='r|gz', fileobj=res)
except : 
	print("Konnte Archiv %s nicht oeffnen" % (FILE))
	sys.exit(1)
# tar.list()

root_dir =  os.path.expanduser(os.path.join('~', '.dacapo'))
is_dir = os.path.isdir(root_dir)
print("does the config-dir exist? %s " % (is_dir))
doit = True
if is_dir :
	doit = showMsg(FILE_EXISTS_MSG)

if doit: tar.extractall(path=root_dir)


