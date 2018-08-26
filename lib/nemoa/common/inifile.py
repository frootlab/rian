# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from configparser import ConfigParser
from typing import Optional

def dumps(d: dict, nosection: bool = True) -> str:

    from io import BytesIO

    if nosection: d = {'root': d.copy()}

    parser = ConfigParser()
    for sec in d:
        if not isinstance(d[sec], dict): continue
        parser.add_section(sec)
        for key, val in list(d[sec].items()):
            parser.set(sec, key, val)

    with BytesIO() as strbuffer:
        parser.write(strbuffer)
        s = strbuffer.getvalue()

    if nosection: s = s.replace('[root]\n', '')

    return s

def load(f: str, structure: Optional[dict] = None) -> dict:

    # get config file parser
    parser = ConfigParser()
    parser.optionxform = str
    parser.read(f)

    # parse sections and create config dictionary
    return parse(parser, structure = structure)

def loads(s: str, structure: Optional[dict] = None,
    nosection: bool = False) -> dict:

    # format string
    lines = s.split('\n')
    for lid, line in enumerate(lines):
        lines[lid] = line.strip(' ')
    if nosection:
        configstr = '[root]\n' + '\n'.join(lines)
        if isinstance(structure, dict):
            structure = structure.copy()
            structure = {'root': structure}
    else: configstr = '\n'.join(lines)

    # get config parser
    parser = ConfigParser()
    parser.read_string(configstr)

    # parse sections and create config dictionary
    d = parse(parser, structure)

    if nosection: return d['root']
    return d

def parse(parser: ConfigParser, structure: Optional[dict] = None) -> dict:

    from re import compile
    from nemoa.common.text import astype

    # parse sections and create config dictionary
    d = {}

    if not isinstance(structure, dict):
        for sec in parser.sections():
            d[sec] = {}
            for key in parser.options(sec):
                d[sec][key] = parser.get(sec, key)

        return d

    regex_sec = {}
    for key in list(structure.keys()):
        regex_sec[key] = compile('\A' + key)

    for sec in parser.sections():

        # use regular expression to match sections
        sec_regex = None
        for key in list(structure.keys()):
            regex_match = regex_sec[key].match(sec)
            if not regex_match: continue
            sec_regex = key
            break
        if not sec_regex: continue
        sec_name = regex_match.group()
        sec_dict = {}

        # use regular expression to match keys
        for regex_key, fmt in structure[sec_regex].items():
            re_key = compile(regex_key)
            for key in parser.options(sec):
                if not re_key.match(key): continue
                val = parser.get(sec, key)
                sec_dict[key] = astype(val, fmt)

        d[sec] = sec_dict

    return d
