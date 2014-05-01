#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import gobject
import pygst
pygst.require("0.10")
import gst
import logging
from gst import STATE_NULL, STATE_PLAYING, STATE_PAUSED, FORMAT_TIME, MESSAGE_EOS, MESSAGE_ERROR, SECOND

class converter():

	def __init__(self):
		self.converter = gst.Pipeline('converter')

		self.source = gst.element_factory_make('filesrc', 'file-source')
		self.decoder = gst.element_factory_make('flacdec', 'decoder')
		self.conv = gst.element_factory_make("audioconvert", "converter")
		self.encoder = gst.element_factory_make('lame', 'encoder')
		self.xingmux = gst.element_factory_make('xingmux', 'xingmux')
		self.id3mux = gst.element_factory_make('id3mux', 'id3mux')
		# mode=1 quality=2 vbr=4 vbr-quality=2  bitrate=192
		# self.encoder.set_property('mode', 1)
		# self.encoder.set_property('vbr', 3)
		# self.encoder.set_property('bitrate', 192)
		self.encoder.set_property('mode', 4)
		self.encoder.set_property('quality', 2)
		self.encoder.set_property('vbr', 4)
		self.encoder.set_property('vbr-quality', 1)
		# self.encoder.set_property('error-protection', True)
		
		# id3mux means use default id3v2.3
		# use gst-inspect-0.10 lame for lame options
		# use gst-inspect-0.10 id3mux for id3mux options
		self.id3mux.set_property('write-v1', False)
		self.id3mux.set_property('write-v2', True)
		self.id3mux.set_property('v2-version', 3)
				
		self.debug = True
		self.sink = gst.element_factory_make('filesink', 'sink')
		self.converter.add(self.source, self.decoder, self.conv, self.encoder, self.xingmux, self.id3mux,  self.sink)
		# self.converter.add(self.source, self.decoder, self.encoder, self.id3mux,  self.sink)
		# gst.element_link_many(self.source, self.decoder, self.encoder, self.id3mux, self.sink)
		gst.element_link_many(self.source, self.decoder, self.conv, self.encoder, self.xingmux, self.id3mux,  self.sink)
		self.mainloop = gobject.MainLoop()
		gobject.threads_init()
		self.context = self.mainloop.get_context()
		bus = self.converter.get_bus()
		bus.add_signal_watch()
		self.__bus_id = bus.connect("message", self.on_message)
		
		if self.debug : 
			logging.debug("Encode mode: %s " % (self.encoder.get_property('mode') ))
			logging.debug("Encode quality: %s " % (self.encoder.get_property('quality') ))
			logging.debug("Encode vbr: %s " % (self.encoder.get_property('vbr') ))
			logging.debug("Encode vbr-quality: %s " % (self.encoder.get_property('vbr-quality') ))
			logging.debug("Encode bitrate: %s " % (self.encoder.get_property('bitrate') ))


	def convert(self, source, target):
		self.source.set_property('location', source)
		self.sink.set_property('location', target)
		self.converter.set_state(gst.STATE_PLAYING)
		if self.debug : logging.debug('self.mainloop.run() ->start ')	
		self.mainloop.run()
		if self.debug : logging.debug(' done ')	


	def doEnd(self):
		self.converter.set_state(STATE_NULL)
		self.mainloop.quit()
		
	
	def on_message(self, bus, message):
		t = message.type
		if t == MESSAGE_EOS:
			if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
			self.converter.set_state(STATE_NULL)
			self.mainloop.quit()
		elif t == MESSAGE_ERROR:
			if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
			self.converter.set_state(STATE_NULL)
			err, debug = message.parse_error()
			logging.debug("gPlayerGST on_message gst.MESSAGE_ERROR: %s " % err)
			self.mainloop.quit()
		elif message.type == gst.MESSAGE_TAG:
			# if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
			pass
		elif message.type == gst.MESSAGE_BUFFERING:
			if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
			percent = message.parse_buffering()
			# self.__buffering(percent)
		elif message.type == gst.MESSAGE_ELEMENT:
			if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
			name = ""
			if hasattr(message.structure, "get_name"):
				name = message.structure.get_name()



