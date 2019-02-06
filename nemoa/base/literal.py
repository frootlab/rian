# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""String conversion functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import ast
from datetime import datetime as Date
import string
from pathlib import Path
import pyparsing as pp
from nemoa.base import check, env, pkg
from nemoa.types import Any, OptStr, OptType

def encode(obj: object, **kwds: Any) -> str:
    """Encode object to literal text representation.

    Args:
        obj: Simple object

    Returns:
        Literal text representation of given object.

    """
    source = type(obj)
    fname = 'from_' + source.__name__.lower()
    if pkg.has_attr(fname):
        return pkg.call_attr(fname, obj, **kwds)
    return repr(obj)

def from_str(text: str, charset: OptStr = None, spacer: OptStr = None) -> str:
    """Filter text to given character set.

    Args:
        text:
        charset: Name of used character set. Supportet options are:

            :printable: Printable characters
            :UAX-31: ASCII identifier characters as defined in [UAX31]_

    Return:
        String, which is filtered to the chiven character set.

    """
    if charset:
        charset = charset.lower()
    if charset == 'printable':
        # TODO: if spacer is not None: test if spacer is printable
        # Get set of non-printable ASCII characters
        ascii_charset = set(chr(i) for i in range(128))
        ascii_non_printable = ascii_charset.difference(string.printable)

        # Replace non printable characters by spacer
        mapping = {ord(char): spacer for char in ascii_non_printable}
        return text.translate(mapping)
    if charset in ['uax31', 'uax-31', 'identifier']:
        # TODO: if spacer is not None: test if spacer is printable
        # # Interpret '-', '(', ')' and ' ' as '_'
        # text = text.strip(' ').translate(str.maketrans('- ', '__'))
        # Get set of non-identifier ASCII characters
        ascii_charset = set(chr(i) for i in range(128))
        ascii_id_charset = string.ascii_letters + string.digits + '_'
        ascii_nonid_charset = ascii_charset.difference(ascii_id_charset)

        # Replace non identifiable characters by spacer
        mapping = {ord(char): spacer for char in ascii_nonid_charset}
        return text.translate(mapping)
    return text

def decode(
        text: str, target: OptType = None, undef: OptStr = 'None',
        **kwds: Any) -> Any:
    """Decode text representation of object to object.

    Args:
        text: String representing the value of a given type in it's respective
            syntax format. The standard format corresponds to the standard
            Python representation if available. Some types also accept
            further formats, which may use additional keywords.
        target: Target type, in which the text is to be converted.
        undef: Optional string, which respresents an undefined value. If undef
            is a string, then the any text, the matches the string is decoded
            as None, independent from the given target type.
        **kwds: Supplementary parameters, that specify the encoding format of
            the target type.

    Returns:
        Value of the text in given target format or None.

    """
    # Check Arguments
    check.has_type("'text'", text, str)
    check.has_opt_type("'target'", target, type)

    # Check for undefined value
    if text == undef:
        return None

    # If no target type is given, estimate type
    target = target or estimate(text) or str

    # Elementary literals
    if target == str:
        return text.strip().replace('\n', '')
    if target == bool:
        return text.lower().strip() == 'true'
    if target in [int, float, complex]:
        return target(text, **kwds)

    fname = 'as_' + target.__name__.lower()
    return pkg.call_attr(fname, text, **kwds)

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
    check.has_type("'delim'", delim, str)

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
    check.has_type("'delim'", delim, str)

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
    check.has_type("'delim'", delim, str)

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
    check.has_type("'expand'", expand, bool)

    if expand:
        return env.expand(text)
    return Path(text)

def as_datetime(text: str, fmt: OptStr = None) -> Date:
    """Convert text to datetime.

    Args:
        text: String representation of datetime
        fmt: Optional string parameter, that specifies the format, which is
            used to decode the text to datetime. The default format is the [ISO
            8601]_ format, given by the string `%Y-%m-%d %H:%M:%S.%f`.


    Returns:
        Value of the text as datetime.

    """
    # Check types of Arguments
    check.has_type("first argument 'text'", text, str)

    # Convert text to datetime
    fmt = fmt or '%Y-%m-%d %H:%M:%S.%f'
    return Date.strptime(text, fmt)

def estimate(text: str) -> OptType:
    """Estimate type of text by using :func:`~ast.literal_eval`.

    Args:
        text: String representation of python object.

    Returns:
        Type of text or None, if the type could not be determined.

    """
    # Test if the given text is a literal
    try:
        return type(ast.literal_eval(text))
    except ValueError:
        pass
    except SyntaxError:
        pass

    # Test if the given text is a datetime in ISO 8601 format
    try:
        dtime = as_datetime(text)
        return Date
    except ValueError:
        pass

    return None
