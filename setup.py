#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import sys

with open('README.txt') as file:
    long_description = file.read()

class my_install():
	def run(self):
		# install.run(self)
		# Custom stuff here
		# distutils.command.install actually has some nice helper methods
		# and interfaces. I strongly suggest reading the docstrings.

		# print "und nu komm ICH dran!"
		import dacapo.config.createconfig

setup(
    name = "dacapo",
    version = "0.1.8",
    packages = ['dacapo', 'dacapo.ui', 'dacapo.config', 'dacapo.data', 'dacapo.errorhandling', 'dacapo.metadata', 'dacapo.playlist'],
    scripts = ["bin/dacapo", "bin/dacapoui"],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    requires=[
			'pygame (>=1.9)',
			'setuptools (>=0.9)',
			'mutagen (>=1.21)'
			],
    install_requires = [
			# 'gtk==2.24',
			# 'pygtk==2.24', 
			# 'gst>=0-10', 
			# 'pygst>=0.10', 
			'pygame>=1.9',
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
	

)

if sys.argv[1] == "install" :
	print "installiere config"
	my_install().run()

