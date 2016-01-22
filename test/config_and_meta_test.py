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
from mock import MagicMock
import sys
import traceback
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
    __filename = "/Musik/flac/Black Flag/1980 Jealous Again/01.Jealous Again.flac"


    def setUp(self):
        self.configObject = readconfig.getConfigObject()
        playerGUI = MagicMock()
        playerGUI.winState = 'fullscreen'
        playerGUI.diaMode = 5
        self.configObject.setConfig('TEMP', Key='PLAYER', Value=playerGUI)
        self.configObject.setDebug('debugM', 'True')



    # def tearDown(self):
        # self.__configObject = None
        # self.__audioFile = None
        # self.__filename = None
        #    self.foo.dispose()
        #    self.foo = None

    def test_can_create_instance_of_config_object(self):
        self.assertIsInstance(
            self.configObject,
            readconfig.Config, 
            "Konnte Config-Object nicht erstellen"
            )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_retrieve_resolution_from_config_object(self):
        resolution = (
            self.configObject.getConfig('gui', 'fullscreen', 'width'),
            self.configObject.getConfig('gui', 'fullscreen', 'height')
            )
        print resolution        
        self.assertIsInstance(resolution[0], int, "Window-Resolution ist nicht integer")
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_store_and_retrieve_value_from_config_object(self):
        self.configObject.setConfig('TEMP', 'gui', 'winState', 'fullscreen')
        winState = self.configObject.getConfig('TEMP', 'gui', 'winState')
        print 'winState: ' + winState
        self.assertEqual('fullscreen', winState, 'Config-Wert konnte nicht gespeichert werden :-(')
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    ## @mock.patch('dacapo.ui.player.playerGUI')
    def test_can_create_instance_of_flac_object(self):        
        audioFile = getAudioFile(self.__filename)
        self.assertIsInstance(
            audioFile,
            flac.FlacFile,
            "Konnte Metadaten-Object nicht erstellen"
            )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_retrieve_artist_from_flac_object(self):
        audioFile = getAudioFile(self.__filename)
        artistName = audioFile.getMetaData("artist")
        self.assertTrue(artistName, "Artist ist leer")
        self.assertIsInstance(
            artistName,
            list,
            "Artist-Metadaten kommen nicht als Liste"
            )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_retrieve_section_metadata_from_config_object(self):
        textMetaData = self.configObject.getConfig('gui', 'metaData', '')
        # print "Metadata: " + str(textMetaData)
        self.assertTrue(textMetaData, "Konnte Metadaten nicht abrufen")        
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_retrieve_section_cond_from_config_object(self):
        textMetaData = self.configObject.getConfig('cond', '')
        self.assertTrue(textMetaData, "Konnte Conditions nicht abrufen")
        self.assertIsInstance(
            textMetaData,
            dict,
            "Conditions sind kein Dictionary"
            )
        for key1 in textMetaData.iterkeys() :
            if isinstance(textMetaData.get(key1), dict):
                print "Condition:  %s Wert: %s Klasse %s" % (
                    key1,
                    textMetaData.get(key1),
                    textMetaData.get(key1).__class__
                    )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_retrieve_fullscreen_fields_from_config_object(self):
        ## MetaTestCase.__configObject = readconfig.getConfigObject()
        textMetaData = self.configObject.getConfig('gui', 'fullscreen', 'fields')
        # print "Metadata: " + str(textMetaData)
        self.assertTrue(textMetaData, "Konnte Metadaten-Fields nicht abrufen")
        self.assertIsInstance(
            textMetaData,
            dict,
            "Metadaten sind kein Dictionary"
            )
        for key1 in textMetaData.iterkeys() :
            if isinstance(textMetaData.get(key1), dict):
                print "Kapitel:  %s Wert: %s Klasse %s" % (
                    key1, 
                    textMetaData.get(key1), 
                    textMetaData.get(key1).__class__
                    )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_retrieve_window_fields_from_config_object(self):
        textMetaData = self.configObject.getConfig('gui', 'window', 'fields')
        # print "Metadata: " + str(textMetaData)
        self.assertTrue(textMetaData, "Konnte Metadaten-Fields nicht abrufen")
        
        for key1 in textMetaData.iterkeys() :
            if isinstance(textMetaData.get(key1), dict):
                print "Kapitel:  %s Wert: %s Klasse %s" % (
                    key1, 
                    textMetaData.get(key1), 
                    textMetaData.get(key1).__class__
                    )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_retrieve_fullscreen_pictures_from_config_object(self):
        ## MetaTestCase.__configObject = readconfig.getConfigObject()
        textMetaData = self.configObject.getConfig('gui', 'fullscreen', 'pictures')
        # print "Metadata: " + str(textMetaData)
        self.assertTrue(textMetaData, "Konnte Pictures nicht abrufen")
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_retrieve_pictures_from_flac_object(self):
        audioFile = getAudioFile(self.__filename)
        self.assertIsInstance(
            audioFile ,
            flac.FlacFile,
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

