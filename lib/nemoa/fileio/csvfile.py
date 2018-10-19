# -*- coding: utf-8 -*-
"""I/O functions for CSV-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _RFC4180:
    https://tools.ietf.org/html/rfc4180

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import csv

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://pypi.org/project/numpy") from err

from nemoa.fileio import textfile
from nemoa.types import (
    FileOrPathLike, NpArray, OptInt, OptIntTuple, OptNpArray, OptStr,
    OptStrList)

FILEEXTS = ['.csv', '.csv.gz']

def load(
        file: FileOrPathLike, delim: OptStr = None,
        labels: OptStrList = None, usecols: OptIntTuple = None,
        rowlabelcol: OptInt = None) -> OptNpArray:
    """Load numpy ndarray from CSV-file.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the CSV-file.
        labels: List of column labels in CSV-file. By default the list of column
            labels is taken from the first content line in the CSV-file.
        usecols: Indices of the columns which are to be imported from the file.
            By default all columns are imported.
        rowlabelcol: Column ID of column, which contains the row annotation.
            By default the first column is used for annotation.

    Returns:
        Numpy ndarray containing data from CSV-file, or None if the data could
        not be imported.

    """
    # Get delimiter
    delim = delim or get_delim(file)
    if not delim:
        return None

    # Get labels
    if not labels:
        labels = get_labels(file, delim=delim)
        if not labels:
            raise ValueError("argument 'usecols' is not valid")
        usecols = tuple(range(len(labels)))
    elif not usecols:
        raise ValueError(
            "argument 'usecols' is required if 'labels' is given")

    # Get column id of annotation column
    rowlabelcol = rowlabelcol or get_annotation_colid(file, delim=delim)

    # Get CSV data format
    if rowlabelcol is None:
        formats = ('<f8',) * len(usecols)
    elif rowlabelcol not in usecols:
        float_count = len(usecols)
        usecols = (rowlabelcol, ) + usecols
        labels = ['label'] + labels
        formats = ('<U12',) + ('<f8',) * float_count
    else:
        float_count = len(usecols) - 1
        rowlabelcollabel = labels[usecols.index(rowlabelcol)]
        usecols = (rowlabelcol, ) + tuple(
            col for col in usecols if col != rowlabelcol)
        labels = ['label'] + [col for col in labels if col != rowlabelcollabel]
        formats = ('<U12',) + ('<f8',) * float_count
    dtype = {'names': labels, 'formats': formats}

    # Count how many 'comment' and 'blank' rows are to be skipped
    skiprows = 1
    with textfile.openx(file, mode='r') as fd:
        for line in fd:
            strip = line.strip()
            if not strip or strip.startswith('#'):
                skiprows += 1
                continue
            break

    # Import CSV-file to NumPy ndarray
    with textfile.openx(file, mode='r') as fd:
        return np.loadtxt(
            fd, skiprows=skiprows, delimiter=delim, usecols=usecols,
            dtype=dtype)

def save(
        file: FileOrPathLike, data: NpArray, header: OptStr = None,
        labels: OptStrList = None, delim: str = ',') -> None:
    """Save NumPy array to CSV-file.

    Args:
        file: String, `path-like object`_ or `file-like object`_ that points to
            a valid CSV-file in the directory structure of the system.
        data: NumPy ndarray containing the data which is to be exported to
            a CSV-file.
        header: String which is included in the CSV-file whithin an initial
            comment. If 'header' is None, then no initial comment is created.
            Default: None
        labels: List of strings containing CSV Column labels.
        delim: String containing CSV-delimiter. The default value is ','

    Returns:
        True if no error occured.

    """
    # Check and prepare arguments
    if isinstance(header, str):
        header = '# ' + header.replace('\n', '\n# ') + '\n\n'
        if isinstance(labels, list):
            header += delim.join(labels)
    elif isinstance(labels, list):
        header = delim.join(labels)

    # Get number of columns from last entry in data.shape
    cols = list(getattr(data, 'shape'))[-1]

    # Get column format
    fmt = delim.join(['%s'] + ['%10.10f'] * (cols - 1))

    with textfile.openx(file, mode='w') as fd:
        np.savetxt(fd, data, fmt=fmt, header=header, comments='')

def get_header(file: FileOrPathLike) -> str:
    """Get header from CSV-file.

    Args:
        file: String or `path-like object`_ that points to a readable file in
            the directory structure of the system, or a `file-like object`_ in
            reading mode.

    Returns:
        String containing the header of the CSV-file or an empty string, if no
        header could be detected.

    """
    return textfile.get_header(file)

def get_delim(
        file: FileOrPathLike, candidates: OptStrList = None, mincount: int = 3,
        maxcount: int = 100) -> OptStr:
    r"""Detect delimiter of CSV-file.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        candidates: Optional list of strings containing delimiter candidates to
            search for. Default: [',', '\t', ';', ' ', ':']
        mincount: Minimum number of lines used to detect CSV delimiter. Thereby
            only non comment and non empty lines are used.
        maxcount: Maximum number of lines used to detect CSV delimiter. Thereby
            only non comment and non empty lines are used.

    Returns:
        Delimiter string of CSV-file or None, if the delimiter could not be
        detected.

    """
    # Initialise CSV-Sniffer with default values
    sniffer = csv.Sniffer()
    sniffer.preferred = candidates or [',', '\t', ';', ' ', ':']
    delim: OptStr = None

    # Detect delimiter
    with textfile.openx(file, mode='r') as fd:
        size, probe = 0, ''
        for line in fd:
            # Check termination criteria
            if size > maxcount:
                break
            # Check exclusion criteria
            strip = line.strip()
            if not strip or strip.startswith('#'):
                continue
            # Increase probe size
            probe += line
            size += 1
            if size <= mincount:
                continue
            # Try to detect delimiter from probe using csv.Sniffer
            try:
                dialect = sniffer.sniff(probe)
            except csv.Error:
                continue
            delim = dialect.delimiter
            break

    return delim

def get_labels_format(file: FileOrPathLike, delim: OptStr = None) -> OptStr:
    """Get format of column labels from CSV-file.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the given file.

    Returns:
        Format of the column labels. The following formats are distinguished:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in `RFC4180`_.
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.

    """
    # Get delimiter
    delim = delim or get_delim(file)
    if not delim:
        return None

    # Get first and second content lines (non comment, non empty) of CSV-file
    lines = textfile.get_content(file, lines=2)
    if len(lines) != 2:
        return None

    # Determine column label format
    if lines[0].count(delim) == lines[1].count(delim):
        return 'standard' # standard format
    if lines[0].count(delim) == lines[1].count(delim) - 1:
        return 'r-table' # R-Table CSV export

    return None

def get_labels(
        file: FileOrPathLike, delim: OptStr = None,
        fmt: OptStr = None) -> OptStrList:
    """Get column labels from CSV-file.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the given file.
        fmt: Format of the column labels. By default the format is detected from
            the given file. Accepted values are:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in `RFC4180`_.
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV-file.

    """
    # Get delimiter
    delim = delim or get_delim(file)
    if not delim:
        return None

    # Get format of column labels
    fmt = fmt or get_labels_format(file, delim=delim)
    if not fmt:
        return None

    # Get first content line (non comment, non empty) of CSV-file
    line = textfile.get_content(file, lines=1)[0]

    # Get column labels from first content
    labels = [col.strip('\"\'\n\r\t ') for col in line.split(delim)]

    # Format column labels
    if fmt == 'standard':
        return labels
    if fmt == 'r-table':
        return ['label'] + labels
    return None

def get_annotation_colid(
        file: FileOrPathLike, delim: OptStr = None,
        fmt: OptStr = None) -> OptInt:
    """Get index of the annotation column of a CSV-file.

    The annotation column designates the CSV column, which contains the
    annotation strings of the records.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the given file.
        fmt: Format of the column labels. By default the format is detected from
            the given file. Accepted values are:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in `RFC4180`_.
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.

    Returns:
        Column ID of the annotation column or None, if the CSV-file does not
        contain record annotation.

    """
    # Get delimiter
    delim = delim or get_delim(file)
    if not delim:
        return None

    # Get format of column labels
    fmt = fmt or get_labels_format(file, delim=delim)
    if not fmt:
        return None
    if fmt == 'r-table':
        return 0 # In R-tables the first column is used for annotation

    # Get first and second content lines (non comment, non empty) of CSV-file
    lines = textfile.get_content(file, lines=2)
    if len(lines) != 2:
        return None

    # Determine annotation column id from first value in the second line, that
    # can not be converted to a float
    values = [col.strip('\"\' \n') for col in lines[1].split(delim)]
    for cid, val in enumerate(values):
        try:
            float(val)
        except ValueError:
            return cid

    return None
