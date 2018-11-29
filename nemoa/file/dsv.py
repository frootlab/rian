# -*- coding: utf-8 -*-
"""Delimiter separated value file I/O.

File formats that use delimiter-separated values (DSV) store two-dimensional
arrays of data by separating the values in each row with specific delimiter
characters. Most database and spreadsheet programs are able to read or save data
in a delimited format, which makes it particularly suitable as a fallback for
data exchange. For more information please see the `wikipedia article`_.

.. _wikipedia article:
    https://en.wikipedia.org/wiki/Delimiter-separated_values

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
IterIOBase = Iterator['IOBase']

#
# Constants
#

DSV_FORMAT_RFC4180 = 0
DSV_FORMAT_RTABLE = 1

#
# DSV-file I/O Base Class
#

class IOBase(ABC):
    """DSV-file IOBase Class."""

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

    def __iter__(self) -> 'IOBase':
        return self

    def __next__(self) -> tuple:
        return self.read_row()

    def __enter__(self) -> 'IOBase':
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
# DSV-Reader Class
#

class Reader(IOBase):
    """DSV-Reader Class.

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

    def read_rows(self) -> List[tuple]:
        return [row for row in self]

    def write_row(self, row: Iterable) -> None:
        raise OSError("writing rows is not supported in reading mode")

    def write_rows(self, row: List[Iterable]) -> None:
        raise OSError("writing rows is not supported in reading mode")

#
# DSV-Writer Class
#

