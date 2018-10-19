# -*- coding: utf-8 -*-
"""I/O functions for workspace-files.

.. References:
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object

"""

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

from nemoa.core import npath, nsysinfo
from nemoa.classes import Attr, ReadOnlyAttr, ReadWriteAttr
from nemoa.errors import DirNotEmptyError, FileNotGivenError
from nemoa.fileio import inifile
from nemoa.types import (
    BytesIOBaseClass, BytesIOLike, BytesLike, ClassVar, IterFileLike, List,
    OptBytes, OptStr, OptPath, OptPathLike, PathLike, PathLikeList,
    TextIOBaseClass, Traceback, StrDict, StrDict2, StrList)

# Module specific types
ZipInfoList = List[ZipInfo]

# Module specific exceptions
class BadWsFile(OSError):
    """Exception for invalid workspace files."""

# Module constants
FILEEXTS = ['.ws', '.ws.zip']

class WsFile:
    """Workspace File.

    Workspace files are Zip-Archives, that contain the INI-formatted
    configuration file 'workspace.ini' in the archives root, and arbitrary
    resource files within subfolders.

    Args:
        filepath: String or `path-like object`_, that points to a valid
            workspace file or None. If the filepath points to a valid workspace
            file, then the class instance is initialized with a memory copy of
            the file. If the given file, however, does not exist, isn't a valid
            ZipFile, or does not contain a workspace configuration, respectively
            one of the errors FileNotFoundError, BadZipFile or BadWsFile is
            raised. The default behaviour, if the filepath is None, is to create
            an empty workspace in the memory, that uses the default folders
            layout. In this case the attribute maintainer is initialized with
            the current username.
        pwd: Bytes representing password of workspace file.

    """

    #
    # Private Class Variables
    #

    _CONFIG_FILE: ClassVar[Path] = Path('workspace.ini')
    _CONFIG_STRUCT: ClassVar[StrDict2] = {
        'workspace': {
            'about': 'str',
            'license': 'str',
            'maintainer': 'str',
            'email': 'str',
            'startup': 'path'}}
    _DEFAULT_CONFIG: ClassVar[StrDict2] = {
        'workspace': {
            'maintainer': nsysinfo.username()}}
    _DEFAULT_DIR_LAYOUT: ClassVar[StrList] = [
        'dataset', 'network', 'system', 'model', 'script']
    _DEFAULT_ENCODING = nsysinfo.encoding()

    #
    # Private Instance Variables
    #

    _attr: StrDict
    _buffer: BytesIOLike
    _changed: bool
    _file: ZipFile
    _path: OptPath
    _pwd: OptBytes

    #
    # Public Instance Attributes
    #

    about: Attr = ReadWriteAttr(str, bind='_attr')
    about.__doc__ = """Summary of the workspace.

    A short description of the contents, the purpose or the intended application
    of the workspace. The attribute about is inherited by resources, that are
    created inside the workspace and support the attribute.
    """

    email: Attr = ReadWriteAttr(str, bind='_attr')
    email.__doc__ = """Email address of the maintainer of the workspace.

    Email address to a person, an organization, or a service that is responsible
    for the content of the workspace. The attribute email is inherited by
    resources, that are created inside the workspace and support the attribute.
    """

    license: Attr = ReadWriteAttr(str, bind='_attr')
    license.__doc__ = """License for the usage of the contents of the workspace.

    Namereference to a legal document giving specified users an official
    permission to do something with the contents of the workspace. The attribute
    license is inherited by resources, that are created inside the workspace
    and support the attribute.
    """

    maintainer: Attr = ReadWriteAttr(str, bind='_attr')
    maintainer.__doc__ = """Name of the maintainer of the workspace.

    A person, an organization, or a service that is responsible for the content
    of the workspace. The attribute maintainer is inherited by resources, that
    are created inside the workspace and support the attribute.
    """

    startup: Attr = ReadWriteAttr(Path, bind='_attr')
    startup.__doc__ = """Startup script inside the workspace.

    The startup script is a path, that points to a a python script inside the
    workspace, which is intended to be executed after loading the workspace.
    """

    name: Attr = ReadOnlyAttr(list, getter='_get_name')
    name.__doc__ = """Filename of the workspace without file extension."""

    path: Attr = ReadOnlyAttr(Path, key='_path')
    path.__doc__ = """Filepath of the workspace."""

    files: Attr = ReadOnlyAttr(list, getter='search')
    files.__doc__ = """List of all files within the workspace."""

    folders: Attr = ReadOnlyAttr(list, getter='_get_folders')
    folders.__doc__ = """List of all folders within the workspace."""

    changed: Attr = ReadOnlyAttr(bool, key='_changed')
    changed.__doc__ = """Tells whether the workspace file has been changed."""

    #
    # Magic
    #

    def __init__(
            self, filepath: OptPathLike = None, pwd: OptBytes = None) -> None:
        """Load Workspace from file."""
        if filepath:
            self.load(filepath, pwd=pwd)
        else:
            self._create_new()

    def __enter__(self) -> 'WsFile':
        """Enter with statement."""
        return self

    def __exit__(self, etype: str, value: int, tb: Traceback) -> None:
        """Close workspace file and buffer."""
        self.close()

    #
    # Public Instance Methods
    #

    def load(self, filepath: PathLike, pwd: OptBytes = None) -> None:
        """Load Workspace from file.

        Args:
            filepath: String or `path-like object`_, that points to a valid
                workspace file. If the filepath points to a valid workspace
                file, then the class instance is initialized with a memory copy
                of the file. If the given file, however, does not exist, isn't a
                valid ZipFile, or does not contain a workspace configuration,
                respectively one of the errors FileNotFoundError, BadZipFile or
                BadWsFile is raised.
            pwd: Bytes representing password of workspace file.

        """
        # Initialize instance Variables, Buffer and buffered ZipFile
        self._attr = {}
        self._changed = False
        self._path = npath.expand(filepath)
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
            with self.open(self._CONFIG_FILE) as file:
                cfg = inifile.load(file, self._CONFIG_STRUCT)
        except KeyError as err:
            raise BadWsFile(
                f"workspace '{self._path}' is not valid: "
                "file '{self._CONFIG_FILE}' is missing") from err

        # Check if configuration contains required sections
        rsec = self._CONFIG_STRUCT.keys()
        if rsec > cfg.keys():
            raise BadWsFile(
                f"workspace '{self._path}' is not valid: "
                f"'{self._CONFIG_FILE}' requires sections '{rsec}'") from err

        # Link configuration
        self._attr = cfg.get('workspace', {})

    def save(self) -> None:
        """Save the workspace to it's filepath."""
        if isinstance(self._path, Path):
            self.saveas(self._path)
        else:
            raise FileNotGivenError(
                "use saveas() to save the workspace to a file")

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file.

        Args:
            filepath: String or `path-like object`_, that represents the name of
                a workspace file.

        """
        path = npath.expand(filepath)

        # Update 'workspace.ini'
        with self.open(self._CONFIG_FILE, mode='w') as file:
            inifile.save({'workspace': self._attr}, file)

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

        # Reload saved workpace from file
        self.load(path, pwd=self._pwd)

    @contextmanager
    def open(
            self, path: PathLike, mode: str = '', encoding: OptStr = None,
            is_dir: bool = False) -> IterFileLike:
        """Open file within the workspace.

        Args:
            path: String or `path-like object`_, that represents a workspace
                member. In reading mode the path has to point to a valid
                workspace file, or a FileNotFoundError is raised. In writing
                mode the path by default is treated as a file path. New
                directories can be written by setting the argument is_dir to
                True.
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is reading in text mode. Suported
                characters are:
                'r': Reading mode (default)
                'w': Writing mode
                'b': Binary mode
                't': Text mode (default)
            encoding: In binary mode encoding has not effect. In text mode
                encoding specifies the name of the encoding, which in reading
                and writing mode respectively is used to decode the stream’s
                bytes into strings, and to encode strings into bytes. By default
                the preferred encoding of the operating system is used.
            is_dir: Boolean value which determines, if the path is to be treated
                as a directory or not. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        Yields:
            Iterator to a file handler, to support the with statement.

        Examples:
            >>> with self.open('workspace.ini') as file:
            >>>     print(file.read())

        """
        # Open file handler to workspace member
        if 'w' in mode:
            if 'r' in mode:
                raise ValueError(
                    "argument mode is not allowed to contain the "
                    "characters 'r' AND 'w'")
            file = self._open_write(path, is_dir=is_dir)
        else:
            file = self._open_read(path)

        # Format buffered stream as bytes-stream or text-stream
        try:
            if 'b' in mode:
                if 't' in mode:
                    raise ValueError(
                        "argument mode is not allowed to contain the "
                        "characters 'b' AND 't'")
                yield file
            else:
                yield TextIOWrapper(
                    file, encoding=encoding or self._DEFAULT_ENCODING,
                    write_through=True)
        finally:
            file.close()

    def close(self) -> None:
        """Close current workspace and buffer."""
        if hasattr(self._file, 'close'):
            self._file.close()
        if hasattr(self._buffer, 'close'):
            self._buffer.close()

    def copy(self, source: PathLike, target: PathLike) -> bool:
        """Copy file within workspace.

        Args:
            source: String or `path-like object`_, that points to a file in the
                directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a new filename
                or an existing directory in the directory structure of the
                workspace. If the target is a directory the target file consists
                of the directory and the basename of the source file. If the
                target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file was copied.

        """
        # Check if source file exists and is not a directory
        src_file = PurePath(source).as_posix()
        src_infos = self._locate(source)
        if not src_infos:
            raise FileNotFoundError(
                f"workspace file '{src_file}' does not exist")
        src_info = src_infos[-1]
        if getattr(src_info, 'is_dir')():
            raise IsADirectoryError(
                f"'{src_file}/' is a directory not a file")

        # If target is a directory get name of target file from
        # source filename
        tgt_file = PurePath(target).as_posix()
        if tgt_file == '.':
            tgt_file = Path(src_file).name
        else:
            tgt_infos = self._locate(target)
            if tgt_infos:
                if getattr(tgt_infos[-1], 'is_dir')():
                    tgt_path = PurePath(tgt_file, Path(src_file).name)
                    tgt_file = tgt_path.as_posix()

        # Check if target file already exists
        if self._locate(tgt_file):
            raise FileExistsError(
                f"workspace file '{tgt_file}' already exist.")

        # Read binary data from source file
        data = self._file.read(src_info, pwd=self._pwd)

        # Create ZipInfo for target file from source file info
        tgt_time = getattr(src_info, 'date_time')
        tgt_info = ZipInfo(filename=tgt_file, date_time=tgt_time) # type: ignore

        # Write binary data to target file
        # TODO (patrick.michl@gmail.com): The zipfile standard module currently
        # does not support encryption in write mode. See:
        # https://docs.python.org/3/library/zipfile.html
        # When support is provided, the below line shall be replaced by:
        # self._file.writestr(tgt_info, data, pwd=self._pwd)
        self._file.writestr(tgt_info, data)
        self._changed = True

        # Check if new file exists
        return bool(self._locate(tgt_file))

    def move(self, source: PathLike, target: PathLike) -> bool:
        """Move file within workspace.

        Args:
            source: String or `path-like object`_, that points to a file in the
                directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a new filename
                or an existing directory in the directory structure of the
                workspace. If the target is a directory the target file consists
                of the directory and the basename of the source file. If the
                target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been moved.

        """
        # Copy source file to target file or directory
        # and on success remove source file
        return self.copy(source, target) and self.unlink(source)

    def append(self, source: PathLike, target: OptPathLike = None) -> bool:
        """Append file to the workspace.

        Args:
            source: String or `path-like object`_, that points to a valid file
                in the directory structure if the system. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, a IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a valid
                directory in the directory structure of the workspace. By
                default the root directory is used. If the directory does not
                exist, a FileNotFoundError is raised. If the target directory
                already contains a file, which name equals the filename of the
                source, a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been appended.

        """
        # Check source file
        src_file = npath.expand(source)
        if not src_file.exists():
            raise FileNotFoundError(f"file '{src_file}' does not exist")
        if src_file.is_dir():
            raise IsADirectoryError(f"'{src_file}' is a directory not a file")

        # Check target directory
        if target:
            tgt_dir = PurePath(target).as_posix() + '/'
            if not self._locate(tgt_dir):
                raise FileNotFoundError(
                    f"workspace directory '{tgt_dir}' does not exist")
        else:
            tgt_dir = '.'
        tgt_file = Path(tgt_dir, src_file.name)
        if self._locate(tgt_file):
            raise FileExistsError(
                f"workspace directory '{tgt_dir}' already contains a file "
                f"with name '{src_file.name}'")

        # Create ZipInfo entry from source file
        filename = PurePath(tgt_file).as_posix()
        datetime = time.localtime(src_file.stat().st_mtime)[:6]
        zinfo = ZipInfo(filename=filename, date_time=datetime) # type: ignore

        # Copy file to archive
        with src_file.open('rb') as src:
            data = src.read()
        # TODO (patrick.michl@gmail.com): The zipfile standard module currently
        # does not support encryption in write mode. See:
        # https://docs.python.org/3/library/zipfile.html
        # When support is provided, the below line shall be replaced by:
        # self._file.writestr(zinfo, data, pwd=pwd)
        self._file.writestr(zinfo, data)

        return True

    def read_text(self, filepath: PathLike, encoding: OptStr = None) -> str:
        """Read text from file.

        Args:
            filepath: String or `path-like object`_, that points to a valid file
                in the directory structure of the workspace. If the file does
                not exist a FileNotFoundError is raised.
            encoding: Specifies the name of the encoding, which is used to
                decode the stream’s bytes into strings. By default the preferred
                encoding of the operating system is used.

        Returns:
            Contents of the given filepath encoded as string.

        """
        with self.open(filepath, mode='r', encoding=encoding) as file:
            text = file.read()
        if not isinstance(text, str):
            return ''
        return text

    def read_bytes(self, filepath: PathLike) -> bytes:
        """Read bytes from file.

        Args:
            filepath: String or `path-like object`_, that points to a valid file
                in the dirctory structure of the workspace. If the file does not
                exist a FileNotFoundError is raised.

        Returns:
            Contents of the given filepath as bytes.

        """
        with self.open(filepath, mode='rb') as file:
            blob = file.read()
        if not isinstance(blob, bytes):
            return b''
        return blob

    def write_text(
            self, text: str, filepath: PathLike,
            encoding: OptStr = None) -> int:
        """Write text to file.

        Args:
            text: String, which has to be written to the given file.
            filepath: String or `path-like object`_, that represents a valid
                filename in the dirctory structure of the workspace.
            encoding: Specifies the name of the encoding, which is used to
                encode strings into bytes. By default the preferred encoding of
                the operating system is used.

        Returns:
            Number of characters, that are written to the file.

        """
        with self.open(filepath, mode='w', encoding=encoding) as file:
            if isinstance(file, TextIOBaseClass):
                return file.write(text)
        return 0

    def write_bytes(self, blob: BytesLike, filepath: PathLike) -> int:
        """Write bytes to file.

        Args:
            blob: Bytes, which are to be written to the given file.
            filepath: String or `path-like object`_, that represents a valid
                filename in the dirctory structure of the workspace.

        Returns:
            Number of bytes, that are written to the file.

        """
        with self.open(filepath, mode='wb') as file:
            if isinstance(file, BytesIOBaseClass):
                return file.write(blob)
        return 0

    def unlink(self, filepath: PathLike, ignore_missing: bool = True) -> bool:
        """Remove file from workspace.

        Args:
            filepath: String or `path-like object`_, that points to a file in
                the directory structure of the workspace. If the filepath points
                to a directory, an IsADirectoryError is raised. For the case,
                that the file does not exist, the argument ignore_missing
                determines, if a FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target file does not exist. The default
                behaviour, is to ignore missing files.

        Returns:
            Boolean value, which is True if the given file was removed.

        """
        matches = self._locate(filepath)
        if not matches:
            if ignore_missing:
                return True
            filename = PurePath(filepath).as_posix()
            raise FileNotFoundError(f"file '{filename}' does not exist")
        if getattr(matches[-1], 'is_dir')():
            dirname = PurePath(filepath).as_posix() + '/'
            raise IsADirectoryError(f"'{dirname}' is a directory not a file")
        return self._remove_members(matches)

    def mkdir(self, dirpath: PathLike, ignore_exists: bool = False) -> bool:
        """Create a new directory at the given path.

        Args:
            dirpath: String or `path-like object`_, that represents a valid
                directory name in the directory structure of the workspace. If
                the directory already exists, the argument ignore_exists
                determines, if a FileExistsError is raised.
            ignore_exists: Boolean value which determines, if FileExistsError is
                raised, if the target directory already exists. The default
                behaviour is to raise an error, if the file already exists.

        Returns:
            Boolean value, which is True if the given directory was created.

        """
        matches = self._locate(dirpath)
        if not matches:
            with self.open(dirpath, mode='w', is_dir=True):
                pass
        elif not ignore_exists:
            dirname = PurePath(dirpath).as_posix() + '/'
            raise FileExistsError(f"directory '{dirname}' already exists")
        return True

    def rmdir(
            self, dirpath: PathLike, recursive: bool = False,
            ignore_missing: bool = False) -> bool:
        """Remove directory from workspace.

        Args:
            dirpath: String or `path-like object`_, that points to a directory
                in the directory structure of the workspace. If the directory
                does not exist, the argument ignore_missing determines, if a
                FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target directory does not exist. The default
                behaviour, is to raise an error if the directory is missing.
            recursive: Boolean value which determines, if directories are
                removed recursively. If recursive is False, then only empty
                directories can be removed. If recursive, however, is True, then
                all files and subdirectories are alse removed. By default
                recursive is False.

        Returns:
            Boolean value, which is True if the given directory was removed.

        """
        matches = self._locate(dirpath)
        dirname = PurePath(dirpath).as_posix() + '/'
        if not matches:
            if ignore_missing:
                return True
            raise FileNotFoundError(f"directory '{dirname}' does not exist")
        files = self.search(dirname + '*')
        if not files:
            return self._remove_members(matches)
        if not recursive:
            raise DirNotEmptyError(f"directory '{dirname}' is not empty")
        allmatches = matches
        for file in files:
            allmatches += self._locate(file)
        return self._remove_members(allmatches)

    def search(self, pattern: OptStr = None) -> StrList:
        """Search for files in the workspace.

        Args:
            pattern: Search pattern that contains Unix shell-style wildcards:
                '*': Matches arbitrary strings
                '?': Matches single characters
                [seq]: Matches any character in seq
                [!seq]: Matches any character not in seq
                By default a list of all files and directories is returned.

        Returns:
            List of files and directories in the directory structure of the
            workspace, that match the search pattern.

        """
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

    #
    # Private Instance Methods
    #

    def _create_new(self) -> None:
        # Initialize instance Variables, Buffer and buffered ZipFile
        self._attr = self._DEFAULT_CONFIG['workspace'].copy()
        self._changed = False
        self._path = None
        self._pwd = None
        self._buffer = BytesIO()
        self._file = ZipFile(self._buffer, mode='w')

        # Create folders
        for folder in self._DEFAULT_DIR_LAYOUT:
            self.mkdir(folder)

    def _open_read(self, path: PathLike) -> BytesIOLike:
        # Locate workspace member by it's path
        # and open file handler for reading the file
        matches = self._locate(path)
        if not matches:
            fname = PurePath(path).as_posix()
            raise FileNotFoundError(
                f"workspace member with filename '{fname}' does not exist")
        # Select latest version of file
        zinfo = matches[-1]
        return self._file.open(zinfo, pwd=self._pwd, mode='r')

    def _open_write(self, path: PathLike, is_dir: bool = False) -> BytesIOLike:
        # Determine workspace member name from path
        # and get ZipInfo with local time as date_time
        filename = PurePath(path).as_posix()
        if is_dir:
            filename += '/'
        zinfo = ZipInfo( # type: ignore
            filename=filename,
            date_time=time.localtime()[:6])
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

    def _locate(self, path: PathLike, sort: bool = True) -> ZipInfoList:
        # Get list of member zipinfos
        zinfos = self._file.infolist()
        # Match members by path-like filenames
        matches = [i for i in zinfos if Path(i.filename) == Path(path)]
        if sort:
            # Sort matches by datetime
            matches = sorted(matches, key=lambda i: i.date_time)
        # Return sorted matches
        return matches

    def _get_name(self) -> OptStr:
        return getattr(self._path, 'stem', None)

    def _get_folders(self) -> StrList:
        names: StrList = []
        for zinfo in self._file.infolist():
            if getattr(zinfo, 'is_dir')():
                name = PurePath(zinfo.filename).as_posix() + '/'
                names.append(name)
        return sorted(names)

    def _remove_members(self, zinfos: ZipInfoList) -> bool:
        # Return True if list of members is empty
        if not zinfos:
            return True

        # Remove entries in the list of members from workspace
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
            raise FileNotFoundError(
                f"could not locate workspace members: {names}")

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
        # Get list of duplicates
        zinfos: ZipInfoList = []
        for filename in self.files:
            zinfos += self._locate(filename, sort=True)[:-1]

        # Remove duplicates
        return self._remove_members(zinfos)
