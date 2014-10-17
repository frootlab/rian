# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import nemoa
import numpy
import re

def csv_get_col_labels(file, delim = None, type = None):
    """Return list with column labels (first row) from csv file."""

    # get delimiter
    if not delim: delim = csv_get_delimiter(file)
    if not delim: return nemoa.log('error',
        'could not get column labels: unknown delimiter!')

    # get first line
    with open(file, 'r') as f: firstline = f.readline()

    # parse first line depending on type
    regEx = r'''\s*([^DELIM"']+?|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*(?:DELIM|$)'''.replace('DELIM', re.escape(delim))
    r = re.compile(regEx, re.VERBOSE)
    if type == None: return r.findall(firstline)
    elif type == 'r-table': return [label.strip('\"\'')
        for label in ['label'] + r.findall(firstline)]
    return []

def csv_get_delimiter(file, delimiters = [',', ';', '\t', ' ']):
    """Return estimated delimiter of csv file."""

    found = False
    lines = 10
    while not found and lines <= 50:
        with open(file, 'rb') as csvfile:
            probe = csvfile.read(len(csvfile.readline()) * lines)
            try:
                dialect = csv.Sniffer().sniff(probe, delimiters)
                found = True
            except:
                lines += 10
    if found: return dialect.delimiter
    return nemoa.log('warning',
        "could not determine delimiter of .csv file '%s'!" % (file))

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
