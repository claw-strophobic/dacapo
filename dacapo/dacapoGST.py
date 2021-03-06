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
		self._gapless = self.config.getConfig('audio_engine', 'audio_engine', 'gapless')
		self.__strTime = "00:00"
		self.is_Playing = False
		self.mainloop = GObject.MainLoop()
		GObject.threads_init()
		Gst.init(None)
		self.context = self.mainloop.get_context()
		self.__init_pipeline()
		logging.debug('GstPlayer __init__() -> done ')

	def __init_pipeline(self):

		bReplayGain = self.config.getConfig('audio_engine', 'audio_engine', 'replayGain')
		bGapless = self.config.getConfig('audio_engine', 'audio_engine', 'gapless')

		replay = Gst.ElementFactory.make("rgvolume", "replay")
		convert = Gst.ElementFactory.make("audioconvert", "convert")
		sink = Gst.ElementFactory.make("autoaudiosink", "audio_sink")

		pipeline = Gst.ElementFactory.make("playbin", "playbin")
		bin = Gst.Bin()
		bin.add(replay)
		bin.add(convert)
		bin.add(sink)

		if bReplayGain:
			logging.debug("Link replay, convert and sink")
			replay.link(convert)
			convert.link(sink)
		else:
			logging.debug("Link convert and sink")
			convert.link(sink)

		if bReplayGain:
			pad = replay.get_static_pad('sink')
		else:
			pad = convert.get_static_pad('sink')
		ghost_pad =  Gst.GhostPad.new('sink', pad)
		ghost_pad.set_active(True)
		bin.add_pad(ghost_pad)

		## Set playbin's audio sink to be our sink bin ##
		logging.debug("Set playbin's audio sink to be our sink bin")
		pipeline.set_property('audio-sink', bin)

		logging.debug("Set playbin to self.player and get bus")
		self.player = pipeline
		bus = self.player.get_bus()
		bus.add_signal_watch()
		self.__bus_id = bus.connect("message", self.on_message)

		if bGapless:
			logging.debug("Setting 'about-to-finish' -> self.on_about_to_finish")
			self.__atf_id = self.player.connect('about-to-finish', self.on_about_to_finish)

		logging.debug("Done.")

		return

	# --------------------------------------------------------------------------------------------#

	def on_about_to_finish(self, bin):
		# The current song is about to finish, if we want to play another
		# song after this, we have to do that now
		logging.debug("--> bin in on_about_to_finish ")
		if self._gapless: self.guiPlayer.play_next_song(True)

	def doGaplessPlay(self, filename):
		self.filename = filename
		self._in_gapless_transition = True
		logging.debug("playing GAPLESS: %s " % self.filename)
		self.player.set_property("uri", "file://" + self.filename)

	def doPlay(self, filename):
		self.player.set_state(Gst.State.NULL)
		self._in_gapless_transition = False
		logging.debug("playing in doPlay: %s " % filename)
		logging.debug("abspath of file: %s " % os.path.abspath(filename))
		logging.debug("realpath of file: %s " % os.path.realpath(filename))
		self.filename = filename
		if self._gapless:
			self.player.set_property("uri", "file://%s" % self.filename)
		else:
			self.player.set_property("uri", "file://" + self.filename)
			#self.player.get_by_name("file-source").set_property("location", self.filename)
		# self.player.get_by_name("file-source").set_property("location", self.filename)
		self.player.set_state(Gst.State.PLAYING)
		# Gst.gst_element_query_duration(self.player, GST_Gst.Format.TIME, time)
		# print "TIME AUS GSTREAMER: " , time
		self.getGstDuration()
		self.is_Playing = True
		self.actualTitel = filename
		logging.debug("done. leaving doplay ")

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
			# logging.debug("--> bin in on_message mit message.type %s " % t)
			if t == Gst.MessageType.EOS:
				logging.debug("--> bin in on_message mit message.type %s " % t)
				if self.stopWhenEOS:
					self.player.set_state(Gst.State.NULL)
					self.guiPlayer.play_next_song()
			elif t == Gst.MessageType.ERROR:
				logging.debug("--> bin in on_message mit message.type %s " % t)
				self.player.set_state(Gst.State.NULL)
				err, debug = message.parse_error()
				logging.debug('MESSAGE_ERROR: %r' % str(err).decode("utf8", 'replace'))
			elif message.type == Gst.MessageType.TAG:
				taglist = message.parse_tag()
				#for key in taglist.keys():
					# logging.info('MESSAGE_TAG: %s = %s' % (key, taglist[key]))
				#	logging.info('MESSAGE_TAG: %s ' % (key))
			elif message.type == Gst.MessageType.BUFFERING:
				logging.debug("--> bin in on_message mit message.type %s " % t)
				percent = message.parse_buffering()
				# self.__buffering(percent)
			elif message.type == Gst.MessageType.STREAM_START:
				self.doTrackChange()
			elif message.type == Gst.MessageType.ELEMENT:
				logging.debug("--> bin in on_message mit message.type %s " % t)
				name = ""
				if hasattr(message.get_structure(), "get_name"):
					name = message.get_structure().get_name()
					self.actualTitel = name
					logging.debug("--> setting current title: %s" % name)

				# This gets sent on song change. Because it is not in the docs
				# we can not rely on it. Additionally we check in get_position
				# which should trigger shortly after this.
				if USE_TRACK_CHANGE and self._in_gapless_transition and \
								name == "playbin-stream-changed":
					logging.debug("--> Titel hat sich geändert! %s" % name)
					self.doTrackChange()
		except Exception, err:
			errorhandling.Error.show()
			self.doEnd()


	def doTrackChange(self):
		# self.player.get_state()
		logging.debug("Do Track Change")
		self.getGstDuration()
		self.actualTitel = self.filename
		self._in_gapless_transition = False
		display_text = getattr(self.guiPlayer, "display_text", None)
		if callable(display_text):
			display_text()

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

	def getGstDuration(self):
		self.player.get_state(timeout=Gst.SECOND / 2)
		try:
			dur_int = self.player.query_duration(Gst.Format.TIME)[1]
		except:
			dur_int = -1
		if dur_int <= 0:
			logging.debug("--> Couldn't get the length of the song. Trying again.")
		dur_str = self.convert_ns(dur_int)
		self.__time = dur_int
		logging.debug("-->  {!s} {!s}".format(dur_int, dur_str))
		self.__strTime = dur_str

	def getDuration(self):
		if self.__time <= 0:
			logging.debug("--> Wrong Duration. Trying to get the real one.")
			self.getGstDuration()
		return self.__strTime

	def getNumericDuration(self):
		if self.__time <= 0:
			logging.debug("--> Wrong Duration. Trying to get the real one.")
			self.getGstDuration()
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
		logging.debug("Dauer: %s - Aktuelle Position: %s - Neue Position %s " % (
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
		try:
			self.player.set_state(Gst.State.NULL)
		except:
			pass
		self.ausschalter.set()
		self.__destroy_pipeline()
		self.mainloop.quit()

	def run(self):
		logging.debug('GstPlayer run() -> self.mainloop.run() ->start ')
		self.mainloop.run()
		logging.debug('GstPlayer run() -> done ')


if __name__ == "__main__":
	print __doc__
	print dir()
	exit(0)
