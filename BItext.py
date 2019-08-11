#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import sys

def len(string):
    """Returns the length of `string' excluding ASCII control sequences.
Example: BItext.len(BItext.red("hello")) => 5.
"""
    l = 0
    skip = False
    for c in string:
        if skip:
            if c == 'm':
                skip = False
        else:
            if c == '\x1b':
                skip = True
            else:
                l += 1
    return l

def _color(string, cidx, bold):
    """Add ascii control codes to `string' to print it in color `cidx', with bold indicator `bold'. Note: This adds 11 characters to `string'."""
    return "\x1b[{};{}m{}\x1b[0m".format(bold, cidx, string)

def black(string):
    return _color(string, 30, 0)

def red(string):
    return _color(string, 31, 0)

def green(string):
    return _color(string, 32, 0)

def yellow(string):
    return _color(string, 33, 0)

def blue(string):
    return _color(string, 34, 0)

def purple(string):
    return _color(string, 35, 0)

def cyan(string):
    return _color(string, 36, 0)

def white(string):
    return _color(string, 37, 0)

def BLACK(string):
    return _color(string, 30, 1)

def RED(string):
    return _color(string, 31, 1)

def GREEN(string):
    return _color(string, 32, 1)

def YELLOW(string):
    return _color(string, 33, 1)

def BLUE(string):
    return _color(string, 34, 1)

def PURPLE(string):
    return _color(string, 35, 1)

def CYAN(string):
    return _color(string, 36, 1)

def WHITE(string):
    return _color(string, 37, 1)

_colors = [ "black", "red", "green", "yellow", "blue", "purple", "cyan", "white" ]
_functions = { "black":  [black, BLACK],
               "red":    [red, RED],
               "green":  [green, GREEN],
               "yellow": [yellow, YELLOW],
               "blue":   [blue, BLUE],
               "purple": [purple, PURPLE],
               "cyan":   [cyan, CYAN],
               "white":  [white, WHITE] }

def isColor(s):
    """Returns True if `s' is a valid color name. Note: `s' could
include a leading +."""
    if s[0] == '+':
        return isColor(s[1:])
    else:
        return s in _colors

def _show():
    for c in _colors:
        funcs = _functions[c]
        sys.stdout.write("{:20}  {:20}\n".format(funcs[0](c), funcs[1](c)))

### Filter to display specific strings in color

DONE = 0
STORING = 1
NOMATCH = 2

class Matcher(object):
    color = ""
    string = ""
    slen = 0
    idx = 0
    func = None
    _status = NOMATCH

    def __init__(self, string, color):
        if color[0] == "+":
            bold = True
            self.color = color[1:]
        else:
            bold = False
            self.color = color
        self.string = string
        f = _functions[self.color]
        self.func = f[1] if bold else f[0]
        self.slen = len(string)
        self.idx = 0
        self._status = NOMATCH

    def match(self, ch):
        """Checks if character `ch' is the next character to be matched in this
matcher's string. Possible return values are DONE (last character of the string
matched, the string was printed, deactivate this matcher); STORING (this character
matched but the string is not finished - no action should be taken); NOMATCH
(character did not match; if a partial match was present, it was printed out)."""
        if ch == self.string[self.idx]:
            # sys.stderr.write("{} found at pos {}\n".format(ch, self.idx))
            self.idx += 1
            if self.idx == self.slen:
                sys.stdout.write(self.func(self.string))
                self.idx = 0
                self._status = DONE
            else:
                self._status = STORING
            return True
        else:
            if self.idx > 0:
                sys.stdout.write(self.string[0:self.idx])
            self.idx = 0
            self._status = NOMATCH
            return False

class MultiMatcher(object):
    matchers = []
    active = None

    def __init__(self, matchers):
        self.matchers = matchers
        
    def findMatcher(self, ch):
        """Find a matcher able to handle `ch'."""
        for m in self.matchers:
            if m.match(ch):
                return m
        return None

    def match(self, ch):
        if self.active:         # Is there an active matcher?
            h = self.active.match(ch) # See if it handles ch
            if h:
                if self.active._status == DONE: # Yes, and the string was printed out
                    self.active._status == NOMATCH # Reset
                    self.active = None
                    # Otherwise, no action
            else:               # Current matcher did not match
                new = self.findMatcher(ch) # Can we find another matcher?
                if new:
                    self.active = new # Yes, the new matcher took care of ch
                else:
                    self.active = None # No, signal we have no matcher
                    sys.stdout.write(ch) # and write ch out.
        else:
            new = self.findMatcher(ch) # Can we find a good matcher?
            if new:
                self.active = new
            else:
                sys.stdout.write(ch)
