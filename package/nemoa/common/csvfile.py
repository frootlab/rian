# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import csv
import nemoa
import numpy
import re
import os

def csv_get_col_labels(file, delim = None, type = None):
    """Return list with column labels (first row) from csv file."""

    # get delimiter
    if not delim: delim = csv_get_delimiter(file)
    if not delim: return nemoa.log('error',
        'could not get column labels: unknown delimiter!')

    # get first line
    with open(file, 'r') as f: firstline = f.readline()

    # parse first line depending on type
    reg_ex = r'''\s*([^DELIM"']+?|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*(?:DELIM|$)'''.replace('DELIM', re.escape(delim))
    r = re.compile(reg_ex, re.VERBOSE)
    if type == None: return r.findall(firstline)
    elif type == 'r-table': return [label.strip('\"\'')
        for label in ['label'] + r.findall(firstline)]
    return []

def csv_get_delimiter(path, delimiters = [',', ';', '\t', ' '],
    minprobesize = 3, maxprobesize = 100):
    """Get delimiter of csv file.

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
