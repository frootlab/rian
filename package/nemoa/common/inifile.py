# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import ConfigParser
import io
import nemoa
import os
import re

def ini_dumps(dictionary, nosection = True):

    if nosection:
        dictionary = dictionary.copy()
        dictionary = {'root': dictionary}

    parser = ConfigParser.ConfigParser()
    for section in dictionary:
        if not isinstance(dictionary[section], dict): continue
        parser.add_section(section)
        for key, val in dictionary[section].items():
            parser.set(section, key, val)

    with io.BytesIO() as strbuffer:
        parser.write(strbuffer)
        string = strbuffer.getvalue()

    if nosection:
        string = string.replace('[root]\n', '')

    return string

def ini_load(path, structure = None):

    # get config file parser
    parser = ConfigParser.ConfigParser()
    parser.optionxform = str
    parser.read(path)

    # parse sections and create config dictionary
    if isinstance(structure, dict):
        return ini_parse_regex(parser, structure)
    return ini_parse(parser)

def ini_loads(string, structure = None, nosection = False):

    # prepare config string
    config_list = string.split('\n')
    for line_id, line in enumerate(config_list):
        config_list[line_id] = line.strip(' ')
    if nosection:
        config_string = '[root]\n' + '\n'.join(config_list)
        if isinstance(structure, dict):
            structure = structure.copy()
            structure = {'root': structure}
    else:
        config_string = '\n'.join(config_list)

    # get config file parser
    parser = ConfigParser.ConfigParser()
    parser.optionxform = str
    parser.readfp(io.BytesIO(config_string))

    # parse sections and create config dictionary
    if isinstance(structure, dict):
        config = ini_parse_regex(parser, structure)
    else:
        config = ini_parse(parser)

    if nosection: return config['root']
    return config

def ini_parse_regex(parser, structure):

    # parse sections and create config dictionary
    config = {}
    regex_section = {}
    for key in structure.keys():
        regex_section[key] = re.compile('\A' + key)

    for section in parser.sections():

        # use regular expression to match sections
        section_regex = None
        for key in structure.keys():
            regex_match = regex_section[key].match(section)
            if not regex_match: continue
            section_regex = key
            break
        if not section_regex: continue
        section_name = regex_match.group()
        section_dict = {}

        # use regular expression to match keys
        for regex_key, fmt in structure[section_regex].iteritems():
            re_key = re.compile(regex_key)
            for key in parser.options(section):
                if not re_key.match(key): continue
                val = parser.get(section, key)
                section_dict[key] = \
                    nemoa.common.str_to_type(val, fmt)

        config[section] = section_dict

    return config

def ini_parse(parser):

    config = {}
    for section in parser.sections():
        config[section] = {}
        for key in parser.options(section):
            config[section][key] = parser.get(section, key)

    return config
