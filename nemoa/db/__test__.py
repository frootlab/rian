# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.db'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import itertools
import string
from nemoa.db import table
from nemoa.test import Case, ModuleTestCase

class TestTable(ModuleTestCase):
    """Testcase for the module nemoa.db.table."""

    module = 'nemoa.db.table'

    def setUp(self) -> None:
        # Create test table
        self.table = table.Table('test', fields=(
            ('uid', int),
            ('prename', str, {'default': ''}),
            ('name', str, {'default': ''})))
        # Create test data
        letters = string.ascii_letters
        size = len(letters)
        self.table.insert([(i, letters[i], letters[-i]) for i in range(size)])

    def test_create_record_class(self) -> None:
        # Check types
        self.assertAllSubclass(table.create_record_class, table.Record, [
            Case(args=(('id', 'name'), )),
            Case(args=((('id', int), ('name', str)), )),
            Case(args=(('id', ('type', type, {'default': str})), ))])
        # Validate
        Record = table.create_record_class((('id', int), ))
        rec1 = Record(id=1) # type: ignore
        self.assertEqual(getattr(rec1, '_id'), 0)
        rec1 = Record(id=1) # type: ignore
        self.assertEqual(getattr(rec1, '_id'), 1)
        self.assertFalse(hasattr(rec1, '__dict__'))

    def test_Cursor(self) -> None:
        pass

    def test_Table(self) -> None:
        pass

    def test_Table_create(self) -> None:
        pass

    def test_Table_drop(self) -> None:
        pass
