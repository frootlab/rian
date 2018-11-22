# -*- coding: utf-8 -*-
"""CSV-file I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
import csv
from contextlib import contextmanager
from io import IOBase
import numpy as np
from nemoa.base import attrib, check, literal
from nemoa.file import stream, textfile
from nemoa.types import FileOrPathLike, NpArray, OptInt, OptIntTuple, ClassVar
from nemoa.types import OptNpArray, OptStr, OptStrList, StrList, List, Tuple
from nemoa.types import IntTuple, OptList, OptStrTuple, TextFileClasses
from nemoa.types import Iterable, Iterator, TextIOBaseClass, Any
from nemoa.types import Traceback, ExcType, Exc, Union
from nemoa.types import StrDict, FileRef

#
# Stuctural Types
#

Fields = List[Tuple[str, type]]
CSVStream = Union['CSVReader', 'CSVWriter']
IterCSVStream = Iterator[CSVStream]
IterCSVIOBase = Iterator['CSVIOBase']

#
# Exceptions
#

class BadCSVFile(OSError):
    """Exception for invalid CSV-files."""

#
# Constants
#

CSV_FORMAT_STANDARD = 0
CSV_FORMAT_RTABLE = 1

#
# CSVFileIO
#

class CSVIOBase(ABC):
    """CSV-file IOBase Class."""

    _cman: stream.Connector
    _file: IOBase

    def __init__(self, file: FileRef, mode: str = 'r') -> None:
        self._cman = stream.Connector(file)
        self._file = self._cman.open(mode)
        if not isinstance(self._file, TextIOBaseClass):
            self._cman.close()
            raise ValueError('the opened stream is not a valid text file')

    def __iter__(self) -> 'CSVIOBase':
        return self

    def __next__(self) -> tuple:
        return self.read_row()

    def __enter__(self) -> 'CSVIOBase':
        return self

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self._cman.close()

    @abstractmethod
    def read_row(self) -> tuple:
        raise NotImplementedError()

    @abstractmethod
    def write_row(self, row: Iterable) -> None:
        raise NotImplementedError()

#
# CSVReader Class
#

class CSVReader(CSVIOBase):
    """CSV-file Reader Class.

    Args:
        file:
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

    def write_row(self, row: Iterable) -> None:
        raise OSError("writing rows is not supported in reading mode")

#
# CSVWriter Class
#

class CSVWriter(CSVIOBase):
    """CSV-file Writer Class.

    Args:
        **kwds: :ref:`Dialects and Formatting Parameters<csv-fmt-params>`

    """

    _writer: Any # TODO (patrick.michl@gmail.com): specify!

    def __init__(
            self, file: FileRef, header: StrList,
            comment: OptStr = None, **kwds: Any) -> None:
        super().__init__(file, mode='w')
        self._writer = csv.writer(self._file, **kwds)
        if comment:
            self._write_comment(comment)
        self._write_header(header)

    def _write_comment(self, comment: str) -> None:
        writeline = getattr(self._file, 'writeline')
        for line in comment.splitlines():
            writeline(f'# line\n')

    def _write_header(self, header: StrList) -> None:
        self.write_row(header)

    def read_row(self) -> tuple:
        raise OSError("reading rows is not supported in writing mode")

    def write_row(self, row: Iterable) -> None:
        self._writer.write_row(row)

#
# CSVFile Class
#

