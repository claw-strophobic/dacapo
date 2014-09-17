#!/usr/bin/python
# -*- coding: utf-8 -*-

from shutil import make_archive
import os

archive_name = os.path.join(os.path.dirname(__file__), 'configarchive')
root_dir =  os.path.join(os.path.dirname(__file__) + '/..', 'data')
base_dir = os.path.expanduser(os.path.join('~', '.dacapo'))
# make_archive(archive_name, 'gztar', root_dir, base_dir)
print("Erstelle Archiv %s aus %s" % (archive_name, root_dir))
make_archive(archive_name, 'gztar', root_dir)
print("Fertig.")
