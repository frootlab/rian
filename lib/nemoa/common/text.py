# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Tuple, Optional

def splitargs(text: str) -> Tuple[str]:
    """Return tuple with function name and function arguments."""

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    import ast

    tree = ast.parse(text)

    # get function name
    func = tree.body[0].value.func.id

    # get list with arguments
    Args = tree.body[0].value.args
    args = tuple()
    for Arg in Args:
        typ = Arg._fields[0]
        val = getattr(Arg, typ)
        args += (val, )

    # get dictionary with keywords
    KwArgs = tree.body[0].value.keywords
    kwargs = {}
    for KwArg in KwArgs:
        key = KwArg.arg
        typ = KwArg.value._fields[0]
        val = getattr(KwArg.value, typ)
        kwargs[key] = val

    return func, args, kwargs

def astype(text: str, typ: Optional[str] = None) -> Any:
    """ """

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # Automatic Types
    if typ == None: return eval(text)

    # Basic Types
    if typ == 'str': return text.strip().replace('\n', '')
    if typ == 'bool': return text.lower().strip() == 'true'
    if typ == 'int': return int(text)
    if typ == 'float': return float(text)
    if typ == 'complex': return complex(text)

    # Composite Types
    if typ == 'list': return aslist(text)
    if typ == 'tuple': return astuple(text)
    if typ == 'set': return asset(text)
    if typ == 'dict': return asdict(text)

    raise KeyError(f"type '{typ}' is not supported")

def aslist(text: str, delim: str = ',') -> list:
    """Return list from given string."""

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # return empty list if string is blank
    if not text or not text.strip(): return list()

    # try python internal syntax grammar
    l = None
    if delim == ',':
        try: l = list(eval(text))
        except: pass
    if isinstance(l, list): return l

    # use dialect "<value>, ..."
    l = [item.strip() for item in text.split(delim)]

    return l

def astuple(text: str, delim: str = ',') -> tuple:
    """Return tuple from given string."""

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # return empty tuple if string is blank
    if not text or not text.strip(): return tuple()

    # try python internal syntax grammar
    t = None
    if delim == ',':
        try: t = tuple(eval(text))
        except: pass
    if isinstance(t, tuple): return t

    # use dialect "<value>, ..."
    l = [item.strip() for item in text.split(delim)]

    return tuple(l)

def asset(text: str, delim: str = ',') -> list:
    """Return set from given string."""

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # return empty set if string is blank
    if not text or not text.strip(): return set()

    # try python internal syntax grammar
    s = None
    if delim == ',':
        try: s = set(eval(text))
        except: pass
    if isinstance(s, set): return s

    # use dialect "<value>, ..."
    l = [item.strip() for item in text.split(delim)]

    return set(l)

def asdict(text: str, delim: str = ',') -> dict:
    """Return dictionary from given string in ini format."""

    # Check Argument Types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # check if string is blank
    if not text or not text.strip(): return {}

    import pyparsing as pp

    Num  = pp.Word(pp.nums + '.')
    Str  = pp.quotedString
    Bool = pp.Or(pp.Word("True") | pp.Word("False"))
    Key  = pp.Word(pp.alphas + "_", pp.alphanums + "_.")
    Val  = pp.Or(Num | Str | Bool)

    # try dictionary dialect "<key> = <value>, ..."
    Term = pp.Group(Key + '=' + Val)
    Terms = Term + pp.ZeroOrMore(delim + Term)
    try: l = Terms.parseString(text.strip('{}'))
    except: l = None

    # try dictionary dialect "'<key>': <value>, ..."
    if not l:
        Term = pp.Group(Str + ':' + Val)
        Terms = Term + pp.ZeroOrMore(delim + Term)
        try: l = Terms.parseString(text.strip('{}'))
        except: return {}

    # create dictionary from list
    d = {}
    for item in l:
        if len(item) == 1:
            if item[0] == ',': continue
            d[item] = True
            continue
        try: key, value = item[0].strip('\'\"'), eval(item[2])
        except: continue

        d[key] = value
        if not isinstance(d[key], str): continue
        d[key] = d[key].strip()

    return d
