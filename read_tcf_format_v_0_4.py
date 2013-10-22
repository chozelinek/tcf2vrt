#!/usr/bin/python
# -*- coding: utf-8 -*-

############################
#
#    read_tcf_format_v_0_4.py
#    by Jörg Didakowski
#
############################

######################################################################################
# In dieser Datei ist eine XML-Reader-Klasse Definiert, die das TCF-Format einliest #
######################################################################################

import xml.sax
import codecs
import sys
import time
import re
import os
from operator import itemgetter

###########################################################################
# klasse zur representation eines token #
###########################################################################
class token(object):

    m_iFrom = 0
    m_iTo = 0
    m_strForm = ''
    m_strId =''
    m_strTokenIDs=""

    def __init__(self,strForm,iFrom,iTo,strId,strTokenIDs=""):
        self.m_iFrom=int(iFrom)
        self.m_iTo=int(iTo)
        self.m_strForm=strForm
        self.m_strId=strId
        self.m_strTokenIDs=strTokenIDs
        pass

######################################
# handler zum parsen des analyse-xml #
######################################
class tcf_handler(xml.sax.ContentHandler):

    def __init__(self):
        self.mapTokSent = {}
        self.mapIdTok = {}
        self.m_iTokenCounter = 0;
        self.m_iSentenceCounter = 0;
        self.m_strSection = ''
        self.m_strSubsection = ''
        self.m_listTokens = []
        self.m_vSentences = []
        self.m_tokenDummy = token('',0,0,'')
        self.m_sentenceDummy = token('',0,0,'')
        self.m_bTokens = False
        self.m_bSentences = False
        self.m_strLanguage = ''
        return

    def split_name(self,qname):
        qname_split = qname.split(':')
        if len(qname_split) == 2:
            prefix, local = qname_split        
        else:
            prefix = None
            local = qname
        return prefix, local

    def startElement(self,qname,attrs):        
        name = self.split_name(qname)[1]
        ### D-Spin
        if name=="D-Spin":
            pass
        ### TextCorpus
        if name == 'TextCorpus':
            if attrs.has_key("lang"):
                self.m_strLanguage = attrs['lang']
        ### sentences
        elif name == 'sentences':
            self.m_strSection = 'sentences'
        ### sentence
        elif name == 'sentence' and self.m_strSection == 'sentences':            
            self.m_bSentences = True
            self.m_strSubsection = 'sentence'
            if attrs.has_key("ID"):
                self.m_sentenceDummy.m_strId = attrs['ID']
            else:
                self.m_iSentenceCounter = self.m_iSentenceCounter +1
                self.m_sentenceDummy.m_strId = 'l' + str(self.m_iSentenceCounter)

            if attrs.has_key("tokenIDs"):
                self.m_sentenceDummy.m_strTokenIDs = attrs['tokenIDs']
                splitDummy = self.m_sentenceDummy.m_strTokenIDs.split(' ')
                for i in splitDummy:
                    self.mapTokSent[i]=len(self.m_vSentences)                
        ### tokens
        elif name == 'tokens':
            self.m_strSection = 'tokens'
        ### token
        elif name == 'token' and self.m_strSection == 'tokens':            
            self.m_bTokens = True
            self.m_strSubsection = 'token'
            if attrs.has_key("start"):
                self.m_tokenDummy.m_iFrom = attrs['start']
            if attrs.has_key("end"):
                self.m_tokenDummy.m_iEnd = attrs['end']
            if attrs.has_key("ID"):
                self.m_tokenDummy.m_strId = attrs['ID']
            else:
                self.m_iTokenCounter = self.m_iTokenCounter +1
                self.m_tokenDummy.m_strId = 't' + str(self.m_iTokenCounter)
        ### text
        elif name == 'text':
            self.m_strSection = 'text'
            self.m_bText = True
        return

    def characters(self,name):
        ### token
        if self.m_strSubsection == 'token':
            self.m_tokenDummy.m_strForm = self.m_tokenDummy.m_strForm + name

    def endElement(self,qname):
        name = self.split_name(qname)[1]
        ### sentences
        if name == 'sentences':
            self.m_strSection = ''
        ### sentence
        elif name == 'sentence' and self.m_strSection == 'sentences':
            self.m_vSentences.append(token(self.m_sentenceDummy.m_strForm,self.m_sentenceDummy.m_iFrom,self.m_sentenceDummy.m_iTo,self.m_sentenceDummy.m_strId,self.m_sentenceDummy.m_strTokenIDs))
            self.m_strSubsection = ''
            self.m_sentenceDummy.m_strForm = ''
        ### tokens
        if name == 'tokens':
            self.m_strSection = ''
        ### token
        elif name == 'token' and self.m_strSection == 'tokens':
            self.m_listTokens.append(token(self.m_tokenDummy.m_strForm,self.m_tokenDummy.m_iFrom,self.m_tokenDummy.m_iTo,self.m_tokenDummy.m_strId))
            self.mapIdTok[self.m_tokenDummy.m_strId] = token(self.m_tokenDummy.m_strForm,self.m_tokenDummy.m_iFrom,self.m_tokenDummy.m_iTo,self.m_tokenDummy.m_strId)
            self.m_strSubsection = ''
            self.m_tokenDummy.m_strForm = ''
        ### text
        elif name == 'text':
            self.m_strSection=''
        return

####################################################################
# Klasse, die aus dem TCF-Format die Tokeninformationen rauszieht    #
####################################################################
class READ_TCF_FORMAT_v_0_4():
    theHandler = tcf_handler()

    def __init__(self):        
        return

    # parsen eines tcf-Strings
    def parse_string(self,strObj):
        self.__init__()
        xml.sax.parseString(strObj,self.theHandler)
        return

    # parsen einer tcf-Datei
    def parse_file(self,strFile):
        self.__init__()
        xml.sax.parse(strFile,self.theHandler)
        return

    def has_tokens(self):
        return self.theHandler.m_bTokens

    def get_language(self):
        return self.theHandler.m_strLanguage

    # zurueckgeben der aus der tcf-Datei extrahierten token mit den IDs satzweise in zwei separaten Listen
    # return: ([[tok1,tok2, ...] ... [tok1,tok2, ...]],[[id1,id2, ...] ... [id1,id2, ...]])
    def get_tokens_and_ids(self):
        mapToken={}
        for i in self.theHandler.m_listTokens:
            mapToken[i.m_strId] = i.m_strForm
        vvToken = []
        vvTokenId = []
        for i in self.theHandler.m_vSentences:
            vSent = []
            vId = []
            j = i.m_strTokenIDs.split(' ')
            for k in j:                
                vSent.append(mapToken[k])
                vId.append(k)
            vvToken.append(vSent)
            vvTokenId.append(vId)
        return (vvToken,vvTokenId)

    
