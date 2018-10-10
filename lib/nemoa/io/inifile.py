# -*- coding: utf-8 -*-
"""I/O functions for INI-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _ntext.astype:
    https://frootlab.github.io/nemoa-doc/latest/source/nemoa.common.ntext.html#nemoa.common.ntext.astype
"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
from io import StringIO

from nemoa.io import textfile
from nemoa.types import FileOrPathLike, OptBool, OptStr, OptStrDict2, StrDict2

FILEEXTS = ['.ini', '.cfg']

def load(file: FileOrPathLike, structure: OptStrDict2 = None) -> StrDict2:
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

    Return:
        Structured configuration dictionary

    """
    # Initialize Configuration Parser
    parser = ConfigParser()
    setattr(parser, 'optionxform', lambda key: key)

    # Read configuration from file-like or path-like object
    with textfile.open_read(file) as fd:
        parser.read_file(fd)

    # Parse sections and create configuration dictionary
    return parse(parser, structure=structure)

def save(
        config: dict, file: FileOrPathLike, flat: OptBool = None,
        header: OptStr = None) -> None:
    """Save configuration dictionary to INI-file.

    Args:
        config: Configuration dictionary
        file: String or `path-like object`_ that represents to a writeable file
            in the directory structure of the system, or a `file-like object`_
            in write mode.
        flat: Determines if the desired INI format structure contains sections.
            By default sections are used, if the dictionary contains
            subdictionaries.
        header: The Header string is written in the INI-file as initial comment.
            By default no header is written.

    """
    # Convert configuration dictionary to INI formated text
    try:
        text = dumps(config, flat=flat, header=header)
    except Exception as err:
        raise ValueError("dictionary is not valid") from err

    # Write text to file
    with textfile.open_write(file) as fd:
        fd.write(text)

def loads(
        text: str, structure: OptStrDict2 = None,
        flat: OptBool = None) -> StrDict2:
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
        flat: Determines if the desired INI format structure
            contains sections or not. By default sections are used, if the
            first non empty, non comment line in the string identifies a
            section.

    Return:
        Structured configuration dictionary.

    """
    # If the usage of sections is not defined by the argument 'flat' their
    # existence is determined by the appearance of a line, that starts with the
    # character '['.
    if flat is None:
        flat = True
        for line in [l.lstrip(' ') for l in text.split('\n')]:
            if not line or line.startswith('#'):
                continue
            flat = not line.startswith('[')
            break

    # If no sections are to be used, a temporary [root] section is created and
    # the structure dictionary is embedded within a further dicvtionary with a
    # 'root' key.
    if flat:
        text = '\n'.join(['[root]', text])
        if isinstance(structure, dict):
            structure = {'root': structure.copy()}

    # Strip leading and trailing white spaces from lines in INI formated text
    text = '\n'.join([line.strip(' ') for line in text.split('\n')])

    # Parse sections and create dictionary
    parser = ConfigParser()
    parser.read_string(text)
    config = parse(parser, structure)

    # If no sections are to be used collapse the 'root' key
    if flat:
        return config.get('root') or {}

    return config

def dumps(config: dict, flat: OptBool = None, header: OptStr = None) -> str:
    """Convert configuration dictionary to INI formated string.

    Args:
        config: Configuration dictionary
        flat: Determines if the desired INI format structure contains sections
            or not. By default sections are used, if the dictionary contains
            subdictionaries.
        header: The Header string is written in the INI format string as an
            initial comment. By default no header is written.

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

    # if no sections are to be used create a temporary [root] section
    if flat:
        config = {'root': config.copy()}

    # succesively pass (key, value) pairs to INI parser
    parser = ConfigParser()
    for sec in config.keys():
        if not isinstance(config[sec], dict):
            continue
        parser.add_section(str(sec))
        for key, val in config[sec].items():
            parser.set(str(sec), str(key), str(val))

    # retrieve INI formated text from INI parser
    with StringIO() as buffer:
        parser.write(buffer)
        text = buffer.getvalue()

    # if no section are to be used remove [root] section from text
    if flat:
        text = text.replace('[root]\n', '')

    # if header is given, write header as comments before text
    if isinstance(header, str):
        comments = ['# ' + line.strip() for line in header.splitlines()]
        text = '\n'.join(comments) + '\n\n' + text

    return text

def get_header(file: FileOrPathLike) -> str:
    """Read header from INI-file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            read mode.

    Returns:
        String containing the header of the INI-file or an empty string, if no
        header could be detected.

    """
    with textfile.open_read(file) as fd:
        return textfile.read_header(fd)

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
    import re
    from nemoa.common import ntext

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
                val = parser.get(sec, key)
                dsec[key] = ntext.astype(val, fmt)

        config[sec] = dsec

    return config
