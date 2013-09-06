=======
dacapo
=======

Einleitung
==========
Zuerst: 
*Was ist dacapo?* Es ist ein kleines, „leichtes“ Musik-
Abspielprogramm („Player“), mit ein paar Besonderheiten.
*Was ist dacapo nicht?* Ein Verwaltungsprogramm für Musiksammlungen. 
Es kann keine Abspiellisten erstellen, keine Änderungen in den Audiodaten 
vornehmen und keine Verzeichnisse organisieren.
*Warum noch einen Player?* Weil die wenigsten Player weder die Bilder 
vernünftig anzeigen, noch die Metadaten frei aufbereiten, oder Texte 
anzeigen etc., und wenn sie es doch können, laufen sie nicht auf meinem
kleinen VIA M800 weil sie zu viel können und zu viel Resourcen fressen.

Dieses Python-Paket habe ich entwickelt, um meine digitalisierte
Musiksammlung (FLAC) auf meinem kleinen, leisen (lüfterlosen) VIA EPIA M800 
abspielen, und mir dabei die Metadaten („Tags“, also Informationen wie 
„Künstler“, „Titel“, „Album“ etc.) als auch die Cover (auch Vollbild) 
anzeigen lassen zu können.
Die Bilder (Cover, Backcover, Bandfotos) sind bei mir in den FLAC-Dateien 
gespeichert. Über Sinn und Unsinn dessen kann man sich streiten, es füllt 
ganze Foren. Auf jeden Fall muss für eine Vollbild-Darstellung schon eine
vernünftige Qualität der Bilder gegeben sein, sonst macht es keinen Spaß. 
Und da hilft kein Tool, welches die Bilder automatisch holt.
Wie es dann so kommt, hat mein Kumpel es gesehen, war begeistert, und das 
Programm wurde noch um einige Module erweitert.
Zudem nutzt mein Kumpel Windows...

Es ist nur ein Abspielprogramm, keine Verwaltung der Sammlung! Dies erledigen 
hervorragende Programme wie Quod Libet [2], oder MP3Tag [3] unter Windows. 
Mit diesen Programmen können die Metadaten gepflegt werden, sowie schöne 
Abspiellisten erstellt werden, die vom dacapo dann verarbeitet werden. 
Mit MP3Tag oder easytag [4] können bequem die Bilder in die Dateien gebracht 
werden. Für die Replay Gain Analyse/Speicherung empfehle ich rgain [5].

Zur Anzeige der Bilder und Daten wird pyGame benutzt, da es m.E. die 
schlankeste und performanteste Möglichkeit ist.
Zum Abspielen der Audiodaten verwende ich den GStreamer, da er so ziemlich 
alles abspielt, sowie Replay Gain [1] und Gapless unterstützt.
Da der GStreamer sowieso Gtk+ benötigt, habe ich dies auch für die GUI 
verwendet.

Funktionen
----------
So hat dacapo nun folgende Funktionen:
 - Replay Gain [1] wird unterstützt
 - Gapless (lückenloses Abspielen) wird unterstützt 
   (wichtig bei Live-Aufnahmen oder Überblendungen)
 - Alles an Metadaten kann angezeigt werden, was in den 
   Audio-Dateien gespeichert ist – frei konfigurierbar
 - Alles an Bilder, was in den Audio-Dateien gespeichert ist, 
   kann angezeigt werden. z.B. als Diashow
 - Songtexte können angezeigt werden (wie ein zusätzliches Bild).
 - Synchronisierte Songtexte können angezeigt werden (wie „Karaoke“)
 - Kommandozeile als auch graphischer Aufruf möglich
 - läuft unter Linux als auch Windows
 - läuft auch auf „kleinen“ Computern (800 MHz mit 1 GB RAM)
 - ist frei Konfigurierbar
 - Spielt (z. Zt.) FLAC, Ogg-Vorbis, WMA und MP3, weitere Formate in der Vorbereitung
 - Mehrsprachig (Übersetzer willkommen)

Es steht und fällt natürlich mit den Daten. Was nicht in den Audiodateien
gespeichert ist, kann auch nicht angezeigt werden.


[1] http://replaygain.org
[2] http://code.google.com/p/quodlibet
[3] http://www.mp3tag.de/
[4] http://easytag.sourceforge.net/
[5] http://bitbucket.org/fk/rgain

Voraussetzungen
===============
 - Python 2.6 or 2.7 -- http://python.org/
 - Gtk+ 2.24 -- http://www.gtk.org/
 - PyGTK 2.24 -- http://www.pygtk.org/
 - pyGame 1.9 -- http://www.pygame.org/
 - Mutagen -- http://code.google.com/p/mutagen/
 - GStreamer 0.10 -- http://gstreamer.org/
 - PyGST 0.10 -- http://gstreamer.freedesktop.org/modules/gst-python.html

Vor der Installation sollte Python, Gtk+ und PyGTK 2.24, sowie GStreamer
und PyGST 0.10 installiert sein.
Mutagen und pyGame sollten ggf. automatisch installiert werden.

Installation
============
Wie jedes andere Python Paket: Entpacken, und dann (als root/mit **sudo**)
 
  # python setup.py install

Nach der Installation muss ggf. die Konfigurationsdatei angepasst werden.
Diese sollte sich im Benutzerverzeichnis befinden:

 # ~/.dacapo/dacapo.conf

Linux Beispiel:
  /home/claw/.dacapo/dacapo.conf

Windows Beispiel:
  C:\Dokumente und Einstellungen\Claw\.dacapo\dacapo.conf

Ebenfalls sollte sich eine dacapo.conf.sample.ger in diesem Verzeichnis
befinden. Darin findet sich die Dokumentation zur Konfiguration.

Sollte etwas nicht bei der Installation nicht funktioniert haben, kann
das Verzeichnis manuell aus dem Paket kopiert werden.
Dazu den Inhalt des Paket-Verzeichnises dacapo/data in das o.g. 
Verzeichnis kopieren. 


Programmstart
=============

Die Skripte dacapo und dacapoui sollten bei der Installation 
in das Verzeichnis */usr/local/bin* bzw. unter Windows in das
Python-Unterverzeichnis *Scripts* kopiert worden sein.

**dacapo**
-----------
Dies ist der Kommandozeilen-Teil.
Der einfache Aufruf ist simpel:

 $ dacapo AUDIOFILE1 AUDIOFILE2 ...
 oder
 $ dacapo PLAYLIST
 oder
 $ dacapo /PATH/TO/MY/MUSIC/

Es gibt einige Aufrufoptionen; anschauen durch

 $ dacapo --help

**dacapoui**
=============
Damit wird der graphische Aufruf gestartet (Gtk+).
Einfach:

 $ dacapoui

**Betrieb**
=============

Folgende Tasten haben eine Funktion während des Betriebs:
 - HOME=Erstes Lied der Playlist 
 - END=Letztes Lied der Playlist
 - SPACE=Pause/Start
 - LINKS/RECHTS=+/-10 Sekunden
 - UP/DOWN=Nächsten/Vorherigen Song
 - ESC/Q=Beenden
 - F=Fullscreen/Fenster

Copyright
=========

Copyright (c) 2013 Thomas Korell <claw.strophob@gmx.de>

