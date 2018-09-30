# -*- coding: utf-8 -*-
"""I/O functions for nemoa workspace files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from zipfile import BadZipFile, ZipFile, ZipInfo
from contextlib import AbstractContextManager, contextmanager
from io import TextIOWrapper
from pathlib import Path, PurePath

from nemoa.common import nioini, npath
from nemoa.exceptions import BadWSFile
from nemoa.types import FileLike, OptBytes, OptStr, OptPath, PathLike, StrDict2

FILEEXTS = ['.nws', '.zip']

class WsFile(AbstractContextManager):
    """Context Manager for Workspace files."""

    CFGFILE: Path = Path('workspace.ini')
    CFGSTRUCT: StrDict2 = {
        'workspace': {
            'about': 'str',
            'license': 'str',
            'maintainer': 'str',
            'email': 'str',
            'startup_script': 'str'},
        'folders': {
            'datasets': 'path',
            'networks': 'path',
            'systems': 'path',
            'models': 'path',
            'scripts': 'path'}}

    _path: Path
    _pwd: OptBytes
    _cfg: StrDict2

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
            zipfile.close()

        # Update path with given file
        self._path = filepath

        # Set Password
        self._pwd = pwd

        # try to open configuration file as StringIO
        # and load configuration from StringIO
        try:
            cfgfile = self.open(self.CFGFILE, fmt=str)
            self._cfg = nioini.load(cfgfile, self.CFGSTRUCT)
        except KeyError as err:
            raise BadWSFile(
                f"file '{str(file)}' is not a valid "
                "nemoa workspace file") from err
        finally:
            cfgfile.close()

        # Check if configuration file is valid
        if self.CFGSTRUCT.keys() > self._cfg.keys():
            raise BadWSFile(
                f"file '{str(file)}' is not a valid "
                "nemoa workspace file") from err

    @property
    def name(self) -> OptStr:
        return getattr(self._path, 'stem')

    @property
    def about(self) -> OptStr:
        """Get a short description of the content of the resource."""
        try:
            return self._cfg['workspace']['description']
        except KeyError:
            return None
        return None

    @about.setter
    def about(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError(
                "attribute 'about' is required to be of type 'str'"
                f", not '{type(val)}'")
        if not 'workspace' in self._cfg:
            self._cfg['workspace'] = {}
        self._cfg['workspace']['about'] = val

    @property
    def path(self) -> OptPath:
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
        """Locate archive member by name or Path."""
        # Open Workspace
        with self.openws() as ws:
            # Get list of Members
            names = ws.namelist()

            # Match Members by Name
            if isinstance(path, str):
                if path in names:
                    return ws.getinfo(path)
                raise KeyError(f"member with name '{path}' does not exist")

            # Match Members by Path
            matches = [name for name in names if Path(name) == path]
            if not matches:
                name = PurePath(path).as_posix()
                raise KeyError(f"member with name '{name}' does not exist")
            if len(matches) > 1:
                name = PurePath(path).as_posix()
                raise KeyError(f"path '{name}' is not unique")
            return ws.getinfo(matches[0])

    @contextmanager
    def openws(self):
        """Open ZIP Archive."""
        zipfile = ZipFile(self._path, 'r')
        try:
            yield zipfile
        finally:
            zipfile.close()

    def open(
            self, name: PathLike, folder: OptStr = None,
            mode: str = 'r', fmt: type = bytes) -> FileLike:
        """Return member of workspace as file handler."""
        # Get path of member
        if folder:
            try:
                dirpath = self._cfg['folders'][folder]
            except KeyError as err:
                raise KeyError(
                    f"folder '{str(folder)}' does not exist") from err
            path = Path(dirpath) / Path(name)
        else:
            path = Path(name)

        # Locate member of archive by it's path
        minfo = self.locate(path)

        # Open member of archive
        with self.openws() as ws:
            file = ws.open(minfo, mode=mode, pwd=self._pwd)

        if issubclass(fmt, bytes):
            return file
        if issubclass(fmt, str):
            return TextIOWrapper(file)
        raise ValueError(
            "argument 'fmt' is required to be a subclass of str or bytes")

    def __enter__(self) -> 'WsFile':
        """ """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """ """
        # Error handling
        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_value}')
            print(f'exc_traceback: {exc_traceback}')

    def __eq__(self, other: 'WsFile') -> bool:
        """ """
        return self.path == other.path
