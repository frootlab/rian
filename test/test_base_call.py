# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Unittests for module 'nemoa.base.call'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from collections import OrderedDict
from nemoa.base import call
import test
from test import Case

#
# Test Cases
#

class TestCall(test.ModuleTest):
    module = call

    def test_safe_call(self) -> None:
        f = call.parameters
        self.assertCaseEqual(call.safe_call, [
            Case(args=(f, list), value=OrderedDict()),
            Case(args=(f, list), kwds={'test': True}, value=OrderedDict())])

    def test_parameters(self) -> None:
        f = call.parameters
        self.assertCaseEqual(call.parameters, [
            Case(args=(f, ), value=OrderedDict()),
            Case(args=(f, list), value=OrderedDict([('op', list)])),
            Case(args=(f, list), kwds={'test': True},
                value=OrderedDict([('op', list), ('test', True)]))])

    def test_parse(self) -> None:
        self.assertEqual(call.parse("f(1., 'a', b = 2)"),
            ('f', (1.0, 'a'), {'b': 2}))
