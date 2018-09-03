# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import os

try:
    import numpy as np
except ImportError as E:
    raise ImportError("requires package numpy: "
        "https://scipy.org") from E

from typing import Optional

def load(path: str, delim: Optional[str] = None,
    labels: Optional[list] = None, usecols: Optional[tuple] = None,
    rowlabelcol: Optional[int] = None) -> Optional[np.ndarray]:
    """Load numpy ndarray from CSV file.

    Args:
        path (string): file path to CSV file.
        delim (string, optional): string containing CSV delimiter.
            If not given, the CSV delimiter is detected from CSV file.
        labels (list, optional): list of strings containing CSV labels.
            If not given, the CSV labels are detected from CSV file.
        usecols (tuple of integers, optional): indices if columns
            which are imported from CSV file. If not given, all columns
            are used.
        rowlabelcol (int, optional): index of column that contains
            rowlabels. If not given, first column of strings is used.

    Returns:
        Numpy ndarray containing data from CSV file, or None if
        data could not be imported.

    """

    # check file
    if not os.path.isfile(path):
        raise ValueError(f"file '{path}' does not exist")

    # get delimiter
    delim = delim or get_delim(path)
    if not delim:
        raise ValueError(f"delimiter in file '{path}' is not supported")

    # get labels
    if labels:
        if not usecols: raise ValueError("argument 'usecols' is not given")
    else:
        labels = get_labels(path, delim = delim)
        usecols = tuple(range(len(labels)))
    if not labels:
        raise ValueError("argument 'usecols' is not valid")

    # get row label column id
    if rowlabelcol is None:
        rowlabelcol = get_labelcolumn(path, delim = delim)

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
        usecols = (rowlabelcol, ) + tuple(col for col in usecols
            if col != rowlabelcol)
        labels = ('label',) + tuple(col for col in labels
            if col != rowlabelcollabel)
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

    data = np.loadtxt(path, skiprows = skiprows,
        delimiter = delim, usecols = usecols, dtype = dtype)

    return data

def save(path: str, data: np.ndarray, header: Optional[str] = None,
    labels: Optional[list] = None, delim: str = ',') -> bool:
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
        if isinstance(labels, list): header += delim.join(labels)
    elif isinstance(labels, list): header = delim.join(labels)

    fmt = delim.join(['%s'] + ['%10.10f'] * (len(data[0]) - 1))
    np.savetxt(path, data, fmt = fmt, header = header, comments = '')

    return True

def get_header(path: str) -> str:
    """Get header from CSV file.

    Args:
        path (string): file path to CSV file.

    Returns:
        String containing header of CSV file or empty string if header
        could not be detected.

    """

    # check file
    if not os.path.isfile(path): raise OSError(
        "could not get CSV header: "
        f"file '{path}' does not exist.")

    # scan csvfile for header
    header = ''
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line in ['\n', '\r\n']: continue
            if stripped_line.startswith('#'):
                header += stripped_line[1:].lstrip()
                continue
            break

    # strip header
    header = header.strip()

    return header

def get_delim(path: str, delims: list = [',', ';', '\t', ' '],
    minprobe: int = 3, maxprobe: int = 100) -> str:
    """Get delimiter from CSV file.

    Args:
        path (string): file path to CSV file.
        delims (list, optional): list of strings containing delimiter
            candidates to search for.
        minprobe (integer, optional): minimum number of non comment,
            non empty lines used to detect CSV delimiter.
        maxprobe (integer, optional): maximum number of non comment,
            non empty lines used to detect CSV delimiter.

    Returns:
        String containing delimiter of CSV file or False if delimiter
        could not be detected.

    """

    # check file
    if not os.path.isfile(path): raise OSError(
        "could not determine csv delimiter: "
        "file '%s' does not exist." % path)

    delim = None
    with open(path, 'r') as csvfile:
        lines = 1
        probe = ''
        for line in csvfile:

            # check termination criteria
            if bool(delim) or lines > maxprobe: break

            # check exclusion criteria
            sline = line.lstrip(' ')
            if sline.startswith('#') or sline in ['\n', '\r\n']: continue

            # increase probe
            probe += line
            lines += 1

            # try to detect delimiter of probe
            if lines > minprobe:
                try: dialect = csv.Sniffer().sniff(probe, delims)
                except Exception as e: continue
                delim = dialect.delimiter

    if not delim: raise TypeError(
        f"could not get CSV delimiter: file '{path}' is not valid.")

    return delim

def get_labels(path: str, delim: Optional[str] = None) -> list:
    """Get (column) labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delim (string, optional): string containing CSV delimiter.

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV file.

    """

    # check file
    if not os.path.isfile(path): raise TypeError(
        f"could not get CSV labels: file '{path}' does not exist.")

    # get delimiter
    if not delim: delim = get_delim(path)
    if not delim: raise TypeError(
        "could not get CSV labels: "
        f"the delimiter in file '{path}' is not supported.")

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:
            stripped_line = line.lstrip(' ')
            if stripped_line.startswith('#'): continue
            if stripped_line  in ['\n', '\r\n']: continue
            if first is None: first = line
            elif second is None:
                second = line
                break

    if not first or not second: raise TypeError(
        f"could not get CSV labels: file '{path}' is not valid.")

    if first.count(delim) == second.count(delim): csvtype = 'default'
    elif first.count(delim) == second.count(delim) - 1:
        csvtype == 'r-table'
    else: raise TypeError(
        f"could not get CSV labels: file '{path}' is not valid.")

    col_labels = first.split(delim)
    col_labels = [col.strip('\"\'\n\r\t ') for col in col_labels]

    if csvtype == 'default': return col_labels
    if csvtype == 'r_table': return ['label'] + col_labels

    return []

def get_labelcolumn(path: str, delim: Optional[str] = None) -> int:
    """Get column id for column containing row labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delim (string, optional): string containing CSV delimiter.

    Returns:
        Integer containing first index of CSV data column containing
        strings.

    """

    # check file
    if not os.path.isfile(path): raise OSError(
        "could not get csv row label column id: "
        f"file '{path}' does not exist.")

    # get delimiter
    if not delim: delim = get_delim(path)
    if not delim: raise TypeError(
        "could not get csv row label column id: "
        f"the delimiter in file '{path}' is not supported.")

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            sline = line.lstrip(' ')
            if sline.startswith('#') or sline in ['\n', '\r\n']:
                continue

            if not first: first = line
            elif not second:
                second = line
                break

    if first is None or second is None: raise TypeError(
        "could not get csv row label column id: "
        f"file '{path}' is not valid.")

    colvals = second.split(delim)
    colvals = [col.strip('\"\' \n') for col in colvals]
    for colid, colval in enumerate(colvals):
        try: float(colval)
        except ValueError: return colid

    return False
