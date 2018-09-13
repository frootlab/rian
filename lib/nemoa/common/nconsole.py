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

        def get(self) -> str:
            """Return character from stdin."""

            import msvcrt

            if not msvcrt.kbhit(): return ''
            return str(msvcrt.getch(), 'utf-8')

    class GetchTermios:
        """Unix/Termios implementation of getch."""

        def __init__(self) -> None:
            """Create thread to fill internal buffer."""

            import queue
            import sys
            import termios
            import threading
            import time

            fd = sys.stdin.fileno()
            curterm = termios.tcgetattr(fd)

            # set unbuffered terminal
            newterm = termios.tcgetattr(fd)
            newterm[3] = (newterm[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(fd, termios.TCSAFLUSH, newterm)

            self.queue = {
                'stdin': queue.Queue(),
                'runsignal': True,
                'time': time.time(),
                'curterm': curterm,
                'fd': fd
            }

            def stream(queue):
                import sys
                while queue['runsignal']:
                    queue['stdin'].put(sys.stdin.read(1))

            self.queue['handler'] = threading.Thread(
                target = stream, args = (self.queue, ))
            self.queue['handler'].daemon = True
            self.queue['handler'].start()

        def __del__(self) -> None:
            """ """

            import termios

            fd = self.queue['fd']
            curterm = self.queue['curterm']
            termios.tcsetattr(fd, termios.TCSAFLUSH, curterm)
            self.queue['runsignal'] = False

            del self.__dict__['queue']

        def get(self) -> str:
            """Return character from internal buffer."""

            import time

            if not self.__dict__.get('queue', None): self.start()
            now = time.time()
            if now < self.queue['time'] + .5: return ''
            self.queue['time'] = now
            if self.queue['stdin'].empty(): return ''

            return self.queue['stdin'].get()

    from nemoa.common import nsysinfo

    lib = nsysinfo.ttylib()

    if lib == 'msvcrt': return GetchMsvcrt()
    if lib == 'Carbon': return GetchCarbon()
    if lib == 'termios': return GetchTermios()

    return None
