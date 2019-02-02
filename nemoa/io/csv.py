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
"""File I/O for textfiles containing delimiter-separated values.

The `delimiter-separated values format`_ is a family of file formats, used for
the storage of tabular data. In it's most common variant, the `comma-separated
values format`_, the format was used many years prior to attempts to it's
standardization in :RFC:`4180`, such that subtle differences often exist in the
data produced and consumed by different applications. This circumstance has
and basically been addressed by :PEP:`305` and the standard library module
:mod:`csv`. The current module extends the capabilities of the standard library
by I/O handling of :term:`file references <file reference>`, support of
non-standard CSV headers, as used in CSV exports of the `R programming
language`_, automation in CSV parameter detection and row names.

.. _delimiter-separated values format:
    https://en.wikipedia.org/wiki/Delimiter-separated_values
.. _comma-separated values format:
    https://en.wikipedia.org/wiki/Comma-separated_values
.. _R programming language:
    https://www.r-project.org/

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import csv
import contextlib
import collections
import io
import weakref
from nemoa.base import abc, attrib, check, literal
from nemoa.errors import FileFormatError, ColumnLookupError
from nemoa.io import FileConnector, FileProxy, plain
from nemoa.types import OptInt, OptIntTuple, OptStr, StrList, List, Tuple
from nemoa.types import IntTuple, OptList, OptStrTuple, Union
from nemoa.types import Iterable, Iterator, Any, ErrStack, ErrMeta, ErrType
from nemoa.types import StrDict, FileRef, Optional, FileLike, StrTuple
from nemoa.types import Path

#
# Types and ClassInfos
#

IterableClass = collections.abc.Iterable
OptDialectLike = Optional[Union[str, csv.Dialect]]
OptDialect = Optional[csv.Dialect]
Header = Iterable[str]
OptHeader = Optional[Header]
Field = Tuple[str, type]
Fields = List[Field]
Rows = List[tuple]
RowsLike = Iterable[tuple]
OptColumns = OptStrTuple
FileRefClasses = (str, Path, io.BufferedIOBase, io.TextIOBase, abc.FileAccessor)

#
# Constants
#

CSV_HFORMAT_RFC4180 = 0
CSV_HFORMAT_RLANG = 1

#
# CSV file I/O Handler Base Class
#

class HandlerBase(abc.ABC):
    """CSV file I/O Handler Base Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading mode.
        mode: String, which characters specify the mode in which the file is to
            be opened. The default mode is *reading mode*, which is indicated by
            the character `r`. The character `w` indicates *writing mode*.
            Thereby reading- and writing mode are exclusive and can not be used
            together.

    """

    _mode: str
    _connector: FileConnector
    _proxy: FileProxy
    _file: FileLike

    def __init__(self, file: FileRef, mode: str = 'r') -> None:
        self._mode = mode

        # In reading mode open file handler from a file connector
        if 'r' in mode:
            self._connector = FileConnector(file)
            self._file = self._connector.open(mode=mode)

        # In writing mode use a buffer
        elif 'w' in mode:
            self._proxy = FileProxy(file, mode='w')
            self._file = self._proxy.open(mode='w', newline='')

        # Check file handler
        if not isinstance(self._file, io.TextIOBase):
            self._connector.close()
            raise ValueError('the opened stream is not a valid text file')

    def __iter__(self) -> 'HandlerBase':
        return self

    def __next__(self) -> tuple:
        return self.read_row()

    def __enter__(self) -> 'HandlerBase':
        return self

    def __exit__(self, cls: ErrMeta, obj: ErrType, tb: ErrStack) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """Close the CSV file handler."""
        # In reading mode, when closing the file connector, also all opened file
        # handlers to the connected file are closed
        if 'r' in self._mode:
            self._connector.close()

        # In writing mode, when closing the file wrapper, also all opened file
        # handlers to the temporary file are closed and the changes are written
        # to the original file.
        elif 'w' in self._mode:
            self._proxy.close()

    @abc.abstractmethod
    def read_row(self) -> tuple:
        """Read a single row from the referenced file as a tuple."""
        raise NotImplementedError()

    @abc.abstractmethod
    def read_rows(self) -> Rows:
        """Read multiple rows from the referenced file as a list of tuples."""
        raise NotImplementedError()

    @abc.abstractmethod
    def write_row(self, row: Iterable) -> None:
        """Write a single row to the referenced file from a tuple."""
        raise NotImplementedError()

    @abc.abstractmethod
    def write_rows(self, rows: RowsLike) -> None:
        """Write multiple rows to the referenced file from a list of tuples."""
        raise NotImplementedError()

#
# CSV file I/O Reader Class
#

class Reader(HandlerBase):
    """CSV file I/O Reader Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading mode.
        skiprows: Number of initial lines within the given CSV file before the
            CSV Header. By default no lines are skipped.
        usecols: Tuple with column IDs of the columns, which are imported from
            the given CSV file. By default all columns are imported.
        fields: List (or arbitrary iterable) of field descriptors, respectively
            given by a tuple, containing a column name and a column type.
        **kwds: Formatting parameters used by :mod:`csv`. See also
            :ref:`Dialects and formatting parameters<csv-fmt-params>`

    """

    _reader: Iterator # TODO (patrick.michl@gmail.com): specify!
    _usecols: OptIntTuple
    _fields: Fields

    def __init__(
            self, file: FileRef, skiprows: int, usecols: OptIntTuple,
            fields: Fields, **kwds: Any) -> None:
        super().__init__(file, mode='r')
        self._reader = csv.reader(self._file, **kwds) # type: ignore
        for i in range(skiprows):
            next(self._reader)
        self._usecols = usecols
        self._fields = fields

    def read_row(self) -> tuple:
        """Read a single row from the referenced file as a tuple."""
        row = next(self._reader)
        decode = lambda i: literal.decode(row[i[1]], self._fields[i[0]][1])
        usecols = self._usecols or range(row)
        return tuple(map(decode, enumerate(usecols)))

    def read_rows(self) -> Rows:
        """Read multiple rows from the referenced file as a list of tuples."""
        return [row for row in self]

    def write_row(self, row: Iterable) -> None:
        """Write a single row to the referenced file from a tuple."""
        raise OSError("writing rows is not supported in reading mode")

    def write_rows(self, rows: RowsLike) -> None:
        """Write multiple rows to the referenced file from a list of tuples."""
        raise OSError("writing rows is not supported in reading mode")

#
# CSV file I/O Writer Class
#

class Writer(HandlerBase):
    """CSV file I/O Writer Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            writing mode.
        header: List (or arbitrary iterable) of column names, that specify the
            header of the CSV file.
        comment: Initial comment of the CSV file.
        **kwds: Formatting parameters used by :mod:`csv`. See also
            :ref:`Dialects and formatting parameters<csv-fmt-params>`

    """

    _writer: Any # TODO (patrick.michl@gmail.com): specify!

    def __init__(
            self, file: FileRef, header: Header, comment: str = '',
            **kwds: Any) -> None:
        super().__init__(file, mode='w')

        # Initialize CSV writer
        self._writer = csv.writer(self._file, **kwds)

        self._write_comment(comment) # Write initial comment lines
        self._write_header(header) # Write CSV header

    def _write_comment(self, comment: str) -> None:
        if not comment:
            return
        writelines = getattr(self._file, 'writelines')
        writelines([f'# {line}\n' for line in comment.splitlines()] + ['\n'])

    def _write_header(self, header: Header) -> None:
        self._writer.writerow(header)

    def read_row(self) -> tuple:
        """Read a single row from the referenced file as a tuple."""
        raise OSError("reading rows is not supported in writing mode")

    def read_rows(self) -> Rows:
        """Read multiple rows from the referenced file as a list of tuples."""
        raise OSError("reading rows is not supported in writing mode")

    def write_row(self, row: Iterable) -> None:
        """Write a single row to the referenced file from a tuple."""
        self._writer.writerow(row)

    def write_rows(self, rows: RowsLike) -> None:
        """Write multiple rows to the referenced file from a list of tuples."""
        self._writer.writerows(rows)

#
# CSV File Class
#

class File(attrib.Group):
    """File Class for text files containing delimiter-separated values.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading or writing mode.
        header: Optional list (or arbitrary iterable) of strings, that specify
            the column names within the CSV file. For an existing file, the
            header by default is extracted from the first content line (not
            blank and not starting with `#`). For a new file the header is
            required and an error is raised if the header is not given.
        comment: Optional string, which precedes the header and the rows of the
            CSV file, e.g. to include metadata within the file. For an existing
            file, the string by default is extracted from the initial comment
            lines (starting with `#`). For a new file the comment by default is
            empty.
        dialect: Optional parameter, that indicates the used CSV dialect. The
            parameter can be given as a dialect name from the list returned by
            the function :func:`csv.list_dialects`, or an instance of the class
            :class:`csv.Dialect`.
        delimiter: Single character, which is used to separetate the column
            values within the CSV file. For an existing file, the delimiter by
            default is detected from it's appearance within the file. For a new
            file the default value is `,`.
        namecol: Optional column name of a column, which contains row names. If
            a valid column is given, then the readonly attribute *rownames*
            returns this column as a list. By default the column is infered from
            the used header format. For a :RFC:`4180` compliant header by
            default no row names are used. For a header as used in exports of
            the `R programming language`_ by default the first column is used to
            store row names.
        hformat: Used CSV Header format. The following formats are supported:
            0: :RFC:`4180`:
                The column header represents the structure of the rows.
            1: `R programming language`_:
                The column header does not include the first column of the rows.
                This follows by the convention, that in the R programming
                language the CSV export adds an extra column with row names as
                the first column, which is omitted within the CSV header.

    """

    #
    # Public Attributes
    #

    name: property = attrib.Virtual('_get_name')
    name.__doc__ = "Filename of the given CSV file."

    # TODO: implement by default factory:
    comment: property = attrib.MetaData(dtype=str, factory='_get_comment')
    comment.__doc__ = """
    String containing the initial '#' lines of the CSV file or an empty string,
    if no initial comment lines could be detected.
    """

    delimiter: property = attrib.MetaData(dtype=str, factory='_get_delimiter')
    delimiter.__doc__ = """
    Delimiter character of the CSV file or None, if for an existing file the
    delimiter could not be detected.
    """

    namecol: property = attrib.MetaData(dtype=str, factory='_get_namecol')
    namecol.__doc__ = """
    Readonly name of column, that contains the row names. By default the column
    is infered from the used header format. For a :RFC:`4180` compliant header
    by default no row names are used. For a header as used in exports of the `R
    programming language`_ by default the name of the first column is returned.
    """

    header: property = attrib.MetaData(
        dtype=IterableClass, factory='_get_header')
    header.__doc__ = """
    List of strings containing column names from first non comment, non empty
    line of CSV file.
    """

    hformat: property = attrib.MetaData(dtype=int, factory='_get_hformat')
    hformat.__doc__ = """
    CSV Header format. The following formats are supported:
        0: :RFC:`4180`:
            The column header represents the structure of the rows.
        1: `R programming language`_:
            The column header does not include the first column of the rows.
            This follows by the convention, that in the R programming language
            the CSV export adds an extra column with row names as the first
            column, which is omitted within the CSV header.
    """

    fields: property = attrib.Virtual(fget='_get_fields')
    fields.__doc__ = """
    Readonly list of pairs containing the column names and the estimated (or
    given) column types of the CSV file.
    """

    rownames: property = attrib.Virtual(fget='_get_rownames')
    rownames.__doc__ = """
    Readonly list of row names extracted from the name column, given by the
    attribute *namecol* or None, if *namecol* is not given.
    """

    dialect: property = attrib.Virtual(fget='_get_dialect')
    dialect.__doc__ = """
    Readonly attribute, that indicates the used CSV dialect. The attribute is
    given as an instance of the class :class:`csv.Dialect`.
    """

    #
    # Protected Attributes
    #

    _file: property = attrib.Temporary(dtype=FileRefClasses)
    _children: property = attrib.Temporary(dtype=list)
    _dialect: property = attrib.MetaData(default=None)

    #
    # Special Methods
    #

    def __init__(
            self, file: FileRef, header: OptHeader = None,
            comment: OptStr = None, dialect: OptDialectLike = None,
            delimiter: OptStr = None, namecol: OptStr = None,
            hformat: OptInt = None) -> None:
        super().__init__() # Initialize attribute container
        self._file = file
        if header:
            self.header = header
        if comment:
            self.comment = comment
        if delimiter:
            self.delimiter = delimiter
        if namecol:
            self.namecol = namecol
        if hformat:
            self.hformat = hformat
        self._dialect = dialect
        self._children = []

    def __enter__(self) -> 'File':
        return self

    def __exit__(self, cls: ErrMeta, obj: ErrType, tb: ErrStack) -> None:
        self.close()

    #
    # Public Methods
    #

    def open(self, mode: str = 'r', columns: OptColumns = None) -> HandlerBase:
        """Open CSV file in reading or writing mode.

        Args:
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is *reading mode*, which is
                indicated by the character `r`. The character `w` indicates
                *writing mode*. Thereby reading- and writing mode are exclusive
                and can not be used together.
            columns: Has no effect in writing mode. For reading mode it
                specifies the columns, which are return from the CSV file by
                their respective column names. By default all columns are
                returned.

        Returns:
            In *reading mode* (if mode contains the character `w`) an instance
            of the class :class:`~nemoa.io.csv.Reader` is returned and in
            writing mode (if mode contains the character `r`) an instance of the
            class :class:`~nemoa.io.csv.Writer` is returned.

        """
        if 'w' in mode:
            if 'r' in mode:
                raise ValueError("'mode' requires to be excusively 'r' or 'w'")
            return self._open_write() # Open CSV Writer
        return self._open_read(columns) # Open CSV Reader

    def close(self) -> None:
        """Close all opened file handlers of CSV File."""
        for fh in self._children:
            with contextlib.suppress(ReferenceError):
                fh.close()

    def read(self, columns: OptColumns = None) -> Rows:
        """Read all rows from current CSV file.

        Args:
            columns: Specifies the columns, which are return from the CSV file
                by their respective column names. By default all columns are
                returned.

        Returns:
            List of tuples, which contain the values of the specified columns.

        """
        with self.open(mode='r', columns=columns) as fh:
            return fh.read_rows()

    def write(self, rows: Rows) -> None:
        """Write rows to current CSV file.

        Args:
            rows: List of tuples (or arbitrary iterables), which respectively
                contain the values of a single row.

        """
        with self.open(mode='w') as fh:
            fh.write_rows(rows)

    #
    # Protected Methods
    #

    def _get_name(self) -> OptStr:
        return plain.get_name(self._file)

    def _get_comment(self) -> str:
        return plain.get_comment(self._file)

    def _get_delimiter(self) -> OptStr:
        # Initialize CSV sniffer with default values
        mincount: int = 1
        maxcount: int = 100
        candidates: StrList = [',', '\t', ';', ' ', ':', '|']
        sniffer = csv.Sniffer()
        sniffer.preferred = candidates
        delimiter: OptStr = None

        # Detect delimiter
        try:
            with plain.openx(self._file, mode='r') as fd:
                size = 0
                probe = ''
                passed_header = False
                for line in fd:
                    # Check termination criteria
                    if size > maxcount:
                        break
                    # Skip blank and comment lines
                    strip = line.strip()
                    if not strip or strip.startswith('#'):
                        continue
                    # Skip header
                    if not passed_header:
                        passed_header = True
                        continue
                    # Increase probe size
                    probe += line
                    size += 1
                    if size <= mincount:
                        continue
                    # Try to detect delimiter from probe using csv.Sniffer
                    try:
                        dialect = sniffer.sniff(probe)
                    except csv.Error:
                        continue
                    delimiter = dialect.delimiter
                    break
        except FileNotFoundError:
            return ','

        return delimiter

    def _get_header(self) -> StrTuple:
        # Get first content line (non comment, non empty) of CSV file
        lines = plain.get_content(self._file, lines=1)
        if len(lines) != 1:
            raise FileFormatError(self._file, 'CSV')

        # Read column names from first content line
        tokens = lines[0].split(self.delimiter)
        names = [col.strip('\"\'\n\r\t ') for col in tokens]
        if self.hformat == CSV_HFORMAT_RFC4180:
            colnames = names
        elif self.hformat == CSV_HFORMAT_RLANG:
            if not '_name' in names:
                colnames = ['_name'] + names
            else:
                i = 1
                while f'_name_{i}' in names:
                    i += 1
                colnames = [f'_name_{i}'] + names
        else:
            raise FileFormatError(self._file, 'CSV')

        # Replace empty column names by unique identifier
        while '' in colnames:
            colid = colnames.index('')
            colname = 'col' + str(colid)
            if not colname in colnames:
                colnames[colid] = colname
                continue
            i = 1
            while f'{colname}_{i}' in colnames:
                i += 1
            colnames[colid] = f'{colname}_{i}'
        return tuple(colnames)

    def _get_hformat(self) -> OptInt:
        # Get first and second content lines (non comment, non empty) of
        # CSV file and determine column label format
        lines = plain.get_content(self._file, lines=2)
        if len(lines) == 2:
            delimiter = self.delimiter
            if lines[0].count(delimiter) == lines[1].count(delimiter):
                return CSV_HFORMAT_RFC4180
            if lines[0].count(delimiter) == lines[1].count(delimiter) - 1:
                return CSV_HFORMAT_RLANG
        raise FileFormatError(self._file, 'CSV')

    def _get_fields(self) -> Fields:
        colnames = self.header
        delimiter = self.delimiter
        lines = plain.get_content(self._file, lines=3)

        # By default estimate the column types from the values of two rows and
        # add the type if the estimations are identical
        if len(lines) == 3:
            row1 = lines[1].split(delimiter)
            row2 = lines[2].split(delimiter)
            fields = []
            for name, str1, str2 in zip(colnames, row1, row2):
                type1 = literal.estimate(str1)
                type2 = literal.estimate(str2)
                if type1 and type2 == type1:
                    fields.append((name, type1))
                    continue
                fields.append((name, str))
            return fields

        # If the CSV file only contains a single row of values, estimate the
        # column tyoe from the values of this row
        if len(lines) == 2:
            row = lines[1].split(delimiter)
            fields = []
            for name, text in zip(colnames, row):
                fields.append((name, literal.estimate(text) or str))
            return fields
        raise FileFormatError(self._file, 'CSV')

    def _get_rownames(self) -> OptList:
        namecol = self.namecol
        if namecol is None:
            return None
        if not namecol in self.header:
            raise ColumnLookupError(namecol)
        return [col[0] for col in self.read(columns=(namecol,))]

    def _get_skiprows(self) -> int:
        # Count how many 'comment' and 'blank' rows are to be skipped
        skiprows = 1
        with plain.openx(self._file, mode='r') as fd:
            for line in fd:
                strip = line.strip()
                if not strip or strip.startswith('#'):
                    skiprows += 1
                    continue
                break
        return skiprows

    def _get_namecol(self) -> OptStr:
        # In RFC4180 by default no row names are used
        if self.hformat == CSV_HFORMAT_RFC4180:
            return None

        # In R-language format by default the first column name is returned
        if self.hformat == CSV_HFORMAT_RLANG:
            return self.header[0]
        return None

    def _get_usecols(self, columns: OptColumns = None) -> IntTuple:
        # Get column IDs for given column names
        colnames = self.header
        if not columns:
            return tuple(range(len(colnames)))

        # Check if columns exist
        check.is_subset("'columns'", set(columns), 'colnames', set(colnames))
        return tuple(colnames.index(col) for col in columns)

    def _get_dialect(self) -> csv.Dialect:
        # Get default format parameters from dialect
        attr = self._dialect
        if attr is None:
            dialect = csv.get_dialect('excel') # Default dialect
        elif isinstance(attr, csv.Dialect):
            dialect = attr # type: ignore
        elif attr in csv.list_dialects():
            dialect = csv.get_dialect(attr)
        else:
            raise ValueError(f"unkown CSV-dialect '{attr}'")
        return dialect # type: ignore

    def _get_fmt_params(self) -> StrDict:
        params: StrDict = {}
        # Copy format params from dialect object
        dialect = self.dialect
        keys = list(filter(lambda x: not x.startswith('_'), dialect.__dir__()))
        for key in keys:
            params[key] = getattr(dialect, key)
        # Update params
        if self.delimiter:
            params['delimiter'] = self.delimiter
        return params

    def _open_read(self, columns: OptColumns = None) -> Reader:
        usecols = self._get_usecols(columns)
        skiprows = self._get_skiprows()
        fields = self.fields
        usefields = [fields[colid] for colid in usecols]
        fmtparams = self._get_fmt_params()
        return Reader(
            self._file, skiprows=skiprows, usecols=usecols, fields=usefields,
            **fmtparams)

    def _open_write(self, columns: OptColumns = None) -> Writer:
        fmtparams = self._get_fmt_params()
        handler = Writer(
            self._file, header=self.header, comment=self.comment,
            **fmtparams)
        self._children.append(weakref.proxy(handler))
        return handler

#
# Constructors
#

def load(
        file: FileRef, delimiter: OptStr = None,
        hformat: OptInt = None) -> File:
    """Load CSV file.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading or writing mode.
        delimiter: Single character, which is used to separetate the column
            values within the CSV file. By default the delimiter is detected
            from it's appearance within the file.
        hformat:

    Returns:
        Instance of class :class:`nemoa.csv.File`

    """
    return File(file, delimiter=delimiter, hformat=hformat)

def save(
        file: FileRef, header: Header, values: Rows, comment: OptStr = None,
        delimiter: OptStr = None, hformat: OptInt = None) -> None:
    """Save data to CSV file.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, an instance of the class
            :class:`~nemoa.base.abc.FileAccessor` or an opened file object in
            reading or writing mode.
        header: Optional list (or arbitrary iterable) of strings, that specify
            the column names within the CSV file. For an existing file, the
            header by default is extracted from the first content line (not
            blank and not starting with `#`). For a new file the header is
            required and an error is raised if the header is not given.
        comment: Optional string, which precedes the header and the rows of the
            CSV file, e.g. to include metadata within the file. For an existing
            file, the string by default is extracted from the initial comment
            lines (starting with `#`). For a new file the comment by default is
            empty.
        delimiter: Single character, which is used to separetate the column
            values within the CSV file. For an existing file, the delimiter by
            default is detected from it's appearance within the file. For a new
            file the default value is `,`.
        hformat:

    """
    csvfile = File(
        file, header=header, comment=comment, hformat=hformat,
        delimiter=delimiter)
    csvfile.write(values)
