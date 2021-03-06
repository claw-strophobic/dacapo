#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install import install
import sys, os
import shutil

with open('README.txt') as file:
    long_description = file.read()

print("Setup-Mode: %s" % (sys.argv[1]) )
if sys.argv[1] == "sdist" or \
	sys.argv[1] == "bdist" :    
	src_file = "./dacapo/data/VERSION"
	dest_file = "./VERSION" 
	# shutil.copy(src_file, dest_file)

VERSION = open("./dacapo/data/VERSION").read().strip()

class dacapo_install(install):
	description = "Custom Install Process"
	user_options= install.user_options[:]
	user_options.extend([('manprefix=', None, 
		'MAN Prefix Path if not /usr/local/share/>')])
	user_options.extend([('qlprefix=', None,
		'QuodLibet plugin Path if not ~/.quodlibet/plugins/')])
	user_options.extend([('localprefix=', None,
		'Localization Path if not /usr/local/share/')])

	def initialize_options(self):
		self.manprefix = None
		self.qlprefix = None
		self.localprefix = None
		install.initialize_options(self)

	def finalize_options(self):
		if self.manprefix is None :
			self.manprefix = "/usr/local/share/"
		if self.qlprefix is None :
			self.qlprefix = os.path.expanduser('~') + "/.quodlibet/plugins/"
		if self.localprefix is None :
			self.localprefix = "/usr/share/locale/"
		install.finalize_options(self)

	def install_manpages(self):
		print "copy manpages..."
		for root, dirs, files in os.walk('./man/'):
			for filename in files:
				src_file = os.path.join(root, filename)
				man_root = os.path.join(self.manprefix, \
					root.replace('./', ''))
				dest_file = os.path.join(man_root, filename)
				if not os.path.exists(man_root):
					os.makedirs(man_root)
				print("copy %s -> %s " % (src_file, dest_file))
				shutil.copy(src_file, dest_file)

	def install_qlplugins(self):
		print "copy QuodLibet-Plugins"
		for root, dirs, files in os.walk('./dacapo/ql-plugins/'):
			for filename in files:
				src_file = os.path.join(root, filename)
				dest_file = os.path.join(self.qlprefix, filename)
				if not os.path.exists(self.qlprefix):
					os.makedirs(self.qlprefix)
				print("copy %s -> %s " % (src_file, dest_file))
				shutil.copy(src_file, dest_file)

	def install_translations(self):
		print "copy translations"
		for root, dirs, files in os.walk('./dacapo/locale/'):
			for filename in files:
				src_file = os.path.join(root, filename)
				man_root = os.path.join(self.localprefix, \
					root.replace('./dacapo/locale/', ''))
				dest_file = os.path.join(man_root, filename)
				if not os.path.exists(man_root):
					os.makedirs(man_root)
				print("copy %s -> %s " % (src_file, dest_file))
				shutil.copy(src_file, dest_file)

	def run(self):
		install.run(self)
		# Custom stuff here
		# distutils.command.install actually has some nice helper methods
		# and interfaces. I strongly suggest reading the docstrings.

		if sys.argv[1] == "install" :
			print "installiere config"
			import dacapo.config.packconfigdir
			dacapo.config.packconfigdir.main()
			import dacapo.config.createconfig
			self.install_manpages()
			self.install_qlplugins()
			self.install_translations()
		

setup(
    name = "dacapo",
    version=VERSION,
    packages = ['dacapo', 'dacapo.ui', 'dacapo.config', 'dacapo.config.gui','dacapo.data',
    'dacapo.errorhandling', 'dacapo.metadata', 'dacapo.playlist',
    'dacapo.qtflac2mp3'],
    scripts = ["bin/dacapo", "bin/QtSyncLyrics",
    "bin/QtFlac2Mp3", "bin/dacapoconfig",],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    requires=[
			'pygame (>=1.9)',
			'argparse (>=1.1)',
			'setuptools (>=0.9)',
			'mutagen (>=1.21)',
			'rgain (>=1.1)'
			],
    

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.glade files found in the 'dacapo' package, too:
        'dacapo': ['*.glade'],
        # And include any *.tar.gz from the package 'dacapo.config, too:
        'dacapo.config': ['*.gz'],
        'dacapo.config.gui': ['*.css'],
        'dacapo.data': ['*'],
        'dacapo': ['locale/*/LC_MESSAGES/*'],
    },

	# data_files = ['docs'],

    # metadata for upload to PyPI
    author = "Thomas Korell",
    author_email = "claw.strophobic@gmx.de",
    description = "Lightweight Music Player with cover- and lyrics-display",
	long_description=long_description,
    license = "GNU General Public License (v2 or later)",
    keywords = "FLAC MP3 Player Coverart lyrics karaoke",
    url = "http://dacapo.netztakt.de",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
	# cmdclass={'setconfig': my_install},
	classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: X11 Applications',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
          ],
	cmdclass={"install": dacapo_install},

)

