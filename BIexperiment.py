#!/usr/bin/env python

__author__    = "Alberto Riva, ICBR Bioinformatics Core"
__contact__   = "ariva@ufl.edu"
__copyright__ = "(c) 2019, University of Florida Foundation"
__license__   = "MIT"
__date__      = "Mar 19 2019"
__version__   = "1.0"

"""This module provides a class to represent a biological experiment. It defines a list of conditions,
each of which is represented by multiple samples, and a list of contrasts between pairs of conditions.
"""

import sys
from BIutils import BIcsv

class Experiment(object):
    conditions = []
    condsamples = {}
    samples = []
    samplescond = []
    contrasts = []

    def __init__(self):
        self.conditions = []
        self.condsamples = {}
        self.samples = []
        self.samplescond = []
        self.contrasts = []

    def addCondition(self, cname, csamples):
        """Add a condition `cname' with samples `csamples' (a list). Prints a warning
if any of the samples has already been defined."""
        cidx = len(self.conditions)
        for cs in csamples:
            if cs in self.samples:
                sys.stderr.write("Warning: duplicate sample name `{}'.\n".format(cs))
            self.samples.append(cs)
            self.samplescond.append(cidx)
        self.conditions.append(cname)
        self.condsamples[cname] = csamples

    def addContrast(self, test, ctrl):
        if test not in self.conditions:
            sys.stderr.write("Error: {} is not a condition name.\n".format(test))
            return False
        if ctrl not in self.conditions:
            sys.stderr.write("Error: {} is not a condition name.\n".format(ctrl))
            return False
        self.contrasts.append([test, ctrl])
        return True

    def initConditionsFromFile(self, filename):
        """Initialize conditions and samples from a tab-delimited file. Each row contains two columns:
a condition name, and a comma-delimited list of sample names."""
        for line in BIcsv.CSVreader(filename):
            cname = line[0]
            csamples = [ s.strip() for s in line[1].split(",") ]
            self.addCondition(cname, csamples)
    
    def initContrastsFromFile(self, filename):
        """Initialize contrasts from a tab-delimited file. Each row contains two columns:
test condition, and control condition."""
        ln = 1
        for line in BIcsv.CSVreader(filename):
            if len(line) < 2:
                sys.stderr.write("Error - line {} of file {} should contain two condition names.\n".format(ln, filename))
            else:
                self.addContrast(line[0], line[1])
            ln += 1

    def sampleLabels(self):
        "Returns a list with one element for each sample, being the condition the sample belongs to."""
        result = []
        for cond in self.conditions:
            for smp in self.condsamples[cond]:
                result.append(cond)
        return result

    def dump(self):
        sys.stdout.write("Conditions: {}\n".format(", ".join(self.conditions)))
        sys.stdout.write("Samples: {}\n".format(", ".join(self.samples)))
        sys.stdout.write("Contrasts: {}\n".format(", ".join(self.conditions)))
