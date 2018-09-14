# -*- coding: utf-8 -*-
"""Collection of frequently used functions for CSV data handling."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import os

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://scipy.org") from err

from nemoa.common.ntype import (
    Optional, OptStr, OptStrList, OptIntTuple, OptInt)

OptArray = Optional[np.ndarray]

def load(
        path: str, delim: OptStr = None, labels: OptStrList = None,
        usecols: OptIntTuple = None, rowlabelcol: OptInt = None
    ) -> OptArray:
    """Load numpy ndarray from CSV file.

    Args:
        path: file path to CSV file.
        delim: string containing CSV delimiter.
            If not given, the CSV delimiter is detected from CSV file.
        labels: list of strings containing CSV labels.
            If not given, the CSV labels are detected from CSV file.
        usecols: indices if columns
            which are imported from CSV file. If not given, all columns
            are used.
        rowlabelcol: index of column that contains
            rowlabels. If not given, first column of strings is used.

    Returns:
        Numpy ndarray containing data from CSV file, or None if
        data could not be imported.

    """

    # check file
    if not os.path.isfile(path):
        raise ValueError(f"file '{path}' does not exist")

    # get delimiter
    delim = delim or delimiter(path)
    if not delim:
        raise ValueError(f"delimiter in file '{path}' is not supported")

    # get labels
    if not labels:
        labels = get_labels(path, delim=delim)
        if not labels:
            raise ValueError("argument 'usecols' is not valid")
        usecols = tuple(range(len(labels)))
    elif not usecols:
        raise ValueError(
            "argument 'usecols' is required if 'labels' is given")

    # get row label column id
    if rowlabelcol is None:
        rowlabelcol = labelcolid(path, delim=delim)

    # get datatype
    if rowlabelcol is None:
        formats = ('<f8',) * len(usecols)
    elif rowlabelcol not in usecols:
        float_count = len(usecols)
        usecols = (rowlabelcol, ) + usecols
        labels = ('label',) + labels
        formats = ('<U12',) + ('<f8',) * float_count
    else:
        float_count = len(usecols) - 1
        rowlabelcollabel = labels[usecols.index(rowlabelcol)]
        usecols = (rowlabelcol, ) + tuple(
            col for col in usecols if col != rowlabelcol)
        labels = ('label',) + tuple(
            col for col in labels if col != rowlabelcollabel)
        formats = ('<U12',) + ('<f8',) * float_count
    dtype = {'names': labels, 'formats': formats}

    # count rows to skip
    skiprows = 1
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line.startswith('#'):
                skiprows += 1
                continue
            if stripped_line in ['\n', '\r\n']:
                skiprows += 1
                continue
            break

    data = np.loadtxt(
        path, skiprows=skiprows, delimiter=delim, usecols=usecols, dtype=dtype)

    return data

def save(
        path: str, data: np.ndarray, header: OptStr = None,
        labels: OptStrList = None, delim: str = ','
    ) -> bool:
    """Save numpy array to CSV file.

    Args:
        path (string): file path to CSV file.
        data (numpy ndarray): data
        header (string, optional):
        labels (list, optional): list of strings containing CSV labels.
        delim (string, optional):

    Returns:
        True if no error occured.

    """

    if isinstance(header, str):
        header = '# %s\n\n' % (header.replace('\n', '\n# '))
        if isinstance(labels, list):
            header += delim.join(labels)
    elif isinstance(labels, list):
        header = delim.join(labels)

    fmt = delim.join(['%s'] + ['%10.10f'] * (len(data[0]) - 1))

    return np.savetxt(path, data, fmt=fmt, header=header, comments='') is None

def get_header(path: str) -> str:
    """Get header from CSV file.

    Args:
        path (string): file path to CSV file.

    Returns:
        String containing header of CSV file or empty string if header
        could not be detected.

    """

    # check file
    if not os.path.isfile(path):
        raise OSError(
            "could not get CSV header: "
            f"file '{path}' does not exist.")

    # scan csvfile for header
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

    # strip header
    header = header.strip()

    return header

def delimiter(
        path: str, delims: OptStrList = None, minprobe: int = 3,
        maxprobe: int = 100
    ) -> str:
    """Get delimiter from CSV file.

    Args:
        path: file path to CSV file.
        delims: Optional list of strings containing delimiter candidates to
            search for. Default: [',', ';', '\t', ' ']
        minprobe: minimum number of (non comment, not empty) lines used to
            detect CSV delimiter.
        maxprobe: maximum number of (non comment, not empty) lines used to
            detect CSV delimiter.

    Returns:
        Delimiter string of CSV file or False, if delimiter could not be
        detected.

    """

    # check file
    if not os.path.isfile(path):
        raise OSError(f"file '{path}' does not exist.")

    # get default delims
    delims = delims or [',', ';', '\t', ' ']

    delim = None
    with open(path, 'r') as csvfile:
        lines = 1
        probe = ''
        for line in csvfile:

            # check termination criteria
            if bool(delim) or lines > maxprobe:
                break

            # check exclusion criteria
            sline = line.lstrip(' ')
            if sline.startswith('#') or sline in ['\n', '\r\n']:
                continue

            # increase probe
            probe += line
            lines += 1

            # try to detect delimiter of probe
            if lines > minprobe:
                try:
                    dialect = csv.Sniffer().sniff(probe, delims)
                except csv.Error:
                    continue
                delim = dialect.delimiter

    if not delim:
        raise TypeError(f"file '{path}' is not valid")

    return delim

def get_labels(path: str, delim: OptStr = None) -> list:
    """Get (column) labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delim (string, optional): string containing CSV delimiter.

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV file.

    """

    # check file
    if not os.path.isfile(path):
        raise TypeError(f"file '{path}' does not exist")

    # get delimiter
    delim = delim or delimiter(path)
    if not delim:
        raise TypeError(f"delimiter in file '{path}' is not supported")

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:
            sline = line.lstrip(' ')
            if sline.startswith('#') or sline in ['\n', '\r\n']:
                continue
            if first is None:
                first = line
            elif second is None:
                second = line
                break

    if not first or not second:
        raise TypeError(f"file '{path}' is not valid")

    if first.count(delim) == second.count(delim):
        csvtype = 'default'
    elif first.count(delim) == second.count(delim) - 1:
        csvtype = 'r-table'
    else:
        raise TypeError(f"file '{path}' is not valid")

    labels = first.split(delim)
    labels = [col.strip('\"\'\n\r\t ') for col in labels]

    if csvtype == 'default':
        return labels
    if csvtype == 'r_table':
        return ['label'] + labels

    return []

def labelcolid(path: str, delim: OptStr = None) -> int:
    """Get column id for column containing row labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delim (string, optional): string containing CSV delimiter.

    Returns:
        Integer containing first index of CSV data column containing
        strings.

    """

    # check file
    if not os.path.isfile(path):
        raise OSError(f"file '{path}' does not exist")

    # get delimiter
    delim = delim or delimiter(path)
    if not delim:
        raise TypeError(f"the delimiter in file '{path}' is not supported")

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            sline = line.lstrip(' ')
            if sline.startswith('#') or sline in ['\n', '\r\n']:
                continue

            if not first:
                first = line
            elif not second:
                second = line
                break

    if first is None or second is None:
        raise TypeError(f"file '{path}' is not valid")

    colvals = second.split(delim)
    colvals = [col.strip('\"\' \n') for col in colvals]
    for colid, colval in enumerate(colvals):
        try:
            float(colval)
        except ValueError:
            return colid

    return False
