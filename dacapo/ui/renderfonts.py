#!/usr/bin/env python
# -*- coding: UTF-8 -*-
###############################################################################
#! /usr/bin/python
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="claw"
__date__ ="$03.08.2014 11:44:27$"
import sys
from dacapo import errorhandling
try:
    import pygame
    import logging
    from dacapo.config import readconfig
    import copy
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

class MetaFonts(object):
    """
    Documentation
    """
    def __init__(self):
        self._config = readconfig.getConfigObject()
        self._debug = self._config.getConfig('debug', ' ', 'debugGUI')
        self._player = self._config.getConfig('TEMP', Key='PLAYER')
        assert isinstance(self._player.gstPlayer, object)
        self._gstPlayer = self._player.gstPlayer
        self._winState = self._config.getConfig('TEMP', 'gui', 'winState')
        self._isPlaylist = self._config.getConfig(
                    'TEMP', Key='PLAYLIST').isPlaylist()
        self._audioFile = None
        pygame.init()
    
    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def doPrepareFonts(self):
        
        ## Ein Dictionary anlegen mit den anzuzeigenen Feldern
        ## und den Schritfattributen dazu
        self.__metaFields = self._config.getConfig(
                'gui', 
                self._winState,
                'fields'
                )
        self.__lyricFont = self._config.getConfig(
                'gui',
                self._winState,
                'lyricFont'
                )
        print(self.__lyricFont['font'])
        print(self.__lyricFont['fontSize'])
        print(self.__lyricFont['fontColor'])
        if self._debug : logging.debug("LyricFont: %s" %(self.__lyricFont))

        if self._debug : logging.debug('LyricFont initialisieren. ')
        self.__metaFields['lyricFont'] = self.__lyricFont
        self.__metaFields.get('lyricFont')['value'] = None
        if self._debug : logging.debug("LyricFont: %s Fontsize: %s FontColor: %s" % (
                self.__lyricFont['font'],
                self.__lyricFont['fontSize'],
                self.__lyricFont['fontColor']
        ))

        for key1 in self.__metaFields.iterkeys() :
            if self._debug : logging.debug("%s Font: %s Fontsize: = %s"
                % (key1, 
                self.__metaFields.get(key1)['font'],
                self.__metaFields.get(key1)['fontSize']))
                
            self.__metaFields.get(key1)['sysFont'] = \
                pygame.font.SysFont(
                    self.__metaFields.get(key1)['font'], 
                    self.__metaFields.get(key1)['fontSize']
                )
            fontHeightFont = \
                self.__metaFields.get(key1)['sysFont'].render(
                    "M", 
                    True, 
                    self.__metaFields.get(key1)['fontColor']
                )
            self.__metaFields.get(key1)['realFontSize'] = \
                fontHeightFont.get_size()


        if self._debug :
            for key1 in self.__metaFields.iterkeys() :
                for key2 in self.__metaFields.get(key1).iterkeys() :
                    logging.debug("%s: %s:  %s Klasse %s" % (
                        key1, 
                        key2,
                        self.__metaFields.get(key1).get(key2), 
                        self.__metaFields.get(key1).get(key2).__class__
                        ))
                        

                        
                        
    def getRenderedMetadata(self):                
        """
        In dieser Funktion werden die metadata in die Variablen
        gelesen und anhand der parametresierten Werte gerendert.
        In doBlitText werden diese dann weiter verarbeitet.
        Zurückgegeben wird ein Dictionary mit den Keys:
            - Feldname
                - ['data'] -> die aufbereiteten Daten
                - ['renderedData'] -> die gerenderten Daten
        """
        # metadata holen und aufbereiten
        self._audioFile = self._config.getConfig('TEMP', Key='AUDIOFILE')

        if self._debug: logging.debug(\
                'rendere Texte: {0}'.format(
                self._config.getConfig('TEMP', Key='FILENAME')
                ))

        posActTime = -1
        textActTime = None
        self.__metaFields.pop('posActTime', None)            

        textMetaVar = {}
        textMetaVar['if_playlist'] = self._config.getConfig(
            'gui', 
            'metaData', 
            'if_playlist'
            )
        textMetaVar['if_discNr'] = self._config.getConfig(
            'gui', 
            'metaData', 
            'if_discNr'
            )

        for key1 in textMetaVar.iterkeys() :
            s = textMetaVar.get(key1)
            try:
                s = s.replace('%time%', self._gstPlayer.getDuration())
                s = s.replace('%duration%', self._gstPlayer.getDuration())
                if self._isPlaylist :
                    s = s.replace('%tracknumberlist%', str(self._player.getActSong()))
                    s = s.replace('%tracktotallist%', str(
                            self._player.getNumberOfSongs()))
                text = s
                while True :
                    text = self.find_between(s, '%', '%')
                    if text == '' : break
                    s = s.replace('%' + text + '%', self._audioFile.getMetaData(text))

                textMetaVar[key1] = s
            except: pass			

        if not self._isPlaylist : textMetaVar['if_playlist'] = ''
        if self._audioFile.getDiscNo() == "0" : textMetaVar['if_discNr'] = ''

        for key1 in self.__metaFields.iterkeys() :
            vList = list()
            self.__metaFields.get(key1)['data'] = ''
            self.__metaFields.get(key1)['renderedData'] = None
            if (not self.__metaFields.get(key1).has_key('value')) :
                self.__metaFields.get(key1)['value'] = None
            if (self.__metaFields.get(key1).has_key('value')) and \
                (self.__metaFields.get(key1)['value'] != None) and \
                (self.__metaFields.get(key1)['value'] != '') :
                s = self.__metaFields.get(key1)['value']
                try:
                    s = s.replace('%if_playlist%', textMetaVar['if_playlist'])
                    s = s.replace('%if_discNr%', textMetaVar['if_discNr'])
                    if self._isPlaylist :
                        s = s.replace('%tracknumberlist%', str(self._player.getActSong()))
                        s = s.replace('%tracktotallist%', str(
                                self._player.getNumberOfSongs()))

                    multi = False
                    if (self.__metaFields.get(key1).has_key('multiLine')) and \
                            (self.__metaFields.get(key1)['multiLine'] == True):
                        multi = True

                    s = self._audioFile.replaceTags(s)

                    if '#time#' in s :
                        posActTime = key1
                        textActTime = s

                    s = s.replace('#time#', self._gstPlayer.getDuration())
                    s = s.replace('#duration#', self._gstPlayer.getDuration())

                    if multi == False:
                        if (s != ''):
                            self.__metaFields.get(key1)['data'] =  s
                            if self._debug:
                                logging.debug('Rendere Metadaten: %s: %s -> %s' % (
                                    key1,
                                    self.__metaFields.get(key1)['value'],
                                    self.__metaFields.get(key1)['data']
                                    ))
                            self.__metaFields.get(key1)['renderedData'] = \
                                self.__metaFields.get(key1)['sysFont'].render(
                                    self.__metaFields.get(key1)['data'] ,
                                    True,
                                    self.__metaFields.get(key1)['fontColor']
                                )
                            self.__metaFields.get(key1)['renderedSize'] = \
                                  self.__metaFields.get(key1)['renderedData'].get_size()
                    else:
                        if self._debug:
                            logging.debug('Multiline: %s:' % (s))
                        if (self.__metaFields.get(key1).has_key('splitSpaces')) and \
                            (self.__metaFields.get(key1)['splitSpaces'] == True):
                            if self._debug: logging.debug('Split Spaces')
                            s = s.replace(' ', '\\n')
                        vList = s.split('\\n')
                        if (len(vList) > 0):
                            self.__metaFields.get(key1)['data'] =  vList
                            image = self.get_rendered_multiline(
                                    self.__metaFields, key1
                                )

                            self.__metaFields.get(key1)['renderedData'] = image
                            self.__metaFields.get(key1)['renderedSize'] = image.get_size()

                except pygame.error, err: 
                    print("Autsch! Konnte Metadaten %s nicht rendern: %s" % (
                        key1, self.__metaFields.get(key1)['data']))
                    logging.warning("konnte Metadaten nicht rendern: %s: %s -> %s" % 
                        (key1, 
                        self.__metaFields.get(key1)['value'],
                        self.__metaFields.get(key1)['data']))
                    logging.warning(err)

        if (posActTime != -1):
            self.__metaFields['TIME'] = {}
            self.__metaFields.get('TIME')['textActTime'] = textActTime
            self.__metaFields.get('TIME')['posActTime'] = posActTime

        return self.__metaFields

    def get_rendered_maxwidth(self, array, key):
        maxwidth = array.get(key)['max-width']
        if self._debug:
            logging.debug('Rendere Metadaten mit Max-Width: %s %s: %s -> %s' % (
                maxwidth,
                key,
                array.get(key)['value'],
                array.get(key)['data']
                ))
        rList = list()
        w = 0
        h = 0
        lineH = 0
        lineTest = ''
        lineSave = None
        counter = 0
        for s in array.get(key)['data']:
            counter += 1
            if len(lineTest) > 0:
                lineTest = lineTest + ' ' + s
            else:
                lineTest = s
            rData = array.get(key)['sysFont'].render(
                        lineTest,
                        True,
                        array.get(key)['fontColor']
                    )
            wT,hT = rData.get_size()
            if self._debug:
                logging.debug('Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
            if wT < maxwidth and counter < len(array.get(key)['data']):
                lineSave = rData
                continue
            if lineSave == None:
                lineSave = rData
            if self._debug:
                logging.debug('List-Append Text: %s Text-Width: %s - Max-Width: %s ' % (lineTest, wT, maxwidth))
            rList.append(rData)
            lineTest = ''
            lineSave = None
            if wT > w: w = wT
            h += hT
            lineH = hT

        image = pygame.Surface([w, h])
        image.set_colorkey(self._config.getConfig('gui', self._winState, 'backgroundColor'))
        image.fill(self._config.getConfig('gui', self._winState, 'backgroundColor'))
        array.get(key)['savedRect'] = image
        hT = 0
        for r in rList:
            mW = 0
            wT,htT = r.get_size()
            if self.__metaFields.get(key).has_key('alignH')and \
                        self.__metaFields.get(key)['alignH'] == 'right':
                mW = w - wT
            elif self.__metaFields.get(key).has_key('alignH') and \
                        self.__metaFields.get(key)['alignH'] == 'center':
                mW = (w - wT) / 2

            image.blit(r, (mW, hT))
            hT += lineH

        return image

    def get_rendered_multiline(self, array, key):
        if not self.__metaFields.get(key).has_key('max-width'):
            self.__metaFields.get(key)['max-width'] = 0
        return self.get_rendered_maxwidth(array, key)
        

    def getRenderedActTime(self):                
        """
        In dieser Methode wird die aktuelle Songposition in die Variablen
        gelesen und anhand der parametresierten Werte gerendert.
        """

        s = self.__metaFields.get('TIME')['textActTime'] 
        key1 = self.__metaFields.get('TIME')['posActTime'] 
        try:
            s = s.replace('#time#', self._gstPlayer.queryPosition())
            s = s.replace('#duration#', self._gstPlayer.getDuration())

            if (s != ''):
                self.__metaFields.get(key1)['data'] =  s
                if self._debug:
                    logging.debug('Rendere Metadaten: %s: %s -> %s' % (
                        key1,
                        self.__metaFields.get(key1)['value'],
                        self.__metaFields.get(key1)['data']
                        ))
                self.__metaFields.get(key1)['renderedData'] = \
                    self.__metaFields.get(key1)['sysFont'].render(
                        self.__metaFields.get(key1)['data'] ,
                        True,
                        self.__metaFields.get(key1)['fontColor'] 
                    )
        except pygame.error, err: 
            print("Autsch! Konnte Metadaten %s nicht rendern: %s" % (
                key1, self.__metaFields.get(key1)['data']))
            logging.warning("konnte Metadaten nicht rendern: %s: %s -> %s" % 
                (key1, 
                self.__metaFields.get(key1)['value'],
                self.__metaFields.get(key1)['data']))
            logging.warning(err)
        
        return self.__metaFields
        
if __name__ == "__main__":
    print "Hello World"
    