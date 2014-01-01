#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install import install
import sys, os

with open('README.txt') as file:
    long_description = file.read()

print("Setup-Mode: %s" % (sys.argv[1]) )
if sys.argv[1] == "sdist" or \
	sys.argv[1] == "bdist" :    
	import shutil
	src_file = "dacapo/data/VERSION" 
	dest_file = "./VERSION" 
	shutil.copy(src_file, dest_file)

VERSION = open("VERSION").read().strip()

class dacapo_install(install):
	description = "Custom Install Process"
	user_options= install.user_options[:]
	user_options.extend([('manprefix=', None, 
		'MAN Prefix Path if not /usr/local/share/>')])

	def initialize_options(self):
		self.manprefix = None
		install.initialize_options(self)

	def finalize_options(self):
		if self.manprefix is None :
			self.manprefix = "/usr/local/share/"
		install.finalize_options(self)

	def install_manpages(self):
		import platform, string, shutil
		if platform.system() <> 'Windows':
			print "copy manpages..."
			for root, dirs, files in os.walk('./man/'):
				for filename in files:
					src_file = os.path.join(root, filename) 
					man_root = os.path.join(self.manprefix, \
						string.lstrip(root, './'))
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
			import dacapo.config.createconfig
			self.install_manpages()
		

setup(
    name = "dacapo",
    version=VERSION,
    packages = ['dacapo', 'dacapo.ui', 'dacapo.config', 'dacapo.data', 
    'dacapo.errorhandling', 'dacapo.metadata', 'dacapo.playlist'],
    scripts = ["bin/dacapo", "bin/dacapoui"],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    requires=[
			'pygame (>=1.9)',
			'argparse (>=1.1)',
			'setuptools (>=0.9)',
			'mutagen (>=1.21)'
			],
    install_requires = [
			# 'gtk==2.24',
			# 'pygtk==2.24', 
			# 'gst>=0-10', 
			# 'pygst>=0.10', 
			'pygame>=1.9',
			'argparse>=1.1',
			'setuptools>=0.9',
			'mutagen>=1.21'
		],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.glade files found in the 'dacapo' package, too:
        'dacapo': ['*.glade'],
        # And include any *.tar.gz from the package 'dacapo.config, too:
        'dacapo.config': ['*.gz'],
        'dacapo.data': ['*'],
    },

	# data_files = ['docs'],

    # metadata for upload to PyPI
    author = "Thomas Korell",
    author_email = "claw.strophob@gmx.de",
    description = "Lightweight Music Player with cover- and lyrics-display",
	long_description=long_description,
    license = "GNU General Public License (v2 or later)",
    keywords = "FLAC MP3 Player Coverart lyrics karaoke",
    url = "http://sourceforge.net/projects/dacapo-player",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
	# cmdclass={'setconfig': my_install},
	classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Win32 (MS Windows)',
          'Environment :: X11 Applications',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
          ],
	cmdclass={"install": dacapo_install},

)

