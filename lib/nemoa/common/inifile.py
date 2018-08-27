# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from configparser import ConfigParser
from typing import Optional

def dumps(d: dict, flat: Optional[bool] = None,
    header: Optional[str] = None) -> str:
    """Convert configuration dictionary to INI formated string.

    Args:
        d (dict): dictionary containing configuration

    Kwargs:
        flat (bool, optional): Determines if the desired INI format structure
            contains sections or not. By default sections are used, if the
            dictionary contains subdictionaries.
        header (str, optional): The Header string is written in the INI format
            string as an initial comment. By default no header is written.

    Return:
        String with INI File Structure

    """

    from io import StringIO

    # if the usage of sections is not explicitely given, use sections if
    # the dictionary contains subdictionaries
    if flat == None:
        flat = True
        for key, val in d.items():
            if not type(val) is dict: continue
            flat = False

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

    # if header is given, write header as comment before string
    if isinstance(header, str):
        s = '\n'.join(['# ' + l for l in header.split('\n')]) + '\n\n' + s

    return s

def load(f: str, structure: Optional[dict] = None) -> dict:
    """Import configuration dictionary from INI file.

    Args:
        f (str): full qualified path to INI File

    Kwargs:
        structure (dict, optional): Dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.

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
    flat: Optional[bool] = None) -> dict:
    """Import configuration dictionary from INI formated string

    Args:
        s (str): INI formated string, that contains the configuration

    Kwargs:
        structure (dict, optional): Dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.
        flat (bool, optional): Determines if the desired INI format structure
            contains sections or not. By default sections are used, if the
            first non empty, non comment line in the string identifies a
            section.

    Return:
        Structured configuration dictionary

    """

    # if the usage of sections is not explicitely given, search for sections
    # in the given string
    if flat == None:
        flat = True
        for line in [l.lstrip(' ') for l in s.split('\n')]:
            if len(line) == 0 or line.startswith('#'): continue
            flat = not line.startswith('[')
            break

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
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.

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
            if not rsecs[key].match(sec): continue
            rsec = key
            break
        if not rsec: continue

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
