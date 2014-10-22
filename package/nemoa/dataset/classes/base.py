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

    _default = { 'name': None }
    _config = None
    _source = None

    def __init__(self, **kwargs):
        """Import dataset from dictionary."""
        self._set_copy(**kwargs)

    def _is_empty(self):
        """Return true if dataset is empty."""
        return not 'name' in self._config or not self._config['name']

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
        return len(self._source.keys()) > 0

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
        layers = network.get('layers', visible = True)

        # convert network node labels to common format
        nemoa.log('search network nodes in dataset sources')
        nodes_conv = {}
        nodes_lost = []
        nodes_conv_count = 0
        net_label_format = network.get('config', 'label_format')
        for layer in layers:

            # get node names of layer
            nodes = network.get('nodes', layer = layer)

            # get node labels of layer
            node_labels = []
            for node in nodes:
                node_labels.append(
                    network.get('node', node)['params']['label'])

            # convert node labels to standard label format
            conv, lost = nemoa.dataset.annotation.convert(
                node_labels, input = net_label_format)
            nodes_conv[layer] = conv
            nodes_lost += lost
            nodes_conv_count += len(nodes_conv[layer])

        # notify about lost (not convertable) nodes
        if nodes_lost:
            nemoa.log("""%s of %s network nodes could not
                be converted! (see logfile)"""
                % (len(nodes_lost), nodes_conv_count))
            nemoa.log('logfile', nemoa.common.str_to_list(nodes_lost))

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
            # TODO: if column labels are allready known
            # get columns from source config
            path = src_cnf['source']['file']
            orig_col_labels = nemoa.common.csv_get_labels(path)
            if not orig_col_labels: continue

            # set annotation format
            label_format = src_cnf['source']['columns'] \
                if 'columns' in src_cnf['source'] else 'generic:string'

            # convert column labes
            columns_conv, columns_conv_lost = \
                nemoa.dataset.annotation.convert(
                orig_col_labels, input = label_format)

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
                nemoa.log('warning', """%i of %i network nodes
                    could not be found in dataset source!
                    (see logfile)""" % (num_lost, num_all))
                for layer in nodes_lost:
                    nemoa.log('logfile', "missing nodes (layer '%s'): "
                        % (layer) + ', '.join(nodes_lost[layer]))

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
            black_list = [list[i] for i in \
                col_labels[src]['notusecols']]
            inter_col_labels = [val for val in inter_col_labels \
                if val in list and not val in black_list]

        # search network nodes in dataset columns
        self._config['columns'] = ()
        for layer in layers:
            found = 0

            for id, col in enumerate(nodes_conv[layer]):
                if not col in inter_col_labels: continue
                found += 1

                # add column (use network label and layer)
                node = network.get('nodes', layer = layer)[id]
                label = network.get('node', node)['params']['label']
                self._config['columns'] += ((layer, label), )

                for src in col_labels:
                    col_labels[src]['usecols'] \
                        += (col_labels[src]['conv'].index(col), )

            if not found:
                nemoa.log('error', """no node from network layer '%s'
                    could be found in dataset source!""" % (layer))
                nemoa.log('set', indent = '-1')
                return False

        # update source file config
        for src in col_labels:
            self._config['table'][src]['source']['usecols'] \
                = col_labels[src]['usecols']

        # Column & Row Filters

        # add column filters from network layers
        self._config['colfilter'] = {'*': ['*:*']}
        for layer in layers:
            self._config['colfilter'][layer] = [layer + ':*']

        # add row filters and partitions from sources
        self._config['rowfilter'] = {'*': ['*:*']}
        for source in self._config['table']:
            self._config['rowfilter'][source] = [source + ':*']

        # import data from csv files
        nemoa.log('import data from sources')
        nemoa.log('set', indent = '+1')
        self._source = {}
        for src in self._config['table']:
            source_config = self._config['table'][src]['source']
            path = source_config['file']
            labels = tuple(self._get_columns())
            if 'rows' in source_config and source_config['rows']:
                rowlabelcol = None
            else:
                rowlabelcol = 0
            if 'usecols' in source_config and source_config['usecols']:
                usecols = source_config['usecols']
            else:
                usecols = None
            data = nemoa.common.csv_get_data(path, labels = labels,
                rowlabelcol = rowlabelcol, usecols = usecols)

            self._source[src] = {
                'fraction': self._config['table'][src]['fraction'],
                'array': data }

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
            for src in self._source:
                allSize += self._source[src]['array'].shape[0]
            for src in self._source: self._source[src]['fraction'] = \
                float(allSize) / float(self._source[src]['array'].shape[0])
            return True
        if algorithm.lower() in ['auto']: return True
        if algorithm.lower() in ['equal']:
            frac = 1. / float(len(self._source))
            for src in self._source: self._source[src]['fraction'] = frac
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
        if len(self._source.keys()) == 1:
            source = self._source.keys()[0]
            data = self._get_source(type = 'recarray', source = source)
        else:
            data = self._get_data(size = size, output = 'recarray')

        # iterative normalize sources
        for source in self._source.keys():
            source_array = self._source[source]['array']
            if source_array == None:
                continue
            # iterative normalize columns (recarray)
            for col in source_array.dtype.names[1:]:
                mean = data[col].mean()
                sdev = data[col].std()
                self._source[source]['array'][col] = \
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

            self._set_colnames(source_columns)

            for src in self._source:

                # get data, mapping and transformation function
                data = self._source[src]['array']
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
                num_rows = self._source[src]['array']['label'].size
                col_names = ('label',) + tuple(target_columns)
                col_formats = ('<U12',) + tuple(['<f8' \
                    for x in target_columns])
                new_rec_array = numpy.recarray((num_rows,),
                    dtype = zip(col_names, col_formats))

                # set values in record array
                new_rec_array['label'] = \
                    self._source[src]['array']['label']
                for colID, colName in \
                    enumerate(new_rec_array.dtype.names[1:]):

                    # update source data columns
                    new_rec_array[colName] = \
                        (trans_array[:, colID]).astype(float)

                # set record array
                self._source[src]['array'] = new_rec_array

            self._set_colnames(target_columns)
            nemoa.log('set', indent = '-1')
            return True

        # gauss to binary data transformation
        elif algorithm.lower() in ['gausstobinary', 'binary']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._source:
                # update source per column (recarray)
                for colName in self._source[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._source[src]['array'][colName] = \
                        (self._source[src]['array'][colName] > 0.
                        ).astype(float)
            return True

        # gauss to weight in [0, 1] data transformation
        elif algorithm.lower() in ['gausstoweight', 'weight']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._source:
                # update source per column (recarray)
                for colName in self._source[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self._source[src]['array'][colName] = \
                        (2. / (1. + numpy.exp(-1. * \
                        self._source[src]['array'][colName] ** 2))
                        ).astype(float)
            return True

        # gauss to distance data transformation
        # ????
        elif algorithm.lower() in ['gausstodistance', 'distance']:
            nemoa.log('transform data using \'%s\'' % (algorithm))
            for src in self._source:
                # update source per column (recarray)
                for colName in self._source[src]['array'].dtype.names[1:]:
                    self._source[src]['array'][colName] = \
                        (1. - (2. / (1. + numpy.exp(-1. * \
                        self._source[src]['array'][colName] ** 2)))
                        ).astype(float)
            return True

        return nemoa.log('error', """could not transform data:
            unknown algorithm '%s'!""" % (algorithm))

    def _corrupt(self, data, type = None, factor = 0.5):
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

    def _format(self, data, cols = '*', output = 'array'):
        """Return data in given format.

        Args:
            cols: name of column group
                default: value '*' does not filter columns
            output: ...

        """

        # check columns
        if cols == '*': cols = self._get_columns()
        elif not len(cols) == len(set(cols)):
            return nemoa.log('error', """could not retrieve data:
                columns are not unique!""")
        elif [c for c in cols if c not in self._get_columns()]:
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
            if fmt_str == 'array':
                ret_tuple += (data[cols].view('<f8').reshape(data.size,
                    len(cols)), )
            elif fmt_str == 'recarray':
                ret_tuple += (data[['label'] + cols], )
            elif fmt_str == 'cols':
                #ret_tuple += (data.dtype.names, )
                col_list = []
                for col in cols:
                    if ':' in col:
                        col_list.append(col.split(':')[1])
                    else:
                        col_list.append(col)
                ret_tuple += (col_list, )
            elif fmt_str in ['rows', 'list']:
                ret_tuple += (data['label'].tolist(), )
        if isinstance(output, str): return ret_tuple[0]
        return ret_tuple

    #def delColFilter(self, name):
        #if name in self._config['colfilter']:
            #del self._config['colfilter'][name]
            #return True
        #return False

    #def getBccaPartition(self, **params):
        #rowLabels, data = self._get_data(output = 'list,array')
        #num_rows, numCols = data.shape

        ## check parameters
        #if 'groups' in params:
            #groups = params['groups']
        #else:
            #nemoa.log('warning', """parameter 'groups' is needed to
                #create BCCA partition!""")
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
            #return self.getBccaBiclusters(**params)

        #nemoa.log('warning', "unsupported biclustering algorithm '" + algorithm + "'!")
        #return None

    #def getBccaBiclusters(self, **params):
        #data = self._get_data(output = 'array')
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
        #data = self._get_data(output = 'array')
        #num_rows, numCols = data.shape

        ## create distance matrix using binary metric
        #distance = numpy.ones(shape = (num_rows, len(biclusters)))
        #for cID, (cRowIDs, cColIDs) in enumerate(biclusters):
            #distance[cRowIDs, cID] = 0

        #return distance

    #def getBiclusterCorrelationDistance(self, biclusters):
        ### EXPERIMENTAL!!
        #data = self._get_data(output = 'array')
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

    def _get_cache_file(self, network):
        """Return cache file path."""
        return '%sdata-%s-%s.npz' % (self._config['cache_path'],
            network.get('config', 'id'), self._config['id'])

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
        """Get meta information, parameters and data of dataset."""

        # get meta information of dataset
        if key == 'fullname': return self._get_fullname()
        if key == 'name': return self._get_name()
        if key == 'branch': return self._get_branch()
        if key == 'version': return self._get_version()
        if key == 'about': return self._get_about()
        if key == 'author': return self._get_author()
        if key == 'email': return self._get_email()
        if key == 'license': return self._get_license()
        if key == 'type': return self._get_type()

        # get dataset parameters and data
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

        # export dataset configuration and data
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'source': return self._get_source(*args, **kwargs)

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
        """Return list of strings containing column groups and labels."""
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
        for source in self._source.keys():
            labels = self._source[source]['array']['label'].tolist()
            row_names += ['%s:%s' % (source, name) for name in labels]
        return row_names

    def _get_rowgroups(self):
        return self._source.keys()

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
                        A fraction of every sample is forced to min or max
                        with equal possibility
                    default: Value None equals to 'no'
                second entry of tuple: noise factor
                    float in interval [0, 1] describing the strengt
                    of the noise. The influence of the parameter
                    depends on the noise type
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
        for source in self._source.keys():
            if size > 0:
                src_data = self._get_source(type = 'recarray',
                    source = source, size = size + 1, rows = rows)
            else:
                src_data = self._get_source(type = 'recarray',
                    source = source, rows = rows)
            if src_data == False or src_data.size == 0: continue
            src_stack += (src_data, )
        if not src_stack: return nemoa.log('error',
            'could not get data: no valid data sources found!')
        data = numpy.concatenate(src_stack)

        # (optional) shuffle data and correct size
        if size:
            numpy.random.shuffle(data)
            data = data[:size]

        # format data
        if isinstance(cols, str):
            fmt_data = self._format(data,
                cols = self._get_columns(cols),
                output = output)
        elif isinstance(cols, list):
            fmt_data = self._format(data,
                cols = cols,
                output = output)
        elif isinstance(cols, tuple):
            fmt_data = tuple([self._format(data,
                cols = self._get_columns(col_filter),
                output = output) for col_filter in cols])
        else:
            return nemoa.log('error', """could not get data:
                invalid argument for columns!""")

        # Corrupt data (optional)
        return self._corrupt(fmt_data, \
            type = noise[0], factor = noise[1])

    def _get_value(self, row = None, col = None):
        """get single value from dataset."""
        return float(self._get_data(cols = [col], rows = [row]))

    def _get_copy(self, key = None, *args, **kwargs):
        """get dataset copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'source': self._get_source() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'source': return self._get_source(*args, **kwargs)

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

    def _get_source(self, type = 'dict', source = None, size = 0,
        rows = '*'):
        """Get data from sources.

        Args:
            type (string, optional): 'dict' or 'recarray'
            source: name of data source to get data from
            size: number of random choosen samples to return
                default: value 0 returns all samples of given source
            rows: string describing a row filter using wildcards
                default: value '*' selects all rows

        Returns:
            Dictionary with source data OR numpy recarray with data
            from a single source.

        """

        if type == 'dict': return copy.deepcopy(self._source)
        if type == 'recarray':

            # check source
            if not isinstance(source, str) \
                or not source in self._source \
                or not isinstance(self._source[source]['array'],
                numpy.ndarray):
                return nemoa.log('error', """could not retrieve data:
                    invalid source: '%s'!""" % (source))

            # get valid row names from row filter
            if isinstance(rows, str):

                # check row Filter
                if not rows in self._config['rowfilter']:
                    return nemoa.log('error', """could not retrieve
                        data: invalid row filter: '%s'!""" % (rows))

                # get row filter
                row_filter = self._config['rowfilter'][rows]

            elif isinstance(rows, list):
                # TODO filter list to valid row names
                row_filter = rows

            # get filtered source array
            if '*:*' in row_filter or source + ':*' in row_filter:
                src_array = self._source[source]['array']
            else:
                row_filter_filtered = [
                    row.split(':')[1] for row in row_filter
                    if row.split(':')[0] in [source, '*']]
                row_select = numpy.asarray([
                    rowid for rowid, row in enumerate(
                    self._source[source]['array']['label'])
                    if row in row_filter_filtered])
                if row_select.size == 0: return row_select
                src_array = numpy.take(self._source[source]['array'],
                    row_select)

            # stratify and return data as numpy record array
            if size == 0 or size == None: return src_array
            src_frac = self._source[source]['fraction']
            row_select = numpy.random.randint(src_array.size,
                size = round(src_frac * size))
            return numpy.take(src_array, row_select)

    def set(self, key = None, *args, **kwargs):
        """Set meta information, parameters and data of dataset."""

        # set meta information of dataset
        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'branch': return self._set_branch(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)
        if key == 'about': return self._set_about(*args, **kwargs)
        if key == 'author': return self._set_author(*args, **kwargs)
        if key == 'email': return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)

        # modify dataset parameters and data
        if key == 'colfilter': return self._set_colfilter(**kwargs)

        # import dataset configuration and source data
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'source': return self._set_source(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

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

    def _set_colnames(self, colnames):
        """Set column names from list of strings."""

        self._config['columns'] = tuple()
        for col in colnames:
            if ':' in col:
                self._config['columns'] += (col.split(':'), )
            else:
                self._config['columns'] += (('', col), )
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
        if source: retval &= self._set_source(source)

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
        self._source = {}

        return True

    def _set_source(self, source = None):
        """Set source data of dataset.

        Args:
            source (dict or None, optional): dataset source data

        Returns:
            Bool which is True if and only if no error occured.

        """

        if not source: return True
        nemoa.common.dict_merge(copy.deepcopy(source), self._source)

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

    #def addRowFilter(self, name, filter):
        ## create unique name for filter
        #filterName = name
        #i = 1
        #while filterName in self._config['rowfilter']:
            #i += 1
            #filterName = '%s.%i' % (name, i)

        ## TODO: check filter
        #self._config['rowfilter'][filterName] = filter
        #return filterName

    #def delRowFilter(self, name):
        #if name in self._config['rowfilter']:
            #del self._config['rowfilter'][name]
            #return True
        #return False
