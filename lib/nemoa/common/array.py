# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

try: import numpy
except ImportError as E: raise ImportError(
    "nemoa.common.array requires numpy: https://scipy.org") from E

from typing import Optional, Tuple, Union

ndarray = numpy.ndarray
recarray = numpy.recarray
Axis = Optional[Union[int, Tuple[int]]]

#
# numpy ndarray functions
#

def sumnorm(a: ndarray, norm: str = 'S', axis: Axis = 0) -> ndarray:
    """Sum of array.

    Calculate sum of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str, optional): Data mean norm
            'S': Sum of Values
            'SE': Sum of Errors / L1 Norm
            'SSE': Sum of Squared Errors
            'RSSE': Root Sum of Squared Errors / L2 Norm
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a sum is performed.

    Returns:
        Sum of data as ndarray.

    """

    n = norm.upper()

    # Sum of Values (S)
    if n == 'S': return numpy.sum(a, axis = axis)

    # Sum of Errors (SE) / L1-Norm (L1)
    if n in ['SE', 'L1']: return numpy.sum(numpy.abs(a), axis = axis)

    # Sum of Squared Errors (SSE)
    if n == 'SSE': return numpy.sum(a ** 2, axis = axis)

    # Root Sum of Squared Errors (RSSE) / L2-Norm (L2)
    if n in ['RSSE', 'L2']: return numpy.sqrt(numpy.sum(a ** 2, axis = axis))

    raise ValueError(f"usupported norm '{norm}'")

def meannorm(a: ndarray, norm: str = 'M', axis: Axis = 0) -> ndarray:
    """Mean of data.

    Calculate mean of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str, optional): Data mean norm
            'M': Arithmetic Mean of Values
            'ME': Mean of Errors
            'MSE': Mean of Squared Errors
            'RMSE': Root Mean of Squared Errors / L2 Norm
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a mean is performed.

    Returns:
        Mean of data as ndarray

    """

    n = norm.upper()

    # Mean of Values (M)
    if n == 'M': return numpy.mean(a, axis = axis)

    # Mean of Errors (ME)
    if n == 'ME': return numpy.mean(numpy.abs(a), axis = axis)

    # Mean of Squared Errors (MSE)
    if n == 'MSE': return numpy.mean(a ** 2, axis = axis)

    # Root Mean of Squared Errors (RMSE) / L2-Norm
    if n == 'RMSE': return numpy.sqrt(numpy.mean(a ** 2, axis = axis))

    raise ValueError(f"unsupported norm '{norm}'")

def devnorm(a: ndarray, norm: str = 'SD', axis: Axis = 0) -> ndarray:
    """Deviation of data.

    Calculate deviation of data along given axes, using a given norm.

    Args:
        a (ndarray): Numpy array containing data
        norm (str, optional): Data deviation norm
            'SD': Standard Deviation of Values
            'SDE': Standard Deviation of Errors
            'SDSE': Standard Deviation of Squared Errors
        axis (None or int or tuple of ints, optional):
            Axis or axes along which a deviation is performed.

    Returns:
        Deviation of data as ndarray

    """

    n = norm.upper()

    # Standard Deviation of Data (SD)
    if n == 'SD': return numpy.std(a, axis = axis)

    # Standard Deviation of Errors (SDE)
    if n == 'SDE': return numpy.std(numpy.abs(a), axis = axis)

    # Standard Deviation of Squared Errors (SDSE)
    if n == 'SDSE': return numpy.std(a ** 2, axis = axis)

    raise ValueError(f"unsupported norm '{norm}'")

#
# numpy recarray functions
#

def add_columns(base: recarray, data: recarray,
    names: Optional[Tuple[str]] = None) -> recarray:
    """Add columns from source recarray to target recarray.

    Wrapper function to numpy.lib.recfunctions.rec_append_fields:
    https://www.numpy.org/devdocs/user/basics.rec.html

    Args:
        base (recarray): Numpy record array with table like data
        data (recarray): Numpy record array storing the fields
            to add to the base.
        names (tuple of string or None, optional): String or sequence
            of strings corresponding to the names of the new fields.

    Returns:
        Numpy record array containing the base array, as well as the
        appended columns.

    """

    from numpy.lib import recfunctions

    if not columns: columns = s.dtype.names
    extended = recfunctions.rec_append_fields(base, names,
        [data[c] for c in names])

    return extended
