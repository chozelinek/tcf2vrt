#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

"""
Module to manipalute files in TCF format.
"""

import codecs # to handle properly unicode
import re
import sys
import os

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

class TcfReader(object):
    """Read a text in TCF format."""
    
    def __init__(self,infile):
       self.tcfile = infile
       self.tc = "{http://www.dspin.de/data/textcorpus}"
       self.cmd = "{http://www.clarin.eu/cmd/}"
       self.md = "{http://www.dspin.de/data/metadata}"
       self.positional_elements = ["POStags","lemmas"]
       self.structural_elements = ["textstructure","sentences","namedEntities"]
       self.tok_dic = {}
       self.tagsets = []
       self.language = ''
       self.tools = []
       self.textid = ''
       self.xml = etree.Element('text')
       self.xmltree = etree.ElementTree(self.xml)
#        self.read_tcf()
       
    def __str__(self):
#         print self.tok_dic
#         print etree.tostring(self.xml, encoding='unicode', method='xml',pretty_print=True)
#         print etree.tostring(self.xmltree, encoding='unicode', method='xml',pretty_print=True)
        return "-------------"

    def open(self):
        with codecs.open(self.tcfile, encoding='utf-8', mode='r') as input:
            self.tree = etree.parse(input) # If XML is not well formed will rise an exception
        
    def get_layers(self):
        self.layers = self.tree.find('{}TextCorpus'.format(self.tc))
        
    def layer_is_present(self,layername):
        if any(item.tag == '{}{}'.format(self.tc,layername) for item in self.layers):
            return True
        else:
            return False
    
    def tokens_is_present(self):
        """
        Function to check if the tokens layer is present
        """
        if self.layer_is_present("tokens") == True:
            pass
        else:
            sys.exit("Ups! 'tokens' layer is not present, conversion aborted.")
    
    def get_metadata(self):
        self.language = self.tree.find('{}TextCorpus'.format(self.tc)).attrib["lang"]
        toolsinchain = self.tree.findall('//{}PID'.format(self.cmd))
        self.tools = []
        for i in toolsinchain:
            item = i.text
            item = re.sub(r"(http://hdl.handle.net/)?(.+)", r"\2", item)
            self.tools.append(item)
        (indirname, infilename) = os.path.split(self.tcfile)
        (self.fileid, inextension) = os.path.splitext(infilename)
        text = self.xmltree.getroot()
        text.set('id', self.fileid)
        text.set('lang', self.language)
        text.set('tools'," ".join(self.tools))
    
    def get_tokens(self):
        tokens = self.tree.findall('//{}{}'.format(self.tc,'token'))
        for i in tokens:
            tokenID = i.attrib["ID"]
            word = i.text
            self.tok_dic[tokenID] = {'word':word}
            
    def get_pos(self):
        if self.layer_is_present('POStags'):
            pos_layer = self.tree.find('//{}{}'.format(self.tc,'POStags'))
            self.tagsets.append(('pos',pos_layer.attrib['tagset']))
            for i in pos_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['pos'] = value
        else:
            pass
    
    def get_lemmas(self):
        if self.layer_is_present('lemmas'):
            lemmas_layer = self.tree.find('//{}{}'.format(self.tc,'lemmas'))
            for i in lemmas_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['lemma'] = value
        else:
            pass
    
    def get_pos_elements(self):
        self.get_pos()
        self.get_lemmas()

    def get_sentences(self,parent):
        for element in self.tree.iter('{}{}'.format(self.tc,'sentence')):
            s = etree.SubElement(parent, 's')
            if 'ID' in element.keys():
                s.attrib['id'] = element.attrib['ID']
            tokenIDs = element.attrib["tokenIDs"].split(" ")
            for i in tokenIDs:
                token = etree.SubElement(s, "token")
                token.attrib['id'] = i
                for j in self.tok_dic[i].items():
                    if j[0] == 'word':
                        token.text = j[1]
                    else:
                        token.attrib[j[0]] = j[1]

    def get_textspans(self,parent,stype,element,prefix):
        counter = 0
        for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan',stype)):
            item = etree.SubElement(parent, element)
            item.attrib["id"] = prefix+str(counter)
            item.attrib['start'] = i.attrib['start']
            item.attrib['end'] = i.attrib['end']
            counter +=1
