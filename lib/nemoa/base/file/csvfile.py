# -*- coding: utf-8 -*-
"""I/O functions for CSV-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _RFC4180:
    https://tools.ietf.org/html/rfc4180

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import csv
from pathlib import Path

try:
    import numpy as np
except ImportError as err:
    raise ImportError(
        "requires package numpy: "
        "https://pypi.org/project/numpy") from err

from nemoa.base import check
from nemoa.base.file import textfile
from nemoa.base.container import BaseContainer, ContentAttr, MetadataAttr
from nemoa.base.container import VirtualAttr
from nemoa.types import FileOrPathLike, NpArray, OptInt, OptIntTuple, ClassVar
from nemoa.types import OptNpArray, OptStr, OptStrList, TextIOBaseClass, StrList
from nemoa.types import IntTuple, StrTuple, OptList, OptStrTuple

# Module specific exceptions
class BadCSVFile(OSError):
    """Exception for invalid CSV-files."""

# Module specific types and classinfos
FileClassInfo = (str, Path, TextIOBaseClass)

# Module Constants
FORMAT_STANDARD = 0
FORMAT_RTABLE = 1

class CSVFile(BaseContainer):
    """CSV File.

    Args:
        file: String or `path-like object`_ that points to a readable CSV-file
            in the directory structure of the system, or a `file-like object`_
            in read mode.
        delim: String containing CSV-delimiter. By default the CSV-delimiter is
            detected from the CSV-file.
        labels: List of column labels in CSV-file. By default the list of column
            labels is taken from the first content line in the CSV-file.
        usecols: Indices of the columns which are to be imported from the file.
            By default all columns are imported.
        rowlabelcol: Column ID of column, which contains the row annotation.
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
    # Private Attributes
    #

    _file: property = ContentAttr(FileClassInfo)
    _header: property = MetadataAttr(str, default=None)
    _delim: property = MetadataAttr(str, default=None)
    _format: property = MetadataAttr(str, default=None)
    _colnames: property = MetadataAttr(list, default=None)
    _rownames: property = MetadataAttr(list, default=None)
    _labelid: property = MetadataAttr(int, default=None)

    #
    # Public Attributes
    #

    header: property = VirtualAttr(str, getter='_get_header', readonly=True)
    header.__doc__ = """
    String containing the header of the CSV-file or an empty string, if
    no header could be detected.
    """

    delim: property = VirtualAttr(str, getter='_get_delim', readonly=True)
    delim.__doc__ = """
    Delimiter string of the CSV-file or None, if the delimiter could not be
    detected.
    """

    format: property = VirtualAttr(int, getter='_get_format', readonly=True)
    format.__doc__ = """
    Format of the column labels. The following formats are distinguished:
        0:
            The number of column labels equals the size of the
            CSV records, as desribed in `RFC4180`_.
        1:
            The first column always is used for record annotation
            and therfore does not require a seperate column label for it's
            identification.
    """

    colnames: property = VirtualAttr(getter='_get_colnames', readonly=True)
    colnames.__doc__ = """
    List of strings containing column names from first non comment, non empty
    line of CSV-file.
    """

    rownames: property = VirtualAttr(getter='_get_rownames', readonly=True)
    rownames.__doc__ = """
    List of strings containing row names from column with id given by labelid or
    None, if labelid is not given.
    """

    labelid: property = VirtualAttr(int, getter='_get_labelid', readonly=True)
    labelid.__doc__ = """
    Index of the column of a CSV-file that contains the row names. The value
    None is used for CSV-files that do not contain row names.
    """

    def __init__(self, file: FileOrPathLike, mode: str = '',
        header: OptStr = None, delim: OptStr = None, format: OptStr = None,
        labels: OptStrList = None, usecols: OptIntTuple = None,
        labelid: OptInt = None) -> None:
        """Initialize instance attributes."""
        super().__init__()
        self._file = file
        self._header = header
        self._delim = delim
        self._format = format
        self._colnames = labels
        self._labelid = labelid

    def _get_header(self) -> str:
        # Return header if set manually
        if self._header is not None:
            return self._header
        return textfile.get_header(self._file)

    def _get_delim(self,  maxcount: int = 100) -> OptStr:
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
        if self._format is not None:
            return self._format

        # Get first and second content lines (non comment, non empty) of
        # CSV-file
        lines = textfile.get_content(self._file, lines=2)
        if len(lines) != 2:
            return None

        # Determine column label format
        if lines[0].count(self.delim) == lines[1].count(self.delim):
            return FORMAT_STANDARD
        if lines[0].count(self.delim) == lines[1].count(self.delim) - 1:
            return FORMAT_RTABLE
        return None

    def _get_colnames(self) -> StrList:
        # Return value if set manually
        if self._colnames is not None:
            return self._colnames

        # Get first content line (non comment, non empty) of CSV-file
        line = textfile.get_content(self._file, lines=1)[0]

        # Get column labels from first content
        labels = [col.strip('\"\'\n\r\t ') for col in line.split(self.delim)]

        # Format column labels
        if self.format == FORMAT_STANDARD:
            return labels
        if self.format == FORMAT_RTABLE:
            return [''] + labels
        # TODO (patrick.michl@gmail.com): Give filename!
        raise BadCSVFile("Bad file!")

    def _get_rownames(self) -> OptList:
        # Check type of 'cols'
        lblcol = self._get_labelid()
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

    def _get_labelid(self) -> OptInt:
        # Return value if set manually
        if self._labelid is not None:
            return self._labelid

        # In R-tables the first column is always used for record names
        if self.format == FORMAT_RTABLE:
            return 0

        # Get first and second content lines (non comment, non empty) of
        # CSV-file
        lines = textfile.get_content(self._file, lines=2)
        if len(lines) != 2:
            return None

        # Determine annotation column id from first value in the second line, that
        # can not be converted to a float
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
        check.is_subset(
            "argument 'columns'", set(columns), 'column names', set(colnames))
        return tuple(colnames.index(col) for col in columns)

    def select(self, columns: OptStrTuple = None) -> OptNpArray:
        """Load numpy ndarray from CSV-file.

        Args:
            columns: List of column labels in CSV-file. By default the list of
                column labels is taken from the first content line in the
                CSV-file.

        Returns:
            Numpy ndarray containing data from CSV-file, or None if the data
            could not be imported.

        """
        # Check type of 'cols'
        check.has_opt_type("argument 'columns'", columns, tuple)

        # Get column names and formats
        usecols = self._get_usecols(columns)
        colnames = self._get_colnames()
        names = tuple(colnames[colid] for colid in usecols)
        lblcol = self._get_labelid()
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

        # Import CSV-file to NumPy ndarray
        with textfile.openx(self._file, mode='r') as fh:
            return np.loadtxt(fh,
                skiprows=self._get_skiprows(),
                delimiter=self._get_delim(),
                usecols=usecols,
                dtype={'names': names, 'formats': formats})

def save(
        file: FileOrPathLike, data: NpArray, header: OptStr = None,
        labels: OptStrList = None, delim: str = ',') -> None:
    """Save NumPy array to CSV-file.

    Args:
        file: String, `path-like object`_ or `file-like object`_ that points to
            a valid CSV-file in the directory structure of the system.
        data: NumPy ndarray containing the data which is to be exported to
            a CSV-file.
        header: String which is included in the CSV-file whithin an initial
            comment. If 'header' is None, then no initial comment is created.
            Default: None
        labels: List of strings containing CSV Column labels.
        delim: String containing CSV-delimiter. The default value is ','

    Returns:
        True if no error occured.

    """
    # Check and prepare arguments
    if isinstance(header, str):
        header = '# ' + header.replace('\n', '\n# ') + '\n\n'
        if isinstance(labels, list):
            header += delim.join(labels)
    elif isinstance(labels, list):
        header = delim.join(labels)

    # Get number of columns from last entry in data.shape
    cols = list(getattr(data, 'shape'))[-1]

    # Get column format
    fmt = delim.join(['%s'] + ['%10.10f'] * (cols - 1))

    with textfile.openx(file, mode='w') as fd:
        np.savetxt(fd, data, fmt=fmt, header=header, comments='')