class CSVFile(attrib.Container):
    """CSV-File Class.

    Args:
        file: String or :term:`path-like object`, which points to a readable
            CSV-file in the directory structure of the system, or a :term:`file
            object` in reading mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the CSV-file.
        labels: List of column labels in CSV-file. By default the list of column
            labels is taken from the first content line in the CSV-file.
        usecols: Indices of the columns which are to be imported from the file.
            By default all columns are imported.
        namecol: Column ID of column, which contains the row annotation.
            By default the first column is used for annotation.

    """

    #
    # Class Variables
    #

    _delim_candidates: ClassVar[StrList] = [',', '\t', ';', ' ', ':']
    """
    Optional list of strings containing delimiter candidates to search for.
    Default: [',', '\t', ';', ' ', ':']
    """

    _delim_mincount: ClassVar[int] = 3
    """
    Minimum number of lines used to detect CSV delimiter. Thereby only non
    comment and non empty lines are used.
    """

    _delim_maxcount: ClassVar[int] = 100
    """
    Maximum number of lines used to detect CSV delimiter. Thereby only non
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

    delim: property = attrib.Virtual(fget='_get_delim')
    delim.__doc__ = """
    Delimiter string of the CSV-file or None, if the delimiter could not be
    detected.
    """

    format: property = attrib.Virtual(fget='_get_format')
    format.__doc__ = """
    CSV-Header format. The following formats are supported:
        0: :RFC:`4180`:
            The column header equals the size of the rows.
        1: `R-Table`:
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

    _file: property = attrib.Content(classinfo=TextFileClasses)
    _comment: property = attrib.MetaData(classinfo=str, default=None)
    _delim: property = attrib.MetaData(classinfo=str, default=None)
    _format: property = attrib.MetaData(classinfo=str, default=None)
    _colnames: property = attrib.MetaData(classinfo=list, default=None)
    _rownames: property = attrib.MetaData(classinfo=list, default=None)
    _namecol: property = attrib.MetaData(classinfo=int, default=None)

    #
    # Events
    #

    def __init__(self, file: FileRef, mode: str = '',
            comment: OptStr = None, delim: OptStr = None,
            csvformat: OptInt = None, labels: OptStrList = None,
            usecols: OptIntTuple = None, namecol: OptInt = None) -> None:
        """Initialize instance attributes."""
        super().__init__()
        self._file = file
        self._comment = comment
        self._delim = delim
        self._csvformat = csvformat
        self._colnames = labels
        self._namecol = namecol

    #
    # Public Methods
    #

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
        with textfile.openx(self._file, mode='r') as fh:
            return np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delim(),
                usecols=usecols,
                dtype={'names': names, 'formats': formats})

    @contextmanager
    def open(
            self, mode: str = '', columns: OptStrTuple = None) -> IterCSVIOBase:
        """Open CSV-file in reading or writing mode.

        Args:
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is reading mode. Supported
                characters are:
                'r': Reading mode (default)
                'w': Writing mode
            columns:

        Yields:
            :term:`File object`, that supports the given mode.

        """
        # Open file handler
        fh: CSVIOBase
        if 'w' in mode:
            if 'r' in mode:
                raise ValueError(
                    "'mode' is not allowed to contain characters 'r' AND 'w'")
            fh = self._open_write()
        else:
            fh = self._open_read(columns)

        try:
            yield fh
        finally:
            fh.close()

    def read(self) -> List[tuple]:
        with self.open(mode='r') as fp:
            content = [row for row in fp]
        return content

    def write(self, rows: List[Iterable]) -> None:
        with self.open(mode='w') as fp:
            for row in rows:
                fp.write_row(row)

    #
    # Protected Methods
    #

    def _get_comment(self) -> str:
        # Return comment if set manually
        if self._comment is not None:
            return self._comment
        return textfile.get_comment(self._file)

    def _get_delim(self) -> OptStr:
        # Return delimiter if set manually
        if self._delim is not None:
            return self._delim

        # Initialize CSV-Sniffer with default values
        sniffer = csv.Sniffer()
        sniffer.preferred = self._delim_candidates
        delim: OptStr = None

        # Detect delimiter
        with textfile.openx(self._file, mode='r') as fd:
            size, probe = 0, ''
            for line in fd:
                # Check termination criteria
                if size > self._delim_maxcount:
                    break
                # Check exclusion criteria
                strip = line.strip()
                if not strip or strip.startswith('#'):
                    continue
                # Increase probe size
                probe += line
                size += 1
                if size <= self._delim_mincount:
                    continue
                # Try to detect delimiter from probe using csv.Sniffer
                try:
                    dialect = sniffer.sniff(probe)
                except csv.Error:
                    continue
                delim = dialect.delimiter
                break

        return delim

    def _get_format(self) -> OptInt:
        # Return value if set manually
        if self._csvformat is not None:
            return self._csvformat

        # Get first and second content lines (non comment, non empty) of
        # CSV-file
        lines = textfile.get_content(self._file, lines=2)
        if len(lines) != 2:
            return None

        # Determine column label format
        delim = self.delim
        if lines[0].count(delim) == lines[1].count(delim):
            return CSV_FORMAT_STANDARD
        if lines[0].count(delim) == lines[1].count(delim) - 1:
            return CSV_FORMAT_RTABLE
        return None

    def _get_colnames(self) -> StrList:
        # Return value if set manually
        if self._colnames is not None:
            return self._colnames

        # Get first content line (non comment, non empty) of CSV-file
        line = textfile.get_content(self._file, lines=1)[0]

        # Get column names from first content line
        names = [col.strip('\"\'\n\r\t ') for col in line.split(self.delim)]

        # Format column labels
        if self.format == CSV_FORMAT_STANDARD:
            return names
        if self.format == CSV_FORMAT_RTABLE:
            return [''] + names
        raise BadCSVFile(f"file {self._file.name} is not valid")

    def _get_fields(self) -> Fields:
        colnames = self.colnames
        delim = self.delim
        lines = textfile.get_content(self._file, lines=3)
        if len(lines) != 3:
            return []
        row1 = lines[1].split(delim)
        row2 = lines[2].split(delim)
        fields = []
        for colname, str1, str2 in zip(colnames, row1, row2):
            type1 = literal.estimate(str1)
            if type1:
                type2 = literal.estimate(str1)
                if type2 == type1:
                    fields.append((colname, type1))
                    continue
            fields.append((colname, str))
        return fields

    def _get_rownames(self) -> OptList:
        # Check type of 'cols'
        lblcol = self._get_namecol()
        if lblcol is None:
            return None
        lbllbl = self.colnames[lblcol]

        # Import CSV-file to NumPy ndarray
        with textfile.openx(self._file, mode='r') as fh:
            rownames = np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delim(),
                usecols=(lblcol, ),
                dtype={'names': (lbllbl, ), 'formats': ('<U12', )})
        return [name[0] for name in rownames.flat]

    def _get_skiprows(self) -> int:
        # Count how many 'comment' and 'blank' rows are to be skipped
        skiprows = 1
        with textfile.openx(self._file, mode='r') as fd:
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
        if self.format == CSV_FORMAT_RTABLE:
            return 0

        # Get first and second content lines (non comment, non empty) of
        # CSV-file
        lines = textfile.get_content(self._file, lines=2)
        if len(lines) != 2:
            return None

        # Determine annotation column id from first value in the second line,
        # which can not be converted to a float
        values = [col.strip('\"\' \n') for col in lines[1].split(self.delim)]
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
        return {
            'delimiter': self.delim}

    def _open_read(self, columns: OptStrTuple = None) -> CSVReader:
        usecols = self._get_usecols(columns)
        skiprows = self._get_skiprows()
        fields = self.fields
        usefields = [fields[colid] for colid in usecols]
        fmt = self._get_fmt_params()
        return CSVReader(
            self._file, skiprows=skiprows, usecols=usecols, fields=usefields,
            **fmt)

    def _open_write(self, columns: OptStrTuple = None) -> CSVWriter:
        fmt = self._get_fmt_params()
        return CSVWriter(
            self._file, header=self.colnames, comment=self.comment, **fmt)