# get entities very slow            
    def get_entities(self):
        if self.layer_is_present('namedEntities'):
            e_counter = 0
            entities = self.tree.findall('//{}{}'.format(self.tc,'entity'))
            for i in entities:
                dif_tok = []
                entity = etree.Element('e',id='e_'+str(e_counter))
                tokenIDs = i.attrib['tokenIDs'].split(" ")
                for j in tokenIDs:
                    token = etree.SubElement(entity, 'token', id=j)
                    dif_tok.append(j)
                    for h in self.tok_dic[j].items():
                        if h[0] == 'word':
                            token.text = h[1]
                        else:
                            token.attrib[h[0]] = h[1]
                e_counter += 1
                first = self.xml.find('.//{}[@id="{}"]'.format('token',tokenIDs[0]))
                first.addprevious(entity)
#                 here we start removing unnecessary tokens
                path = self.xmltree.getpath(first)
                r_counter = len(dif_tok)
                while r_counter > 0:
                    tbr = self.xmltree.xpath(path)[0]
                    tbr.getparent().remove(tbr)
                    r_counter += -1
        else:
            print "no named entities!" 

# Some of the loops could be converted into functions
    def get_textstructure(self):
        """With this I should reconstruct the structure and build it in an element.tree element"""
        if self.layer_is_present('textstructure'):
#             interventions             
            if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','div')) != None:
                div = []
                i_counter = 0
                for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','div')):
                    item = etree.SubElement(self.xml, 'div')
                    item.attrib["id"] = 'd_'+str(i_counter)
                    item.attrib['start'] = i.attrib['start']
                    item.attrib['end'] = i.attrib['end']
                    div.append(int(re.sub(r'.+?(\d+)',r'\1',i.attrib['end'])))
                    i_counter +=1
                if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
                    paragraph = []
                    p_counter = 0
                    for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')):
                        p_end = int(re.sub(r'.+?(\d+)',r'\1',i.attrib['end']))
                        paragraph.append(p_end)
                        for j in div:
                            if p_end<=j:
                                parent = self.xml.find('./div[@id="{}"]'.format('d_'+str(div.index(j))))
                                item = etree.SubElement(parent, 'p')
                                item.attrib["id"] = 'p_'+str(p_counter)
                                item.attrib['start'] = i.attrib['start']
                                item.attrib['end'] = i.attrib['end']
                                break
                        p_counter +=1
                    for k in self.tree.findall('//{}{}'.format(self.tc,'sentence')):
                        s_tokens = k.attrib['tokenIDs'].split(" ")
                        s_end = int(re.sub(r'.+?(\d+)',r'\1',s_tokens[-1]))
                        for l in paragraph:
                            if s_end<=l:
                                parent = self.xml.find('.//p[@id="{}"]'.format('p_'+str(paragraph.index(l))))
                                s = etree.SubElement(parent, 's')
                                if 'ID' in k.keys():
                                    s.attrib['id'] = k.attrib['ID']
#                                 tokenIDs = element.attrib["tokenIDs"].split(" ")
                                for m in s_tokens:
                                    token = etree.SubElement(s, "token")
                                    token.attrib['id'] = m
                                    for n in self.tok_dic[m].items():
                                        if n[0] == 'word':
                                            token.text = n[1]
                                        else:
                                            token.attrib[n[0]] = n[1]
                                break
                    self.get_entities()
#             elif self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
#                 self.get_textspans(self.xml,'paragraph','p','p_')
#             else:
#                 print 'Unknown structural element'
        else:
            print 'No structural elements found'
            self.get_sentences(self.xml)
            self.get_entities()
    
    def read_tcf(self):
        self.open()
        self.get_layers()
        self.tokens_is_present()
        self.get_metadata()
        self.get_tokens()
        self.get_pos_elements()
        self.get_textstructure()
#         print etree.tostring(self.xmltree, encoding='unicode', method='xml',pretty_print=True)
        return self.xmltree
#         self.get_sentences(self.xml)
#         self.get_entities()      
    
