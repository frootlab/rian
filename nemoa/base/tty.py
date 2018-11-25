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
from nemoa.types import Module, OptModule, ClassVar

def get_lib() -> OptModule:
    """Get module for tty I/O control.

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
        ref = entity.get_module(name)
        if ref:
            return ref
    return None

class GetchBase(ABC):
    """Abstract base class for Getch classes."""

    ttylib: Module

    def __init__(self) -> None:
        """Initialize instance."""
        self.ttylib = get_lib()
        self.start()

    def __del__(self) -> None:
        """Release resources required for handling :meth:`.getch` requests."""
        self.stop()
        self.ttylib = None

    @abstractmethod
    def start(self) -> None:
        """Start handling of :meth:`.getch` requests."""
        raise NotImplementedError()

    @abstractmethod
    def getch(self) -> str:
        """Get character from TTY."""
        raise NotImplementedError()

    @abstractmethod
    def stop(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        raise NotImplementedError()

class GetchMsvcrt(GetchBase):
    """Windows/msvcrt implementation of Getch.

    This implementation supports Microsoft Windows by using the Microsoft Visual
    C/C++ Runtime Library for Python :py:mod:`msvcrt`.

    """

    encoding: ClassVar[str] = env.get_encoding()

    def start(self) -> None:
        """Start handling of :meth:`.getch` requests."""
        pass

    def getch(self) -> str:
        """Get character from tty."""
        if not isinstance(self.ttylib, Module):
            return ''
        if not getattr(self.ttylib, 'kbhit')():
            return ''
        return str(getattr(self.ttylib, 'getch')(), self.encoding)

    def stop(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        pass

class GetchTermios(GetchBase):
    """Unix/Termios implementation of Getch.

    This implementation supports Unix-like systems by using the Unix Terminal
    I/O API for Python :py:mod:`termios`.

    """

    buffer: Queue
    runsignal: bool
    time: float
    curterm: list
    fdesc: int
    thread: Thread

    def start(self) -> None:
        """Change terminal mode and start reading stdin to buffer."""
        # Get current tty attributes
        tcgetattr = getattr(self.ttylib, 'tcgetattr')
        self.fdesc = sys.stdin.fileno()
        self.curterm = tcgetattr(self.fdesc)

        # Modify lflag from current TTY attributes
        # to set terminal to unbuffered mode (not waiting for Enter)
        newattr = tcgetattr(self.fdesc)
        if isinstance(newattr[3], int):
            ECHO = getattr(self.ttylib, 'ECHO')
            ICANON = getattr(self.ttylib, 'ICANON')
            newattr[3] = newattr[3] & ~ICANON & ~ECHO
        tcsetattr = getattr(self.ttylib, 'tcsetattr')
        TCSAFLUSH = getattr(self.ttylib, 'TCSAFLUSH')
        tcsetattr(self.fdesc, TCSAFLUSH, newattr)

        # Initialize buffer and start thread for reading stdio to buffer
        def buffer(attr: dict) -> None:
            while attr['resume']:
                attr['buffer'].put(sys.stdin.read(1))
        self.resume = True
        self.buffer = Queue()
        self.thread = Thread(
            target=buffer, args=(self.__dict__, ), daemon=True)
        self.thread.start()

        # Update time
        self.time = time.time()

    def getch(self) -> str:
        """Return single Character from buffer."""
        now = time.time()
        if now < self.time + .1: # Wait for 100 milliseconds
            return ''

        # Update time
        self.time = now

        try:
            return self.buffer.get_nowait()
        except Empty:
            return ''

    def stop(self) -> None:
        """Stop handling of :meth:`.getch` requests."""
        # Reset terminal mode to previous tty attributes
        TCSAFLUSH = getattr(self.ttylib, 'TCSAFLUSH')
        tcsetattr = getattr(self.ttylib, 'tcsetattr')
        tcsetattr(self.fdesc, TCSAFLUSH, self.curterm)

        # Stop thread from reading characters
        self.resume = False

def getch_class() -> GetchBase:
    """Get platform specific class to handle getch() requests.

    This implementation supports Microsoft Windows by using the Microsoft Visual
    C/C++ Runtime Library for Python :py:mod:`msvcrt` and Unix-like systems by
    using the Unix Terminal I/O API for Python :py:mod:`termios`.

    """
    # Get platform specific tty I/O module.
    ref = get_lib()
    if not ref:
        raise ImportError("no module for tty I/O could be imported")
    cname = 'Getch' + ref.__name__.capitalize()
    if not cname in globals() or not callable(globals()[cname]):
        raise RuntimeError(
            f"tty I/O module '{ref.__name__}' is not supported")
    return globals()[cname]

Getch: GetchBase = getch_class()
