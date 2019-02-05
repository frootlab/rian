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
"""Unittests for module 'nemoa.io.csv'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import env
from nemoa.io import csv
import test

#
# Test Cases
#

class TestCsv(test.ModuleTest):
    module = csv

    def setUp(self) -> None:
        path = env.get_temp_file()
        self.rfc_path = path.with_suffix('.csv')
        self.rfc_header = ('name', 'id', 'value')
        self.rfc_sep = ','

        self.rlang_path = path.with_suffix('.tsv')
        self.rlang_header = tuple(list(self.rfc_header)[1:])
        self.rlang_sep = '\t'

        self.comment = '-*- coding: utf-8 -*-'
        self.values = [('r1', 1, 1.), ('r2', 2, 2.), ('r3', 3, 3.)]
        self.rownames = [col[0] for col in self.values]

        # Manually Write RFC compliant CSV-File
        with self.rfc_path.open(mode='w') as file:
            # Write Comment
            file.writelines([f"# {self.comment}\n\n"])
            # Write Header
            file.writelines([self.rfc_sep.join(self.rfc_header) + '\n'])
            # Write Data
            for row in self.values:
                strrow = [str(token) for token in row]
                file.writelines([self.rfc_sep.join(strrow) + '\n'])

        # Manually Write R Language compliant TSV-File
        with self.rlang_path.open(mode='w') as file:
            # Write Comment
            file.writelines([f"# {self.comment}\n\n"])
            # Write Header
            file.writelines([self.rlang_sep.join(self.rlang_header) + '\n'])
            # Write Data
            for row in self.values:
                strrow = [str(token) for token in row]
                file.writelines([self.rlang_sep.join(strrow) + '\n'])

    def test_load(self) -> None:
        with self.subTest(format='rfc'):
            with csv.load(self.rfc_path) as file:
                self.assertEqual(file.delimiter, self.rfc_sep)
                self.assertEqual(file.header, self.rfc_header)
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RFC4180)
                self.assertEqual(file.namecol, None)
                self.assertEqual(file.read(), self.values)
        with self.subTest(format='rlang'):
            with csv.load(self.rlang_path) as file:
                self.assertEqual(file.delimiter, self.rlang_sep)
                self.assertEqual(list(file.header)[1:], list(self.rlang_header))
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RLANG)
                self.assertEqual(file.namecol, file.header[0])
                self.assertEqual(file.read(), self.values)

    def test_save(self) -> None:
        with self.subTest(format='rfc'):
            filepath = env.get_temp_file(suffix='.csv')
            csv.save( # type: ignore
                filepath, header=self.rfc_header, values=self.values,
                comment=self.comment, delimiter=self.rfc_sep)
            with csv.File(filepath) as file:
                self.assertEqual(file.delimiter, self.rfc_sep)
                self.assertEqual(file.header, self.rfc_header)
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RFC4180)
                self.assertEqual(file.namecol, None)
                self.assertEqual(file.read(), self.values)
            filepath.unlink()
        with self.subTest(format='rlang'):
            filepath = env.get_temp_file(suffix='.tsv')
            csv.save( # type: ignore
                filepath, header=self.rlang_header, values=self.values,
                comment=self.comment, delimiter=self.rlang_sep)
            with csv.File(filepath) as file:
                self.assertEqual(file.delimiter, self.rlang_sep)
                self.assertEqual(list(file.header)[1:], list(self.rlang_header))
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RLANG)
                self.assertEqual(file.namecol, file.header[0])
                self.assertEqual(file.read(), self.values)
            filepath.unlink()

    def test_File(self) -> None:
        # TODO: Test completeness of unittest with respect to the class
        pass

    def test_Reader(self) -> None:
        # TODO: Test completeness of unittest with respect to the class
        pass

    def test_Writer(self) -> None:
        # TODO: Test completeness of unittest with respect to the class
        pass

    def test_File_init(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(
                self.rfc_path, header=self.rfc_header, comment=self.comment,
                delimiter=self.rfc_sep) as file:
                self.assertIsInstance(file, csv.File)
        with self.subTest(format='rlang'):
            with csv.File(
                self.rlang_path, header=self.rlang_header, comment=self.comment,
                delimiter=self.rlang_sep) as file:
                self.assertIsInstance(file, csv.File)

    def test_File_name(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.name, self.rfc_path.name)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.name, self.rlang_path.name)

    def test_File_delimiter(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.delimiter, self.rfc_sep)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.delimiter, self.rlang_sep)

    def test_File_header(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.header, self.rfc_header)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(list(file.header)[1:], list(self.rlang_header))

    def test_File_comment(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.comment, self.comment)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.comment, self.comment)

    def test_File_hformat(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RFC4180)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RLANG)

    def test_File_namecol(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.namecol, None)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.namecol, file.header[0])

    def test_File_read(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.read(), self.values)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.read(), self.values)

    def test_File_rownames(self) -> None:
        with self.subTest(format='rfc'):
            with csv.File(self.rfc_path) as file:
                self.assertEqual(file.rownames, None)
            with csv.File(self.rfc_path, namecol='name') as file:
                self.assertEqual(file.rownames, self.rownames)
        with self.subTest(format='rlang'):
            with csv.File(self.rlang_path) as file:
                self.assertEqual(file.rownames, self.rownames)

    def test_File_write(self) -> None:
        with self.subTest(format='rfc'):
            filepath = env.get_temp_file(suffix='.csv')
            with csv.File(
                filepath, header=self.rfc_header, comment=self.comment,
                delimiter=self.rfc_sep) as file:
                file.write(self.values) # type: ignore
            with csv.File(filepath) as file:
                self.assertEqual(file.delimiter, self.rfc_sep)
                self.assertEqual(file.header, self.rfc_header)
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RFC4180)
                self.assertEqual(file.namecol, None)
                self.assertEqual(file.read(), self.values)
            filepath.unlink()
        with self.subTest(format='rlang'):
            filepath = env.get_temp_file(suffix='.tsv')
            with csv.File(
                filepath, header=self.rlang_header, comment=self.comment,
                delimiter=self.rlang_sep) as file:
                file.write(self.values) # type: ignore
            with csv.File(filepath) as file:
                self.assertEqual(file.delimiter, self.rlang_sep)
                self.assertEqual(list(file.header)[1:], list(self.rlang_header))
                self.assertEqual(file.comment, self.comment)
                self.assertEqual(file.hformat, csv.CSV_HFORMAT_RLANG)
                self.assertEqual(file.namecol, file.header[0])
                self.assertEqual(file.read(), self.values)
            filepath.unlink()

    def tearDown(self) -> None:
        if self.rfc_path.is_file():
            self.rfc_path.unlink()
        if self.rlang_path.is_file():
            self.rlang_path.unlink()