class TcfWriter(object):
    """Write a text in TCF format."""
    
    def __init__(self,xmltree,outfile):
        self.xmltree = xmltree
        self.outfile = outfile
        self.tc = "{http://www.dspin.de/data/textcorpus}"
        self.cmd = "{http://www.clarin.eu/cmd/}"
        self.md = "{http://www.dspin.de/data/metadata}"
        self.positional_elements = ["POStags","lemmas"]
        self.structural_elements = ["textstructure","sentences","namedEntities"]
        self.tok_dic = {}
        self.tagsets = []
        self.language = ''
        self.tools = []
        self.textid = ''
        self.xml = etree.Element('text')
        self.xmltree = etree.ElementTree(self.xml)
    
    def __str__(self):
        return "-------------"

    def serialize_tcf(self):
        """Output serialization in TCF format suitable for WebLicht"""
        
        # here we have to provide the logic
        tcf = etree.ElementTree(etree.fromstring(tcf)) # parse the string as an element and convert the element in a tree
        tcf.write(self.outfile, encoding="utf8", xml_declaration=True, method="xml") # write the result to a file
    
        # input should be an XML tree like the inline model where we have text,
        # tokens, and each token carries attributes, and it could happen that
        # there are sentences and other structural markup
        
    # create root element with all the necessary properties regarding NameSpaces
    
    # compulsory
    def create_metadata(self):
        pass
    
    # compulsory
    def get_tokens(self):
        self.layers = self.tree.find('{}TextCorpus'.format(self.tc))
    
    # compulsory
    def create_text_layer(self):
        pass
    
    # compulsory    
    def create_tokens_layer(self):
        pass
    
    def create_pos_layer(self):
        pass
    
    def create_lemma_layer(self):
        pass
    
    def create_sentences(self):
        pass
    
    def create_entities(self):
        pass
    
    def create_textstructure(self):
        pass
    
    
    
    def get_metadata(self):
        self.language = self.tree.find('{}TextCorpus'.format(self.tc)).attrib["lang"]
        toolsinchain = self.tree.findall('//{}PID'.format(self.cmd))
        self.tools = []
        for i in toolsinchain:
            item = i.text
            item = re.sub(r"(http://hdl.handle.net/)?(.+)", r"\2", item)
            self.tools.append(item)
        (indirname, infilename) = os.path.split(self.tcfile)
        (self.fileid, inextension) = os.path.splitext(infilename)
        text = self.xmltree.getroot()
        text.set('id', self.fileid)
        text.set('lang', self.language)
        text.set('tools'," ".join(self.tools))
    
    def get_tokens(self):
        tokens = self.tree.findall('//{}{}'.format(self.tc,'token'))
        for i in tokens:
            tokenID = i.attrib["ID"]
            word = i.text
            self.tok_dic[tokenID] = {'word':word}
            
    def get_pos(self):
        if self.layer_is_present('POStags'):
            pos_layer = self.tree.find('//{}{}'.format(self.tc,'POStags'))
            self.tagsets.append(('pos',pos_layer.attrib['tagset']))
            for i in pos_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['pos'] = value
        else:
            pass
    
    def get_lemmas(self):
        if self.layer_is_present('lemmas'):
            lemmas_layer = self.tree.find('//{}{}'.format(self.tc,'lemmas'))
            for i in lemmas_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['lemma'] = value
        else:
            pass
    
    def get_pos_elements(self):
        self.get_pos()
        self.get_lemmas()

    def get_sentences(self,parent):
        for element in self.tree.iter('{}{}'.format(self.tc,'sentence')):
            s = etree.SubElement(parent, 's')
            if 'ID' in element.keys():
                s.attrib['id'] = element.attrib['ID']
            tokenIDs = element.attrib["tokenIDs"].split(" ")
            for i in tokenIDs:
                token = etree.SubElement(s, "token")
                token.attrib['id'] = i
                for j in self.tok_dic[i].items():
                    if j[0] == 'word':
                        token.text = j[1]
                    else:
                        token.attrib[j[0]] = j[1]

    def get_textspans(self,parent,stype,element,prefix):
        counter = 0
        for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan',stype)):
            item = etree.SubElement(parent, element)
            item.attrib["id"] = prefix+str(counter)
            item.attrib['start'] = i.attrib['start']
            item.attrib['end'] = i.attrib['end']
            counter +=1
