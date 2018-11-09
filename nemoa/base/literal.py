# -*- coding: utf-8 -*-
"""String conversion functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import ast
import datetime
import sys
from pathlib import Path

try:
    import pyparsing as pp
except ImportError as err:
    raise ImportError(
        "requires package pyparsing: "
        "https://pypi.org/project/pyparsing/") from err

from nemoa.base import check, npath
from nemoa.types import Any, OptStr, Date, OptType

def decode(
        text: str, cls: OptType = None, undef: str = 'None',
        **kwds: Any) -> Any:
    """Convert text into given target format.

    Args:
        text: String representing the value of a given type in it's respective
            syntax format. The standard format corresponds to the standard
            Python representation if available. Some types also accept
            further formats, which may use additional keywords.
        cls: Target type in which the text is to be converted.
        undef: String, which respresents an undefined value. If the given text
            matches the string, None is returned.
        **kwds: Supplementary parameters, that specify the target format

    Returns:
        Value of the text in given target format or None.

    """
    # Check Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_opt_type("argument 'cls'", cls, type)

    if text == undef:
        return None

    # Evaluate text as Python literal if no type is given
    if cls is None:
        return ast.literal_eval(text)

    # Basic types
    if cls == str:
        return text.strip().replace('\n', '')
    if cls == bool:
        return text.lower().strip() == 'true'
    if cls in [int, float, complex]:
        return cls(text)

    # Sequence and special types
    fname = 'as_' + cls.__name__.lower()
    try:
        return getattr(sys.modules[__name__], fname)(text, **kwds)
    except AttributeError as err:
        raise ValueError(f"type '{cls}' is not supported") from err

def as_list(text: str, delim: str = ',') -> list:
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

    # Return empty list if the string is blank
    if not text or not text.strip():
        return list()

    # Python format
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

def as_tuple(text: str, delim: str = ',') -> tuple:
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

def as_set(text: str, delim: str = ',') -> set:
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

def as_dict(text: str, delim: str = ',') -> dict:
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

def as_path(text: str, expand: bool = True) -> Path:
    """Convert text into list.

    Args:
        text: String representing a path.
        expand: Boolen value, whoch determines, if variables in environmental
            path variables are expanded.

    Returns:
        Value of the text as Path.

    """
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    check.has_type("argument 'expand'", expand, bool)

    if expand:
        return npath.expand(text)
    return Path(text)

def as_datetime(text: str, fmt: OptStr = None) -> Date:
    """Convert text into list.

    Args:
        text: String representing datetime.
        fmt:

    Returns:
        Value of the text as datetime.

    """
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.datetime.strptime(text, fmt)
