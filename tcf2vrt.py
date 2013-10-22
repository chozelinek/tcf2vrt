#!/usr/bin/python
# -*- coding: utf-8 -*-

############################
#
#    tcf_wrapper.py
#    by Jörg Didakowski
#
############################

# Vorsicht, hier funktionieren die Namespaces noch nicht.
# das muss noch implementiert werden !

# der aufruf des seminer-Programms muss noch angepasst werden (call_seminer/0)

import cgi
import string, sys, os
import re
from read_tcf_format_v_0_4 import READ_TCF_FORMAT_v_0_4
import codecs

###########################################################################
# klasse die den TCF-Wrapper für Seminer implementiert
###########################################################################
class TCF_WRAPPER:
        
    def __init__ (self):
        # nach belieben Konfigurieren
        self.m_strFileInterfaceIn = 'seminer_in.txt'
        self.m_strFileInterfaceOut = 'seminer_out.txt'
        self.m_strSeminerModel = 'raw'    # 'full'

        self.m_vvToken = []
        self.m_vvTokenId = []
        self.m_vvNeClass = []
        self.m_strRequest = ""
        pass

    # aufrufen des Programms seminer
    def call_seminer (self):
        # os.system("./seminer %s <%s >%s" % (self.m_strSeminerModel,self.m_strFileInterfaceIn,self.m_strFileInterfaceOut) )
        # os.system("echo hier noch den seminer-Aufruf einfügen")
        os.system("/Users/jmmmac/resources/sequor-0.3.0/bin/seminer %s <%s >%s" % (self.m_strSeminerModel,self.m_strFileInterfaceIn,self.m_strFileInterfaceOut) )

    # integrieren der NE-Information in das TCF-XML
    def merge_information (self, clarinxml, insert):
        sresult = re.search("</[\w]*:?TextCorpus>", clarinxml)
        pos = sresult.start()
        return clarinxml[0:pos] + insert + clarinxml[pos:]

    # formatieren der Token als seminer-Eingabeformat
    def token_2_seminer (self, vvToken):
        vDummy1 = []
        for i in vvToken:
            vDummy2 = []
            for j in i:
                vDummy2.append(j)
                vDummy2.append('\n')
            if len(vDummy1) > 0:
                vDummy1.append('\n')
            vDummy1.append(''.join(vDummy2))
        return ''.join(vDummy1)

    # extrahieren der NE-Klassifizierungen aus der seminer-Ausgabe
    def seminer_2_neclass (self, fileIn):
        vNeClass = []
        vvNeClass = []
        vLine = fileIn.readlines()
        for i in vLine:
            strLine = i.rstrip('\n')
            if strLine == "":
                vvNeClass.append(vNeClass)
                vNeClass = []
            else:
                vNeClass.append(strLine)
        return vvNeClass

    # formatieren von tcf-entity
    def format_tcf_entity (self, vvNeClass, vvTokenIds):
        vTCF = []
        iIdCounter = 0
        for i in range(0, len(vvNeClass)):
            for j in range(0, len(vvNeClass[i])):
                if vvNeClass[i][j] != "O":
                    vTCF.append("<entity ID=\"%s\" class=\"%s\" tokenIDs=\"%s\"/>" % ("ne_" + str(iIdCounter), vvNeClass[i][j], vvTokenIds[i][j]))
                    iIdCounter += 1
        return ''.join(vTCF)

    # formatieren von tcf-entities
    def format_tcf_entities (self, strEntity):
        return "<namedEntities type=\"CoNLL2002\">" + strEntity + "</namedEntities>"

    # wrapper um seminer wird aufgerufen
    def process(self, strFileTcfIn, strFileTcfOut):
        self.read_tcf(strFileTcfIn)
        self.write_seminer_input(self.m_strFileInterfaceIn)
        self.call_seminer()
        self.read_seminer_output(self.m_strFileInterfaceOut)
        self.write_tcf(strFileTcfOut)

    # einlesen des tcf-Formats
    def read_tcf (self, strFilename):
        fileTcfIn = codecs.open(strFilename, 'r', 'utf8')
        self.m_strRequest = ''.join(fileTcfIn.readlines())
        fileTcfIn.close()
        data_v_0_4 = READ_TCF_FORMAT_v_0_4()
        data_v_0_4.parse_string(self.m_strRequest.encode('utf8'))
        (self.m_vvToken, self.m_vvTokenId) = data_v_0_4.get_tokens_and_ids()

    # schreiben der seminer-Eingabe
    def write_seminer_input (self, strFilename):
        strSeminerInput = self.token_2_seminer(self.m_vvToken)
        fileInterfaceOut = codecs.open(strFilename, 'w', 'utf8')
        fileInterfaceOut.write(strSeminerInput)
        fileInterfaceOut.close()

    # lesen der Seminer-Ausgabe
    def read_seminer_output (self, strFilename):
        fileInterfaceIn = codecs.open(strFilename, 'r', 'utf8')
        self.m_vvNeClass = self.seminer_2_neclass(fileInterfaceIn)
        fileInterfaceIn.close()

    # schreiben der tcf-Datei
    def write_tcf (self, strFilename):
        strTcfEntities = self.format_tcf_entities (self.format_tcf_entity(self.m_vvNeClass, self.m_vvTokenId))
        fileOut = codecs.open(strFilename, 'w', 'utf8')
        fileOut.write(self.merge_information (self.m_strRequest, strTcfEntities))
        fileOut.close()


### MAIN ###############################

wrapper = TCF_WRAPPER()
wrapper.process ("./in2.tcf", "./out2.tcf")
