#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy

def convert(list, input, output = None, filter = False, quiet = True):

    genericClasses = ['number', 'string', 'float']

    if isinstance(list, (numpy.ndarray)):
        list = list.tolist()
        inputDtype = 'nparray'
    else:
        inputDtype = 'list'

    # 'input'
    if input in genericClasses:
        inputClass  = 'generic'
        inputFormat = input
    elif ':' in input:
        inputClass  = input.lower().split(':')[0].strip()
        inputFormat = input.lower().split(':')[1].strip()
    else:
        nemoa.log('warning', 'could not convert list: unknown input format "' + input + '"!')
        return None

    # 'output'
    if output in genericClasses:
        outputClass  = 'generic'
        outputFormat = output
    elif output == None:
        outputClass  = inputClass
        outputFormat = None
    elif ':' in input: 
        outputClass  = output.lower().split(':')[0].strip()
        outputFormat = output.lower().split(':')[1].strip()
    else:
        mp_warnung('could not convert list: unknown output format "' + output + '"!')
        return None

    # 'input' vs 'output'
    if inputClass != outputClass:
        nemoa.log('warning', '"' + inputClass + '" can not be converted to "' + outputClass + '"')
        return None

    # trivial cases
    if inputClass == 'generic' or inputFormat == outputFormat:
        if inputDtype == 'nparray':
            return numpy.asarray(list), numpy.asarray([])
        else:
            return list, []

    # import annotation module
    modName = inputClass.lower()
    import importlib
    module = importlib.import_module('nemoa.annotation.' + modName)
    converter = getattr(module, modName)()
    
    outList, outLost = converter.convert_list(list, inputFormat, outputFormat, filter, quiet = quiet)

    if inputDtype == 'nparray':
        return numpy.asarray(outList), numpy.asarray(outLost)

    return outList, outLost
