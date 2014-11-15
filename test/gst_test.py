#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
#! /usr/bin/python
###############################################################################
# small GTK/GStreamer Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
###############################################################################


import unittest
import mock
import sys
try:
    from dacapo.dacapoGST import GstPlayer
    from dacapo.config import readconfig    
except ImportError, err:
    print "Fehler beim Importieren eines Moduls. \n"
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msgLines = ''.join(line + '\n' for line in lines)
    print ''.join('!! ' + line for line in lines)
    sys.exit(2)

class  RenderTestCase(unittest.TestCase):

    __filename = "/Musik/flac/Black Flag/1980 Jealous Again/01.Jealous Again.flac"


    def setUp(self):
        self.verbosity=4
        configObject = readconfig.getConfigObject()
        player = mock.MagicMock()
        player.playNextSong.return_value = None
        configObject.setConfig('TEMP', Key='PLAYER', Value=player)


    def testCanCreateInstanceOfGstPlayerObject(self):
        schalter = mock.MagicMock()
        gstPlayer = GstPlayer(schalter)
	gstPlayer.start()
        self.assertIsInstance(
            gstPlayer , 
            GstPlayer, 
            "Konnte GstPlayer-Object nicht erstellen"
            )
        gstPlayer.doEnd()
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def testRetrieveDurationAndPositionFromGstPlayerObject(self):
        schalter = mock.MagicMock()
        gstPlayer = GstPlayer(schalter)
	gstPlayer.start()
        self.assertIsInstance(
            gstPlayer , 
            GstPlayer, 
            "Konnte GstPlayer-Object nicht erstellen"
            )
        gstPlayer.doPlay(self.__filename)        
        dur = gstPlayer.getDuration()
        print "Duration: " + dur
        position = gstPlayer.queryPosition()
        print "Position: " + position
        gstPlayer.doPause()
        gstPlayer.doStop()
        gstPlayer.doEnd()
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

          
if __name__ == '__main__':
    print "starte Test"
    unittest.main(verbosity=1)
#gstPlayer.doPlay(self.filename)
