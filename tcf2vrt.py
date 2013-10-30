#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

# refactor Jörg's reader in a simple ElementTree API

try:
    from lxml import etree # if we don't need any of the fancy things provided by lxml we should drop it, although it does not hurt
    print("running with lxml.etree")
except importError:
    try:
        import xml.etree.cElementTree as etree
        print("running with cElementTree")
    except importError:
        import xml.etree.ElementTree as etree
        print("running with ElementTree")
        
import re # To use regular expressions


#===============================================================================
# Read the input file
#===============================================================================

# input variable as command line argument

# output variable as command line argument

# read the file in a SAX-like style to reduce memory consumption to a minimum?
# Does semiNER wrapper do that or it is just a matter of style?

# check which tcf layers are present. This can be done at the very beginning or
# per function/element manipulation. Or handle exceptions with try. Because if
# the elements are no present we will get an error and the script will be
# aborted.

tcf = etree.parse("result7_2794771265787765018.xml")

#===============================================================================
# Add positional attributes to tokens
#===============================================================================

# declare a namespace to avoid typing the whole URI again and again?

for token in tcf.findall('//{http://www.dspin.de/data/textcorpus}token'):
    ID = token.attrib["ID"]
    # pos
    tag = tcf.find('//{}tag[@tokenIDs="{}"]'.format('{http://www.dspin.de/data/textcorpus}',ID))
    token.attrib["pos"] = tag.text
    # lemma
    lemma = tcf.find('//{}lemma[@tokenIDs="{}"]'.format('{http://www.dspin.de/data/textcorpus}',ID))
    token.attrib["lemma"] = lemma.text


#===============================================================================
# Construct the output tree
#===============================================================================

# what value should be given to the id attribute? The name of the file without
# the extension? And checking that is a valid token (no strange characters and
# starting with an alphabetic character)

text = etree.Element('text', attrib={'id':"text1"})

tcf_sentences = tcf.findall('//{http://www.dspin.de/data/textcorpus}sentence')

for sentence in tcf_sentences:
    s = etree.SubElement(text, "s")
    s.attrib["ID"] = sentence.attrib["ID"]
    s_tokenIDs = sentence.attrib["tokenIDs"].split(" ")
    for i in s_tokenIDs:
        word =  tcf.find('//{}token[@ID="{}"]'.format('{http://www.dspin.de/data/textcorpus}',i))
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

"""
sentences = xml.findall('//s')

for i in sentences:
    tokens = []
    for j in i:
        tokens.append(j.text+"\t"+j.attrib["pos"]+"\t"+j.attrib["lemma"]+"\t"+j.attrib["ID"])
        j.getparent().remove(j)
    i.text = '\n'.join(tokens)
    
# solution below is better, once structural attributes are added
# getparent() is only available in lxml, good for me and server, but bad dependency for students
"""

tokens = xml.findall('//token')

for token in tokens:
    string = token.text+"\t"+token.attrib["pos"]+"\t"+token.attrib["lemma"]+"\t"+token.attrib["ID"] # convert token into string
    parent = xml.find('//token[@ID="{}"]..'.format(token.attrib["ID"])) # get the parent element
    if parent.text == None:
        parent.text = string
    else:
        parent.text = "\n".join([parent.text,string])
    parent.remove(token)

# Is there a way to avoid writing to a file and do the last block on the fly?

xml.write("out.vrt", encoding="utf8", xml_declaration=True, method="xml")

# the following is to prettify the xml for encoding with cwb

with open("out.vrt", mode='r+') as vrt:# do we need the encoding?
    text = vrt.read()
    text = re.sub(r"><", r">\n<", text)
    text = re.sub(r">([^<\n])", r">\n\1", text)
    text = re.sub(r"([^\n])<", r"\1\n<", text)
    vrt.seek(0)
    vrt.write(text)


#xml.write("out.xml",encoding="utf-8")
    
    # this could be saved for each sentence, to retrieve the corresponding tokens 
    #s = etree.Element('s', attrib={'ID':item.attrib["ID"],'start':tokenIDs[0],'end':tokenIDs[-1]})
    #print(s.tag, s.attrib["ID"], s.attrib["start"], s.attrib["end"])

"""
        self.tokenIDs = item.attrib[1].split(" ")
        self.sentstart = item.tokenIDs[0]
        self.sentend = item.tokenIDs[-1]
"""

#===============================================================================
# Save into
#===============================================================================

