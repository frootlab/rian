# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Tuple, Optional

def splitargs(text: str) -> Tuple[str]:
    """Return tuple with function name and function arguments."""

    # check types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    if '(' not in text: return text, {}
    name = text.split('(')[0]
    args = asdict(text.lstrip(name).strip()[1:-1])

    return name, args

def astype(text: str, type: Optional[str] = None) -> Any:
    """ """

    # check types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    if type == 'bool': return text.lower().strip() == 'true'
    if type == 'str': return text.strip().replace('\n', '')
    if type == 'int': return int(text)
    if type == 'float': return float(text)
    if type == 'list': return aslist(text)
    if type == 'tuple': return astuple(text)
    if type == 'dict': return asdict(text)

    return None

def aslist(text: str, delim: str = ',') -> list:
    """Return list from given string."""

    # check types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # check if string is blank
    if not text or not text.strip(): return []

    # try python internal syntax grammar
    l = None
    if delim == ',':
        try: l = list(eval(text))
        except: pass
    if isinstance(l, list): return l

    # split string by delimiter
    l = [item.strip() for item in text.split(delim)]

    return l

def astuple(text: str, delim: str = ',') -> tuple:
    """Return tuple from given string."""

    # check types
    if not isinstance(text, str): raise TypeError(
        f"argument 'text' requires to be of type 'str', not '{type(text)}'")

    # check if string is valid and not blank
    if not text or not text.strip(): return ()

    # try python internal syntax grammar
    t = None
    if delim == ',':
        try: t = tuple(eval(text))
        except: pass
    if isinstance(t, tuple): return t

    # split string by delimiter
    t = tuple([item.strip() for item in text.split(delim)])

    return t

def asdict(text: str, delim: str = ',') -> dict:
    """Return dictionary from given string in ini format."""

    # check types
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

    # try dictionary dialect "<key>: <value>, ..."
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
