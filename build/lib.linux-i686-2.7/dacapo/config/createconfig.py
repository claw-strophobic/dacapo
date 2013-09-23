#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkg_resources
import os, sys, shutil
import tarfile, tempfile
from datetime import datetime
from dacapo.config.mergeconfig import XMLCombiner

FILE="configarchive.tar.gz"
FILE_EXISTS_MSG="The Config-Dir already exists! Overide existing files?"

def showMsg(msg):
	import platform
	if platform.system() == 'Windows':
		import win32ui
		import win32con
		answer = win32ui.MessageBox(msg, "Error", win32con.MB_OKCANCEL)
		if answer == win32con.IDOK: return True
	else :
		import gtk
		dlg = gtk.MessageDialog(None, 
			type=gtk.MESSAGE_WARNING,
			buttons=gtk.BUTTONS_OK_CANCEL,
			message_format=msg
		)
		answer = dlg.run()
		dlg.destroy()
		if answer == -5 : return True

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


doit = True
mergeConfig = False

root_dir =  os.path.expanduser(os.path.join('~', '.dacapo'))
is_dir = os.path.isdir(root_dir)
print("does the config-dir exist? %s " % (is_dir))
if is_dir :
    doit = False
    # doit = showMsg(FILE_EXISTS_MSG)
    # print("replace the existing config-dir? %s " % (doit))

if doit: 
	tar.extractall(path=root_dir)
else:
    tempdir = tempfile.mkdtemp()
    for tarinfo in tar:
        if tarinfo.isreg():
            if os.path.isfile(os.path.join(root_dir, tarinfo.name)) :   
                # print("%s existiert bereits." % (tarinfo.name))
                if ('./dacapo.conf' == tarinfo.name) : 
                    mergeConfig = True
                    tar.extract(tarinfo, path=tempdir)
                    # print("Extracting %s to %s" % (tarinfo.name, tempdir))
            else:
                tar.extract(tarinfo, path=root_dir)
        elif tarinfo.isdir():
            if os.path.isdir(os.path.join(root_dir, tarinfo.name)) :   
                # print("%s existiert bereits." % (tarinfo.name))
                pass
            else:
                tar.extract(tarinfo, path=root_dir)
        else:
            print("%s is something else." % (tarinfo.name))
    tar.close()

if mergeConfig: 
    save_config = os.path.join(root_dir, 'dacapo.conf.' + 
        datetime.now().strftime("%Y-%m-%d %H-%M-%S" + '.bak'))
    print("save the existing configuration-file to %s" % (save_config))
    shutil.copy(os.path.join(root_dir, 'dacapo.conf'), save_config)
    print("updating the configuration")
    fileOld = os.path.join(root_dir, 'dacapo.conf')
    fileNew = os.path.join(tempdir, 'dacapo.conf')
    r = XMLCombiner((fileOld, fileNew)).combine()
    print("done.")

