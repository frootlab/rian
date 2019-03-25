# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

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
