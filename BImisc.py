#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import sys
import os.path
import subprocess as sp

# Global

SHELL_VERBOSE = False

# Utilities

def missingOrStale(target, reference=None):
    """Return True if file `target' is missing, or is older than `reference'."""
    if not os.path.isfile(target):
        return True
    if reference:
        return os.path.getmtime(target) < os.path.getmtime(reference)
    else:
        return False

def shell(commandline, verbose=SHELL_VERBOSE):
    """Execute the specified command in a subshell. If `verbose' is True,
Prints the command being executed to standard error."""
    if verbose:
        sys.stderr.write("[Executing: " + commandline + "]\n")
    return sp.check_output(commandline, shell=True)

def linkify(url, name, target="_blank"):
    if name is None:
        name = os.path.split(url)[1]
    return "<A target='{}' href='{}'>{}</A>".format(target, url, name)

def get_iterator(dict):
    if PYTHON_VERSION == 2:
        return dict.iteritems()
    else:
        return dict.items()

def genOpen(filename, mode):
    """Generalized open() function - works on both regular files and .gz files."""
    (name, ext) = os.path.splitext(filename)
    if ext == ".gz":
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)

def decodeUnits(x):
    if x.endswith("G"):
        return (x[:-1], 1000000000)
    if x.endswith("M") or x.endswith("m"):
        return (x[:-1], 1000000)
    else:
        return (x, 1)
    
def parseFraction(f):
    """Parse a fraction (a string of the form N/D) returning a float.
Returns None if f is not in the form N/D, or if D is 0."""
    p = f.find("/")
    if p < 1:
        return None
    s1 = f[:p]
    s2 = f[p+1:]
    try:
        v1 = int(s1)
        v2 = int(s2)
    except ValueError:
        return None
    if v2:
        return 1.0 * v1 / v2
    else:
        return None

class Output():
    destination = sys.stdout
    out = None                  # stream
    __doc__ = "A class that returns a stream to an open file, or sys.stdout if the filename is None or '-'."

    def __init__(self, destination):
        if destination != '-':
            self.destination = destination

    def __enter__(self):
        if self.destination:
            self.out = genOpen(self.destination, "w")
        return self.out

    def __exit__(self, type, value, traceback):
        if self.destination:
            self.out.close()

class ShellScript():
    filename = ""
    out = None

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.out = open(self.filename, "w")
        self.out.write("#!/bin/bash\n\n")
        return self.out

    def __exit__(self, type, value, traceback):
        self.out.close()
        try:
            os.chmod(self.filename, 0o770)
        except:
            pass