class Writer(IOBase):
    """DSV-Writer Class.

    Args:
        file:
        header:
        comment:
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
        file: String or :term:`path-like object`, which points to a readable
            DSV-file in the directory structure of the system, or a :term:`file
            object` in reading mode.
        delim: String containing DSV-delimiter. By default the DSV-delimiter is
            detected from the DSV-file.
        labels: List of column labels in DSV-file. By default the list of column
            labels is taken from the first content line in the DSV-file.
        usecols: Indices of the columns which are to be imported from the file.
            By default all columns are imported.
        namecol: Column ID of column, which contains the row annotation.
            By default the first column is used for annotation.

    """

    #
    # Class Variables
    #

    _delim_candidates: ClassVar[StrList] = [',', '\t', ';', ' ', ':', '|']
    """
    Optional list of strings containing delimiter candidates to search for.
    Default: [',', '\t', ';', ' ', ':']
    """

    _delim_mincount: ClassVar[int] = 3
    """
    Minimum number of lines used to detect DSV delimiter. Thereby only non
    comment and non empty lines are used.
    """

    _delim_maxcount: ClassVar[int] = 100
    """
    Maximum number of lines used to detect DSV delimiter. Thereby only non
    comment and non empty lines are used.
    """

    #
    # Public Attributes
    #

    comment: property = attrib.Virtual(fget='_get_comment')
    comment.__doc__ = """
    String containing the initial '#' lines of the DSV-file or an empty string,
    if no initial comment lines could be detected.
    """

    delim: property = attrib.Virtual(fget='_get_delim')
    delim.__doc__ = """
    Delimiter string of the DSV-file or None, if the delimiter could not be
    detected.
    """

    format: property = attrib.Virtual(fget='_get_format')
    format.__doc__ = """
    DSV-Header format. The following formats are supported:
        0: :RFC:`4180`:
            The column header equals the size of the rows.
        1: `R-Table`:
            The column header has a size that is reduced by one, compared to the
            rows. This smaller number of entries follows by the convention, that
            in R the DSV export of tables adds an extra column with row names
            as the first column. The column name of this column is omitted
            within the header.
    """

    colnames: property = attrib.Virtual(fget='_get_colnames')
    colnames.__doc__ = """
    List of strings containing column names from first non comment, non empty
    line of DSV-file.
    """

    fields: property = attrib.Virtual(fget='_get_fields')
    colnames.__doc__ = """
    List of pairs containing the column names and the estimated or given column
    types of the DSV-file.
    """

    rownames: property = attrib.Virtual(fget='_get_rownames')
    rownames.__doc__ = """
    List of strings containing row names from column with id given by namecol or
    None, if namecol is not given.
    """

    namecol: property = attrib.Virtual(fget='_get_namecol')
    namecol.__doc__ = """
    Index of the column of a DSV-file that contains the row names. The value
    None is used for DSV-files that do not contain row names.
    """

    #
    # Protected Attributes
    #

    _fileref: property = attrib.Content(classinfo=FileRefClasses)
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

        self._fileref = file
        self._comment = comment
        self._delim = delim
        self._csvformat = csvformat
        self._colnames = labels
        self._namecol = namecol

    #
    # Public Methods
    #

    def select(self, columns: OptStrTuple = None) -> OptNpArray:
        """Load numpy ndarray from DSV-file.

        Args:
            columns: List of column labels in DSV-file. By default the list of
                column labels is taken from the first content line in the
                DSV-file.

        Returns:
            :class:`numpy.ndarray` containing data from DSV-file, or None if
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

        # Import data from DSV-file as numpy array
        with textfile.openx(self._fileref, mode='r') as fh:
            return np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delim(),
                usecols=usecols,
                dtype={'names': names, 'formats': formats})

    @contextlib.contextmanager
    def open(
            self, mode: str = 'r', columns: OptStrTuple = None) -> IterIOBase:
        """Open DSV-file in reading or writing mode.

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
        fh: IOBase
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
            return fp.read_rows()

    def write(self, rows: List[Iterable]) -> None:
        with self.open(mode='w') as fp:
            fp.write_rows(rows)

    #
    # Protected Methods
    #

    def _get_comment(self) -> str:
        # Return comment if set manually
        if self._comment is not None:
            return self._comment
        return textfile.get_comment(self._fileref)

    def _get_delim(self) -> OptStr:
        # Return delimiter if set manually
        if self._delim is not None:
            return self._delim

        # Initialize DSV-Sniffer with default values
        sniffer = csv.Sniffer()
        sniffer.preferred = self._delim_candidates
        delim: OptStr = None

        # Detect delimiter
        with textfile.openx(self._fileref, mode='r') as fd:
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
        # DSV-file
        lines = textfile.get_content(self._fileref, lines=2)
        if len(lines) != 2:
            return None

        # Determine column label format
        delim = self.delim
        if lines[0].count(delim) == lines[1].count(delim):
            return DSV_FORMAT_RFC4180
        if lines[0].count(delim) == lines[1].count(delim) - 1:
            return DSV_FORMAT_RTABLE
        return None

    def _get_colnames(self) -> StrList:
        # Return value if set manually
        if self._colnames is not None:
            return self._colnames

        # Get first content line (non comment, non empty) of DSV-file
        try:
            line = textfile.get_content(self._fileref, lines=1)[0]
        except IndexError as err:
            raise FileFormatError(self._fileref, 'DSV') from err

        # Read column names from first content line
        names = [col.strip('\"\'\n\r\t ') for col in line.split(self.delim)]
        if self.format == DSV_FORMAT_RFC4180:
            colnames = names
        elif self.format == DSV_FORMAT_RTABLE:
            if not 'name' in names:
                colnames = ['name'] + names
            else:
                i = 1
                while f'name_{i}' in names:
                    i += 1
                colnames = [f'name_{i}'] + names
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
        delim = self.delim
        lines = textfile.get_content(self._fileref, lines=3)
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
        # TODO (patrick.michl@gmail.com): Reimplement without using numpy
        # Check type of 'cols'
        lblcol = self._get_namecol()
        if lblcol is None:
            return None
        lbllbl = self.colnames[lblcol]

        # Import DSV-file to Numpy ndarray
        with textfile.openx(self._fileref, mode='r') as fh:
            rownames = np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delim(),
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
        if self.format == DSV_FORMAT_RTABLE:
            return 0

        # Get first and second content lines (non comment, non empty) of
        # DSV-file
        lines = textfile.get_content(self._fileref, lines=2)
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
        comment: OptStr = None, delim: str = ',') -> None:
    """Save NumPy array to DSV-file.

    Args:
        file: String, :term:`path-like object` or :term:`file object` that
            points to a valid DSV-file in the directory structure of the system.
        data: :class:`numpy.ndarray` containing the data which is to be
            exported to a DSV-file.
        comment: String, which is included in the DSV-file whithin initial
            '#' lines. By default no initial lines are created.
        labels: List of strings with column names.
        delim: String containing DSV-delimiter. The default value is ','

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
