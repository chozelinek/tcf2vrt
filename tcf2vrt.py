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
import codecs # to handle properly unicode
import re # to use regular expressions
import argparse # to parse command-line arguments
import importlib

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
# Import XML module
#===============================================================================

import xml.etree.ElementTree as etree

try:
    from lxml import etree # if we don't need any of the fancy things provided by lxml we should drop it, although it does not hurt
    print "running with lxml.etree"
except importError:
    try:
        import xml.etree.cElementTree as etree
        print "running with cElementTree"
    except importError:
        import xml.etree.ElementTree as etree
        print "running with ElementTree"
#===============================================================================
# Read the input file
#===============================================================================

with codecs.open(infile, encoding='utf-8', mode='r') as input:
    tree = etree.parse(input) # If XML is not well formed will rise an exception

# declare namespaces to avoid typing the whole URI again and again?
tc = "{http://www.dspin.de/data/textcorpus}"
cmd = "{http://www.clarin.eu/cmd/}"
md = "{http://www.dspin.de/data/metadata}"

#===============================================================================
# Find out which layers are present in the file and check tokens
#===============================================================================

layers = tree.find('{}TextCorpus'.format(tc)) # We get the element that contains all the annotation layers in the file

elements = ((etree.QName(layer)).localname for layer in layers) # Get only the local names of the layers

def layer_is_present(layername):
    if any(item.tag == '{}{}'.format(tc,layername) for item in layers):#can this with in instead any
        return True
    else:
        return False

def tokens_is_present():
    """
    Function to check if the tokens layer is present
    """
    if layer_is_present("tokens") == True:
        pass
    else:
        sys.exit("Ups! 'tokens' layer is not present, conversion aborted.")

tokens_is_present() # check if tokens is present, if not abort

#===============================================================================
# Create the text element
#===============================================================================

text = etree.Element('text')

#===============================================================================
# Add metadata to text element
#===============================================================================

#file ID, the name of the file

text.set("id", inshortname)

#language

text.set("lang", (tree.find('{}TextCorpus'.format(tc))).attrib["lang"])

#PIDs of all ToolsInChain

def get_tools():
    toolsinchain = tree.findall('//{}PID'.format(cmd)) # find the PIDs of all the tools used
    tools = []
    for i in toolsinchain:
        item = i.text
        item = re.sub(r"(http://hdl.handle.net/)?(.+)", r"\2", item)
        tools.append(item)
    text.set("tools", " ".join(tools))
    
get_tools()

#===============================================================================
# Process positional attributes
#===============================================================================

#positional_elements = ["lemmas","POStags","morphology","namedEntities","orthography","depparsing"]

positional_elements = ["POStags","lemmas"]

#===============================================================================
# Add positional attributes to tokens
#===============================================================================


def add_positional_attrib(id,element,attribute):
    positional_element = tree.find('//{}{}[@tokenIDs="{}"]'.format(tc,element,id))
    token = tree.find('//{}token[@ID="{}"]'.format(tc,id))
    token.attrib[attribute] = positional_element.text

# We iterate over the list of positional elements that we have already implemented
# Is there a more elegant way to pass the variables to the functions in the modules imported?

start3 = timeit.default_timer()
def process_positional_elements():
    processed_positional_attrib = []
    for item in positional_elements:
        start2 = timeit.default_timer()
        if layer_is_present(item):
            module = importlib.import_module(item, package=None)
            module.tree = tree
            module.tc = tc
            module.text = text
            module.etree = etree
            (id_attrib,element,attribute,elements) = module.function() # as a convention I can call all the functions processing the layer function
            stop2 = timeit.default_timer()
            runtime2 = stop2 - start2
            runtime2 = '%.2f' % runtime2
            function2 = 'add_positional_attrib'
            print function2+'\t'+runtime2
            for i in elements:
                id = i.attrib["{}".format(id_attrib)]
                add_positional_attrib(id,element,attribute)
            processed_positional_attrib.append(attribute)
    text.set("p_attributes", " ".join(processed_positional_attrib))
stop3 = timeit.default_timer()

runtime3 = stop3 - start3
runtime3 = '%.2f' % runtime3
function3 = 'process_positional_elements'
print function3+'\t'+runtime3        

process_positional_elements()

#===============================================================================
# Build the output tree
#===============================================================================
# create a general function to reconstruct the information as structural in-line
# XML

#structural_elements = [("sentence","s"),("text","text")] # list of tuples: each list element is
# a structural attribute, each element has three values: the name of the element
# in tcf, the name of the attribute in vrt, and the parent

# we need also a structure, at least the parent of the structural element to be constructed

# since there are only a few potential structural attributes it might be better
# to have ad hoc functions for each of this structures, since each of this
# structural attributes will be a different challenge.
def build_sentences():
    """Function to reconstruct sentences."""
    tree_sentences = tree.findall('//{}sentence'.format(tc))
    for sentence in tree_sentences:
        s = etree.SubElement(text, "s")
        s.attrib["ID"] = sentence.attrib["ID"]
        s_tokenIDs = sentence.attrib["tokenIDs"].split(" ")
        for i in s_tokenIDs:
            word = tree.find('//{}token[@ID="{}"]'.format(tc,i))
            word.tag = "token"
            s.append(word)

build_sentences()

#===============================================================================
# Save the output
#===============================================================================

def serialize_inxml(xml):
    """Output serialization in XML format with in-line annotation"""
    xml.write(outfile, encoding="utf8", pretty_print=True, xml_declaration=True, method="xml")

def serialize_vrt(xml):
    """Output serialization in XML/VRT format suitable for CWB"""
    tokens = xml.findall('//token')
    for token in tokens:
        #string = "\t".join([token.text,token.attrib["pos"],token.attrib["lemma"],token.attrib["ID"]]) # convert token into string
        string = "\t".join([token.text,token.attrib["pos"],token.attrib["ID"]]) # convert token into string
        parent = xml.find('//token[@ID="{}"]..'.format(token.attrib["ID"])) # get the parent element
        if parent.text == None:
            parent.text = string
        else:
            parent.text = "\n".join([parent.text,string])
        parent.remove(token)
    vrt = etree.tostring(xml, encoding='unicode', method='xml') # convert the XML tree into a string to manipulate it
    vrt = re.sub(r"><", r">\n<", vrt)
    vrt = re.sub(r">([^<\n])", r">\n\1", vrt)
    vrt = re.sub(r"([^\n])<", r"\1\n<", vrt)
    vrt = etree.ElementTree(etree.fromstring(vrt)) # parse the string as an element and convert the element in a tree
    vrt.write(outfile, encoding="utf8", xml_declaration=True, method="xml") # write the result to a file    
  
def serialize():
    """Output serialization"""
    xml = etree.ElementTree(text)
    if outformat == "in.xml":
        serialize_inxml(xml)
    elif outformat == "vrt":
        serialize_vrt(xml) 
    
serialize()

#===============================================================================
# Finished!
#===============================================================================

stop1 = timeit.default_timer()

runtime = stop1 - start1
runtime = '%.2f' % runtime

print outfile+" obtained in "+runtime+" seconds!\n============="