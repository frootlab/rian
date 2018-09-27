# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import importlib

def convert(list, input, output = None, filter = False):

    generic_types = ['number', 'string', 'float']

    if isinstance(list, (numpy.ndarray)):
        list = list.tolist()
        input_dtype = 'nparray'
    else: input_dtype = 'list'

    # 'input'
    if input in generic_types:
        input_class  = 'generic'
        input_format = input
    elif ':' in input:
        input_class  = input.lower().split(':')[0].strip()
        input_format = input.lower().split(':')[1].strip()
    else: raise Warning("""could not convert list:
        unknown input format '%s'.""" % input)

    # 'output'
    if output in generic_types:
        output_class  = 'generic'
        output_format = output
    elif not output:
        output_class  = input_class
        output_format = None
    elif ':' in input:
        output_class  = output.lower().split(':')[0].strip()
        output_format = output.lower().split(':')[1].strip()
    else: raise Warning("""could not convert list:
        unknown output format '%s'.""" % output)

    # 'input' vs 'output'
    if input_class != output_class:
        raise Warning("'%s' can not be converted to '%s'"
            % (input_class, output_class))

    # trivial cases
    if input_class == 'generic' or input_format == output_format:
        if input_dtype == 'nparray':
            return numpy.asarray(list), numpy.asarray([])
        else: return list, []

    # import annotation module
    module_name = input_class.lower()
    module = importlib.import_module('nemoa.dataset.commons.labels.'
        + module_name)
    converter = getattr(module, module_name)()
    output_list, output_lost = converter.convert_list(
        list, input_format, output_format, filter)
    if input_dtype == 'nparray':
        return numpy.asarray(output_list), numpy.asarray(output_lost)
    return output_list, output_lost
