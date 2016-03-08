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
import dacapo.ui.blitobject

def find_between(s, first, last ):
	try:
		start = s.index( first ) + len( first )
		end = s.index( last, start )
		return s[start:end]
	except ValueError:
		return ""


class BlitInterface(object):

	def getBlitObject( self ):
		raise NotImplementedError( "Should have implemented this" )

	def doFillBackground(self, screen, color, update=False):
		try: screen.fill(color)
		except:
			raise pygame.get_error()
			return
		# Fenstergröße holen
		width, height = screen.get_size()
		print("Set Background-Color {!s} on size {!s}x{!s}".format(str(color), width, height))
		image = pygame.Surface(screen.get_size())
		image.fill(color)
		obj = dacapo.ui.blitobject.BlitObject('Background')
		obj.renderedData = image
		obj.setBlitRect((0,0), screen.get_size())
		self.doBlitObject(screen, obj, update)
		return

	def doBlitObject(self, screen, blitObj, update=False):
		if (screen is None):
			print("Screen is None for blit: %s " % (blitObj.name))
			return False
		if (blitObj is None):
			print("Rect is None for blit: %s " % (blitObj.name))
			return False
		if (blitObj.renderedData is None):
			print("RenderedData is None for blit: %s " % (blitObj.name))
			return False
		print( \
			"Trying blit for %s at position %s " % (
				blitObj.name, blitObj.blitPos))
		if not screen.get_locked():
			try: screen.blit(blitObj.renderedData, blitObj.rect)
			except pygame.error, err:
				print( \
					"Error at self.screen.blit(%s, (%s)) . %s " % (
						blitObj.name, blitObj.rect, err))
				return False
		if not screen.get_locked() and update == True:
			screen.lock()
			try:
				pygame.display.update(blitObj.rect)
			# try: pygame.display.flip()
			except pygame.error, err:
				print( \
					"Error at pygame.display.update(%s) . %s " % (
						blitObj.rect, err))
				return False
			screen.unlock()
