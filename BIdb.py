#!/usr/bin/env python

"""High-level interface to sqlite3."""

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import sys
import sqlite3 as sql

class DBField(object):
    name = ""
    spec = ""
    ftype = ""                  # I, C, V, T (for int, char, varchar, text respectively)
    pk = False                  # primary key?
    index = False               # X - Create index on this field?
    notnull = False             # N
    default = None              # D

    def __init__(self, name, spec):
        self.name = name
        self.spec = spec
        self.parseSpec(spec)

    def parseSpec(self, spec):
        fields = spec.split(",")
        idx = 0
        n = len(fields)
        for v in fields:
            if v == 'I':
                self.ftype = 'INT'
            elif v == 'R':
                self.ftype = 'REAL'
            elif v == 'T':
                self.ftype = 'TEXT'
            elif v[0] == 'C':
                self.ftype = 'CHAR(' + v[1:] + ")"
            elif v[0] == 'V':
                self.ftype = 'VARCHAR(' + v[1:] + ")"
            elif v == 'N':
                self.notnull = True
            elif v == 'X':
                self.index = True
            elif v == 'P':
                self.pk = True
            elif v[0] == 'D':
                self.default = v[1:]
                
    def __str__(self):
        return "{} {}{}{}{}".format(self.name, self.ftype,
                                    " DEFAULT " + self.default if self.default else "",
                                    " PRIMARY KEY" if self.pk else "",
                                    " NOT NULL" if self.notnull else "")

    def idx(self, tname):
        return "CREATE INDEX {}_{} on {}({});".format(tname, self.name, tname, self.name)

class DBTable(object):
    name = ""
    fields = []

    def __init__(self, name, *fields):
        self.name = name
        self.fields = fields

    def create(self):
        return "CREATE TABLE {} ({});".format(self.name, ", ".join([str(f) for f in self.fields]))

    def drop(self):
        return "DROP TABLE IF EXISTS {};".format(self.name)

    def indexes(self):
        l = []
        for f in self.fields:
            if f.index:
                l.append(f.idx(self.name))
        return l

    def empty(self):
        return "DELETE FROM {};".format(self.name)

class Database(object):
    filename = ""
    tables = {}
    _conn = None
    _lvl = 0
    _verbose = False

    def __init__(self, filename, *tables):
        self.filename = filename
        self.tables = {}
        for tab in tables:
            self.tables[tab.name] = tab

    def __enter__(self):
        if not self._conn:
            self._conn = sql.connect(self.filename)
        self._lvl += 1
        return self

    def __exit__(self, type, value, traceback):
        self._lvl += -1
        if self._lvl == 0:
            self._conn.close()
            self._conn = None

    def addTable(self, tab):
        self.tables[tab.name] = tab

    def execute(self, statement, args=()):
        if self._verbose:
            sys.stderr.write("Executing: {} {}\n".format(statement, args))
        self._conn.execute(statement, args)

    def commit(self):
        self._conn.commit()

    def create(self):
        for tab in self.tables.values():
            self._conn.execute(tab.drop())
            w = tab.create()
            print w
            self._conn.execute(tab.create())
            for i in tab.indexes():
                self._conn.execute(i)

def initDB(filename):
    pass

if __name__ == "__main__":
    DB = Database("testdb.db", DBTable("table1",
                                       DBField("test", "T"),
                                       DBField("test2", "C5,X,N,D'abc'")))
    with DB:
        DB.create()
