# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import copy
from typing import Any, Dict, Optional
import numpy as np
from flab.base import catalog, otree
import nemoa
from nemoa.base import array, nbase
from nemoa.core import log, ui

class Dataset(nbase.ObjectIP):
    """Dataset base class.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        columns (list of str): List of all columns in the dataset.
            Hint: Readonly wrapping attribute to get('columns')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        path (str): Path to a file containing or referencing the
            resource.
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        rows (list of str): List of all rows in the dataset.
            Hint: Readonly wrapping attribute to get('rows')
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _config: Optional[dict] = None
    _tables: Optional[dict] = None
    _default = { 'name': None }

    _attr: Dict[str, int] = {
        'columns': 0b01, 'rows': 0b01
    }

    _copy: Dict[str, str] = {
        'tables': '_tables'
    }

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize dataset with content from arguments."""

        # get attribute and storage defaults from parent
        self._attr = {**getattr(super(), '_attr', {}), **self._attr}
        self._copy = {**getattr(super(), '_copy', {}), **self._copy}

        super().__init__(*args, **kwds)

    def configure(self, network):
        """Configure dataset columns to a given network.

        Args:
            network (network instance): nemoa network instance

        Returns:
            Boolen value which is True if no error occured.

        """

        from nemoa.dataset.commons import labels

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
            # 2do: network.get('nodelabel', node = node)
            # 2do: network.get('nodelabels', layer = layer)
            node_labels = []
            for node in nodes:
                node_labels.append(
                    network.get('node', node)['params']['label'])

            # convert node labels to standard label format
            conv, lost = labels.convert(node_labels, input = labelformat)

            nodes_conv[layer] = conv
            nodes_lost += [conv[i] for i in lost]
            nodes_count += len(nodes_conv[layer])

        # notify about lost (not convertable) nodes
        if nodes_lost:
            log.warning("""%s of %s network nodes could not
                be converted!""" % (len(nodes_lost), nodes_count))
            log.debug(', '.join(nodes_lost))

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
                    self._tables[table].dtype.names

                if 'labelformat' in table_config:
                    source_labelformat = table_config['labelformat']
                else:
                    source_labelformat = 'generic:string'

                columns_conv, columns_lost = \
                    labels.convert(source_columns, input = source_labelformat)

                table_config['columns_orig'] = source_columns
                table_config['columns_conv'] = columns_conv
                table_config['columns_lost'] = columns_lost

            self._test = table_config

            # convert table columns
            self._tables[table].dtype.names = \
                tuple(table_config['columns_conv'])

            # notify if any table columns could not be converted
            if columns_lost:
                log.warning("""%i of %i table column names
                    could not be converted.""" %
                    (len(columns_lost), len(columns_conv)))
                log.debug(', '.join([columns_conv[i] for i in columns_lost]))

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
                log.warning("""%i of %i network nodes
                    could not be found in dataset table column names!
                    """ % (num_lost, num_all))
                for layer in nodes_lost:
                    log.debug("missing nodes (layer '%s'): "
                        % (layer) + ', '.join(nodes_lost[layer]))

            # prepare dictionary for column source ids
            col_labels[table] = {
                #'original': source_columns,
                'conv': columns_conv,
                #'usecols': (),
                'notusecols': columns_lost }

        # intersect converted table column names
        inter_col_labels = col_labels[list(col_labels.keys())[0]]['conv']
        for table in col_labels:
            conv_list = col_labels[table]['conv']
            black_list = [conv_list[i] for i in \
                col_labels[table]['notusecols']]
            inter_col_labels = [val for val in inter_col_labels \
                if val in conv_list and not val in black_list]

        # search network nodes in dataset columns and create
        # dictionary for column mapping from columns to table column
        # names
        columns = []
        mapping = {}
        for layer in layers:

            found = False
            for id, column in enumerate(nodes_conv[layer]):
                if column not in inter_col_labels: continue
                found = True

                # add column (use network label and layer)
                # 2do: network.get('nodelabel', node = node)
                node = network.get('nodes', layer = layer)[id]
                node_label = network.get('node', node)['params']['label']
                colid = layer + ':' + node_label
                columns.append(colid)
                mapping[colid] = column

            if not found: raise ValueError(
                "no node from network layer '%s' "
                "could be found in dataset tables." % layer)

        self._set_columns(columns, mapping)

        # add '*' and network layer names as column filters
        colfilter = {key: [key + ':*'] for key in layers + ['*']}
        self._config['colfilter'] = colfilter

        # add '*' and table names as row filters
        tables = list(self._tables.keys())
        rowfilter = {key: [key + ':*'] for key in tables + ['*']}
        self._config['rowfilter'] = rowfilter

        return True

    def initialize(self, system = None):
        """Initialize tables and data preprocessing.

        Stratification, normalization and transformation of tables.

        Returns:
            Boolen value which is True if no error occured.

        """

        ui.info('preprocessing data')

        stratify = None
        normalize = None
        transform = None

        # get preprocessing parameters from dataset configuration
        if 'preprocessing' in self._config:
            preprocessing = self._config['preprocessing']
            if 'stratify' in preprocessing:
                stratify = preprocessing['stratify']
            if 'normalize' in preprocessing:
                normalize = preprocessing['normalize']
            if 'transform' in preprocessing:
                transform = preprocessing['transform']

        # get preprocessing parameters from system
        if otree.has_base(system, 'System'):
            input_layer = system.get('layers')[0]
            distribution = system.get('layer', input_layer)['class']
            if distribution == 'gauss': normalize = 'gauss'
            if distribution == 'sigmoid': normalize = 'bernoulli'

        retval = True

        if stratify: retval &= self._initialize_stratify(stratify)
        if normalize: retval &= self._initialize_normalize(normalize)
        if transform: retval &= self._initialize_transform(transform)

        return retval

    def _initialize_stratify(self, stratification: str = 'hierarchical',
        *args, **kwds):
        """Update sampling fractions for stratified sampling.

        Calculates sampling fractions for each table used in stratified
        sampling. The method get('data', 'size' = $n$) creates
        stratified samples of size $n$. The assigned fraction $f_t$ of
        a table $t$ determines the ratio of the samples that is taken
        from table $t$.

        Args:
            stratification (str, optional): name of algorithm used to
                calculate the sampling fractions for each table.
                'proportional':
                    The sampling fractions of the tables are choosen to
                    be the proportion of the size of the table to the
                    total population.
                'equal':
                    The sampling fractions are equal distributed to
                    the tables. Therefore the hierarchical structure
                    of the compound is assumed to be flat.
                'hierarchical':
                    The sampling fractions are choosen to represent
                    the hierarchical structure of the compounds.

        Returns:
            Boolen value which is True if no error occured.

        """

        ui.info("update sampling fractions using stratification '%s'."
            % stratification)

        # hierarchical sampling fractions
        if stratification.lower() == 'hierarchical':
            return True

        # proportional sampling fractions
        if stratification.lower() == 'proportional':
            total = 0
            for table in self._tables:
                total += self._tables[table].shape[0]
            for table in self._tables:
                size = self._tables[table].shape[0]
                fraction = float(total) / float(size)
                self._config['tables'][table]['fraction'] = fraction
            return True

        # equal sampling fractions
        if stratification.lower() == 'equal':
            fraction = 1. / float(len(self._tables))
            for src in self._tables:
                self._config['tables'][table]['fraction'] = fraction
            return True

        raise ValueError(
            "could not update sampling fractions: "
            "stratification '%s' is not supported." % stratification)

    def _initialize_normalize(self, distribution: str = 'gauss',
        *args, **kwds):
        """Normalize data to a given distribution.

        Args:
            distribution (str, optional): name of distribution to
                be normalized.
                'gauss': normalization of gauss distributed data
                    to (mu = 0, sigma = 1.)
                'bernoulli': normalization of bernoulli distributed data
                    to (q = 0.5)

        Returns:
            Boolen value which is True if no error occured.

        """

        ui.info(f"normalize data using '{distribution}'")

        if distribution.lower() == 'gauss':
            return self._initialize_normalize_gauss(*args, **kwds)
        if distribution.lower() == 'bernoulli':
            return self._initialize_normalize_bernoulli(*args, **kwds)

        return False

    def _initialize_normalize_gauss(self, mu: float = 0.0, sigma: float = 1.0,
        size: int = 100000) -> bool:
        """Gauss normalization of tables.

        Args:
            mu (float, optional): mean value of normalized data.
            sigma (float, optional): Variance of normalized data.
            size (int, optional): Number of samples to calculate
                quantiles if dataset is stratified

        Returns:
            Boolen value which is True if no error occured.

        """

        tables = list(self._tables.keys())
        columns = self._get_colnames()

        # get data for calculation of mean value and standard deviation
        # for single table datasets take all data from
        # for multi table datasets take a big bunch of stratified data
        if len(tables) == 1: data = self._get_table(table = tables[0])
        else: data = self._get_data(size = size, output = 'recarray')

        # calculate mean value and standard deviation for each column
        mean = {col: data[col].mean() for col in columns}
        sdev = {col: data[col].std() for col in columns}

        # iterative normalize tables and columns
        for table in tables:
            for column in columns:
                self._tables[table][column] = \
                    (self._tables[table][column] - mean[column] + mu) \
                    / sdev[column] * sigma

        return True

    def _initialize_normalize_bernoulli(self, p: float = 0.5,
        size: int = 100000):
        """Bernoulli normalization of tables.

        Args:
            p (float, optional): Probability for value 1.
            size (int, optional): Number of samples to calculate
                quantiles if dataset is stratified

        Returns:
            Boolen value which is True if no error occured.

        """

        tables = list(self._tables.keys())
        columns = self._get_colnames()

        # get data for calculation of mean value and standard deviation
        # for single table datasets take all data from
        # for multi table datasets take a big bunch of stratified data
        if len(tables) == 1: data = self._get_table(table = tables[0])
        else: data = self._get_data(size = size, output = 'recarray')

        # calculate q-quantile for each column
        quantile = {}
        for col in columns:
            scol = np.sort(data[col].copy())
            rid = int((1. - p) * data.size)
            lrid = rid - int(0.1 * p * data.size)
            urid = rid + int(0.1 * p * data.size)
            quantile[col] = scol[lrid:urid].mean()

        # iterative normalize tables and columns
        for table in list(self._tables.keys()):
            for column in self._tables[table].dtype.names[1:]:
                mean = data[column].mean()
                self._tables[table][column] = \
                    (self._tables[table][column] > quantile[column]
                    ).astype(float)

        return True

    def _initialize_transform(self, transformation: str = 'system',
        *args, **kwds):
        """Transform data in tables.

        Args:
            transformation (str, optional): name of algorithm used for
                data transformation
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

        Returns:
            Boolen value which is True if no error occured.

        """

        ui.info("transform data using '%s'" % (transformation))

        # system based data transformation
        if transformation.lower() == 'system':
            return self._initialize_transform_system(*args, **kwds)

        # gauss to binary data transformation
        if transformation.lower() in ['gausstobinary', 'binary']:
            for table in self._tables:
                for column in self._tables[table].dtype.names[1:]:
                    self._tables[table][column] = \
                        (self._tables[table][column] > 0.).astype(float)
            return True

        # gauss to weight in [0, 1] data transformation
        if transformation.lower() in ['gausstoweight', 'weight']:
            for table in self._tables:
                for column in self._tables[table].dtype.names[1:]:
                    self._tables[table][column] = \
                        (2. / (1. + np.exp(-1. * \
                        self._tables[table][column] ** 2))
                        ).astype(float)
            return True

        # gauss to distance data transformation
        if transformation.lower() in ['gausstodistance', 'distance']:
            for table in self._tables:
                for column in self._tables[table].dtype.names[1:]:
                    self._tables[table][column] = \
                        (1. - (2. / (1. + np.exp(-1. * \
                        self._tables[table][column] ** 2)))
                        ).astype(float)
            return True

        raise ValueError(
            "could not transform data: "
            "unsupported transformation '%s'." % transformation)

    def _initialize_transform_system(self, system = None,
        mapping = None, func: str = 'expect'):
        """ """

        if not otree.has_base(system, 'System'):
            raise ValueError("system is not valid")

        ui.info("transform data using model '%s'." % system.name)

        if mapping is None: mapping = system.mapping

        source_columns = system.get('units', layer = mapping[0])
        target_columns = system.get('units', layer = mapping[-1])

        colnames = self._get_colnames(source_columns)

        for table in self._tables:

            # get data, mapping and transformation function
            data = self._tables[table]
            data = self._get_table(table, cols = source_columns)

            # 2Do: do not create copy of data but view!
            data_array = data.copy().view('<f8').reshape(data.size,
                len(source_columns))

            # transform data
            if func == 'expect':
                trans_array = system._get_unitexpect(
                    data_array, mapping)
            elif func == 'value':
                trans_array = system._get_unitvalues(
                    data_array, mapping)
            elif func == 'sample':
                trans_array = system._get_unitsamples(
                    data_array, mapping)

            # create empty record array
            num_rows = self._tables[table]['label'].size
            col_names = ('label',) + tuple(target_columns)
            col_formats = ('<U12',) + tuple(['<f8' \
                for x in target_columns])
            new_rec_array = np.recarray((num_rows,),
                dtype = list(zip(col_names, col_formats)))

            # set values in record array
            new_rec_array['label'] = self._tables[table]['label']
            for colid, colname in \
                enumerate(new_rec_array.dtype.names[1:]):

                # update source data columns
                new_rec_array[colname] = \
                    (trans_array[:, colid]).astype(float)

            # set record array
            self._tables[table] = new_rec_array

        # create trivial column mapping
        colmapping = { col: col for col in target_columns }

        return self._set_columns(target_columns, colmapping)

    def get(self, key: str = 'name', *args, **kwds):
        """Get meta information and content."""

        # get readable attributes
        if self._attr.get(key, 0b00) & 0b01:
            return getattr(self, '_get_' + key)(*args, **kwds)

        # algorithms
        if key == 'algorithm': return self._get_algorithm(*args, **kwds)
        if key == 'algorithms': return self._get_algorithms(
            attribute = 'about', *args, **kwds)

        # content
        if key == 'columns': return self._get_columns(*args, **kwds)
        if key == 'colgroups': return self._get_colgroups()
        if key == 'colfilter': return self._get_colfilter(*args, **kwds)
        if key == 'colfilters': return self._get_colfilters()
        if key == 'data': return self._get_data(*args, **kwds)
        if key == 'rows': return self._get_rows(*args, **kwds)
        if key == 'rowgroups': return self._get_rowgroups(*args, **kwds)
        if key == 'rowfilter': return self._get_rowfilter(*args, **kwds)
        if key == 'rowfilters': return self._get_rowfilters()
        if key == 'table': return self._get_table(*args, **kwds)
        if key == 'value': return self._get_value(*args, **kwds)

        # direct access
        if key == 'copy':
            return self._get_copy(*args, **kwds)
        if key == 'config':
            return self._get_config(*args, **kwds)
        if key == 'tables':
            return self._get_table(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _get_algorithms(
            self, category = None, attribute = None, astree = False):
        """Get algorithms provided by dataset."""
        # get dictionary with all methods
        # with prefix '_get_' and attribute 'name'
        methods = otree.get_methods(self, pattern = '_get_*', val = 'name')

        # filter algorithms by given category
        if category is not None:
            for key, val in list(methods.items()):
                if val.get('category', None) != category:
                    del methods[key]

        # create flat structure if category is given or astree is False
        structured = {}
        if category or not astree:
            for ukey, udata in methods.items():
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            return structured

        # create tree structure if category is not given
        categories = {
            ('dataset', 'evaluation'): None,
            ('dataset', 'transformation'): None,
            ('dataset', 'columns', 'evaluation'): 'columns',
            ('dataset', 'rows', 'evaluation'): 'rows'
        }
        for ukey, udata in methods.items():
            if udata['category'] not in categories: continue
            ckey = categories[udata['category']]
            if ckey is None:
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            else:
                if ckey not in structured: structured[ckey] = {}
                if attribute: structured[ckey][udata['name']] = \
                    udata[attribute]
                else: structured[ckey][udata['name']] = udata

        return structured

    def _get_algorithm(self, algorithm = None, *args, **kwds):
        """Get algorithm."""
        algorithms = self._get_algorithms(*args, **kwds)
        if algorithm not in algorithms: return None
        return algorithms[algorithm]

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
            filter (str, optional): name of column filter

        Returns:
            List of strings containing dataset column names or False
            if column filter is not known.

        """

        if isinstance(filter, list):
            # 2do: test for existing columns
            return filter

        if filter == '*':
            columns = []
            for column in self._config['columns']:
                if column[0]:
                    columns.append('%s:%s' % (column[0], column[1]))
                elif column[1]:
                    columns.append(column[1])
            return columns

        if filter in self._config['colfilter']:
            colfilter = self._config['colfilter'][filter]
            columns = []
            for column in self._config['columns']:
                if ('*:*') in colfilter \
                    or ('%s:*' % (column[0])) in colfilter \
                    or ('*:%s' % (column[1])) in colfilter \
                    or ('%s:%s' % (column[0], column[1])) in colfilter:
                    if column[0]:
                        columns.append('%s:%s' % (column[0], column[1]))
                    elif column[1]:
                        columns.append(column[1])
            return columns

        raise ValueError("""could not retrive dataset columns:
            column filter '%s' is not known.""" % (filter))

    def _get_colnames(self, columns = None):
        """Get internal columns.

        Nemoa datasets differ between internal column names (colnames)
        and external column names (columns). The internal column names
        correspond to the real column names of the numpy structured
        arrays. The external column names provide an additional layer.
        These column names are mapped to internal column names when
        accessing tables, which allows to provide identical columns to
        different column names, for example used by autoencoders.

        Args:
            columns (list of strings or None): Dataset column names.
                Default value None retrieves all dataset columns.

        Returns:
            List of strings containing table column names.

        """

        if columns is None: columns = self._get_columns()

        mapping = self._config['colmapping']
        mapper = lambda column: mapping[column]

        return list(map(mapper, columns))

    def _get_colgroups(self):
        """Get grouped lists of columns."""
        groups = {}
        for group, col_label in self._config['columns']:
            if not group: continue
            if group not in groups: groups[group] = []
            groups[group].append(col_label)
        return groups

    def _get_colfilter(self, name):
        """Get column filter by name."""
        return self._config['colfilter'].get(name, log.warning(
            "unknown column filter: '%s'." % name) or [])

    def _get_colfilters(self):
        """Get list of column filters."""
        return list(self._config['colfilter'].keys())

    def _get_rows(self):
        """Get list of row names."""
        row_names = []
        for table in list(self._tables.keys()):
            labels = self._tables[table]['label'].tolist()
            row_names += ['%s:%s' % (table, name) for name in labels]
        return row_names

    def _get_rowgroups(self):
        """Get list of tables."""
        return list(self._tables.keys())

    def _get_rowfilter(self, name):
        if name not in self._config['rowfilter']:
            raise Warning("unknown row filter '" + name + "'!")

        return self._config['rowfilter'][name]

    def _get_rowfilters(self):
        """Get list of row filters."""
        return list(self._config['rowfilter'].keys())

    def _get_data(self, size = 0, rows = '*', cols = '*',
        noise = (None, 0.), output = 'array'):
        """Return a given number of stratified samples.

        Args:
            size (int, optional): size of data (number of samples)
                default: value 0 returns all samples unstratified
            rows (str, optional): name of row select filter
                default: '*' selects all rows
            cols (str, optional): name of column select filter
                default: '*' selects all columns
            noise (2-tuple, optional): noise model and noise strength
                first entry of tuple (string): name of noise model
                    'none': no noise
                    'mask': Masking Noise
                        A fraction of every sample is forced to zero
                    'gauss': Gaussian Noise
                        Additive isotropic Gaussian noise
                    'salt': Salt-and-pepper noise
                        A fraction of every sample is forced to min or
                        max with equal possibility
                    default: 'none'
                second entry of tuple (float): noise strength
                    float in interval [0, 1] describing the noise
                    strengt factor, depending on the used noise model.
                    default: 0.5
            output (str or tuple of str, optional):
                data return format:
                'recarray': numpy record array containing data, column
                    names and row names in column 'label'
                'array': numpy ndarray containing data
                'cols': list of column names
                'rows': list of row names
                default: 'array'

        """

        if not isinstance(size, int) or size < 0:
            raise ValueError(
                "could not get data: "
                "argument 'size' is required to be of type 'int'.")

        # get stratified and filtered data
        src_stack = ()
        for table in self._tables.keys():
            if size > 0:
                src_data = self._get_table(table = table,
                    rows = rows, size = size + 1, labels = True)
            else:
                src_data = self._get_table(table = table,
                    rows = rows, labels = True)
            if hasattr(src_data, 'size') and src_data.size > 0:
                src_stack += (src_data, )

        if not src_stack:
            raise ValueError(
                "could not get data: "
                "no valid data sources found!")
        data = np.concatenate(src_stack)

        # (optional) shuffle data and correct size
        if size:
            np.random.shuffle(data)
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
            raise ValueError(
                "could not get data: "
                "invalid argument for columns!")

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
        if isinstance(cols, str):
            columns = self._get_columns(cols)
        elif isinstance(cols, list):
            columns = cols
        else:
            raise ValueError("""could not retrieve data:
                Argument 'cols' is not valid.""")

        # assert validity of columns and get column names of tables
        if not len(columns) == len(set(columns)):
            raise ValueError("""could not retrieve data:
                columns are not unique!""")
        if [col for col in columns if col not in self._get_columns()]:
            raise ValueError("""could not retrieve data:
                unknown columns!""")
        colnames = self._get_colnames(columns)

        # check return data type
        if isinstance(output, str): fmt_tuple = (output, )
        elif isinstance(output, tuple): fmt_tuple = output
        else:
            raise ValueError("""could not retrieve data:
                invalid 'format' argument!""")

        # check for identical column names
        if len(set(colnames)) == len(colnames):
            ucolnames = colnames
        else:
            redcols = sorted(set(colnames),
                key = colnames.index)
            counter = dict(list(zip(redcols, [0] * len(redcols))))
            ucolnames = []
            for col in colnames:
                counter[col] += 1
                if counter[col] == 1: ucolnames.append(col)
                else: ucolnames.append('%s.%i' % (col, counter[col]))

        # format data
        rettuple = ()
        for fmt_str in fmt_tuple:
            if fmt_str == 'recarray':
                rettuple += (data[['label'] + ucolnames], )
            elif fmt_str == 'array':
                # 2Do: do not create copy of data but view!
                rettuple += (data[ucolnames].copy().view('<f8').reshape(
                    data.size, len(ucolnames)), )
            elif fmt_str == 'cols':
                rettuple += (ucolnames, )
            elif fmt_str == 'rows':
                rettuple += (data['label'].tolist(), )
            else:
                raise ValueError("""could not retrieve data:
                    invalid argument 'cols'.""")
        if isinstance(output, str):
            return rettuple[0]
        return rettuple

    def _get_data_corrupt(self, data, type = None, factor = 0.5):
        """Corrupt given data.

        Args:
            data (numpy ndarray): numpy array containing data
            type (str): noise model
                'gauss': Gaussian noise model
                    Additive isotropic Gaussian distributed noise
                'bernoulli': Bernoulli noise model
                    Additive isotropic Bernoulli distributed noise
                'mask': Masking noise Model
                    A fraction of every sample is forced to zero
                'salt': Salt-and-pepper noise model
                    A fraction of every sample is forced to min or max
                    with equal possibility
            factor (float, optional): strengt of the noise
                The influence of the parameter depends on the
                noise model

        Returns:
            Numpy array with (partly) corrupted data. The shape is
            identical to the shape of the given data.

        """

        if isinstance(data, tuple):
            return tuple([self._get_data_corrupt(table)
                for table in list(data)])

        if not isinstance(type, str): return data
        if type.lower() == 'none': return data

        # gaussian noise model
        elif type.lower() == 'gauss':
            noise = np.random.normal(
                size = data.shape, loc = 0., scale = factor)
            return data + noise

        # bernoulli noise model
        elif type.lower() == 'bernoulli':
            mask = np.random.binomial(
                size = data.shape, n = 1, p = 1. - factor)
            return (data - mask).astype(bool).astype(int)

        # masking noise model
        elif type.lower() == 'mask':
            mask = np.random.binomial(
                size = data.shape, n = 1, p = 1. - factor)
            return mask * data

        # salt & pepper noise model
        elif type.lower() == 'salt':
            amax = np.amax(data, axis = 0)
            amin = np.amin(data, axis = 0)
            mask = np.random.binomial(
                size = data.shape, n = 1, p = 1. - factor)
            sp = np.random.binomial(
                size = data.shape, n = 1, p = .5)
            noise = mask * (amax * sp + amin * (1. - sp))

            return data + noise

        else: raise ValueError("""could not corrupt data:
            unkown noise model '%s'.""" % (type))

    def _get_data_pca(self, data, k: int = 2, embed: bool = True):
        """Calculate projection to principal components."""

        # get dimension of data
        datadim = data.shape[1]
        if k > datadim: k = datadim

        # calculate covariance matrix
        cov = np.cov(data.T)

        # calculate eigevectors and eigenvalues
        eigvals, eigvecs = np.linalg.eig(cov)

        # sort eigevectors by absolute eigenvalues
        eigpairs = [(np.abs(eigvals[i]), eigvecs[:, i])
            for i in range(len(eigvals))]
        eigpairs.sort(key = lambda x: x[0], reverse = True)

        # calculate projection and inverse transformation
        vec = lambda i: eigpairs[i][1] if i < k else np.zeros(datadim)
        if embed:
            proj = np.hstack(
                [vec(i).reshape(datadim, 1) for i in range(datadim)])
            trans = np.hstack(
                [eigpairs[i][1].reshape(datadim, 1) for i in range(datadim)])
            itrans = np.linalg.inv(trans)
            data_pca = np.dot(np.dot(data, proj), itrans)
        else:
            proj = np.hstack(
                [vec(i).reshape(datadim, 1) for i in range(k)])
            data_pca = np.dot(data, proj)

        return data_pca

    def _get_table(self, table = None, cols = '*', rows = '*',
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
            Numpy recarray with data from a single dataset table.

        """

        if table is None:
            return copy.deepcopy(self._tables)

        # check table name
        if not isinstance(table, str) \
            or not table in list(self._tables.keys()) \
            or not isinstance(self._tables[table], np.ndarray):
            raise ValueError(
                "could not retrieve data: "
                "invalid table name: '%s'." % table)

        # get column names from column filter
        columns = self._get_columns(cols)
        colnames = self._get_colnames(columns)
        if labels:
            colnames = ['label'] + colnames

        # get row names from filter
        if isinstance(rows, str):
            if rows not in self._config['rowfilter']:
                raise ValueError("invalid row filter '%s'!" % rows)
            rowfilter = self._config['rowfilter'][rows]
        elif isinstance(rows, list):
            # 2do: filter list to valid row names
            rowfilter = rows

        # test for not unique column names and create dublicates
        if len(set(colnames)) == len(colnames):

            # 2do: multi-field indexing recarrays
            # changes from Numpy 1.14 to Numpy 1.15
            # https://docs.scipy.org/doc/numpy/user/basics.rec.html

            with np.warnings.catch_warnings():
                np.warnings.filterwarnings('ignore')
                table_colsel = self._tables[table][colnames]

        else:
            if labels:
                datacols = colnames[1:]
            else:
                datacols = colnames
            redcols = sorted(set(datacols), key = datacols.index)
            redrec = self._tables[table][redcols]
            redfmt = [col[1] for col in redrec.dtype.descr]
            select = [redcols.index(col) for col in datacols]
            names = []
            counter = dict(list(zip(redcols, [0] * len(redcols))))
            for col in datacols:
                counter[col] += 1
                if counter[col] == 1: names.append(col)
                else: names.append('%s.%i' % (col, counter[col]))
            formats = [redfmt[cid] for cid in select]
            dtype = np.dtype({'names': names, 'formats': formats})
            arr = redrec[redcols].view('<f8').reshape(
                redrec.size, len(redcols))[:,select].copy().view(
                type = np.recarray, dtype = dtype)

            if labels:
                table_colsel = array.add_cols(arr, self._tables[table], 'label')
            else:
                table_colsel = arr

        # row selection
        if '*:*' in rowfilter or source + ':*' in rowfilter:
            data = table_colsel
        else:
            rowfilter_filtered = [
                row.split(':')[1] for row in rowfilter
                if row.split(':')[0] in [source, '*']]
            rowsel = np.asarray([
                rowid for rowid, row in enumerate(
                self._tables[table]['label'])
                if row in rowfilter_filtered])
            data = np.take(table_colsel, rowsel)

        # stratify and return data as numpy record array
        if size == 0 or size is None: return data
        fraction = self._config['table'][table]['fraction']
        rowsel = np.random.randint(data.size,
            size = int(round(fraction * size)))

        return np.take(data, rowsel)

    def _get_value(self, row = None, col = None):
        """Get single value from dataset."""
        return float(self._get_data(cols = [col], rows = [row]))

    def _get_tables(self, key = None):
        """Get dataset tables."""

        if key is None:
            return copy.deepcopy(self._tables)

        if isinstance(key, str) and key in list(self._tables.keys()):
            return self._tables[key]

        raise ValueError("""could not get table:
            unknown tables name '%s'.""" % key) or None

    def set(self, key = None, *args, **kwds):
        """Set meta information, parameters and data of dataset."""

        # set writeable attribute
        if self._attr.get(key, 0b00) & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwds)

        # modify dataset parameters
        if key == 'columns': return self._set_columns(*args, **kwds)
        if key == 'colfilter': return self._set_colfilter(**kwds)

        # import dataset configuration and dataset tables
        if key == 'copy': return self._set_copy(*args, **kwds)
        if key == 'config': return self._set_config(*args, **kwds)
        if key == 'tables': return self._set_tables(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_columns(self, columns, mapping):
        """Set virtual columns.

        Nemoa datasets differ between real columns (colnames) and
        virtual columns (columns). The real columns correspond to the
        columns of numpy structured arrays, whereas the virtual columns
        provide an additional layer, that allows to adress identical
        colmuns bydifferent names, as i.e. used for the opzimization of
        autoencoders.

        Args:
            columns (list of 2-tuples): list of virtual column names
            mapping (dict): mapping from virtual to real columns

        Returns:
            bool: True if no error occured.

        """

        # assert validity of argument 'columns'
        if not isinstance(columns, list):
            raise ValueError("""could not set columns:
                columns list is not valid.""")

        # assert validity of argument 'mapping'
        if not isinstance(mapping, dict):
            raise ValueError("""could not set columns:
                mapping dictionary is not valid.""")

        # assert validity of external columns in 'mapping'
        for column in columns:
            if column not in mapping: raise ValueError(
                f"column '{column}' can not be mapped")

        # assert validity of internal columns in 'mapping'
        for column in list(set(mapping.values())):
            for table in self._tables.keys():
                if column in self._tables[table].dtype.names:
                    continue
                raise ValueError(
                    "table '{table}' has no column '{column}'")

        # set 'columns' and 'colmapping'
        self._config['colmapping'] = mapping.copy()
        self._config['columns'] = tuple()
        for column in columns:
            if ':' in column: colid = tuple(column.split(':'))
            else: colid = ('', column)
            self._config['columns'] += (colid, )

        return True

    def _set_colfilter(self, **kwds):
        """ """

        col_names = self._get_columns()

        for col_filter_name in list(kwds.keys()):
            col_filter_cols = kwds[col_filter_name]

            # test column names of new column filter
            valid = True
            for col_name in col_filter_cols:
                if col_name not in col_names:
                    valid = False
                    break
            if not valid: continue

            # add / set column filter
            self._config['colfilter'][col_filter_name] \
                = col_filter_cols

        return True

    def _set_copy(self, config = None, tables = None):
        """Set dataset configuration and dataset tables.

        Args:
            config (dict or None, optional): dataset configuration
            tables (dict or None, optional): dataset tables data

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if tables: retval &= self._set_tables(tables)

        return retval

    def _set_config(self, config = None):
        """Set configuration of dataset.

        Args:
            config (dict or None, optional): dataset configuration

        Returns:
            Bool which is True if and only if no error occured.

        """
        # initialize configuration dictionary
        self._config = {
            **self._default, **(self._config or {}), **(config or {})}

        # 2do: reconfigure!?
        self._tables = {}

        return True

    def _set_tables(self, tables = None):
        """Set tables of dataset.

        Args:
            tables (dict or None, optional): dataset tables

        Returns:
            Bool which is True if and only if no error occured.

        """

        if not tables:
            return True

        self._tables = {**self._tables, **tables}
        return True

    def evaluate(self, name = None, *args, **kwds):
        """Evaluate dataset."""

        algorithms = self._get_algorithms(attribute = 'reference')
        if name not in list(algorithms.keys()):
            raise ValueError(f"algorithm '{name}' is not supported")

        return algorithms[name](*args, **kwds)

    @catalog.custom(
        name     = 'sample',
        title    = 'Sample Values',
        category = ('dataset', 'evaluation'),
        plot     = 'histogram'
    )
    def _get_sample(self, *args, **kwds):
        """Return a given number of stratified samples."""

        return self._get_data(*args, **kwds)

    @catalog.custom(
        name     = 'covariance',
        title    = 'Covariance',
        category = ('dataset', 'columns', 'evaluation'),
        plot     = 'heatmap'
    )
    def _get_covariance(self, cols: str = '*'):
        """Calculate covariance matrix between given columns.

        Args:
            cols (str, optional): name of column select filter
                default: '*' selects all columns

        Returns:
            Numpy.ndarray containing covariance matrix.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # calculate matrix with covariance coefficients
        C = np.cov(data.T)

        return C

    @catalog.custom(
        name     = 'correlation',
        title    = 'Pearson Correlation',
        category = ('dataset', 'columns', 'evaluation'),
        plot     = 'heatmap'
    )
    def _get_correlation(self, cols: str = '*'):
        """Calculate correlation matrix between given columns.

        Args:
            cols (str, optional): name of column select filter
                default: '*' selects all columns

        Returns:
            Numpy.ndarray containing correlation coeffinient matrix.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # calculate matrix with correlation coefficients
        C = np.corrcoef(data.T)

        return C

    @catalog.custom(
        name     = 'pca-sample',
        title    = 'PCA Sample Values',
        category = ('dataset', 'evaluation'),
        plot     = 'histogram'
    )
    def _get_pcasample(self, cols = '*', k: int = 2, embed: bool = True):
        """Calculate projection to principal components.

        Args:
            cols (str, optional): name of column select filter
                default: '*' selects all columns
            k (int, optional): number of principal components, which is used
                for dimensionality reduction
                default: 2

        Returns:
            Numpy.ndarray containing dimensionality reduced sample.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # calculate numpy array with dimensionality reduced test data
        pca_data = self._get_data_pca(data, k = k, embed = embed)

        return pca_data

    @catalog.custom(
        name      = 'k-covariance',
        title     = 'k-Covariance',
        title_tex = '$k$-Covariance',
        category  = ('dataset', 'columns', 'evaluation'),
        plot      = 'heatmap'
    )
    def _get_kcovariance(self, cols: str = '*', k: int = 2):
        """Calculate k-Covariance matrix between given columns.

        Args:
            cols (str, optional): name of column select filter
                default: '*' selects all columns
            k (int, optional): number of principal components, which is used
                for dimensionality reduction
                default: 2

        Returns:
            Numpy.ndarray containing k-Covariance coefficients.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # calculate numpy array with dimensionality reduced test data
        pca_data = self._get_data_pca(data, k = k, embed = True)

        # calculate matrix with covariance coefficients
        C = np.cov(pca_data.T)

        return C

    @catalog.custom(
        name      = 'k-correlation',
        title     = 'k-Correlation',
        title_tex = '$k$-Correlation',
        category  = ('dataset', 'columns', 'evaluation'),
        plot      = 'heatmap'
    )
    def _get_kcorrelation(self, cols: str = '*', k: int = 2):
        """Calculate k-Correlation matrix between given columns.

        Args:
            cols (str, optional): name of column select filter
                default: '*' selects all columns
            k (int, optional): number of principal components, which are used
                for dimensionality reduction
                default: 2

        Returns:
            Numpy.ndarray containing k-Correlation coefficients.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # calculate numpy array with dimensionality reduced test data
        pca_data = self._get_data_pca(data, k = k, embed = True)

        # calculate matrix with correlation coefficients
        C = np.corrcoef(pca_data.T)

        return C

    @catalog.custom(
        name     = 'test_binary',
        title    = None,
        category = ('dataset', 'evaluation'),
        plot     = 'none'
    )
    def _get_test_binary(self, cols: str = '*'):
        """Test if dataset strictly contains binary values.

        Args:
            cols (str, optional): column filter used to select columns
                default: '*' selects all columns

        Returns:
            Boolean value which is True if dataset contains only
            binary values.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # test
        isbinary = ((data == data.astype(bool)).sum() == data.size)

        return isbinary

    @catalog.custom(
        name     = 'test_gauss',
        title    = None,
        category = ('dataset', 'evaluation'),
        plot     = 'none'
    )
    def _get_test_gauss(self, cols: str = '*', mu: float = 0.0,
        sigma: float = 1.0, delta: float = 0.05):
        """Test if dataset contains gauss normalized data per columns.

        Args:
            cols (str, optional): name of column filter used to
                select columns.
                default: '*' selects all columns
            mu (float, optional): parameter of the gauss distribution
                which is compared to the mean values of the data.
                default: 0.0
            sigma (float, optional): parameter of the gauss distribution
                which is compared to the standard deviation of the data.
                default 1.0
            delta (float, optional): allowed maximum difference
                to distribution parameters per column.
                default: 0.05

        Returns:
            Boolean value which is True if the following conditions are
            satisfied:
            (1) The mean value of every selected column over a given
                number of random selected samples has an absolute
                difference to mu, which is lower than delta.
            (2) The standard deviation of every selected column over a
                given number of random selected samples has an absolute
                difference to sigma, which is lower than delta.

        """

        # get numpy array with test data
        data = self._get_data(cols = cols)

        # test mean values of columns
        mean = data.mean(axis = 0)
        test = np.all(np.abs(mu - mean) < delta)
        if not test: return False

        # test standard deviations of columns
        sdev = data.std(axis = 0)
        test = np.all(np.abs(sigma - sdev) < delta)
        if not test: return False

        return True

    def save(self, *args, **kwds):
        """Export dataset to file."""
        return nemoa.dataset.save(self, *args, **kwds)

    def show(self, *args, **kwds):
        """Show dataset as image."""
        return nemoa.dataset.show(self, *args, **kwds)

    def copy(self, *args, **kwds):
        """Create copy of dataset."""
        return nemoa.dataset.copy(self, *args, **kwds)
