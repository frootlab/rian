# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Tuple, Optional

def splitargs(text: str) -> Tuple[str, tuple, dict]:
    """Split a function call in the function name, its arguments and keywords.

    Args:
        text: Function call given as valid Python code. Beware: Function
            definitions are no valid function calls.

    Returns:
        A tuple consisting of the function name as string, the arguments as
        tuple and the keywords as dictionary.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")

    import ast
    tree = ast.parse(text)

    # get function name
    func = tree.body[0].value.func.id

    # get tuple with arguments
    Args = tree.body[0].value.args
    args = []
    for Arg in Args:
        typ = Arg._fields[0]
        val = getattr(Arg, typ)
        args.append(val)
    args = tuple(args)

    # get dictionary with keywords
    KwArgs = tree.body[0].value.keywords
    kwargs = {}
    for KwArg in KwArgs:
        key = KwArg.arg
        typ = KwArg.value._fields[0]
        val = getattr(KwArg.value, typ)
        kwargs[key] = val

    return func, args, kwargs

def astype(text: str, fmt: Optional[str] = None, **kwargs: Any) -> Any:
    """Convert text into given target format.

    Args:
        text: String representing the value of a given type in it's respective
            syntax format. Thereby the standard format corresponds to the
            representation, which is obtained by an application of the 'str'
            function. Some types however also accept additional formats, which
            e.g. appear in the formatting of ini files.
        fmt: Target format in which the text is converted.
        **kwargs: Supplementary parameters, that specify the target format

    Returns:
        Value of the text in given target format.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")

    # evaluate text if no format is given
    if fmt == None: return eval(text)

    # basic types
    if fmt == 'str': return text.strip().replace('\n', '')
    if fmt == 'bool': return text.lower().strip() == 'true'
    if fmt == 'int': return int(text)
    if fmt == 'float': return float(text)
    if fmt == 'complex': return complex(text)

    # sequence types
    if fmt == 'list': return aslist(text, **kwargs)
    if fmt == 'tuple': return astuple(text, **kwargs)
    if fmt == 'set': return asset(text, **kwargs)
    if fmt == 'dict': return asdict(text, **kwargs)

    raise KeyError(f"type '{fmt}' is not supported")

def aslist(text: str, delim: str = ',') -> list:
    """Convert text into list.

    Args:
        text: String representing a list. Valid representations are:
            Python format: Allows elements of arbitrary types:
                Example: "['a', 'b', 3]"
            Delimiter separated values (DSV): Allows string elements:
                Example: "a, b, c"
        delim: A string, which is used as delimiter for the separatation of the
            text. This parameter is only used in the DSV format.

    Returns:
        Value of the text as list.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")
    if not isinstance(delim, str):
        raise TypeError("argument 'delim' requires type "
            f"'str', not '{type(text)}'")

    # return empty list if the string is blank
    if not text or not text.strip(): return list()

    # python format
    l = None
    if delim == ',':
        try: l = list(eval(text))
        except: pass
    if isinstance(l, list): return l

    # Delimited String Fromat: "<value>, ..."
    l = [item.strip() for item in text.split(delim)]

    return l

def astuple(text: str, delim: str = ',') -> tuple:
    """Convert text into tuple.

    Args:
        text: String representing a tuple. Valid representations are:
            Python format: Allows elements of arbitrary types:
                Example: "('a', 'b', 3)"
            Delimiter separated values (DSV): Allows string elements:
                Example: "a, b, c"
        delim: A string, which is used as delimiter for the separatation of the
            text. This parameter is only used in the DSV format.

    Returns:
        Value of the text as tuple.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")
    if not isinstance(delim, str):
        raise TypeError("argument 'delim' requires type "
            f"'str', not '{type(text)}'")

    # return empty tuple if the string is blank
    if not text or not text.strip(): return tuple()

    # python format
    t = None
    if delim == ',':
        try: t = tuple(eval(text))
        except: pass
    if isinstance(t, tuple): return t

    # delimited string format
    l = [item.strip() for item in text.split(delim)]

    return tuple(l)

def asset(text: str, delim: str = ',') -> list:
    """Convert text into set.

    Args:
        text: String representing a set. Valid representations are:
            Python format: Allows elements of arbitrary types:
                Example: "{'a', 'b', 3}"
            Delimiter separated values (DSV): Allows string elements:
                Example: "a, b, c"
        delim: A string, which is used as delimiter for the separatation of the
            text. This parameter is only used in the DSV format.

    Returns:
        Value of the text as set.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")
    if not isinstance(delim, str):
        raise TypeError("argument 'delim' requires type "
            f"'str', not '{type(text)}'")

    # return empty set if the string is blank
    if not text or not text.strip(): return set()

    # python format
    s = None
    if delim == ',':
        try: s = set(eval(text))
        except: pass
    if isinstance(s, set): return s

    # delimited string format
    l = [item.strip() for item in text.split(delim)]

    return set(l)

def asdict(text: str, delim: str = ',') -> dict:
    """Convert text into dictionary.

    Args:
        text: String representing a dictionary. Valid representations are:
            Python format: Allows keys and values of arbitrary types:
                Example: "{'a': 2, 1: True}"
            Delimiter separated expressions: Allow string keys and values:
                Example (Variant A): "<key> = <value><delim> ..."
                Example (Variant B): "'<key>': <value><delim> ..."
        delim: A string, which is used as delimiter for the separatation of the
            text. This parameter is only used in the DSV format.

    Returns:
        Value of the text as dictionary.

    """

    # check argument types
    if not isinstance(text, str):
        raise TypeError("argument 'text' requires type "
            f"'str', not '{type(text)}'")
    if not isinstance(delim, str):
        raise TypeError("argument 'delim' requires type "
            f"'str', not '{type(text)}'")

    # return empty dict if the string is blank
    if not text or not text.strip(): return dict()

    import pyparsing as pp

    Num  = pp.Word(pp.nums + '.')
    Str  = pp.quotedString
    Bool = pp.Or(pp.Word("True") | pp.Word("False"))
    Key  = pp.Word(pp.alphas + "_", pp.alphanums + "_.")
    Val  = pp.Or(Num | Str | Bool)

    # try dictionary format "<key> = <value><delim> ..."
    Term = pp.Group(Key + '=' + Val)
    Terms = Term + pp.ZeroOrMore(delim + Term)
    try: l = Terms.parseString(text.strip('{}'))
    except: l = None

    # try dictionary format "'<key>': <value><delim> ..."
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
