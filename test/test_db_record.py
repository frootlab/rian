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
"""Unittests for module 'nemoa.db.record'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
from nemoa.db import record
from nemoa.types import AnyOp
import test
from test import Case

#
# Test Cases
#

class TestRecord(test.ModuleTest):
    module = record

    def test_build(self) -> None:

        # Check types
        self.assertCaseIsSubclass(record.build, record.Record, [
            Case(args=('id', 'name')),
            Case(args=(('id', int), ('name', str))),
            Case(args=('id', ('type', type, {'default': str})), )])

        # Validate
        Rec = record.build(('id', int))
        rec = Rec(1)
        self.assertIsInstance(rec, record.Record)
        self.assertFalse(hasattr(rec, '__dict__'))
        self.assertEqual(getattr(rec, 'id', None), 1)
        self.assertEqual(getattr(rec, '_id'), 0)
        rec = Rec(1)
        self.assertEqual(getattr(rec, '_id'), 1)

    def test_is_record(self) -> None:
        init: AnyOp = lambda self, *args: None
        Rec = type('rec', (record.Record, ), {
            '__init__': init, '_get_newid': None,
            '_delete_hook': None, '_restore_hook': None,
            '_update_hook': None, '_revoke_hook': None})
        self.assertFalse(record.is_record(Rec(1, 2))) # pylint: disable=E0110
        Rec = dataclasses.make_dataclass('rec', ('x', 'y'))
        self.assertFalse(record.is_record(Rec(1, 2)))
        Rec = record.build('x', 'y')
        self.assertTrue(record.is_record(Rec(1, 2))) # type: ignore

    def test_get_fields(self) -> None:
        Rec = record.build(('x', int), ('y', float, {'default': 0.}))
        rec = Rec(1, 2.)
        fields = record.get_fields(rec)
        self.assertEqual(len(fields), 2)
        x, y = fields
        self.assertIsInstance(x, dataclasses.Field)
        self.assertEqual(x.name, 'x')
        self.assertEqual(x.type, int)
        self.assertIsInstance(y, dataclasses.Field)
        self.assertEqual(y.name, 'y')
        self.assertEqual(y.type, float)
        self.assertEqual(y.default, 0.)

    def test_create_from(self) -> None:
        Rec = record.build(('x', int), ('y', float, {'default': 0.}))
        rec = Rec(1, 2.)
        new = record.create_from(rec, x=2)
        self.assertEqual(getattr(new, 'x', None), 2)
        self.assertEqual(getattr(new, 'y', None), 2.)
