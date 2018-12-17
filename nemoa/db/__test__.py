# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.db'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import string
from nemoa.db import cursor, record, table
from nemoa.test import Case, ModuleTestCase
from nemoa.types import Any, StrList

class TestCursor(ModuleTestCase):
    module = cursor

    def setUp(self) -> None:
        # Cursor modes
        self.cursor_modes: StrList = []
        for tmode in ['forward-only', 'scrollable', 'random']:
            for omode in ['dynamic', 'indexed', 'static']:
                self.cursor_modes.append(' '.join([tmode, omode]))

        # Create test table
        self.columns = (
            ('uid', int),
            ('prename', str, {'default': ''}),
            ('name', str, {'default': ''}))
        self.table = table.Table('test', columns=self.columns)

        # Create test data
        letters = string.ascii_letters
        self.size = len(letters)
        self.table.insert( # type: ignore
            [(i + 1, letters[i], letters[-i]) for i in range(self.size)])
        self.table.commit()

    def create_cursor(self, *args: Any, **kwds: Any) -> cursor.Cursor:
        return cursor.create(
            *args, getter=self.table.row, parent=self.table, **kwds)

    def test_Cursor(self) -> None:
        pass

    def test_Cursor_fetch(self) -> None:
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = self.create_cursor(mode=mode)
                self.assertIsInstance(cur.fetch()[0], record.Record)
                self.assertEqual(len(cur.fetch(4)), 4)
                if mode.split()[0] == 'random':
                    self.assertRaises(cursor.CursorModeError, cur.fetch, -1)
                else:
                    self.assertEqual(len(cur.fetch(-1)), self.size - 5)
                    self.assertEqual(cur.fetch(), [])

    def test_Cursor_reset(self) -> None:
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = self.create_cursor(mode=mode)
                if mode.split()[0] == 'random':
                    self.assertNotRaises(Exception, cur.reset)
                else:
                    cur.fetch(-1)
                    self.assertEqual(cur.fetch(), [])
                    cur.reset()
                    self.assertEqual(len(cur.fetch(-1)), self.size)

    def test_Cursor_batchsize(self) -> None:
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                cur = self.create_cursor(mode=mode, batchsize=5)
                self.assertEqual(len(cur.fetch()), 5)
                cur.batchsize = 1
                self.assertEqual(len(cur.fetch()), 1)
                if mode.split()[0] != 'random':
                    cur.batchsize = -1
                    self.assertEqual(len(cur.fetch()), self.size - 6)
                cur = self.create_cursor(mode=mode, batchsize=100)
                if mode.split()[0] == 'random':
                    self.assertEqual(len(cur.fetch()), 100)
                else:
                    self.assertEqual(len(cur.fetch()), self.size)

    def test_Cursor_predicate(self) -> None:
        for mode in self.cursor_modes:
            with self.subTest(mode=mode):
                predicate = lambda row: row._id < 5 # pylint: disable=W0212
                cur = self.create_cursor(mode=mode, predicate=predicate)
                size = len(cur.fetch(10))
                if mode.split()[0] == 'random':
                    self.assertEqual(size, 10)
                else:
                    self.assertEqual(size, 5)
                predicate = lambda row: row.name in 'abc'
                cur = self.create_cursor(mode=mode, predicate=predicate)
                size = len(cur.fetch(10))
                if mode.split()[0] == 'random':
                    self.assertEqual(size, 10)
                else:
                    self.assertEqual(size, 3)

    def test_Cursor_orderby(self) -> None:
        for column in self.table.columns:
            for mode in self.cursor_modes:
                with self.subTest(mode=mode, orderby=column):
                    if (mode.split()[0] == 'random'
                        or mode.split()[1] != 'static'):
                        self.assertRaises(
                            cursor.CursorModeError, self.create_cursor,
                            mode=mode, orderby=column, reverse=False)
                        continue
                    cur = self.create_cursor(
                        mode=mode, orderby=column, reverse=False)
                    rcur = self.create_cursor(
                        mode=mode, orderby=column, reverse=True)
                    self.assertEqual(cur.fetch(-1), rcur.fetch(-1)[::-1])

    # def test_Cursor_mapper(self) -> None:
    #     for dtype in [tuple, dict]:
    #         mapper = self.table._create_mapper( # pylint: disable=W0212
    #             None, dtype=dtype)
    #         for mode in self.cursor_modes:
    #             with self.subTest(mode=mode, dtype=dtype):
    #                 cur = self._create_cursor( # pylint: disable=W0212
    #                     mode=mode, mapper=mapper)
    #                 row = cur.fetch()[0]
    #                 self.assertEqual(type(row), dtype)

class TestRecord(ModuleTestCase):
    module = record

    def test_build(self) -> None:

        # Check types
        self.assertAllSubclass(record.build, record.Record, [
            Case(args=(('id', 'name'), )),
            Case(args=((('id', int), ('name', str)), )),
            Case(args=(('id', ('type', type, {'default': str})), ))])

        # Validate
        Record = record.build((('id', int), ))
        rec1 = Record(id=1) # type: ignore
        self.assertEqual(getattr(rec1, '_id'), 0)
        rec1 = Record(id=1) # type: ignore
        self.assertEqual(getattr(rec1, '_id'), 1)
        self.assertFalse(hasattr(rec1, '__dict__'))

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
