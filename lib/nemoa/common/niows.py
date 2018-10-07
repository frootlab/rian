# -*- coding: utf-8 -*-
"""I/O functions for workspace files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import time
import warnings

from zipfile import BadZipFile, ZipFile, ZipInfo
from contextlib import contextmanager
from io import TextIOWrapper, BytesIO
from pathlib import Path, PurePath

from nemoa.common import nioini, npath, nsysinfo
from nemoa.classes import Attr, ReadOnlyAttr, ReadWriteAttr
from nemoa.errors import BadWsFile, DirNotEmptyError, FileNotGivenError
from nemoa.types import (
    BinaryFile, BytesIOLike, BytesLike, IterFileLike, List,
    OptBytes, OptStr, OptPath, OptPathLike, PathLike, PathLikeList,
    TextFile, Traceback, StrDict, StrDict2, StrList)

ZipInfoList = List[ZipInfo]

ENCODING = nsysinfo.encoding()
FILEEXTS = ['.ws.zip', '.ws', '.zip']

class WsFile:
    """I/O handling of Workspace Files."""

    _CFGFILE: Path = Path('workspace.ini')
    _CFGSTRUCT: StrDict2 = {
        'workspace': {
            'about': 'str',
            'license': 'str',
            'maintainer': 'str',
            'email': 'str',
            'startup': 'path'}}
    _CFGDEFAULT: StrDict2 = {
        'workspace': {
            'maintainer': nsysinfo.username()}}
    _DIRDEFAULT: StrList = [
        'dataset', 'network', 'system', 'model', 'script']

    _buffer: BytesIOLike
    _file: ZipFile
    _cfg: StrDict
    _path: OptPath
    _pwd: OptBytes
    _changed: bool

    about: Attr = ReadWriteAttr(str, key='_cfg')
    """Summary description of the workspace.

    Short description of the contents, the purpose or the application of the
    workspace. The attribute about is inherited by resources, that are created
    inside the workspace.
    """

    email: Attr = ReadWriteAttr(str, key='_cfg')
    """Email address of the maintainer of the workspace.

    Email address to a person, an organization, or a service that is responsible
    for the content of the workspace. The attribute email is inherited by
    resources, that are created inside the workspace.
    """

    license: Attr = ReadWriteAttr(str, key='_cfg')
    """License for the usage of the contents of the workspace.

    Namereference to a legal document giving specified users an official
    permission to do something with the contents of the workspace. The attribute
    license is inherited by resources, that are created inside the workspace.
    """

    maintainer: Attr = ReadWriteAttr(str, key='_cfg')
    """Name of the maintainer of the workspace.

    A person, an organization, or a service that is responsible for the content
    of the workspace. The attribute maintainer is inherited by resources, that
    are created inside the workspace.
    """

    startup: Attr = ReadWriteAttr(Path, key='_cfg')
    """Path that points to a python script inside the workspace.

    The startup script identifies a python script that is aimed to be executed
    after loading the workspace.
    """

    files: Attr = ReadOnlyAttr(list, getter='get_files')
    """List of all files within the workspace."""

    name: Attr = ReadOnlyAttr(list, getter='_get_name')
    """Filename of the workspace without file extension."""

    path: Attr = ReadOnlyAttr(Path, getter='_get_path')
    """Filepath of the workspace."""

    folders: Attr = ReadOnlyAttr(list, getter='_get_folders')
    """List of all folders within the workspace."""

    def __init__(
            self, filepath: OptPathLike = None, pwd: OptBytes = None) -> None:
        """Load Workspace from file.

        Args:
            filepath: Filepath that points to a valid workspace file or None
            pwd: Bytes representing password of workspace file

        """
        if filepath:
            self.load(filepath, pwd=pwd)
        else:
            self.create_new()

    def load(self, filepath: PathLike, pwd: OptBytes = None) -> None:
        """Load Workspace from file."""
        # Initialize instance Variables, Buffer and buffered ZipFile
        self._cfg = {}
        self._changed = False
        self._path = npath.getpath(filepath)
        self._pwd = pwd
        self._buffer = BytesIO()
        self._file = ZipFile(self._buffer, mode='w')

        # Copy contents from ZipFile to buffered ZipFile
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            try:
                with ZipFile(self._path, mode='r') as zipfile:
                    for zinfo in zipfile.infolist():
                        data = zipfile.read(zinfo, pwd=pwd)
                        # TODO (patrick.michl@gmail.com): The zipfile standard
                        # module currently does not support encryption in write
                        # mode of new ZipFiles. See:
                        # https://docs.python.org/3/library/zipfile.html
                        # When support is provided, the below line for writing
                        # files shall be replaced by:
                        # self._file.writestr(zinfo, data, pwd=pwd)
                        self._file.writestr(zinfo, data)
            except FileNotFoundError as err:
                raise FileNotFoundError(
                    f"file '{self._path}' does not exist") from err
            except BadZipFile as err:
                raise BadZipFile(
                    f"file '{self._path}' is not a valid ZIP file") from err

        # Try to open and load workspace configuration from buffer
        try:
            with self.open(self._CFGFILE) as file:
                cfg = nioini.load(file, self._CFGSTRUCT)
        except KeyError as err:
            raise BadWsFile(
                f"workspace '{self._path}' is not valid: '{self._CFGFILE}' "
                "is missing") from err

        # Check if configuration contains required sections
        rsec = self._CFGSTRUCT.keys()
        if rsec > cfg.keys():
            raise BadWsFile(
                f"workspace '{self._path}' is not valid: '{self._CFGFILE}' "
                f"requires sections '{rsec}'") from err

        # Link configuration
        self._cfg = cfg.get('workspace', {})

    def create_new(self) -> None:
        """Create new Workspace."""
        # Initialize instance Variables, Buffer and buffered ZipFile
        self._cfg = self._CFGDEFAULT['workspace'].copy()
        self._changed = False
        self._path = None
        self._pwd = None
        self._buffer = BytesIO()
        self._file = ZipFile(self._buffer, mode='w')

        # Create folders
        for folder in self._DIRDEFAULT:
            self.mkdir(folder)

    @contextmanager
    def open(
            self, filepath: PathLike, mode: str = '', encoding: OptStr = None,
            isdir: bool = False) -> IterFileLike:
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
            isdir: Boolean value which determines, if the filepath is to be
                treated as a directory. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        """
        # Get default values
        encoding = encoding or ENCODING

        # Get path representation for workspace member
        path = Path(filepath)

        # Open file handler to workspace member
        if 'w' in mode:
            file = self._open_write(path, isdir=isdir)
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

    def _open_write(self, path: PathLike, isdir: bool = False) -> BytesIOLike:
        """Open workspace member for writing.

        Args:
            path:
            isdir: Boolean value which determines, if the filepath is to be
                treated as a directory. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        """
        # Determine workspace member name from path
        # and get ZipInfo with local time as date_time
        filename = PurePath(path).as_posix()
        if isdir:
            filename += '/'
        zinfo = ZipInfo( # type: ignore
            filename=filename, date_time=time.localtime()[:6])
        # Catch Warning for duplicate files
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            # TODO (patrick.michl@gmail.com): The zipfile standard
            # module currently does not support encryption in write
            # mode of new ZipFiles. See:
            # https://docs.python.org/3/library/zipfile.html
            # When support is provided, the below line for writing
            # files shall be replaced by:
            # file = self._file.open(zinfo, mode='w', pwd=self._pwd)
            file = self._file.open(zinfo, mode='w')
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

    def mkdir(self, path: PathLike, exist_ok: bool = False) -> None:
        """Create a new directory at the given path.

        Args:
            path:
            exist_ok: boolean value which determines, if FileExistsError is
                raised, if the target directory already exists.

        Raises:
            FileExistsError If the path already exists.

        """
        matches = self._locate(path)
        if not matches:
            with self.open(path, mode='w', isdir=True):
                pass
        elif not exist_ok:
            name = PurePath(path).as_posix() + '/'
            raise FileExistsError(f"directory '{name}' does already exist")

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
        if isinstance(self._path, Path):
            self.saveas(self._path)
        else:
            raise FileNotGivenError(
                "use saveas() to save the workspace to a file")

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file."""
        path = npath.getpath(filepath)

        # Update 'workspace.ini'
        with self.open(self._CFGFILE, mode='w') as file:
            config = {'workspace': self._cfg}
            nioini.save(config, file)

        # Remove duplicates from workspace
        self._remove_duplicates()

        # Mark plattform, which created the files as Windows
        # to avoid inference of wrong Unix permissions
        for zinfo in self._file.infolist():
            zinfo.create_system = 0

        # Close ZipArchive (to allow to read the buffer)
        self._file.close()

        # Read buffer and write workspace file
        if isinstance(self._buffer, BytesIO):
            with open(path, 'wb') as file:
                file.write(self._buffer.getvalue())
        else:
            raise TypeError("buffer has not been initialized")

        # Close buffer
        self._buffer.close()

        # Load saved workpace file
        self.load(path, pwd=self._pwd)

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

    def _get_name(self) -> OptStr:
        return getattr(self._path, 'stem', None)

    def _get_path(self) -> OptPath:
        return self._path

    def _get_folders(self) -> StrList:
        names: StrList = []
        for zinfo in self._file.infolist():
            if getattr(zinfo, 'is_dir')():
                name = PurePath(zinfo.filename).as_posix() + '/'
                names.append(name)
        return sorted(names)

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
        if hasattr(self._file, 'close'):
            self._file.close()
        if hasattr(self._buffer, 'close'):
            self._buffer.close()

    def __enter__(self) -> 'WsFile':
        """Enter with statement."""
        return self

    def __exit__(self, etype: str, value: int, tb: Traceback) -> None:
        """Close workspaces and buffer."""
        self.close()
        # Error handling
        if etype:
            print(f'exc_type: {etype}')
            print(f'exc_value: {value}')
            print(f'exc_traceback: {tb}')

    def __eq__(self, other: object) -> bool:
        """Compare workspaces by path."""
        return self.path == getattr(other, 'path')
