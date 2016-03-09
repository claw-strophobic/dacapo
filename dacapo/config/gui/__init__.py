#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import gi
gi.require_version('Gtk', '3.0')
import dacapo.config.gui

from dacapo.ui.field import Field
import dacapo.ui.interface_blitobject
import dacapo.ui.blitobject
import pygame
from dacapo.config import readconfig

from gi.repository import Gtk, Gdk, GdkPixbuf
import gettext
t = gettext.translation('dacapo', "/usr/share/locale/")
t.install()

CONFIG = readconfig.getConfigObject()
ALIGNH = {
		"center": _("center"),
		"left": _("left"),
		"right": _("right"),
	}
