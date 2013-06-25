#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('./package')
import metapath

def main():

    # create workspace and open project

    mp = metapath.open('example')

    model = mp.model(
        name     = 'sim1Gauss',
        network  = 'example.etfs(e.size = 4, tf.size = 4, s.size = 4)',
        dataset  = 'example.sim1',
        system   = 'example.GRBM',
        optimize = 'example.CD')

    mp.plot(model, 'boltzmann.HiddenLayerGraph')

if __name__ == "__main__":
    main()

