# -*- coding: utf-8 -*-

def function():
    layer = tree.find('//{}lemmas'.format(tc))
    element = etree.QName(layer[0]).localname #get the tag name
    attribute = "lemma" #provide the attribute name to be added to tokens
    id_attrib = "tokenIDs"
    elements = list(layer)
    return (id_attrib, element, attribute, elements)