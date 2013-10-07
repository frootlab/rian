#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')
import metapath

def main():

    # create workspace and open project

    mp = metapath.open('example')

    # create and optimize GRBM (Gaussian Restricted Boltzmann Machine) based model and plot the model graph

    GRBM_model = mp.model(
        name     = 'sim1-GRBM',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'ann.GRBM',
        optimize = 'example.codeTestCD')

    mp.plot(GRBM_model, 'ann.HiddenLayerGraph')

    # create and optimize DBN (Deep Beliefe Network) based model and plot the model graph

    AutoEnc_model = mp.model(
        name     = 'test',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'ann.DBN',
        optimize = 'example.codeTestCD)

    mp.plot(AutoEnc_model, 'ann.HiddenLayerGraph')

if __name__ == "__main__":
    main()

