#!/usr/bin/env python -w
# -*- coding: utf-8 -*-

"""
Module to manipalute files in TCF format.
"""

# Falta montar los elementos estructurales

# Empezar por frase, párrafo, intervención

# Frases OK

# Párrafos buscar la frase que contiene el primer token,
# añadir tantas frases hasta llegar a la que contenga el último

# Intervenciones, agregar los párrafos que contengan desde el primer hasta el
# último token

#Los elementos estructurales por encima de la frase son ad hoc, por lo tanto a
# implementar en cada caso particular

#Los elementos estructurales que producen mixed XML, como las dificultades o
# named entities revisten complejidad, porque
# hemos de incrustarlos dentro de las frases ya existentes.

# revisa el texto ep2_master, en la estructura del texto hemos incluido el
# título del debate, cuando, o no debería estarlo, o si lo está habría que
# etiquetarlo como título y no como parte de una intervención

import codecs # to handle properly unicode
import re
import sys

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
       self.xml = etree.Element('text')
       self.__read_tcf()
       
    def __str__(self):
#         print self.tok_dic
        print etree.tostring(self.xml, encoding='unicode', method='xml',pretty_print=True)
        return "-------------"

    def __open(self):
        with codecs.open(self.tcfile, encoding='utf-8', mode='r') as input:
            self.tree = etree.parse(input) # If XML is not well formed will rise an exception
        
    def __get_layers(self):
        self.layers = self.tree.find('{}TextCorpus'.format(self.tc))
        
#     def __get_elements(self):
#         self.elements = ((etree.QName(layer)).localname for layer in self.layers)
    
    def __layer_is_present(self,layername):
#         if any(item.tag == '{}{}'.format(tc,layername) for item in layers):#can this with in instead any
        if any(item.tag == '{}{}'.format(self.tc,layername) for item in self.layers):
            return True
        else:
            return False
    
    def __tokens_is_present(self):
        """
        Function to check if the tokens layer is present
        """
        if self.__layer_is_present("tokens") == True:
            pass
        else:
            sys.exit("Ups! 'tokens' layer is not present, conversion aborted.")
    
    def __get_metadata(self):
        self.language = self.tree.find('{}TextCorpus'.format(self.tc)).attrib["lang"]
        toolsinchain = self.tree.findall('//{}PID'.format(self.cmd))
        self.tools = []
        for i in toolsinchain:
            item = i.text
            item = re.sub(r"(http://hdl.handle.net/)?(.+)", r"\2", item)
            self.tools.append(item)
    
    def __get_tokens(self):
        tokens = self.tree.findall('//{}{}'.format(self.tc,'token'))
        for i in tokens:
            tokenID = i.attrib["ID"]
            word = i.text
            self.tok_dic[tokenID] = {'word':word}
            
    def __get_pos(self):
        if self.__layer_is_present('POStags'):
            pos_layer = self.tree.find('//{}{}'.format(self.tc,'POStags'))
            self.tagsets.append(('pos',pos_layer.attrib['tagset']))
            for i in pos_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['pos'] = value
        else:
            pass
    
    def __get_lemmas(self):
        if self.__layer_is_present('lemmas'):
            lemmas_layer = self.tree.find('//{}{}'.format(self.tc,'lemmas'))
            for i in lemmas_layer:
                tokenID = i.attrib['tokenIDs']
                value = i.text
                self.tok_dic[tokenID]['lemma'] = value
        else:
            pass
    
    def __get_pos_elements(self):
        self.__get_pos()
        self.__get_lemmas()

    def __get_sentences(self,parent):
        for element in self.tree.iter('{}{}'.format(self.tc,'sentence')):
            s = etree.SubElement(parent, 's')
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

    def __get_textspans(self,parent,stype,element,prefix):
        counter = 0
        for i in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan',stype)):
            item = etree.SubElement(parent, element)
            item.attrib["id"] = prefix+str(counter)
            item.attrib['start'] = i.attrib['start']
            item.attrib['end'] = i.attrib['end']
            counter +=1
            
    def __get_entities(self):
        if self.__layer_is_present('namedEntities'):
            counter = 0
            entities = self.tree.findall('//{}{}'.format(self.tc,'entity'))
            dif_tok = []
            for i in entities:
                entity = etree.Element('e',id='e_'+str(counter))
                tokenIDs = i.attrib['tokenIDs'].split(" ")
                for j in tokenIDs:
                    token = etree.SubElement(entity, 'token', id=j)
                    dif_tok.append(j)
                    for h in self.tok_dic[j].items():
                        if h[0] == 'word':
                            token.text = h[1]
                        else:
                            token.attrib[h[0]] = h[1]
                counter += 1
                first = self.xml.find('.//{}[@id="{}"]'.format('token',tokenIDs[0]))
                first.addprevious(entity)
            for l in dif_tok:
                items = self.xml.findall('.//s/token[@id="{}"]'.format(l))
                for item in items:
                    item.getparent().remove(item)
        else:
            print "no named entities!"
 
    def __get_hierarchical_ts(self,parent,child):
        parents = self.xml.findall('//{}'.format(parent))
        children = self.tree.findall('//{}{}'.format(self.tc,child))
        ichildren = iter(children)
        for i in parents: 
            child = next(ichildren)
            p_start = i.attrib['start']
            p_end = i.attrib['end']       
            while child >= p_start and child <= p_end:
                i.append(child)
            
    
    def __is_in_span(self,parent,child):

        pass
    
    def __get_textstructure(self):
        """With this I should reconstruct the structure and build it in an element.tree element"""
        if self.__layer_is_present('textstructure'):
            if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','intervention')) != None:
                self.__get_textspans(self.xml,'intervention','intervention','i_')