#
# DEPRECATED
#

def save(
        file: FileOrPathLike, data: NpArray, labels: OptStrList = None,
        comment: OptStr = None, delim: str = ',') -> None:
    """Save NumPy array to CSV-file.

    Args:
        file: String, :term:`path-like object` or :term:`file object` that
            points to a valid CSV-file in the directory structure of the system.
        data: :class:`numpy.ndarray` containing the data which is to be
            exported to a CSV-file.
        comment: String, which is included in the CSV-file whithin initial
            '#' lines. By default no initial lines are created.
        labels: List of strings with column names.
        delim: String containing CSV-delimiter. The default value is ','

    Returns:
        True if no error occured.

    """
    # Check and prepare arguments
    if isinstance(comment, str):
        comment = '# ' + comment.replace('\n', '\n# ') + '\n\n'
        if isinstance(labels, list):
            comment += delim.join(labels)
    elif isinstance(labels, list):
        comment = delim.join(labels)

    # Get number of columns from last entry in data.shape
    cols = list(getattr(data, 'shape'))[-1]

    # Get column format
    fmt = delim.join(['%s'] + ['%10.10f'] * (cols - 1))

    with textfile.openx(file, mode='w') as fh:
        np.savetxt(fh, data, fmt=fmt, header=comment, comments='')
