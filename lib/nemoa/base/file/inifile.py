# -*- coding: utf-8 -*-
"""I/O functions for INI-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _ntext.astype:
    https://frootlab.github.io/nemoa-doc/latest/source/nemoa.base.ntext.html#nemoa.base.ntext.astype
"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
from io import StringIO
import re
from nemoa.base import literal
from nemoa.base.file import textfile
from nemoa.types import FileOrPathLike, OptBool, OptStr, OptStrDict2, StrDict2
from nemoa.types import Union, StrDict, Optional

StrucType = Union[StrDict, StrDict2]
OptStrucType = Optional[StrucType]

def load(
        file: FileOrPathLike, structure: OptStrucType = None,
        flat: OptBool = None) -> StrucType:
    """Import configuration dictionary from INI file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            read mode.
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the the INI-file
            is completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid attribute names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries describe the type of the
            attributes by strings representing the name of the type, e.g. 'str',
            'int', 'float', 'path' etc. Accepted type names can be found in the
            documentation of the function `ntext.astype`_.
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
        text: str, structure: OptStrucType = None,
        flat: OptBool = None) -> StrucType:
    """Load configuration dictionary from INI-formated text.

    Args:
        text: Text, that describes a configuration in INI-format.
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the the INI-file
            is completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid attribute names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries describe the type of the
            attributes by strings representing the name of the type, e.g. 'str',
            'int', 'float', 'path' etc. Accepted type names can be found in the
            documentation of the function `ntext.astype`_.
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the first non empty, non
            comment line in the string identifies a section.

    Return:
        Structured configuration dictionary.

    """
    # If the usage of sections is not defined by the argument 'flat' their
    # existence is determined by the first not blank and comment line. If this
    # line does not start with the character '[', then the file structure is
    # considered to be flat.
    if flat is None:
        flat = True
        with StringIO(text) as fh:
            line = ''
            for line in fh:
                content = line.strip()
                if content and not content.startswith('#'):
                    break
            flat = not line.lstrip().startswith('[')

    # For flat structured files a a temporary [root] section is created and the
    # structure dictionary is embedded within the 'root' key of a wrapping
    # dictionary.
    if flat:
        text = '\n'.join(['[root]', text])
        if isinstance(structure, dict):
            structure = {'root': structure}

    # Parse inifile without literal decoding
    parser = ConfigParser()
    setattr(parser, 'optionxform', lambda key: key)
    parser.read_string(text)

    # Decode literals by using the structure dictionary
    config = parse(parser, structure=structure)

    # If structure is flat collapse the 'root' key
    return config.get('root') or {} if flat else config

def save(
        config: dict, file: FileOrPathLike, flat: OptBool = None,
        comment: OptStr = None) -> None:
    """Save configuration dictionary to INI-file.

    Args:
        config: Configuration dictionary
        file: String or `path-like object`_ that represents to a writeable file
            in the directory structure of the system, or a `file-like object`_
            in write mode.
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
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        String containing the initial comment lines of the INI-file or an empty
        string, if no initial comment lines could be detected.

    """
    return textfile.get_comment(file)

def parse(parser: ConfigParser, structure: OptStrDict2 = None) -> StrDict2:
    """Import configuration dictionary from INI formated text.

    Args:
        parser: ConfigParser instance that contains an unstructured
            configuration dictionary
        structure: Dictionary of dictionaries, which determines the structure of
            the configuration dictionary. If structure is None, the the INI-file
            is completely imported and all values are interpreted as strings. If
            the structure is a dictionary of dictionaries, the keys of the outer
            dictionary describe valid section names by strings, that are
            interpreted as regular expressions. Therupon, the keys of the
            respective inner dictionaries describe valid attribute names as
            strings, that are also interpreted as regular expressions. Finally
            the values of the inner dictionaries describe the type of the
            attributes by strings representing the name of the type, e.g. 'str',
            'int', 'float', 'path' etc. Accepted type names can be found in the
            documentation of the function `ntext.astype`_.

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
        for regexkey, fmt in getattr(structure[rsec], 'items')():
            rekey = re.compile(regexkey)
            for key in parser.options(sec):
                if not rekey.match(key):
                    continue
                string = parser.get(sec, key)
                dsec[key] = literal.decode(string, fmt)

        config[sec] = dsec

    return config
