# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.io'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import tempfile
from pathlib import Path

import numpy as np

from nemoa.core import ntest
from nemoa.io import binfile, csvfile, inifile

class TestBinfile(ntest.ModuleTestCase):
    """Testcase for the module nemoa.io.binfile."""

    module = 'nemoa.io.binfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.gz')
        self.data = b'eJxrYK4tZDoiGBkGT0ZqotZJzt3/AbFpXoAgyI=='

    def test_save(self) -> None:
        binfile.save(self.data, self.filepath)
        self.assertTrue(self.filepath.is_file())
        self.filepath.unlink()

    def test_load(self) -> None:
        binfile.save(self.data, self.filepath)
        data = binfile.load(self.filepath)
        self.filepath.unlink()
        self.assertEqual(data, self.data)

class TestCsvfile(ntest.ModuleTestCase):
    """Testcase for the module nemoa.io.csvfile."""

    module = 'nemoa.io.csvfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.csv')
        self.header = '-*- coding: utf-8 -*-'
        self.data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        self.delim = ','
        self.labels = ['', 'col1', 'col2']
        csvfile.save(
            self.filepath, self.data, header=self.header, labels=self.labels,
            delim=self.delim)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_get_header(self) -> None:
        header = csvfile.get_header(self.filepath)
        self.assertEqual(header, self.header)

    def test_get_delim(self) -> None:
        delim = csvfile.get_delim(self.filepath)
        self.assertEqual(delim, self.delim)

    def test_get_labels_format(self) -> None:
        fmt = csvfile.get_labels_format(self.filepath)
        self.assertEqual(fmt, 'standard')

    def test_get_labels(self) -> None:
        labels = csvfile.get_labels(self.filepath)
        self.assertEqual(labels, self.labels)

    def test_get_annotation_colid(self) -> None:
        colid = csvfile.get_annotation_colid(self.filepath)
        self.assertEqual(colid, 0)

    def test_load(self) -> None:
        data = csvfile.load(self.filepath)
        self.assertTrue(isinstance(data, np.ndarray))
        col1 = np.array(data)['col1']
        self.assertTrue(np.all(col1 == self.data['col1']))
        col2 = np.array(data)['col2']
        self.assertTrue(np.all(col2 == self.data['col2']))

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestInifile(ntest.ModuleTestCase):
    """Testcase for the module nemoa.io.inifile."""

    module = 'nemoa.io.inifile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.ini')
        self.header = '-*- coding: utf-8 -*-'
        self.obj = {
            'n': {'a': 's', 'b': True, 'c': 1},
            'l1': {'a': 1}, 'l2': {'a': 2}}
        self.structure = {
            'n': {'a': 'str', 'b': 'bool', 'c': 'int'},
            'l[0-9]*': {'a': 'int'}}
        self.string = (
            "# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")
        inifile.save(self.obj, self.filepath, header=self.header)

    def test_dumps(self) -> None:
        text = inifile.dumps(self.obj, header=self.header)
        self.assertEqual(text, self.string)

    def test_loads(self) -> None:
        obj = inifile.loads(self.string, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        obj = inifile.load(self.filepath, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_get_header(self) -> None:
        header = inifile.get_header(self.filepath)
        self.assertEqual(header, self.header)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()
