#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

#===============================================================================
#    tcf2vrt.py
#    by José Manuel Martínez Martínez
#===============================================================================
import timeit

import sys
import os
import codecs # to handle properly unicode by I/O
import re # to use regular expressions
import argparse # to parse command-line arguments
import fnmatch

from tcf2vrt import tcf
from tcf2vrt import inxml
from tcf2vrt import vrt

#===============================================================================
# Parse command-line arguments
#===============================================================================

def cli():
    """CLI parses command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="path to the input files directory.")
    parser.add_argument(
        "-o", "--output",
        required=False,
        help="path to the output files directory.")
    parser.add_argument(
        "-e",
        "--extension",
        required=False,
        default="*.xml",
        help="pattern for the extension of the files.")
    parser.add_argument(
        "-f",
        "--format",
        required=True,
        choices=['vrt', 'xml'],
        help="output format, VRT or inline XML")
    args = parser.parse_args()
    indir = args.input
    outdir = args.output
    extension = args.extension
    outformat = args.format
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    return indir, outdir, extension, outformat



# parser = argparse.ArgumentParser()
# parser.add_argument("infile", help="path to the input file in TCF format")
# #parser.add_argument("outfile", help="path to the output file in VRT format")
# parser.add_argument("outformat", help="output format: vrt (input for CWB) in.xml (inline XML annotation)")
# #format arguments should be parsed, to check that the values are valid formats, see
# args = parser.parse_args()

# convert each transformation into a class to avoid any kind of problem with concurrent queries.
# provide a test file as demo

def get_files(directory, fileclue):
        """Get files matching a pattern in a given directory.

        Return a list of paths.

        directory -- a string for the path
        fileclue -- a string to glob files
        """
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, fileclue):
                matches.append(os.path.join(root, filename))
        return matches


indir, outdir, extension, outformat = cli()

print(outdir)

infiles = get_files(indir, extension)

for i in infiles:
    print(i)
    infilename = os.path.split(i)[1]
    inshortname = os.path.splitext(infilename)[0]
    if outformat == 'vrt':
        outextension = '.vrt'
    elif outformat == 'xml':
        outextension = '.xml'
    outfilename = inshortname+outextension
    outfilepath = os.path.join(outdir, outfilename)
    print(outfilepath)

    if outformat == "xml":
        inxml.InXmlWriter.serialize_inxml(inxml.InXmlWriter(tcf.TcfReader.read_tcf(tcf.TcfReader(i)),outfilepath))
    elif outformat == "vrt":
        vrt.VrtWriter.serialize_vrt(vrt.VrtWriter(tcf.TcfReader.read_tcf(tcf.TcfReader(i)),outfilepath))
 
