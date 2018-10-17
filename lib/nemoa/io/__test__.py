# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.io'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import tempfile
from pathlib import Path

from nemoa.core import ntest

class TestCase(ntest.GenericTestCase):
    """Testsuite for modules within the package 'nemoa.io'."""

    def test_io_binfile(self) -> None:
        """Test module 'nemoa.io.binfile'."""
        from nemoa.io import binfile

        file = Path(tempfile.NamedTemporaryFile().name + '.gz')
        data = b'eJxrYK4tZDoiGBkGT0ZqotZJzt3/AbFpXoAgyI=='

        with self.subTest('save'):
            binfile.save(data, file)
            self.assertTrue(file.is_file())

        with self.subTest('load'):
            self.assertEqual(binfile.load(file), data)

        if file.is_file():
            file.unlink()

    def test_io_csvfile(self) -> None:
        """Test module 'nemoa.io.csvfile'."""
        from nemoa.io import csvfile

        import numpy as np

        file = Path(tempfile.NamedTemporaryFile().name + '.csv')
        header = '-*- coding: utf-8 -*-'
        data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        delim = ','
        labels = ['', 'col1', 'col2']

        with self.subTest("save"):
            csvfile.save(
                file, data, header=header, labels=labels, delim=delim)
            self.assertTrue(file.is_file())

        with self.subTest("get_header"):
            self.assertEqual(csvfile.get_header(file), header)

        with self.subTest("get_delim"):
            self.assertEqual(csvfile.get_delim(file), delim)

        with self.subTest("get_labels_format"):
            self.assertEqual(csvfile.get_labels_format(file), 'standard')

        with self.subTest("get_labels"):
            self.assertEqual(csvfile.get_labels(file), labels)

        with self.subTest("get_annotation_colid"):
            self.assertEqual(csvfile.get_annotation_colid(file), 0)

        with self.subTest("load"):
            rval = csvfile.load(file)
            self.assertTrue(
                isinstance(rval, np.ndarray))
            self.assertTrue(
                np.all(np.array(rval)['col1'] == data['col1']))
            self.assertTrue(
                np.all(np.array(rval)['col2'] == data['col2']))

        if file.is_file():
            file.unlink()

    def test_io_inifile(self) -> None:
        """Test module 'nemoa.io.inifile'."""
        from nemoa.io import inifile

        file = Path(tempfile.NamedTemporaryFile().name + '.ini')
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
                inifile.loads(string, structure=structure), obj)

        with self.subTest("save"):
            inifile.save(obj, file, header=header)
            self.assertTrue(file.is_file())

        with self.subTest("load"):
            self.assertEqual(
                inifile.load(file, structure=structure), obj)

        with self.subTest("get_header"):
            self.assertEqual(inifile.get_header(file), header)

        if file.is_file():
            file.unlink()
