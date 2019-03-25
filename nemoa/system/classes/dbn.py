# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Deep Belief Network (DBN).

Deep Beliefe Network implementation for multilayer data modeling, nonlinear data
dimensionality reduction and nonlinear data analysis.

"""
__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import nemoa.system.classes.ann
import numpy

class DBN(nemoa.system.classes.ann.ANN):
    """Deep Belief Network (DBN).

    'Deep Belief Networks' are layered feed forward Artificial Neural
    Networks with hidden layers, a symmetric graph structure and
    optimization in two steps. The first step, known as 'pretraining',
    utilizes Restricted Boltzmann Machines as builing blocks to
    initialize the optimization parameters. This allows the introduction
    of energy based weak constraints on direct unit interactions and
    improves the ability to overcome bad local optima. The second step,
    known as 'finetuning', uses a gradient descent by Backpropagation of
    Error to optimize the reconstruction of output data.

    DBNs are typically used for data classification tasks and nonlinear
    dimensionality reduction (1). By using data manipulation tests, DBNs
    can also be utilized to find and analyse nonlinear dependency
    sructures in data.

    References:
        (1) "Reducing the dimensionality of data with neural networks",
            G. E. Hinton, R. R. Salakhutdinov, Science, 2006

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _default = {
        'params': {
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'gauss',
            'hidden_class': 'sigmoid',
            'visible_system_type': 'rbm.GRBM',
            'hidden_system_type': 'rbm.RBM' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 }}

    def _check_network(self, network):
        return network._is_compatible_dbn()
