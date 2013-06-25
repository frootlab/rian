#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')
import metapath

def main():

    # create workspace and open project
    mp = metapath.open('example')

    model = mp.model(
        name     = 'test',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'ann.autoencoder',
        optimize = 'ann.CD')

    quit()

    model = mp.model(
        name     = 'GAG Regulation',
        network  = 'felix.GAG',
        dataset  = 'gbm.tcga.all',
        system   = 'boltzmann.autoencoder',
        optimize = 'boltzmann.CD',
        autosave = True)

    # create workspace and open project
    mp = metapath.open('simulation')

    model = mp.model(
        network  = 'simulation.ETFS(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'simulation.sim40-0.1',
        system   = 'boltzmann.GRBM',
        optimize = 'boltzmann.CD(updates = 100000, estimateTime = False, inspect = True, inspectInterval = 1000, inspectFunction = \'error\')',
        autosave = False)

    mp.plot(model, 'boltzmann.HiddenLayerGraph')

    quit()

    #model = mp.model(
        #network  = 'simulation.ETFS(e.size = 4, tf.size = 8, s.size = 4)',
        #dataset  = 'simulation.sim40-0.1-binary',
        #system   = 'boltzmann.RBM',
        #optimize = 'boltzmann.CD(updates = 1000000, updateRate = 0.001, minibatchSize = 1000, minibatchInterval = 10, inspect = True, inspectFunction = "energy", inspectInterval = 1000)',
        #autosave = False)

    #quit()


    #model = mp.loadModel('test2-sim30-0-04-rbm (2)')
    #mp.plot(model, 'boltzmann.HiddenLayerGraph', output = 'display')
    #quit()

    #model = mp.model(
        #network  = 'simulation.ETFS(e.size = 4, tf.size = 8, s.size = 4)',
        #dataset  = 'simulation.sim41-0.0-binary',
        #system   = 'boltzmann.RBM',
        #optimize = 'boltzmann.CD',
        #autosave = True)
    #quit()

    # create workspace and open project
    mp = metapath.open('anna')

    model = mp.model(
        name     = 'TelAnchor Regulation',
        dataset  = 'anna.TelAnchors',
        system   = 'boltzmann.GRBM(hidden = 32)',
        optimize = 'boltzmann.CD(updates = 1000000, updateRate = 0.001, minibatchSize = 100, minibatchInterval = 10, inspect = True, inspectFunction = "performance", inspectInterval = 1000)',
        autosave = True)

    quit()
    #print 'SystemEnergy: ' + str(model._getEval(func = 'energy'))
    
    #for i in range(100):
        #print 'SystemEnergy: ' + str(model._getEval(func = 'energy'))
        #mp.optimizeModel(model, 'boltzmann.CD(updates = 1000, updateRate = 0.01, minibatchSize = 10000)')
    #quit()

    quit()

    model = mp.loadModel('TelAnchor Regulation')
    print model._getEval(func = 'energy')
    quit()
    mp.plot(model, 'boltzmann.InteractionHeatmap')

    quit()

    model = mp.model(
        name     = 'TLM Genes',
        dataset  = 'anna.TLMGenes',
        system   = 'boltzmann.GRBM(hidden = 100)',
        optimize = 'boltzmann.CD',
        autosave = True)
    quit()

    model = mp.model(
        name     = 'TelAnchor Regulation',
        dataset  = 'anna.TelAnchors',
        system   = 'boltzmann.GRBM(hidden = 10)',
        optimize = 'boltzmann.CD',
        autosave = True)

    mp.plot(model, 'HiddenLayerGraph')

    quit()

    title = r'sim41: $\sigma=0.5$, (32,24,16,8,4) filtering'
    mp.plot(model, 'HiddenLayerGraph', title = title)
    mp.plot(model, 'Histogram', title = title)

    model = mp.createModel(
        network  = 'e-tf-s(e.size = 4, tf.size = 8, s.size = 4)',
        dataset  = 'sim41-0.5',
        system   = 'GRBM',
        optimize = 'CD',
        autosave = True)
    title = r'sim41: $\sigma=0.5$, no filtering'
    mp.plot(model, 'HiddenLayerGraph', title = title)
    mp.plot(model, 'Histogram', title = title)

    quit()
    model = mp.createModel(
        name     = 'test-sim30-0-04-grbm',
        network  = 'e-tf-s(tf.size = 4)',
        dataset  = 'simulation30_4',
        system   = 'GRBM',
        optimize = 'CD(updates = 50000)',
        autosave = True)
    mp.plot(model, 'HiddenLayerGraph')
    model = mp.createModel(
        name     = 'test-sim30-0-04-grbm',
        network  = 'e-tf-s(tf.size = 4)',
        dataset  = 'simulation30_4',
        system   = 'RBM',
        optimize = 'CD(updates = 50000)',
        autosave = True)
    mp.plot(model, 'HiddenLayerGraph')
    quit()

    model = mp.loadModel('sim30-0-04')
    print model._getUnitEval(func = 'intperformance')
    quit()
    model.cfg['name'] = r'$ \mathrm{Simulation 30} (\sigma = 0.3) - \mathrm{no filtering} $'
    mp.plot(model, 'HiddenLayerGraph')
    #print model._getEval(func = 'energy')
    quit()

    # create models
    for i in range(1, 32):
        valList = [0, 0, 0]
        for j in range(0, 3):
            name = 'sim30-%d-%02d' % (j, i)
            model = mp.loadModel(name, quiet = True)
            if not model:
                continue
            valList[j] = model._getEval(func = 'performance')
        print '%d;%.1f;%.1f;%.1f' % (i, 100*valList[0], 100*valList[1], 100*valList[2])

    model = mp.loadModel('sim30-1-04')
    
    mp.plot(model, 'HiddenLayerGraph')

    quit()

    quit()

    model = mp.createModel(
        name     = 'sim30-0-04-rbm',
        network  = 'e-tf-s(tf.size = 4)',
        dataset  = 'simulation30_4',
        system   = 'RBM',
        optimize = 'CD(updates = 1000000)',
        autosave = True)

    mp.plot(model, 'HiddenLayerGraph')
    quit()

    model = mp.createModel(
        name     = 'sim30-0-04-rbm',
        network  = 'e-tf-s(tf.size = 4)',
        dataset  = 'simulation30_4',
        system   = 'RBM',
        optimize = 'CD(updates = 20000)',
        autosave = True)
    quit()

if __name__ == "__main__":
    main()

