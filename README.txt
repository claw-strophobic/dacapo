=======
dacapo
=======

Note
====
I'd really appreciate any feedback. 
Send an E-Mail (german or english) to claw <dot> strophob <at> gmx <dot> de or
visit the project-homepage at http://sourceforge.net/projects/dacapo-audio
where you can open a ticket (if you found a bug) or write a review or open open a discussion.
Also, I'd welcome any translator, anybody who would create RPM- or DEB-Packages, 
as well as Windows-Installer.

Introduction
============
First: 
*What is dacapo?* It is a small, "lightweight" music
Player, with a few special features.
*What is dacapo not?* A system for managing music collections.
It can't create playlists, will not do changes in the audio data
nor organize any directories.
*Why another player?* Because most players neither show the images properly
nor prepare the metadata free configurable, nor display the songtext, etc., 
and if they can, they will not run on my little VIA M800 because they can
way too much and eat too much resources.

I developed this Python package to play my digitized Music Collection (FLAC) 
on my small, quiet (fanless) VIA EPIA M800, and I like the metadata ("tags", 
ie information such as "Artist", "Title", "Album", etc.) and the cover 
(also full screen) to display.
The images (cover, back cover, band photos) are stored in my FLAC files. 
Sense and nonsense about this one can argue, it fills forums. 
In any case, for a full screen display has a reasonable quality of the images 
to be added, otherwise it's no fun.
And this does no tool which automatically fetches the images.
How it comes then, that my buddy saw it, loved it, and so the
Program has been expanded by some modules.
In addition, my buddy uses Windows ...

It's just a player, no management of the collection! This is done by
excellent programs such as Quod Libet [2], or MP3Tag [3] in Windows.
With these programs, the metadata can be maintained, as well as fine
Playlists could be created, which are then processed by dacapo.
With MP3Tag or easytag [4] you can easily put the images in the files. 
For the ReplayGain analysis/storage I recommend RGain [5].

To display the images and data pyGame is used because IMHO it is the
thinnest and fastest performing option.
To play the audio I use the GStreamer, because he plays pretty much
everything, and has Replay Gain [1] and gapless support.
Since GStreamer requires Gtk+ anyway, I've used this for the GUI, too.

Features
--------
Thus, dacapo has now the following features:
 - Replay Gain [1] is supported
 - Gapless (gapless playback) is supported
   (important during live music or transitions)
 - All metadata can be displayed, which is stored in the
   Audio files - freely configurable
 - All images (what is stored in the audio files)
   can be shown. e.g. as slideshow
 - Lyrics can be displayed (as an additional image).
 - Synchronized Lyrics can be displayed (like "karaoke")
 - Command line and graphical call possible
 - Runs on Linux and Windows
 - Runs on "small" computers (800 MHz with 1 GB RAM)
 - Is freely configurable
 - Plays (currently) FLAC, Ogg-Vorbis, WMA and MP3 (other formats are in preparation)
 - Multilingual (Translator welcome)


Of course it stands and falls with the data. What is not stored in the audio 
files can not be displayed.


[1] http://replaygain.org
[2] http://code.google.com/p/quodlibet
[3] http://www.mp3tag.de/
[4] http://easytag.sourceforge.net/
[5] http://bitbucket.org/fk/rgain

Requirements
============
 - Python 2.6 or 2.7 -- http://python.org/
 - Gtk+ 2.24 -- http://www.gtk.org/
 - PyGTK 2.24 -- http://www.pygtk.org/
 - pyGame 1.9 -- http://www.pygame.org/
 - Mutagen -- http://code.google.com/p/mutagen/
 - GStreamer 0.10 -- http://gstreamer.org/
 - PyGST 0.10 -- http://gstreamer.freedesktop.org/modules/gst-python.html

Before installing: Python, GTK and PyGTK 2.24, GStreamer
and PyGST 0.10 should be installed.
Mutagen and pyGame should be installed automatically.


Installation
============
Just install it like any other Python package: Unpack, then (as root/with
**sudo**)

 # python setup.py install

After installation, the configuration file should be adapted.
This should be located in the user directory:

 # ~/.dacapo/dacapo.conf

Linux example:
  /home/claw/.dacapo/dacapo.conf

Windows example:
  C:\Dokumente und Einstellungen\Claw\.dacapo\dacapo.conf

There should also be an dacapo.conf.sample.eng with the documentation
of the config-file.

Should something gone wrong during the installation,
the directory could be copied manually from the package.
Copy the contents of the package directory dacapo/data in the
directory mentioned above.


Program start
=============

The scripts dacapo and dacapoui should have been copied during installation
in the directory */usr/local/bin* or on Windows in the python subdirectory *Scripts*.

**dacapo**
=============
This is the command line part.
Basic usage is simple:

 $ dacapo AUDIOFILE1 AUDIOFILE2 ...
 or
 $ dacapo PLAYLIST 
 or
 $ dacapo /PATH/TO/MY/MUSIC/

There are some options; see them by running

 $ dacapo --help

**dacapoui**
=============
Thre you go with the graphical part (Gtk+).
Simple:

 $ dacapoui

**Function-Keys**
=================

The following keys have a function during operation:
 - HOME = first song of the playlist
 - END = Last song of the playlist
 - SPACE = pause / start
 - LEFT / RIGHT = + / -10 seconds
 - Up / Down = next / previous song
 - ESC / Q = Quit
 - F = Full screen / window

Copyright
=========

Copyright (c) 2013 Thomas Korell <claw.strophob@gmx.de>
