# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.io'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import os
import tempfile
from pathlib import Path

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):
    """Testsuite for modules within the package 'nemoa.io'."""

    def test_io_csvfile(self) -> None:
        """Test module 'nemoa.io.csvfile'."""
        from nemoa.io import csvfile

        import numpy as np

        filename = tempfile.NamedTemporaryFile().name + '.csv'
        header = '-*- coding: utf-8 -*-'
        data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        delim = ','
        labels = ['', 'col1', 'col2']

        with self.subTest("save"):
            csvfile.save(
                filename, data, header=header, labels=labels, delim=delim)
            self.assertTrue(Path(filename).is_file())

        with self.subTest("get_header"):
            self.assertEqual(csvfile.get_header(filename), header)

        with self.subTest("get_delim"):
            self.assertEqual(csvfile.get_delim(filename), delim)

        with self.subTest("get_labels_format"):
            self.assertEqual(csvfile.get_labels_format(filename), 'standard')

        with self.subTest("get_labels"):
            self.assertEqual(csvfile.get_labels(filename), labels)

        with self.subTest("get_annotation_column"):
            self.assertEqual(csvfile.get_annotation_column(filename), 0)

        with self.subTest("load"):
            rval = csvfile.load(filename)
            self.assertTrue(
                isinstance(rval, np.ndarray))
            self.assertTrue(
                np.all(np.array(rval)['col1'] == data['col1']))
            self.assertTrue(
                np.all(np.array(rval)['col2'] == data['col2']))

        if os.path.exists(filename):
            os.remove(filename)

    def test_io_inifile(self) -> None:
        """Test module 'nemoa.io.inifile'."""
        from nemoa.io import inifile

        from typing import cast

        filename = tempfile.NamedTemporaryFile().name + '.ini'
        header = '-*- coding: utf-8 -*-'
        obj = {
            'n': {'a': 's', 'b': True, 'c': 1},
            'l1': {'a': 1}, 'l2': {'a': 2}}
        structure = {
            'n': {'a': 'str', 'b': 'bool', 'c': 'int'},
            'l[0-9]*': {'a': 'int'}}
        string = (
            "# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")

        with self.subTest("dumps"):
            self.assertEqual(
                inifile.dumps(obj, header=header), string)

        with self.subTest("loads"):
            self.assertEqual(
                inifile.loads(string, structure=cast(dict, structure)), obj)

        with self.subTest("save"):
            inifile.save(obj, filename, header=header)
            self.assertTrue(Path(filename).is_file())

        with self.subTest("load"):
            self.assertEqual(
                inifile.load(filename, structure=cast(dict, structure)), obj)

        with self.subTest("get_header"):
            self.assertEqual(inifile.get_header(filename), header)

        if os.path.exists(filename):
            os.remove(filename)

    def test_io_gzfile(self) -> None:
        """Test module 'nemoa.io.gzfile'."""
        from nemoa.io import gzfile

        obj = {True: 'a', 2: {None: .5}}
        blob = b'eJxrYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
        filename = tempfile.NamedTemporaryFile().name

        with self.subTest("dumps"):
            self.assertEqual(gzfile.dumps(obj), blob)

        with self.subTest("loads"):
            self.assertEqual(gzfile.loads(blob), obj)

        with self.subTest("dump"):
            self.assertTrue(gzfile.dump(obj, filename))
            self.assertTrue(os.path.exists(filename))

        with self.subTest("load"):
            self.assertEqual(gzfile.load(filename), obj)

        if os.path.exists(filename):
            os.remove(filename)
