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
    conditions = []             # list of all conditions
    condsamples = {}            # samples associated with each condition
    samples = []                # list of all samples
    samplescond = []            # index of condition for each sample
    samplecondname = {}         # condition name associated with each sample
    contrasts = []

    def __init__(self):
        self.conditions = []
        self.condsamples = {}
        self.samplecondname = {}
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
            self.samplecondname[cs] = cname
        self.conditions.append(cname)
        self.condsamples[cname] = csamples

    def addContrast(self, test, ctrl):
        if test not in self.conditions:
            sys.stderr.write("Error: {} is not a condition name.\n".format(test))
            return False
        if ctrl not in self.conditions:
            sys.stderr.write("Error: {} is not a condition name.\n".format(ctrl))
            return False
        if test == ctrl:
            sys.stderr.write("Error: test and control conditions are the same ({}).\n".format(test))
            return False
        self.contrasts.append([test, ctrl])
        return True

    def initConditionsFromFile(self, filename):
        """Initialize conditions and samples from a tab-delimited file. Each row contains two columns:
a condition name, and a comma-delimited list of sample names."""
        for line in BIcsv.CSVreader(filename):
            if len(line) == 2:
                cname = line[0]
                csamples = [ s.strip() for s in line[1].split(",") ]
                self.addCondition(cname, csamples)
        # print(self.samples)
        # print(self.conditions)
        # print(self.samplescond)
        # print(self.condsamples)
        # print(self.samplecondname)
        
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

    def getSampleLabels(self, samples):
        """Return the labels for the specified samples as a list."""
        result = []
        for smp in samples:
            idx = 0
            found = False
            for s in self.samples:
                if s == smp:
                    result.append(self.conditions[self.samplescond[idx]])
                    found = True
                idx += 1
            if not found:
                sys.stderr.write("Error: column `{}' not found in conditions file.\n".format(smp))
                sys.exit(1)
        return result
                
    def dump(self):
        sys.stdout.write("Conditions: {}\n".format(", ".join(self.conditions)))
        sys.stdout.write("Samples: {}\n".format(", ".join(self.samples)))
        sys.stdout.write("Contrasts: {}\n".format(", ".join(self.conditions)))
