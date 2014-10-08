# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import copy
import csv
import nemoa
import numpy
import os
import re
import scipy.cluster.vq

class Dataset:

    _config = None
    _data = None

    def __init__(self, config = {}):
        """Set configuration of dataset from dictionary."""
        self._config = config.copy()
        self._data = {}

    def _is_empty(self):
        """Return true if dataset is empty."""
        return not 'name' in self._config or not self._config['name']

    def _is_binary(self):
        """Test if dataset contains only binary data.

        Returns:
            Boolean value which is True if dataset contains only
            binary values.

        """

        data = self.data()
        binary = ((data == data.astype(bool)).sum() == data.size)

        if not binary: return nemoa.log('error',
            'The dataset does not contain binary data!')

        return True

    def _eval_normalization(self, algorithm = 'gauss', **kwargs):
        """Test dataset for normalization.

        Args:
            algorithm: name of distribution to test for normalization
                'gauss': normalization of gauss distribution

        """

        nemoa.log("""test dataset for normalization assuming
            distribution '%s'""" % (algorithm))

        if algorithm.lower() == 'gauss':
            return self._eval_normalization_gauss(**kwargs)

        return False

    def _eval_normalization_gauss(self, size = 100000,
        max_diff_mean = 0.05, max_diff_sdev = 0.05):
        """Test if dataset contains gauss normalized data.

        Args:
            size (int, optional): number of samples used to calculate
                mean of absolute values and standard deviation
            max_diff_mean (float, optional): allowed maximum difference
                to zero for mean value
            max_diff_sdev (float, optional): allowed maximum difference
                to one for standard deviation

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The mean value over a given number of random samples
                has a distance to zero which is lower than max_diff_mean
            (2) The standard deviation over a given number of random
                samples has a distance to one zero which is lower than
                max_diff_sdev

        """

        data = self.data(size) # get numpy array with data

        # test mean value
        mean = data.mean()
        diff_mean = numpy.abs(0. - mean)
        if diff_mean > max_diff_mean:
            return nemoa.log('error',
                """dataset does not contain gauss normalized data:
                mean value is %.3f!""" % (mean))

        # test standard deviation
        sdev = data.std()
        diff_sdev = numpy.abs(1. - sdev)
        if diff_sdev > max_diff_sdev:
            return nemoa.log('error',
                """dataset does not contain gauss normalized data:
                standard deviation is %.3f!""" % (sdev))

        return True

    def _is_configured(self):
        """Return true if dataset is configured."""
        return len(self._data.keys()) > 0

    def configure(self, network, cache_enable = False, **kwargs):
        """Configure dataset to a given network.

        Args:
            network (object): nemoa network instance
            cache_enable (bool, optional): enable caching

        """

        nemoa.log("configure dataset '%s' to network '%s'" % \
            (self._config['name'], network.get('name')))
        nemoa.log('set', indent = '+1')

        # load data from cachefile if caching is activated
        if cache_enable:
            cache_file = self._search_cache_file(network)

            # load data from cachefile
            try:
                copy = nemoa.dataset.load(cache_file)
                nemoa.log("loading data from cachefile: '%s'"
                    % (cache_file))
                self.set('copy', **copy)
                if 'preprocessing' in self._config.keys():
                    self.preprocess(**self._config['preprocessing'])
                nemoa.log('set', indent = '-1')
            except:
                cache_file = self._create_cache_file(network)

        # create table with one record for every single dataset file
        if not 'table' in self._config:
            conf = self._config.copy()
            self._config['table'] = {}
            self._config['table'][self._config['name']] = conf
            self._config['table'][self._config['name']]['fraction'] = 1.

        # Annotation

        # get network node labels, grouped by layers
        network_layers = network.get('layers', visible = True)

        # convert network node labels to common format
        nemoa.log('search network nodes in dataset sources')
        conv_net_layers = {}
        conv_net_layers_lost = {}
        conv_net_nodes = []
        conv_net_nodes_lost = []
        net_label_format = network._config['label_format']
        for layer in network_layers:
            net_layer_node_names = \
                network.get('nodes', layer = layer)
            net_layer_node_labels = []
            for node in net_layer_node_names:
                net_layer_node_labels.append(
                    network.get('node', node)['label'])
            conv_net_layers[layer], conv_net_layers_lost[layer] = \
                nemoa.dataset.annotation.convert(
                net_layer_node_labels, input = net_label_format)
            conv_net_nodes += conv_net_layers[layer]
            conv_net_nodes_lost += conv_net_layers_lost[layer]

        # notify if any network node labels could not be converted
        if conv_net_nodes_lost:
            nemoa.log("""%s of %s network nodes could not
                be converted! (see logfile)"""
                % (len(conv_net_nodes_lost), len(conv_net_nodes)))
            # TODO: get original node labels for log file
            nemoa.log('logfile', nemoa.common.str_to_list(
                conv_net_nodes_lost))

        # get columns from dataset files and convert to common format
        col_labels = {}
        nemoa.log('configure data sources')
        nemoa.log('set', indent = '+1')
        for src in self._config['table']:
            nemoa.log("configure '%s'" % (src))
            src_cnf = self._config['table'][src]

            # get column labels from csv-file
            csv_type = src_cnf['source']['csvtype'].strip().lower() \
                if 'csvtype' in src_cnf['source'] else None
            orig_col_labels = nemoa.common.csv_get_col_labels(
                src_cnf['source']['file'], type = csv_type)
            if not orig_col_labels: continue

            # set annotation format
            format = src_cnf['source']['columns'] \
                if 'columns' in src_cnf['source'] else 'generic:string'

            # convert column labes
            columns_conv, columns_conv_lost = \
                nemoa.dataset.annotation.convert(
                orig_col_labels, input = format)

            # notify if any dataset columns could not be converted
            if columns_conv_lost:
                nemoa.log('warning', """%i of %i dataset columns
                    could not be converted! (see logfile)""" %
                    (len(columns_conv_lost), len(columns_conv)))
                nemoa.log('logfile', ", ".join([columns_conv[i] \
                    for i in columns_conv_lost]))

            # search converted nodes in converted columns
            num_lost = 0
            num_all = 0
            nodes_lost = {}
            for group in network_layers:
                nodes_conv_lost = \
                    [val for val in conv_net_layers[group] \
                    if val not in columns_conv]
                num_all += len(conv_net_layers[group])

                if not nodes_conv_lost: continue
                num_lost += len(nodes_conv_lost)

                # get lost nodes
                nodes_lost[group] = []
                for val in nodes_conv_lost:
                    node_lost_id = conv_net_layers[group].index(val)
                    node_lost = network.get('nodes',
                        type = group)[node_lost_id]
                    node_label = network.get('node',
                        node_lost)['label']
                    nodes_lost[group].append(node_label)

            # notify if any network nodes could not be found
            if num_lost:
                nemoa.log('warning', """%i of %i network nodes
                    could not be found in dataset source!
                    (see logfile)""" % (num_lost, num_all))
                for group in nodes_lost:
                    nemoa.log('logfile',
                        'missing nodes (group %s): ' % (group)
                        + ', '.join(nodes_lost[group]))

            # prepare dictionary for column source ids
            col_labels[src] = {
                'conv': columns_conv,
                'usecols': (),
                'notusecols': columns_conv_lost }

        nemoa.log('set', indent = '-1')

        # intersect converted dataset column labels
        inter_col_labels = col_labels[col_labels.keys()[0]]['conv']
        for src in col_labels:
            list = col_labels[src]['conv']
            black_list = [list[i] for i in col_labels[src]['notusecols']]
            inter_col_labels = [val for val in inter_col_labels \
                if val in list and not val in black_list]

        # search network nodes in dataset columns
        self._config['columns'] = ()
        for group in network_layers:
            found = 0

            for id, col in enumerate(conv_net_layers[group]):
                if not col in inter_col_labels: continue
                found += 1

                # add column (use network label and layer)
                node_name = network.get('nodes', layer = group)[id]
                node_label = network.get('node', node_name)['label']
                self._config['columns'] += ((group, node_label), )

                for src in col_labels:
                    col_labels[src]['usecols'] \
                        += (col_labels[src]['conv'].index(col), )

            if not found:
                nemoa.log('error', """no node from network layer '%s'
                    could be found in dataset source!""" % (group))
                nemoa.log('set', indent = '-1')
                return False

        # update source file config
        for src in col_labels:
            self._config['table'][src]['source']['usecols'] \
                = col_labels[src]['usecols']

        # Column & Row Filters

        # add column filters and partitions from network node layers
        self._config['col_filter'] = {'*': ['*:*']}
        self._config['col_partitions'] = {'groups': []}
        for layer in network_layers:
            self._config['col_filter'][layer] = [layer + ':*']
            self._config['col_partitions']['groups'].append(layer)

        # add row filters and partitions from sources
        self._config['row_filter'] = {'*': ['*:*']}
        self._config['row_partitions'] = {'source': []}
        for source in self._config['table']:
            self._config['row_filter'][source] = [source + ':*']
            self._config['row_partitions']['source'].append(source)

        # import data from .csv-files into numpy arrays

        # import data from sources
        nemoa.log('import data from sources')
        nemoa.log('set', indent = '+1')
        self._data = {}
        for src in self._config['table']:
            self._data[src] = {
                'fraction': self._config['table'][src]['fraction'],
                'array': self._csv_get_data(src) }
        nemoa.log('set', indent = '-1')

        # save cachefile
        if cache_enable:
            nemoa.log("save cachefile: '%s'" % (cache_file))
            nemoa.dataset.save(self, cache_file)

        # preprocess data
        if 'preprocessing' in self._config.keys():
            self.preprocess(**self._config['preprocessing'])

        nemoa.log('set', indent = '-1')
        return True

    def preprocess(self, **kwargs):
        """Data preprocessing.

        Stratification, normalization and transformation of data.

        Args:
            stratify: see method self._stratify()
            normalize: see method self._normalize()
            transform: see method self._transform()

        """

        nemoa.log('preprocessing data')
        nemoa.log('set', indent = '+1')

        if 'stratify' in kwargs.keys():
            self._stratify(kwargs['stratify'])

        if 'normalize' in kwargs.keys():
            self._normalize(kwargs['normalize'])

        if 'transform' in kwargs.keys():
            self._transform(kwargs['transform'])

        nemoa.log('set', indent = '-1')

        return True

    def _stratify(self, algorithm = 'auto'):
        """Stratify data.

        Args:
            algorithm (str): name of algorithm used for stratification
                'none':
                    probabilities of sources are
                    number of all samples / number of samples in source
                'auto':
                    probabilities of sources are hierarchical distributed
                    as defined in the configuration
                'equal':
                    probabilities of sources are
                    1 / number of sources

        """

        nemoa.log("stratify data using '%s'" % (algorithm))

        if algorithm.lower() in ['none']:
            allSize = 0
            for src in self._data:
                allSize += self._data[src]['array'].shape[0]
            for src in self._data: self._data[src]['fraction'] = \
                float(allSize) / float(self._data[src]['array'].shape[0])
            return True
        if algorithm.lower() in ['auto']: return True
        if algorithm.lower() in ['equal']:
            frac = 1. / float(len(self._data))
            for src in self._data: self._data[src]['fraction'] = frac
            return True
        return False

    def _normalize(self, algorithm = 'gauss', **kwargs):
        """Normalize data

        Args:
            algorithm: name of distribution to normalize
                'gauss': normalization of gauss distribution

        """

        nemoa.log("normalize data using '%s'" % (algorithm))

        if algorithm.lower() == 'gauss':
            return self._normalize_gauss(**kwargs)

        return False

    def _normalize_gauss(self, size = 100000):
        """Gauss normalization of dataset."""

        # get data for calculation of mean and standard deviation
        # for single source datasets take all data
        # for multi source datasets take a big bunch of stratified data
        if len(self._data.keys()) == 1:
            source = self._data.keys()[0]
            data = self._get_data_from_source(source = source)
        else:
            data = self.data(size = size, output = 'recarray')

        # iterative normalize sources
        for source in self._data.keys():
            source_array = self._data[source]['array']
            if source_array == None:
                continue
            # iterative normalize columns (recarray)
            for col in source_array.dtype.names[1:]:
                mean = data[col].mean()
                sdev = data[col].std()
                self._data[source]['array'][col] = \
                    (source_array[col] - mean) / sdev
        return True

    def _transform(self, algorithm = 'system', system = None,
        mapping = None, **kwargs):
        """Transform dataset.

        Args:
            algorithm (str): name of algorithm used for data
                transformation
                'system':
                    Transform data using nemoa system instance
                'gaussToBinary':
                    Transform Gauss distributed values to binary values
                    in {0, 1}
                'gaussToWeight':
                    Transform Gauss distributed values to weights
                    in [0, 1]
                'gaussToDistance': ??
                    Transform Gauss distributed values to distances
                    in [0, 1]
            system: nemoa system instance (nemoa object root class
                'system') used for model based transformation of data
            mapping: ...

        """

        if not isinstance(algorithm, str): return False

        # system based data transformation
        if algorithm.lower() == 'system':
            if not nemoa.type.is_system(system):
                return nemoa.log('error', """could not transform data
                    using system: invalid system.""")
            nemoa.log("transform data using system '%s'"
                % (system.get('name')))
            nemoa.log('set', indent = '+1')

            if mapping == None: mapping = system.mapping()

            source_columns = system.get('units', layer = mapping[0])
            target_columns = system.get('units', layer = mapping[-1])

            self._set_col_labels(source_columns)

            for src in self._data:

                # get data, mapping and transformation function
                data = self._data[src]['array']
                data_array = data[source_columns].view('<f8').reshape(
                    data.size, len(source_columns))
                if mapping == None: mapping = system.mapping()
                if not 'func' in kwargs: func = 'expect'
                else: func = kwargs['func']

                # transform data
                if func == 'expect':
                    trans_array = system._eval_units_expect(
                        data_array, mapping)
                elif func == 'value':
                    trans_array = system._eval_units_values(
                        data_array, mapping)
                elif func == 'sample':
                    trans_array = system._eval_units_samples(
                        data_array, mapping)

                # create empty record array
                num_rows = self._data[src]['array']['label'].size
                col_names = ('label',) + tuple(target_columns)
                col_formats = ('<U12',) + tuple(['<f8' \
                    for x in target_columns])
                new_rec_array = numpy.recarray((num_rows,),
                    dtype = zip(col_names, col_formats))

                # set values in record array
                new_rec_array['label'] = \
                    self._data[src]['array']['label']
                for colID, colName in \
                    enumerate(new_rec_array.dtype.names[1:]):

                    # update source data columns
                    new_rec_array[colName] = \
                        (trans_array[:, colID]).astype(float)

                # set record array
                self._data[src]['array'] = new_rec_array

            self._set_col_labels(target_columns)
            nemoa.log('set', indent = '-1')
            return True

        # gauss to binary data transformation
        elif algorithm.lower() in ['gausstobinary', 'binary']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._data:
                # update source per column (recarray)
                for colName in self._data[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._data[src]['array'][colName] = \
                        (self._data[src]['array'][colName] > 0.
                        ).astype(float)
            return True

        # gauss to weight in [0, 1] data transformation
        elif algorithm.lower() in ['gausstoweight', 'weight']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._data:
                # update source per column (recarray)
                for colName in self._data[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._data[src]['array'][colName] = \
                        (2. / (1. + numpy.exp(-1. * \
                        self._data[src]['array'][colName] ** 2))
                        ).astype(float)
            return True

        # gauss to distance data transformation
        # ????
        elif algorithm.lower() in ['gausstodistance', 'distance']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._data:
                # update source per column (recarray)
                for colName in self._data[src]['array'].dtype.names[1:]:
                    self._data[src]['array'][colName] = \
                        (1. - (2. / (1. + numpy.exp(-1. * \
                        self._data[src]['array'][colName] ** 2)))
                        ).astype(float)
            return True

        return nemoa.log('error', """could not transform data:
            unknown algorithm '%s'!""" % (algorithm))

    #def value(self, row = None, col = None):
        #"""Return single value from dataset."""
        #ret_val = self.data(cols = ([col]), output = 'list,array')
        #return ret_val[1][ret_val[0].index(row)]

    def data(self, size = 0, rows = '*', cols = '*',
        corruption = (None, 0.), output = 'array'):
        """Return a given number of stratified samples.

        Args:
            size: Size of data (Number of samples)
                default: value 0 returns all samples unstratified
            rows: string describing row filter (row groups)
                default: value '*' selects all rows
            cols: string describing column filter (column group)
                default: value '*' selects all columns
            corruption: 2-tuple describing artificial data corruption
                first entry of tuple: type of corruption / noise model
                    'none': no corruption
                    'mask': Masking Noise
                        A fraction of every sample is forced to zero
                    'gauss': Gaussian Noise
                        Additive isotropic Gaussian noise
                    'salt': Salt-and-pepper noise
                        A fraction of every sample is forced to min or max
                        with equal possibility
                    default: Value None equals to 'no'
                second entry of tuple: corruption factor
                    float in interval [0, 1] describing the strengt
                    of the corruption. The influence of the parameter
                    depends on the corruption type
                    default: Value 0.5
            fmt: tuple of strings describing data output. Supported strings:
                'array': numpy array with data
                'recarray': numpy record array with data
                'cols': list of column names
                'rows': list of row names
                default: 'array'

        """

        # check Configuration and Keyword Arguments
        if not self._is_configured(): return nemoa.log('error',
            'could not get data: dataset is not yet configured!')
        if not isinstance(size, int) or size < 0: return nemoa.log(
            'error', 'could not get data: invalid argument size!')

        # stratify and filter data
        src_stack = ()
        for source in self._data.keys():
            if size > 0: src_data = self._get_data_from_source(source,
                size = size + 1, rows = rows)
            else: src_data = self._get_data_from_source(source, rows = rows)
            if src_data == False or src_data.size == 0: continue
            src_stack += (src_data, )
        if not src_stack: return nemoa.log('error',
            'could not get data: no valid data sources found!')
        data = numpy.concatenate(src_stack)

        # (optional) Shuffle data and correct size
        if size:
            numpy.random.shuffle(data)
            data = data[:size]

        # Format data
        if isinstance(cols, str): fmtData = self._format(
            data, cols = self._get_cols(cols), output = output)
        elif isinstance(cols, list): fmtData = self._format(
            data, cols = cols, output = output)
        elif isinstance(cols, tuple): fmtData = tuple(
            [self._format(data, cols = self._get_cols(grp),
            output = output) for grp in cols])
        else: return nemoa.log('error', """could not get data:
            invalid argument for columns!""")

        # Corrupt data (optional)
        return self._corrupt(fmtData, \
            type = corruption[0], factor = corruption[1])

    def _get_data_from_source(self, source, size = 0, rows = '*'):
        """Return numpy recarray with data from a single source.

        Args:
            source: name of data source to get data from
            size: number of random choosen samples to return
                default: value 0 returns all samples of given source
            rows: string describing a row filter using wildcards
                default: value '*' selects all rows

        """

        # Check source
        if not isinstance(source, str) \
            or not source in self._data \
            or not isinstance(self._data[source]['array'], numpy.ndarray): \
            return nemoa.log('error', """could not retrieve data:
            invalid source: '%s'!""" % (source))

        # check row Filter
        if not rows in self._config['row_filter']: return nemoa.log('error',
            "could not retrieve data: invalid row filter: '%s'!" % (rows))

        # apply row filter
        if rows == '*' or source + ':*' in self._config['row_filter'][rows]:
            src_array = self._data[source]['array']
        else:
            row_filter = self._config['row_filter'][rows]
            row_filter_filtered = [
                row.split(':')[1] for row in row_filter
                if row.split(':')[0] in [source, '*']]
            row_select = numpy.asarray([
                rowid for rowid, row in enumerate(
                self._data[source]['array']['label'])
                if row in row_filter_filtered])
            if row_select.size == 0: return row_select
            src_array = numpy.take(self._data[source]['array'],
                row_select)

        # stratify and return data as numpy record array
        if size == 0 or size == None: return src_array
        src_frac = self._data[source]['fraction']
        row_select = numpy.random.randint(src_array.size,
            size = round(src_frac * size))
        return numpy.take(src_array, row_select)

    def _corrupt(self, data, type = None, factor = 0.5):
        """Corrupt given data.

        Args:
            data: numpy array containing data
            type (str): algorithm for corruption
                'mask': Masking Noise
                    A fraction of every sample is forced to zero
                'gauss': Gaussian Noise
                    Additive isotropic Gaussian noise
                'salt': Salt-and-pepper noise
                    A fraction of every sample is forced to min or max
                    with equal possibility
            factor (float, optional): strengt of the corruption
                The influence of the parameter depends on the
                type of the corruption

        Returns:
            Numpy array with (partly) corrupted data. The shape is
            identical to the shape of the given data.

        """

        if type in [None, 'none']: return data
        elif type == 'mask': return data * numpy.random.binomial(
            size = data.shape, n = 1, p = 1. - factor)
        elif type == 'gauss': return data + numpy.random.normal(
            size = data.shape, loc = 0., scale = factor)
        # TODO: implement salt and pepper noise
        #elif type == 'salt': return
        else: return nemoa.log('error',
            "unkown data corruption type '%s'!" % (type))

    def _format(self, data, cols = '*', output = 'array'):
        """Return data in given format.

        Args:
            cols: name of column group
                default: value '*' does not filter columns
            output: ...

        """

        # check columns
        if cols == '*': cols = self._get_cols()
        elif not len(cols) == len(set(cols)):
            return nemoa.log('error', """could not retrieve data:
                columns are not unique!""")
        elif [c for c in cols if c not in self._get_cols()]:
            return nemoa.log('error', """could not retrieve data:
                unknown columns!""")

        # check format
        if isinstance(output, str): fmt_tuple = (output, )
        elif isinstance(output, tuple): fmt_tuple = output
        else: return nemoa.log('error',
            "could not retrieve data: invalid 'format' argument!")

        # format data
        ret_tuple = ()
        for fmt_str in fmt_tuple:
            if fmt_str == 'array': ret_tuple += (
                data[cols].view('<f8').reshape(data.size, len(cols)), )
            elif fmt_str == 'recarray': ret_tuple += (
                data[['label'] + cols], )
            elif fmt_str == 'cols': ret_tuple += (
                [col.split(':')[1] for col in cols], )
            elif fmt_str in ['rows', 'list']: ret_tuple += (
                data['label'].tolist(), )
        if isinstance(output, str): return ret_tuple[0]
        return ret_tuple

    def _set_col_labels(self, labels):
        """Set column labels from list of strings."""
        self._config['columns'] = \
            tuple([col.split(':') for col in labels])
        return True

    def _set_col_filter(self, **kwargs):
        columns = self._get_cols()

        for group in kwargs.keys():
            group_columns = kwargs[group]

            valid = True
            for column in group_columns:
                if not column in columns:
                    valid = False
                    break

            if not valid: continue
            self._config['col_filter'][group] = columns

        return True

    #def addRowFilter(self, name, filter):
        ## create unique name for filter
        #filterName = name
        #i = 1
        #while filterName in self._config['row_filter']:
            #i += 1
            #filterName = '%s.%i' % (name, i)

        ## TODO: check filter
        #self._config['row_filter'][filterName] = filter
        #return filterName

    #def delRowFilter(self, name):
        #if name in self._config['row_filter']:
            #del self._config['row_filter'][name]
            #return True
        #return False

    #def getRowFilter(self, name):
        #if not name in self._config['row_filter']:
            #nemoa.log('warning', "unknown row filter '" + name + "'!")
            #return []
        #return self._config['row_filter'][name]

    #def getRowFilterList(self):
        #return self._config['row_filter'].keys()

    #def addColFilter(self):
        #pass

    #def delColFilter(self, name):
        #if name in self._config['col_filter']:
            #del self._config['col_filter'][name]
            #return True
        #return False

    #def getColFilters(self):
        #return self._config['col_filter']

    #def addRowPartition(self, name, partition):
        #if name in self._config['row_partitions']:
            #nemoa.log('warning', "row partition '" + name + "' allready exists!")

        ## create unique name for partition
        #partitionName = name
        #i = 1
        #while partitionName in self._config['row_partitions']:
            #i += 1
            #partitionName = '%s.%i' % (name, i)

        #filterNames = []
        #for id, filter in enumerate(partition):
            #filterNames.append(
                #self.addRowFilter('%s.%i' % (name, id + 1), filter))

        #self._config['row_partitions'][partitionName] = filterNames
        #return partitionName

    #def delRowPartition(self, name):
        #pass

    #def getRowPartition(self, name):
        #if not name in self._config['row_partitions']:
            #nemoa.log('warning', "unknown row partition '" + name + "'!")
            #return []
        #return self._config['row_partitions'][name]

    #def getRowPartitionList(self):
        #return self._config['row_partitions'].keys()

    #def createRowPartition(self, algorithm = 'bcca', **params):
        #if algorithm == 'bcca':
            #partition = self.getBccaPartition(**params)
        #else:
            #nemoa.log('warning', "unknown partition function '%s'")

        ## add partition
        #return self.addRowPartition(algorithm, partition)

    #def getBccaPartition(self, **params):
        #rowLabels, data = self.data(output = 'list,array')
        #num_rows, numCols = data.shape

        ## check parameters
        #if 'groups' in params:
            #groups = params['groups']
        #else:
            #nemoa.log('warning', "parameter 'groups' is needed to create BCCA partition!")
            #return []

        ## get BCCA biclusters
        #biclusters = self.getBccaBiclusters(**params)

        ## get bicluster distances
        #distance = self.getBiclusterDistance(biclusters, **params)

        ## cluster samples using k-means
        #nemoa.log('cluster distances using k-means with k = %i' % (groups))
        #clusters = self.getClusters(algorithm = 'k-means', data = distance, k = groups)
        #cIDs = numpy.asarray(clusters)
        #partition = []
        #for cID in xrange(groups):
            #partition.append(numpy.where(cIDs == cID)[0].tolist())

        ## get labels
        #labeledPartition = []
        #for pID, c in enumerate(partition):
            #labels = []
            #for sID in c:
                #labels.append(rowLabels[sID])
            #labeledPartition.append(list(set(labels)))

        #return labeledPartition

    #def getClusters(self, algorithm = 'k-means', **params):
        #if algorithm == 'k-means':
            #return self.getKMeansClusters(**params)

        #nemoa.log('warning', "unsupported clustering algorithm '" + algorithm + "'!")
        #return None

    #def getKMeansClusters(self, data, k = 3):
        #return scipy.cluster.vq.vq(data, scipy.cluster.vq.kmeans(data, k)[0])[0]

    #def getBiclusters(self, algorithm = 'bcca', **params):
        #if algorithm == 'bcca':
            #return getBccaBiclusters(**params)

        #nemoa.log('warning', "unsupported biclustering algorithm '" + algorithm + "'!")
        #return None

    #def getBccaBiclusters(self, **params):
        #data = self.data(output = 'array')
        #num_rows, numCols = data.shape

        ## check params
        #if not 'threshold' in params:
            #nemoa.log("param 'threshold' is needed for BCCA Clustering!")
            #return []
        #if not ('minsize' in params or 'size' in params):
            #nemoa.log("param 'size' or 'minsize' is needed for BCCA Clustering!")
            #return []

        ## get params
        #threshold = params['threshold']
        #if 'minsize' in params:
            #minsize = params['minsize']
            #size = 0
        #else:
            #minsize = 3
            #size = params['size']

        ## start clustering
        #nemoa.log('detecting bi-correlation clusters')
        #startTime = time.time()

        #biclusters = []
        #for i in xrange(numCols - 1):
            #for j in xrange(i + 1, numCols):

                #npRowIDs = numpy.arange(num_rows)

                ## drop rows until corr(i, j) > sigma or too few rows are left
                #rowIDs = npRowIDs.tolist()
                #corr = numpy.corrcoef(data[:,i], data[:,j])[0, 1]

                #while (size and len(rowIDs) > size) or \
                    #(not size and len(rowIDs) > minsize and corr < threshold):
                    #rowCorr = numpy.zeros(len(rowIDs))

                    #for id in xrange(len(rowIDs)):
                        #mask = rowIDs[:id] + rowIDs[id:][1:]
                        #rowCorr[id] = numpy.corrcoef(data[mask, i], data[mask, j])[0, 1]

                    #rowMaxID = rowCorr.argmax()
                    #corr = rowCorr[rowMaxID]
                    #rowIDs.pop(rowMaxID)

                #if i == 0 and j == 1:
                    #elapsed = time.time() - startTime
                    #estimated = elapsed * numCols ** 2 / 2
                    #nemoa.log('estimated duration: %.1fs' % (estimated))

                #if corr < threshold:
                    #continue

                # expand remaining rows over columns
                #colIDs = [i, j]
                #for id in [id for id in xrange(numCols) if id not in colIDs]:
                    #if numpy.corrcoef(data[rowIDs, i], data[rowIDs, id])[0, 1] < threshold:
                        #continue
                    #if numpy.corrcoef(data[rowIDs, j], data[rowIDs, id])[0, 1] < threshold:
                        #continue
                    #colIDs.append(id)

                # append bicluster if not yet existing
                #bicluster = (list(set(rowIDs)), list(set(colIDs)))
                #if not bicluster in biclusters:
                    #biclusters.append(bicluster)

        ## info
        #if size:
            #nemoa.log('found %i biclusters with: correlation > %.2f, number of samples = %i' \
                #% (len(biclusters), threshold, size))
        #else:
            #nemoa.log('found %i biclusters with: correlation > %.2f, number of samples > %i' \
                #% (len(biclusters), threshold, minsize - 1))

        #return biclusters

    #def getBiclusterDistance(self, biclusters, **params):
        #if 'distance' in params:
            #type = params['distance']
        #else:
            #type = 'correlation'

        #if type == 'hamming':
            #return self.getBiclusterHammingDistance(biclusters)
        #elif type == 'correlation':
            #return self.getBiclusterCorrelationDistance(biclusters)

        #nemoa.log('warning', "   unknown distance type '" + type + "'!")
        #return None

    #def getBiclusterHammingDistance(self, biclusters):
        #data = self.data(output = 'array')
        #num_rows, numCols = data.shape

        ## create distance matrix using binary metric
        #distance = numpy.ones(shape = (num_rows, len(biclusters)))
        #for cID, (cRowIDs, cColIDs) in enumerate(biclusters):
            #distance[cRowIDs, cID] = 0

        #return distance

    #def getBiclusterCorrelationDistance(self, biclusters):
        ### EXPERIMENTAL!!
        #data = self.data(output = 'array')
        #num_rows, numCols = data.shape

        ## calculate differences in correlation
        #corrDiff = numpy.zeros(shape = (num_rows, len(biclusters)))
        #for cID, (cRowIDs, cColIDs) in enumerate(biclusters):

            ## calculate mean correlation within bicluster
            #cCorr = self.getMeanCorr(data[cRowIDs, :][:, cColIDs])

            ## calculate mean correlation by appending single rows
            #for rowID in xrange(num_rows):
                #corrDiff[rowID, cID] = cCorr - self.getMeanCorr(data[cRowIDs + [rowID], :][:, cColIDs])

        ## calculate distances of samples and clusters
        #distance = corrDiff
        ##dist = numpy.nan_to_num(corrDiff / (numpy.max(numpy.max(corrDiff, axis = 0), 0.000001)))
        ##dist = (dist > 0) * dist
        #return distance

    #def getMeanCorr(self, array, axis = 1):
        #if not axis:
            #array = array.T
        #cCorr = numpy.asarray([])
        #for i in xrange(array.shape[1] - 1):
            #for j in xrange(i + 1, array.shape[1]):
                #cCorr = numpy.append(cCorr, numpy.corrcoef(array[:, i], array[:, j])[0, 1])

        #return numpy.mean(cCorr)

    # TODO: move to nemoa.common
    def _csv_get_data(self, name):
        conf = self._config['table'][name]['source']
        file = conf['file']
        delim = conf['delimiter'] if 'delimiter' in conf \
            else nemoa.common.csv_get_delimiter(file)
        cols = conf['usecols']
        names = tuple(self._get_cols())
        formats = tuple(['<f8' for x in names])
        if not 'rows' in conf or conf['rows']:
            cols = (0,) + cols
            names = ('label',) + names
            formats = ('<U12',) + formats
        dtype = {'names': names, 'formats': formats}

        nemoa.log("import data from csv file: " + file)

        try:
            data = numpy.loadtxt(file, skiprows = 1, delimiter = delim,
                usecols = cols, dtype = dtype)
        except:
            return nemoa.log('error', 'could not import data from file!')

        return data

    def _get_cache_file(self, network):
        """Return cache file path."""
        return '%sdata-%s-%s.npz' % (self._config['cache_path'],
            network._config['id'], self._config['id'])

    def _search_cache_file(self, network):
        """Return cache file path if existent."""
        file = self._get_cache_file(network)
        return file if os.path.isfile(file) else None

    def _create_cache_file(self, network):
        """Return empty cache file if existent."""
        file = self._get_cache_file(network)
        if not os.path.isfile(file):
            basedir = os.path.dirname(file)
            if not os.path.exists(basedir): os.makedirs(basedir)
            with open(file, 'a'): os.utime(file, None)
        return file

    def get(self, key = None, *args, **kwargs):
        """Get information about dataset."""

        # get generic information about dataset
        if key == 'name': return self._get_name()
        if key == 'type': return self._get_type()
        if key == 'about': return self._get_about()

        # get information about dataset parameters
        if key == 'cols': return self._get_cols(*args, **kwargs)
        if key == 'filter': return self._get_col_filter(*args, **kwargs)
        if key == 'groups': return self._get_col_groups(*args, **kwargs)

        # get copy of dataset configuration and parameters
        if key == 'copy': return self._get_copy(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_name(self):
        """Get name of dataset."""
        return self._config['name'] if 'name' in self._config else None

    def _get_type(self):
        """Get type of dataset, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_about(self):
        """Get docstring of dataset."""
        return self.__doc__

    def _get_cols(self, group = '*'):
        """Return list of strings containing column groups and labels."""
        if group == '*': return ['%s:%s' % (col[0], col[1])
            for col in self._config['columns']]
        if not group in self._config['col_filter']: return []
        col_filter = self._config['col_filter'][group]
        labels = []
        for col in self._config['columns']:
            if ('*:*') in col_filter \
                or ('%s:*' % (col[0])) in col_filter \
                or ('*:%s' % (col[1])) in col_filter \
                or ('%s:%s' % (col[0], col[1])) in col_filter:
                labels.append('%s:%s' % (col[0], col[1]))
        return labels

    def _get_col_groups(self):
        groups = {}
        for group, label in self._config['columns']:
            if not group in groups: groups[group] = []
            groups[group].append(label)
        return groups

    def _get_col_filter(self):
        return self._config['col_filter'].keys()

    def _get_copy(self, section = None):
        """Get dataset copy as dictionary."""
        if section == None: return {
            'config': copy.deepcopy(self._config),
            'data': copy.deepcopy(self._data) }
        elif section == 'config':
            return copy.deepcopy(self._config)
        elif section == 'data':
            return copy.deepcopy(self._config)
        return nemoa.log('error', """could not get copy of
            configuration: unknown section '%s'.""" % (section))

    def set(self, key = None, *args, **kwargs):

        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'filter': return self._set_col_filter(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def _set_name(self, name):
        """Set name of dataset."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def _set_copy(self, **kwargs):
        if 'data' in kwargs:
            self._data = copy.deepcopy(kwargs['data'])
        if 'config' in kwargs:
            self._config = copy.deepcopy(kwargs['config'])
        return True

