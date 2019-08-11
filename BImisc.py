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
