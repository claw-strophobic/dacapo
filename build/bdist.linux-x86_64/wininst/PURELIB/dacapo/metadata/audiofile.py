#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Dieses Modul enthält eine Klasse um die metadata einer Audiodatei 
    zu verarbeiten. 
    Für die einzelnen Formate (FLAC, MP3 usw.) wird von dieser Klasse
    abgeleitet und die folgenden Methoden implementiert:

    def loadFile(self):
    def loadFrontCover(self):
    def loadStoredPictures(self):

"""
from dacapo import errorhandling
import sys
import os
try:
    import string
    import pygame
    import random
    import logging
    import traceback
    import codecs      # utf8 support
    import platform
    import StringIO
    from dacapo.config import readconfig
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

# ----------- Globale Variablen/Objekte ----------------------- #
HOMEDIR = os.path.expanduser('~')

class AudioFile(object):

    def __init__(self, playerGUI, filename):
        self.fileOpen = False
        self.guiPlayer = playerGUI
        self.config = readconfig.getConfigObject()
        self.LEERCD = HOMEDIR + '/.dacapo/' + self.config.getConfig('gui', 'misc', 'picNoCover')
        self.debug = self.config.getConfig('debug', ' ', 'debugM')
        self.mp3Tags = self.config.getConfig('gui', 'metaData', 'MP3-Tags')
        self.fileOpen = False
        self.filename = filename
        self.clearTags()
        self.tags = dict()
        self.loadFile()
        self.syncLyrics = self.config.getConfig('gui', 'misc', 'showLyricsSynced')
        # synchronisierte Texte laden?
        if self.syncLyrics == True: self.setSyncLyrics()



    def setSyncLyrics(self):
        self.syncTime, self.syncText = self.loadSyncLyrics()

    def loadSyncLyrics(self):
        """
            Hier wird versucht, eine LRC-Datei
            mit synchronisiertem Text zu finden
            und mit <<Sekunden/Text>> zu laden.
            das Ergebnis steht dann in 
                self.syncTime[]  und
                self.syncText[]  und
                self.syncCount   als counter mit 0
        """
        syncedTag = self.config.getConfig('gui', 'syncLyrics', 'tag')
        syncedDir = self.config.getConfig('gui', 'syncLyrics', 'dir')
        # Ersatzvariablen auflösen
        while True :
            text = self.guiPlayer.find_between(syncedDir, '%', '%')
            if text == '' : break
            syncedDir = syncedDir.replace('%' + text + '%', self.getMetaData(text))

        syncTime = list()
        syncText = list()
        lines = list()
        pathName = os.path.dirname(self.filename)
        fullFileName = os.path.basename(self.filename)
        fileName, fileExtension = os.path.splitext(fullFileName)
        lrcFile = fileName + ".lrc"
        # 1. In der Audio-Datei im TAG lt. config
        if self.debug : logging.debug("Versuche LRC-Text aus Tag zu laden -> %s " % (syncedTag))
        text = self.getMetaData(syncedTag)

        # 2. In der Audio-Datei im TAG "syncedlyrics"
        if len(text) <= 0 and syncedTag <> "syncedlyrics":
            if self.debug : logging.debug("Versuche LRC-Text aus Tag zu laden -> %s " % ("syncedlyrics"))
            text = self.getMetaData("syncedlyrics")

        # 3. Im Verzeichnis lt. config mit selben Namen wie Audio-Datei aber der Erweiterung *.lrc
        if len(text) <= 0 and len(syncedDir) > 0:
            try:
                # testPath = os.path.normpath(os.path.join(pathName, syncedDir))
                testPath = os.path.join(pathName, syncedDir)
                testFile = testPath + "/" + lrcFile
                if self.debug : logging.debug("Versuche LRC-Datei zu laden -> %s " % (testFile))
                if os.path.isfile(testFile) :
                    f = codecs.open(testFile, 'r', 'utf-8')
                    try: text = f.read()
                    except: 
                        logging.error("Konnte Datei %s nicht lesen" % (testFile) )
                        f.close()
                        f = open(testFile, 'r')
                        try: text = f.read()
                        except: 
                            logging.error("Konnte Datei %s nicht lesen" % (testFile) )
                    finally: f.close()
            except: 
                logging.error("Konnte Datei %s %s nicht oeffnen" % (pathName, syncedDir) )

        # 4. Im Verzeichnis der Audio-Datei mit selben Namen aber der Erweiterung *.lrc
        if len(text) <= 0:
            testFile = pathName + "/" + lrcFile
            if self.debug : logging.debug("Versuche LRC-Datei zu laden -> %s " % (testFile))
            if os.path.isfile(testFile) :
                f = codecs.open(testFile, 'r', 'utf-8')
                try: text = f.read()
                except: 
                    logging.error("Konnte Datei %s nicht lesen" % (testFile) )
                    f.close()
                    f = open(testFile, 'r')
                    try: text = f.read()
                    except: 
                        logging.error("Konnte Datei %s nicht lesen" % (testFile) )
                finally: f.close()

        # Gefunden?
        if len(text) > 0 :
            lines = text.splitlines()
            for line in lines:
                lineTime = line[line.find("[")+1:line.find("]")]
                lineText = line[line.find("]")+1:]
                if len(lineTime) > 0:
                    try : minutes = int(lineTime[:lineTime.find(":")])
                    except : continue
                    if "." in lineTime :
                        try: seconds = int(lineTime[lineTime.find(":")+1:lineTime.find(".")])
                        except: seconds = 0
                        try: msecs = int(lineTime[lineTime.find(".")+1:])
                        except: msecs = 0
                    else :
                        try: seconds = int(lineTime[lineTime.find(":")+1:])
                        except: seconds = 0
                        msecs = 0
                            
                    seconds += ( minutes * 60 )
                    msecs += (seconds * 1000)
                    syncTime.append(msecs)
                    if len(lineText) > 0:
                        syncText.append(lineText)
                    else :
                        syncText.append("  ")
                    if self.debug : logging.debug("Sekunden: %s lineTime: %s Text: %s " % (seconds, lineTime, lineText))
        return (syncTime, syncText)

    def getMetaData(self, key):
        """
            Hier werden die metadata zurück gegeben.
            In der Konfigurationsdatei wird festgelegt,
            welche Daten wo angezeigt werden.
            Da diese Variablen sich auf FLAC-Tags
            beziehen, muss bei MP3 vorher umgesetzt
            werden.
            Auch diese Umsetzung wird u.a. in der Config-
            Datei festgelegt.
        """
        # Besonderheit, da auch gerne mal tracknumber = "5/7"
        # gespeichert wird... (gerade bei MP3)
        if key == "tracknumber" : return self.getTrack()
        if key == "tracktotal" : return self.getTrackTotal()
        if self.debug : logging.debug("Angeforderter Key: %s" % (key))
        value = ""
        bFirst = True
        if self.tags.has_key(key) :
            try : 
                for text in self.tags[key]:
                    if self.debug : logging.debug("Angeforderter Key %s (%s) = %s" % (key, text, type(text)))
                    if isinstance(text, str) or isinstance(text, unicode):
                        if bFirst : value = text
                        else: value += '\n' + text
                    else :
                        if bFirst : value = text.get_text() 
                        else: value += '\n' + text.get_text() 
                    bFirst = False
            except : pass
        if self.debug : logging.debug("Zurueck Key: %s Value %s" % (key, value))
        return value




    def loadPictures(self) :
        showLyrics = self.guiPlayer.showLyricsAsPics
        showWhenSynced = self.config.getConfig('gui', 'misc', 'showLyricsWhenSynced')
        self.setMiscPic()
        self.loadStoredPictures()
        # Sind Texte vorhanden? Anzeigen als Bild? Dann los!
        if (len(self.syncTime) > 0) and (showWhenSynced == False) :
            showLyrics = False
        if self.debug : logging.debug("Texte als Bild anzeigen? %s" % (showLyrics))        
        listLyrics = list()
        if showLyrics == True :
            listLyrics = self.getLyrics()
        if len(listLyrics) > 0 :
            renderedLyrics = list()
            w = 0
            h = 0
            for strLyrics in listLyrics :
                try:
                    tmpStr = strLyrics.rstrip("\n")
                    if len(tmpStr) <= 0 : tmpStr = ' '
                    fontLyrics = self.guiPlayer.lyricFont.render(tmpStr, True, self.guiPlayer.lyricFontColor)
                    txtW, txtH = fontLyrics.get_size()
                    if txtW > w : w = txtW
                    h = h + txtH
                    renderedLyrics.append(fontLyrics)
                except pygame.error, err: 
                    logging.warning("Error at lyricFont.render(fontLyrics, (%s, %s)) %s " % (0, 0, err))

            image = pygame.Surface([w, h])
            image.fill(self.config.getConfig('gui', self.guiPlayer.winState, 'backgroundColor'))
            w = 0
            h = 0
            for fontLyrics in renderedLyrics :
                try: 
                    image.blit(fontLyrics, (w, h)) 
                except pygame.error, err: 
                    logging.warning("Error at image.blit(fontLyrics, (%s, %s)) %s " % (0, 0, err))
                txtW, txtH = fontLyrics.get_size()
                h = h + txtH
            self.setMiscPic(image)


        return

    def getFrontCover(self):
        self.loadFrontCover()
        if self.debug : logging.info("done.")
        return self.cover

        

# -------------------- getLyrics ----------------------------------------------------------------

    def getLyrics(self):
        listLyrics = list()
        if self.debug : logging.debug("Suche Lyrics in Tag: %s" %("unsyncedlyrics"))
        strLyrics = self.getMetaData('unsyncedlyrics')
        listLyrics = strLyrics.splitlines()
        if len(listLyrics) <= 0 : 
            if self.debug : logging.debug("Nichts gefunden. Suche Lyrics in Tag: %s" %("lyrics"))
            strLyrics = self.getMetaData('lyrics')
            listLyrics = strLyrics.splitlines()
        if len(listLyrics) <= 0 and self.config.getConfig('gui', 'misc', 'showSyncedLyricsAsPics'): 
            if self.debug : logging.debug("Nichts gefunden. Suche Lyrics in %s" %("syncedlyrics"))
            syncTime, listLyrics = self.loadSyncLyrics()

        if len(listLyrics) > 0 :
            if self.debug : logging.debug("Fündig geworden:  %s" %(listLyrics))
        else:       
            if self.debug : logging.debug("Keine Texte gefunden. :-(")

        return listLyrics


# -------------------- preBlitDiaShow ----------------------------------------------------------------

    def preBlitDiaShow(self):

        pics = list(self.getAllPics())

        self.guiPlayer.diaShowPics = []
        if self.debug : logging.info("Anzahl zu skalierender Bilder: %s" %(len(pics)))

        for i, tP in enumerate(pics):

            if self.debug : logging.debug("Anzahl Bilder: %s -> aktuelles Bild: Nr %s " % (len(pics), i))

            # --> skalieren -------------------------------
            if self.debug : logging.debug("Bild skalieren: Nr %s  " % (i))
            picW, picH = pics[i].get_size()

            if picW == 0 : picW = 1
            proz = (self.guiPlayer.winWidth * 100.0) / (picW)  
            h = int(round( (picH * proz) / 100.0))
            w = int(round(self.guiPlayer.winWidth))
            if self.debug : logging.debug("Picture skalieren: " \
                "Originalbreite: %s Hoehe: %s PROZENT: %s " \
                "-> Neue W: %s H: %s" % (picW, picH, proz, w, h))
            if h > self.guiPlayer.winHeight :
                proz = (self.guiPlayer.winHeight * 100.0) / (h)  
                w = int(round( (w * proz) / 100.0 ))
                h = int(round( (h * proz) / 100.0))
                if self.debug : logging.debug(\
                    "NEUSKALIERUNG da Bild zu hoch wurde: "\
                    "Originalbreite: %s Hoehe: %s PROZENT: %s " \
                    "-> Neue W: %s H: %s " % (picW, picH, proz, w, h))
            tmp = pygame.transform.scale(pics[i], (w, h))   
            # <-- skalieren -------------------------------
            self.guiPlayer.diaShowPics.append(tmp)

        if self.debug : logging.info("done.")
        return
## --------------- Getter -----------------------------------

    def getTempPic(self, data):
        datei = StringIO.StringIO()
        datei.write(data)
        datei.seek(0)
        return datei

    def getCover(self):
        return self.cover 

    def getMiscPic(self):
        random.seed()
        if not self.guiPlayer.resize : random.shuffle(self._MiscPictures)
        return self._MiscPictures 

    def getAllPics(self):
        pics = []
        pics.append(self.cover)
        if self._Backcover <> None :
            pics.append(self._Backcover)
        return pics + self.getMiscPic()

    def getNoOfPics(self):
        return 1 + len(self._MiscPictures)
        
    def getTitle(self):
        return self.songtitle

    def getArtist(self):
        return self.artist

    def getAlbum(self):
        return self.album

    def getAlbumWithNo(self):
        if self.getDiscNo() != "0" :
            return '{0} (Disc {1})'.format(self.getAlbum(), self.getDiscNo())
        else :
            return self.getAlbum()

    def getTrack(self):
        return self.tracknumber

    def getTrackTotal(self):
        return self.trackTotal

    def getTrackOfTotal(self):
        track = self.getTrack()
        totals = self.getTrackTotal()       
        if totals == 0 :
            return str(track)
        else:
            return '{0}/{1}'.format(track, totals)

    def getYear(self):
        return self.date

    def getDiscNo(self):
        if type(self.discNo) is str :
            if self.debug : logging.debug('DiscNo ist Typ Str()  %s' % (self.discNo))
            if self.discNo == "1" :
                return "0"
            elif self.discNo == "0" :
                return "0"
            else :
                return self.discNo
        elif type(self.discNo) is not None :
            if self.debug : logging.debug('DiscNo ist nicht None %s' % (self.discNo))
            return str(self.discNo)
        else :
            return "0"
    def getComments(self):
        return self.comments



## --------------- Setter -----------------------------------

    def setCover(self, cover = None ):
        if cover == None :
            self.cover = "???"
        else :
            self.cover = cover

    def setBackcover(self, cover = None ):
        self._Backcover = cover

    def setMiscPic(self, cover = None ):
        if cover == None :
            self._MiscPictures = []
        else :
            self._MiscPictures.append(cover)

    def setTitle(self, title = None):
        if title == None :
            self.songtitle = "???"
        else :
            self.songtitle = title

    def setArtist(self, artist = None):
        if artist == None :
            self.artist = "???"
        else :
            self.artist = artist

    def setAlbum(self, album = None):
        if album == None :
            self.album = "???"
        else :
            self.album = album

    def setTrack(self, tracknumber = None):
        if tracknumber == None :
            self.tracknumber = 0
        else :
            if "/" in tracknumber:
                self.tracknumber = tracknumber[:tracknumber.find("/")]
                self.setTrackTotal(tracknumber[tracknumber.find("/")+1:])
            else:
                self.tracknumber = tracknumber

    def setTrackTotal(self, tracks = None):
        if tracks == None :
            self.trackTotal = "0"
        else :
            self.trackTotal = tracks

    def setDiscNo(self, number = None):
        if number == None :
            self.discNo = "0"
        else :
            self.discNo = str(number)

    def setCDDB(self, number = None):
        if number == None :
            self.cddb = 0
        else :
            self.cddb = number

    def setYear(self, date = None):
        if date == None :
            self.date = "???"
        else :
            self.date = date

    def setComments(self, comment = None):
        if comment == None :
            self.comments = []
        else :
            self.comments.append(comment)
    

    def clearTags(self):
        self.setCover()
        self.setBackcover()
        self.setMiscPic()
        self.setTitle()
        self.setArtist()
        self.setAlbum()
        self.setTrack()
        self.setTrackTotal()
        self.setDiscNo()
        self.setCDDB()
        self.setYear()
        self.setComments()
        self.syncTime = []
        self.syncText = []
        self.syncCount = 0


