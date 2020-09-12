#!/usr/bin/env python

"""High-level interface to MySQL, sqlite3."""

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

import sys
import sqlite3 as sql
import mysql.connector as mysql

def dget(dict, key):
    if key in dict:
        return dict[key]
    else:
        return None

class DBField(object):
    name = ""
    spec = ""
    ftype = ""                  # I, B, C, V, T, Y (for int, bigint, char, varchar, text, date respectively)
    pk = False                  # P - Primary key?
    autoinc = False             # A - Auto increment?
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
            elif v == 'B':
                self.ftype = 'BIGINT'
            elif v == 'R':
                self.ftype = 'REAL'
            elif v == 'T':
                self.ftype = 'TEXT'
            elif v == 'Y':
                self.ftype = 'DATE'
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
            elif v == 'A':
                self.autoinc = True
            elif v[0] == 'D':
                self.default = v[1:]
                
    def __str__(self):
        return "{} {}{}{}{}".format(self.name, self.ftype,
                                    " DEFAULT '" + self.default + "'" if self.default else "",
                                    " PRIMARY KEY" if self.pk else "",
                                    " AUTO_INCREMENT" if self.autoinc else "",
                                    " NOT NULL" if self.notnull else "")

    def idx(self, tname):
        return "CREATE INDEX {}_{} on {}({});".format(tname, self.name, tname, self.name)

class DBTable(object):
    name = ""
    fields = []

    def __init__(self, name, *fields):
        self.name = name
        self.fields = [ DBField(f[0], f[1]) for f in fields ]

    def create(self):
        s = "CREATE TABLE {} ({});".format(self.name, ", ".join([str(f) for f in self.fields]))
        # sys.stderr.write(s + "\n")
        return s

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
    tables = {}
    _keyargs = {}
    _conn = None
    _curs = None
    _lvl = 0
    _verbose = False

    def __init__(self, tables, **keyargs):
        self._keyargs = keyargs
        self.tables = {}
        for tab in tables:
            self.tables[tab.name] = tab
        self.init()

    def k(self, key):
        if key in self._keyargs:
            return self._keyargs[key]
        else:
            return None

    def __enter__(self):
        self._lvl += 1
        if not self._conn:
            self._conn = self.connect()
        return self._conn.cursor()

    def __exit__(self, type, value, traceback):
        self._lvl += -1
        if self._lvl == 0:
            self._conn.close()
            self._conn = None

    def addTable(self, tab):
        self.tables[tab.name] = tab

    def getTable(self, tablename):
        if tablename in self.tables:
            return self.tables[tablename]
        else:
            return None

    def cursor(self):
        return self._conn.cursor()

    def execute(self, statement, args=()):
        if self._verbose:
            sys.stderr.write("Executing: {} {}\n".format(statement, args))
        self._curs.execute(statement, args)
        return self._curs

    def commit(self):
        self._conn.commit()

    def create(self):
        for tab in self.tables.values():
            self.execute(tab.drop())
            w = tab.create()
            self.execute(tab.create())
            for i in tab.indexes():
                self.execute(i)

    def tuplesToDict(self, table, querytail=""):
        tab = self.getTable(table)
        if tab:
            alltuples = []
            c = self.cursor()
            fnames = [ f.name for f in tab.fields ]
            q = "SELECT " + ",".join(fnames) + " FROM " + table + " " + querytail + ";"
            c.execute(q)
            for row in c.fetchall():
                result = {}
                for f, d in zip(fnames, row):
                    result[f] = d
                alltuples.append(result)
            return alltuples
        return []

    def queryToDict(self, query, fnames):
        alltuples = []
        c = self.cursor()
        c.execute(query)
        for row in c.fetchall():
            result = {}
            for f, d in zip(fnames, row):
                result[f] = d
            alltuples.append(result)
        return alltuples

    def rowToDict(self, table, querytail=""):
        tab = self.getTable(table)
        if tab:
            result = {}
            c = self.cursor()
            fnames = [ f.name for f in tab.fields ]
            q = "SELECT " + ",".join(fnames) + " FROM " + table + " " + querytail + ";"
            c.execute(q)
            row = c.fetchone()
            if row:
                for f, d in zip(fnames, row):
                    result[f] = d
                return result
            else:
                return None
        else:
            return None

    def getColumn(self, query, column=0):
        result = []
        c = self.cursor()
        c.execute(query)
        for row in c.fetchall():
            result.append(row[column])
        return result

    def getRow(self, query):
        c = self.cursor()
        c.execute(query)
        return c.fetchone()

    def getValue(self, query, column=0):
        c = self.cursor()
        c.execute(query)
        return c.fetchone()[column]

class SQLiteDatabase(Database):
    filename = ""

    def init(self):
        self.filename = self.k("filename")

    def connect(self):
        return sql.connect(self.filename)

class MySQLDatabase(Database):
    host = ""
    user = ""
    password = ""
    database = ""

    def init(self):
        self.host = self.k("host")
        self.user = self.k("user")
        self.password = self.k("password")
        self.database = self.k("database")

    def connect(self):
        return mysql.connect(host=self.host, user=self.user, password=self.password, database=self.database)

def initDB(filename):
    pass

if __name__ == "__main__":
    DB = SQLiteDatabase([DBTable("table1",
                                 ("test", "T"),
                                 ("test2", "C5,X,N,D'abc'"))],
                        filename="testdb.db")

    with DB as cx:
        DB.create()
