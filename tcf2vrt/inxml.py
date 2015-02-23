#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

"""
Module to manipulate files in inline XML
"""

import codecs # to handle properly unicode
import re
import sys

#===============================================================================
# Import XML module
#===============================================================================

import xml.etree.ElementTree as etree

try:
    from lxml import etree # if we don't need any of the fancy things provided by lxml we should drop it, although it does not hurt
#     print "running with lxml.etree"
except importError:
    try:
        import xml.etree.cElementTree as etree
        print "running with cElementTree"
    except importError:
        import xml.etree.ElementTree as etree
        print "running with ElementTree"

class InXmlWriter(object):
    """Save a corpus in TCF format."""
    def __init__(self,xmltree,outfile):
        self.xmltree = xmltree
        self.outfile = outfile
#         self.serialize_inxml()
        
    def __str__(self):
        return "-------------"
    
    def serialize_inxml(self):
        """Output serialization in XML format with in-line annotation"""
        self.xmltree.write(self.outfile, encoding="utf8", pretty_print=True, xml_declaration=True, method="xml")