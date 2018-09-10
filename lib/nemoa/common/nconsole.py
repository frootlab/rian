# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def getch():
    """Getch wrapper for various platforms."""

    found = False
    try:
        retval = GetchWindows()
        found = True
    except ImportError: pass
    if not found:
        try:
            retval = GetchUnix()
            found = True
        except ImportError: pass
    if not found:
        try:
            retval = GetchMac()
            found = True
        except ImportError: pass
    if not found: return False

    return retval

class GetchUnix:
    """Unix/Termios implementation of getch."""

    def __init__(self):
        import termios

    def get(self):
        import time

        if not self.__dict__.get('queue', None): self.start()
        now = time.time()
        if now < self.queue['time'] + 0.5: return ''
        self.queue['time'] = now
        if self.queue['stdin'].empty(): return ''
        return self.queue['stdin'].get()

    def start(self):
        import sys
        import threading
        import time
        import queue
        import termios

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
            'fd': fd }

        def stream(queue):
            import sys
            while queue['runsignal']:
                queue['stdin'].put(sys.stdin.read(1))

        self.queue['handler'] = threading.Thread(
            target = stream, args = (self.queue, ))
        self.queue['handler'].daemon = True
        self.queue['handler'].start()

        return True

    def stop(self):

        import termios
        fd = self.queue['fd']
        curterm = self.queue['curterm']
        termios.tcsetattr(fd, termios.TCSAFLUSH, curterm)
        self.queue['runsignal'] = False

        del self.__dict__['queue']

        return True

class GetchWindows:
    """Microsoft Windows/Visual C Run-Time implementation of getch."""

    def __init__(self):
        import msvcrt

    def get(self):
        import msvcrt
        if msvcrt.kbhit(): return str(msvcrt.getch(), 'utf-8')
        return ''

    def start(self):
        return True

    def stop(self):
        return True

class GetchMacCarbon:
    """OSX/Carbon implementation of getch.

    A function which returns the current ASCII key that is down.
    If no ASCII key is down, the null string is returned. See [1].

    References:
        [1] http://www.mactech.com/macintosh-c/chap02-1.html

    """

    def __init__(self):
        import Carbon

    def get(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0] == 0: return ''
        else:
            (what, msg, when, where, mod) = \
                Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)
        return ''

    def start(self):
        return True

    def stop(self):
        return True
