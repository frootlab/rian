# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import copy
import nemoa
import numpy

class Dataset:
    """Dataset class."""

    _default = { 'name': None }
    _config = None
    _tables = None

    def __init__(self, **kwargs):
        """Import dataset from dictionary."""
        self._set_copy(**kwargs)

    def _is_binary(self):
        """Test if dataset contains only binary data.

        Returns:
            Boolean value which is True if dataset contains only
            binary values.

        """

        data = self._get_data()
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

        data = self._get_data(size) # get numpy array with data

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
        return len(self._tables.keys()) > 0

    def configure(self, network):
        """Configure dataset columns to a given network.

        Args:
            network (network instance): nemoa network instance

        """

        # get visible network layers and node label format
        layers = network.get('layers', visible = True)
        labelformat = network.get('config', 'labelformat')

        # normalize network node labels
        nodes_conv = {}
        nodes_lost = []
        nodes_count = 0
        for layer in layers:

            # get nodes from layer
            nodes = network.get('nodes', layer = layer)

            # get node labels from layer
            # TODO: network.get('nodelabel', node = node)
            # TODO: network.get('nodelabels', layer = layer)
            node_labels = []
            for node in nodes:
                node_labels.append(
                    network.get('node', node)['params']['label'])

            # convert node labels to standard label format
            conv, lost = nemoa.common.annotation.convert(
                node_labels, input = labelformat)
            nodes_conv[layer] = conv
            nodes_lost += [conv[i] for i in lost]
            nodes_count += len(nodes_conv[layer])

        # notify about lost (not convertable) nodes
        if nodes_lost:
            nemoa.log('error', """%s of %s network nodes could not
                be converted!""" % (len(nodes_lost), nodes_count))
            nemoa.log('logfile', nemoa.common.str_from_list(nodes_lost))

        # get columns from dataset files and convert to common format
        col_labels = {}
        for table in self._config['table']:
            table_config = self._config['table'][table]

            # convert column names
            if 'columns_orig' in table_config \
                and 'columns_conv' in table_config \
                and 'columns_lost' in table_config:
                source_columns = table_config['columns_orig']
                columns_conv = table_config['columns_conv']
                columns_lost = table_config['columns_lost']
            else:
                source_columns = \
                    self._tables[table]['array'].dtype.names

                if 'labelformat' in table_config:
                    source_labelformat = table_config['labelformat']
                else:
                    source_labelformat = 'generic:string'

                columns_conv, columns_lost = \
                    nemoa.common.annotation.convert(
                    source_columns, input = source_labelformat)

                table_config['columns_orig'] = source_columns
                table_config['columns_conv'] = columns_conv
                table_config['columns_lost'] = columns_lost

            # convert table columns
            self._tables[table]['array'].dtype.names = \
                tuple(table_config['columns_conv'])

            # notify if any table columns could not be converted
            if columns_lost:
                nemoa.log('error', """%i of %i table column names
                    could not be converted.""" %
                    (len(columns_lost), len(columns_conv)))
                nemoa.log('logfile', ', '.join([columns_conv[i] \
                    for i in columns_lost]))

            # search network nodes in table columns
            num_lost = 0
            num_all = 0
            nodes_lost = {}
            for layer in layers:
                nodes_conv_lost = \
                    [val for val in nodes_conv[layer] \
                    if val not in columns_conv]
                num_all += len(nodes_conv[layer])

                if not nodes_conv_lost: continue
                num_lost += len(nodes_conv_lost)

                # get lost nodes
                nodes_lost[layer] = []
                for val in nodes_conv_lost:
                    node_lost_id = nodes_conv[layer].index(val)
                    node_lost = network.get('nodes',
                        layer = layer)[node_lost_id]
                    node_label = network.get('node',
                        node_lost)['params']['label']
                    nodes_lost[layer].append(node_label)

            # notify if any network nodes could not be found
            if num_lost:
                nemoa.log('error', """%i of %i network nodes
                    could not be found in dataset table column names!
                    (see logfile)""" % (num_lost, num_all))
                for layer in nodes_lost:
                    nemoa.log('logfile', "missing nodes (layer '%s'): "
                        % (layer) + ', '.join(nodes_lost[layer]))

            # prepare dictionary for column source ids
            col_labels[table] = {
                #'original': source_columns,
                'conv': columns_conv,
                #'usecols': (),
                'notusecols': columns_lost }

        # intersect converted table column names
        inter_col_labels = col_labels[col_labels.keys()[0]]['conv']
        for table in col_labels:
            list = col_labels[table]['conv']
            black_list = [list[i] for i in \
                col_labels[table]['notusecols']]
            inter_col_labels = [val for val in inter_col_labels \
                if val in list and not val in black_list]

        # search network nodes in dataset columns and create
        # dictionary for column mapping from columns to table column
        # names
        columns = []
        mapping = {}
        for layer in layers:

            found = False
            for id, column in enumerate(nodes_conv[layer]):
                if not column in inter_col_labels: continue
                found = True

                # add column (use network label and layer)
                # TODO: network.get('nodelabel', node = node)
                node = network.get('nodes', layer = layer)[id]
                label = network.get('node', node)['params']['label']
                colid = layer + ':' + label
                columns.append(colid)
                mapping[colid] = column

            if not found:
                return nemoa.log('error', """no node from network layer
                    '%s' could be found in dataset tables.""" % (layer))

        self._set_columns(columns, mapping)

        # add '*' and network layer names as column filters
        colfilter = {key: [key + ':*'] for key in layers + ['*']}
        self._config['colfilter'] = colfilter

        # add '*' and table names as row filters
        tables = self._tables.keys()
        rowfilter = {key: [key + ':*'] for key in tables + ['*']}
        self._config['rowfilter'] = rowfilter

        # preprocess data
        if 'preprocessing' in self._config.keys():
            self.preprocess(**self._config['preprocessing'])

        return True

    def preprocess(self, stratify = None, normalize = None,
        transform = None):
        """Data preprocessing.

        Stratification, normalization and transformation of data.

        Args:
            stratify (dict or None): see method self._stratify()
            normalize (dict or None): see method self._normalize()
            transform (dict or None): see method self._transform()

        """

        nemoa.log('preprocessing data')
        nemoa.log('set', indent = '+1')

        if stratify: self._stratify(stratify)
        if normalize: self._normalize(normalize)
        if transform: self._transform(transform)

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
            for src in self._tables:
                allSize += self._tables[src]['array'].shape[0]
            for src in self._tables: self._tables[src]['fraction'] = \
                float(allSize) / float(self._tables[src]['array'].shape[0])
            return True
        if algorithm.lower() in ['auto']: return True
        if algorithm.lower() in ['equal']:
            frac = 1. / float(len(self._tables))
            for src in self._tables: self._tables[src]['fraction'] = frac
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
        if len(self._tables.keys()) == 1:
            data = self._get_tables(source = self._tables.keys()[0])
        else:
            data = self._get_data(size = size, output = 'recarray')

        # iterative normalize sources
        for source in self._tables.keys():
            source_array = self._tables[source]['array']
            if source_array == None: continue

            # iterative normalize columns (recarray)
            for col in source_array.dtype.names[1:]:
                mean = data[col].mean()
                sdev = data[col].std()
                self._tables[source]['array'][col] = \
                    (source_array[col] - mean) / sdev
        return True

    def _transform(self, algorithm = 'system', *args, **kwargs):
        """Transform data in tables.

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
            return self._transform_system(*args, **kwargs)

        # gauss to binary data transformation
        elif algorithm.lower() in ['gausstobinary', 'binary']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._tables:
                # update source per column (recarray)
                for colName in self._tables[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._tables[src]['array'][colName] = \
                        (self._tables[src]['array'][colName] > 0.
                        ).astype(float)
            return True

        # gauss to weight in [0, 1] data transformation
        elif algorithm.lower() in ['gausstoweight', 'weight']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._tables:
                # update source per column (recarray)
                for colName in self._tables[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._tables[src]['array'][colName] = \
                        (2. / (1. + numpy.exp(-1. * \
                        self._tables[src]['array'][colName] ** 2))
                        ).astype(float)
            return True

        # gauss to distance data transformation
        # TODO: obsolete
        elif algorithm.lower() in ['gausstodistance', 'distance']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._tables:
                # update source per column (recarray)
                for colName in self._tables[src]['array'].dtype.names[1:]:
                    self._tables[src]['array'][colName] = \
                        (1. - (2. / (1. + numpy.exp(-1. * \
                        self._tables[src]['array'][colName] ** 2)))
                        ).astype(float)
            return True

        return nemoa.log('error', """could not transform data:
            unknown algorithm '%s'!""" % (algorithm))

    def _transform_system(self, system = None, mapping = None,
        func = 'expect'):
        if not nemoa.type.is_system(system):
            return nemoa.log('error', """could not transform data
                using system: invalid system.""")

        nemoa.log("transform data using system '%s'"
            % (system.get('name')))

        nemoa.log('set', indent = '+1')
        if mapping == None: mapping = system.mapping()

        source_columns = system.get('units', layer = mapping[0])
        target_columns = system.get('units', layer = mapping[-1])

        colnames = self._get_colnames(source_columns)

        for table in self._tables:

            # get data, mapping and transformation function
            data = self._tables[table]['array']
            data_array = data[colnames].view('<f8').reshape(
                data.size, len(colnames))

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
            num_rows = self._tables[table]['array']['label'].size
            col_names = ('label',) + tuple(target_columns)
            col_formats = ('<U12',) + tuple(['<f8' \
                for x in target_columns])
            new_rec_array = numpy.recarray((num_rows,),
                dtype = zip(col_names, col_formats))

            # set values in record array
            new_rec_array['label'] = \
                self._tables[table]['array']['label']
            for colid, colname in \
                enumerate(new_rec_array.dtype.names[1:]):

                # update source data columns
                new_rec_array[colname] = \
                    (trans_array[:, colid]).astype(float)

            # set record array
            self._tables[table]['array'] = new_rec_array

        # create column mapping
        colmapping = {}
        for column in target_columns:
            colmapping[column] = column

        self._set_columns(target_columns, colmapping)
        nemoa.log('set', indent = '-1')
        return True

    def get(self, key = 'name', *args, **kwargs):
        """Get meta information, parameters and data of dataset."""

        # get meta information
        if key == 'fullname': return self._get_fullname()
        if key == 'name': return self._get_name()
        if key == 'branch': return self._get_branch()
        if key == 'version': return self._get_version()
        if key == 'about': return self._get_about()
        if key == 'author': return self._get_author()
        if key == 'email': return self._get_email()
        if key == 'license': return self._get_license()
        if key == 'type': return self._get_type()

        # get parameters and data
        if key == 'columns': return self._get_columns(*args, **kwargs)
        if key == 'colgroups': return self._get_colgroups()
        if key == 'colfilter': return self._get_colfilter(*args, **kwargs)
        if key == 'colfilters': return self._get_colfilters()
        if key == 'rows': return self._get_rows(*args, **kwargs)
        if key == 'rowgroups': return self._get_rowgroups(*args, **kwargs)
        if key == 'rowfilter': return self._get_rowfilter(*args, **kwargs)
        if key == 'rowfilters': return self._get_rowfilters()
        if key == 'data': return self._get_data(*args, **kwargs)
        if key == 'value': return self._get_value(*args, **kwargs)

        # export configuration and data
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'source': return self._get_tables(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_fullname(self):
        """Get fullname of dataset."""
        fullname = ''
        name = self._get_name()
        if name: fullname += name
        branch = self._get_branch()
        if branch: fullname += '.' + branch
        version = self._get_version()
        if version: fullname += '.' + str(version)
        return fullname

    def _get_name(self):
        """Get name of dataset."""
        if 'name' in self._config: return self._config['name']
        return None

    def _get_branch(self):
        """Get branch of dataset."""
        if 'branch' in self._config: return self._config['branch']
        return None

    def _get_version(self):
        """Get version number of dataset branch."""
        if 'version' in self._config: return self._config['version']
        return None

    def _get_about(self):
        """Get description of dataset."""
        if 'about' in self._config: return self._config['about']
        return None

    def _get_author(self):
        """Get author of dataset."""
        if 'author' in self._config: return self._config['author']
        return None

    def _get_email(self):
        """Get email of author of dataset."""
        if 'email' in self._config: return self._config['email']
        return None

    def _get_license(self):
        """Get license of dataset."""
        if 'license' in self._config: return self._config['license']
        return None

    def _get_type(self):
        """Get type of dataset, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_columns(self, filter = '*'):
        """Get external columns.

        Nemoa datasets differ between internal column names (colnames)
        and external column names (columns). The internal column names
        correspond to the real column names of the numpy structured
        arrays. The external column names provide an additional layer.
        These column names are mapped to internal column names when
        accessing tables, which allows to provide identical columns to
        different column names, for example used by autoencoders.

        Args:
            colfilter (string, optional):

        Returns:
            List of strings containing column names.

        """

        if filter == '*':
            colnames = []
            for col in self._config['columns']:
                if col[0]: colnames.append('%s:%s' % (col[0], col[1]))
                elif col[1]: colnames.append(col[1])
            return colnames
        if not filter in self._config['colfilter']:
            return []
        col_filter = self._config['colfilter'][filter]
        colnames = []
        for col in self._config['columns']:
            if ('*:*') in col_filter \
                or ('%s:*' % (col[0])) in col_filter \
                or ('*:%s' % (col[1])) in col_filter \
                or ('%s:%s' % (col[0], col[1])) in col_filter:
                if col[0]: colnames.append('%s:%s' % (col[0], col[1]))
                elif col[1]: colnames.append(col[1])
        return colnames

    def _get_colnames(self, columns):
        """Get internal columns.

        Nemoa datasets differ between internal column names (colnames)
        and external column names (columns). The internal column names
        correspond to the real column names of the numpy structured
        arrays. The external column names provide an additional layer.
        These column names are mapped to internal column names when
        accessing tables, which allows to provide identical columns to
        different column names, for example used by autoencoders.

        """

        mapping = self._config['colmapping']
        mapper = lambda column: mapping[column]

        return map(mapper, columns)

    def _get_colgroups(self):
        groups = {}
        for group, label in self._config['columns']:
            if not group in groups: groups[group] = []
            groups[group].append(label)
        return groups

    def _get_colfilter(self, name):
        if not name in self._config['colfilter']:
            nemoa.log('warning', "unknown column filter '" + name + "'!")
            return []
        return self._config['colfilter'][name]

    def _get_colfilters(self):
        return self._config['colfilter'].keys()

    def _get_rows(self):
        row_names = []
        for source in self._tables.keys():
            labels = self._tables[source]['array']['label'].tolist()
            row_names += ['%s:%s' % (source, name) for name in labels]
        return row_names

    def _get_rowgroups(self):
        return self._tables.keys()

    def _get_rowfilter(self, name):
        if not name in self._config['rowfilter']:
            nemoa.log('warning', "unknown row filter '" + name + "'!")
            return []
        return self._config['rowfilter'][name]

    def _get_rowfilters(self):
        return self._config['rowfilter'].keys()

    def _get_data(self, size = 0, rows = '*', cols = '*',
        noise = (None, 0.), output = 'array'):
        """Return a given number of stratified samples.

        Args:
            size: Size of data (Number of samples)
                default: value 0 returns all samples unstratified
            rows: string describing row filter
                default: value '*' selects all rows
            cols: string describing column filter
                default: value '*' selects all columns
            noise: 2-tuple describing noise model and strength
                first entry of tuple: type of noise / noise model
                    'none': no noise
                    'mask': Masking Noise
                        A fraction of every sample is forced to zero
                    'gauss': Gaussian Noise
                        Additive isotropic Gaussian noise
                    'salt': Salt-and-pepper noise
                        A fraction of every sample is forced to min or
                        max with equal possibility
                    default: Value None equals to 'no'
                second entry of tuple: noise factor
                    float in interval [0, 1] describing the strengt
                    of the noise. The influence of the parameter
                    depends on the noise type
                    default: Value 0.5
            output (string or tuple of strings, optional):
                data return format:
                'recarray': numpy record array containing data, column
                    names and row names in column 'label'
                'array': numpy ndarray containing data
                'cols': list of column names
                'rows': list of row names
                default value is 'array'

        """

        # check Configuration and Keyword Arguments
        if not self._is_configured(): return nemoa.log('error',
            'could not get data: dataset is not yet configured!')
        if not isinstance(size, int) or size < 0: return nemoa.log(
            'error', 'could not get data: invalid argument size!')

        # stratify and filter data
        src_stack = ()
        for table in self._tables.iterkeys():
            # TODO: fix size: size + 1 -> size
            if size > 0:
                src_data = self._get_tables(source = table,
                    rows = rows, size = size + 1, labels = True)
            else:
                src_data = self._get_tables(source = table,
                    rows = rows, labels = True)
            if src_data == False or src_data.size == 0: continue
            src_stack += (src_data, )
        if not src_stack:
            return nemoa.log('error', """could not get data:
                no valid data sources found!""")
        data = numpy.concatenate(src_stack)

        # (optional) shuffle data and correct size
        if size:
            numpy.random.shuffle(data)
            data = data[:size]

        # format data
        if isinstance(cols, str):
            fmt_data = self._get_data_format(data,
                cols = self._get_columns(cols),
                output = output)
        elif isinstance(cols, list):
            fmt_data = self._get_data_format(data,
                cols = cols,
                output = output)
        elif isinstance(cols, tuple):
            fmt_data = tuple([self._get_data_format(data,
                cols = self._get_columns(col_filter),
                output = output) for col_filter in cols])
        else:
            return nemoa.log('error', """could not get data:
                invalid argument for columns!""")

        # Corrupt data (optional)
        return self._get_data_corrupt(fmt_data, \
            type = noise[0], factor = noise[1])

    def _get_data_format(self, data, cols = '*', output = 'array'):
        """Return data in given format.

        Args:
            cols: name of column filter or list of columns
                default: value '*' does not filter columns
            output (string or tuple of strings, optional):
                data return format:
                'recarray': numpy record array containing data, column
                    names and row names in column 'label'
                'array': numpy ndarray containing data
                'cols': list of column names
                'rows': list of row names
                default value is 'array'

        """

        # get columns from column filter or from list
        if isinstance(cols, basestring):
            columns = self._get_columns(cols)
        elif isinstance(cols, list):
            columns = cols
        else:
            return nemoa.log('error', """could not retrieve data:
                Argument 'cols' is not valid.""")

        # assert validity of columns and get column names of tables
        if not len(columns) == len(set(columns)):
            return nemoa.log('error', """could not retrieve data:
                columns are not unique!""")
        if [col for col in columns if col not in self._get_columns()]:
            return nemoa.log('error', """could not retrieve data:
                unknown columns!""")
        colnames = self._get_colnames(columns)

        # check return data type
        if isinstance(output, str): fmt_tuple = (output, )
        elif isinstance(output, tuple): fmt_tuple = output
        else:
            return nemoa.log('error', """could not retrieve data:
                invalid 'format' argument!""")

        # format data
        rettuple = ()
        for fmt_str in fmt_tuple:
            if fmt_str == 'recarray':
                rettuple += (data[['label'] + colnames], )
            elif fmt_str == 'array':
                rettuple += (data[colnames].view('<f8').reshape(
                    data.size, len(colnames)), )
            elif fmt_str == 'cols':
                rettuple += (colnames, )
            elif fmt_str == 'rows':
                rettuple += (data['label'].tolist(), )
            else:
                return nemoa.log('error', """could not retrieve data:
                    invalid argument 'cols'.""")
        if isinstance(output, str):
            return rettuple[0]
        return rettuple

    def _get_data_corrupt(self, data, type = None, factor = 0.5):
        """Corrupt given data.

        Args:
            data: numpy array containing data
            type (str): noise model
                'mask': Masking Noise
                    A fraction of every sample is forced to zero
                'gauss': Gaussian Noise
                    Additive isotropic Gaussian noise
                'salt': Salt-and-pepper noise
                    A fraction of every sample is forced to min or max
                    with equal possibility
            factor (float, optional): strengt of the noise
                The influence of the parameter depends on the
                noise model

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
            "unkown data noise type '%s'!" % (type))

    def _get_value(self, row = None, col = None):
        """get single value from dataset."""
        return float(self._get_data(cols = [col], rows = [row]))

    def _get_copy(self, key = None, *args, **kwargs):
        """get dataset copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'source': self._get_tables() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'source': return self._get_tables(*args, **kwargs)

        return nemoa.log('error', """could not get dataset copy:
            unknown key '%s'.""" % (key))

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in self._config.keys():
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        return nemoa.log('error', """could not get configuration:
            unknown key '%s'.""" % (key))

    def _get_tables(self, source = None, cols = '*', rows = '*',
        size = 0, labels = False):
        """Get data from tables.

        Args:
            table (string or None, optional): name of table.
                If None, a copy of all tables is returned.
            cols (string, optional): string describing a column filter
                using wildcards. Default value '*' selects all columns.
            rows (string, optional): string describing a row filter
                using wildcards. Default value '*' selects all rows.
            size (int, optional): number of random choosen samples to
                return. Default value 0 returns all samples of given
                source.
            labels (bool, optional): if True, the returned table
                contains a column 'label' which contains row labels.

        Returns:
            Dictionary with tables data OR numpy recarray with data
            from a single table.

        """

        if source == None: return copy.deepcopy(self._tables)

        # check source
        if not isinstance(source, str) \
            or not source in self._tables \
            or not isinstance(self._tables[source]['array'],
            numpy.ndarray):
            return nemoa.log('error', """could not retrieve table:
                invalid table name: '%s'.""" % (source))

        # get column names from column filter
        columns = self._get_columns(cols)
        colnames = self._get_colnames(columns)
        if labels: colnames = ['label'] + colnames

        # get row names from filter
        if isinstance(rows, str):
            if not rows in self._config['rowfilter']:
                return nemoa.log('error', """could not retrieve
                    data: invalid row filter: '%s'!""" % (rows))
            rowfilter = self._config['rowfilter'][rows]
        elif isinstance(rows, list):
            # TODO filter list to valid row names
            rowfilter = rows

        src_array_colsel = self._tables[source]['array'][colnames]

        # row selection
        if '*:*' in rowfilter or source + ':*' in rowfilter:
            src_array = src_array_colsel
        else:
            rowfilter_filtered = [
                row.split(':')[1] for row in rowfilter
                if row.split(':')[0] in [source, '*']]
            rowsel = numpy.asarray([
                rowid for rowid, row in enumerate(
                self._tables[source]['array']['label'])
                if row in rowfilter_filtered])
            src_array = numpy.take(src_array_colsel, rowsel)

        # stratify and return data as numpy record array
        if size == 0 or size == None: return src_array
        src_frac = self._config['table'][source]['fraction']
        rowsel = numpy.random.randint(src_array.size,
            size = round(src_frac * size))

        return numpy.take(src_array, rowsel)

    def set(self, key = None, *args, **kwargs):
        """Set meta information, parameters and data of dataset."""

        # set meta information
        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'branch': return self._set_branch(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)
        if key == 'about': return self._set_about(*args, **kwargs)
        if key == 'author': return self._set_author(*args, **kwargs)
        if key == 'email': return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)

        # modify dataset parameters and data
        if key == 'columns': return self._set_columns(*args, **kwargs)
        if key == 'colfilter': return self._set_colfilter(**kwargs)

        # import configuration and source data
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'source': return self._set_tables(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_name(self, dataset_name):
        """Set name of dataset."""
        if not isinstance(dataset_name, str): return False
        self._config['name'] = dataset_name
        return True

    def _set_branch(self, dataset_branch):
        """Set branch of dataset."""
        if not isinstance(dataset_branch, str): return False
        self._config['branch'] = dataset_branch
        return True

    def _set_version(self, dataset_version):
        """Set version number of dataset branch."""
        if not isinstance(dataset_version, int): return False
        self._config['version'] = dataset_version
        return True

    def _set_about(self, dataset_about):
        """Get description of dataset."""
        if not isinstance(dataset_about, str): return False
        self._config['about'] = dataset_about
        return True

    def _set_author(self, dataset_author):
        """Set author of dataset."""
        if not isinstance(dataset_author, str): return False
        self._config['author'] = dataset_author
        return True

    def _set_email(self, dataset_author_email):
        """Set email of author of dataset."""
        if not isinstance(dataset_author_email, str): return False
        self._config['email'] = dataset_author_email
        return True

    def _set_license(self, dataset_license):
        """Set license of dataset."""
        if not isinstance(dataset_license, str): return False
        self._config['license'] = dataset_license
        return True

    def _set_columns(self, columns, mapping):
        """Set external column names.

        Nemoa datasets differ between internal column names (colnames)
        and external column names (columns). The internal column names
        correspond to the real column names of the numpy structured
        arrays. The external column names provide an additional layer.
        These column names are mapped to internal column names when
        accessing tables, which allows to provide identical columns to
        different column names, for example used by autoencoders.

        Args:
            columns (liats): list of external column names
            mapping (dict): mapping from external columns to internal
                colnames.

        Returns:
            bool: True if no error occured.

        """

        # assert validity of argument 'columns'
        if not isinstance(columns, list):
            return nemoa.log('error', """could not set columns:
                columns list is not valid.""")

        # assert validity of argument 'mapping'
        if not isinstance(mapping, dict):
            return nemoa.log('error', """could not set columns:
                mapping dictionary is not valid.""")

        # assert validity of external columns in 'mapping'
        for column in columns:
            if not column in mapping.keys():
                return nemoa.log('error', """could not set columns:
                    column '%s' can not be mapped to table column."""
                    % (column))

        # assert validity of internal columns in 'mapping'
        for column in list(set(mapping.values())):
            for table in self._tables.iterkeys():
                if column in self._tables[table]['array'].dtype.names:
                    continue
                return nemoa.log('error', """could not set columns:
                    table '%s' has no column '%s'."""
                    % (table, column))

        # set 'columns' and 'colmapping'
        self._config['colmapping'] = mapping.copy()
        self._config['columns'] = tuple()
        for column in columns:
            if ':' in column: colid = tuple(column.split(':'))
            else: colid = ('', column)
            self._config['columns'] += (colid, )

        return True

    def _set_colfilter(self, **kwargs):
        col_names = self._get_columns()

        for col_filter_name in kwargs.keys():
            col_filter_cols = kwargs[col_filter_name]

            # test column names of new column filter
            valid = True
            for col_name in col_filter_cols:
                if not col_name in col_names:
                    valid = False
                    break
            if not valid: continue

            # add / set column filter
            self._config['colfilter'][col_filter_name] \
                = col_filter_cols

        return True

    def _set_copy(self, config = None, source = None):
        """Set configuration and source data of dataset.

        Args:
            config (dict or None, optional): dataset configuration
            source (dict or None, optional): dataset source data

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if source: retval &= self._set_tables(source)

        return retval

    def _set_config(self, config = None):
        """Set configuration of dataset.

        Args:
            config (dict or None, optional): dataset configuration

        Returns:
            Bool which is True if and only if no error occured.

        """

        # initialize configuration dictionary
        if not self._config: self._config = self._default.copy()

        # update configuration dictionary
        if not config: return True
        nemoa.common.dict_merge(copy.deepcopy(config), self._config)
        # TODO: reconfigure!?
        self._tables = {}

        return True

    def _set_tables(self, source = None):
        """Set source data of dataset.

        Args:
            source (dict or None, optional): dataset source data

        Returns:
            Bool which is True if and only if no error occured.

        """

        if not source: return True
        nemoa.common.dict_merge(copy.deepcopy(source), self._tables)

        return True

    def save(self, *args, **kwargs):
        """Export dataset to file."""
        return nemoa.dataset.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show dataset as image."""
        return nemoa.dataset.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of dataset."""
        return nemoa.dataset.copy(self, *args, **kwargs)
