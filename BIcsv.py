#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import csv

class CSVreader(object):
    _reader = None
    _stream = None
    _close = False
    _header = []

    def __init__(self, source, delimiter='\t', skip=0):
        self._stream = open(source, "r")
        self._reader = csv.reader(self._stream, delimiter=delimiter)
        for i in range(skip):
            self._header = self._reader.next()
        self._close = True

    def __iter__(self):
        return self

    def next(self):
        try:
            row = self._reader.next()
        except StopIteration as e:
            #sys.stderr.write("Cleanup!\n")
            if self._close:
                self._stream.close()
            raise e
        return row

class DictCSVReader(object):
    _reader = None
    _stream = None
    _delim  = "\t"
    _close  = False
    _header = []
    _ncols  = 0
    _row    = {}

    def __init__(self, source, delimiter='\t'):
        self._stream = open(source, "r")
        self._reader = csv.reader(self._stream, delimiter=delimiter)
        self._delim = delimiter
        self._header = self._reader.next()
        self._ncols = len(self._header)
        self._row = dict([ (h, None) for h in self._header])
        self._close = True

    def __iter__(self):
        return self

    def next(self):
        try:
            row = self._reader.next()
            for i in range(self._ncols):
                self._row[self._header[i]] = row[i]
        except StopIteration as e:
            #sys.stderr.write("Cleanup!\n")
            if self._close:
                self._stream.close()
            raise e
        return self._row

    def emitHeader(self):
        return self._delim.join(self._header)

    def emit(self):
        return self._delim.join([self._row[h] for h in self._header])

class DualCSVreader(object):
    _reader1 = None
    _reader2 = None

    def __init__(self, filename1, filename2):
        self._reader1 = CSVreader(filename1)
        self._reader2 = CSVreader(filename2)

    def __iter__(self):
        return self

    def next(self):
        row1 = self._reader1.next()
        row2 = self._reader2.next()
        if row1[0] == row2[0] and row1[1] == row2[1] and row1[2] == row2[2]:
            return [row1[0], row1[1], row1[2], row1[3], row1[4], row2[3], row2[4] ]
        else:
            raise IOError()

