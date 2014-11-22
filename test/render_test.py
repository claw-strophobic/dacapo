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
    from dacapo.ui import renderfonts
    from dacapo.metadata import *
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
        configObject.setConfig('TEMP', Key='FULLSCREEN', Value=True)
        configObject.setConfig('TEMP', 'gui', 'winState', 'fullscreen')
        configObject.setConfig('TEMP', Key='FILENAME', Value=self.__filename)
        ## Playlisten-Objekt
        oPlaylist = mock.MagicMock()
        oPlaylist.isPlaylist.return_value = True
        configObject.setConfig('TEMP', Key='PLAYLIST', Value=oPlaylist)
        ## GStreamer-Player
        playerGST = mock.MagicMock()
        playerGST.getDuration.return_value = "5:32"
        playerGST.queryPosition.return_value = "0:12"
        ## Audiofile-Metadaten-Objekt
        playerGUI = mock.MagicMock()
        playerGUI.getActSong.return_value = 1
        playerGUI.getNumberOfSongs.return_value = 1
        playerGUI.playNextSong.return_value = None
        playerGUI.gstPlayer = playerGST
        configObject.setConfig('TEMP', Key='PLAYER', Value=playerGUI)
        configObject.setDebug('debugM', 'True')
        audioFile = getAudioFile(self.__filename)
        configObject.setConfig('TEMP', Key='AUDIOFILE', Value=audioFile)
        



    def test_can_create_instance_of_render_object(self):
        metaFontsObject = renderfonts.MetaFonts()
        self.assertIsInstance(
            metaFontsObject , 
            renderfonts.MetaFonts, 
            "Konnte MetaFonts-Object nicht erstellen"
            )
        print "\n " + sys._getframe().f_code.co_name + " Test passed"


    def test_can_run_prepare_fonts(self):
        metaFontsObject = renderfonts.MetaFonts()
        self.assertIsInstance(
            metaFontsObject, 
            renderfonts.MetaFonts, 
            "Konnte MetaFonts-Object nicht erstellen"
            )
        metaFontsObject.doPrepareFonts()
        print "\n " + sys._getframe().f_code.co_name + " Test passed"

    def test_can_run_render_metadata(self):
        metaFontsObject = renderfonts.MetaFonts()
        self.assertIsInstance(
            metaFontsObject, 
            renderfonts.MetaFonts, 
            "Konnte MetaFonts-Object nicht erstellen"
            )
        metaFontsObject.doPrepareFonts()
        meta = metaFontsObject.getRenderedMetadata()
        for key1 in meta.iterkeys() :
            value = ''
            data = ''
            if (meta.get(key1).has_key('value')):
                value = meta.get(key1)['value']
            if (meta.get(key1).has_key('data')):
                data = meta.get(key1)['data']
            print("Feld: %s Value: %s Data: %s " % 
                (key1,
                value,
                data
                ))
        print "\n " + sys._getframe().f_code.co_name + " Test passed"
          
    def testCanRunRenderActTime(self):
        metaFontsObject = renderfonts.MetaFonts()
        self.assertIsInstance(
            metaFontsObject, 
            renderfonts.MetaFonts, 
            "Konnte MetaFonts-Object nicht erstellen"
            )
        metaFontsObject.doPrepareFonts()
        meta = metaFontsObject.getRenderedMetadata()
        meta = metaFontsObject.getRenderedActTime()
        key1 = meta.get('TIME')['posActTime']

        print("Feld: %s Value: %s Data: %s " % 
            (key1,
            meta.get(key1)['value'],
            meta.get(key1)['data']
            ))
        print "\n " + sys._getframe().f_code.co_name + " Test passed"
          

if __name__ == '__main__':
    print "starte Test"
    unittest.main(verbosity=1)

