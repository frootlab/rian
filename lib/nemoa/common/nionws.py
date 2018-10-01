# -*- coding: utf-8 -*-
"""I/O functions for nemoa workspace files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import time

from zipfile import BadZipFile, ZipFile, ZipInfo
from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path, PurePath

from nemoa.common import nioini, npath
from nemoa.exceptions import BadWorkspaceFile
from nemoa.types import (
    IterAny, IterFileLike, OptBytes, OptStr, OptPath, PathLike,
    Traceback, StrDict2)

FILEEXTS = ['.nws', '.zip']

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
            'startup_script': 'str'},
        'folders': {
            'dataset': 'path',
            'network': 'path',
            'system': 'path',
            'model': 'path',
            'script': 'path'}}

    _cfg: StrDict2
    _path: Path
    _pwd: OptBytes

    def __init__(self, file: PathLike, pwd: OptBytes = None) -> None:
        """ """
        self._cfg = {}
        filepath = npath.getpath(file)

        # Test if given file is a valid ZIP Archive
        try:
            zipfile = ZipFile(filepath, 'r')
        except FileNotFoundError as err:
            raise FileNotFoundError(
                f"file '{str(filepath)}' does not exist") from err
        except BadZipFile as err:
            raise BadZipFile(
                f"file '{str(filepath)}' is not a valid ZIP file") from err
        finally:
            # Close zipfile if it is open
            if 'zipfile' in locals() and 'close' in dir(zipfile):
                zipfile.close()

        # Update path with given file
        self._path = filepath

        # Set Password
        self._pwd = pwd

        # try to open configuration file as StringIO
        # and load configuration from StringIO
        try:
            with self.open(self._CFGFILE, fmt=str) as cfgfile:
                self._cfg = nioini.load(cfgfile, self._CFGSTRUCT)
        except KeyError as err:
            raise BadWorkspaceFile(
                f"file '{str(file)}' is not a valid "
                "nemoa workspace file") from err
        finally:
            # Close cfgfile if it is open
            if 'cfgfile' in locals() and 'close' in dir(cfgfile):
                cfgfile.close()

        # Check if configuration file is valid
        if self._CFGSTRUCT.keys() > self._cfg.keys():
            raise BadWorkspaceFile(
                f"file '{str(file)}' is not a valid "
                "nemoa workspace file") from err

    @contextmanager
    def openws(self, mode: str = 'r') -> IterAny:
        """Open ZIP Archive."""
        zipfile = ZipFile(self._path, mode=mode)
        try:
            yield zipfile
        finally:
            zipfile.close()

    @contextmanager
    def open(
            self, name: PathLike, folder: OptStr = None,
            mode: str = 'r', fmt: type = bytes) -> IterFileLike:
        """Open workspace member as file handler."""
        # Get path representation for member
        if folder:
            try:
                dirpath = self._cfg['folders'][folder]
            except KeyError as err:
                raise KeyError(
                    f"folder '{str(folder)}' does not exist") from err
            path = Path(dirpath) / Path(name)
        else:
            path = Path(name)

        # Open member of archive
        if mode == 'r':
            # Locate member within archive by it's path representation
            # and open file handler for reading the file
            minfo = self.locate(path)
            zipfile = ZipFile(self._path, mode='r')
            file = zipfile.open(minfo, pwd=self._pwd, mode='r')
        elif mode == 'w':
            # Determine member name from path
            # and open file handler for writing file
            minfo = ZipInfo(
                filename=PurePath(path).as_posix(),
                date_time=time.localtime())
            zipfile = ZipFile(self._path, mode='a')
            file = zipfile.open(minfo, mode='w', pwd=self._pwd)
        else:
            raise ValueError(
                "argument 'mode' is required to by 'r' or 'w'"
                f", not {str(mode)}")

        # Format buffered stream as bytes-stream or text-stream
        try:
            if issubclass(fmt, bytes):
                yield file
            elif issubclass(fmt, str):
                yield TextIOWrapper(file, write_through=True)
                # if mode == 'r':
                #
                # else:
                #     yield file
            else:
                raise ValueError(
                    "argument 'fmt' is required to be a subclass of "
                    "str or bytes")
        finally:
            file.close()
            zipfile.close()

    def save(self) -> None:
        """Save."""
        with self.open(Path(self._CFGFILE), mode='w', fmt=str) as cfgfile:
            nioini.save(self._cfg, cfgfile)

    @property
    def name(self) -> OptStr:
        """Filename without file extension."""
        return getattr(self._path, 'stem')

    @property
    def about(self) -> OptStr:
        """Get a short description of the content of the resource."""
        try:
            return self._cfg['workspace']['about']
        except KeyError:
            return None
        return None

    @about.setter
    def about(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'about' is required to be of type 'str'"
                f", not '{type(val).__name__}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['about'] = val

    @property
    def branch(self) -> OptStr:
        """Name of a duplicate of the original resource."""
        try:
            return self._cfg['workspace']['branch']
        except KeyError:
            return None
        return None

    @branch.setter
    def branch(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'branch' is required to be of type 'str'"
                f", not '{type(val).__name__}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['branch'] = val

    @property
    def version(self) -> OptStr:
        """Version of the branch of the workspace."""
        try:
            return self._cfg['workspace']['version']
        except KeyError:
            return None
        return None

    @version.setter
    def version(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'version' is required to be of type 'str'"
                f", not '{type(val).__name__}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['version'] = val

    @property
    def license(self) -> OptStr:
        """License for the usage of the workspace.

        Namereference to a legal document giving specified users an
        official permission to do something with the workspace. The attribute
        license is inherited by resources, that are created inside the
        workspace.

        """
        try:
            return self._cfg['workspace']['license']
        except KeyError:
            return None
        return None

    @license.setter
    def license(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'license' is required to be of type 'str'"
                f", not '{type(val).__name__}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['license'] = val

    @property
    def email(self) -> OptStr:
        """Email address of the maintainer of the workspace.

        Email address to a person, an organization, or a service that is
        responsible for the content of the workspace. The attribute email
        is inherited by resources, that are created inside the workspace.

        """
        try:
            return self._cfg['workspace']['email']
        except KeyError:
            return None
        return None

    @email.setter
    def email(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'email' is required to be of type 'str'"
                f", not '{type(val).__name__}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['email'] = val

    @property
    def path(self) -> OptPath:
        """Filepath of the workspace."""
        return self._path

    @property
    def folders(self) -> list:
        """List of folder names within archive."""
        return list(self._cfg.get('folders', {}).keys())

    def files(self, folder: str) -> list:
        """List of filenames within named folder."""
        # Check value of argument 'folder'
        try:
            dirpath = self._cfg['folders'][folder]
        except KeyError as err:
            raise KeyError(
                "first argument is required to be a valid folder"
                f", not '{str(folder)}'") from err
        path = Path(dirpath)

        # Open Workspace
        with self.openws() as ws:
            # Get list of all members
            names = ws.namelist()

        # Search for members which path is located within the folder
        files = []
        pid = len(path.parts)
        for name in names:
            parts = Path(name).parts
            head, tail = parts[:pid], parts[pid:]
            if Path(*head) == path:
                if not tail:
                    continue
                files.append(PurePath(*tail).as_posix())
        return files

    def locate(self, path: PathLike) -> ZipInfo:
        """Locate workspace members by their path inside the workspace."""
        # Open Workspace
        with self.openws() as ws:
            # Get list of member zipinfos
            infos = ws.infolist()
            # Match members by path-like filenames
            matches = [i for i in infos if Path(i.filename) == Path(path)]
            if not matches:
                fname = PurePath(path).as_posix()
                raise KeyError(
                    f"member with filename '{fname}' does not exist")
            # Sort matches by datetime
            matches = sorted(matches, key=lambda i: i.date_time)
            # Return newest Member
            return matches[-1]

    def __enter__(self) -> 'NwsFile':
        """ """
        return self

    def __exit__(self, etype: str, value: int, tb: Traceback) -> None:
        """ """
        # Error handling
        if etype:
            print(f'exc_type: {etype}')
            print(f'exc_value: {value}')
            print(f'exc_traceback: {tb}')

    def __eq__(self, other: 'NwsFile') -> bool:
        """ """
        return self.path == other.path
