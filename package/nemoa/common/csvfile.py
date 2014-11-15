# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import nemoa
import numpy
import os

def csv_get_header(path):
    """Get header from CSV file.

    Args:
        path (string): file path to CSV file.

    Returns:
        String containing header of CSV file or empty string if header
        could not be detected.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not get csv header: file '%s' does not exist." % (path))

    # scan csvfile for header
    header = ''
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line == '\n': continue
            if stripped_line.startswith('#'):
                header += stripped_line[1:]
                continue
            break

    return header

def csv_get_delimiter(path, delimiters = [',', ';', '\t', ' '],
    minprobesize = 3, maxprobesize = 100):
    """Get delimiter from CSV file.

    Args:
        path (string): file path to CSV file.
        delimiters (list, optional): list of strings containing
            delimiter candidates to search for.
        minprobesize (integer, optional): minimum number of non comment,
            non empty lines used to detect csv delimiter.
        maxprobesize (integer, optional): maximum number of non comment,
            non empty lines used to detect csv delimiter.

    Returns:
        String containing delimiter of CSV file or False if delimiter
        could not be detected.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not determine delimiter: file '%s' does not exist."
        % (path))

    delimiter = None
    with open(path, 'rb') as csvfile:
        lines = 1
        probe = ''
        for line in csvfile:

            # check termination criteria
            if not delimiter == None: break
            if lines > maxprobesize: break

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line.startswith('#'): continue
            if stripped_line == '\n': continue

            # increase probe
            probe += line
            lines += 1

            # try to detect delimiter of probe
            if lines > minprobesize:
                try: dialect = csv.Sniffer().sniff(probe, delimiters)
                except: continue
                delimiter = dialect.delimiter

    if delimiter == None:
        return nemoa.log('warning', """could not determine delimiter
            of csv file '%s'!""" % (path))

    return delimiter

def csv_get_labels(path, delimiter = None):
    """Get (column) labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delimiter (string, optional): string containing CSV delimiter.

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV file.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not get csv labels: file '%s' does not exist." % (path))

    # get delimiter
    if not delimiter: delimiter = csv_get_delimiter(path)
    if not delimiter: return nemoa.log('error',
        'could not get column labels: unknown delimiter.')

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line.startswith('#'): continue
            if stripped_line == '\n': continue

            if first == None:
                first = line
            elif second == None:
                second = line
                break
    if first == None or second == None:
        return nemoa.log('error', """could not get column labels:
            file '%s' is not valid.""" % (path))

    if first.count(delimiter) == second.count(delimiter):
        csvtype = 'default'
    elif first.count(delimiter) == second.count(delimiter) - 1:
        csvtype == 'r-table'
    else:
        return nemoa.log('error', """could not get column labels:
            file '%s' is not valid.""" % (path))

    col_labels = first.split(delimiter)
    col_labels = [col.strip('\"\'\n\r\t ') for col in col_labels]

    if csvtype == 'default': return col_labels
    if csvtype == 'r_table': return ['label'] + col_labels
    return []

def csv_get_rowlabelcol(path, delimiter = None):
    """Get column id for column containing row labels from CSV file.

    Args:
        path (string): file path to CSV file.
        delimiter (string, optional): string containing CSV delimiter.

    Returns:
        Integer containing first index of CSV data column containing
        strings.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        """could not get csv row label column id:
        file '%s' does not exist.""" % (path))

    # get delimiter
    if not delimiter: delimiter = csv_get_delimiter(path)
    if not delimiter: return nemoa.log('error',
        "could not get csv row label column id: unknown delimiter.")

    # get first and second non comment and non empty line
    first = None
    second = None
    with open(path, 'r') as csvfile:
        for line in csvfile:

            # check exclusion criteria
            stripped_line = line.lstrip(' ')
            if stripped_line.startswith('#'): continue
            if stripped_line == '\n': continue

            if first == None:
                first = line
            elif second == None:
                second = line
                break
    if first == None or second == None:
        return nemoa.log('error', """could not get csv row label column
            id: file '%s' is not valid.""" % (path))

    col_values = second.split(delimiter)
    col_values = [col.strip('\"\' \n') for col in col_values]

    for col_id, value in enumerate(col_values):
        try:
            float(value)
        except ValueError:
            return col_id

    return False

def csv_get_data(path, delimiter = None, labels = None,
    usecols = None, rowlabelcol = None):
    """Import data from CSV file.

    Args:
        path (string): file path to CSV file.
        delimiter (string, optional): string containing CSV delimiter.
            If not given, the CSV delimiter is detected from CSV file.
        labels (list, optional): list of strings containing CSV labels.
            If not given, the CSV labels are detected from CSV file.
        usecols (tuple of integers, optional): indices if columns
            which are imported from CSV file. If not given, all columns
            are used.
        rowlabelcol (int, optional): index of column that contains
            rowlabels. If not given, first column of strings is used.

    Returns:
        Numpy record array containing data from CSV file or False if
        data could not be imported.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not get csv data: file '%s' does not exist." % (path))

    # get delimiter
    if not delimiter: delimiter = csv_get_delimiter(path)
    if not delimiter: return nemoa.log('error',
        "could not get data from csv file: unknown delimiter.")

    # get labels
    if labels:
        if not usecols: return nemoa.log('error',
            "could not get data from csv file: usecols are not given.")
    else:
        labels = csv_get_labels(path, delimiter = delimiter)
        usecols = tuple(range(len(labels)))
    if not labels: return nemoa.log('error',
        "could not get data from csv file: unknown labels.")

    # get row label coumn id
    if rowlabelcol == None:
        rowlabelcol = csv_get_rowlabelcol(path, delimiter = delimiter)

    # get datatype
    if rowlabelcol == None:
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
            if not col == rowlabelcol)
        labels = ('label',) + tuple(col for col in labels
            if not col == rowlabelcollabel)
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
            if stripped_line == '\n':
                skiprows += 1
                continue
            break

    try:
        # Todo: use genfromtxt to allow missing values
        data = numpy.loadtxt(path, skiprows = skiprows,
            delimiter = delimiter, usecols = usecols, dtype = dtype)
    except:
        return nemoa.log('error', """could not import data from CSV
            file.""")

    return data

def csv_save_data(path, data, header = None, labels = None,
    delimiter = ','):

    if isinstance(header, str):
        header = '# %s\n\n' % (header.replace('\n', '\n# '))
        if isinstance(labels, list):
            header += delimiter.join(labels)
    elif isinstance(labels, list):
        header = delimiter.join(labels)

    fmt = delimiter.join(['%s'] + ['%10.10f'] * (len(data[0]) - 1))
    numpy.savetxt(path, data, fmt = fmt, header = header, comments = '')
    return path

def csv_dump(dic, path, **kwargs):
    header = dic['header']
    data = dic['table']
    labels = data.dtype.names
    return csv_save_data(path, data, header, labels, **kwargs)
