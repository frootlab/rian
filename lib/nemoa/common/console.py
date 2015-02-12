# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import os

inkey = None

class _Getch:
    """Get a character from standard input."""
    def __init__(self):
        found = False
        try:
            self.impl = _GetchWindows()
            found = True
        except ImportError:
            pass
        if not found:
            try:
                self.impl = _GetchUnix()
                found = True
            except ImportError:
                pass
        if not found:
            try:
                self.impl = _GetchMac()
                found = True
            except ImportError:
                pass

    def get(self): return self.impl.get()
    def start(self): return self.impl.start()
    def stop(self): return self.impl.stop()

class _GetchUnix:

    _buffer = None

    def __init__(self):
        import termios

    def get(self):

        import time
        import sys

        if not self._is_running(): self.start()
        if time.time() - self._buffer['time'] > 0.5:
            self._buffer['time'] = time.time()
            if not self._buffer['stdin'].empty():
                ch = self._buffer['stdin'].get()
                return ch

    def start(self):
        import sys
        import threading
        import time
        import Queue
        import termios

        fd = sys.stdin.fileno()
        curterm = termios.tcgetattr(fd)

        # new terminal setting unbuffered
        newterm = termios.tcgetattr(fd)
        newterm[3] = (newterm[3] & ~termios.ICANON & ~termios.ECHO)

        # set unbuffered terminal
        termios.tcsetattr(fd, termios.TCSAFLUSH, newterm)

        self._buffer = {
            'stdin': Queue.Queue(),
            'runsignal': True,
            'time': time.time(),
            'curterm': curterm,
            'fd': fd }

        def instream(dictionary):
            while dictionary['runsignal']:
                dictionary['stdin'].put(sys.stdin.read(1))

        self._buffer['handler'] = threading.Thread(
            target = instream, args = (self._buffer, ))
        self._buffer['handler'].daemon = True
        self._buffer['handler'].start()

    def _is_running(self):
        return not self._buffer == None

    def stop(self):
        import termios

        fd = self._buffer['fd']
        curterm = self._buffer['curterm']
        termios.tcsetattr(fd, termios.TCSAFLUSH, curterm)
        self._buffer['runsignal'] = False
        self._buffer = None

class _GetchWindows:
    def __init__(self):
        import msvcrt
    def start(self): pass
    def get(self):
        import msvcrt
        if msvcrt.kbhit(): return msvcrt.getch()
    def stop(self): pass

class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
    def start(self): pass
    def get(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)
    def stop(self): pass

def startgetch():
    global inkey
    if not inkey: inkey = _Getch()
    return inkey.start()

def stopgetch():
    global inkey
    if not inkey: inkey = _Getch()
    return inkey.stop()

def getch():
    global inkey
    if not inkey: inkey = _Getch()
    return inkey.get()
