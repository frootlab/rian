# -*- coding: utf-8 -*-
"""I/O functions for nemoa workspace files."""

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

from nemoa.common import nioini, npath
from nemoa.exceptions import BadWorkspaceFile
from nemoa.types import (
    BytesIOLike, IterFileLike, List, OptBytes, OptStr, OptPath,
    PathLike, PathLikeList, Traceback, StrDict, StrDict2, StrList)

ZipInfoList = List[ZipInfo]

FILEEXTS = ['.zip', '.nws']

class NwsFile:
    """Context Manager for Reading and Writing Nemoa Workspace files (NWS)."""

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
                    # Copy all members from archive file to memory
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
            with self.open(self._CFGFILE, fmt=str) as file:
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
            self, filepath: PathLike, mode: str = 'r',
            fmt: type = bytes) -> IterFileLike:
        """Open archive member as file handler."""
        # Get path representation for archive member
        path = Path(filepath)

        # Open file handler to archive member
        if mode == 'r':
            file = self._open_read(path)
        elif mode == 'w':
            file = self._open_write(path)
        else:
            raise ValueError(
                "argument 'mode' is required to be 'r' or 'w'"
                f", not {mode}")

        # Format buffered stream as bytes-stream or text-stream
        try:
            if issubclass(fmt, bytes):
                yield file
            elif issubclass(fmt, str):
                yield TextIOWrapper(file, write_through=True)
            else:
                raise ValueError(
                    "argument 'fmt' is required to be a subclass of "
                    "str or bytes")
        finally:
            file.close()

    def _open_read(self, path: PathLike) -> BytesIOLike:
        """Open archive member for reading."""
        # Locate archive member by it's path
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
        """Open archive member for writing."""
        # Determine archive member name from path
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

    def _locate(self, path: PathLike, sort: bool = True) -> ZipInfoList:
        """Locate archive members by their path."""
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
        with self.open(self._CFGFILE, mode='w', fmt=str) as file:
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

    def getfiles(self, pattern: OptStr = None) -> StrList:
        """Get list of files in the archive."""
        # Get list of normalized unique paths of archive members
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
        """Remove members from archive.

        Args:
            zinfos: List of ZipInfo entries, which are to be removed from
                the archive

        Returns:
            Boolean value which is true if no error occured.

        """
        if not zinfos:
            return True

        # Remove given entries from the list of archive members
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
            raise KeyError(f"could not locate archive members: {names}")

        # Create new ZipArchive in Memory
        new_buffer = BytesIO()
        new_file = ZipFile(new_buffer, mode='w')

        # Copy all archive members on the new list from current to new archive
        for zinfo in new_zinfos:
            data = self._file.read(zinfo, pwd=self._pwd)
            new_file.writestr(zinfo, data)

        # Close current archive and buffer and link new archive and buffer
        self._file.close()
        self._buffer.close()
        self._buffer = new_buffer
        self._file = new_file

        self._changed = True

        return True

    def _remove_duplicates(self) -> bool:
        """Remove all duplicates from archive."""
        # Get list of duplicates
        zinfos: ZipInfoList = []
        for filename in self.files:
            zinfos += self._locate(filename, sort=True)[:-1]

        # Remove duplicates
        return self._remove(zinfos)

    def close(self) -> None:
        """Close current archive and buffer."""
        self._file.close()
        self._buffer.close()

    @property
    def name(self) -> OptStr:
        """Filename of the archive without file extension."""
        return getattr(self._path, 'stem')

    @property
    def path(self) -> OptPath:
        """Filepath of the workspace."""
        return self._path

    @property
    def files(self) -> StrList:
        """List of all files within the workspace."""
        return self.getfiles()

    @property
    def folders(self) -> StrList:
        """List of folders within the workspace."""
        # Get list of unique foldernames in posix standard
        names: StrList = []
        for zinfo in self._file.infolist():
            if getattr(zinfo, 'is_dir')():
                name = PurePath(zinfo.filename).as_posix() + '/'
                names.append(name)
        return sorted(names)

    # @property
    # def about(self) -> OptStr:
    #     """Get a short description of the content of the resource."""
    #     try:
    #         return self._cfg['workspace']['about']
    #     except KeyError:
    #         return None
    #     return None
    #
    # @about.setter
    # def about(self, val: str) -> None:
    #     if not isinstance(val, str):
    #         raise TypeError(
    #             "attribute 'about' is required to be of type 'str'"
    #             f", not '{type(val).__name__}'")
    #     wscfg = self._cfg['workspace']
    #     if wscfg.get('about') != val:
    #         wscfg['about'] = val
    #         self._changed = True
    #
    # @property
    # def branch(self) -> OptStr:
    #     """Name of a duplicate of the original resource."""
    #     try:
    #         return self._cfg['workspace']['branch']
    #     except KeyError:
    #         return None
    #     return None
    #
    # @branch.setter
    # def branch(self, val: str) -> None:
    #     if not isinstance(val, str):
    #         raise TypeError(
    #             "attribute 'branch' is required to be of type 'str'"
    #             f", not '{type(val).__name__}'")
    #     wscfg = self._cfg['workspace']
    #     if wscfg.get('branch') != val:
    #         wscfg['branch'] = val
    #         self._changed = True
    #
    # @property
    # def version(self) -> OptStr:
    #     """Version of the branch of the workspace."""
    #     try:
    #         return self._cfg['workspace']['version']
    #     except KeyError:
    #         return None
    #     return None
    #
    # @version.setter
    # def version(self, val: str) -> None:
    #     if not isinstance(val, str):
    #         raise TypeError(
    #             "attribute 'version' is required to be of type 'str'"
    #             f", not '{type(val).__name__}'")
    #     wscfg = self._cfg['workspace']
    #     if wscfg.get('version') != val:
    #         wscfg['version'] = val
    #         self._changed = True
    #
    # @property
    # def license(self) -> OptStr:
    #     """License for the usage of the workspace.
    #
    #     Namereference to a legal document giving specified users an
    #     official permission to do something with the workspace. The attribute
    #     license is inherited by resources, that are created inside the
    #     workspace.
    #
    #     """
    #     try:
    #         return self._cfg['workspace']['license']
    #     except KeyError:
    #         return None
    #     return None
    #
    # @license.setter
    # def license(self, val: str) -> None:
    #     if not isinstance(val, str):
    #         raise TypeError(
    #             "attribute 'license' is required to be of type 'str'"
    #             f", not '{type(val).__name__}'")
    #     wscfg = self._cfg['workspace']
    #     if wscfg.get('license') != val:
    #         wscfg['license'] = val
    #         self._changed = True
    #
    # @property
    # def email(self) -> OptStr:
    #     """Email address of the maintainer of the workspace.
    #
    #     Email address to a person, an organization, or a service that is
    #     responsible for the content of the workspace. The attribute email
    #     is inherited by resources, that are created inside the workspace.
    #
    #     """
    #     try:
    #         return self._cfg['workspace']['email']
    #     except KeyError:
    #         return None
    #     return None
    #
    # @email.setter
    # def email(self, val: str) -> None:
    #     if not isinstance(val, str):
    #         raise TypeError(
    #             "attribute 'email' is required to be of type 'str'"
    #             f", not '{type(val).__name__}'")
    #     wscfg = self._cfg['workspace']
    #     if wscfg.get('email') != val:
    #         wscfg['email'] = val
    #         self._changed = True

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
