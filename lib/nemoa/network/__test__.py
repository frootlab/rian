# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common.unittest import TestSuite as NmTestSuite

class TestSuite(NmTestSuite):

    def test_network_import(self):
        with self.subTest(filetype = 'ini'):
            network = nemoa.network.open('deep', workspace = 'testsuite')
            test = nemoa.common.type.isnetwork(network)
            self.assertTrue(test)

    def test_network_create(self):
        with self.subTest(create = 'autoencoder'):
            network = nemoa.network.create('autoencoder',
                columns = ['v1', 'v2', 'v3'],
                shape = [6, 3, 6])
            test = nemoa.common.type.isnetwork(network)
            self.assertTrue(test)
        with self.subTest(create = 'factor'):
            network = nemoa.network.create('factor',
                visible_nodes = ['v1', 'v2', 'v3'], visible_type = 'gauss',
                hidden_nodes = ['h1', 'h2'], hidden_type = 'sigmoid')
            test = nemoa.common.type.isnetwork(network)
            self.assertTrue(test)
