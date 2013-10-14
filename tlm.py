#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')
import metapath

def main():

    # create workspace and open project
    mp = metapath.open('tlm')

    # create and optimize model
    grbmModel = mp.model(
        name     = 'tlm-tf2anchor-knockout-grbm',
        network  = 'tlm.tf2anchor',
        dataset  = 'tlm.knockout',
        system   = 'ann.grbm',
        optimize = 'tlm.CD')

    # save model in projects directory
    mp.saveModel(grbmModel)

    #grbmModel = mp.loadModel('tlm-tf2anchor-knockout-grbm')

    # create plot
    mp.plot(grbmModel, 'Histogram')
    mp.plot(grbmModel, 'Network')
    mp.plot(grbmModel, 'CorrelationHeatmap')
    mp.plot(grbmModel, 'CorrelationNetwork')
    mp.plot(grbmModel, 'ann.InteractionHeatmap')
    mp.plot(grbmModel, 'ann.ConnectionHeatmap')
    mp.plot(grbmModel, 'ann.DirectionHeatmap')
    mp.plot(grbmModel, 'ann.HiddenLayerGraph')
    quit()

    
    mp.saveModel(grbmModel)

    quit()

    #
    # Example for GRBM (Gaussian Restricted Boltzmann Machine) based model
    #

    # create and optimize model
    grbmModel = mp.model(
        name     = 'sim1-grbm',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'ann.grbm',
        optimize = 'example.codeTestCD')

    # save model in projects directory
    mp.saveModel(grbmModel)

    # create plot
    mp.plot(grbmModel, 'ann.HiddenLayerGraph')

    quit()

    #
    # Example for DBN (Deep Beliefe Network) based model
    #

    # create and optimize model
    dbnModel = mp.model(
        name     = 'test',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'ann.dbn',
        optimize = 'example.codeTestCD')

    # save model in projects directory
    mp.saveModel(dbnModel)

    # create plot
    mp.plot(dbnModel, 'ann.HiddenLayerGraph')

if __name__ == "__main__":
    main()

