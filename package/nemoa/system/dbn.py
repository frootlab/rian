#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, time
import nemoa.system.ann

class dbn(nemoa.system.ann.ann):
    """Deep Belief Network (DBN).

    Description:
        Used for data classification and compression / decompression

    Reference:
    
    """

    def _getSystemDefaultConfig(self):
        """Return default configuration as dictionary."""
        sysModule = '.'.join(self.__module__.split('.')[2:])
        return {
            'params': {
                'visible': 'auto',
                'hidden': 'auto',
                'visibleSystem': None,
                'visibleSystemModule': 'rbm',
                'visibleSystemClass': 'grbm',
                'visibleUnitRatio': '1:2',
                'hiddenSystem': None,
                'hiddenSystemClass': 'rbm',
                'hiddenSystemModule': 'rbm',
                'hiddenUnitRatio': '2:1' },
            'optimize': {
                'schedule': None,
                'visible': None,
                'hidden': None },
            'visibleParams': { },
            'visibleInit': { }, # use defaults from visible system
            'hiddenParams': { },
            'hiddenInit': { }, # use defaults from hidden system
            }

    def _configure(self, dataset = None, network = None, **kwargs):
        """Configure system to network and dataset."""
        if not 'check' in self._config:
            self._config['check'] = {
                'config': True, 'network': False,
                'dataset': False, 'subSystems': False}
        if not network == None:
            self._setNetwork(network)
        if not dataset == None:
            self._setDataset(dataset)
        return self._isConfigured()

    def _checkNetwork(self, network):
        return self._isNetworkDBNCompatible(network)

    def _setConfig(self, config, *args, **kwargs):
        """Set configuration from dictionary."""
        nemoa.common.dictMerge(self._getSystemDefaultConfig(), self._config)
        nemoa.common.dictMerge(config, self._config)
        self._setUnits(self._getUnitsFromConfig())
        self._config['check']['config'] = True
        return True

    def _setNetwork(self, network):
        """Update units to network instance."""
        nemoa.log('info', 'get system units and links from network \'%s\'' % (network.getName()))
        self.setUnits(self._getUnitsFromNetwork(network))
        self._config['check']['network'] = True
        return True

    def _setDataset(self, dataset, *args):
        """Update units and links to dataset instance."""
        #2DO: check if data is ok for visibleSystemClass
        self._config['check']['dataset'] = True
        return True

    def _configureSubSystems(self):
        """Configure subsystems."""
        import nemoa
        nemoa.log('info', 'configure subsystems')
        nemoa.setLog(indent = '+1')
        if not 'layers' in self._params:
            nemoa.log('warning', 'could not configure subsystems: no layers have been defined')
            nemoa.setLog(indent = '-1')
            return False

        self._sub = []
        layerID = 0
        while layerID < len(self._params['layers']) - 1:
            layerA = self._params['layers'][layerID]
            layerB = self._params['layers'][layerID + 1]
            layerID += 1
            
            # get settings for current subsystem
            if 'visible' in [layerA['type'], layerB['type']]:
                sysUserConf = self._config['params']['visibleSystem']
                sysModule = self._config['params']['visibleSystemModule']
                sysClass = self._config['params']['visibleSystemClass']
            else:
                sysUserConf = self._config['params']['hiddenSystem']
                sysModule = self._config['params']['visibleSystemModule']
                sysClass = self._config['params']['visibleSystemClass']

            # get configuration for current subsystem
            if sysUserConf:
                sysConfig = nmConfig.get(type = 'system', name = sysUserConf)
                if sysConfig == None:
                    nemoa.log('error', """
                        could not configure system:
                        unknown system configuration \'%s\'
                        """ % (sysUserConf))
                    nemoa.setLog(indent = '-1')
                    return False
            else:
                sysConfig = {'package': sysModule, 'class': sysClass}

            # update configuration
            sysConfig['name'] = '%s → %s' % (layerA['name'], layerB['name'])
            if not 'params' in sysConfig:
                sysConfig['params'] = {}
            if layerID <= (len(self._params['layers']) - 1) / 2:
                sysConfig['params']['visible'] = layerA['units']
                sysConfig['params']['hidden'] = layerB['units']
            else:
                sysConfig['params']['hidden'] = layerA['units']
                sysConfig['params']['visible'] = layerB['units']

            # create subsystem
            import nemoa.system
            system = nemoa.system.new(config = sysConfig)
            nemoa.log('info', """
                adding subsystem: \'%s\' (%s units, %s links)
                """ % (system.getName(),
                len(system.getUnits(type = 'visible')) + len(system.getUnits(type = 'hidden')),
                len(system.getLinks())))
            self._sub.append(system)

        self._config['check']['subSystems'] = True
        nemoa.setLog(indent = '-1')
        return True

        nemoa.log('error', 'configuration of subsystems failed!')
        nemoa.setLog(indent = '-1')
        return False

    def _isConfigured(self):
        """Return configuration state of ANN."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    # UNITS

    def _getUnitsFromConfig(self):
        """Return tuple of list, containing the unit labels
        of visible and hidden units using configuration
        """

        # create labels for visible input and output layers
        if isinstance(self._config['params']['visible'], str) \
            and self._config['params']['visible'] == 'auto':
            lInput = ([],)
            lOutput = ([],)
        elif not isinstance(self._config['params']['visible'], int):
            lInput = ([],)
            lOutput = ([],)
        else:
            lInput = (['in:v%_i' % (nodeID) for nodeID
                in range(1, self._config['params']['visible'] + 1)],)
            lOutput = (['out:v%i' % (nodeID) for nodeID
                in range(1, self._config['params']['visible'] + 1)],)

        lHidden = self._createHiddenUnitsStackLayout(self._config['params']['hidden'])

        return lInput + lHidden + lOutput

    def _getUnitsFromNetwork(self, network):
        """Return tuple with lists of unit labels from network."""
        layers = network.layers()
        inputLayer = layers[0]
        outputLayer = layers[-1]
        visible = network.nodes(type = inputLayer) + network.nodes(type = outputLayer)
        units = (visible, )
        for layer in layers[1:-1]:
            units += (network.nodes(type = layer), )
        units += (visible, )
        return units

        #import math
        #vList = network.nodes(visible = True)
        #hList = network.nodes(visible = False)
        #print self._config['params']
        #quit()
        #vRatioStr = self._config['params']['visibleUnitRatio'].split(':')
        #vRatio = float(vRatioStr[1]) / float(vRatioStr[0])
        #hRatioStr = self._config['params']['hiddenUnitRatio'].split(':')
        #hRatio = float(hRatioStr[1]) / float(hRatioStr[0])
        #units = (vList, )
        #hSize = int(math.ceil(float(len(vList)) * vRatio))
        #hLayer = 1
        #while hSize > len(hList):
            #units += (['h%i:h%i' % (hLayer, num) for num in range(1, hSize + 1)], )
            #hSize = int(math.ceil(float(hSize) * hRatio))
            #hLayer += 1
        #units += (hList, )
        #numLayers = len(units)
        #if numLayers > 2:
            #for layerID in range(1, numLayers - 1)[::-1]:
                #hSize = len(units[layerID])
                #units += (['h%i:h%i' % (hLayer, num) for num in range(1, hSize + 1)], )
                #hLayer += 1
        #units += (vList, )

        #return units

    def _createHiddenUnitsStackLayout(self, layout):
        """Return tuple with hidden unit label lists from tuple with numbers."""
        # create labels for hidden layers
        if isinstance(layout, str) and layout == 'auto':
            lHidden = ([], ) # return empty stack if parameter layout is 'auto'
        elif not isinstance(layout, tuple):
            lHidden = ([], ) # return empty stack if parameter layout is not a tuple
        else:
            layerID = 1
            lHidden = ()
            for lSize in layout:
                if not isinstance(lSize, int):
                    lHidden = ([], )
                    break
                lHidden += (['h%i:h%i' % (layerID, nodeID) for nodeID in range(1, lSize + 1)], )
                layerID += 1
            numLayers = len(layout)
            if numLayers > 1:
                for i in range(numLayers - 1)[::-1]:
                    lSize = layout[i]
                    lHidden += (['h%i:h%i' % (layerID, nodeID) for nodeID in range(1, lSize + 1)], )
                    layerID += 1

        return lHidden

    def _setUnits(self, units):
        """Set unit labels of all layers."""
        # check units
        if not isinstance(units, tuple):
            return False
        if len(units) < 2:
            return False
        for val in units:
            if not isinstance(val, list):
                return False
        self._params['layers'] = []
        for layerID, labels in enumerate(units):
            if layerID == 0:
                name = 'input'
                type = 'visible'
            elif layerID == len(units) - 1:
                name = 'output'
                type = 'visible'
            else:
                name = 'h' + str(layerID)
                type = 'hidden'
            self._params['layers'].append(
                {'name': name, 'type': type, 'units': labels})
        return True

    def _getUnits(self):
        """Return a list with units."""
        # 2DO!!
        return []

    def _optimizeParams(self, dataset, **config):
        """Optimize system parameters."""

        # PRETRAINING USING RESTRICTED BOLTZMANN MACHINES
        self._preTraining(dataset, **config)

        # finetuning using backpropagation
        # 2DO

        return True

    def _preTraining(self, dataset, **config):
        """Pretraining system using restricted boltzmann machines."""
        nemoa.log('info', 'pretraining system')
        nemoa.setLog(indent = '+1')

        # configure subsystems
        self._configureSubSystems()

        # create copy of dataset values (before transformation)
        datasetCopy = dataset._get()

        # optimize subsystems
        for sysID in range(0, len(self._sub) / 2):
            nemoa.log('info', 'optimize subsystem %s (%s)' % (self._sub[sysID].getName(), self._sub[sysID].getType()))
            nemoa.setLog(indent = '+1')

            # link encoder and decoder system
            encSystem = self._sub[sysID]
            decSystem = self._sub[len(self._sub) - sysID - 1]

            # transform dataset with previous system / fix lower stack
            if sysID > 0:
                dataset.transformData(
                    system = self._sub[sysID - 1],
                    transformation = 'hiddenvalue',
                    colLabels = self._sub[sysID - 1].getUnits(type = 'hidden'))

            # optimize encoder system
            encSystem.initParams(dataset)
            encSystem.optimizeParams(dataset, **config)

            # copy parameters from encoder to decoder system
            nemoa.log('info', 'copy inverted system parameters to %s' % (decSystem.getName()))
            decSystem._setParams(encSystem._getInvertedParams())

            print encSystem.getParams()['v']
            print decSystem.getParams()['h']

            nemoa.setLog(indent = '-1')

        # reset data to initial state (before transformation)
        dataset._set(**datasetCopy)

        nemoa.setLog(indent = '-1')
        return True

    def _initParams(self, data = None):
        """Initialize system parameters using data.

        Not needed for multilayer ANNs since subsystems
        are initialized during optimization
        """

        return True

#class ae(dbn):
    #"""Autoencoder.
    
    #Description:
        #Used for dimensionality reduction and compression / decompression

    #Reference:
        #"Reducing the Dimensionality of Data with Neural Networks",
        #Geoffrey E. Hinton, and R. R. Salakhutdinov, Science Vol 313, July 2006
    #"""

    #def _getSystemDefaultConfig(self):
        #"""Return autoencoder default configuration as dictionary."""
        #sysModule = '.'.join(self.__module__.split('.')[2:])
        #return {
            #'params': {
                #'visible': 'auto',
                #'hidden': 'auto',
                #'visibleSystem': 'default',
                #'visibleSystemModule': 'rbm',
                #'visibleSystemClass': 'grbm',
                #'visibleUnitRatio': '1:2',
                #'hiddenSystem': 'default',
                #'hiddenSystemModule': 'rbm',
                #'hiddenSystemClass': 'rbm',
                #'hiddenUnitRatio': '2:1' },
            #'optimize': {
                #'visible': None,
                #'hidden': None } ,
            #'visibleParams': { },
            #'visibleInit': { }, # use defaults from visible system
            #'hiddenParams': { },
            #'hiddenInit': { }, # use defaults from hidden system
            #}

    #def _configure(self, config = None, network = None, dataset = None, update = False, **kwargs):
        #"""Configure autoencoder and sybsystems to network and dataset."""
        #if not 'check' in self._config:
            #self._config['check'] = {
                #'config': False, 'network': False,
                #'dataset': False, 'subSystems': False}
        #if not config == None:
            #self._setConfig(config)
        #if not network == None:
            #self._setNetwork(network, update)
        #if not dataset == None:
            #self._setDataset(dataset)
        #if self._config['check']['config'] \
            #and self._config['check']['network'] \
            #and self._config['check']['dataset']:
            #self._setSubSystems()
        #return self._isConfigured()

    #def _setConfig(self, config, *args, **kwargs):
        #"""Set configuration from dictionary."""
        #mp.dictMerge(self._getSystemDefaultConfig(), self._config)
        #mp.dictMerge(config, self._config)
        #self._setUnits(self._getUnitsFromConfig())
        #self._config['check']['config'] = True
        #return True

    #def _setNetwork(self, network, update = False, *args, **kwargs):
        #"""Update units to network instance."""
        #self.setUnits(self._getUnitsFromNetwork(network), update)
        #self._config['check']['network'] = True
        #return True

    #def _setDataset(self, dataset, *args, **kwargs):
        #"""Update units and links to dataset instance.
        #has no effect in autoencoders"""
        #if not nemoa.type.isDataset(dataset):
            #nm.log("error", "could not configure autoencoder: dataset object is not valid!")
            #return False
        #self._config['check']['dataset'] = True
        #return True

    #def _setSubSystems(self):
        #"""Configure and initialize subsystems."""
        #nm.log('info', 'configure subsystems')
        #if not 'layers' in self._params:
            #nm.log('warning', 'could not configure subsystems: no layers have been defined')
            #return False
        #self._sub = []
        #layerID = 0
        #nodes = len(self._params['layers'][0]['units'])
        #links = 0
        #errors = 0
        #while layerID < len(self._params['layers']) - 1:
            #layerA = self._params['layers'][layerID]
            #layerB = self._params['layers'][layerID + 1]
            #layerID += 1
            
            ## get configuration for subsystem
            #if layerA['type'] == 'visible' or layerB['type'] == 'visible':
                #sysConfName = self._config['params']['visibleSystem']
                #if not isinstance(sysConfName, str) or sysConfigName == 'default':
                    #sysConfig = {
                        #'package': self._config['params']['visibleSystemModule'],
                        #'class': self._config['params']['visibleSystemClass']}
                #else:
                    #sysConfig = nmConfig.get(
                        #type = 'system', name = sysConfName)
            #else:
                #sysConfName = self._config['params']['hiddenSystem']
                #if not isinstance(sysConfName, str) or sysConfigName == 'default':
                    #sysConfig = {
                        #'package': self._config['params']['hiddenSystemModule'],
                        #'class': self._config['params']['hiddenSystemClass']}
                #else:
                    #sysConfig = nmConfig.get(
                        #type = 'system', name = sysConfName)

            ## check configuration
            #if sysConfig == None:
                #nm.log('error', 'could not optimize autoencoder: could not create subsystem \'%s\'' % (sysName))
                #errors += 1
                #continue
            #if not 'params' in sysConfig:
                #sysConfig['params'] = {}

            ## set units in configuration
            #if layerID <= (len(self._params['layers']) - 1) / 2:
                #sysConfig['params']['visible'] = layerA['units']
                #sysConfig['params']['hidden'] = layerB['units']
            #else:
                #sysConfig['params']['hidden'] = layerA['units']
                #sysConfig['params']['visible'] = layerB['units']

            ## create subsystem
            #import nemoa.system
            #system = nemoa.system.new(config = sysConfig)
            #nodes += len(layerB['units'])
            #links += len(system.getLinks())
            #self._sub.append(system)

        #if not errors:
            #nm.log('info', 'total number of layers: %i' % (len(self._params['layers'])))
            #nm.log('info', 'total number of nodes: %i' % (nodes))
            #nm.log('info', 'total number of links: %i' % (links))
            #self._config['check']['subSystems'] = True
            #return True

        #nm.log('error', 'configuration of subsystems failed!')
        #return False

    #def _isConfigured(self):
        #"""Return configuration state of autoencoder."""
        #return self._config['check']['config'] \
            #and self._config['check']['network'] \
            #and self._config['check']['dataset'] \
            #and self._config['check']['subSystems']

    ## Autoencoder units

    #def _getUnitsFromConfig(self):
        #"""Return tuple of list, containing the unit labels
        #of visible and hidden units using configuration."""

        ## create labels for visible input and output layers
        #if isinstance(self._config['params']['visible'], str) \
            #and self._config['params']['visible'] == 'auto':
            #lInput = ([],)
            #lOutput = ([],)
        #elif not isinstance(self._config['params']['visible'], int):
            #lInput = ([],)
            #lOutput = ([],)
        #else:
            #lInput = (['in:v%_i' % (nodeID) for nodeID
                #in range(1, self._config['params']['visible'] + 1)],)
            #lOutput = (['out:v%i' % (nodeID) for nodeID
                #in range(1, self._config['params']['visible'] + 1)],)

        #lHidden = self._createHiddenUnitsStackLayout(self._config['params']['hidden'])

        #return lInput + lHidden + lOutput

    #def _getUnitsFromNetwork(self, network):
        #"""
        #Return tuple with lists of unit labels ([input], [h1], [h2], ..., [output])
        #using network.
        #"""
        #import math
        #vList = network.nodes(visible = True)
        #hList = network.nodes(visible = False)
        #vRatioStr = self._config['params']['visibleUnitRatio'].split(':')
        #vRatio = float(vRatioStr[1]) / float(vRatioStr[0])
        #hRatioStr = self._config['params']['hiddenUnitRatio'].split(':')
        #hRatio = float(hRatioStr[1]) / float(hRatioStr[0])
        #units = (vList, )
        #hSize = int(math.ceil(float(len(vList)) * vRatio))
        #hLayer = 1
        #while hSize > len(hList):
            #units += (['h%i:h%i' % (hLayer, num) for num in range(1, hSize + 1)], )
            #hSize = int(math.ceil(float(hSize) * hRatio))
            #hLayer += 1
        #units += (hList, )
        #numLayers = len(units)
        #if numLayers > 2:
            #for layerID in range(1, numLayers - 1)[::-1]:
                #hSize = len(units[layerID])
                #units += (['h%i:h%i' % (hLayer, num) for num in range(1, hSize + 1)], )
                #hLayer += 1
        #units += (vList, )

        #return units

    #def _createHiddenUnitsStackLayout(self, layout):

        ## create labels for hidden layers
        #if isinstance(layout, str) and layout == 'auto':
            #lHidden = ([], )
        #elif not isinstance(layout, tuple):
            #lHidden = ([], )
        #else:
            #layerID = 1
            #lHidden = ()
            #for lSize in layout:
                #if not isinstance(lSize, int):
                    #lHidden = ([], )
                    #break
                #lHidden += (['h%i:h%i' % (layerID, nodeID) for nodeID in range(1, lSize + 1)], )
                #layerID += 1
            #numLayers = len(layout)
            #if numLayers > 1:
                #for i in range(numLayers - 1)[::-1]:
                    #lSize = layout[i]
                    #lHidden += (['h%i:h%i' % (layerID, nodeID) for nodeID in range(1, lSize + 1)], )
                    #layerID += 1

        #return lHidden

    #def _setUnits(self, units):
        #"""Set unit labels of all layers."""
        ## check units
        #if not isinstance(units, tuple):
            #return False
        #if len(units) < 2:
            #return False
        #for val in units:
            #if not isinstance(val, list):
                #return False
        #self._params['layers'] = []
        #for layerID, labels in enumerate(units):
            #if layerID == 0:
                #name = 'input'
                #type = 'visible'
            #elif layerID == len(units) - 1:
                #name = 'output'
                #type = 'visible'
            #else:
                #name = 'h' + str(layerID)
                #type = 'hidden'
            #self._params['layers'].append(
                #{'name': name, 'type': type, 'units': labels})
        #return True

    #def _getUnits(self):
        #"""Return a list with units."""
        ## 2DO!!
        #return []

    #def _optimizeParams(self, dataset, quiet = False, **config):
        #"""Optimize system parameters."""

        ## PRETRAINING USING RESTRICTED BOLTZMANN MACHINES

        ## try to get pretraining configurations from user parameter
        #vOptConfig = {}
        #hOptConfig = {}
        #if isinstance(config, dict):
            #if 'visible' in config \
                #and isinstance(config['visible'], str):
                #vOptConfigName = config['visible']
                #vOptConfig = nmConfig.get(
                    #type = 'schedule', name = vOptConfigName)
            #if 'hidden' in config \
                #and isinstance(config['hidden'], str):
                #hOptConfigName = config['hidden']
                #hOptConfig = nmConfig.get(
                    #type = 'schedule', name = hOptConfigName)

        ## if no configuration name passed or name is invalid
        ## use default configuration
        #if not vOptConfig:
            #vOptConfigName = 'default' #self._config['optimize']['visible']
            #vOptConfig = {} #nmConfig.get(
                ##type = 'schedule', name = vOptConfigName)
        #if not hOptConfig:
            #hOptConfigName = 'default' #self._config['optimize']['hidden']
            #hOptConfig = {} #nmConfig.get(
                ##type = 'schedule', name = hOptConfigName)

        ## pretrain subsystems
        #nm.log('info', 'pretraining subsystems')
        #datasetCopy = dataset._get()
        
        ## pretrain visible subsystem
        #layerA = self._params['layers'][0]['name']
        #layerB = self._params['layers'][1]['name']
        #nm.log('info', 'optimize subsystem \'%s\': using algorithm \'%s\''
            #% (self._sub[0].getName(), vOptConfigName))
        #nm.log('info', 'visible layer: \'%s\', hidden layer: \'%s\'' % (layerA, layerB))
        #self._sub[0].initParams(dataset)
        #self._sub[0].optimizeParams(dataset, **vOptConfig)
        
        ## pretrain hidden subsystems
        #for sysID in range(1, len(self._sub) / 2):
            #nm.log('info', 'optimize model \'%s\': using algorithm \'%s\''
                #% (self._sub[sysID].getName(), hOptConfigName))
            ## transform data in dataset with previous subsystem
            #dataset.transformData(
                #system = self._sub[sysID - 1],
                #transformation = 'hiddenvalue',
                #colLabels = self._sub[sysID - 1].getUnits(type = 'hidden'))
            #self._sub[sysID].initParams(dataset)
            #self._sub[sysID].optimizeParams(dataset, **hOptConfig)

        ## reset data to the initial state
        #dataset._set(**datasetCopy)

        ## copy params from encoder to decoder
        ## 2DO

        ## finetuning using backpropagation
        ## 2DO

        #return True

    #def _initParams(self, data = None):
        #"""Initialize system parameters using data.

        #Not needed for autoencoders since subsystems
        #are initialized during optimization
        #"""

        #return True

#class denoisingAE(ae):
    #"""Denoising Autoencoder.
    
    #Description:
        #Used for dimensionality reduction and compression / decompression

    #Reference:
        #Vincent08
    #"""
    #pass