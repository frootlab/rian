# -*- coding: utf-8 -*-
"""Collection of frequently used string conversion functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import ast
import sys

try:
    import pyparsing as pp
except ImportError as err:
    raise ImportError(
        "requires package pyparsing: "
        "https://pypi.org/project/pyparsing/") from err

from nemoa.base import check
from nemoa.types import Any, OptStr, Tuple, Path

def splitargs(text: str) -> Tuple[str, tuple, dict]:
    """Split a function call in the function name, its arguments and keywords.

    Args:
        text: Function call given as valid Python code. Beware: Function
            definitions are no valid function calls.

    Returns:
        A tuple consisting of the function name as string, the arguments as
        tuple and the keywords as dictionary.

    """
    # Check type of 'text'
    check.has_type("first argument 'text'", text, str)

    # Get function name
    try:
        tree = ast.parse(text)
        func = getattr(getattr(getattr(tree.body[0], 'value'), 'func'), 'id')
    except SyntaxError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err
    except AttributeError as err:
        raise ValueError(f"'{text}' is not a valid function call") from err

    # Get tuple with arguments
    astargs = getattr(getattr(tree.body[0], 'value'), 'args')
    largs = []
    for astarg in astargs:
        typ = astarg._fields[0]
        val = getattr(astarg, typ)
        largs.append(val)
    args = tuple(largs)

    # Get dictionary with keywords
    astkwds = getattr(getattr(tree.body[0], 'value'), 'keywords')
    kwds = {}
    for astkw in astkwds:
        key = astkw.arg
        typ = astkw.value._fields[0]
        val = getattr(astkw.value, typ)
        kwds[key] = val

    return func, args, kwds

def astype(text: str, fmt: OptStr = None, **kwds: Any) -> Any:
    """Convert text into given target format.

    Args:
        text: String representing the value of a given type in it's respective
            syntax format. Thereby the standard format corresponds to the
            representation, which is obtained by an application of the 'str'
            function. Some types however also accept additional formats, which
            e.g. appear in the formatting of ini files.
        fmt: Target format in which the text is converted.
        **kwds: Supplementary parameters, that specify the target format

    Returns:
        Value of the text in given target format.

    """
    # Check Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_opt_type("argument 'fmt'", fmt, str)

    # Evaluate text if no format is given
    if fmt is None:
        return ast.literal_eval(text)

    # Basic types
    if fmt == 'str':
        return text.strip().replace('\n', '')
    if fmt == 'bool':
        return text.lower().strip() == 'true'
    if fmt == 'int':
        return int(text)
    if fmt == 'float':
        return float(text)
    if fmt == 'complex':
        return complex(text)

    # Sequence and special types
    stypes = ['list', 'tuple', 'set', 'dict', 'path']
    if fmt in stypes:
        return getattr(sys.modules[__name__], 'as' + fmt)(text, **kwds)

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
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argument 'delim'", delim, str)

    # return empty list if the string is blank
    if not text or not text.strip():
        return list()

    # python format
    val = None
    if delim == ',':
        try:
            val = list(ast.literal_eval(text))
        except (SyntaxError, ValueError, Warning):
            pass
    if isinstance(val, list):
        return val

    # Delimited String Fromat: "<value>, ..."
    return [item.strip() for item in text.split(delim)]

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
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argument 'delim'", delim, str)

    # Return empty tuple if the string is blank
    if not text or not text.strip():
        return tuple()

    # Python format
    val = None
    if delim == ',':
        try:
            val = tuple(ast.literal_eval(text))
        except (SyntaxError, ValueError, Warning):
            pass
    if isinstance(val, tuple):
        return val

    # Delimited string format
    return tuple([item.strip() for item in text.split(delim)])

def asset(text: str, delim: str = ',') -> set:
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
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argument 'delim'", delim, str)

    # Return empty set if the string is blank
    if not text or not text.strip():
        return set()

    # Python standard format
    val = None
    if delim == ',':
        try:
            val = set(ast.literal_eval(text))
        except (SyntaxError, ValueError, Warning):
            pass
    if isinstance(val, set):
        return val

    # Delimited string format
    return {item.strip() for item in text.split(delim)}

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
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argumnt 'delim'", delim, str)

    # Return empty dict if the string is blank
    if not text or not text.strip():
        return dict()

    Num = pp.Word(pp.nums + '.')
    Str = pp.quotedString
    Bool = pp.Or(pp.Word("True") | pp.Word("False"))
    Key = pp.Word(pp.alphas + "_", pp.alphanums + "_.")
    Val = pp.Or(Num | Str | Bool)

    # Try dictionary format "<key> = <value><delim> ..."
    Term = pp.Group(Key + '=' + Val)
    Terms = Term + pp.ZeroOrMore(delim + Term)
    try:
        l = Terms.parseString(text.strip('{}'))
    except pp.ParseException:
        l = None

    # Try dictionary format "'<key>': <value><delim> ..."
    if not l:
        Term = pp.Group(Str + ':' + Val)
        Terms = Term + pp.ZeroOrMore(delim + Term)
        try:
            l = Terms.parseString(text.strip('{}'))
        except pp.ParseException:
            return {}

    # Create dictionary from list
    d = {}
    for item in l:
        if len(item) == 1:
            if item[0] == ',':
                continue
            d[item] = True
            continue
        try:
            key, val = item[0].strip('\'\"'), ast.literal_eval(item[2])
        except (
            KeyError, NameError, TypeError, ValueError, SyntaxError,
            AttributeError):
            continue

        if isinstance(val, str):
            val = val.strip()
        d[key] = val

    return d

def aspath(text: str, expand: bool = True) -> Path:
    """Convert text into list.

    Args:
        text: String representing a path.
        unpack: Boolen value, whoch determines, if variables in the text
            of format '%VARIABLA%' are expanded.

    Returns:
        Value of the text as Path.

    """
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argument 'expand'", expand, bool)

    from nemoa.base import npath
    return npath.expand(text)
