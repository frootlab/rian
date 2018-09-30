# -*- coding: utf-8 -*-
"""I/O functions for CSV files."""

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
        "https://scipy.org") from err

from nemoa.common import npath
from nemoa.types import (
    NpArray, OptStr, OptStrList, OptInt, OptIntTuple, PathLike)

FILEEXTS = ['.csv', '.tsv']

def load(
        filepath: PathLike, delim: OptStr = None,
        labels: OptStrList = None, usecols: OptIntTuple = None,
        rowlabelcol: OptInt = None) -> NpArray:
    """Load numpy ndarray from CSV file.

    Args:
        filepath: Filepath that points to a valid CSV file.
        delim: String containing CSV delimiter.
            If 'delim' is None, then the CSV delimiter is detected from file.
            Default: None
        labels: list of strings containing CSV labels.
            If 'labels' is None, the the CSV labels are detected from file.
            Default: None
        usecols: Column IDs of columns which are to be imported from the file.
            If 'usecols' is None, then all columns are imported.
            Default: None
        rowlabelcol: Column ID of column, which contains the row annotation.
            If 'rowlabelcol' is None, then the first column is used.
            Default: None

    Returns:
        NumPy ndarray containing data from CSV file, or None if
        data could not be imported.

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Get delimiter
    delim = delim or getdelim(path)
    if not delim:
        raise ValueError(f"delimiter in file '{path}' is not supported")

    # Get labels
    if not labels:
        labels = getlabels(path, delim=delim)
        if not labels:
            raise ValueError("argument 'usecols' is not valid")
        usecols = tuple(range(len(labels)))
    elif not usecols:
        raise ValueError(
            "argument 'usecols' is required if 'labels' is given")

    # Get column id of annotation column
    if rowlabelcol is None:
        rowlabelcol = getanncolid(path, delim=delim)

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
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # Check exclusion criteria
            sline = line.lstrip(' ')
            if sline.startswith('#'):
                skiprows += 1
                continue
            if sline in ['\n', '\r\n']:
                skiprows += 1
                continue
            break

    # Import CSV file to NumPy ndarray
    return np.loadtxt(
        path, skiprows=skiprows, delimiter=delim, usecols=usecols,
        dtype=dtype)

def save(
        filepath: PathLike, data: NpArray, header: OptStr = None,
        labels: OptStrList = None, delim: str = ',') -> bool:
    """Save NumPy array to CSV file.

    Args:
        filepath: Filepath that points to a valid filename in a writeable
            directory.
        data: NumPy ndarray containing the data which is to be exported to
            a CSV file.
        header: String which is included in the CSV file whithin an initial
            comment. If 'header' is None, then no initial comment is created.
            Default: None
        labels: List of strings containing CSV Column labels.
        delim: String containing CSV delimiter.
            Default: ','

    Returns:
        True if no error occured.

    """
    # Convert filepath to str
    path = str(filepath)

    # Check and prepare arguments
    if isinstance(header, str):
        header = '# ' + header.replace('\n', '\n# ') + '\n\n'
        if isinstance(labels, list):
            header += delim.join(labels)
    elif isinstance(labels, list):
        header = delim.join(labels)

    # Get number of columns from last entry in data.shape
    cols = list(getattr(data, 'shape'))[-1]

    # Get format from number of columns
    fmt = delim.join(['%s'] + ['%10.10f'] * (cols - 1))

    return np.savetxt(
        path, data, fmt=fmt, header=header, comments='') is None

def getheader(filepath: PathLike) -> str:
    """Get header from CSV file.

    Args:
        filepath: Filepath that points to a valid CSV file.

    Returns:
        String containing header of CSV file or empty string if header
        could not be detected.

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Scan CSV-file for Header
    header = ''
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line in ['\n', '\r\n']:
                continue
            if stripped_line.startswith('#'):
                header += stripped_line[1:].lstrip()
                continue
            break

    # Strip and return Header
    return header.strip()

