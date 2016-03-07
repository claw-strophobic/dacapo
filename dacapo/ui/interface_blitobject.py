#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Korell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
import pygame
import logging
import dacapo.ui.blitobject

class BlitInterface(object):

	def getBlitObject( self ):
		raise NotImplementedError( "Should have implemented this" )

	def doBlitObject(self, screen, object, update=False):
		if (screen == None):
			logging.warning("Screen is None for blit: %s " % (object.name))
			return False
		if (self.getBlitObject() == None):
			logging.warning("Rect is None for blit: %s " % (object.name))
			return False
		logging.debug( \
			"Trying blit for %s at position %s " % (
				object.name, object.blitPos))
		if not screen.get_locked():
			try: screen.blit(object.renderedData, object.rect)
			except pygame.error, err:
				logging.warning( \
					"Error at self.screen.blit(%s, (%s)) . %s " % (
						object.name, object.rect, err))
				return False
		if not screen.get_locked() and update == True:
			screen.lock()
			try:
				pygame.display.update(object.rect)
			# try: pygame.display.flip()
			except pygame.error, err:
				logging.error( \
					"Error at pygame.display.update(%s) . %s " % (
						object.rect, err))
				return False
			screen.unlock()
