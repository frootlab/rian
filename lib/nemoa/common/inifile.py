# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from configparser import ConfigParser
from typing import Optional

def dumps(d: dict, flat: bool = False) -> str:
    """Convert configuration dictionary to INI formated string.

    Args:
        d (dict): dictionary containing configuration

    Kwargs:
        flat (bool, optional): Determines if the desired INI format structure
            contains sections or not. By default sections are used.

    Return:
        String with INI File Structure

    """

    from io import StringIO

    # if no sections are to be used create a temporary [root] section
    if flat: d = {'root': d.copy()}

    # succesively pass (key, value) pairs to INI parser
    parser = ConfigParser()
    for sec in d.keys():
        if not isinstance(d[sec], dict): continue
        parser.add_section(str(sec))
        for key, val in d[sec].items():
            parser.set(str(sec), str(key), str(val))

    # retrieve INI formated string from INI parser
    with StringIO() as buffer:
        parser.write(buffer)
        s = buffer.getvalue()

    # if no section are to be used remove [root] section from string
    if flat: s = s.replace('[root]\n', '')

    return s

def load(f: str, structure: Optional[dict] = None) -> dict:
    """Import configuration dictionary from INI file.

    Args:
        f (str): full qualified path to INI File

    Kwargs:
        structure (dict, optional): Dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported. If "structure" however is a dictionary, only
            those sections, keys and values are imported, that match it.
            Thereby the sections and keys can be given as regular expressions,
            e.g. to allow equally structured sections, and the values determine
            validity by types in string format: 'str', 'int' etc.

    Return:
        Structured configuration dictionary

    """

    # get configuration from INI File
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(f)

    # parse sections and create configuration dictionary
    d = parse(parser, structure = structure)

    return d

def loads(s: str, structure: Optional[dict] = None,
    flat: bool = False) -> dict:
    """Import configuration dictionary from INI formated string

    Args:
        s (str): INI formated string, that contains the configuration

    Kwargs:
        structure (dict, optional): Dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported. If "structure" however is a dictionary, only
            those sections, keys and values are imported, that match it.
            Thereby the sections and keys can be given as regular expressions,
            e.g. to allow equally structured sections, and the values determine
            validity by types in string format: 'str', 'int' etc.
        flat (bool, optional): Determines if the desired INI format structure
            contains sections or not. By default sections are used.

    Return:
        Structured configuration dictionary

    """

    # if no sections are to be used create a temporary [root] section
    # and embed the structure dictionary within a 'root' key
    if flat:
        s = '[root]\n' + s
        if isinstance(structure, dict):
            structure = {'root': structure.copy()}

    # strip leading and trailing white spaces from lines in INI string
    s = '\n'.join([line.strip(' ') for line in s.split('\n')])

    # parse sections and create config dictionary
    parser = ConfigParser()
    parser.read_string(s)
    d = parse(parser, structure)

    # if no sections are to be used collapse the 'root' key
    if flat: d = d.get('root')

    return d

def parse(parser: ConfigParser, structure: Optional[dict] = None) -> dict:
    """Import configuration dictionary from INI formated string

    Args:
        parser (ConfigParser): ConfigParser instance that contains an
            unstructured / unfiltered configuration dictionary

    Kwargs:
        structure (dict, optional): Dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported. If "structure" however is a dictionary, only
            those sections, keys and values are imported, that match it.
            Thereby the sections and keys can be given as regular expressions,
            e.g. to allow equally structured sections, and the values determine
            validity by types in string format: 'str', 'int' etc.

    Return:
        Structured configuration dictionary

    """

    from re import compile
    from nemoa.common import text

    # if no structure is given retrieve dictionary from INI parser
    if not isinstance(structure, dict):
        d = {}
        for sec in parser.sections():
            d[sec] = {key: parser.get(sec, key) for key in parser.options(sec)}
        return d

    # if structure is given use regular expression to match sections and keys
    d = {}
    rsecs = {key: compile('\A' + key) for key in structure.keys()}
    for sec in parser.sections():

        # use regular expression to match sections
        rsec = None
        for key in structure.keys():
            match = rsecs[key].match(sec)
            if not match: continue
            rsec = key
            break
        if not rsec: continue
        ssec = match.group()

        # use regular expression to match keys
        dsec = {}
        for regex_key, fmt in structure[rsec].items():
            re_key = compile(regex_key)
            for key in parser.options(sec):
                if not re_key.match(key): continue
                val = parser.get(sec, key)
                dsec[key] = text.astype(val, fmt)

        d[sec] = dsec

    return d
