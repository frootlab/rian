#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, copy, os, re, scipy.cluster.vq, csv

class dataset:
    """Base class for datasets"""

    # Configuration

    def __init__(self, config = {}, **kwargs):
        """Set configuration of dataset from dictionary."""
        self.cfg = None
        self.setConfig(config)
        self.data = {}

    def setConfig(self, config):
        """Set configuration of dataset from dictionary."""
        self.cfg = config.copy()
        return True

    def getConfig(self):
        """Return configuration as dictionary."""
        return self.cfg.copy()

    def getName(self):
        """Return name of dataset."""
        return self.cfg['name'] if 'name' in self.cfg else ''

    def isEmpty(self):
        """Return true if dataset is empty."""
        return not 'name' in self.cfg or not self.cfg['name']

    def configure(self, network, useCache = False, **kwargs):
        """Configure dataset to a given network object

        Keyword arguments:
            network -- nemoa network object
            useCache -- shall data be cached
        """

        nemoa.log('info', 'configure dataset: \'%s\'' % (self.getName()))
        nemoa.setLog(indent = '+1')

        # load data from cachefile (if caching is used and cachefile exists)
        cacheFile = self.searchCacheFile(network) if useCache else None
        if cacheFile and self.load(cacheFile):
            nemoa.log('info', 'load cachefile: \'%s\'' % (cacheFile))

            # preprocess data
            if 'preprocessing' in self.cfg.keys():
                self.preprocessData(**self.cfg['preprocessing'])
            nemoa.setLog(indent = '-1')
            return True

        # create table with one record for every single dataset files 
        if not 'table' in self.cfg:
            conf = self.cfg.copy()
            self.cfg['table'] = {}
            self.cfg['table'][self.cfg['name']] = conf
            self.cfg['table'][self.cfg['name']]['fraction'] = 1.0

        ################################################################
        # Annotation                                                   #
        ################################################################

        # get nodes from network and convert to common format
        if network.cfg['type'] == 'auto':
            netGroups = {'v': None}
        else:
            # get grouped network node labels and label format
            netGroups = network.getNodeGroups(type = 'visible')

            netGroupsOrder = []
            for layer in netGroups:
                netGroupsOrder.append((network.layer(layer)['id'], layer))
            netGroupsOrder = sorted(netGroupsOrder)

            # convert network node labels to common format
            nemoa.log('info', 'search network nodes in dataset sources')
            convNetGroups = {}
            convNetGroupsLost = {}
            convNetNodes = []
            convNetNodesLost = []
            netLblFmt = network.cfg['label_format']
            for id, group in netGroupsOrder:
                convNetGroups[group], convNetGroupsLost[group] = \
                    nemoa.annotation.convert(netGroups[group], input = netLblFmt)
                convNetNodes += convNetGroups[group]
                convNetNodesLost += convNetGroupsLost[group]

            # notify if any network node labels could not be converted
            if convNetNodesLost:
                nemoa.log('info', """%s of %s network nodes
                    could not be converted! (see logfile)"""
                    % (len(convNetNodesLost), len(convNetNodes)))
                ## 2DO get original node labels for log file
                nemoa.log('logfile', nemoa.common.strToList(convNetNodesLost))

        # get columns from dataset files and convert to common format
        colLabels = {}
        nemoa.log('info', 'configure data sources')
        nemoa.setLog(indent = '+1')
        for src in self.cfg['table']:
            nemoa.log('info', """
                configure '%s'""" % (src))
            srcCnf = self.cfg['table'][src]

            # get column labels from csv-file
            if 'csvtype' in srcCnf['source']:
                csvType = srcCnf['source']['csvtype'].strip().lower()
            else: csvType = None
            origColLabels = nemoa.common.csvGetColLabels(
                srcCnf['source']['file'], type = csvType)

            # set annotation format
            format = srcCnf['source']['columns'] \
                if 'columns' in srcCnf['source'] else 'generic:string'

            # convert column labes
            convColLabels, convColLabelsLost = \
                nemoa.annotation.convert(origColLabels, input = format)

            # notify if any dataset columns could not be converted
            if convColLabelsLost:
                nemoa.log("warning", 
                    "%i of %i dataset columns could not be converted! (logfile)"
                        % (len(convColLabelsLost), len(convColLabels)))
                nemoa.log("logfile", ", ".join([convColLabels[i] \
                    for i in convColLabelsLost]))

            if not network.cfg['type'] == 'auto':

                # search converted network nodes in converted column labels
                numLost = 0
                numAll = 0
                lostNodes = {}
                for id, group in netGroupsOrder:
                    lostNodesConv = \
                        [val for val in convNetGroups[group] \
                        if val not in convColLabels]
                    numAll += len(convNetGroups[group])
                    if not lostNodesConv: continue
                    numLost += len(lostNodesConv)

                    # get original labels
                    lostNodes[group] = [netGroups[group][
                        convNetGroups[group].index(val)] for val in lostNodesConv]

                # notify if any network nodes could not be found
                if numLost:
                    nemoa.log("warning", """
                        %i of %i network nodes could not be found in
                        dataset source! (logfile)""" % (numLost, numAll))
                    for group in lostNodes:
                        nemoa.log("logfile", """
                            missing nodes (group %s): """ % (group)
                            + ", ".join(lostNodes[group]))

            # prepare dictionary for column source ids
            colLabels[src] = {
                'conv': convColLabels,
                'usecols': (),
                'notusecols': convColLabelsLost }

        nemoa.setLog(indent = '-1')

        # intersect converted dataset column labels
        interColLabels = colLabels[colLabels.keys()[0]]['conv']
        for src in colLabels:
            list = colLabels[src]['conv']
            blackList = [list[i] for i in colLabels[src]['notusecols']]
            interColLabels = [val for val in interColLabels \
                if val in list and not val in blackList]

        # if network type is 'auto', set network visible nodes
        # to intersected data from database files (without label column)
        if network.cfg['type'] == 'auto':
            netGroups['v'] = [label for label in interColLabels \
                if not label == 'label']
            convNetGroups = netGroups

        # search network nodes in dataset columns
        self.cfg['columns'] = ()
        for groupid, group in netGroupsOrder:
            found = 0

            for id, col in enumerate(convNetGroups[group]):
                if not col in interColLabels:
                    continue
                found += 1

                # add column (use network label and group)
                self.cfg['columns'] += ((group, netGroups[group][id]), )
                for src in colLabels: colLabels[src]['usecols'] \
                    += (colLabels[src]['conv'].index(col), )
            if not found:
                nemoa.log('error', """
                    no node from network group '%s'
                    could be found in dataset source!
                    """ % (group))
                nemoa.setLog(indent = '-1')
                return False

        # update source file config
        for src in colLabels: self.cfg['table'][src]['source']['usecols'] \
            = colLabels[src]['usecols']

        ################################################################
        # Column & Row Filters                                         #
        ################################################################

        # add column filters and partitions from network node groups
        self.cfg['colFilter'] = {'*': ['*:*']}
        self.cfg['colPartitions'] = {'groups': []}
        for group in netGroups:
            self.cfg['colFilter'][group] = [group + ':*']
            self.cfg['colPartitions']['groups'].append(group)

        # add row filters and partitions from sources
        self.cfg['rowFilter'] = {'*': ['*:*']}
        self.cfg['rowPartitions'] = {'source': []}
        for source in self.cfg['table']:
            self.cfg['rowFilter'][source] = [source + ':*']
            self.cfg['rowPartitions']['source'].append(source)

        ################################################################
        # Import data from CSV-files into numpy arrays                 #
        ################################################################

        # import data from sources
        nemoa.log('info', 'import data from sources')
        nemoa.setLog(indent = '+1')
        self.data = {}
        for src in self.cfg['table']:
            self.data[src] = {
                'fraction': self.cfg['table'][src]['fraction'],
                'array': self.csvGetData(src) }
        nemoa.setLog(indent = '-1')

        # save cachefile
        if useCache:
            cacheFile = self.createCacheFile(network)
            nemoa.log('info', 'save cachefile: \'%s\'' % (cacheFile))
            self.save(cacheFile)

        # preprocess data
        if 'preprocessing' in self.cfg.keys():
            self.preprocessData(**self.cfg['preprocessing'])

        nemoa.setLog(indent = '-1')
        return True

    ####################################################################
    # Data preprocessing                                               #
    ####################################################################

    def preprocessData(self, **kwargs):
        """Data preprocessing.

        Keyword Arguments:
            stratify -- see algorithm in stratifyData
            normalize -- see algorithm in normalizeData
            transform -- see algorithm in transformData

        Description:
            Process stratification, normalization and transformation.
        """

        nemoa.log('info', 'preprocessing data')
        nemoa.setLog(indent = '+1')
        if 'stratify'  in kwargs.keys(): self.stratifyData(kwargs['stratify'])
        if 'normalize' in kwargs.keys(): self.normalizeData(kwargs['normalize'])
        if 'transform' in kwargs.keys(): self.transformData(kwargs['transform'])
        nemoa.setLog(indent = '-1')

        return True

    def stratifyData(self, algorithm = 'auto'):
        """Stratify data.

        Keyword arguments:
            algorithm -- name of algorithm used for stratification
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
        nemoa.log('info', 'stratify data using \'%s\'' % (algorithm))

        if algorithm.lower() in ['auto']:
            return True
        if algorithm.lower() in ['equal']:
            frac = 1.0 / float(len(self.data))
            for src in self.data:
                self.data[src]['fraction'] = frac
        return True

    def normalizeData(self, algorithm = 'gauss'):
        """Normalize stratified data

        Keyword arguments:
            algorithm -- name of algorithm used for data normalization
                'gauss':
                    Gaussian normalization (aka z-transformation)
        """

        nemoa.log('info', 'normalize data using \'%s\'' % (algorithm))

        if algorithm.lower() in ['gauss', 'z-trans']:

            # get data for calculation of mean and variance
            # for single source datasets take all data
            # for multi source datasets take a big bunch of stratified data
            if len(self.data.keys()) > 1: data = \
                self.getData(size = 1000000, output = 'recarray')
            else: data = self.getSingleSourceData(source = self.data.keys()[0])

            # iterative update sources
            # get mean and standard deviation per column (recarray)
            # and update the values
            for src in self.data:
                if self.data[src]['array'] == None: continue
                for col in self.data[src]['array'].dtype.names[1:]:
                    self.data[src]['array'][col] = \
                        (self.data[src]['array'][col] - data[col].mean()) \
                        / data[col].std()
            return True

        return False

    def transformData(self, algorithm = 'system', system = None, mapping = None, **kwargs):
        """Transform dataset.

        Keyword Arguments:
            algorithm -- name of algorithm used for data transformation
                'system':
                    Transform data using nemoa system instance
                'gaussToBinary':
                    Transform Gauss distributed values to binary values in {0, 1}
                'gaussToWeight':
                    Transform Gauss distributed values to weights in [0, 1]
                'gaussToDistance':
                    Transform Gauss distributed values to distances in [0, 1]
            system -- nemoa system instance (nemoa object root class 'system')
                used for model based transformation of data
            mapping -- ...
        """

        if not isinstance(algorithm, str): return False
        if algorithm.lower() == 'system':
            if not nemoa.type.isSystem(system): return nemoa.log('error',
                """could not transform data using system:
                parameter 'system' is invalid!""")
            nemoa.log('info', 'transform data using system \'%s\'' % (system.getName()))
            nemoa.setLog(indent = '+1')

            if mapping == None: mapping = system.getMapping()
            sourceColumns = system.getUnits(group = mapping[0])[0]
            targetColumns = system.getUnits(group = mapping[-1])[0]
            self.setColLabels(sourceColumns)
            for src in self.data:
                data = self.data[src]['array']
                dataArray = data[sourceColumns].view('<f8').reshape(
                    data.size, len(sourceColumns))
                transArray = system.mapData(dataArray, mapping = mapping, **kwargs)

                # create empty record array
                numRows = self.data[src]['array']['label'].size
                colNames = ('label',) + tuple(targetColumns)
                colFormats = ('<U12',) + tuple(['<f8' for x in targetColumns])
                newRecArray = numpy.recarray((numRows,),
                    dtype = zip(colNames, colFormats))

                # set values in record array
                newRecArray['label'] = self.data[src]['array']['label']
                for colID, colName in enumerate(newRecArray.dtype.names[1:]):

                    # update source data columns
                    newRecArray[colName] = (transArray[:, colID]).astype(float)

                # set record array
                self.data[src]['array'] = newRecArray

            self.setColLabels(targetColumns)
            nemoa.setLog(indent = '-1')
            return True
        elif algorithm.lower() in ['gausstobinary', 'binary']:
            nemoa.log('info', 'transform data using \'%s\'' % (algorithm))
            for src in self.data:
                # update source per column (recarray)
                for colName in self.data[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self.data[src]['array'][colName] = \
                        (self.data[src]['array'][colName] > 0.0).astype(float)
            return True
        elif algorithm.lower() in ['gausstoweight', 'weight']:
            nemoa.log('info', 'transform data using \'%s\'' % (algorithm))
            for src in self.data:
                # update source per column (recarray)
                for colName in self.data[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self.data[src]['array'][colName] = \
                        (2.0 / (1.0 + numpy.exp(-1.0 * \
                        self.data[src]['array'][colName] ** 2))).astype(float)
            return True
        elif algorithm.lower() in ['disttoweight', 'dist']:
            nemoa.log('info', 'transform data using \'%s\'' % (algorithm))
            for src in self.data:
                # update source per column (recarray)
                for colName in self.data[src]['array'].dtype.names[1:]:
                    # update source data columns
                    self.data[src]['array'][colName] = \
                        (1.0 - (2.0 / (1.0 + numpy.exp(-1.0 * \
                        self.data[src]['array'][colName] ** 2)))).astype(float)
            return True

        return nemoa.log('error',
            """could not transform data:
            unknown algorithm '%s'!""" % (algorithm))

    def getValue(self, row = None, col = None):
        """Return single value from dataset."""
        retVal = self.getData(cols = ([col]), output = 'list,array')
        return retVal[1][retVal[0].index(row)]

    def getData(self, size = 0, rows = '*', cols = '*',
        output = 'array', corruption = None, corruptionFactor = 0.0):
        """Return a given number of stratified samples.

        Keyword Arguments:
            size -- Number of samples
                default: value 0 returns all samples unstratified
            rows -- string describing row filter
                default: value '*' selects all rows
            cols -- name of column group
                default: value '*' selects all columns
            output -- tuple of strings describing data output. Supported strings:
                'array': numpy array just containing data
                'recarray': numpy record array
                'cols': list with column names
                'rows': list with row names
        """

        # Stratification and row filtering
        srcStack = ()
        for source in self.data.keys():
            srcData = self.getSingleSourceData(source,
                size = size, rows = rows)
            if srcData == False or srcData.size == 0: continue
            srcStack += (srcData, )
        if not srcStack: return nemoa.log('error',
            'could not get data: no valid data sources found!')
        data = numpy.concatenate(srcStack)
        if size: numpy.random.shuffle(data)

        # Optionally corrupt data
        # to improve stability in stochastical learning
        if not corruption == None: data = \
            getCorruptedData(data, algorithm = corruption, corruptionFactor = 0.5)

        # Format data
        if isinstance(cols, str): return self.getFormatedData(data,
            cols = self.getColLabels(cols), output = output)
        elif isinstance(cols, list): return self.getFormatedData(data,
            cols = cols, output = output)
        elif isinstance(cols, tuple): return tuple([self.getFormatedData(data,
            cols = self.getColLabels(grp), output = output) for grp in cols])
        return nemoa.log('error',
            'could not get data: invalid argument for columns!')

    def getSingleSourceData(self, source, size = 0, rows = '*'):
        """Return numpy recarray with data from a single source.

        Keyword Arguments:
            source -- name of data source to get data from
            size -- number of random choosen samples to return
                default: value 0 returns all samples of given source
            rows -- string describing a row filter using wildcards
                default: value '*' selects all rows
        """

        # Check source
        if not isinstance(source, str) \
            or not source in self.data \
            or not isinstance(self.data[source]['array'], numpy.ndarray): \
            return nemoa.log('error',
            "could not retrieve data: invalid source: '%s'!" % (source))

        # Check row Filter
        if not rows in self.cfg['rowFilter']: return nemoa.log('error',
            "could not retrieve data: invalid row filter: '%s'!" % (rows))

        # Apply row filter
        if rows == '*' or source + ':*' in self.cfg['rowFilter'][rows]:
            srcArray = self.data[source]['array']
        else:
            rowFilter = self.cfg['rowFilter'][rows]
            rowFilterFiltered = [
                row.split(':')[1] for row in rowFilter
                        if row.split(':')[0] in [source, '*']]
            rowSelect = numpy.asarray([
                rowid for rowid, row in enumerate(self.data[source]['array']['label'])
                    if row in rowFilterFiltered])
            if rowSelect.size == 0: return rowSelect
            srcArray = numpy.take(self.data[source]['array'], rowSelect)

        # Stratify and return data as numpy record array
        if size == 0 or size == None: return srcArray
        srcFrac = self.data[source]['fraction']
        rowSelect = numpy.random.randint(srcArray.size,
            size = round(srcFrac * size))
        return numpy.take(srcArray, rowSelect)

    def getCorruptedData(self, data, algorithm = 'mn', factor = 0.5):
        """Return numpy array with (partly) corrupted data.

        Keyword Arguments:
            algorithm -- string describing algorithm for corruption
                'mn': Masking Noise
                    A fraction of every sample is forced to zero
                'gs': Gaussian Noise
                    Additive isotropic Gaussian noise
                'sp': Salt-and-pepper noise
                    A fraction of every sample is forced to min or max
                    with equal possibility
            factor -- float in [0, 1] describing the strengt of the corruption
                The influence of the parameter depends on the used algorithm
        """

        if algorithm == None: return data
        elif algorithm == 'mn': return data * numpy.random.binomial(
            size = data.shape, n = 1, p = 1 - factor)
        elif algorithm == 'gs': return data * numpy.random.normal(
            size = data.shape, loc = 0.0, scale = factor)
        #elif algorithm == 'sp': return
        else: return nemoa.log('error',
            "unkown corruption algorithm '%s'!" % (algorithm))

    def getFormatedData(self, data, cols = '*', output = 'array'):
        """Return data in given format.

        Keyword Arguments:
            cols -- name of column group
                default: value '*' does not filter columns
            format"""
        
        # check columns
        if cols == '*': cols = self.getColLabels()
        elif not len(cols) == len(set(cols)): return nemoa.log('error',
            "could not retrieve data: columns are not unique!")
        elif [c for c in cols if c not in self.getColLabels()]: \
            return nemoa.log('error',
            "could not retrieve data: unknown columns!")
    
        # check format
        if isinstance(output, str): fmtTuple = (output, )
        elif isinstance(output, tuple): fmtTuple = output
        else: return nemoa.log('error',
            "could not retrieve data: inval 'format' argument!")

        # format data
        retTuple = ()
        for fmtStr in fmtTuple:
            if fmtStr == 'array': retTuple += (
                data[cols].view('<f8').reshape(data.size, len(cols)), )
            elif fmtStr == 'recarray': retTuple += (
                data[['label'] + cols], )
            elif fmtStr == 'cols': retTuple += (
                [col.split(':')[1] for col in cols], )
            elif fmtStr in ['rows', 'list']: retTuple += (
                data['label'].tolist(), )
        if isinstance(output, str): return retTuple[0]
        return retTuple

    # Column Labels and Column Groups

    def getColLabels(self, group = '*'):
        """Return list of strings containing column groups and labels."""
        if group == '*': return ['%s:%s' % (col[0], col[1])
            for col in self.cfg['columns']]
        if not group in self.cfg['colFilter']: return []
        colFilter = self.cfg['colFilter'][group]
        labels = []
        for col in self.cfg['columns']:
            if ('*:*') in colFilter \
                or ('%s:*' % (col[0])) in colFilter \
                or ('*:%s' % (col[1])) in colFilter \
                or ('%s:%s' % (col[0], col[1])) in colFilter:
                labels.append('%s:%s' % (col[0], col[1]))
        return labels

    def setColLabels(self, labels):
        """Set column labels from list of strings."""
        self.cfg['columns'] = tuple([col.split(':') for col in labels])
        return True

    #def getRowLabels(self):
        #labelStack = ()
        #for source in self.data:
            #labelStack += (self.data[source]['array']['label'],)
        #labels = numpy.concatenate(labelStack).tolist()
        #return labels

    def getColGroups(self):
        groups = {}
        for group, label in self.cfg['columns']:
            if not group in groups: groups[group] = []
            groups[group].append(label)
        return groups

    #def getRowGroups(self):
        #pass

    #
    # FILTERS
    #

    #def addRowFilter(self, name, filter):
        ## create unique name for filter
        #filterName = name
        #i = 1
        #while filterName in self.cfg['rowFilter']:
            #i += 1
            #filterName = '%s.%i' % (name, i)

        ## TODO: check filter
        #self.cfg['rowFilter'][filterName] = filter
        #return filterName

    #def delRowFilter(self, name):
        #if name in self.cfg['rowFilter']:
            #del self.cfg['rowFilter'][name]
            #return True
        #return False

    #def getRowFilter(self, name):
        #if not name in self.cfg['rowFilter']:
            #nemoa.log("warning", "unknown row filter '" + name + "'!")
            #return []
        #return self.cfg['rowFilter'][name]

    #def getRowFilterList(self):
        #return self.cfg['rowFilter'].keys()

    #def addColFilter(self):
        #pass

    #def delColFilter(self, name):
        #if name in self.cfg['colFilter']:
            #del self.cfg['colFilter'][name]
            #return True
        #return False

    #def getColFilters(self):
        #return self.cfg['colFilter']

    #
    # PARTITIONS
    #

    #def addRowPartition(self, name, partition):
        #if name in self.cfg['rowPartitions']:
            #nemoa.log("warning", "row partition '" + name + "' allready exists!")

        ## create unique name for partition
        #partitionName = name
        #i = 1
        #while partitionName in self.cfg['rowPartitions']:
            #i += 1
            #partitionName = '%s.%i' % (name, i)

        #filterNames = []
        #for id, filter in enumerate(partition):
            #filterNames.append(
                #self.addRowFilter('%s.%i' % (name, id + 1), filter))

        #self.cfg['rowPartitions'][partitionName] = filterNames
        #return partitionName

    #def delRowPartition(self, name):
        #pass

    #def getRowPartition(self, name):
        #if not name in self.cfg['rowPartitions']:
            #nemoa.log("warning", "unknown row partition '" + name + "'!")
            #return []
        #return self.cfg['rowPartitions'][name]

    #def getRowPartitionList(self):
        #return self.cfg['rowPartitions'].keys()

    #def createRowPartition(self, algorithm = 'bcca', **params):
        #if algorithm == 'bcca':
            #partition = self.getBccaPartition(**params)
        #else:
            #nemoa.log("warning", "unknown partition function '%s'")

        ## add partition
        #return self.addRowPartition(algorithm, partition)

    #def getBccaPartition(self, **params):
        #rowLabels, data = self.getData(output = 'list,array')
        #numRows, numCols = data.shape

        ## check parameters
        #if 'groups' in params:
            #groups = params['groups']
        #else:
            #nemoa.log("warning", "parameter 'groups' is needed to create BCCA partition!")
            #return []

        ## get BCCA biclusters
        #biclusters = self.getBccaBiclusters(**params)

        ## get bicluster distances
        #distance = self.getBiclusterDistance(biclusters, **params)

        ## cluster samples using k-means
        #nemoa.log("info", 'cluster distances using k-means with k = %i' % (groups))
        #clusters = self.getClusters(algorithm = 'k-means', data = distance, k = groups)
        #cIDs = numpy.asarray(clusters)
        #partition = []
        #for cID in range(groups):
            #partition.append(numpy.where(cIDs == cID)[0].tolist())

        ## get labels
        #labeledPartition = []
        #for pID, c in enumerate(partition):
            #labels = []
            #for sID in c:
                #labels.append(rowLabels[sID])
            #labeledPartition.append(list(set(labels)))

        #return labeledPartition

    #
    # CLUSTERING
    #

    #def getClusters(self, algorithm = 'k-means', **params):
        #if algorithm == 'k-means':
            #return self.getKMeansClusters(**params)

        #nemoa.log("warning", "unsupported clustering algorithm '" + algorithm + "'!")
        #return None

    #def getKMeansClusters(self, data, k = 3):
        #return scipy.cluster.vq.vq(data, scipy.cluster.vq.kmeans(data, k)[0])[0]

    #
    # BICLUSTERING
    #

    #def getBiclusters(self, algorithm = 'bcca', **params):
        #if algorithm == 'bcca':
            #return getBccaBiclusters(**params)

        #nemoa.log("warning", "unsupported biclustering algorithm '" + algorithm + "'!")
        #return None

    #def getBccaBiclusters(self, **params):
        #data = self.getData(output = 'array')
        #numRows, numCols = data.shape

        ## check params
        #if not 'threshold' in params:
            #nemoa.log("info", "param 'threshold' is needed for BCCA Clustering!")
            #return []
        #if not ('minsize' in params or 'size' in params):
            #nemoa.log("info", "param 'size' or 'minsize' is needed for BCCA Clustering!")
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
        #nemoa.log("info", 'detecting bi-correlation clusters')
        #startTime = time.time()

        #biclusters = []
        #for i in range(numCols - 1):
            #for j in range(i + 1, numCols):

                #npRowIDs = numpy.arange(numRows)

                ## drop rows until corr(i, j) > sigma or too few rows are left
                #rowIDs = npRowIDs.tolist()
                #corr = numpy.corrcoef(data[:,i], data[:,j])[0, 1]

                #while (size and len(rowIDs) > size) or \
                    #(not size and len(rowIDs) > minsize and corr < threshold):
                    #rowCorr = numpy.zeros(len(rowIDs))

                    #for id in range(len(rowIDs)):
                        #mask = rowIDs[:id] + rowIDs[id:][1:]
                        #rowCorr[id] = numpy.corrcoef(data[mask, i], data[mask, j])[0, 1]

                    #rowMaxID = rowCorr.argmax()
                    #corr = rowCorr[rowMaxID]
                    #rowIDs.pop(rowMaxID)

                #if i == 0 and j == 1:
                    #elapsed = time.time() - startTime
                    #estimated = elapsed * numCols ** 2 / 2
                    #nemoa.log("info", 'estimated duration: %.1fs' % (estimated))

                #if corr < threshold:
                    #continue

                # expand remaining rows over columns
                #colIDs = [i, j]
                #for id in [id for id in range(numCols) if id not in colIDs]:
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
            #nemoa.log("info", 'found %i biclusters with: correlation > %.2f, number of samples = %i' \
                #% (len(biclusters), threshold, size))
        #else:
            #nemoa.log("info", 'found %i biclusters with: correlation > %.2f, number of samples > %i' \
                #% (len(biclusters), threshold, minsize - 1))

        #return biclusters

    #
    # BICLUSTER DISTANCES
    #

    #def getBiclusterDistance(self, biclusters, **params):
        #if 'distance' in params:
            #type = params['distance']
        #else:
            #type = 'correlation'

        #if type == 'hamming':
            #return self.getBiclusterHammingDistance(biclusters)
        #elif type == 'correlation':
            #return self.getBiclusterCorrelationDistance(biclusters)

        #nemoa.log("warning", "   unknown distance type '" + type + "'!")
        #return None

    #def getBiclusterHammingDistance(self, biclusters):
        #data = self.getData(output = 'array')
        #numRows, numCols = data.shape

        ## create distance matrix using binary metric
        #distance = numpy.ones(shape = (numRows, len(biclusters)))
        #for cID, (cRowIDs, cColIDs) in enumerate(biclusters):
            #distance[cRowIDs, cID] = 0

        #return distance

    #def getBiclusterCorrelationDistance(self, biclusters):
        ### EXPERIMENTAL!!
        #data = self.getData(output = 'array')
        #numRows, numCols = data.shape

        ## calculate differences in correlation
        #corrDiff = numpy.zeros(shape = (numRows, len(biclusters)))
        #for cID, (cRowIDs, cColIDs) in enumerate(biclusters):
            
            ## calculate mean correlation within bicluster
            #cCorr = self.getMeanCorr(data[cRowIDs, :][:, cColIDs])
            
            ## calculate mean correlation by appending single rows
            #for rowID in range(numRows):
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
        #for i in range(array.shape[1] - 1):
            #for j in range(i + 1, array.shape[1]):
                #cCorr = numpy.append(cCorr, numpy.corrcoef(array[:, i], array[:, j])[0, 1])

        #return numpy.mean(cCorr)

    def csvGetData(self, name):
        conf    = self.cfg['table'][name]['source']
        file    = conf['file']
        delim   = conf['delimiter'] if 'delimiter' in conf \
            else nemoa.common.csvGetDelimiter(file)
        cols    = conf['usecols']
        names   = tuple(self.getColLabels())
        formats = tuple(['<f8' for x in names])
        if not 'rows' in conf or conf['rows']:
            cols = (0,) + cols
            names = ('label',) + names
            formats = ('<U12',) + formats
        dtype = {'names': names, 'formats': formats}

        nemoa.log('info', "import data from csv file: " + file)

        try:
            #data = numpy.genfromtxt(file, skiprows = 1, delimiter = delim,
                #usecols = cols, dtype = dtype)
            data = numpy.loadtxt(file, skiprows = 1, delimiter = delim,
                usecols = cols, dtype = dtype)
        except:
            nemoa.log('error', 'could not import data from file!')
            return None

        return data

    #
    # object configuration handling
    #

    def save(self, file):
        """Export dataset to numpy zip compressed file."""
        numpy.savez(file, cfg = self.cfg, data = self.data)

    def exportDataToFile(self, file, **kwargs):
        """Export data to file."""

        file = nemoa.common.getEmptyFile(file)
        type = nemoa.common.getFileExt(file).lower()

        nemoa.log('title', 'export data to file')
        nemoa.setLog(indent = '+1')

        nemoa.log('info', 'exporting data to file: \'%s\'' % (file))
        if type in ['gz', 'data']: retVal = self.save(file)
        elif type in ['csv', 'tsv', 'txt']:
            cols, data = self.getData(output = ('cols','recarray'))
            retVal = nemoa.common.csvSaveData(file, data,
                cols = [''] + cols, **kwargs)
        else: retVal = nemoa.log('error', """
            could not export dataset:
            unsupported file type '%s'""" % (type))

        nemoa.setLog(indent = '-1')
        return retVal

    def getCacheFile(self, network):
        """Return cache file path."""
        return '%sdata-%s-%s.npz' % (
            self.cfg['cache_path'], network.cfg['id'], self.cfg['id'])

    def searchCacheFile(self, network):
        """Return cache file path if existent."""
        file = self.getCacheFile(network)
        return file if os.path.isfile(file) else None

    def createCacheFile(self, network):
        """Return empty cache file if existent."""
        file = self.getCacheFile(network)
        if not os.path.isfile(file):
            basedir = os.path.dirname(file)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            with open(file, 'a'):
                os.utime(file, None)
        return file

    def load(self, file):
        npzfile = numpy.load(file)
        self.cfg  = npzfile['cfg'].item()
        self.data = npzfile['data'].item()
        return True

    def _get(self, sec = None):
        dict = {
            'data': copy.deepcopy(self.data),
            'cfg': copy.deepcopy(self.cfg)
        }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set(self, **dict):
        if 'data' in dict: self.data = copy.deepcopy(dict['data'])
        if 'cfg' in dict: self.cfg = copy.deepcopy(dict['cfg'])
        return True
