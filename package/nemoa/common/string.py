# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import binascii
import pyparsing

def str_to_hash(str):
    """Return crc32 hash-valkue of given string."""
    return abs(binascii.crc32(str))

def str_split_params(str):
    """Return tuple with function name and function parameters."""
    if not '(' in str: return str, {}
    func_name = str.split('(')[0]
    func_params = str_to_dict(str.lstrip(func_name).strip()[1:-1])
    return func_name, func_params

def str_to_type(string, type = None):
    if type == 'bool': return string.lower().strip() == 'true'
    if type == 'str': return string.strip().replace('\n', '')
    if type == 'int': return int(string)
    if type == 'float': return float(string)
    if type == 'list': return str_to_list(string)
    if type == 'dict': return str_to_dict(string)
    return string

def str_to_list(string, delim = ','):
    """Return list from given string."""
    return [item.strip() for item in string.split(delim)]

def str_from_list(list, delim = ','):
    """Return string from given list."""
    return delim.join(list)

def str_to_dict(string, delim = ','):
    """Return dictionary from given string in ini format."""
    if string.strip() == '': return {}

    pp_num = pyparsing.Word(pyparsing.nums + '.')
    pp_str = pyparsing.quotedString
    pp_bool = pyparsing.Or(
        pyparsing.Word("True") | pyparsing.Word("False"))
    pp_key = pyparsing.Word(pyparsing.alphas + "_",
        pyparsing.alphanums + "_.")
    pp_val = pyparsing.Or(pp_num | pp_str | pp_bool)

    # try dictionary dialect "<key> = <value>, ..."
    pp_term = pyparsing.Group(pp_key + '=' + pp_val)
    pp_term_lists = pp_term + pyparsing.ZeroOrMore(delim + pp_term)
    try: list = pp_term_lists.parseString(string.strip('{}'))
    except: list = None

    # try dictionary dialect "'<key>': <value>, ..."
    if list == None:
        pp_term = pyparsing.Group(pp_str + ':' + pp_val)
        pp_term_lists = pp_term + pyparsing.ZeroOrMore(delim + pp_term)
        try: list = pp_term_lists.parseString(string.strip('{}'))
        except: return {}

    # create dictionary
    dictionary = {}
    for item in list:
        if len(item) == 1:
            if item[0] == ',': continue
            dictionary[item] = True
            continue
        try:
            key = item[0].strip('\'\"')
            value = eval(item[2])
        except: continue

        dictionary[key] = value
        if isinstance(dictionary[key], str):
            dictionary[key] = dictionary[key].strip()

    return dictionary

def str_format_unit_label(string):
    """Return TeX style unit String used for plots."""
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
