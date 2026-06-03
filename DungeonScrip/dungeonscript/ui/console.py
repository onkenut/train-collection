import os
import sys
from typing import Optional

_WINDOWS = sys.platform.startswith('win')

if not _WINDOWS:
    import termios
    import tty

class InputReader:
    def __init__(self):
        self._orig_settings = None
        
    def __enter__(self):
        if not _WINDOWS:
            self._orig_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self
        
    def __exit__(self, *args):
        if not _WINDOWS and self._orig_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._orig_settings)
            
    def read_key(self) -> str:
        if _WINDOWS:
            return self._read_key_windows()
        else:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
                    if ch3 == 'C': return 'right'
                    if ch3 == 'D': return 'left'
                    return ch3
                return ch2
            if ch == '\x7f': return 'backspace'
            if ch == '\n': return 'enter'
            return ch.lower()
            
    def _read_key_windows(self) -> str:
        import msvcrt
        ch = msvcrt.getwch()
        if ch == '\xe0':
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return 'up'
            if ch2 == 'P': return 'down'
            if ch2 == 'M': return 'right'
            if ch2 == 'K': return 'left'
            return ch2
        if ch == '\x08': return 'backspace'
        if ch == '\r': return 'enter'
        if ch == '\x1b': return 'escape'
        return ch.lower()

class Terminal:
    @staticmethod
    def size() -> tuple[int, int]:
        try:
            cols, rows = os.get_terminal_size()
            return cols, rows
        except:
            return 80, 24
            
    @staticmethod
    def clear():
        os.system('cls' if _WINDOWS else 'clear')
        
    @staticmethod
    def beep():
        print('\a', end='', flush=True)
