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
                'hiddenSystem': None,
                'hiddenSystemClass': 'rbm',
                'hiddenSystemModule': 'rbm',
            },
            'init': {
                'ignoreUnits': []
            },
            'optimize': {
                'schedule': None,
                'visible': None,
                'hidden': None
            }
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
        self.setUnits(self._getUnitsFromConfig())
        self.setLinks(self._getLinksFromConfig())
        self._config['check']['config'] = True
        return True

    def _setNetwork(self, network):
        """Update units to network instance."""
        nemoa.log('info', 'get system units and links from network \'%s\'' % (network.getName()))
        self.setUnits(self._getUnitsFromNetwork(network))
        self.setLinks()
        self._config['check']['network'] = True
        return True

    def _setDataset(self, dataset, *args):
        """Update units and links to dataset instance."""
        #2DO: check if data is ok for visibleSystemClass
        self._config['check']['dataset'] = True
        return True

    def _isConfigured(self):
        """Return configuration state of ANN."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    # UNITS

    #def _getUnitsFromConfig(self):
        #"""Return tuple of list, containing the unit labels
        #of visible and hidden units using configuration
        #"""

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

    ###############################
    # 2DO!!!!!!!!!!!!!!!!!!!!!!
    ###############################
    #def _getUnitsFromSystem(self, type = None):
        #if type == 'visible':
            #return self_params['units'][0]['label']
        #if type == 'hidden':
            #return self._params['units'][1]['label']
        #if type in self._params['units']:
            #quit()
            
        #return (self_params['units'][0]['label'], self._params['units'][1]['label'])

    def _getUnitsFromNetwork(self, network):
        """Return tuple with lists of unit labels from network."""
        return tuple([network.nodes(type = layer) for layer in network.layers()])

        #layers = network.layers()
        #inputLayer = layers[0]
        #outputLayer = layers[-1]
        #visible = network.nodes(type = inputLayer) + network.nodes(type = outputLayer)

        #units = (visible, )
        #for layer in layers[1:-1]:
            #units += (network.nodes(type = layer), )
        #units += (visible, )
        #return units

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

    #def _createHiddenUnitsStackLayout(self, layout):
        #"""Return tuple with hidden unit label lists from tuple with numbers."""
        ## create labels for hidden layers
        #if isinstance(layout, str) and layout == 'auto':
            #lHidden = ([], ) # return empty stack if parameter layout is 'auto'
        #elif not isinstance(layout, tuple):
            #lHidden = ([], ) # return empty stack if parameter layout is not a tuple
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

        #
        # 2DO: get unit class from subsystems!!!!
        #

        # update unit parameters per layer
        self._params['units'] = []
        for layerID, labels in enumerate(units):
            if layerID == 0:
                name = 'input'
                visible = True
                unitClass = 'gauss'
            elif layerID == len(units) - 1:
                name = 'output'
                visible = True
                unitClass = 'gauss'
            else:
                name = 'h' + str(layerID)
                visible = False
                unitClass = 'bernoulli'
            self._params['units'].append({
                'name': name,
                'visible': visible,
                'class': unitClass,
                'label': labels})
        return True

    def _setLinks(self, *args, **kwargs):

        # update link parameters
        self._params['links'] = {}
        for layerID in range(len(self._params['units']) - 1):
            self._params['links'][(layerID, layerID + 1)] = {
                'source': self._params['units'][layerID]['name'],
                'target': self._params['units'][layerID + 1]['name']}
        return True

    #def _getUnits(self):
        #"""Return a list with units."""
        ## 2DO!!
        #return []

    def _optimizeParams(self, dataset, **config):
        """Optimize system parameters."""

        # pretraining neuronal network using
        # layerwise restricted boltzmann machines as subsystems
        self._preTraining(dataset, **config)

        # finetuning neuronal network using backpropagation
        self._fineTuning(dataset, **config)
        return True

    def _fineTuning(self, dataset, **config):
        """Finetuning system using backpropagation."""
        nemoa.log('info', 'finetuning system')
        nemoa.setLog(indent = '+1')

        

        nemoa.setLog(indent = '-1')
        return True

    def _preTraining(self, dataset, **config):
        """Pretraining ANN using Restricted Boltzmann Machines."""
        nemoa.log('info', 'pretraining system')
        nemoa.setLog(indent = '+1')

        # configure subsystems
        self._preTrainingPrepare()
        
        # optimize subsystems
        self._preTrainingOptimize(dataset, **config)
        
        # import parameters from subsystems
        self._preTrainingImport()
        
        # cleanup subsystem
        self._preTrainingCleanup()

        nemoa.setLog(indent = '-1')
        return True

    def _preTrainingPrepare(self):
        """Configure subsystems for pretraining."""
        ### 2DO: Why is this import necessary???
        import nemoa
        ###
        nemoa.log('info', 'configure subsystems')
        nemoa.setLog(indent = '+1')
        if not 'units' in self._params:
            nemoa.log('error', 'could not configure subsystems: no layers have been defined')
            nemoa.setLog(indent = '-1')
            return False

        # create and configure subsystems
        import nemoa.system
        self._subSystems = []
        for layerID in range((len(self._params['units']) - 1)  / 2):
            inUnits = self._params['units'][layerID]
            outUnits = self._params['units'][layerID + 1]
            links = self._params['links'][(layerID, layerID + 1)]

            # get subsystem configuration
            sysType = 'visible' if inUnits['visible'] else 'hidden'
            sysUserConf = self._config['params'][sysType + 'System']
            sysModule = self._config['params'][sysType + 'SystemModule']
            sysClass = self._config['params'][sysType + 'SystemClass']
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

            # update subsystem configuration
            sysConfig['name'] = '%s → %s' % (inUnits['name'], outUnits['name'])
            if not 'params' in sysConfig:
                sysConfig['params'] = {}
            if inUnits['visible']:
                sysConfig['params']['visible'] = \
                    self._params['units'][0]['label'] \
                    + self._params['units'][-1]['label']
            else:
                sysConfig['params']['visible'] = inUnits['label']
            sysConfig['params']['hidden'] = outUnits['label']

            # create instance of subsystem from configuration
            system = nemoa.system.new(config = sysConfig)

            nemoa.log('info', """
                adding subsystem: \'%s\' (%s units, %s links)
                """ % (system.getName(),
                len(system.getUnits(type = 'visible')) + len(system.getUnits(type = 'hidden')),
                len(system.getLinks())))

            # link subsystem
            self._subSystems.append(system)

            # link linksparameters of subsystem
            links['init'] = system._params['links'][(0, 1)]

            # link layerparameters of subsystem
            if layerID == 0:
                inUnits['init'] = system._units['visible']
                outUnits['init'] = system._units['hidden']
                if not 'init' in system._config:
                    print system._config
                    quit()
                system._config['init']['ignoreUnits'] = []
                system._config['optimize']['ignoreUnits'] = []
            else:
                # do not link params from upper
                # upper layer should be linked with pervious subsystem
                # (higher abstraction layer)
                outUnits['init'] = system._params['units'][1]
                system._config['init']['ignoreUnits'] = ['visible']
                system._config['optimize']['ignoreUnits'] = ['visible']

        self._config['check']['subSystems'] = True
        nemoa.setLog(indent = '-1')
        return True

    def _preTrainingOptimize(self, dataset, **config):
        """Optimize Subsystems."""
    
        # create copy of dataset values (before transformation)
        datasetCopy = dataset._get()

        # optimize subsystems
        for sysID in range(len(self._subSystems)):
            nemoa.log('info', 'optimize subsystem %s (%s)' \
                % (self._subSystems[sysID].getName(), self._subSystems[sysID].getType()))
            nemoa.setLog(indent = '+1')

            # link encoder and decoder system
            system = self._subSystems[sysID]

            # transform dataset with previous system / fix lower stack
            if sysID > 0:
                dataset.transformData(
                    system = self._subSystems[sysID - 1],
                    transformation = 'hiddenvalue',
                    colLabels = self._subSystems[sysID - 1].getUnits(type = 'hidden'))

            # initialize system
            # in higher layers 'initVisible' = False
            # prevents the system from reinitialization
            system.initParams(dataset)

            # optimize (free) system parameter
            system.optimizeParams(dataset, **config)

            nemoa.setLog(indent = '-1')

        # reset data to initial state (before transformation)
        dataset._set(**datasetCopy)
        return True

    def _preTrainingImport(self):
        nemoa.log('info', 'initialize system with subsystem parameters')
        nemoa.setLog(indent = '+1')

        # keep original inputs and outputs
        inputs = self._units['input']['label']
        outputs = self._units['output']['label']

        # expand unit parameters to all layers
        import numpy
        nemoa.log('info', 'import unit and link parameters from subsystems (enrolling)')
        inputUnits = self._units['input']['label']
        outputUnits = self._units['output']['label']
        units = self._params['units']
        links = self._params['links']
        for id in range((len(self._params['units']) - 1)  / 2):
            # copy unit parameters
            for attrib in units[id]['init'].keys():
                if attrib in ['name', 'visible']:
                    continue
                units[id][attrib] = units[id]['init'][attrib]
                units[-(id + 1)][attrib] = units[id][attrib]
            del units[id]['init']
            # copy link parameters and transpose numpy arrays
            for attrib in links[(id, id + 1)]['init'].keys():
                if attrib in ['source', 'target']:
                    continue
                links[(id, id + 1)][attrib] = \
                    links[(id, id + 1)]['init'][attrib]
            del links[(id, id + 1)]['init']
            links[(len(units) - id - 2, len(units) - id - 1)] = \
                self._getTransposedLinks((id, id + 1))

        nemoa.log('info', 'cleanup unit and linkage parameter arrays')
        # remove output units from input layer
        self._removeUnits('input', outputs)
        # remove input units from output layer
        self._removeUnits('output', inputs)

        nemoa.setLog(indent = '-1')
        return True

    def _preTrainingCleanup(self):
        del self._subSystems
        return True

    def _initParams(self, data = None):
        """Initialize DBN parameters.
        Use of data is not necessary because real initialization
        of parameters appears in pre training."""
        return (self._initUnits() and self._initLinks())
