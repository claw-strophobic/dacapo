#!/usr/bin/python
# -*- coding: utf-8 -*-
 
"""Dieses Modul enthält eine Klasse für den GStreamer. """

import errorhandling
import sys, os
try:
	import pygst
	pygst.require("0.10")
	import threading
	import datetime
	import gobject
	import gst
	import traceback
	import logging
	from config import readconfig
except ImportError, err:
	errorhandling.Error.show()
	sys.exit(2)

	# from gst import Pipeline, element_factory_make, STATE_NULL, STATE_PLAYING, STATE_PAUSED, MESSAGE_EOS, MESSAGE_ERROR

try:
    from gst import pbutils
except ImportError:
    pbutils = None


### Klassendefinitionen

class GstPlayer(threading.Thread):

    def __init__(self, playerGUI, ausschalter):
        from gst import Pipeline, element_factory_make, Format, FORMAT_TIME
        threading.Thread.__init__(self)
        self.ausschalter = ausschalter	
        self.stopWhenEOS = True
        self._last_position = 0
        self.actualTitel = ""
        self.guiPlayer = playerGUI
        self.config = readconfig.getConfigObject()
        self.debug = playerGUI.getGSDebug()
        self._gapless = playerGUI.isGapless
        self.setDuration( datetime.timedelta(seconds=0) )
        self.is_Playing = False
        self.format = Format(FORMAT_TIME)
        self.mainloop = gobject.MainLoop()
        gobject.threads_init()
        self.context = self.mainloop.get_context()
        if self._gapless : self.__init_pipelineGapless()
        else : self.__init_pipeline()
        if self.debug : logging.debug('GstPlayer __init__() -> done ')


    def __init_pipeline(self):
	    bReplayGain = self.guiPlayer.getReplayGain()
	    # Pipeline erstellen
	    self.player = gst.Pipeline("player")
	    # File-Source erstellen und der Pipeline zufügen
	    self.filesrc = gst.element_factory_make("filesrc", "file-source")
	    self.player.add(self.filesrc)

	    # (Auto-) Decoder erstellen und der Pipeline zufügen
	    self.decode = gst.element_factory_make("decodebin", "decode")
	    self.decode.connect("new-decoded-pad", self.OnDynamicPad)
	    self.player.add(self.decode)		

	    # Link den Decoder an die File-Source
	    self.filesrc.link(self.decode)

	    # Converter erstellen und zufügen
	    self.convert = gst.element_factory_make("audioconvert", "convert")
	    # self.convert.connect("about-to-finish", self.on_about_to_finish)
	    self.player.add(self.convert)

	    # ReplayGain erstellen und zufügen
	    if bReplayGain:
		    if self.debug : logging.debug("ReplayGain wird aktiviert! ")
		    self.replay = gst.element_factory_make("rgvolume", "replay")
		    self.player.add(self.replay)
		    self.convert.link(self.replay)
		    if self.debug : logging.debug("ReplayGain ist an Converter gelinkt! ")

	    # Output-Sink erstellen und zufügen
	    # self.sink = gst.element_factory_make("alsasink", "sink")
	    sinkType = self.config.getConfig('audio_engine', ' ', 'sinkType') + 'sink'
	    if self.debug : logging.debug("Versuche Sink: %s " % sinkType)
	    self.sink = gst.element_factory_make(sinkType, "sink")
	    self.player.add(self.sink)
	    if bReplayGain:
		    self.replay.link(self.sink)		
		    if self.debug : logging.debug("Sink an ReplayGain gelinkt! " )
	    else:
		    if self.debug : logging.debug("ReplayGain ist deaktiviert! \n ")
		    self.convert.link(self.sink)

	    # self.player.add(source, decoder, conv, sink)
	    # gst.element_link_many(source, self.decoder, conv, sink)

	    bus = self.player.get_bus()
	    bus.add_signal_watch()
	    self.__bus_id = bus.connect("message", self.on_message)
	    return

    def __init_pipelineGapless(self):
	    bReplayGain = self.guiPlayer.getReplayGain()
	    USE_QUEUE = True

	    # Pipeline erstellen
	    self.pipe = []
	    # self.pipe += gst.Pipeline("player")
	    sinkType = self.config.getConfig('audio_engine', ' ', 'sinkType') + 'sink'
	    if self.debug : logging.debug("Versuche Sink: %s " % sinkType )
	    self.pipe, self.name = self.GStreamerSink(sinkType)
	    # self.pipe, self.name = self.GStreamerSink("alsasink")
	    conv = gst.element_factory_make('audioconvert')
	    self.pipe = [conv] + self.pipe
	    prefix = []

	    if USE_QUEUE:
		    queue = gst.element_factory_make('queue')
		    queue.set_property('max-size-time', 500 * gst.MSECOND)
		    prefix.append(queue)

	    # playbin2 has started to control the volume through pulseaudio,
	    # which means the volume property can change without us noticing.
	    # Use our own volume element for now until this works with PA.
	    # Also, when using the queue, this removes the delay..
	    self._vol_element = gst.element_factory_make('volume')
	    prefix.append(self._vol_element)
	
	    # ReplayGain erstellen und zufügen
	    if bReplayGain:
		    if self.debug : logging.debug("ReplayGain wird aktiviert! ")
		    self.replay = gst.element_factory_make("rgvolume", "replay")
		    prefix.append(self.replay)

	    self.pipe = prefix + self.pipe
	    # --------------------------------------------------------------------------------------------#
	    bufbin = gst.Bin()
	    map(bufbin.add, self.pipe)
	    if len(self.pipe) > 1:
		    try:
			    gst.element_link_many(*self.pipe)
		    except gst.LinkError, e:
			    logging.error("Could not link GStreamer pipeline: '%s' " % e)
			    exc_type, exc_value, exc_traceback = sys.exc_info()
			    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			    for line in lines :
				    logging.error(line)
			    self.__destroy_pipeline()
			    return False

	    # Test to ensure output pipeline can preroll
	    bufbin.set_state(gst.STATE_READY)
	    result, state, pending = bufbin.get_state(timeout=gst.SECOND/2)
	    if result == gst.STATE_CHANGE_FAILURE:
		    bufbin.set_state(gst.STATE_NULL)
		    self.__destroy_pipeline()
		    return False

	    # Make the sink of the first element the sink of the bin
	    gpad = gst.GhostPad('sink', self.pipe[0].get_pad('sink'))
	    bufbin.add_pad(gpad)
	    # --------------------------------------------------------------------------------------------#


	    self.player = gst.element_factory_make("playbin2", "player")
	    # by default playbin will render video -> suppress using fakesink
	    fakesink = gst.element_factory_make("fakesink", "fakesink")
	    self.player.set_property("video-sink", fakesink)
	    # disable all video/text decoding in playbin2
	    GST_PLAY_FLAG_VIDEO = 1 << 0
	    GST_PLAY_FLAG_TEXT = 1 << 2
	    flags = self.player.get_property("flags")
	    flags &= ~(GST_PLAY_FLAG_VIDEO | GST_PLAY_FLAG_TEXT)
	    self.player.set_property("flags", flags)
	    # set the buffer for gapless playback
	    duration = float(1.5)
	    duration = int(duration * 1000) * gst.MSECOND
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

	    if not pipeline and not gst.element_factory_find('gconfaudiosink'):
	        pipeline = "autoaudiosink"
	    elif not pipeline or pipeline == "gconf":
	        pipeline = "gconfaudiosink profile=music"

	    try: 
		    pipe = [gst.parse_launch(element) for element in pipeline.split('!')]
	    except gobject.GError, err:
	        logging.warning("Invalid GStreamer output pipeline, trying default. ")
	        try: 
			    pipe = [gst.parse_launch("autoaudiosink")]
	        except gobject.GError: pipe = None
	        else: 
			    pipeline = "autoaudiosink"

	    if pipe:
	        # In case the last element is linkable with a fakesink
	        # it is not an audiosink, so we append the default pipeline
	        fake = gst.element_factory_make('fakesink')
	        try:
	            gst.element_link_many(pipe[-1], fake)
	        except gst.LinkError: pass
	        else:
	            gst.element_unlink_many(pipe[-1], fake)
	            default, default_text = GStreamerSink("")
	            if default:
	                return pipe + default, pipeline + " ! "  + default_text
	    else:
	        logging.error("Could not create default GStreamer pipeline. " )

	    return pipe, pipeline

    # --------------------------------------------------------------------------------------------#



    # create a simple function that is run when decodebin gives us the signal to let us 
    # know it got audio data for us. Use the get_pad call on the previously 
    #created audioconverter element asking to a "sink" pad.
    def OnDynamicPad(self, dbin, pad, islast):
	      if self.debug : logging.debug("OnDynamicPad Called! ")
	      pad.link(self.convert.get_pad("sink")) 

    def on_about_to_finish(self, bin):
	    #The current song is about to finish, if we want to play another
	    #song after this, we have to do that now
	    if self.debug : logging.debug("--> bin in on_about_to_finish ")
	    if self._gapless : self.guiPlayer.playNextSong(True)

    def doGaplessPlay(self, filename):
	    self.filename = filename
	    self._in_gapless_transition = True
	    if self.debug : logging.debug("playing GAPLESS: %s " % self.filename)
	    self.player.set_property("uri", "file://" + self.filename)

    def doPlay(self, filename):
	    from gst import STATE_NULL, STATE_PLAYING, STATE_PAUSED, FORMAT_TIME, MESSAGE_EOS, MESSAGE_ERROR, SECOND
	    self.player.set_state(STATE_NULL)
	    self._in_gapless_transition = False
	    if self.debug : logging.debug("playing in doPlay: %s " % filename)
	    if self.debug : logging.debug("abspath of file: %s " % os.path.abspath(filename))
	    if self.debug : logging.debug("realpath of file: %s " % os.path.realpath(filename))		
	    self.filename=filename
	    if self._gapless : self.player.set_property("uri", "file://%s" % self.filename)
	    else : self.player.get_by_name("file-source").set_property("location", self.filename)
	    # self.player.get_by_name("file-source").set_property("location", self.filename)
	
	    self.player.set_state(STATE_PLAYING)
	    #gst.gst_element_query_duration(self.player, GST_FORMAT_TIME, time)
	    # print "TIME AUS GSTREAMER: " , time
	    self.player.get_state()
	    try: 
		    duration = self.player.query_duration(self.format)[0]
		    self.setDuration( datetime.timedelta(seconds=(duration / SECOND)) )
	    except: self.setDuration( datetime.timedelta(seconds=(500 / SECOND)) )
	
	    self.is_Playing = True
	    self.actualTitel = filename


    def doUnpause(self):
	    from gst import STATE_PLAYING
	    self.player.set_state(STATE_PLAYING)
	    self.is_Playing = True
	
    def doPause(self):
	    from gst import STATE_PAUSED
	    self.player.set_state(STATE_PAUSED)
	    self.is_Playing = False
					
    def doStop(self):
        from gst import STATE_NULL
        self.player.set_state(STATE_NULL)
        self.is_Playing = False

    def setStopWhenEOS(self, value = True):
        self.stopWhenEOS = value	

    def on_message(self, bus, message):
        from gst import STATE_NULL, MESSAGE_EOS, MESSAGE_ERROR
        USE_TRACK_CHANGE = True
        t = message.type
        if t == MESSAGE_EOS:
            if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
            if self.stopWhenEOS :
                self.player.set_state(STATE_NULL)
                self.guiPlayer.playNextSong()
        elif t == MESSAGE_ERROR:
            if self.debug : logging.debug("--> bin in on_message mit message.type %s " % t)
            self.player.set_state(STATE_NULL)
            err, debug = message.parse_error()
            logging.debug("dacapoGST on_message gst.MESSAGE_ERROR: %s " % err)
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
	            self.actualTitel = name

            # This gets sent on song change. Because it is not in the docs
            # we can not rely on it. Additionally we check in get_position
            # which should trigger shortly after this.
            if USE_TRACK_CHANGE and self._in_gapless_transition and \
	            name == "playbin2-stream-changed":
		            if self.debug : logging.debug("--> Titel hat sich geändert! %s" % name)
		            self.doTrackChange()


    def doTrackChange(self) :
	    self.player.get_state()
	    try: 
		    duration = self.player.query_duration(self.format)[0]
		    self.setDuration( datetime.timedelta(seconds=(duration / gst.SECOND)) )
	    except: 
		    if self.debug : logging.debug("--> Konnte Titellänge nicht speichern! ")
		    self.setDuration( datetime.timedelta(seconds=0 ))
	    self.actualTitel = self.filename
	

    def setDuration(self, duration) :
        self.__time = duration
        hours, remainder = divmod(self.__time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # print '%s:%s:%s' % (hours, minutes, seconds)
        if self.debug : logging.debug("--> setDuration() Stunden: %s Minuten: %s Sekunden: %s " % (str(hours).zfill(2) , str(minutes).zfill(2), str(seconds).zfill(2)) )
        strTime = ""
        if hours > 0 :
            strTime = str(hours) + ":" + str(minutes).zfill(2) 
        else :
            strTime = str(minutes).zfill(1)
        strTime += ":" + str(seconds).zfill(2)
        self.__strTime = strTime

    def getDuration(self) :
        return self.__strTime

    def getNumericDuration(self) :
        return self.__time.seconds

    def queryTimeRemaining(self):
        from gst import MSECOND, SECOND, QueryError
        time = self.queryNumericPosition()
        duration = self.getNumericDuration()
        remain = duration - time
        hours, remainder = divmod(remain, 3600)
        minutes, seconds = divmod(remainder, 60)
        # if self.debug : print "--> query_position() : ", '%s:%s:%s' % (hours, minutes, seconds)
        strTime = ""
        if hours > 0 :
            strTime = str(hours) + ":" + str(minutes).zfill(2) 
        else :
            strTime = str(minutes).zfill(1)
        strTime += ":" + str(seconds).zfill(2)

        return strTime

    def queryPosition(self):
	    from gst import MSECOND, SECOND, QueryError
	    p = 0
	    if self.is_Playing:
		    try: 
			    p = self.player.query_position(self.format)[0]
			    self._last_position = p
		    except QueryError: p = self._last_position 			
	    else:
		    # During stream seeking querying the position fails.
		    # Better return the last valid one instead of 0.
		    try: p = self._last_position 
		    except BaseException: return None 

	    hours, remainder = divmod(p / SECOND, 3600)
	    minutes, seconds = divmod(remainder, 60)
	    # if self.debug : print "--> query_position() : ", '%s:%s:%s' % (hours, minutes, seconds)
	    strTime = ""
	    if hours > 0 :
		    strTime = str(hours) + ":" + str(minutes).zfill(2) 
	    else :
		    strTime = str(minutes).zfill(1)
	    strTime += ":" + str(seconds).zfill(2)

	    return strTime


    def queryNumericPosition(self):
	    from gst import MSECOND, SECOND, QueryError
	    p = 0
	    if self.is_Playing:
		    try: 
			    p = self.player.query_position(self.format)[0]
			    self._last_position = p
		    except QueryError: p = self._last_position 			
	    else:
		    # During stream seeking querying the position fails.
		    # Better return the last valid one instead of 0.
		    try: p = self._last_position 
		    except BaseException: return None 

	    hours, remainder = divmod(p / SECOND, 3600)
	    minutes, seconds = divmod(remainder, 60)
	    return (seconds + (minutes * 60))

    def queryPositionInMilliseconds(self):
	    from gst import MSECOND, SECOND, QueryError
	    p = 0
	    if self.is_Playing:
		    try: 
			    p = self.player.query_position(self.format)[0]
			    self._last_position = p
		    except QueryError: p = self._last_position 			
	    else:
		    # During stream seeking querying the position fails.
		    # Better return the last valid one instead of 0.
		    try: p = self._last_position 
		    except BaseException: return None 
	    mseconds = (p / MSECOND)
	    hours, remainder = divmod(p / SECOND, 3600)
	    minutes, seconds = divmod(remainder, 60)
	    # print("P: %s Min: %s Sec: %s MSec: %s" % (p, minutes, seconds, mseconds) )
	    return mseconds

    def seekPosition(self, pos = 0):
	    from gst import CORE_ERROR_SEEK, FORMAT_TIME, SEEK_FLAG_FLUSH, SEEK_FLAG_KEY_UNIT, MSECOND, SECOND
	    try: nanosecs, format = self.player.query_position(self.format)
	    except: return
	    try: duration_nanosecs, format = self.player.query_duration(self.format)
	    except: return
	    # print "nanosecs: %s - pos: %s - SECOND %s" % (nanosecs, pos, SECOND)
	    self._posRange = float(duration_nanosecs) / SECOND
	    self._posValue = float(nanosecs) / SECOND
	    self._posNewValue = ( float(nanosecs) / SECOND )  + float(pos)

	    seek_time_secs = self._last_position + pos
	    if self._posNewValue < 0 : self._posNewValue = 0
	    if self._posNewValue > self.__time.seconds : return
	    if self.debug : logging.debug("Dauer: %s - Aktuelle Position: %s - Neue Position %s " % (self._posRange, self._posValue, self._posNewValue))
	    try: 	self.player.seek_simple(FORMAT_TIME, SEEK_FLAG_FLUSH | SEEK_FLAG_KEY_UNIT, self._posNewValue * SECOND)
	    except CORE_ERROR_SEEK: pass 			

	    return

    def __destroy_pipeline(self):
	    try :
		    if self.__bus_id:
			    bus = self.player.get_bus()
			    bus.disconnect(self.__bus_id)
			    bus.remove_signal_watch()
			    self.__bus_id = False
	    except : pass

	    try :
		    if self.__atf_id:
			    self.player.disconnect(self.__atf_id)
			    self.__atf_id = False
	    except : pass

	    try :
		    if self.player:
			    self.player.set_state(gst.STATE_NULL)
			    self.player.get_state(timeout=gst.SECOND/2)
			    self.player = None
	    except : pass

	    self._in_gapless_transition = False
	    self._inhibit_play = False
	    self._last_position = 0

	    self._vol_element = None
	    self._eq_element = None
	
	    return

    def doEnd(self):
	    from gst import STATE_NULL
	    self.player.set_state(STATE_NULL)
	    self.ausschalter.set()
	    self.__destroy_pipeline()
	    self.mainloop.quit()
	
    def run(self):
	    if self.debug : logging.debug('GstPlayer run() -> self.mainloop.run() ->start ')	
	    self.mainloop.run()
	    if self.debug : logging.debug('GstPlayer run() -> done ')	


if __name__ == "__main__":
	print __doc__
	print dir()
	exit(0)	

