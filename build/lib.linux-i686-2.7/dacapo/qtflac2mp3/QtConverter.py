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
		self.encoder = gst.element_factory_make('lame', 'encoder')
		# mode=1 quality=2 vbr=4 vbr-quality=2  bitrate=192
		self.encoder.set_property('mode', 4)
		self.encoder.set_property('quality', 2)
		self.encoder.set_property('vbr', 4)
		# self.encoder.set_property('bitrate', 192)
		self.encoder.set_property('vbr-quality', 1)
		self.debug = True

		self.sink = gst.element_factory_make('filesink', 'sink')
		self.converter.add(self.source, self.decoder, self.encoder, self.sink)
		gst.element_link_many(self.source, self.decoder, self.encoder, self.sink)
		self.mainloop = gobject.MainLoop()
		gobject.threads_init()
		self.context = self.mainloop.get_context()
		bus = self.converter.get_bus()
		bus.add_signal_watch()
		self.__bus_id = bus.connect("message", self.on_message)


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

	def add_mp3_encoder(self):
		cmd = 'lamemp3enc encoding-engine-quality=2 '

		if self.mp3_mode is not None:
		    properties = {
		        'cbr' : 'target=bitrate cbr=true bitrate=%s ',
		        'abr' : 'target=bitrate cbr=false bitrate=%s ',
		        'vbr' : 'target=quality cbr=false quality=%s ',
		    }

		    cmd += properties[self.mp3_mode] % self.mp3_quality

		    if 'xingmux' in available_elements and properties[self.mp3_mode][0]:
		        # add xing header when creating VBR mp3
		        cmd += '! xingmux '

		if 'id3v2mux' in available_elements:
		    # add tags
		    cmd += '! id3v2mux '

		return cmd

