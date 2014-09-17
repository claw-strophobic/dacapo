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
    from dacapo.metadata import *
    from dacapo.config import readconfig
except ImportError, err:
    print "Fehler beim Importieren eines Moduls. \n"
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msgLines = ''.join(line + '\n' for line in lines)
    print ''.join('!! ' + line for line in lines)
    sys.exit(2)

class  MetaTestCase(unittest.TestCase):
    # First define a class variable that determines 
    # if setUp was ever run
    __audioFile = None
    __filename = "/Musik/mp3/Black Flag/1980 Jealous Again/01.Jealous Again.mp3"


    def setUp(self):
        self.configObject = readconfig.getConfigObject()
        playerGUI = mock.MagicMock()
        playerGUI.winState = 'fullscreen'
        playerGUI.slide_mode = 5
        self.configObject.setConfig('TEMP', Key='PLAYER', Value=playerGUI)
        self.configObject.setDebug('debugM', 'True')



    def tearDown(self):
        self.configObject = None
        # self.__audioFile = None
        # self.__filename = None
        #    self.foo.dispose()
        #    self.foo = None


    def test_can_create_instance_of_mp3_object(self):
        audioFile = getAudioFile(self.__filename)
        self.assertIsInstance(
            audioFile,
            mp3.Mp3File,
            "Konnte Metadaten-Object nicht erstellen"
            )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_retrieve_artist_from_mp3_object(self):
        audioFile = getAudioFile(self.__filename)
        artistName = audioFile.getMetaData("artist")
        self.assertTrue(artistName, "Artist ist leer")
        self.assertIsInstance(
            artistName,
            list,
            "Artist-Metadaten kommen nicht als Liste"
            )
        print("Artist: %s" % (artistName))
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_retrieve_pictures_from_mp3_object(self):
        audioFile = getAudioFile(self.__filename)
        self.assertIsInstance(
            audioFile ,
            mp3.Mp3File,
            "Konnte Metadaten-Object nicht erstellen"
            )
        audioFile.getFrontCover()
        audioFile.loadPictures()
        bilder = audioFile.preBlitDiaShow()
        self.assertIsInstance(
            bilder,
            list,
            "Bilder sind keine List"
            )

        for bild in bilder:
            print "Bild: ", bild
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

if __name__ == '__main__':
    print "starte Test"
    unittest.main(verbosity=1)

