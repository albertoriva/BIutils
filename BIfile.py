#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

from BImisc import shell, missingOrStale

class File(object):
    directory = ""
    name = ""
    sources = []
    _pathname = None
    _nlines = None

    def __init__(self, name, dir="", sources=[]):
        self.name = name
        self.directory = dir
        self.sources = sources

    def __str__(self):
        return self.pathname()

    def pathname(self):
        """Returns the pathname string of this file."""
        if not self._pathname:
            if self.directory:
                self._pathname = self.directory + "/" + self.name
            else:
                self._pathname = self.name
        return self._pathname

    def nlines(self):
        """Returns the number of lines in this file (computing it if necessary)."""
        if self._nlines is None:
            s = shell("wc -l " + self.pathname()).strip()
            self._nlines = int(s.split(" ")[0])
        return self._nlines

    def stale(self):
        """Returns True if this file is older than at least one of its sources. If this
file has no sources, always returns True."""
        if self.sources:
            for s in self.sources:
                if Utils.missingOrStale(self.pathname(), s.pathname()):
                    return True
            return False
        else:
            return True

class Filer(object):
    _files = {}
    directory = ""
    
    def __init__(self, directory):
        self._files = {}
        self.directory = directory

    def addFile(self, tag, name, sources=[], dir=None):
        """Add the file `name' to this filer with the supplied `tag'."""
        f = File(name, dir=dir or self.directory, sources=sources)
        self._files[tag] = f
        return f

    def file(self, tag):
        """Return the file having the supplied `tag' in this filer."""
        if tag in self._files:
            return self._files[tag]
        else:
            return None
        
    def pathname(self, tag):
        """Returns the pathname string for the file with the supplied `tag' in this filer."""
        f = self.file(tag)
        if f:
            return f.pathname()
        else:
            return None
