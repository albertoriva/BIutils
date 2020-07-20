#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2020, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Jul 20 2020"
__version__   = "1.0"

import os
import sys

ESCAPE = '\x1b['

def esc(code, *args):
    return ESCAPE + ";".join([str(a) for a in args]) + code

def terminal_size():
    rows, cols = os.popen('stty size', 'r').read().split()
    return [int(rows), int(cols)]

# Cursor controls

def home():
    return esc("H")

def goto(line, col):
    return esc("H", line, col)

def up(lines):
    return esc("A", lines)

def down(lines):
    return esc("B", lines)

def left(cols):
    return esc("C", cols)

def right(cols):
    return esc("D", cols)

def begOfNextLine(lines=1):
    return esc("E", lines)

def endOfPreviousLine(lines=1):
    return esc("F", lines)

def goToColumn(col):
    return esc("G", col)

def reportPosition(line, col):
    return esc("R", line, col)

def savePosition():
    return esc("s")

def restorePosition():
    return esc("u")

# Erase functions

def clearScreen():
    return esc("J", 2)

def clearToEOS():
    return esc("J", 0)

def clearFromBOS():
    return esc("J", 1)

def clearLine():
    return esc("K")

def clearToEOL():
    return esc("K", 0)

def clearFromBOL():
    return esc("K", 1)

# Set mode

def setMode(mode):
    return esc("h", "="+str(mode))

def cursorOff():
    return esc("l", "?25")

def cursorOn():
    return esc("h", "?25")

def saveScreen():
    return esc("h", "?47")

def restoreScreen():
    return esc("l", "?47")