def getdelim(
        filepath: PathLike, delims: OptStrList = None, minprobe: int = 3,
        maxprobe: int = 100) -> str:
    r"""Detect delimiter from CSV file.

    Args:
        filepath: filepath that points to a valid CSV file.
        delims: Optional list of strings containing delimiter candidates to
            search for. Default: [',', '\t', ';', ' ', ':']
        minprobe: Minimum number of lines used to detect CSV delimiter.
            Remark: Only non comment, not empty lines are used
        maxprobe: Maximum number of lines used to detect CSV delimiter.
            Remark: Only non comment, not empty lines are used

    Returns:
        Delimiter string of CSV file or False, if delimiter could not be
        detected.

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Set default delimiters
    delims = delims or [',', '\t', ';', ' ', ':']

    # Detect delimiter
    delim = None
    lines = 1
    probe = ''
    with open(path, 'r') as file:
        for line in file:

            # Check termination criteria
            if delim or lines > maxprobe:
                break

            # Check exclusion criteria
            bare = line.lstrip(' ')
            if bare.startswith('#') or bare in ['\n', '\r\n']:
                continue

            # Increase probe size
            probe += line
            lines += 1

            # Try to detect delimiter from probe using csv.Sniffer
            sniffer = csv.Sniffer()
            sniffer.preferred = delims
            if lines > minprobe:
                try:
                    dialect = sniffer.sniff(probe)
                except csv.Error:
                    continue
                else:
                    delim = dialect.delimiter

    if not delim:
        raise csv.Error(f"file '{path}' is not a valid CSV file")

    return delim

def getlabelformat(filepath: PathLike, delim: OptStr = None) -> str:
    """Get column label format from CSV file.

    Args:
        filepath: Filepath that points to a valid CSV file.
        delim: String containing CSV delimiter.
            If 'delim' is None, then the CSV delimiter is detected from file.
            Default: None

    Returns:
        Format of the column labels. The following formats are distinguished:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in [RFC4180].
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.

    References:
        [RFC4180] https://tools.ietf.org/html/rfc4180

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Get delimiter
    delim = delim or getdelim(path)
    if not delim:
        raise csv.Error(f"delimiter in CSV file '{path}' is not supported")

    # Get first and second (non comment, non empty) line
    line1, line2 = None, None
    with open(path, 'r') as file:
        for line in file:
            bare = line.lstrip(' ')
            if bare.startswith('#') or bare in ['\n', '\r\n']:
                continue
            if line1 is None:
                line1 = line
            elif line2 is None:
                line2 = line
                break
    if not line1 or not line2:
        raise csv.Error(f"file '{path}' is not a valid CSV file")

    # Determine column label format
    if line1.count(delim) == line2.count(delim):
        return 'standard' # standard format
    if line1.count(delim) == line2.count(delim) - 1:
        return 'r-table' # R-Table CSV export

    raise csv.Error(f"file '{path}' is not a valid CSV file")

def getlabels(
        filepath: PathLike, delim: OptStr = None, fmt: OptStr = None) -> list:
    """Get column labels from CSV file.

    Args:
        filepath: Filepath that points to a valid CSV file.
        delim: String containing CSV delimiter.
            If 'delim' is None, then the CSV delimiter is detected from file.
            Default: None
        fmt: Format of the column labels. Accepted values are:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in [RFC4180].
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.
            None: Detect the used format from the CSV file.
            Default: None

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV file.

    References:
        [RFC4180] https://tools.ietf.org/html/rfc4180

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Get delimiter
    delim = delim or getdelim(path)
    if not delim:
        raise csv.Error(f"delimiter in CSV file '{path}' is not supported")

    # Get column label format
    fmt = fmt or getlabelformat(path, delim=delim)
    if not fmt:
        raise csv.Error(f"label format in CSV file '{path}' is not supported")

    # Get first line (non comment, non empty) of CSV file
    line1 = ''
    with open(path, 'r') as file:
        for line in file:
            bare = line.lstrip(' ')
            if bare.startswith('#') or bare in ['\n', '\r\n']:
                continue
            line1 = line
            break

    # Get unformated column labels from first line
    labels = [col.strip('\"\'\n\r\t ') for col in line1.split(delim)]

    # Format column labels
    if fmt == 'standard':
        return labels
    if fmt == 'r-table':
        return ['label'] + labels

    raise csv.Error(f"label format in CSV file '{path}' is not supported")

def getanncolid(
        filepath: PathLike, delim: OptStr = None, fmt: OptStr = None) -> OptInt:
    """Get column id of the annotation column from CSV file.

    The annotation column designates the CSV column, which contains the
    annotation strings of the records.

    Args:
        filepath: Filepath that points to a valid CSV file.
        delim: String containing CSV delimiter.
            If 'delim' is None, then the CSV delimiter is detected from file.
            Default: None
        fmt: Format of the column labels. Accepted values are:
            'standard': The number of column labels equals the size of the
                CSV records, as desribed in [RFC4180].
            'r-table': The first column always is used for record annotation
                and therfore does not require a seperate column label for it's
                identification.

    Returns:
        Column ID of the annotation column or None, if the CSV file does not
        contain record annotation.

    References:
        [RFC4180] https://tools.ietf.org/html/rfc4180

    """
    # Validate path
    path = npath.validfile(filepath)
    if not path:
        raise OSError(f"file '{str(filepath)}' does not exist")

    # Get delimiter
    delim = delim or getdelim(path)
    if not delim:
        raise csv.Error(f"delimiter in CSV file '{path}' is not supported")

    # Get column label format
    fmt = fmt or getlabelformat(path, delim=delim)
    if not fmt:
        raise csv.Error(f"label format in CSV file '{path}' is not supported")
    if fmt == 'r-table':
        return 0 # In R-tables the first column is used for annotation

    # Get first and second non comment and non empty lines
    line1, line2 = None, None
    with open(path, 'r') as file:
        for line in file:
            # Check for comments and blank lines
            bare = line.lstrip(' ')
            if bare.startswith('#') or bare in ['\n', '\r\n']:
                continue

            if not line1:
                line1 = line
            elif not line2:
                line2 = line
                break
    if line1 is None or line2 is None:
        raise csv.Error(f"file '{path}' is not a valid CSV file")

    # Determine annotation column id from first value in the second line,
    # that can not be converted to a float
    values = [col.strip('\"\' \n') for col in line2.split(delim)]
    for cid, val in enumerate(values):
        try:
            float(val)
        except ValueError:
            return cid

    return None
