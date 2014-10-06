# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

def data_sum(data, norm = 'S'):
    """Return sum of data.

    Args:
        data: numpy array containing data
        norm: data mean norm
            'S': Sum of Values
            'SE': Sum of Errors / L1 Norm
            'SSE': Sum of Squared Errors
            'RSSE': Root Sum of Squared Errors

    """

    norm = norm.upper()

    # Sum of Values (S)
    if norm == 'S':
        return numpy.sum(data, axis = 0)

    # Sum of Errors (SE) / L1-Norm (L1)
    if norm == 'SE':
        return numpy.sum(numpy.abs(data), axis = 0)

    # Sum of Squared Errors (SSE)
    if norm == 'SSE':
        return numpy.sum(data ** 2, axis = 0)

    # Root Sum of Squared Errors (RSSE)
    if norm == 'RSSE':
        return numpy.sqrt(numpy.sum(data ** 2, axis = 0))

    return nemoa.log('error',
        "unsupported data sum norm '%s'" % (norm))

def data_mean(data, norm = 'M'):
    """Return mean of data.

    Args:
        data: numpy array containing data
        norm: data mean norm
            'M': Arithmetic Mean of Values
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors / L2 Norm

    """

    norm = norm.upper()

    # Mean of Values (M)
    if norm == 'M':
        return numpy.mean(data, axis = 0)

    # Mean of Errors (ME)
    if norm == 'ME':
        return numpy.mean(numpy.abs(data), axis = 0)

    # Mean of Squared Errors (MSE)
    if norm == 'MSE':
        return numpy.mean(data ** 2, axis = 0)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if norm == 'RMSE':
        return numpy.sqrt(numpy.mean(data ** 2, axis = 0))

    return nemoa.log('error',
        "unsupported data mean norm '%s'" % (norm))

def data_deviation(data, norm = 'SD'):
    """Return deviation of data.

    Args:
        data: numpy array containing data
        norm: data deviation norm
            'SD': Standard Deviation of Values
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors

    """

    norm = norm.upper()

    # Standard Deviation of Data (SD)
    if norm == 'SD':
        return numpy.std(data, axis = 0)

    # Standard Deviation of Errors (SDE)
    if norm == 'SDE':
        return numpy.std(numpy.abs(data), axis = 0)

    # Standard Deviation of Squared Errors (SDSE)
    if norm == 'SDSE':
        return numpy.std(data ** 2, axis = 0)

    return nemoa.log('error',
        "unsupported data deviation norm '%s'" % (deviation))
