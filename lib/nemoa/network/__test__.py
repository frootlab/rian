# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class TestSuite(nemoa.common.unittest.TestSuite):

    def test_network_import(self):
        with self.subTest(filetype = 'ini'):
            network = nemoa.network.open('deep', workspace = 'testsuite')
            test = nemoa.common.type.isnetwork(network)
            self.assertTrue(test)

    def test_network_create(self):
        with self.subTest(create = 'autoencoder'):
            network = nemoa.network.create('autoencoder',
                columns = ['i1', 'i2', 'o1'],
                shape = [6, 3, 6])
            test = nemoa.common.type.isnetwork(network)
            self.assertTrue(test)
