# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import ConfigParser
import io
import nemoa
import os
import re

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

    config_handler = ConfigParser.ConfigParser()
    config_handler.optionxform = str
    config_handler.readfp(io.BytesIO(config_string))

    # parse sections and create dictionaries
    config = {}
    if isinstance(structure, dict):
        re_section = re.compile('\A' + '|'.join(structure.keys()))
    for section in config_handler.sections():

        if isinstance(structure, dict):
            # use regular expression to match sections in structure
            re_match = re_section.match(section)
            if not re_match: continue
            struc_sec = re_match.group()
            if not struc_sec in structure.keys(): continue
            section_config = {}
            for (reg_ex_key, fmt) in structure[struc_sec].items():
                re_key = re.compile(reg_ex_key)
                for key in config_handler.options(section):
                    if not re_key.match(key): continue
                    val = config_handler.get(section, key)
                    section_config[key] = \
                        nemoa.common.str_to_type(val, fmt)
        else:
            section_config = {}
            for key in config_handler.options(section):
                section_config[key] = config_handler.get(section, key)

        config[section] = section_config

    if nosection: return config['root']
    return config
