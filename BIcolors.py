#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import sys

class Palette():
    step = 7
    size = 27
    colors = []
    ptr = 0

    def __init__(self, step=7, size=27):
        """Generate a palette of either 27 or 64 web safe colors trying to separate similar colors."""
        if size == 27:
            c = ["00", "66", "CC"]
        elif size == 64:
            c = ["00", "44", "88", "CC"]
        else:
            sys.stderr.write("Error in generatePalette: palette size should be either 27 or 64!\n")
            return None
        rgbs = []
        for r in c:
            for g in c:
                for b in c:
                    rgbs.append('"#' + r + g + b + '"')
        idx = 0
        self.colors = []
        for i in range(size):
            self.colors.append(rgbs[idx])
            idx = (idx + step) % size

    def nextColor(self):
        """Return the next color in the palette. If all colors have been used, restart from first one."""
        c = self.colors[self.ptr]
        self.ptr = (self.ptr + 1) % self.size
        return c

if __name__ == "__main__":
    sys.stdout.write("""BIcolors.py - This module contains the following classes:

Palette - Generate a palette of either 27 or 64 web safe colors. Methods:
    __init__(step=7, size=27) - Initialize palette. step and size should be mutually prime.
    nextColor() - Returns the next color in the palette.

""")
