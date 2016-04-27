#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Dieses Modul enthält eine Klasse für den GStreamer. """

import errorhandling
import sys, os

try:
	#import pygst

	# pyGst.require("0.10")
	import threading
	import time
	import gi
	from gi.repository import GObject
	gi.require_version('Gst', '1.0')
	from gi.repository import Gst
	import traceback
	import logging
	from config import readconfig
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

### Klassendefinitionen

class GstPlayer(threading.Thread):
	def __init__(self, ausschalter):
		threading.Thread.__init__(self)
		self.ausschalter = ausschalter
		self.stopWhenEOS = True
		self._last_position = 0
		self.actualTitel = ""
		self.config = readconfig.getConfigObject()
		self.guiPlayer = self.config.getConfig('TEMP', Key='PLAYER')
		self.debug = self.config.getConfig('debug', ' ', 'debugS')
		self._gapless = self.config.getConfig('audio_engine', 'audio_engine', 'gapless')
		self.__strTime = "00:00"
		self.is_Playing = False
		self.mainloop = GObject.MainLoop()
		GObject.threads_init()
		Gst.init(None)
		self.context = self.mainloop.get_context()
		if self._gapless:
			self.__init_pipelineGapless()
		else:
			self.__init_pipeline()
		if self.debug: logging.debug('GstPlayer __init__() -> done ')

	def __init_pipeline(self):
		if self.debug: logging.debug("start creating pipeline! ")
		bReplayGain = self.config.getConfig('audio_engine', 'audio_engine', 'replayGain')
		# Pipeline erstellen
		self.player = Gst.Pipeline()
		# File-Source erstellen und der Pipeline zufügen
		self.filesrc = Gst.ElementFactory.make("filesrc", "file-source")
		self.player.add(self.filesrc)

		# (Auto-) Decoder erstellen und der Pipeline zufügen
		self.decode = Gst.ElementFactory.make("decodebin", "decode")
		self.decode.connect("pad-added", self.OnDynamicPad)
		self.player.add(self.decode)

		# Link den Decoder an die File-Source
		self.filesrc.link(self.decode)

		# Converter erstellen und zufügen
		self.convert = Gst.ElementFactory.make("audioconvert", "convert")
		# self.convert.connect("about-to-finish", self.on_about_to_finish)
		self.player.add(self.convert)

		# ReplayGain erstellen und zufügen
		if bReplayGain:
			if self.debug: logging.debug("ReplayGain wird aktiviert! ")
			self.replay = Gst.ElementFactory.make("rgvolume", "replay")
			self.player.add(self.replay)
			self.convert.link(self.replay)
			if self.debug: logging.debug("ReplayGain ist an Converter gelinkt! ")

		# Output-Sink erstellen und zufügen
		# self.sink = Gst.ElementFactory.make("alsasink", "sink")
		sinkType = self.config.getConfig('audio_engine', ' ', 'sinkType') + 'sink'
		if self.debug: logging.debug("Versuche Sink: %s " % sinkType)
		self.sink = Gst.ElementFactory.make(sinkType, "sink")
		self.player.add(self.sink)
		if bReplayGain:
			self.replay.link(self.sink)
			if self.debug: logging.debug("Sink an ReplayGain gelinkt! ")
		else:
			if self.debug: logging.debug("ReplayGain ist deaktiviert! \n ")
			self.convert.link(self.sink)

		bus = self.player.get_bus()
		bus.add_signal_watch()
		self.__bus_id = bus.connect("message", self.on_message)
		return

	def __init_pipelineGapless(self):
		if self.debug: logging.debug("start creating gapless pipeline! ")
		bReplayGain = self.config.getConfig('audio_engine', 'audio_engine', 'replayGain')
		USE_QUEUE = True

		# Pipeline erstellen
		self.pipe = []
		# self.pipe += Gst.Pipeline("player")
		sinkType = self.config.getConfig('audio_engine', ' ', 'sinkType') + 'sink'
		if self.debug: logging.debug("Versuche Sink: %s " % sinkType)
		self.pipe, self.name = self.GStreamerSink(sinkType)
		# self.pipe, self.name = self.GStreamerSink("alsasink")
		conv = Gst.ElementFactory.make('audioconvert')
		self.pipe = [conv] + self.pipe
		prefix = []

		if USE_QUEUE:
			queue = Gst.ElementFactory.make('queue')
			queue.set_property('max-size-time', 500 * Gst.MSECOND)
			prefix.append(queue)

		# playbin2 has started to control the volume through pulseaudio,
		# which means the volume property can change without us noticing.
		# Use our own volume element for now until this works with PA.
		# Also, when using the queue, this removes the delay..
		self._vol_element = Gst.ElementFactory.make('volume')
		prefix.append(self._vol_element)

		# ReplayGain erstellen und zufügen
		if bReplayGain:
			if self.debug: logging.debug("ReplayGain wird aktiviert! ")
			self.replay = Gst.ElementFactory.make("rgvolume", "replay")
			prefix.append(self.replay)

		self.pipe = prefix + self.pipe
		# --------------------------------------------------------------------------------------------#
		bufbin = Gst.Bin()
		map(bufbin.add, self.pipe)
		if len(self.pipe) > 1:
			try:
				Gst.element_link_many(*self.pipe)
			except Gst.LinkError, e:
				logging.error("Could not link GStreamer pipeline: '%s' " % e)
				exc_type, exc_value, exc_traceback = sys.exc_info()
				lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
				for line in lines:
					logging.error(line)
				self.__destroy_pipeline()
				return False

		# Test to ensure output pipeline can preroll
		bufbin.set_state(Gst.State.READY)
		result, state, pending = bufbin.get_state(timeout=Gst.SECOND / 2)
		if result == Gst.State.CHANGE_FAILURE:
			bufbin.set_state(Gst.State.NULL)
			self.__destroy_pipeline()
			return False

		# Make the sink of the first element the sink of the bin
		gpad = Gst.GhostPad.new('sink', self.pipe[0].get_pad('sink'))
		bufbin.add_pad(gpad)
		# --------------------------------------------------------------------------------------------#


		self.player = Gst.ElementFactory.make("playbin", "player")
		# by default playbin will render video -> suppress using fakesink
		fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)
		# disable all video/text decoding in playbin2
		GST_PLAY_FLAG_VIDEO = 1 << 0
		GST_PLAY_FLAG_TEXT = 1 << 2
		flags = self.player.get_property("flags")
		flags &= ~(GST_PLAY_FLAG_VIDEO | GST_PLAY_FLAG_TEXT)
		self.player.set_property("flags", flags)
		# set the buffer for gapless playback
		duration = float(1.5)
		duration = int(duration * 1000) * Gst.MSECOND
		self.player.set_property('buffer-duration', duration)
		# link the function for gapless playback
		self.__atf_id = self.player.connect("about-to-finish", self.on_about_to_finish)

		# --------------------------------------------------------------------------------------------#

		# Hier wird die Ausgabe von playbin2 auf bufbin gesetzt!
		self.player.set_property('audio-sink', bufbin)

		bus = self.player.get_bus()
		bus.add_signal_watch()
		self.__bus_id = bus.connect("message", self.on_message)

		return

	# --------------------------------------------------------------------------------------------#

	def GStreamerSink(self, pipeline):
		"""Try to create a GStreamer pipeline:
		* Try making the pipeline (defaulting to gconfaudiosink or
		  autoaudiosink on Windows).
		* If it fails, fall back to autoaudiosink.
		* If that fails, return None

		Returns the pipeline's description and a list of disconnected elements."""

		if not pipeline and not Gst.element_factory_find('gconfaudiosink'):
			pipeline = "autoaudiosink"
		elif not pipeline or pipeline == "gconf":
			pipeline = "gconfaudiosink profile=music"

		try:
			pipe = [Gst.parse_launch(element) for element in pipeline.split('!')]
		except GObject.GError, err:
			logging.warning("Invalid GStreamer output pipeline, trying default. ")
			try:
				pipe = [Gst.parse_launch("autoaudiosink")]
			except GObject.GError:
				pipe = None
			else:
				pipeline = "autoaudiosink"

		if pipe:
			# In case the last element is linkable with a fakesink
			# it is not an audiosink, so we append the default pipeline
			fake = Gst.ElementFactory.make('fakesink')
			try:
				pipe[-1].link(fake)
			except Gst.LinkError:
				pass
			else:
				Gst.element_unlink_many(pipe[-1], fake)
				default, default_text = pyGst.GStreamerSink("")
				if default:
					return pipe + default, pipeline + " ! " + default_text
		else:
			logging.error("Could not create default GStreamer pipeline. ")

		return pipe, pipeline

		# --------------------------------------------------------------------------------------------#



		# create a simple function that is run when decodebin gives us the signal to let us
		# know it got audio data for us. Use the get_pad call on the previously

	# created audioconverter element asking to a "sink" pad.
	def OnDynamicPad(self, dbin, pad):
		try:
			string = pad.query_caps(None).to_string()
			if self.debug: logging.debug("OnDynamicPad Called: {!s}".format(string))
			pad.link(self.convert.get_static_pad("sink"))
		except Exception, err:
			errorhandling.Error.show()
			self.doEnd()

	def on_about_to_finish(self, bin):
		# The current song is about to finish, if we want to play another
		# song after this, we have to do that now
		if self.debug: logging.debug("--> bin in on_about_to_finish ")
		if self._gapless: self.guiPlayer.play_next_song(True)

	def doGaplessPlay(self, filename):
		self.filename = filename
		self._in_gapless_transition = True
		if self.debug: logging.debug("playing GAPLESS: %s " % self.filename)
		self.player.set_property("uri", "file://" + self.filename)

	def doPlay(self, filename):
		self.player.set_state(Gst.State.NULL)
		self._in_gapless_transition = False
		if self.debug: logging.debug("playing in doPlay: %s " % filename)
		if self.debug: logging.debug("abspath of file: %s " % os.path.abspath(filename))
		if self.debug: logging.debug("realpath of file: %s " % os.path.realpath(filename))
		self.filename = filename
		if self._gapless:
			self.player.set_property("uri", "file://%s" % self.filename)
		else:
			self.player.get_by_name("file-source").set_property("location", self.filename)
		# self.player.get_by_name("file-source").set_property("location", self.filename)
		self.player.set_state(Gst.State.PLAYING)
		# Gst.gst_element_query_duration(self.player, GST_Gst.Format.TIME, time)
		# print "TIME AUS GSTREAMER: " , time
		self.setDuration()
		self.is_Playing = True
		self.actualTitel = filename
		if self.debug: logging.debug("done. leaving doplay ")

	def doUnpause(self):
		self.player.set_state(Gst.State.PLAYING)
		self.is_Playing = True

	def doPause(self):
		self.player.set_state(Gst.State.PAUSED)
		self.is_Playing = False

	def doStop(self):
		self.player.set_state(Gst.State.NULL)
		self.is_Playing = False

	def setStopWhenEOS(self, value=True):
		self.stopWhenEOS = value

	def on_message(self, bus, message):
		try:
			USE_TRACK_CHANGE = True
			t = message.type
			# if self.debug: logging.debug("--> bin in on_message mit message.type %s " % t)
			if t == Gst.MessageType.EOS:
				if self.debug: logging.debug("--> bin in on_message mit message.type %s " % t)
				if self.stopWhenEOS:
					self.player.set_state(Gst.State.NULL)
					self.guiPlayer.play_next_song()
			elif t == Gst.MessageType.ERROR:
				if self.debug: logging.debug("--> bin in on_message mit message.type %s " % t)
				self.player.set_state(Gst.State.NULL)
				err, debug = message.parse_error()
				logging.debug('MESSAGE_ERROR: %r' % str(err).decode("utf8", 'replace'))
			elif message.type == Gst.MessageType.TAG:
				# if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
				taglist = message.parse_tag()
				#for key in taglist.keys():
					# logging.info('MESSAGE_TAG: %s = %s' % (key, taglist[key]))
				#	logging.info('MESSAGE_TAG: %s ' % (key))
			elif message.type == Gst.MessageType.BUFFERING:
				if self.debug: logging.debug("--> bin in on_message mit message.type %s " % t)
				percent = message.parse_buffering()
				# self.__buffering(percent)
			elif message.type == Gst.MessageType.ELEMENT:
				if self.debug: logging.debug("--> bin in on_message mit message.type %s " % t)
				name = ""
				if hasattr(message.structure, "get_name"):
					name = message.structure.get_name()
					self.actualTitel = name

				# This gets sent on song change. Because it is not in the docs
				# we can not rely on it. Additionally we check in get_position
				# which should trigger shortly after this.
				if USE_TRACK_CHANGE and self._in_gapless_transition and \
								name == "playbin-stream-changed":
					if self.debug: logging.debug("--> Titel hat sich geändert! %s" % name)
					self.doTrackChange()
		except Exception, err:
			errorhandling.Error.show()
			self.doEnd()


	def doTrackChange(self):
		# self.player.get_state()
		self.setDuration()
		self.actualTitel = self.filename

	def convert_ns(self, t):
		# This method was submitted by Sam Mason.
		# It's much shorter than the original one.
		s,ns = divmod(t, 1000000000)
		m,s = divmod(s, 60)

		if m < 60:
			return "%02i:%02i" %(m,s)
		else:
			h,m = divmod(m, 60)
			return "%i:%02i:%02i" %(h,m,s)

	def setDuration(self):
		self.player.get_state(timeout=Gst.SECOND / 2)
		dur_int = self.player.query_duration(Gst.Format.TIME)[1]
		if dur_int == -1:
			if self.debug: logging.debug("--> setDuration() Couldn't get the length of the song")
		dur_str = self.convert_ns(dur_int)
		self.__time = dur_int
		if self.debug: logging.debug("--> setDuration() {!s} {!s}".format(dur_int, dur_str))
		self.__strTime = dur_str

	def getDuration(self):
		return self.__strTime

	def getNumericDuration(self):
		return self.__time

	def queryTimeRemaining(self):
		time = self.queryNumericPosition()
		duration = self.getNumericDuration()
		remain = duration - time
		return self.convert_ns(remain)

	def queryPosition(self):
		strTime = self.convert_ns(self.queryNumericPosition())
		return strTime

	def queryNumericPosition(self):
		p = 0
		if self.is_Playing:
			try:
				p = self.player.query_position(Gst.Format.TIME)[1]
				self._last_position = p
			except BaseException:
				p = self._last_position
		else:
			# During stream seeking querying the position fails.
			# Better return the last valid one instead of 0.
			try:
				p = self._last_position
			except BaseException:
				return None
		return p

	def queryPositionInMilliseconds(self):
		p = self.queryNumericPosition()
		mseconds = (p / Gst.MSECOND)
		return mseconds

	def seekPosition(self, pos=0):
		nanosecs = self.queryNumericPosition()
		duration_nanosecs = self.getNumericDuration()
		# print "nanosecs: %s - pos: %s - SECOND %s" % (nanosecs, pos, SECOND)
		self._posRange = float(duration_nanosecs) / Gst.SECOND
		self._posValue = float(nanosecs) / Gst.SECOND
		self._posNewValue = (float(nanosecs) / Gst.SECOND) + float(pos)

		seek_time_secs = self._last_position + pos
		if self._posNewValue < 0: self._posNewValue = 0
		if self._posNewValue > self._posRange: return
		if self.debug: logging.debug("Dauer: %s - Aktuelle Position: %s - Neue Position %s " % (
		self._posRange, self._posValue, self._posNewValue))
		try:
			self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, self._posNewValue * Gst.SECOND)
		except Gst.CORE_ERROR_SEEK:
			pass

		return

	def __destroy_pipeline(self):
		try:
			if self.__bus_id:
				bus = self.player.get_bus()
				bus.disconnect(self.__bus_id)
				bus.remove_signal_watch()
				self.__bus_id = False
		except:
			pass

		try:
			if self.__atf_id:
				self.player.disconnect(self.__atf_id)
				self.__atf_id = False
		except:
			pass

		try:
			if self.player:
				self.player.set_state(Gst.State.NULL)
				self.player.get_state(timeout=Gst.SECOND / 2)
				self.player = None
		except:
			pass

		self._in_gapless_transition = False
		self._inhibit_play = False
		self._last_position = 0

		self._vol_element = None
		self._eq_element = None

		return

	def doEnd(self):
		self.player.set_state(Gst.State.NULL)
		self.ausschalter.set()
		self.__destroy_pipeline()
		self.mainloop.quit()

	def run(self):
		if self.debug: logging.debug('GstPlayer run() -> self.mainloop.run() ->start ')
		self.mainloop.run()
		if self.debug: logging.debug('GstPlayer run() -> done ')


if __name__ == "__main__":
	print __doc__
	print dir()
	exit(0)
