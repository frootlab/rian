# -*- coding: utf-8 -*-#
"""Text Terminal I/O."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import sys
import time
from abc import ABC, abstractmethod
from queue import Empty, Queue
from threading import Thread
from nemoa.base import entity, env
from nemoa.types import Any, Module, ClassVar, Exc, ExcType, Traceback, Method
from nemoa.types import OptStr

#
# TTY Classes
#

class TTYBase(ABC):
    """Abstract base class for text terminals."""

    _ttylib: Module
    _cur_attr: Any

    def __init__(self, mode: OptStr = None) -> None:
        """Modify terminal attributes."""
        self._ttylib = get_lib()
        self._cur_attr = self.get_attr()
        if mode:
            self.set_mode(mode)

    def __enter__(self) -> 'TTYBase':
        return self

    def __exit__(self, cls: ExcType, obj: Exc, tb: Traceback) -> None:
        """Reset current terminal attributes."""
        self.reset()

    def __del__(self) -> None:
        """Reset current terminal attributes."""
        self.reset()
        if hasattr(self, 'ttylib'):
            del self._ttylib

    def reset(self) -> None:
        """Reset current terminal attributes to it's initial value."""
        if hasattr(self, 'cur_attr'):
            self.set_attr(self._cur_attr)

    @abstractmethod
    def get_attr(self) -> Any:
        """Get current terminal attributes."""
        raise NotImplementedError()

    @abstractmethod
    def set_attr(self, attr: Any) -> None:
        """Set current terminal attributes."""
        raise NotImplementedError()

    @abstractmethod
    def set_mode(self, mode: str) -> None:
        """Set current terminal mode."""
        raise NotImplementedError()

    @abstractmethod
    def getch(self) -> str:
        """Get character from TTY."""
        raise NotImplementedError()

    @abstractmethod
    def start_getch(self) -> None:
        """Start handling of :meth:`.getch` requests."""
        raise NotImplementedError()

    @abstractmethod
    def stop_getch(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        raise NotImplementedError()

class TTYMsvcrt(TTYBase):
    """Windows/msvcrt implementation of Getch.

    This implementation supports Microsoft Windows by using the Microsoft Visual
    C/C++ Runtime Library for Python :py:mod:`msvcrt`.

    """

    _encoding: ClassVar[str] = env.get_encoding()

    def get_attr(self) -> Any:
        """Get attributes of current terminal."""
        return None

    def set_attr(self, attr: Any) -> None:
        """Set attributes of current terminal."""
        pass

    def set_mode(self, mode: str) -> None:
        """Set mode of current terminal."""
        pass

    def start_getch(self) -> None:
        """Start handling of :meth:`.getch` requests."""
        pass

    def stop_getch(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        pass

    def getch(self) -> str:
        """Get character from TTY."""
        return str(getattr(self._ttylib, 'getch')(), self._encoding)

class TTYTermios(TTYBase):
    """Unix/Termios implementation of Getch.

    This implementation supports Unix-like systems by using the Unix Terminal
    I/O API for Python :py:mod:`termios`.

    """

    _fd: int
    _tcgetattr: Method
    _tcsetattr: Method
    _buffer: Queue
    _resume: bool
    _thread: Thread
    _time: float

    def __init__(self, mode: OptStr = None) -> None:
        self._fd = sys.stdin.fileno()
        super().__init__(mode)

    def get_attr(self) -> Any:
        """Get attributes of current terminal."""
        try:
            return self._tcgetattr(self._fd)
        except AttributeError:
            self._tcgetattr = getattr(self._ttylib, 'tcgetattr')
        return self._tcgetattr(self._fd)

    def set_attr(self, attr: Any) -> None:
        """Set attributes of current terminal."""
        TCSAFLUSH = getattr(self._ttylib, 'TCSAFLUSH')
        try:
            return self._tcsetattr(self._fd, TCSAFLUSH, attr)
        except AttributeError:
            self._tcsetattr = getattr(self._ttylib, 'tcsetattr')
        self._tcsetattr(self._fd, TCSAFLUSH, attr)

    def set_mode(self, mode: str) -> None:
        """Set mode of current terminal."""
        # Buffered terminal for 'line'-mode:
        # Echo Chars; Wait for Enter
        if mode == 'line':
            # Modify lflag from current TTY attributes
            attr = self._cur_attr.copy()
            if isinstance(attr[3], int):
                ECHO = getattr(self._ttylib, 'ECHO')
                ICANON = getattr(self._ttylib, 'ICANON')
                attr[3] = attr[3] | ICANON | ECHO
            self.set_attr(attr)
        # Unbufered terminal for 'key'-mode:
        # No Echo; Don't wait for Enter
        elif mode == 'key':
            # Modify lflag from current TTY attributes
            attr = self._cur_attr.copy()
            if isinstance(attr[3], int):
                ECHO = getattr(self._ttylib, 'ECHO')
                ICANON = getattr(self._ttylib, 'ICANON')
                attr[3] = attr[3] & ~ICANON & ~ECHO
            self.set_attr(attr)

    def start_getch(self) -> None:
        """Start handling of :meth:`.getch` requests."""
        # Initialize buffer and start thread for reading stdio to buffer
        def buffer(attr: dict) -> None:
            while attr['_resume']:
                attr['_buffer'].put(sys.stdin.read(1))

        self._resume = True
        self._buffer = Queue()
        self._thread = Thread(
            target=buffer, args=(self.__dict__, ), daemon=True)
        self._thread.start()

        # Update time
        self._time = time.time()

    def getch(self) -> str:
        """Return single Character from buffer."""
        now = time.time()
        if now < self._time + .1: # Wait for 100 milliseconds
            return ''

        # Update time
        self._time = now

        try:
            return self._buffer.get_nowait()
        except Empty:
            return ''

    def stop_getch(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        self._resume = False # Stop thread from reading characters

#
# Functions
#

def get_lib() -> Module:
    """Get module for TTY I/O control.

    Depending on the plattform the module within the standard library, which is
    required for tty I/O control differs. The module :py:mod:`termios` provides
    an interface to the POSIX calls for tty I/O control. The module
    :py:mod:`msvcrt` provides access to some useful capabilities on Windows
    platforms.

    Returns:
        Reference to module for tty I/O control or None, if the module could
        not be determined.

    """
    libs = ['msvcrt', 'termios']
    for name in libs:
        module = entity.get_module(name)
        if module:
            return module
    raise ImportError("no module for TTY I/O could be imported")

def get_class() -> type:
    """Get platform specific class to handle getch() requests.

    This implementation supports Microsoft Windows by using the Microsoft Visual
    C/C++ Runtime Library for Python :py:mod:`msvcrt` and Unix-like systems by
    using the Unix Terminal I/O API for Python :py:mod:`termios`.

    """
    # Get platform specific tty I/O module.
    module = get_lib()
    mname = module.__name__
    cname = 'TTY' + mname.capitalize()
    if not cname in globals() or not callable(globals()[cname]):
        raise RuntimeError(f"TTY I/O module '{mname}' is not supported")
    return globals()[cname]

def get_instance() -> TTYBase:
    """Get current terminal instance."""
    if not '_tty' in globals():
        globals()['_tty'] = get_class()()
    return globals()['_tty']
