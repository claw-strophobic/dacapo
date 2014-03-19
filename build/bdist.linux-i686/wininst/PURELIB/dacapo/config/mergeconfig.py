#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#! /usr/bin/python
################################################################################
# small Gnome Musicplayer
# Thomas Korell <claw DOT strophob AT gmx DOT de>
# GNU General Public License
################################################################################

"""
  Dieses Modul enthält eine Klasse um die bestehende Konfiguration 
  aus einer neuen XML-Datei zu ergänzen. 
"""

import sys, os
import xml.etree.ElementTree as et

# -------------------- class -----------------------------------------------------------------


class XMLCombiner(object):
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        self.oldFile = filenames[0]
        self.newFile = filenames[1]
        self.oldConfig = et.parse(self.oldFile)
        self.oldRoot = self.oldConfig.getroot()
        self.newConfig = et.parse(self.newFile)
        # save all the roots, in order, to be processed later
        self.roots = [et.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            # combine each element with the first oldConfig, and update that
            self.combine_element(self.oldRoot, r)
        # return the string representation
        updVer = self.oldRoot.find('version')
        updVer.text = self.newConfig.getroot().find('version').text
        self.oldConfig.write(self.oldFile, encoding="UTF-8")
        return et.tostring(self.oldRoot)

    def combine_element(self, oldConfig, newConfig):
        """
        This function recursively updates either the text or the children
        of an element if annewConfig element is found in `oldConfig`, or adds it
        from `newConfig` if not found.
        """
        # Create a mapping from tag name to element, as that's what we are fltering with
		# windows mag diese Syntax nicht...
        # mapping = {elOld.tag: elOld for elOld in oldConfig}
        mapping = {}
        for elOld in oldConfig:
            mapping[elOld.tag] = elOld 
			
        for elNew in newConfig:
            if len(elNew) == 0:
                # Not nested
                try:
                    # Not! Update the text
                    # Just test, if it's existing
                    mapping[elNew.tag].text = mapping[elNew.tag].text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[elNew.tag] = elNew
                    # Add it
                    oldConfig.append(elNew)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[elNew.tag], elNew)
                except KeyError:
                    # Not in the mapping
                    mapping[elNew.tag] = elNew
                    # Just add it
                    oldConfig.append(elNew)  

# -------------------- main() -----------------------------------------------------------------


def main(cmdline):
    fileOld = cmdline[1]
    fileNew = cmdline[2]

    r = XMLCombiner((fileOld, fileNew)).combine()
    print '-'*20
    print r

if __name__ == '__main__':
  main(sys.argv)


