# -*- coding: utf-8 -*-
"""I/O functions for workspace files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import locale
import time
import warnings

from zipfile import BadZipFile, ZipFile, ZipInfo
from contextlib import contextmanager
from io import TextIOWrapper, BytesIO
from pathlib import Path, PurePath

from nemoa.common import nioini, npath
from nemoa.exceptions import BadWorkspaceFile, DirNotEmptyError
from nemoa.types import (
    BinaryFile, BytesIOLike, BytesLike, IterFileLike, List,
    OptBytes, OptStr, OptPath, PathLike, PathLikeList, TextFile,
    Traceback, StrDict, StrDict2, StrList)

ZipInfoList = List[ZipInfo]

ENCODING = locale.getpreferredencoding()
FILEEXTS = ['.zip', '.ws']

class NwsFile:
    """Context Manager for reading and writing workspace files."""

    _CFGFILE: Path = Path('workspace.ini')
    _CFGSTRUCT: StrDict2 = {
        'workspace': {
            'about': 'str',
            'branch': 'str',
            'version': 'str',
            'license': 'str',
            'maintainer': 'str',
            'email': 'str',
            'startup_script': 'path'}}

    _buffer: BytesIOLike
    _file: ZipFile
    _cfg: StrDict
    _path: Path
    _pwd: OptBytes
    _changed: bool

    def __init__(self, filepath: PathLike, pwd: OptBytes = None) -> None:
        """Load nemoa workspace from file."""
        self.load(filepath, pwd=pwd)

    def load(self, filepath: PathLike, pwd: OptBytes = None) -> None:
        """Load Workspace from File."""
        # Initialize instance variables
        self._cfg = {}
        self._changed = False
        self._path = npath.getpath(filepath)
        self._pwd = pwd
        self._buffer = BytesIO()
        self._file = ZipFile(self._buffer, mode='w')

        # Extract ZipFile to Buffer
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            try:
                with ZipFile(self._path, mode='r') as zipfile:
                    # Copy all members from workspace file to memory
                    # TODO: writing new archives currently does not
                    # support encryption. See:
                    # https://docs.python.org/3/library/zipfile.html
                    for zinfo in zipfile.infolist():
                        data = zipfile.read(zinfo, pwd=pwd)
                        self._file.writestr(zinfo, data)
            except FileNotFoundError as err:
                raise FileNotFoundError(
                    f"file '{filepath}' does not exist") from err
            except BadZipFile as err:
                raise BadZipFile(
                    f"file '{filepath}' is not a valid ZIP file") from err

        # Try to open and load workspace configuration from buffer
        try:
            with self.open(self._CFGFILE) as file:
                cfg = nioini.load(file, self._CFGSTRUCT)
        except KeyError as err:
            raise BadWorkspaceFile(
                f"workspace '{self._path}' is not valid: '{self._CFGFILE}' "
                "is missing") from err

        # Check if configuration contains required sections
        rsec = self._CFGSTRUCT.keys()
        if rsec > cfg.keys():
            raise BadWorkspaceFile(
                f"workspace '{self._path}' is not valid: '{self._CFGFILE}' "
                f"requires sections '{rsec}'") from err

        # Link configuration
        self._cfg = cfg.get('workspace', {})

    @contextmanager
    def open(
            self, filepath: PathLike, mode: str = '',
            encoding: OptStr = None) -> IterFileLike:
        """Open file within the workspace.

        Args:
            filepath:
            mode: String, which characters specify the mode in which the file is
                to be opened. It defaults to 'r' which means open for reading in
                text mode. Suported characters are:
                'r': Open for reading (default)
                'w': Open for writing
                'b': Binary mode
                't': Text mode (default)
            encoding:

        """
        # Get default values
        encoding = encoding or ENCODING

        # Get path representation for workspace member
        path = Path(filepath)

        # Open file handler to workspace member
        if 'w' in mode:
            file = self._open_write(path)
        else:
            file = self._open_read(path)

        # Format buffered stream as bytes-stream or text-stream
        try:
            if 'b' in mode:
                yield file
            else:
                yield TextIOWrapper(
                    file, encoding=encoding, write_through=True)
        finally:
            file.close()

    def _open_read(self, path: PathLike) -> BytesIOLike:
        """Open workspace member for reading."""
        # Locate workspace member by it's path
        # and open file handler for reading the file
        matches = self._locate(path)
        if not matches:
            fname = PurePath(path).as_posix()
            raise KeyError(
                f"member with filename '{fname}' does not exist")
        # Select latest version of file
        zinfo = matches[-1]
        return self._file.open(zinfo, pwd=self._pwd, mode='r')

    def _open_write(self, path: PathLike) -> BytesIOLike:
        """Open workspace member for writing."""
        # Determine workspace member name from path
        # and open file handler for writing file
        zinfo = ZipInfo(
            filename=PurePath(path).as_posix(),
            date_time=time.localtime()[:6])
        # Catch Warning for duplicate files
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            file = self._file.open(zinfo, mode='w', pwd=self._pwd)
        self._changed = True
        return file

    def read_text(self, filepath: PathLike, encoding: OptStr = None) -> str:
        """Read text from file."""
        with self.open(filepath, mode='r', encoding=encoding) as file:
            text = file.read()
        if not isinstance(text, str):
            return ''
        return text

    def read_bytes(self, filepath: PathLike) -> bytes:
        """Read bytes from file."""
        with self.open(filepath, mode='rb') as file:
            blob = file.read()
        if not isinstance(blob, bytes):
            return b''
        return blob

    def write_text(
            self, text: str, filepath: PathLike,
            encoding: OptStr = None) -> int:
        """Write text to file.

        Returns:
            Number of characters written.

        """
        with self.open(filepath, mode='w', encoding=encoding) as file:
            if isinstance(file, TextFile):
                return file.write(text)
        return 0

    def write_bytes(self, blob: BytesLike, filepath: PathLike) -> int:
        """Write bytes to file.

        Returns:
            Number of bytes written.

        """
        with self.open(filepath, mode='wb') as file:
            if isinstance(file, BinaryFile):
                return file.write(blob)
        return 0

    def unlink(self, filepath: PathLike) -> bool:
        """Remove file or symbolic link from workspace.

        If the path points to a directory, use rmdir() instead.
        """
        matches = self._locate(filepath)
        if not matches:
            return True
        if getattr(matches[-1], 'is_dir')():
            raise IsADirectoryError(
                f"the requested path '{str(filepath)}' is a directory"
                ", not a file")
        return self._remove(matches)

    def mkdir(self, dirpath: PathLike, exist_ok: bool = False) -> None:
        """Create a new directory at the given path.

        Args:
            dirpath:
            exist_ok: boolean value which determines, if FileExistsError is
                raised, if the target directory already exists.

        Raises:
            FileExistsError If the path already exists.

        """
        dirname = PurePath(dirpath).as_posix() + '/'
        if not self._locate(dirname):
            return self._file.write(dirname)
        if not exist_ok:
            raise FileExistsError(f"directory '{dirname}' does already exist")
        return None

    def rmdir(self, dirpath: PathLike, recursive: bool = False) -> bool:
        """Remove directory from workspace."""
        matches = self._locate(dirpath)
        dirname = PurePath(dirpath).as_posix() + '/'
        if not matches:
            raise FileNotFoundError(f"directory '{dirname}' does not exist")
        files = self.get_files(dirname + '*')
        if not files:
            return self._remove(matches)
        if not recursive:
            raise DirNotEmptyError(f"directory '{dirname}' is not empty")
        allmatches = matches
        for file in files:
            allmatches += self._locate(file)
        return self._remove(allmatches)

    def _locate(self, path: PathLike, sort: bool = True) -> ZipInfoList:
        """Locate workspace members by their path."""
        # Get list of member zipinfos
        zinfos = self._file.infolist()
        # Match members by path-like filenames
        matches = [i for i in zinfos if Path(i.filename) == Path(path)]
        if sort:
            # Sort matches by datetime
            matches = sorted(matches, key=lambda i: i.date_time)
        # Return sorted matches
        return matches

    def save(self) -> None:
        """Save the workspace to it's original file path."""
        self.saveas(self._path)

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file."""
        # Update 'workspace.ini'
        with self.open(self._CFGFILE, mode='w') as file:
            config = {'workspace': self._cfg}
            nioini.save(config, file)

        # Remove duplicates from workspace
        self._remove_duplicates()

        # Mark plattform, which created the files as Windows
        # to avoid Unix permissions to be inferred as 0000
        for zinfo in self._file.infolist():
            zinfo.create_system = 0

        # Close ZipArchive to read buffer
        self._file.close()

        # Read buffer and write to file
        if isinstance(self._buffer, BytesIO):
            with open(filepath, 'wb') as file:
                file.write(self._buffer.getvalue())
        else:
            raise TypeError("buffer has not been initialized")

        # Close buffer
        self._buffer.close()

        # Reopen file
        self.load(self._path, pwd=self._pwd)

    def get_files(self, pattern: OptStr = None) -> StrList:
        """Get list of files in the workspace."""
        # Get list of normalized unique paths of workspace members
        paths: PathLikeList = []
        for zinfo in self._file.infolist():
            path = PurePath(zinfo.filename).as_posix()
            if getattr(zinfo, 'is_dir')():
                path += '/'
            if path not in paths:
                paths.append(path)

        # Match path list with given pattern
        if pattern:
            paths = npath.match(paths, pattern)

        # Sort paths
        return sorted([str(path) for path in paths])

    def _remove(self, zinfos: ZipInfoList) -> bool:
        """Remove members from workspace.

        Args:
            zinfos: List of ZipInfo entries, which are to be removed from
                the workspace

        Returns:
            Boolean value which is true if no error occured.

        """
        if not zinfos:
            return True

        # Remove given entries from the list of workspace members
        new_zinfos = []
        zids = [(zinfo.filename, zinfo.date_time) for zinfo in zinfos]
        for zinfo in self._file.infolist():
            zid = (zinfo.filename, zinfo.date_time)
            if zid in zids:
                zids.remove(zid)
            else:
                new_zinfos.append(zinfo)

        # If any entry on the list could not be found raise an error
        if zids:
            names = [zid[0] for zid in zids]
            raise KeyError(f"could not locate workspace members: {names}")

        # Create new ZipArchive in Memory
        new_buffer = BytesIO()
        new_file = ZipFile(new_buffer, mode='w')

        # Copy all workspace members on the new list from current
        # to new workspace
        for zinfo in new_zinfos:
            data = self._file.read(zinfo, pwd=self._pwd)
            new_file.writestr(zinfo, data)

        # Close current workspace and buffer and link new workspace and buffer
        self._file.close()
        self._buffer.close()
        self._buffer = new_buffer
        self._file = new_file

        self._changed = True

        return True

    def _remove_duplicates(self) -> bool:
        """Remove all duplicates from workspace."""
        # Get list of duplicates
        zinfos: ZipInfoList = []
        for filename in self.files:
            zinfos += self._locate(filename, sort=True)[:-1]

        # Remove duplicates
        return self._remove(zinfos)

    def close(self) -> None:
        """Close current workspace and buffer."""
        self._file.close()
        self._buffer.close()

    @property
    def name(self) -> OptStr:
        """Filename of the workspace without file extension."""
        return getattr(self._path, 'stem')

    @property
    def path(self) -> OptPath:
        """Filepath of the workspace."""
        return self._path

    @property
    def files(self) -> StrList:
        """List of all files within the workspace."""
        return self.get_files()

    @property
    def folders(self) -> StrList:
        """List of folders within the workspace."""
        # Get list of unique foldernames in POSIX standard
        names: StrList = []
        for zinfo in self._file.infolist():
            if getattr(zinfo, 'is_dir')():
                name = PurePath(zinfo.filename).as_posix() + '/'
                names.append(name)
        return sorted(names)

    @property
    def members(self) -> ZipInfoList:
        """List of members within the workspace."""
        # Get list of worksoace members as ZipInfo
        return self._file.infolist()

    def __enter__(self) -> 'NwsFile':
        """ """
        return self

    def __exit__(self, etype: str, value: int, tb: Traceback) -> None:
        """ """
        self.close()
        # Error handling
        if etype:
            print(f'exc_type: {etype}')
            print(f'exc_value: {value}')
            print(f'exc_traceback: {tb}')

    def __eq__(self, other: object) -> bool:
        """Compare workspaces by path."""
        return self.path == getattr(other, 'path')
