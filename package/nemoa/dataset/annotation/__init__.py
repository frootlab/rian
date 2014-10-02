# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import importlib

def convert(list, input, output = None, filter = False):

    generic_types = ['number', 'string', 'float']

    if isinstance(list, (numpy.ndarray)):
        list = list.tolist()
        inputDtype = 'nparray'
    else: inputDtype = 'list'

    # 'input'
    if input in generic_types:
        input_class  = 'generic'
        input_format = input
    elif ':' in input:
        input_class  = input.lower().split(':')[0].strip()
        input_format = input.lower().split(':')[1].strip()
    else: return nemoa.log('warning',
        'could not convert list: unknown input format "' + input + '"!')

    # 'output'
    if output in generic_types:
        output_class  = 'generic'
        output_format = output
    elif output == None:
        output_class  = input_class
        output_format = None
    elif ':' in input:
        output_class  = output.lower().split(':')[0].strip()
        output_format = output.lower().split(':')[1].strip()
    else: return nemoa.log('warning',
        'could not convert list: unknown output format "' + output + '"!')

    # 'input' vs 'output'
    if input_class != output_class:
        return nemoa.log('warning', "'%s' can not be converted to '%s'"
            % (input_class, output_class))

    # trivial cases
    if input_class == 'generic' or input_format == output_format:
        if inputDtype == 'nparray':
            return numpy.asarray(list), numpy.asarray([])
        else: return list, []

    # import annotation module
    module_name = input_class.lower()
    module = importlib.import_module('nemoa.dataset.annotation.' + module_name)
    converter = getattr(module, module_name)()
    output_list, output_lost = converter.convert_list(
        list, input_format, output_format, filter)
    if inputDtype == 'nparray':
        return numpy.asarray(output_list), numpy.asarray(output_lost)
    return output_list, output_lost