#                 if self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
#                     children = iter(self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')))
#                     parents = self.xml.iter('{}'.format('intervention'))
#                     for i in parents:
# #                         print i.attrib['id']
#                         p_start = i.attrib['start'].split('_')
#                         p_end = i.attrib['end'].split('_')
#                         child = children.next()
#                         for i in children:
#                             c_start = child.attrib['start'].split('_')
#                             c_end = child.attrib['end'].split('_')
#                             if c_start[1] >= p_start[1] and c_end[1] <= p_end[1]:
#                                 print c_start, p_start, c_end, p_end 
#                                 child = children.next()
#                         parents.next()
#                          
#                     self.__get_textspans(self.xml,'paragraph','p','p_')
#                 counter = 0
#                 for element in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','intervention')):
#                     intervention = etree.SubElement(self.xml, "intervention")
#                     intervention.attrib["id"] = 'in_'+str(counter)
#                     intervention.attrib['start'] = element.attrib['start']
#                     intervention.attrib['end'] = element.attrib['end']
#                     counter +=1
            elif self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
                self.__get_textspans(self.xml,'paragraph','p','p_')
#                 counter = 0
#                 for element in self.tree.findall('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')):
#                     paragraph = etree.SubElement(self.xml, "p")
#                     paragraph.attrib["id"] = 'p_'+str(counter)
#                     paragraph.attrib['start'] = element.attrib['start']
#                     paragraph.attrib['end'] = element.attrib['end']
#                     counter += 1
            else:
                print 'mogambo'
        #             elif self.tree.find('//{}{}[@type="{}"]'.format(self.tc,'textspan','paragraph')) != None:
#                 elif element.attrib['type'] == 'paragraph':
#                     paragraph = etree.SubElement(self.xml, "p")
#                     paragraph.attrib["id"] = 'p_'+str(paragraph_counter)
#                     paragraph.attrib['start'] = element.attrib['start']
#                     paragraph.attrib['end'] = element.attrib['end']
#                     paragraph_counter += 1
#                 else:
#                     print element.attrib['type']
                 
                    
        else:
            print 'No structural elements found'
            #self.__get_sentences(self.xml)
    
    def __read_tcf(self):
        self.__open()
        self.__get_layers()
        self.__tokens_is_present()
        self.__get_metadata()
        self.__get_tokens()
        self.__get_pos_elements()
        self.__get_textstructure()
        self.__get_sentences(self.xml)
        self.__get_entities()      
    