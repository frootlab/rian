# -*- coding: utf-8 -*-
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
from nemoa.file import textfile
from nemoa.types import FileOrPathLike, OptBool, OptStr, StrDict
from nemoa.types import Union, Optional, OptType, Dict

#
# Structural Types
#

FlatDict = Dict[str, OptType]
SecDict = Dict[str, FlatDict]
OptSecDict = Optional[SecDict]
StrucDict = Union[FlatDict, SecDict]
OptStrucDict = Optional[StrucDict]
ConfigDict = Dict[str, StrDict]

#
# Functions
#

def load(
        file: FileOrPathLike, structure: OptStrucDict = None,
        flat: OptBool = None) -> StrucDict:
    """Import configuration dictionary from INI file.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in read mode.
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the INI-file is
            completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            `literal.decode`_.
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the first non empty, non
            comment line in the string identifies a section.

    Return:
        Structured configuration dictionary

    """
    # Read configuration from file-like or path-like object
    with textfile.openx(file, mode='r') as fh:
        return decode(fh.read(), structure=structure, flat=flat)

def decode(
        text: str, structure: OptStrucDict = None,
        flat: OptBool = None) -> StrucDict:
    """Load configuration dictionary from INI-formated text.

    Args:
        text: Text, that describes a configuration in INI-format.
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the INI-file
            is completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            :func:`~nemoa.base.literal.decode`.
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the first non empty, non
            comment line in the string identifies a section.

    Return:
        Structured configuration dictionary.

    """
    # Check arguments
    check.has_type("first argument", text, str)

    # If the usage of sections is not defined by the argument 'flat' their
    # existence is determined from the given file structure. If the file
    # structure also is not given, it is determined by the first not blank and
    # non comment line in the text. If this line does not start with the
    # character '[', then the file structure is considered to be flat.
    if flat is None:
        if isinstance(structure, dict):
            flat = not any(isinstance(val, dict) for val in structure.values())
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
    # structure dictionary is embedded within the 'root' key of a wrapping
    # dictionary.
    if flat:
        text = '\n'.join(['[root]', text])
        if isinstance(structure, dict):
            structure = cast(SecDict, {'root': structure})

    # Parse inifile without literal decoding
    parser = ConfigParser()
    setattr(parser, 'optionxform', lambda key: key)
    parser.read_string(text)

    # Decode literals by using the structure dictionary
    config = parse(parser, structure=cast(SecDict, structure))

    # If structure is flat collapse the 'root' key
    return config.get('root') or {} if flat else config

def save(
        config: dict, file: FileOrPathLike, flat: OptBool = None,
        comment: OptStr = None) -> None:
    """Save configuration dictionary to INI-file.

    Args:
        config: Configuration dictionary
        file: String or :term:`path-like object` that represents to a writeable
            file in the directory structure of the system, or a :term:`file
            object` in write mode.
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
    with textfile.openx(file, mode='w') as fh:
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

def get_comment(file: FileOrPathLike) -> str:
    """Read initial comment lines from INI-file.

    Args:
        file: String or :term:`path-like object` that points to a readable file
            in the directory structure of the system, or a :term:`file object`
            in reading mode.

    Returns:
        String containing the initial comment lines of the INI-file or an empty
        string, if no initial comment lines could be detected.

    """
    return textfile.get_comment(file)

def parse(parser: ConfigParser, structure: OptSecDict = None) -> ConfigDict:
    """Import configuration dictionary from INI formated text.

    Args:
        parser: ConfigParser instance that contains an unstructured
            configuration dictionary
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the INI-file
            is completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid parameter names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries define the type of the
            parameters by their own type, e.g. str, int, float etc. Accepted
            types can be found in the documentation of the function
            :func:`~nemoa.base.literal.decode`.

    Return:
        Structured configuration dictionary.

    """
    # Retrieve dictionary from INI parser, if no structure is given
    if not isinstance(structure, dict):
        config = {}
        for sec in parser.sections():
            config[sec] = {
                key: parser.get(sec, key) for key in parser.options(sec)}
        return config

    # Use regular expression to match sections and keys, if a structure is given
    config = {}
    rsecs = {key: re.compile(r'\A' + str(key)) for key in structure.keys()}
    for sec in parser.sections():

        # Use regular expression to match sections
        rsec = None
        for key in structure.keys():
            if not rsecs[key].match(sec):
                continue
            rsec = key
            break
        if not rsec:
            continue

        # Use regular expression to match keys
        dsec = {}
        for regexkey, cls in getattr(structure[rsec], 'items')():
            rekey = re.compile(regexkey)
            for key in parser.options(sec):
                if not rekey.match(key):
                    continue
                string = parser.get(sec, key)
                dsec[key] = literal.decode(string, cls)

        config[sec] = dsec

    return config