# get entities very slow            
    def get_entities(self):
        if self.layer_is_present('namedEntities'):
            e_counter = 0
            entities = self.tree.findall('//{}{}'.format(self.tc,'entity'))
            for i in entities:
                dif_tok = []
                entity = etree.Element('e',id='e_'+str(e_counter))
                tokenIDs = i.attrib['tokenIDs'].split(" ")
                for j in tokenIDs:
                    token = etree.SubElement(entity, 'token', id=j)
                    dif_tok.append(j)
                    for h in self.tok_dic[j].items():
                        if h[0] == 'word':
                            token.text = h[1]
                        else:
                            token.attrib[h[0]] = h[1]
                e_counter += 1
                first = self.xml.find('.//{}[@id="{}"]'.format('token',tokenIDs[0]))
                first.addprevious(entity)
#                 here we start removing unnecessary tokens
                path = self.xmltree.getpath(first)
                r_counter = len(dif_tok)
                while r_counter > 0:
                    tbr = self.xmltree.xpath(path)[0]
                    tbr.getparent().remove(tbr)
                    r_counter += -1
        else:
            print "no named entities!" 

# Some of the loops could be converted into functions
    def get_textstructure(self):
        """With this I should reconstruct the structure and build it in an element.tree element"""
        if self.layer_is_present('textstructure'):
#             interventions             
            if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','div')) != None:
                div = []
                i_counter = 0
                for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','div')):
                    item = etree.SubElement(self.xml, 'div')
                    item.attrib["id"] = 'd_'+str(i_counter)
                    item.attrib['start'] = i.attrib['start']
                    item.attrib['end'] = i.attrib['end']
                    div.append(int(re.sub(r'.+?(\d+)',r'\1',i.attrib['end'])))
                    i_counter +=1
                if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
                    paragraph = []
                    p_counter = 0
                    for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')):
                        p_end = int(re.sub(r'.+?(\d+)',r'\1',i.attrib['end']))
                        paragraph.append(p_end)
                        for j in div:
                            if p_end<=j:
                                parent = self.xml.find('./div[@id="{}"]'.format('d_'+str(div.index(j))))
                                item = etree.SubElement(parent, 'p')
                                item.attrib["id"] = 'p_'+str(p_counter)
                                item.attrib['start'] = i.attrib['start']
                                item.attrib['end'] = i.attrib['end']
                                break
                        p_counter +=1
                    for k in self.tree.findall('//{}{}'.format(self.tc,'sentence')):
                        s_tokens = k.attrib['tokenIDs'].split(" ")
                        s_end = int(re.sub(r'.+?(\d+)',r'\1',s_tokens[-1]))
                        for l in paragraph:
                            if s_end<=l:
                                parent = self.xml.find('.//p[@id="{}"]'.format('p_'+str(paragraph.index(l))))
                                s = etree.SubElement(parent, 's')
                                if 'ID' in k.keys():
                                    s.attrib['id'] = k.attrib['ID']
#                                 tokenIDs = element.attrib["tokenIDs"].split(" ")
                                for m in s_tokens:
                                    token = etree.SubElement(s, "token")
                                    token.attrib['id'] = m
                                    for n in self.tok_dic[m].items():
                                        if n[0] == 'word':
                                            token.text = n[1]
                                        else:
                                            token.attrib[n[0]] = n[1]
                                break
                    self.get_entities()
#             elif self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
#                 self.get_textspans(self.xml,'paragraph','p','p_')
#             else:
#                 print 'Unknown structural element'
        else:
            print 'No structural elements found'
            self.get_sentences(self.xml)
            self.get_entities()
    
    def read_tcf(self):
        self.open()
        self.get_layers()
        self.tokens_is_present()
        self.get_metadata()
        self.get_tokens()
        self.get_pos_elements()
        self.get_textstructure()
#         print etree.tostring(self.xmltree, encoding='unicode', method='xml',pretty_print=True)
        return self.xmltree
#         self.get_sentences(self.xml)
#         self.get_entities()    