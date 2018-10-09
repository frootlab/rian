# -*- coding: utf-8 -*-#
"""Console functions."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import sys
import time

from queue import Queue
from threading import Thread

from nemoa.common import nsysinfo

ENCODING = nsysinfo.encoding()

class GetchTermios:
    """Unix/Termios implementation of getch()."""

    stdin: Queue
    runsignal: bool
    time: float
    curterm: list
    fdesc: int
    thread: Thread

    def __init__(self) -> None:
        """Change terminal mode and start reading stdin to buffer."""
        try:
            import termios
        except ImportError as err:
            raise ImportError("requires package termios") from err

        def queue(attr: dict) -> None:
            """Copy characters from stdin to the buffer."""
            while attr['runsignal']:
                attr['stdin'].put(sys.stdin.read(1))

        self.fdesc = sys.stdin.fileno()
        self.curterm = termios.tcgetattr(self.fdesc)

        # Modify lflag from tty attributes
        # to set terminal mode to unbuffered
        attr = termios.tcgetattr(self.fdesc)
        if isinstance(attr[3], int):
            attr[3] = attr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(self.fdesc, termios.TCSAFLUSH, attr)

        self.stdin = Queue()
        self.runsignal = True
        self.time = time.time()
        self.thread = Thread(
            target=queue, args=(self.__dict__, ), daemon=True)
        self.thread.start()

    def __del__(self) -> None:
        """Reset terminal mode and stop reading stdin to buffer."""
        try:
            import termios
        except ImportError as err:
            raise ImportError("requires package termios") from err

        termios.tcsetattr(self.fdesc, termios.TCSAFLUSH, self.curterm)

        # Stop thread from reading characters
        self.runsignal = False

    def get(self) -> str:
        """Return character from buffer."""
        now = time.time()
        if now < self.time + .5:
            return ''
        self.time = now
        if self.stdin.empty():
            return ''
        return self.stdin.get()

def getch() -> str:
    """Get character from stdin.

    This getch() implementation supports Microsoft Windows by using the
    Microsoft Visual C/C++ Runtime Library (`msvcrt`_) and Unix-like Systems by
    using the Terminal I/O API `termios`_.

    .. _termios: https://docs.python.org/3/library/termios.html
    .. _msvcrt: https://docs.python.org/3/library/msvcrt.html

    """
    # Get platform spoecific implementation of getch()
    # Buffer result to reduce latency of later getch() calls
    if 'getch' not in globals():
        lib = nsysinfo.ttylib()
        if lib == 'msvcrt':
            globals()['getch'] = getch_windows
        elif lib == 'termios':
            globals()['getch'] = getch_unix
        else:
            raise ModuleNotFoundError()

    # Return character from stdin
    return globals()['getch']()

def getch_unix() -> str:
    """Get character from stdin."""
    # Create
    if 'getch_termios' not in globals():
        globals()['getch_termios'] = GetchTermios()
    return globals()['getch_termios'].get()

def getch_windows() -> str:
    """Get character from stdin.

    Microsoft Visual C/C++ Runtime Library implementation of getch().
    """
    try:
        import msvcrt
    except ImportError as err:
        raise ImportError(
            "required package msvcrt from standard library "
            "is only available on the Windows plattform")

    if not getattr(msvcrt, 'kbhit')():
        return ''
    return str(getattr(msvcrt, 'getch')(), ENCODING)
