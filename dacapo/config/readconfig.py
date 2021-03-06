#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#! /usr/bin/python
################################################################################
# small Gnome Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
################################################################################

"""Dieses Modul enthält eine Klasse um die Konfiguration aus einer XML-Datei zu verarbeiten. """

from dacapo import errorhandling
from dacapo.ui import condition
from dacapo.ui import gui as MetaGUI
from dacapo.ui import meta as MetaData
from dacapo.ui import audio_engine as AudioEngine
try:
    # import pkg_resources
    import sys, os
    import xml.etree.ElementTree as ET
except ImportError, err:
    errorhandling.Error.show()
    sys.exit(2)

FILE="configarchive.tar.gz"
HOMEDIR = os.path.expanduser('~')
CONFIG_DIR = HOMEDIR + '/.dacapo/'
XML_CONFIG = 'dacapo.conf'

global CONFIG


# -------------------- class -----------------------------------------------------------------


class Config(object):


	def __init__(self, debug, filename):
		global CONFIG
		self.debug = debug
		self.XML = filename
		if not os.path.isfile(filename):
			import dacapo.config.createconfig
		if not os.path.isfile(filename):
			print  >> sys.stderr, "FEHLER: Datei nicht gefunden -> ", filename
			errorhandling.Error.show()
			sys.exit(2)
			return 1
		else:
			VERSION = [0, 0, 0]
			self.loadConfig()
		CONFIG = self


	def readChild(self, root):
		d = {}
		for child in root :
			elementTyp = child.get("type", "str")
			# elementText = child.text.split(',')
			if elementTyp == "int" :
				d[child.tag] = int(child.text)
			elif elementTyp == "float" :
				d[child.tag] = float(child.text)
			elif elementTyp == "tuple" :
				d[child.tag] = tuple(child.text)
			elif elementTyp == "color" :
				tmp = tuple(child.text.split(','))
				color = (int(tmp[0]), int(tmp[1]), int(tmp[2]))
				d[child.tag] = tuple(color)
			elif elementTyp == "boolean" :
				if child.text.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh'] :
					d[child.tag] = True
				else: d[child.tag] = False
				# d[child.tag] = bool(child.text) --> Funktioniert nicht!
			elif elementTyp == "dict" :
				if self.debug :
					print " DICT   ->  ", child.tag, child.text
				neuesDict = self.readChild(child)
				d[child.tag]  = neuesDict
			elif elementTyp == "cond" :
				mf = condition.Condition()
				mf.grabXMLData(child)
				if self.debug :
					print " COND   ->  ", child.tag, child.text
				self.__dCond[child.tag] = mf
			else :
				d[child.tag] = child.text
		return d

	# -------------------- readConfig() -----------------------------------------------------------------


	def readConfig(self):
		from lxml import etree
		self.gui = {}

		parser = etree.XMLParser(remove_blank_text=True)
		xmltree = etree.parse(self.XML, parser)
		root = xmltree.getroot()
		gui = root.xpath('gui')

		for child in gui[0] :
			if ((child.tag == 'window') or (child.tag == 'fullscreen')):
				g = MetaGUI.Gui(child.tag)
				g.grabXMLData(child)
				self.gui[child.tag] = g
			else:
				d = self.readChild(child)
				self.__dConfigGUI[child.tag] = d
			if self.debug : print child.tag, child.attrib

		g = MetaData.Meta('metaData')
		g.grabXMLData(root)
		self.gui['metaData'] = g
		g = AudioEngine.AudioEngine('audio_engine')
		audio_engine = root.xpath('audio_engine')
		g.grabXMLData(audio_engine[0])
		self.gui['audio_engine'] = g


	def loadConfig(self):
		self.__dConfigGUI = {}
		self.__dConfigAudio = {}
		self.__dDebug = {}
		self.__dCond = {}
		self.__dTEMP = {}
		self.gui = {}

		try:
			tree = ET.parse(self.XML)
			root = tree.getroot()
		except ET.ParseError:
			print  >> sys.stderr, "FEHLER beim Einlesen der Konfigurationsdatei ", self.XML, " ---> "
			errorhandling.Error.show()
			sys.exit(2)

		version = str(root.find('version').text)
		tmp = version.split('.')
		if len(tmp) == 4 :
			self.__version = [int(tmp[0]), int(tmp[1]), int(tmp[2]), tmp[3]]
		else:
			self.__version = [int(tmp[0]), int(tmp[1]), int(tmp[2])]
		if self.debug : print "Version: %s " % (version)

		self.readConfig()

		audio = root.find('audio_engine')
		self.__dConfigAudio = self.readChild(audio)

		debug = root.find('debug')
		self.__dDebug = self.readChild(debug)

		if self.debug :
			for key1 in self.__dConfigGUI.iterkeys() :
				print "Kapitel:  %s " % (key1)
				kap = self.__dConfigGUI.get(key1)
				for key2 in kap.iterkeys() :
					print "Tag:  %s  - Wert: %s" % (key2, self.getConfig('gui', key1, key2) )

			print "Kapitel:  %s " % ('audio_engine')
			for key2 in self.__dConfigAudio.iterkeys() :
				print "Tag:  %s  - Wert: %s" % (key2, self.getConfig('audio_engine', 'audio_engine', key2) )


	# -------------------- getConfig() -----------------------------------------------------------------



	def getConfig(self, Type, Cap = '', Key = ''):
		# if self.debug : print "getConfig()-Abfrage --> Type: %s Cap: %s Key: %s " % (Type, Cap, Key)
		if Type == 'version':
			return 	self.__version
		if Type == 'gui':
			if Key == '':
				return self.__dConfigGUI.get(Cap)
			else:
				return self.__dConfigGUI.get(Cap).get(Key)
		elif Type == 'audio_engine':
			return self.__dConfigAudio.get(Key)
		elif Type == 'debug':
			return self.__dDebug.get(Key)
		elif Type == 'cond':
			if Key == '':
				return self.__dCond.copy()
			else:
				return self.__dCond.get(Cap).get(Key)
		elif Type == 'TEMP':
			return self.__dTEMP.get(Key)
		else : pass


	# -------------------- setConfig() -----------------------------------------------------------------


	def setConfig(self, Type, Cap=None, Key=None, Value=None):
		# if self.debug : print "getConfig()-Abfrage --> Type: %s Cap: %s Key: %s " % (Type, Cap, Key)
		if Type == 'version':
			pass
		if Type == 'gui':
			try:
				self.__dConfigGUI[Cap][Key] = Value
			except:
				print  >> sys.stderr, "FEHLER beim Setzen eines Konfigurationswertes "
				errorhandling.Error.show()

		elif Type == 'audio_engine':
			try:
				self.__dConfigAudio[Key] = Value
			except:
				print  >> sys.stderr, "FEHLER beim Setzen eines Konfigurationswertes "
				errorhandling.Error.show()

		elif Type == 'debug':
			try:
				self.__dDebug[Key] = Value
			except:
				print  >> sys.stderr, "FEHLER beim Setzen eines Konfigurationswertes "
				errorhandling.Error.show()

		elif Type == 'TEMP':
			self.__dTEMP[Key] = Value

		else : pass
		return


	def saveConfig(self, file=None):
		global CONFIG_DIR, XML_CONFIG
		from lxml import etree
		parser = etree.XMLParser(remove_blank_text=True)
		xmltree = etree.parse(self.XML, parser)
		root = xmltree.getroot()
		gui = root.xpath('gui')
		for child in gui[0] :
			if ((child.tag == 'window') or (child.tag == 'fullscreen')):
				gui[0].remove(child)
		gui[0].append(self.gui['window'].getXMLData())
		gui[0].append(self.gui['fullscreen'].getXMLData())
		for element in root.getiterator():
			if (element.tag == 'audio_engine'):
				root.remove(element)

		root.append(self.gui['audio_engine'].getXMLData())
		if file is None:
			file = CONFIG_DIR + XML_CONFIG
		filedata = etree.tostring(root, pretty_print=True).decode()
		try:
			f = open(file, 'w')
			f.write(filedata)
			f.close()
		except:
			print  >> sys.stderr, "ERROR saving configuration! "
			errorhandling.Error.show()
		return filedata


	def setDebug(self, Key, Value):
		# if self.debug : print "setDebug() --> Key: %s Value: %s " % (Key, Value)
		self.__dDebug[Key] = Value

		if self.debug :
			for key2 in self.__dDebug.iterkeys() :
				pass
				# print "Tag:  %s  - Wert: %s" % (key2, self.getConfig('debug', key2, key2) )


	def fver(self, tup):
		return ".".join(map(str, tup))


def getConfigObject():
	global CONFIG, CONFIG_DIR, XML_CONFIG
	if 'CONFIG' in globals():
		return CONFIG
	else:
		CONFIG = Config(False, CONFIG_DIR + XML_CONFIG)
		return CONFIG

def getConfigDir():
	global CONFIG, CONFIG_DIR, XML_CONFIG
	return CONFIG_DIR

def quit():
	global CONFIG
	if 'CONFIG' in globals():
		del globals()['CONFIG']


def main(cmdline):
	global CONFIG, CONFIG_DIR, XML_CONFIG
	CONFIG = Config(False, CONFIG_DIR + XML_CONFIG)
	return

if __name__ == '__main__':
    main(sys.argv)


