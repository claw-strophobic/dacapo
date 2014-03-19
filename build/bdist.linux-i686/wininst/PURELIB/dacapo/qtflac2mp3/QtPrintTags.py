#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys, os, locale
import string
import logging

logger = logging.getLogger(__name__)
encoding = locale.getpreferredencoding()
utf8conv = lambda x : unicode(x, encoding).encode('utf8')

def printMP3(mp3File):
	from mutagen.id3 import ID3, APIC
	from mutagen.easyid3 import EasyID3
	from mutagen.mp3 import MP3

	audio = MP3(mp3File, ID3=EasyID3)
	print "--EasyID3-----------------------------------------"
	for k in EasyID3.valid_keys.keys():
		if audio.has_key(k):
			print 'Key {0}: {1}'.format(k, audio[k][0])

	print "--ID3---------------------------------------------"
	# Cover vorhanden?
	audio = MP3(mp3File, ID3=ID3)
	for tag in audio.keys():
		if 'APIC' in tag:
			print 'Tag {0}'.format(tag)
		else:
			print 'Tag {0}: {1}'.format(tag, audio[tag])

	# keys = [tag for tag in a.keys() if 'APIC' in tag and a[tag].type == 3]
	# for key in keys:
	#    del a[key]

def printFLAC(flacFile):
	from mutagen.flac import FLAC, Picture

	audio = FLAC(flacFile)
	print "--FLAC--------------------------------------------"
	for tag in audio.keys():
		for text in audio[tag]:
			if 'APIC' in tag:
				print("Tag %s" % (tag) )
			else:
				print("Tag %s: %s" % (tag, text) )
	pics = audio.pictures		
	for p in pics:
		print("Bild gefunden. Typ %s: %s" % (p.type, p.desc) )

def printTags(mimeFile):
	import mimetypes

	logger.debug('Habe folgende Datei empfangen: %s' % (mimeFile))
	contentType = mimetypes.guess_type(mimeFile) # Mimetype herausfinden
	mimeType = contentType[0]
	if mimeType <> None:
		print " "
		print "Verarbeite Datei: %s" % (mimeFile)
		print "Angegebene Datei ist vom Typ: %s" % (mimeType)

		if mimeType == 'audio/flac':
			printFLAC(mimeFile)
		if mimeType == 'audio/mpeg' : 
			printMP3(mimeFile)



	
