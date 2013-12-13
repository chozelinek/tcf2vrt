#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

#===============================================================================
#    tcf2vrt.py
#    by José Manuel Martínez Martínez
#===============================================================================

import sys
import codecs # to handle properly unicode
import re # to use regular expressions
import argparse # to parse command-line arguments 

#===============================================================================
# Parse command-line arguments
#===============================================================================

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="path to the input file in TCF format")
parser.add_argument("outfile", help="path to the output file in VRT format")
args = parser.parse_args()

infile = args.infile
outfile = args.outfile

#===============================================================================
# Import XML module module
#===============================================================================

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

# check which tcf layers are present. This can be done at the very beginning or
# per function/element manipulation. Or handle exceptions with try. Because if
# the elements are no present we will get an error and the script will be
# aborted. IMPORTANT

# For an off-line version we might want to convert only a few layers (specify
# them, etc), for an on-line version we want to convert all layers contained in
# a tcf file at a particular point of the pipeline

# I think the easiest approach is to check which layers are there and convert
# them if we have an algorithm for it. If not, just ignore the layer.

# generate kind of metadata, like which tools have been used, or which tagset has been used

# create functions whenever it is posible

# infile = sys.argv[1] # input file
# outfile = sys.argv[2] # output file

with codecs.open(infile, encoding='utf-8', mode='r') as input:
    tree = etree.parse(input)

# declare a namespace to avoid typing the whole URI again and again?
dspin = "{http://www.dspin.de/data/textcorpus}"

layers = tree.find('{}TextCorpus'.format(dspin)) # We get the element that contains all the annotation layers in the file

print len(layers) # How many layers we have

for child in layers:
    print child.tag,'\t', child.attrib # Print all layers and attributes

# we need to classify the different layers as positional attribute or structural attribute, do we need some kind of dictionary with this information?

#===============================================================================
# Add positional attributes to tokens
#===============================================================================

# The following block adds to each token element an attribute per each layer containing positional information

# this function works as long as the tcf element contains the token ID as
# attribute and the text/content is the info to be taken as attrib. For example:
# lemma, tag. Moreover, every token has always its counterpart in the particular
# layer. For some layers, that will be the case, for other layers won't. Some
# checking has to be introduced, like in norm layer.

# we might need a method to process each layer if necessary, and transform the
# information in something that can be used by add_positional_attrib

# May we need to define a class for attributes, an attribute has to contain the
# tcf nomenclature, our vrt nomenclature, and if they are positional or
# structural? Is it enough to have a kind of data structure containing all this
# information?

def add_positional_attrib(id,element,attribute): 
    positional_element = tree.find('//{}{}[@tokenIDs="{}"]'.format(dspin,element,id))
    token.attrib[attribute] = positional_element.text
    
positional_elements = [("lemma","lemma"), ("tag","pos")] # list of tuples: each
# list element is a layer/positional attribute, each element has two values: the
# name of the element in tcf and the name of the attribute in vrt

for token in tree.findall('//{}token'.format(dspin)):
    ID = token.attrib["ID"]
    for item in positional_elements:
        add_positional_attrib(ID,item[0],item[1])
    """
    # pos
    tag = tree.find('//{}tag[@tokenIDs="{}"]'.format(dspin,ID))
    token.attrib["pos"] = tag.text
    # lemma
    lemma = tree.find('//{}lemma[@tokenIDs="{}"]'.format(dspin,ID))
    token.attrib["lemma"] = lemma.text
    """
    """
    # norm
    norm = tree.find('//{}correction[@tokenIDs="{}"]'.format(dspin,ID))
    if norm == None:
        token.attrib["norm"] = token.text
    else:
        token.attrib["norm"] = norm.text
    print(token.attrib["norm"])
    """
#===============================================================================
# Construct the output tree
#===============================================================================

# what value should be given to the id attribute? The name of the file without
# the extension? And checking that is a valid token (no strange characters and
# starting with an alphabetic character)

text = etree.Element('text', attrib={'id':"text1"})

# create a general function to reconstruct the information as structural inline
# XML

"""
structural_elements = [("sentence","s", "text")] # list of tuples: each list element is
# a structural attribute, each element has three values: the name of the element
# in tcf, the name of the attribute in vrt, and the parent
"""

# we need also a structure, at least the parent of the structural element to be constructed

# since there are only a few potential structural attributes it might be better
# to have ad hoc functions for each of this structures, since each of this
# structural attributes will be a different challenge.
    
tree_sentences = tree.findall('//{}sentence'.format(dspin))

for sentence in tree_sentences:
    s = etree.SubElement(text, "s")
    s.attrib["ID"] = sentence.attrib["ID"]
    s_tokenIDs = sentence.attrib["tokenIDs"].split(" ")
    for i in s_tokenIDs:
        word = tree.find('//{}token[@ID="{}"]'.format(dspin,i))
        word.tag = "token"
        s.append(word)

xml = etree.ElementTree(text)

#===============================================================================
# Save the output as a XML file
#===============================================================================

# xml.write("out.xml", encoding="utf8", pretty_print=True, xml_declaration=True, method="xml")

#===============================================================================
# Save the output as a VRT file
#===============================================================================

tokens = xml.findall('//token')

for token in tokens:
    string = "\t".join([token.text,token.attrib["pos"],token.attrib["lemma"],token.attrib["ID"]]) # convert token into string
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

vrt.write("out.vrt", encoding="utf8", xml_declaration=True, method="xml") # write the result to a file