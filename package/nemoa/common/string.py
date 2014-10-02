# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import binascii
import pyparsing

def str_to_hash(str):
    """return crc32 hash-valkue of given string."""
    return abs(binascii.crc32(str))

def str_split_params(str):
    """return tuple with function name and function parameters."""
    if not '(' in str: return str, {}
    funcName = str.split('(')[0]
    funcParams = str_to_dict(str.lstrip(funcName).strip()[1:-1])
    return funcName, funcParams

def str_to_list(str, delim = ','):
    """return list from given string."""
    return [item.strip() for item in str.split(delim)]

def str_to_dict(string, delim = ','):
    """return dictionary from given string in ini format."""
    if string.strip() == '': return {}
    ppNum  = pyparsing.Word(pyparsing.nums + '.')
    ppStr  = pyparsing.quotedString
    ppBool = pyparsing.Or(pyparsing.Word("True") | pyparsing.Word("False"))
    ppKey  = pyparsing.Word(pyparsing.alphas + "_", pyparsing.alphanums + "_.")
    ppVal  = pyparsing.Or(ppNum | ppStr | ppBool)
    ppTerm = pyparsing.Group(ppKey + '=' + ppVal)
    ppTermLists = ppTerm + pyparsing.ZeroOrMore(delim + ppTerm)

    try: list = ppTermLists.parseString(string)
    except: return {}

    # create dictionary
    dict = {}
    for item in list:
        if len(item) == 1:
            if item[0] == ',': continue
            dict[item] = True
            continue
        key = item[0]
        value = item[2]
        try: dict[key] = eval(value)
        except: continue
        if isinstance(dict[key], str): dict[key] = dict[key].strip()

    return dict

def str_format_unit_label(string):
    """return TeX style unit String used for plots."""
    text = string.rstrip(''.join([str(x) for x in xrange(0, 10)]))
    return '$%s_{%d}$' % (text, int(string.lstrip(text)))

def str_doc_trim(string):
    if not string: return ''

    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = string.expandtabs().splitlines()

    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped: indent = min(indent, len(line) - len(stripped))

    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]: trimmed.append(line[indent:].rstrip())

    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]: trimmed.pop()
    while trimmed and not trimmed[0]: trimmed.pop(0)

    # Return a single string:
    return '\n'.join(trimmed)
