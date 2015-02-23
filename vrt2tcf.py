#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

#===============================================================================
#    tcf2vrt.py
#    by José Manuel Martínez Martínez
#===============================================================================
import timeit
start1 = timeit.default_timer()

import sys
import os
import codecs # to handle properly unicode by I/O
import re # to use regular expressions
import argparse # to parse command-line arguments

from tcf2vrt import *

#===============================================================================
# Following code block is only needed if lxml is not used as the parser
#===============================================================================

reload(sys)
sys.setdefaultencoding('utf-8')

#===============================================================================
# Parse command-line arguments
#===============================================================================

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="path to the input file in TCF format")
#parser.add_argument("outfile", help="path to the output file in VRT format")
parser.add_argument("outformat", help="output format: vrt (input for CWB) in.xml (inline XML annotation)")
#format arguments should be parsed, to check that the values are valid formats, see 
args = parser.parse_args()

# convert each transformation into a class to avoid any kind of problem with concurrent queries.
# provide a test file as demo


infile = args.infile
#outfile = args.outfile
outformat = args.outformat

def check_outformat():
    knownformats = ["vrt","in.xml"]
    if any(item == outformat for item in knownformats):
        pass
    else:
        sys.exit("Ups! '"+outformat+"' is not a valid output format!\nTry with: '"+"' or '".join(knownformats)+"'. Conversion aborted!")
        
check_outformat()

#===============================================================================
# Find out input file name, extension, path
#===============================================================================

(indirname, infilename) = os.path.split(infile)

(inshortname, inextension) = os.path.splitext(infilename) # shortname can be used as text ID

#===============================================================================
# Produce output file name, extension, path
#===============================================================================

outextension = outformat

outfilename = inshortname+"."+outextension

outfile = os.path.join(indirname,outfilename) # we can provide as command line argument the format/extension

#===============================================================================
# Finished!
#===============================================================================

if outformat == "in.xml":
    inxml.InXmlWriter.serialize_inxml(InXmlWriter(tcf.TcfReader.read_tcf(TcfReader(infile)),outfile))
elif outformat == "vrt":
    vrt.VrtWriter.serialize_vrt(VrtWriter(tcf.TcfReader.read_tcf(TcfReader(infile)),outfile))

stop1 = timeit.default_timer()

runtime = stop1 - start1
runtime = '%.2f' % runtime

print outfile+" obtained in "+runtime+" seconds!\n============="