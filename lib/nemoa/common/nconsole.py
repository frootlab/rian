# -*- coding: utf-8 -*-#
"""Collection of frequently used console functions."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import Optional

def getch() -> Optional[object]:
    """Getch wrapper for various platforms."""

    class GetchMsvcrt:
        """Microsoft Visual C/C++ Runtime Library implementation of getch."""

        @staticmethod
        def get() -> str:
            """Return character from stdin."""

            import msvcrt

            if not msvcrt.kbhit():
                return ''
            return str(msvcrt.getch(), 'utf-8')

    class GetchTermios:
        """Unix/Termios implementation of getch."""

        def __init__(self) -> None:
            import queue
            import sys
            import threading
            import time

            try:
                import termios
            except ImportError as err:
                raise ImportError("requires package termios") from err

            fdesc = sys.stdin.fileno()
            curterm = termios.tcgetattr(fdesc)

            # set unbuffered terminal
            newterm = termios.tcgetattr(fdesc)
            newterm[3] = (newterm[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(fdesc, termios.TCSAFLUSH, newterm)

            self.queue = {
                'stdin': queue.Queue(),
                'runsignal': True,
                'time': time.time(),
                'curterm': curterm,
                'fdesc': fdesc
            }

            def stream(queue):
                import sys
                while queue['runsignal']:
                    queue['stdin'].put(sys.stdin.read(1))

            self.queue['handler'] = threading.Thread(
                target=stream, args=(self.queue, ))
            self.queue['handler'].daemon = True
            self.queue['handler'].start()

        def __del__(self) -> None:
            try:
                import termios
            except ImportError as err:
                raise ImportError("requires package termios") from err

            fdesc = self.queue['fdesc']
            curterm = self.queue['curterm']
            termios.tcsetattr(fdesc, termios.TCSAFLUSH, curterm)
            self.queue['runsignal'] = False

            del self.__dict__['queue']

        def get(self) -> str:
            """Return character from internal buffer."""

            import time

            if not self.__dict__.get('queue', None):
                self.__init__()
            now = time.time()
            if now < self.queue['time'] + .5:
                return ''
            self.queue['time'] = now
            if self.queue['stdin'].empty():
                return ''

            return self.queue['stdin'].get()

    from nemoa.common import nsysinfo

    lib = nsysinfo.ttylib()

    if lib == 'msvcrt':
        return GetchMsvcrt()
    if lib == 'termios':
        return GetchTermios()

    return None
