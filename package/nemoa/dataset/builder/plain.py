# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

def types():
    """Get supported plain dataset types for dataset building."""

    return {
        'rules': 'Simulated data with manipulation rules',
        'system': 'Simulated data using system',
        'model': 'Real data using model'
    }

def build(type = None, *args, **kwargs):
    """Build plain dataset from building parameters."""

    if type == 'rules': return Rules(**kwargs).build()

    return False

class Rules:
    """Build rule based manipulated dataset from building parameters."""

    settings = None
    default = {
        'name': 'data',
        'columns': ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
        'rules': {
            'o1': '%i1% + %i2%',
            'o2': '%i3% + %i4%' },
        'normalize': 'gauss',
        'rowlabel': 'r%i',
        'samples': 100,
        'abin': 0.0,
        'sdev': 1.0 }

    def __init__(self, **kwargs):
        self.settings = self.default.copy()
        nemoa.common.dict_merge(kwargs, self.settings)

    def build(self):

        # create dataset configuration
        columns = self.settings['columns']
        name = self.settings['name']
        rowsize = self.settings['samples']
        config = {
            'name': name,
            'type': 'base.Dataset',
            'columns': tuple(),
            'colmapping': {},
            'colfilter': { '*': ['*:*'] },
            'rowfilter': { '*': ['*:*'], name: [name + ':*'] } }
        for column in columns:
            config['colmapping'][column] = column
            config['columns'] += (('', column), )
        config['table'] = {name: config.copy()}
        config['table'][name]['fraction'] = 1.

        # create array with random entries
        dtype = numpy.dtype({
            'names': ('label',) + tuple(columns),
            'formats': ('<U12',) + ('<f8',) * len(columns) })
        data = numpy.recarray((rowsize, ), dtype)
        rowlabels = [self.settings['rowlabel'] % (i + 1) \
            for i in range(rowsize)]
        data['label'] = rowlabels
        for column in columns:

            if self.settings['sdev'] > 0.:
                gauss = numpy.random.normal(0, self.settings['sdev'],
                    size = rowsize)
            else:
                gauss = 0.

            if self.settings['abin'] > 0.:
                bernoulli = self.settings['abin'] * 2.0 \
                    * numpy.random.randint(2, size = rowsize) - 0.5
            else:
                bernoulli = 0.

            data[column] = gauss + bernoulli

        # manipulate array data
        rules = self.settings['rules'].copy()
        for key, val in rules.iteritems():
            if not key in columns: continue
            for column in columns:
                val = val.replace(
                    '%' + column + '%', "data['%s']" % (column))
            rules[key] = val
        for key, val in rules.iteritems():
            try: column = eval(val)
            except:
                nemoa.log('warning', 'could not interpret "%s".'
                    % (self.settings['rules'][key]))
                continue
            data[key] = column

        # normalize data (gauss)
        for column in columns:
            data[column] = (data[column] - data[column].mean()) \
                / data[column].std()

        return { 'config': config, 'tables': { name: data } }
