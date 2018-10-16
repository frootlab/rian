# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.core import ntest

class TestCase(ntest.TestCase):

    def test_network_import(self):
        from nemoa.core import nclass

        with self.subTest(filetype = 'ini'):
            network = nemoa.network.open('deep', workspace = 'testsuite')
            self.assertTrue(nclass.hasbase(network, 'Network'))

    def test_network_create(self):
        from nemoa.core import nclass

        with self.subTest(create = 'autoencoder'):
            network = nemoa.network.create('autoencoder',
                columns = ['v1', 'v2', 'v3'],
                shape = [6, 3, 6])
            self.assertTrue(nclass.hasbase(network, 'Network'))

        with self.subTest(create = 'factor'):
            network = nemoa.network.create('factor',
                visible_nodes = ['v1', 'v2', 'v3'], visible_type = 'gauss',
                hidden_nodes = ['h1', 'h2'], hidden_type = 'sigmoid')
            self.assertTrue(nclass.hasbase(network, 'Network'))
