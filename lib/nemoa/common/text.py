# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def split_kwargs(s: str):
    """Return tuple with function name and function parameters."""

    if '(' not in s: return s, {}
    name = s.split('(')[0]
    args = asdict(s.lstrip(name).strip()[1:-1])

    return name, args

def astype(s: str, type = None):
    """ """

    if type == 'bool': return s.lower().strip() == 'true'
    if type == 'str': return s.strip().replace('\n', '')
    if type == 'int': return int(s)
    if type == 'float': return float(s)
    if type == 'list': return aslist(s)
    if type == 'tuple': return astuple(s)
    if type == 'dict': return asdict(s)

    return None

def aslist(s: str, delim = ','):
    """Return list from given string."""

    # check if string is valid and not blank
    if not isinstance(s, str) or not s or not s.strip(): return []

    # try python internal syntax grammar
    l = None
    if delim == ',':
        try: l = list(eval(s))
        except: pass
    if isinstance(l, list): return l

    # split string by delimiter
    l = [item.strip() for item in s.split(delim)]

    return l

def astuple(s: str, delim = ','):
    """Return tuple from given string."""

    # check if string is valid and not blank
    if not isinstance(s, str) or not s or not s.strip(): return ()

    # try python internal syntax grammar
    t = None
    if delim == ',':
        try: t = tuple(eval(s))
        except: pass
    if isinstance(t, tuple): return t

    # split string by delimiter
    t = tuple([item.strip() for item in s.split(delim)])

    return t

def asdict(s: str, delim = ','):
    """Return dictionary from given string in ini format."""

    # check if string is valid and not blank
    if not isinstance(s, str) or not s or not s.strip(): return {}

    import pyparsing

    pp_num = pyparsing.Word(pyparsing.nums + '.')
    pp_str = pyparsing.quotedString
    pp_bool = pyparsing.Or(pyparsing.Word("True") | pyparsing.Word("False"))
    pp_key = pyparsing.Word(pyparsing.alphas + "_",
        pyparsing.alphanums + "_.")
    pp_val = pyparsing.Or(pp_num | pp_str | pp_bool)

    # try dictionary dialect "<key> = <value>, ..."
    pp_term = pyparsing.Group(pp_key + '=' + pp_val)
    pp_term_lists = pp_term + pyparsing.ZeroOrMore(delim + pp_term)
    try: list = pp_term_lists.parseString(s.strip('{}'))
    except: list = None

    # try dictionary dialect "'<key>': <value>, ..."
    if list is None:
        pp_term = pyparsing.Group(pp_str + ':' + pp_val)
        pp_term_lists = pp_term + pyparsing.ZeroOrMore(delim + pp_term)
        try: list = pp_term_lists.parseString(s.strip('{}'))
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
