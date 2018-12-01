# -*- coding: utf-8 -*-
"""File I/O for textfiles containing delimiter-separated values.

The `delimiter-separated values format`_ is a family of file formats, used for
the storage of tabular data. In it's most common variant, the `comma-separated
values format`_, the format was used many years prior to attempts to it's
standardization by :RFC:`4180`, such that subtle differences often exist in the
data produced and consumed by different applications. This circumstance is
explained in more detail in :PEP:`305` and basically addressed by the standard
library module :mod:`csv`. The current module extends the capabilities by
additional conveniance functions for file I/O handling and parameter detection.

.. _delimiter-separated values format:
    https://en.wikipedia.org/wiki/Delimiter-separated_values
.. _comma-separated values format:
    https://en.wikipedia.org/wiki/Comma-separated_values

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
import csv
import contextlib
import io
import numpy as np
from nemoa.base import attrib, check, literal
from nemoa.errors import FileFormatError
from nemoa.file import stream, textfile
from nemoa.types import FileOrPathLike, NpArray, OptInt, OptIntTuple, ClassVar
from nemoa.types import OptNpArray, OptStr, OptStrList, StrList, List, Tuple
from nemoa.types import IntTuple, OptList, OptStrTuple, FileRefClasses
from nemoa.types import Iterable, Iterator, Any, Traceback, ExcType, Exc
from nemoa.types import StrDict, FileRef

#
# Stuctural Types
#

Fields = List[Tuple[str, type]]
IterHandler = Iterator['HandlerBase']

#
# Constants
#

CSV_FORMAT_RFC4180 = 0
CSV_FORMAT_RLANG = 1

#
# CSV-file I/O Handler Base Class
#

class HandlerBase(ABC):
    """CSV-file I/O Handler Base Class."""

    _cman: stream.Connector
    _file: io.IOBase
    _wrapper: stream.FileWrapper
    _tmpfile: io.IOBase

    def __init__(self, file: FileRef, mode: str = 'r') -> None:
        self._cman = stream.Connector(file)
        self._file = self._cman.open(mode)
        if not isinstance(self._file, io.TextIOBase):
            self._cman.close()
            raise ValueError('the opened stream is not a valid text file')

    def __iter__(self) -> 'HandlerBase':
        return self

    def __next__(self) -> tuple:
        return self.read_row()

    def __enter__(self) -> 'HandlerBase':
        return self

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        with contextlib.suppress(AttributeError):
            self._tmpfile.close()
        with contextlib.suppress(AttributeError):
            self._wrapper.close()
        with contextlib.suppress(AttributeError):
            self._cman.close()

    @abstractmethod
    def read_row(self) -> tuple:
        raise NotImplementedError()

    @abstractmethod
    def read_rows(self) -> List[tuple]:
        raise NotImplementedError()

    @abstractmethod
    def write_row(self, row: Iterable) -> None:
        raise NotImplementedError()

    @abstractmethod
    def write_rows(self, row: List[Iterable]) -> None:
        raise NotImplementedError()

#
# CSV-file I/O Reader Class
#

class Reader(HandlerBase):
    """CSV-file I/O Reader Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.types.FileAccessorBase>` or an opened file object in reading
            mode.
        **kwds: :ref:`Dialects and Formatting Parameters<csv-fmt-params>`

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
        row = next(self._reader)
        decode = lambda i: literal.decode(row[i[1]], self._fields[i[0]][1])
        usecols = self._usecols or range(row)
        return tuple(map(decode, enumerate(usecols)))

    def read_rows(self) -> List[tuple]:
        return [row for row in self]

    def write_row(self, row: Iterable) -> None:
        raise OSError("writing rows is not supported in reading mode")

    def write_rows(self, row: List[Iterable]) -> None:
        raise OSError("writing rows is not supported in reading mode")

#
# CSV-file I/O Writer Class
#

class Writer(HandlerBase):
    """CSV-file I/O Writer Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.types.FileAccessorBase>` or an opened file object in writing
            mode.
        header: List of column names, that specify the header of the CSV-file.
        comment: Initial comment of the CSV-file.
        **kwds: :ref:`Dialects and Formatting Parameters<csv-fmt-params>`

    """

    _writer: Any # TODO (patrick.michl@gmail.com): specify!

    def __init__(
            self, file: FileRef, header: StrList, comment: str = '',
            **kwds: Any) -> None:
        super().__init__(file, mode='w')

        # Create file wrapper and temporary file
        self._wrapper = stream.FileWrapper(file, mode='w')
        self._tmpfile = self._wrapper.path.open(mode='w', newline='')

        # Initialize CSV writer with temporary file
        self._writer = csv.writer(self._tmpfile, **kwds)

        self._write_comment(comment) # Write initial comment lines
        self._write_header(header) # Write CSV header

    def _write_comment(self, comment: str) -> None:
        if not comment:
            return
        writeline = getattr(self._file, 'writeline')
        for line in comment.splitlines():
            writeline(f'# line\n')

    def _write_header(self, header: StrList) -> None:
        self.write_row(header)

    def read_row(self) -> tuple:
        raise OSError("reading rows is not supported in writing mode")

    def read_rows(self) -> List[tuple]:
        raise OSError("reading rows is not supported in writing mode")

    def write_row(self, row: Iterable) -> None:
        self._writer.writerow(row)

    def write_rows(self, rows: List[Iterable]) -> None:
        self._writer.writerows(rows)

#
# DSV-format File Class
#

class File(attrib.Container):
    """DSV-format File Class.

    Args:
        file: :term:`File reference` to a :term:`file object`. The reference can
            ether be given as a String or :term:`path-like object`, that points
            to a valid entry in the file system, a :class:`file accessor
            <nemoa.types.FileAccessorBase>` or an opened file object in reading
            or writing mode.
        delimiter: Single character, which is used as delimiter within the
            CSV-file. For an existing file, the delimiter by default is detected
            from the file.
        labels: List of column names, that specify the header of the CSV-file.
            For an existing file, the column names by default are taken from the
            first content line of the file.
        usecols: Tuple with column IDs of the columns, which are imported from
            the given CSV-file. By default all columns are imported.
        namecol: Single column ID of a column, which is used to identify row
            names. By default the first text column is used for row names.

    """

    #
    # Protected Class Variables
    #

    _delimiter_candidates: ClassVar[StrList] = [',', '\t', ';', ' ', ':', '|']
    """
    Optional list of strings containing delimiter candidates to search for.
    Default: [',', '\t', ';', ' ', ':', '|']
    """

    _delimiter_mincount: ClassVar[int] = 2
    """
    Minimum number of lines used to detect DSV delimiter. Thereby only non
    comment and non empty lines are used.
    """

    _delimiter_maxcount: ClassVar[int] = 100
    """
    Maximum number of lines used to detect DSV delimiter. Thereby only non
    comment and non empty lines are used.
    """

    #
    # Public Attributes
    #

    comment: property = attrib.Virtual(fget='_get_comment')
    comment.__doc__ = """
    String containing the initial '#' lines of the CSV-file or an empty string,
    if no initial comment lines could be detected.
    """

    delimiter: property = attrib.Virtual(fget='_get_delimiter')
    delimiter.__doc__ = """
    Delimiter string of the CSV-file or None, if the delimiter could not be
    detected.
    """

    format: property = attrib.Virtual(fget='_get_format')
    format.__doc__ = """
    DSV-Header format. The following formats are supported:
        0: :RFC:`4180`:
            The column header equals the size of the rows.
        1: R-Table:
            The column header has a size that is reduced by one, compared to the
            rows. This smaller number of entries follows by the convention, that
            in R the CSV export of tables adds an extra column with row names
            as the first column. The column name of this column is omitted
            within the header.
    """

    colnames: property = attrib.Virtual(fget='_get_colnames')
    colnames.__doc__ = """
    List of strings containing column names from first non comment, non empty
    line of CSV-file.
    """

    fields: property = attrib.Virtual(fget='_get_fields')
    colnames.__doc__ = """
    List of pairs containing the column names and the estimated or given column
    types of the CSV-file.
    """

    rownames: property = attrib.Virtual(fget='_get_rownames')
    rownames.__doc__ = """
    List of strings containing row names from column with id given by namecol or
    None, if namecol is not given.
    """

    namecol: property = attrib.Virtual(fget='_get_namecol')
    namecol.__doc__ = """
    Index of the column of a CSV-file that contains the row names. The value
    None is used for CSV-files that do not contain row names.
    """

    #
    # Protected Attributes
    #

    _fileref: property = attrib.Content(classinfo=FileRefClasses)
    _comment: property = attrib.MetaData(classinfo=str, default=None)
    _delimiter: property = attrib.MetaData(classinfo=str, default=None)
    _format: property = attrib.MetaData(classinfo=str, default=None)
    _colnames: property = attrib.MetaData(classinfo=list, default=None)
    _rownames: property = attrib.MetaData(classinfo=list, default=None)
    _namecol: property = attrib.MetaData(classinfo=int, default=None)

    #
    # Events
    #

    def __init__(self, file: FileRef, mode: str = '',
            comment: OptStr = None, delimiter: OptStr = None,
            csvformat: OptInt = None, labels: OptStrList = None,
            usecols: OptIntTuple = None, namecol: OptInt = None) -> None:
        """Initialize instance attributes."""
        super().__init__()

        self._fileref = file
        self._comment = comment
        self._delimiter = delimiter
        self._csvformat = csvformat
        self._colnames = labels
        self._namecol = namecol

    #
    # Public Methods
    #

    @contextlib.contextmanager
    def open(self, mode: str = 'r', columns: OptStrTuple = None) -> IterHandler:
        """Open CSV-file in reading or writing mode.

        Args:
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is *reading mode*, which is
                indicated by the character `r`. The character `w` indicates
                *writing mode*. Thereby reading- and writing mode are exclusive
                and can not be used together.
            columns: List of column labels in the CSV-file, that specifies the
                row header. By default the list of column labels is taken from
                the first content line of the current CSV-file.

        Yields:
            :class:`~nemoa.file.csv.Reader` in reading mode and
            :class:`~nemoa.file.csv.Writer` in writing mode.

        """
        # Open file handler
        fh: HandlerBase
        if 'w' in mode:
            if 'r' in mode:
                raise ValueError("'mode' requires to be excusively 'r' or 'w'")
            fh = self._open_write()
        else:
            fh = self._open_read(columns)
        try:
            yield fh
        finally:
            fh.close()

    def read(self) -> List[tuple]:
        """Read all rows from current CSV-file.

        Returns:
            rows: List of tuples, which respectively contain the values of a
                single row.

        """
        file: Reader
        with self.open(mode='r') as file:
            return file.read_rows()

    def write(self, rows: List[Iterable]) -> None:
        """Write rows to current CSV-file.

        Args:
            rows: List of tuples (or arbitrary iterables), which respectively
                contain the values of a single row.

        """
        file: Writer
        with self.open(mode='w') as file:
            file.write_rows(rows)

    # DEPRECATED
    def select(self, columns: OptStrTuple = None) -> OptNpArray:
        """Load numpy ndarray from CSV-file.

        Args:
            columns: List of column labels in CSV-file. By default the list of
                column labels is taken from the first content line in the
                CSV-file.

        Returns:
            :class:`numpy.ndarray` containing data from CSV-file, or None if
            the data could not be imported.

        """
        # Check type of 'cols'
        check.has_opt_type("'columns'", columns, tuple)

        # Get column names and formats
        usecols = self._get_usecols(columns)
        colnames = self._get_colnames()
        names = tuple(colnames[colid] for colid in usecols)
        lblcol = self._get_namecol()
        if lblcol is None:
            formats = tuple(['<f8'] * len(usecols))
        elif lblcol not in usecols:
            formats = tuple(['<U12'] + ['<f8'] * len(usecols))
            names = ('label', ) + names
            usecols = (lblcol, ) + usecols
        else:
            lbllbl = colnames[lblcol]
            formats = tuple(['<U12'] + ['<f8'] * (len(usecols) - 1))
            names = tuple(['label'] + [l for l in names if l != lbllbl])
            usecols = tuple([lblcol] + [c for c in usecols if c != lblcol])

        # Import data from CSV-file as numpy array
        with textfile.openx(self._fileref, mode='r') as fh:
            return np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delimiter(),
                usecols=usecols,
                dtype={'names': names, 'formats': formats})

    #
    # Protected Methods
    #

    def _get_comment(self) -> str:
        # Return comment if set manually
        if self._comment is not None:
            return self._comment
        return textfile.get_comment(self._fileref)

    def _get_delimiter(self) -> OptStr:
        # Return delimiter if set manually
        if self._delimiter is not None:
            return self._delimiter

        # Initialize DSV-Sniffer with default values
        sniffer = csv.Sniffer()
        sniffer.preferred = self._delimiter_candidates
        delimiter: OptStr = None

        # Detect delimiter
        with textfile.openx(self._fileref, mode='r') as fd:
            size, probe = 0, ''
            for line in fd:
                # Check termination criteria
                if size > self._delimiter_maxcount:
                    break
                # Check exclusion criteria
                strip = line.strip()
                if not strip or strip.startswith('#'):
                    continue
                # Increase probe size
                probe += line
                size += 1
                if size <= self._delimiter_mincount:
                    continue
                # Try to detect delimiter from probe using csv.Sniffer
                try:
                    dialect = sniffer.sniff(probe)
                except csv.Error:
                    continue
                delimiter = dialect.delimiter
                break

        return delimiter

    def _get_format(self) -> OptInt:
        # Return value if set manually
        if self._csvformat is not None:
            return self._csvformat

        # Get first and second content lines (non comment, non empty) of
        # CSV-file and determine column label format
        lines = textfile.get_content(self._fileref, lines=2)
        if len(lines) == 2:
            delimiter = self.delimiter
            if lines[0].count(delimiter) == lines[1].count(delimiter):
                return CSV_FORMAT_RFC4180
            if lines[0].count(delimiter) == lines[1].count(delimiter) - 1:
                return CSV_FORMAT_RLANG

        raise FileFormatError(self._fileref, 'DSV')

    def _get_colnames(self) -> StrList:
        # Return value if set manually
        if self._colnames is not None:
            return self._colnames

        # Get first content line (non comment, non empty) of CSV-file
        lines = textfile.get_content(self._fileref, lines=1)
        if len(lines) != 1:
            raise FileFormatError(self._fileref, 'DSV')

        # Read column names from first content line
        tokens = lines[0].split(self.delimiter)
        names = [col.strip('\"\'\n\r\t ') for col in tokens]
        if self.format == CSV_FORMAT_RFC4180:
            colnames = names
        elif self.format == CSV_FORMAT_RLANG:
            if not '_name' in names:
                colnames = ['_name'] + names
            else:
                i = 1
                while f'_name_{i}' in names:
                    i += 1
                colnames = [f'_name_{i}'] + names
        else:
            raise FileFormatError(self._fileref, 'DSV')

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

        return colnames

    def _get_fields(self) -> Fields:
        colnames = self.colnames
        delimiter = self.delimiter
        lines = textfile.get_content(self._fileref, lines=3)

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

        # If the DSV file only contains a single row of values, estimate the
        # column tyoe from the values of this row
        if len(lines) == 2:
            row = lines[1].split(delimiter)
            fields = []
            for name, text in zip(colnames, row):
                fields.append((name, literal.estimate(text) or str))
            return fields

        raise FileFormatError(self._fileref, 'DSV')

    def _get_rownames(self) -> OptList:
        # TODO (patrick.michl@gmail.com): Reimplement without using numpy
        # Check type of 'cols'
        lblcol = self._get_namecol()
        if lblcol is None:
            return None
        lbllbl = self.colnames[lblcol]

        # Import CSV-file to Numpy ndarray
        with textfile.openx(self._fileref, mode='r') as fh:
            rownames = np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delimiter(),
                usecols=(lblcol, ),
                dtype={'names': (lbllbl, ), 'formats': ('<U12', )})
        return [name[0] for name in rownames.flat]

    def _get_skiprows(self) -> int:
        # Count how many 'comment' and 'blank' rows are to be skipped
        skiprows = 1
        with textfile.openx(self._fileref, mode='r') as fd:
            for line in fd:
                strip = line.strip()
                if not strip or strip.startswith('#'):
                    skiprows += 1
                    continue
                break
        return skiprows

    def _get_namecol(self) -> OptInt:
        # Return value if set manually
        if self._namecol is not None:
            return self._namecol

        # In R-tables the first column is always used for record names
        if self.format == CSV_FORMAT_RLANG:
            return 0

        # Get first and second content lines (non comment, non empty) of
        # CSV-file.
        lines = textfile.get_content(self._fileref, lines=2)
        if len(lines) != 2:
            raise FileFormatError(self._fileref, 'DSV')

        # Determine annotation column id from first value in the second line,
        # which can not be converted to a float
        tokens = lines[1].split(self.delimiter)
        values = [col.strip('\"\' \n') for col in tokens]
        for cid, val in enumerate(values):
            try:
                float(val)
            except ValueError:
                return cid
        return None

    def _get_usecols(self, columns: OptStrTuple = None) -> IntTuple:
        # Get column labels
        colnames = self._get_colnames()
        if not columns:
            return tuple(range(len(colnames)))
        # Check if columns exist
        check.is_subset("'columns'", set(columns), 'colnames', set(colnames))
        return tuple(colnames.index(col) for col in columns)

    def _get_fmt_params(self) -> StrDict:
        return {'delimiter': self.delimiter}

    def _open_read(self, columns: OptStrTuple = None) -> Reader:
        usecols = self._get_usecols(columns)
        skiprows = self._get_skiprows()
        fields = self.fields
        usefields = [fields[colid] for colid in usecols]
        fmt = self._get_fmt_params()
        return Reader(
            self._fileref, skiprows=skiprows, usecols=usecols, fields=usefields,
            **fmt)

    def _open_write(self, columns: OptStrTuple = None) -> Writer:
        fmt = self._get_fmt_params()
        return Writer(
            self._fileref, header=self.colnames, comment=self.comment, **fmt)

#
# DEPRECATED
#

def save(
        file: FileOrPathLike, data: NpArray, labels: OptStrList = None,
        comment: OptStr = None, delimiter: str = ',') -> None:
    """Save NumPy array to CSV-file.

    Args:
        file: String, :term:`path-like object` or :term:`file object` that
            points to a valid CSV-file in the directory structure of the system.
        data: :class:`numpy.ndarray` containing the data which is to be
            exported to a CSV-file.
        comment: String, which is included in the CSV-file whithin initial
            '#' lines. By default no initial lines are created.
        labels: List of strings with column names.
        delimiter: String containing DSV-delimiter. The default value is ','

    Returns:
        True if no error occured.

    """
    # Check and prepare arguments
    if isinstance(comment, str):
        comment = '# ' + comment.replace('\n', '\n# ') + '\n\n'
        if isinstance(labels, list):
            comment += delimiter.join(labels)
    elif isinstance(labels, list):
        comment = delimiter.join(labels)

    # Get number of columns from last entry in data.shape
    cols = list(getattr(data, 'shape'))[-1]

    # Get column format
    fmt = delimiter.join(['%s'] + ['%10.10f'] * (cols - 1))

    with textfile.openx(file, mode='w') as fh:
        np.savetxt(fh, data, fmt=fmt, header=comment, comments='')
