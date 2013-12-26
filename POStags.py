# -*- coding: utf-8 -*-

def function():
    layer = tree.find('//{}POStags'.format(tc))
    tagset = layer.attrib["tagset"]
    text.set("pos_tagset", tagset)
    element = etree.QName(layer[0]).localname #get the tag name
    attribute = "pos" #provide the attribute name to be added to tokens
    id_attrib = "tokenIDs"
    elements = list(layer)
    return (id_attrib, element, attribute, elements)