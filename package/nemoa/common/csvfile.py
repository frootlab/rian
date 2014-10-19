# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import nemoa
import numpy
import os

def csv_get_col_labels(path, delimiter = None):
    """Get labels from CSV file.

    Returns:
        List of strings containing column labels from first non comment,
        non empty line from CSV file.

    """

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not determine column labels: file '%s' does not exist."
        % (path))

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
    col_labels = [col.strip('\"\' \n') for col in col_labels]

    if csvtype == 'default': return col_labels
    if csvtype == 'r_table': return ['label'] + col_labels
    return []

def csv_get_delimiter(path, delimiters = [',', ';', '\t', ' '],
    minprobesize = 3, maxprobesize = 100):
    """Get delimiter from CSV file.

    Args:
        path (string): file path to csv file.
        delimiters (list, optional): list of strings containing
            delimiter candidates to search for.
        minprobesize (integer, optional): minimum number of non comment,
            non empty lines used to detect csv delimiter.
        maxprobesize (integer, optional): maximum number of non comment,
            non empty lines used to detect csv delimiter.

    Returns:
        String containing delimiter of csv file or False if delimiter
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

def csv_get_data(path, delimiter = None, labels = None,
    rowlabels = None, usecols = None):
    """Get data from CSV file."""

    # check file
    if not os.path.isfile(path): return nemoa.log('error',
        "could not get data from csv file: file '%s' does not exist."
        % (path))

    # get delimiter
    if not delimiter: delimiter = csv_get_delimiter(path)
    if not delimiter: return nemoa.log('error',
        "could not get data from csv file: unknown delimiter.")

    # get labels
    if not labels:
        labels = csv_get_col_labels(path, delimiter = delimiter)
        usecols = None
    if not labels: return nemoa.log('error',
        "could not get data from csv file: unknown labels.")

    # get datatype
    if rowlabels:
        formats = ('<f8',) * len(labels)
    else:
        if isinstance(usecols, tuple):
            usecols = (0,) + usecols
        labels = ('label',) + labels
        formats = ('<U12',) + ('<f8',) * len(labels)
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
        data = numpy.loadtxt(path, skiprows = skiprows,
            delimiter = delimiter, usecols = usecols, dtype = dtype)
    except:
        return nemoa.log('error', 'could not import data from file.')

    return data

def csv_save_data(path, data, cols = None, comment = None,
    delimiter = ',', **kwargs):

    header = None
    if isinstance(comment, str):
        header = '# %s\n\n' % (comment.replace('\n', '\n# '))
    if isinstance(cols, list):
        if header == None:
            header = delimiter.join(cols)
        else:
            header += delimiter.join(cols)

    fmt = delimiter.join(['%s'] + ['%10.10f'] * (len(data[0]) - 1))
    numpy.savetxt(path, data, fmt = fmt, header = header,
        comments = '', **kwargs)
    return True
