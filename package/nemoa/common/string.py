#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# string operations
#

def strToHash(str):
    import binascii
    return abs(binascii.crc32(str))

def strSplitParams(str):
    if not '(' in str:
        return str, {}

    funcName = str.split('(')[0]
    funcParams = strToDict(str.lstrip(funcName).strip()[1:-1])
    return funcName, funcParams

def strToList(str, delim = ','):
    list = []
    for item in str.split(delim):
        list.append(item.strip())
    return list

def strToDict(string, delim = ','):
    if string.strip() == '':
        return {}

    import pyparsing as pp
    ppNumber = pp.Word(pp.nums + '.')
    ppString = pp.quotedString
    ppBool = pp.Or(pp.Word("True") | pp.Word("False"))
    ppKey = pp.Word(pp.alphas + "_", pp.alphanums + "_.")
    ppValue = pp.Or(ppNumber | ppString | ppBool)
    ppTerm = pp.Group(ppKey + '=' + ppValue)
    ppTermLists = ppTerm + pp.ZeroOrMore(delim + ppTerm)

    try:
        list = ppTermLists.parseString(string)
    except:
        return {}

    # create dictionary
    dict = {}
    for item in list:
        if len(item) == 1:
            if item[0] == ',':
                continue
            dict[item] = True
            continue
        key = item[0]
        value = item[2]
        try:
            dict[key] = eval(value)
        except:
            continue
        if isinstance(dict[key], str):
            dict[key] = dict[key].strip()

    return dict

