# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as E: raise ImportError(
    "nemoa.common.array requires numpy: https://scipy.org") from E

#
# numpy ndarray functions
#

def sumnorm(data, norm = 'S', axis = 0):
    """Sum of array.

    Calculate sum of data along given axes, using a given norm.

    Args:
        data (ndarray): Numpy array containing data
        norm (str, optional): Data mean norm
            'S': Sum of Values
            'SE': Sum of Errors / L1 Norm
            'SSE': Sum of Squared Errors
            'RSSE': Root Sum of Squared Errors
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a sum is performed.

    Returns:
        Sum of data as ndarray
        or False if given norm is not supported.

    """

    n = norm.upper()

    # Sum of Values (S)
    if n == 'S': return numpy.sum(data, axis = axis)
    # Sum of Errors (SE) / L1-Norm (L1)
    if n == 'SE': return numpy.sum(numpy.abs(data), axis = axis)
    # Sum of Squared Errors (SSE)
    if n == 'SSE': return numpy.sum(data ** 2, axis = axis)
    # Root Sum of Squared Errors (RSSE)
    if n == 'RSSE': return numpy.sqrt(numpy.sum(data ** 2, axis = axis))

    raise Warning("""could not calculate normed sum:
        unsupported norm '%s'""" % norm)

def meannorm(data, norm = 'M', axis = 0):
    """Mean of data.

    Calculate mean of data along given axes, using a given norm.

    Args:
        data (ndarray): Numpy array containing data
        norm (str, optional): Data mean norm
            'M': Arithmetic Mean of Values
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors / L2 Norm
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a mean is performed.

    Returns:
        Mean of data as ndarray
        or False if given norm is not supported.

    """

    n = norm.upper()

    # Mean of Values (M)
    if n == 'M': return numpy.mean(data, axis = axis)
    # Mean of Errors (ME)
    if n == 'ME': return numpy.mean(numpy.abs(data), axis = axis)
    # Mean of Squared Errors (MSE)
    if n == 'MSE': return numpy.mean(data ** 2, axis = axis)
    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if n == 'RMSE':
        return numpy.sqrt(numpy.mean(data ** 2, axis = axis))

    raise ValueError("""could not calculate normed mean:
        unsupported norm '%s'""" % norm)

def devnorm(data, norm = 'SD', axis = 0):
    """Deviation of data.

    Calculate deviation of data along given axes, using a given norm.

    Args:
        data (ndarray): Numpy array containing data
        norm (str, optional): Data deviation norm
            'SD': Standard Deviation of Values
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a deviation is performed.

    Returns:
        Deviation of data as ndarray
        or False if given norm is not supported.

    """

    n = norm.upper()

    # Standard Deviation of Data (SD)
    if n == 'SD': return numpy.std(data, axis = axis)
    # Standard Deviation of Errors (SDE)
    if n == 'SDE': return numpy.std(numpy.abs(data), axis = axis)
    # Standard Deviation of Squared Errors (SDSE)
    if n == 'SDSE': return numpy.std(data ** 2, axis = axis)

    raise ValueError("""could not calculate normed deviation:
        unsupported deviation norm '%s'""" % norm)

#
# numpy recarray functions
#

def insert(data, source, columns = None):
    """Append columns from source to data."""

    from numpy.lib import recfunctions

    if not columns: columns = source.dtype.names
    return recfunctions.rec_append_fields(data, columns,
        [source[col] for col in columns])
