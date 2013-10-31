# -*- coding: utf-8 -*-

#
# list operations
#

def isList(list):
    import types
    return type(list) is types.ListType
