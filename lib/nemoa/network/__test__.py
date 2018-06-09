# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.mode = nemoa.get('mode')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        nemoa.set('mode', self.mode)

    def test_nemoa_network_import_ini(self):
        network = nemoa.network.open('deep', workspace = 'testsuite')
        test = nemoa.common.type.isnetwork(network)
        self.assertTrue(test)

    def test_nemoa_network_create_autoencoder(self):
        network = nemoa.network.create('autoencoder',
            columns = ['i1', 'i2', 'o1'],
            shape = [6, 3, 6])
        test = nemoa.common.type.isnetwork(network)
        self.assertTrue(test)
