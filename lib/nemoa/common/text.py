# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def split_kwargs(string):
    """Return tuple with function name and function parameters."""

    if not '(' in string: return string, {}
    name = string.split('(')[0]
    args = asdict(string.lstrip(name).strip()[1:-1])
    return name, args

def astype(string, type = None):
    if type == 'bool': return string.lower().strip() == 'true'
    if type == 'str': return string.strip().replace('\n', '')
    if type == 'int': return int(string)
    if type == 'float': return float(string)
    if type == 'list': return aslist(string)
    if type == 'dict': return asdict(string)
    return string

def aslist(string, delim = ','):
    """Return list from given string."""

    return [item.strip() for item in string.split(delim)]

def asdict(string, delim = ','):
    """Return dictionary from given string in ini format."""

    if string.strip() == '': return {}

    import pyparsing

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
