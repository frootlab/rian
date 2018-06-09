# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import configparser
import io
import nemoa
import os
import re

def dumps(dictionary, nosection = True):

    if nosection:
        dictionary = dictionary.copy()
        dictionary = {'root': dictionary}

    parser = configparser.ConfigParser()
    for section in dictionary:
        if not isinstance(dictionary[section], dict): continue
        parser.add_section(section)
        for key, val in list(dictionary[section].items()):
            parser.set(section, key, val)

    with io.BytesIO() as strbuffer:
        parser.write(strbuffer)
        string = strbuffer.getvalue()

    if nosection:
        string = string.replace('[root]\n', '')

    return string

def load(path, structure = None):

    # get config file parser
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(path)

    # parse sections and create config dictionary
    return parse(parser, structure)

def loads(string, structure = None, nosection = False):

    # format string
    lines = string.split('\n')
    for lid, line in enumerate(lines):
        lines[lid] = line.strip(' ')
    if nosection:
        configstr = '[root]\n' + '\n'.join(lines)
        if isinstance(structure, dict):
            structure = structure.copy()
            structure = {'root': structure}
    else:
        configstr = '\n'.join(lines)

    # get config parser
    parser = configparser.ConfigParser()
    parser.read_string(configstr)

    # parse sections and create config dictionary
    config = parse(parser, structure)

    if nosection: return config['root']
    return config

def parse(parser, structure = None):

    # parse sections and create config dictionary
    config = {}

    if not isinstance(structure, dict):
        for section in parser.sections():
            config[section] = {}
            for key in parser.options(section):
                config[section][key] = parser.get(section, key)

        return config

    regex_section = {}
    for key in list(structure.keys()):
        regex_section[key] = re.compile('\A' + key)

    for section in parser.sections():

        # use regular expression to match sections
        section_regex = None
        for key in list(structure.keys()):
            regex_match = regex_section[key].match(section)
            if not regex_match: continue
            section_regex = key
            break
        if not section_regex: continue
        section_name = regex_match.group()
        section_dict = {}

        # use regular expression to match keys
        for regex_key, fmt in structure[section_regex].items():
            re_key = re.compile(regex_key)
            for key in parser.options(section):
                if not re_key.match(key): continue
                val = parser.get(section, key)
                section_dict[key] = \
                    nemoa.common.text.astype(val, fmt)

        config[section] = section_dict

    return config
