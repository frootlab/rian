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
"""INI-file I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
from io import StringIO
import re
from typing import cast
from nemoa.base import literal, check
from nemoa.io import plain
from nemoa.types import OptBool, OptStr, StrDict
from nemoa.types import Union, Optional, OptType, Dict, FileRef

#
# Structural Types
#

FlatDict = Dict[str, OptType]
SecDict = Dict[str, FlatDict]
OptSecDict = Optional[SecDict]
Scheme = Union[FlatDict, SecDict]
OptScheme = Optional[Scheme]
ConfigDict = Dict[str, StrDict]

#
# Functions
#

def load(
        file: FileRef, scheme: OptScheme = None, autocast: bool = False,
        flat: OptBool = None) -> Scheme:
    """Import configuration dictionary from INI file.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            mode.
        scheme: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If scheme is None, the INI-file is
            completely imported and all values are interpreted as strings. If
            the scheme is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            :func:`literal.decode <nemoa.base.literal.decode>`.
        autocast: If no scheme is given autocast determines, if the values are
            automatically converted to types, estimated by the function
            :func:`literal.estimate <nemoa.base.literal.estimate>`
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the first non empty, non
            comment line in the string identifies a section.

    Return:
        Structured configuration dictionary

    """
    # Read configuration from file-like or path-like object
    with plain.openx(file, mode='r') as fh:
        return decode(fh.read(), scheme=scheme, autocast=autocast, flat=flat)

def decode(
        text: str, scheme: OptScheme = None, autocast: bool = False,
        flat: OptBool = None) -> Scheme:
    """Load configuration dictionary from INI-formated text.

    Args:
        text: Text, that describes a configuration in INI-format.
        scheme: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If scheme is None, the INI-file
            is completely imported and all values are interpreted as strings. If
            the scheme is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            :func:`literal.decode <nemoa.base.literal.decode>`.
        autocast: If no scheme is given autocast determines, if the values are
            automatically converted to types, estimated by the function
            :func:`literal.estimate <nemoa.base.literal.estimate>`
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the first non blank, non
            comment line in the string identifies a section.

    Return:
        Structured configuration dictionary.

    """
    # Check arguments
    check.has_type("first argument", text, str)

    # If the usage of sections is not defined by the argument 'flat' their
    # existence is determined from the given file scheme. If the file
    # scheme also is not given, it is determined by the first not blank and
    # non comment line in the text. If this line does not start with the
    # character '[', then the file scheme is considered to be flat.
    if flat is None:
        if isinstance(scheme, dict):
            flat = not any(isinstance(val, dict) for val in scheme.values())
        else:
            flat = True
            with StringIO(text) as fh:
                line = ''
                for line in fh:
                    content = line.strip()
                    if content and not content.startswith('#'):
                        break
                flat = not line.lstrip().startswith('[')

    # For flat structured files a temporary [root] section is created and the
    # scheme dictionary is embedded within the 'root' key of a wrapping
    # dictionary.
    if flat:
        text = '\n'.join(['[root]', text])
        if isinstance(scheme, dict):
            scheme = cast(SecDict, {'root': scheme})

    # Parse ini without literal decoding
    parser = ConfigParser()
    setattr(parser, 'optionxform', lambda key: key)
    parser.read_string(text)

    # Decode literals by using the scheme dictionary
    config = parse(parser, scheme=cast(SecDict, scheme), autocast=autocast)

    # If scheme is flat collapse the 'root' key
    return config.get('root') or {} if flat else config

def save(
        config: dict, file: FileRef, flat: OptBool = None,
        comment: OptStr = None) -> None:
    """Save configuration dictionary to INI-file.

    Args:
        config: Configuration dictionary
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in writing
            mode.
        flat: Determines if the desired INI format structure contains sections.
            By default sections are used, if the dictionary contains
            subdictionaries.
        comment: String containing comment lines, which are stored as initial
            '#' lines in the INI-file. By default no comment is written.

    """
    # Convert configuration dictionary to INI formated text
    try:
        text = encode(config, flat=flat, comment=comment)
    except Exception as err:
        raise ValueError("dictionary is not valid") from err

    # Write text to file
    with plain.openx(file, mode='w') as fh:
        fh.write(text)

def encode(config: dict, flat: OptBool = None, comment: OptStr = None) -> str:
    """Convert configuration dictionary to INI formated string.

    Args:
        config: Configuration dictionary
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the dictionary contains
            subdictionaries.
        comment: String containing comment lines, which are stored as initial
            '#' lines in the INI-file. By default no comment is written.

    Returns:
        Text with INI-file structure.

    """
    # If the usage of sections is not explicitely given, use sections if
    # the dictionary contains subdictionaries
    if flat is None:
        flat = True
        for key, val in config.items():
            if not isinstance(val, dict):
                continue
            flat = False

    # If no sections are to be used create a temporary [root] section
    if flat:
        config = {'root': config.copy()}

    # Succesively pass (key, value) pairs to INI parser
    parser = ConfigParser()
    for sec in config.keys():
        if not isinstance(config[sec], dict):
            continue
        parser.add_section(str(sec))
        for key, val in config[sec].items():
            parser.set(str(sec), str(key), str(val))

    # Retrieve INI formated text from INI parser
    with StringIO() as buffer:
        parser.write(buffer)
        text = buffer.getvalue()

    # If no section are to be used remove [root] section from text
    if flat:
        text = text.replace('[root]\n', '')

    # If a comment is given, write initial '# ' lines
    if isinstance(comment, str):
        comments = ['# ' + line.strip() for line in comment.splitlines()]
        text = '\n'.join(comments) + '\n\n' + text

    return text

def get_comment(file: FileRef) -> str:
    """Read initial comment lines from INI-file.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.base.abc.FileAccessor>` or an opened file object in reading
            or writing mode.

    Returns:
        String containing the initial comment lines of the INI-file or an empty
        string, if no initial comment lines could be detected.

    """
    return plain.get_comment(file)

def parse(
        parser: ConfigParser, scheme: OptSecDict = None,
        autocast: bool = False) -> ConfigDict:
    """Import configuration dictionary from INI formated text.

    Args:
        parser: ConfigParser instance that contains an unstructured
            configuration dictionary
        scheme: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If scheme is None, the INI-file
            is completely imported and all values are interpreted as strings. If
            the scheme is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            :func:`literal.decode <nemoa.base.literal.decode>`.
        autocast: If no scheme is given autocast determines, if the values are
            automatically converted to types, estimated by the function
            :func:`literal.estimate <nemoa.base.literal.estimate>`

    Return:
        Structured configuration dictionary.

    """
    # Retrieve dictionary from INI parser, if no scheme is given
    if not isinstance(scheme, dict):
        config = {} # type: ignore
        for sec in parser.sections():
            config[sec] = {}
            for key in parser.options(sec):
                val = parser.get(sec, key)
                if autocast:
                    config[sec][key] = literal.decode(val)
                else:
                    config[sec][key] = val
        return config

    # Use regular expression to match sections and keys, if a scheme is given
    config = {}
    rsecs = {key: re.compile(r'\A' + str(key)) for key in scheme.keys()}
    for sec in parser.sections():

        # Use regular expression to match sections
        rsec = None
        for key in scheme.keys():
            if not rsecs[key].match(sec):
                continue
            rsec = key
            break
        if not rsec:
            continue

        # Use regular expression to match keys
        dsec = {}
        for regexkey, tgttype in getattr(scheme[rsec], 'items')():
            rekey = re.compile(regexkey)
            for key in parser.options(sec):
                if not rekey.match(key):
                    continue
                string = parser.get(sec, key)
                dsec[key] = literal.decode(string, tgttype)

        config[sec] = dsec

    return config
