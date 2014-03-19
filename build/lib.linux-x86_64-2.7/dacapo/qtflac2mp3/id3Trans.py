#!/usr/bin/python
# -*- coding: UTF-8 -*-

import mutagen, mutagen.id3 as id3
from compatid3 import CompatID3
import sys

id3Frames = {
	id3.TRCK: 'TRACKNUMBER',
	id3.TPOS: 'DISCNUMBER',
	id3.TIT2: 'TITLE',
	id3.TALB: 'ALBUM',
	id3.TIT3: 'VERSION',
	id3.TPE1: 'ARTIST',
	id3.TCOM: 'COMPOSER',
	id3.TEXT: 'LYRICIST',
	id3.TPE3: 'CONDUCTOR',
	id3.TPUB: 'PUBLISHER',
	id3.TENC: 'ENCODED-BY',
	id3.TCON: 'GENRE',
	id3.TMED: 'SOURCEMEDIA',
	id3.TDRC: 'DATE',
	id3.COMM: 'COMMENTS',
	id3.TSRC: 'ISRC',
	id3.MCDI: 'CDDB',
	id3.TCOP: 'COPYRIGHT',
	id3.USER: 'LICENSE',
	id3.TCMP: 'COMPILATION',
	id3.TPE2: 'ALBUMARTIST',
	id3.TIT1: "GROUPING",
	id3.WOAR: "website",
	id3.TSOP: "artistsort",
	id3.TSOA: "albumsort",
	id3.TSOT: "titlesort",
	id3.TSO2: "albumartistsort",
	id3.TSOC: "composersort",
	id3.TPE4: "arranger",			   
	id3.TSST: "discsubtitle",
	id3.TOLY: "author",
	id3.TMOO: "mood",
	id3.TBPM: "bpm",			   
	id3.TDOR: "originaldate",
	id3.TOAL: "originalalbum",
	id3.TOPE: "originalartist",			   

}

flacFrames = {}

def revCopy():
	for tag in id3Frames.keys():
		flacFrames[id3Frames[tag]] = tag

def getFrame(tagName):
	return flacFrames[str.upper(tagName)]

def getTagName(frameName):
	return id3Frames[str.upper(frameName)]

def hasFrame(tagName):
	return flacFrames.has_key(str.upper(tagName))

def copyFlacCover(flacFile, mpgFile):		
	from mutagen.id3 import ID3, APIC
	from mutagen.flac import FLAC, Picture
	from mutagen.mp3 import MP3
	from mutagen.id3 import ID3

	audio = MP3(mpgFile, ID3=ID3)
	keys = [tag for tag in audio.keys() if 'APIC' in tag]
	for key in keys:
		del audio[key]
	audio.save()

	flacFile = FLAC(flacFile)
	pics = flacFile.pictures
	for img in pics:
		# Nur Frontcover kopieren!
		if img.type == 3 :
			id3pic = APIC(3, img.mime, img.type, img.desc, img.data)
			print 'fuege der MP3-Datei {0} das Bild Typs {1} hinzu.'.format(mpgFile, img.type)
			audio = ID3(mpgFile)
			audio.add(id3pic)
			audio.save()
			audio.save()
	return

def copyFLAC(flacFile, mpgFile):		
	from mutagen.flac import FLAC, Picture
	from mutagen.mp3 import MP3
	from mutagen.id3 import ID3

	bChange = False
	# audioMP3 = MP3('smiley.mp3', ID3=EasyID3)
	audioMP3 = MP3()
	audioMP3.add_tags(ID3=CompatID3)
	bNew = True

	audioFLAC = FLAC(flacFile)
	if audioFLAC.has_key('tracktotal'):
	    tracktotal = audioFLAC["tracktotal"][0]
	else:
	    tracktotal = 0

	if not audioFLAC.has_key('albumartist'):
	    audioFLAC["albumartist"] = audioFLAC["artist"]

	if not audioFLAC.has_key('compilation'):
	    audioFLAC["compilation"] = 0
	
	
	print "--FLAC--------------------------------------------"


	for tag in audioFLAC.keys():
		# print >> sys.stdout, "--> verarbeite Key: ", tag
		
		# if 'APIC' in tag:
		# 	print 'Tag {0}'.format(tag)
		# else:
		#	print >> sys.stdout, "--> verarbeite Key: Tag {0}: {1}".format(tag, textTag.encode('UTF-8'))
		if tag == "tracktotal": pass
		else:
			# id3.add(mutagen.id3.COMM(encoding=3,text=relationshipLink, lang="eng", desc="MusicGrabberSig"))
			# Tag COMM:Kommentar:'DEU': von Vinyl

			if tag == "tracknumber": 
				audioFLAC[tag]='{0}/{1}'.format(audioFLAC[tag][0], tracktotal)
				# audioFLAC[tag]='{0}/{1}'.format(audioFLAC[tag], tracktotal)

			searchTag = tag
			if "comment" in tag: searchTag = 'COMMENTS'
			if "description" in tag: searchTag = 'COMMENTS'

			# if not str.upper(tag) in id3Trans.flacFrames:
			if not hasFrame(searchTag):  
				if "replaygain" in tag: continue
				print >> sys.stderr, "Key nicht gefunden: ", tag
				continue

			id3Frame = getFrame(searchTag)
			# audioMP3[id3Frame] = audioFLAC[tag]
			# for textTag in audioFLAC[tag]:
			# print >> sys.stderr, "tag: %s  frame: %s " % (tag, id3Frame.__name__)
			if "comment" in tag: 
				# audioMP3.add(id3Frame(encoding=3, text= audioFLAC[tag], lang="DEU", desc="Kommentar"))
				try: audioMP3[id3Frame.__name__] = id3Frame(3, text=audioFLAC[tag], lang="DEU", desc="Kommentar")
				except: pass
			else:
				audioMP3[id3Frame.__name__] = id3Frame(3, text=audioFLAC[tag])
				# audioMP3.add(id3Frame(encoding=3, text= audioFLAC[tag]))
			bChange = True
			# print u'Tag {0}: {1} --> MP3 zugefuegt'.format(id3Frame, audioFLAC[tag])
		
	
	if bChange == True:
#		print dir(audioMP3)
		# if bNew : audioMP3.save(mpgFile,v1=2)
		# else : audioMP3.save(v1=2)
		audioMP3.tags.update_to_v23()
		if bNew : audioMP3.tags.save(filename=mpgFile, v2=3)
		else : audioMP3.tags.save(v2=3)

	print '-'*40


def convertMp3ToV23(mpgFile):	
	from mutagen.mp3 import MP3

	audioMP3 = MP3(mpgFile, ID3=CompatID3)
	audioMP3.tags.update_to_v23()
	audioMP3.tags.save(v2=3)

revCopy()	

