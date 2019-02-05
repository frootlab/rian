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
"""Unittests for submodules of package 'nemoa.db'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
import string
from typing import Any
from nemoa.db import cursor, record, table
from nemoa.test import Case, ModuleTestCase
from nemoa.types import AnyOp, StrList

class TestCursor(ModuleTestCase):
    module = cursor

    def setUp(self) -> None:
        # Cursor modes
        self.cursor_modes: StrList = []
        for tmode in ['forward-only', 'scrollable', 'random']:
            for omode in ['dynamic', 'indexed', 'static']:
                self.cursor_modes.append(' '.join([tmode, omode]))

        # Create test table
        self.table = table.Table('test', columns=(
            ('uid', int),
            ('prename', str, {'default': ''}),
            ('name', str, {'default': ''}),
            ('gid', int, {'default': 0})))

        # Create test data
        letters = string.ascii_letters
        self.table.insert(# type: ignore
            [(i + 1, letters[i], letters[-i], i%3)
            for i in range(len(letters))])
        self.table.commit()

    def create_cursor(self, *args: Any, **kwds: Any) -> cursor.Cursor:
        return cursor.Cursor(
            *args, getter=self.table.row, parent=self.table, **kwds)

    def test_Cursor(self) -> None:
        pass

    def test_Cursor_fetch(self) -> None:
        create = self.create_cursor
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = create(mode=mode)
                self.assertIsInstance(cur.fetch()[0], record.Record)
                self.assertEqual(len(cur.fetch(4)), 4)
                if mode.split()[0] == 'random':
                    self.assertRaises(cursor.CursorError, cur.fetch, -1)
                else:
                    self.assertEqual(len(cur.fetch(-1)), len(self.table) - 5)
                    self.assertEqual(cur.fetch(), [])

    def test_Cursor_reset(self) -> None:
        create = self.create_cursor
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = create(mode=mode)
                if mode.split()[0] == 'random':
                    self.assertNotRaises(Exception, cur.reset)
                else:
                    cur.fetch(-1)
                    self.assertEqual(cur.fetch(), [])
                    cur.reset()
                    self.assertEqual(len(cur.fetch(-1)), len(self.table))

    def test_Cursor_batchsize(self) -> None:
        create = self.create_cursor
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = create(mode=mode, batchsize=5)
                self.assertEqual(len(cur.fetch()), 5)
                cur.batchsize = 1
                self.assertEqual(len(cur.fetch()), 1)
                if mode.split()[0] != 'random':
                    cur.batchsize = -1
                    self.assertEqual(len(cur.fetch()), len(self.table) - 6)
                cur = create(mode=mode, batchsize=100)
                if mode.split()[0] == 'random':
                    self.assertEqual(len(cur.fetch()), 100)
                else:
                    self.assertEqual(len(cur.fetch()), len(self.table))

    def test_Cursor_where(self) -> None:
        create = self.create_cursor
        for where, matches in [
            (lambda row: row._id < 5, 5), # pylint: disable=W0212
            (lambda row: row.name in 'abc', 3),
            ('uid < 6', 5),
            ('uid < 6 and gid == 1', 2)]:
            for mode in self.cursor_modes:
                with self.subTest(mode=mode, where=where):
                    cur = create(mode=mode, where=where)
                    size = len(cur.fetch(10))
                    if mode.split()[0] == 'random':
                        self.assertEqual(size, 10)
                    else:
                        self.assertEqual(size, matches)

    def test_Cursor_groupby(self) -> None:
        create = self.create_cursor
        args = ('gid', ('count', len, 'gid'), ('max(uid)', max, 'uid'))
        for mode in self.cursor_modes:
            with self.subTest(mode=mode, groupby='gid'):
                self.assertRaises(
                    cursor.CursorError, create, mode=mode, groupby='gid')
            with self.subTest(args=args, mode=mode, groupby='gid'):
                if (mode.split()[0] == 'random'
                    or mode.split()[1] != 'static'):
                    self.assertRaises(
                        cursor.CursorError, create, *args, mode=mode,
                        groupby='gid')
                else:
                    cur = create(*args, mode=mode, groupby='gid')
                    self.assertEqual(
                        list(cur), [(0, 18, 52), (1, 17, 50), (2, 17, 51)])

    def test_Cursor_having(self) -> None:
        create = self.create_cursor
        args = ('gid', ('count', len, 'gid'), ('max(uid)', max, 'uid'))
        for mode in self.cursor_modes:
            with self.subTest(mode=mode, groupby='gid', having='max(uid)<52'):
                self.assertRaises(
                    cursor.CursorError, create,
                    mode=mode, groupby='gid', having='max(uid)<52')
            with self.subTest(
                args=args, mode=mode, groupby='gid', having='max(uid)<52'):
                if (mode.split()[0] == 'random'
                    or mode.split()[1] != 'static'):
                    self.assertRaises(
                        cursor.CursorError, create,
                        *args, mode=mode, groupby='gid', having='max(uid)<52')
                else:
                    cur = create(
                        *args, mode=mode, groupby='gid', having='max(uid)<52')
                    self.assertEqual(
                        list(cur), [(1, 17, 50), (2, 17, 51)])

    def test_Cursor_orderby(self) -> None:
        create = self.create_cursor
        for mode in self.cursor_modes:
            with self.subTest(mode=mode, orderby='uid'):
                if (mode.split()[0] == 'random'
                    or mode.split()[1] != 'static'):
                    self.assertRaises(
                        cursor.CursorError, create,
                        mode=mode, orderby='uid')
                    continue
                cur = create(mode=mode, orderby='uid', reverse=False)
                rcur = create(mode=mode, orderby='uid', reverse=True)
                self.assertEqual(cur.fetch(-1), rcur.fetch(-1)[::-1])

    def test_Cursor_dtype(self) -> None:
        create = self.create_cursor
        for dtype in [tuple, dict]:
            for mode in self.cursor_modes:
                with self.subTest('uid', mode=mode, dtype=dtype):
                    cur = create('uid', mode=mode, dtype=dtype)
                    row = cur.fetch()[0]
                    self.assertEqual(type(row), dtype)

class TestRecord(ModuleTestCase):
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

class TestTable(ModuleTestCase):
    module = table

    def test_Table(self) -> None:
        pass

    def test_Table_create(self) -> None:
        kwds: dict
        kwds = {'columns': ('a', )}
        with self.subTest(**kwds):
            tbl = table.Table()
            tbl.create(None, **kwds)
            self.assertEqual(tbl.fields[0].name, 'a')
            self.assertEqual(tbl.fields[0].type, 'typing.Any')
            self.assertEqual(len(tbl.fields[0].metadata), 0)
        kwds = {'columns': (('a', str), )}
        with self.subTest(**kwds):
            tbl = table.Table()
            tbl.create(None, **kwds)
            self.assertEqual(tbl.fields[0].name, 'a')
            self.assertEqual(tbl.fields[0].type, str)
        kwds = {'columns': (('b', int, {'default': ''}), )}
        with self.subTest(**kwds):
            tbl = table.Table()
            tbl.create(None, **kwds)
            self.assertEqual(tbl.fields[0].name, 'b')
            self.assertEqual(tbl.fields[0].type, int)
            self.assertEqual(tbl.fields[0].default, '')
        kwds = {'columns': (('_a', Any, {'metadata': {1: 1, 2: 2}}), )}
        with self.subTest(**kwds):
            tbl = table.Table()
            tbl.create(None, **kwds)
            self.assertEqual(tbl.fields[0].name, '_a')
            self.assertEqual(tbl.fields[0].type, Any)
            self.assertEqual(len(tbl.fields[0].metadata), 2)